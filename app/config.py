"""Settings and the feed registry.

Everything the product measures comes from a feed declared here. A feed that
cannot be automated is declared MANUAL rather than being quietly skipped —
that honesty is a product requirement, not a technical detail.
"""
from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
DB_PATH = pathlib.Path(os.environ.get('BRASS_DB', ROOT / 'brass.db'))

# ----------------------------------------------------------------- model defaults
# These are the inputs to the frozen engine. They are stored per-run in
# model_input so that any floor produced by the product can be reproduced.
DEFAULT_METAL_INR_KG = 983.65      # 0.615*MCX Cu + 0.385*MCX Zn, 2026-11-11
DEFAULT_RATIO = 0.876              # bartan + honey + purja, n=16
DEFAULT_RATIO_SD = 0.039
DEFAULT_MARGIN = 0.05
DEFAULT_TRANSPORT_INR_KG = 0.39    # Delhi 130 km x Rs3/t-km — UNVERIFIED rate
DEFAULT_RATE_INR_PER_T_KM = 3.0
W_CU = 0.615

CITIES_KM = {
    'moradabad': 120, 'delhi': 130, 'jaipur': 250,
    'ahmedabad': 950, 'jamnagar': 1270, 'mumbai': 1340,
}

# ----------------------------------------------------------------- feed registry
OK = 'OK'
STALE = 'STALE'
BLOCKED = 'BLOCKED'
FAILED = 'FAILED'
MANUAL = 'MANUAL'


@dataclass(frozen=True)
class Feed:
    """One data series and how it is obtained."""
    key: str                      # canonical series name, e.g. 'mcx.copper'
    label: str                    # human name
    mode: str                     # 'auto' | 'manual'
    freq: str                     # 'daily' | 'weekly' | 'monthly' | 'event'
    lag_days: int                 # how stale before we flag it
    unit: str
    source: str
    # for manual feeds: what the upload screen should ask for
    template: tuple[str, ...] = field(default=())
    note: str = ''


FEEDS: tuple[Feed, ...] = (
    Feed('fred.DEXINUS', 'USD / INR', 'auto', 'daily', 7, 'INR per USD',
         'FRED H.10'),
    Feed('fred.PCOPPUSDM', 'IMF copper', 'auto', 'monthly', 70, 'USD per tonne',
         'FRED / IMF'),
    Feed('fred.PZINCUSDM', 'IMF zinc', 'auto', 'monthly', 70, 'USD per tonne',
         'FRED / IMF'),
    Feed('fred.DCOILBRENTEU', 'Brent crude', 'auto', 'daily', 7, 'USD per barrel',
         'FRED / EIA'),
    Feed('fred.DEXUSEU', 'USD / EUR', 'auto', 'daily', 7, 'USD per EUR',
         'FRED H.10'),
    Feed('ecb.usd_eur', 'ECB euro reference', 'auto', 'daily', 7, 'USD per EUR',
         'European Central Bank'),
    Feed('cftc.copper_cot', 'COMEX copper COT', 'auto', 'weekly', 14, 'contracts',
         'CFTC'),

    Feed('mcx.copper', 'MCX copper close', 'manual', 'daily', 7, 'INR per kg',
         'MCX bhavcopy', template=('date', 'close_inr'), note=(
             'MCX blocks automated requests (HTTP 403). Open mcxindia.com in a '
             'browser, Market Data -> Bhavcopy, select the table, paste into '
             'Excel, save as CSV, then upload it here.')),
    Feed('mcx.zinc', 'MCX zinc close', 'manual', 'daily', 7, 'INR per kg',
         'MCX bhavcopy', template=('date', 'close_inr')),
    Feed('wpi.brass_index', 'WPI brass index', 'manual', 'monthly', 45, 'index 2011-12=100',
         'OEA / DPIIT', template=('month', 'brass_index'), note=(
             'eaindustry.nic.in -> monthly index workbook, row 596 '
             '"Brass metal/sheet/coils", code 1314090011.')),
    Feed('board.brass_prices', 'Brass board prices', 'manual', 'weekly', 14, 'INR per kg',
         'domestic boards', template=('date', 'grade', 'price_inr_kg', 'source'),
         note='MTLEXS / AajBazar / Steel-Baba / ShreeMetalPrices / PTI.'),
    Feed('owner.brass_rate', 'Castle brass rate', 'manual', 'weekly', 21, 'INR per kg',
         'Castle purchase', template=('week', 'price_inr_kg'), note=(
             'One figure a week from the purchase man turns the ratio into a '
             'tracked series. Optional, but it is what tightens the floor.')),
    Feed('owner.transport', 'Transport rate', 'manual', 'event', 180, 'INR per tonne-km',
         'Castle freight bill', template=('km', 'rate_inr_per_t_km'), note=(
             'One freight bill replaces the assumed Rs3/tonne-km.')),
)

FEED_BY_KEY = {f.key: f for f in FEEDS}
AUTO_FEEDS = tuple(f for f in FEEDS if f.mode == 'auto')
MANUAL_FEEDS = tuple(f for f in FEEDS if f.mode == 'manual')


@dataclass
class Settings:
    db_path: pathlib.Path = DB_PATH
    data_dir: pathlib.Path = DATA
    root: pathlib.Path = ROOT
    enqueue_network: bool = True


SETTINGS = Settings()
