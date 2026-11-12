#!/usr/bin/env python3
"""Convert a markdown subset to a styled .docx.

Usage: python3 md_to_docx.py input.md output.docx ["Title"] ["Subtitle"]

Supports: #/##/###/#### headings, pipe tables, bullet and numbered lists,
fenced code blocks, blockquotes, horizontal rules, and inline **bold**,
*italic*, `code`, [links](url).

Styling matches the project's editorial look: navy + gold accents, serif
headings, shaded table headers, no stock template feel.
"""
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x1C, 0x2F, 0x5C)
GOLD = RGBColor(0xA8, 0x7E, 0x00)
INK = RGBColor(0x1C, 0x1A, 0x17)
MUTED = RGBColor(0x6D, 0x67, 0x5A)
RULE = RGBColor(0xDD, 0xD4, 0xC4)

HEAD_FONT = 'Cambria'
BODY_FONT = 'Calibri'
MONO_FONT = 'Consolas'


# ------------------------------------------------------------------ helpers
def shade(cell, hex_fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_fill)
    tc_pr.append(shd)


def bottom_border(paragraph, color='DDD4C4', size='6'):
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), size)
    bottom.set(qn('w:space'), '4')
    bottom.set(qn('w:color'), color)
    borders.append(bottom)
    p_pr.append(borders)


def left_border(paragraph, color='A87E00', size='12'):
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement('w:pBdr')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), size)
    left.set(qn('w:space'), '8')
    left.set(qn('w:color'), color)
    borders.append(left)
    p_pr.append(borders)


def set_cell_margins(table, top=40, bottom=40, left=70, right=70):
    tbl_pr = table._tbl.tblPr
    mar = OxmlElement('w:tblCellMar')
    for tag, val in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        el = OxmlElement(f'w:{tag}')
        el.set(qn('w:w'), str(val))
        el.set(qn('w:type'), 'dxa')
        mar.append(el)
    tbl_pr.append(mar)


INLINE = re.compile(
    r'(\*\*.+?\*\*|__.+?__|\*[^*]+?\*|_[^_]+?_|`[^`]+?`|\[[^\]]+?\]\([^)]+?\))'
)


def add_inline(paragraph, text, size=None, color=None, base_bold=False, base_italic=False):
    """Render inline markdown into runs on an existing paragraph."""
    text = text.replace('\\|', '|')
    for token in INLINE.split(text):
        if not token:
            continue
        bold = base_bold
        italic = base_italic
        mono = False
        content = token
        if token.startswith('**') and token.endswith('**'):
            bold, content = True, token[2:-2]
        elif token.startswith('__') and token.endswith('__'):
            bold, content = True, token[2:-2]
        elif token.startswith('*') and token.endswith('*') and len(token) > 2:
            italic, content = True, token[1:-1]
        elif token.startswith('_') and token.endswith('_') and len(token) > 2:
            italic, content = True, token[1:-1]
        elif token.startswith('`') and token.endswith('`'):
            mono, content = True, token[1:-1]
        elif token.startswith('[') and '](' in token:
            content = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'\1 (\2)', token)
        # strip any residual emphasis markers inside the token
        content = content.replace('**', '')
        if not content:
            continue
        run = paragraph.add_run(content)
        run.bold = bold
        run.italic = italic
        if mono:
            run.font.name = MONO_FONT
            run.font.size = Pt(8.5)
        if size:
            run.font.size = Pt(size)
        if color:
            run.font.color.rgb = color


def split_row(line):
    cells = re.split(r'(?<!\\)\|', line.strip())
    if cells and cells[0].strip() == '':
        cells = cells[1:]
    if cells and cells[-1].strip() == '':
        cells = cells[:-1]
    return [c.strip() for c in cells]


def is_sep_row(line):
    return bool(re.match(r'^\s*\|?[\s:|-]+\|?\s*$', line)) and '-' in line


# ------------------------------------------------------------------ document
def build(md_path, docx_path, title=None, subtitle=None):
    lines = open(md_path, encoding='utf-8').read().split('\n')

    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)

    normal = doc.styles['Normal']
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.18

    # masthead
    if title or subtitle:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(title or '')
        r.font.name = HEAD_FONT
        r.font.size = Pt(22)
        r.font.bold = True
        r.font.color.rgb = NAVY
        if subtitle:
            p2 = doc.add_paragraph()
            r2 = p2.add_run(subtitle)
            r2.font.size = Pt(9.5)
            r2.font.color.rgb = MUTED
            bottom_border(p2, '1C2F5C', '12')

    i = 0
    n = len(lines)
    in_code = False
    code_buf = []
    skipped_first_h1 = False

    def heading(text, level, size, color):
        """Real Word heading style (so the outline/navigation works), recoloured."""
        # when a masthead title is supplied, shift levels up one so sections are H1
        out_level = max(1, level - 1) if title else level
        p = doc.add_paragraph(style=f'Heading {out_level}')
        p.paragraph_format.space_before = Pt(14 if out_level == 1 else 10 if out_level == 2 else 7)
        p.paragraph_format.space_after = Pt(7 if out_level == 1 else 4)
        p.paragraph_format.keep_with_next = True
        run_text = re.sub(r'\*\*|__', '', text)
        r = p.add_run(run_text)
        r.font.name = HEAD_FONT
        r.font.size = Pt(size)
        r.font.bold = True
        r.font.color.rgb = color
        if out_level == 1:
            bottom_border(p, 'DDD4C4', '6')
        return p

    while i < n:
        raw = lines[i]
        line = raw.rstrip()

        # ---------- fenced code
        if line.strip().startswith('```'):
            if in_code:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.4)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(8)
                r = p.add_run('\n'.join(code_buf))
                r.font.name = MONO_FONT
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(0x2A, 0x28, 0x24)
                shade_para(p, 'F5F2EA')
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(raw)
            i += 1
            continue

        stripped = line.strip()

        # ---------- blank
        if not stripped:
            i += 1
            continue

        # ---------- horizontal rule
        if re.match(r'^-{3,}$', stripped) or re.match(r'^\*{3,}$', stripped):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(10)
            bottom_border(p, 'DDD4C4', '6')
            i += 1
            continue

        # ---------- headings
        m = re.match(r'^(#{1,4})\s+(.*)$', stripped)
        if m:
            level = len(m.group(1))
            text = m.group(2)
            if level == 1 and not skipped_first_h1:
                # a supplied title already serves as the masthead
                skipped_first_h1 = True
                if title:
                    i += 1
                    continue
            if level == 1:
                heading(text, 1, 15, NAVY)
            elif level == 2:
                heading(text, 2, 12.5, GOLD)
            elif level == 3:
                heading(text, 3, 11, NAVY)
            else:
                heading(text, 4, 10.5, MUTED)
            i += 1
            continue

        # ---------- table
        if stripped.startswith('|') and i + 1 < n and is_sep_row(lines[i + 1]):
            header = split_row(stripped)
            i += 2
            body = []
            while i < n and lines[i].strip().startswith('|'):
                body.append(split_row(lines[i]))
                i += 1
            cols = max([len(header)] + [len(r) for r in body]) if body else len(header)
            table = doc.add_table(rows=1, cols=cols)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True
            set_cell_margins(table)
            hdr = table.rows[0]
            for c in range(cols):
                cell = hdr.cells[c]
                cell.text = ''
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                txt = header[c] if c < len(header) else ''
                add_inline(p, txt, size=8.5, color=RGBColor(0xFF, 0xFF, 0xFF), base_bold=True)
                shade(cell, '1C2F5C')
            for r_i, row in enumerate(body):
                cells = table.add_row().cells
                for c in range(cols):
                    cell = cells[c]
                    cell.text = ''
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    txt = row[c] if c < len(row) else ''
                    add_inline(p, txt, size=8.5)
                    if r_i % 2 == 1:
                        shade(cell, 'FAF7F2')
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue

        # ---------- blockquote
        if stripped.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(8)
            left_border(p, 'A87E00', '12')
            for j, b in enumerate(buf):
                if j:
                    p.add_run('\n')
                add_inline(p, b, size=9.5, color=MUTED)
            continue

        # ---------- bullet list
        m = re.match(r'^[-*+]\s+(.*)$', stripped)
        if m:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.55)
            p.paragraph_format.first_line_indent = Cm(-0.3)
            p.paragraph_format.space_after = Pt(3)
            p.add_run('•  ').font.color.rgb = GOLD
            add_inline(p, m.group(1))
            i += 1
            continue

        # ---------- numbered list
        m = re.match(r'^(\d+)[.)]\s+(.*)$', stripped)
        if m:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.first_line_indent = Cm(-0.35)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(f'{m.group(1)}.  ')
            r.font.color.rgb = GOLD
            r.bold = True
            add_inline(p, m.group(2))
            i += 1
            continue

        # ---------- paragraph (join wrapped lines)
        buf = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith('#') or nxt.startswith('|')
                    or nxt.startswith('```') or nxt.startswith('>-')
                    or re.match(r'^[-*+]\s', nxt) or re.match(r'^\d+[.)]\s', nxt)
                    or re.match(r'^-{3,}$', nxt)):
                break
            buf.append(nxt)
            i += 1
        p = doc.add_paragraph()
        add_inline(p, ' '.join(buf))

    doc.save(docx_path)
    return doc


def shade_para(paragraph, hex_fill):
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_fill)
    p_pr.append(shd)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python3 md_to_docx.py in.md out.docx ["Title"] ["Subtitle"]')
        sys.exit(1)
    md, out = sys.argv[1], sys.argv[2]
    t = sys.argv[3] if len(sys.argv) > 3 else None
    s = sys.argv[4] if len(sys.argv) > 4 else None
    d = build(md, out, t, s)
    print(f'OK: {out}  paragraphs={len(d.paragraphs)} tables={len(d.tables)}')
