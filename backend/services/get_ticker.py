import json
import random
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
import config
import secrets

TICKERS_FILE = "tickers.json"
DAILY_TICKER_SECRET = getattr(config, "SECRET_KEY", secrets.token_hex(32))
LOCAL_TZ = ZoneInfo("America/Toronto")
ANCHOR_DATE = getattr(config, "ANCHOR_DATE")

def load_tickers():
    with open(TICKERS_FILE, "r") as f:
        return json.load(f)

def build_stable_permutation(symbols):
    # make the list string stable (no spaces differences etc.)
    symbols_str = "|".join(symbols)
    seed_bytes = f"{DAILY_TICKER_SECRET}|{symbols_str}".encode()
    h = hashlib.sha256(seed_bytes).hexdigest()
    # use a 32-bit seed for random.Random
    seed = int(h[:8], 16)
    rng = random.Random(seed)
    order = symbols[:]
    rng.shuffle(order)
    return order

def days_since_anchor():
    # today according to your chosen timezone
    today_local = datetime.now(LOCAL_TZ).date()
    return (today_local - ANCHOR_DATE).days

def get_daily_ticker():
    rows = load_tickers()
    if not rows:
        raise RuntimeError("tickers.json is empty.")
    symbols = [r["ticker"] for r in rows]

    # build a deterministic permutation
    order = build_stable_permutation(symbols)

    idx = days_since_anchor() % len(order)
    return order[idx]