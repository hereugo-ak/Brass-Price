#!/usr/bin/env python3
"""Build 3 premium style drafts (cover + problem + data) for the DTPS deck.
Blank layouts only, explicit fonts/colors - no default-template styling."""
import sys
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

W, H = Inches(13.333), Inches(7.5)
GH = "https://github.com/hereugo-ak/Brass-Price"

def rgb(s):
    return RGBColor.from_string(s)

def new_deck():
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    return prs

def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)

def box(slide, l, t, w, h):
    tx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tx.text_frame
    tf.word_wrap = True
    return tf

def para(tf, text, size, color, font="Calibri", bold=False, first=False,
         align=PP_ALIGN.LEFT, space_after=Pt(6), link=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = space_after
    r = p.add_run()
    r.text = text
    f = r.font
    f.size, f.bold, f.name = Pt(size), bold, font
    f.color.rgb = rgb(color)
    if link:
        r.hyperlink.address = link
    return p

def rule(slide, l, t, w, color, h=0.045):
    from pptx.enum.shapes import MSO_SHAPE
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = rgb(color)
    sp.line.fill.background()
    return sp

def style_table(shape, header_bg, header_tx, body_tx, band):
    tbl = shape.table
    for j, cell in enumerate(tbl.rows[0].cells):
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(header_bg)
        for p in cell.text_frame.paragraphs:
            for r in p.runs:
                r.font.size, r.font.bold = Pt(12), True
                r.font.color.rgb = rgb(header_tx)
    for i, row in enumerate(list(tbl.rows)[1:]):
        for cell in row.cells:
            if i % 2 == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgb(band)
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(14)
                    r.font.color.rgb = rgb(body_tx)

# ---------------- A: Heritage Brass ----------------
def build_a(path):
    prs = new_deck()
    B = prs.slide_layouts[6]
    # cover
    s = prs.slides.add_slide(B)
    bg(s, "17140D")
    rule(s, 1.2, 2.1, 1.6, "C9A227")
    tf = box(s, 1.2, 2.5, 10.9, 3.4)
    para(tf, "DTPS LIVE PROJECT  ·  MBA-506  ·  AMU", 14, "A89B7C",
         font="Calibri", first=True, space_after=Pt(10))
    para(tf, "Brass Guard", 64, "F5EFE0", font="Georgia", bold=True,
         space_after=Pt(8))
    para(tf, "A defensible floor for fixed-price brass export quotes.", 22,
         "F5EFE0", font="Georgia")
    tf2 = box(s, 1.2, 6.5, 10.9, 0.6)
    para(tf2, "Castle Hardwares, Aligarh (est. 1965)      github.com/hereugo-ak/Brass-Price",
         13, "A89B7C", first=True, link=None)
    # problem
    s = prs.slides.add_slide(B)
    bg(s, "F5EFE0")
    rule(s, 1.2, 0.9, 1.6, "C9A227")
    tf = box(s, 1.2, 1.3, 10.9, 1.2)
    para(tf, "01  ·  THE PROBLEM", 14, "7A5C00", bold=True, first=True,
         space_after=Pt(4))
    para(tf, "Every export quote is priced on gut feel.", 36, "221D10",
         font="Georgia", bold=True)
    tf = box(s, 1.2, 4.3, 10.9, 2.4)
    para(tf, "Castle sells finished hardware to Europe and the Middle East at fixed prices.", 20, "221D10", first=True)
    para(tf, "But the brass it will buy over the delivery period has no forward price.", 20, "221D10")
    # data
    s = prs.slides.add_slide(B)
    bg(s, "221D10")
    tf = box(s, 1.2, 0.9, 10.9, 1.0)
    para(tf, "05  ·  THE FLOOR THIS WEEK", 14, "C9A227", bold=True, first=True)
    tf = box(s, 1.2, 2.0, 5.0, 3.4)
    para(tf, "Same-day floor", 16, "A89B7C", first=True, space_after=Pt(2))
    para(tf, "₹950.40", 60, "F5EFE0", font="Georgia", bold=True,
         space_after=Pt(10))
    para(tf, "per kg, ex-works rod equivalent", 15, "A89B7C")
    shape = s.shapes.add_table(4, 2, Inches(7.0), Inches(2.0),
                               Inches(4.6), Inches(2.6))
    rows = [["HORIZON", "FLOOR"], ["Same-day", "₹950.40"],
            ["15-day", "₹964.61"], ["30-day", "₹972.54"]]
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            shape.table.cell(i, j).text = v
    style_table(shape, "C9A227", "221D10", "F5EFE0", "2E2820")
    prs.save(path)
    return path

# ---------------- B: Console Dark ----------------
def build_b(path):
    prs = new_deck()
    B = prs.slide_layouts[6]
    s = prs.slides.add_slide(B)
    bg(s, "08090A")
    tf = box(s, 1.2, 2.2, 10.9, 3.6)
    para(tf, "CASTLE HARDWARES × AMU  ·  DTPS LIVE", 13, "8B7CFF",
         font="Consolas", bold=True, first=True, space_after=Pt(12))
    para(tf, "Brass Guard", 66, "F4F4F5", bold=True, space_after=Pt(8))
    para(tf, "Weekly band + quote floor. No forecasting fairy tales.", 20,
         "A1A1AA")
    tf = box(s, 1.2, 6.5, 10.9, 0.6)
    para(tf, "github.com/hereugo-ak/Brass-Price", 13, "8B7CFF",
         font="Consolas", first=True, link=GH)
    s = prs.slides.add_slide(B)
    bg(s, "101216")
    rule(s, 1.2, 1.0, 0.9, "8B7CFF")
    tf = box(s, 1.2, 1.4, 10.9, 1.2)
    para(tf, "01 — PROBLEM", 14, "8B7CFF", font="Consolas", bold=True,
         first=True, space_after=Pt(4))
    para(tf, "Every export quote is priced on gut feel.", 36, "F4F4F5",
         bold=True)
    tf = box(s, 1.2, 4.4, 10.9, 2.2)
    para(tf, "Fixed-price sales to Europe + the Middle East.", 20, "E4E4E7", first=True)
    para(tf, "No forward price for the brass bought over delivery.", 20, "A1A1AA")
    s = prs.slides.add_slide(B)
    bg(s, "08090A")
    tf = box(s, 1.2, 0.9, 10.9, 1.0)
    para(tf, "05 — FLOOR / KG", 14, "8B7CFF", font="Consolas", bold=True,
         first=True)
    tf = box(s, 1.2, 2.0, 5.4, 3.4)
    para(tf, "SAME-DAY", 15, "71717A", font="Consolas", first=True,
         space_after=Pt(2))
    para(tf, "₹950.40", 62, "F4F4F5", font="Consolas", bold=True,
         space_after=Pt(10))
    para(tf, "15d → ₹964.61     30d → ₹972.54", 17, "A1A1AA", font="Consolas")
    shape = s.shapes.add_table(4, 2, Inches(7.4), Inches(2.0),
                               Inches(4.2), Inches(2.6))
    rows = [["HORIZON", "FLOOR"], ["same-day", "₹950.40"],
            ["15-day", "₹964.61"], ["30-day", "₹972.54"]]
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            shape.table.cell(i, j).text = v
            for p in shape.table.cell(i, j).text_frame.paragraphs:
                for r in p.runs:
                    r.font.name = "Consolas"
    style_table(shape, "8B7CFF", "08090A", "E4E4E7", "101216")
    prs.save(path)
    return path

# ---------------- C: Stripe Editorial ----------------
def build_c(path):
    prs = new_deck()
    B = prs.slide_layouts[6]
    s = prs.slides.add_slide(B)
    bg(s, "0A2540")
    tf = box(s, 1.2, 2.3, 10.9, 3.4)
    para(tf, "DTPS LIVE PROJECT  ·  MBA-506", 14, "8E9BB5", bold=True,
         first=True, space_after=Pt(10))
    para(tf, "Brass Guard", 64, "FFFFFF", bold=True, space_after=Pt(8))
    para(tf, "A defensible floor for fixed-price brass export quotes.", 22,
         "C7D2E4")
    tf = box(s, 1.2, 6.5, 10.9, 0.6)
    para(tf, "Castle Hardwares, Aligarh  ·  github.com/hereugo-ak/Brass-Price",
         13, "8E9BB5", first=True, link=GH)
    s = prs.slides.add_slide(B)
    bg(s, "FFFFFF")
    rule(s, 1.2, 1.0, 1.6, "635BFF")
    tf = box(s, 1.2, 1.4, 10.9, 1.2)
    para(tf, "1 · The problem", 14, "635BFF", bold=True, first=True,
         space_after=Pt(4))
    para(tf, "Every export quote is priced on gut feel.", 36, "0A2540",
         bold=True)
    tf = box(s, 1.2, 4.4, 10.9, 2.2)
    para(tf, "Fixed-price sales abroad; no forward price at home for the delivery period.", 20, "425466", first=True)
    s = prs.slides.add_slide(B)
    bg(s, "F6F9FC")
    tf = box(s, 1.2, 0.9, 10.9, 1.0)
    para(tf, "THE FLOOR THIS WEEK", 14, "635BFF", bold=True, first=True)
    tf = box(s, 1.2, 2.0, 5.0, 3.2)
    para(tf, "Same-day floor (per kg)", 16, "425466", first=True,
         space_after=Pt(2))
    para(tf, "₹950.40", 60, "0A2540", bold=True, space_after=Pt(10))
    para(tf, "15-day ₹964.61  ·  30-day ₹972.54", 17, "425466")
    shape = s.shapes.add_table(4, 2, Inches(7.0), Inches(2.0),
                               Inches(4.6), Inches(2.6))
    rows = [["HORIZON", "FLOOR"], ["Same-day", "₹950.40"],
            ["15-day", "₹964.61"], ["30-day", "₹972.54"]]
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            shape.table.cell(i, j).text = v
    style_table(shape, "0A2540", "FFFFFF", "0A2540", "E8EEF4")
    prs.save(path)
    return path

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    import os
    for fn in (build_a(os.path.join(out, "DTPS_style_A_heritage.pptx")),
               build_b(os.path.join(out, "DTPS_style_B_console.pptx")),
               build_c(os.path.join(out, "DTPS_style_C_stripe.pptx"))):
        print("wrote", fn)
