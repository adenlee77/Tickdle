import time
import yfinance as yf
from typing import Optional, Dict

CACHE_TTL = 600
_cache: Dict[str, Dict] = {}

def _get_cached(symbol: str) -> Optional[Dict]:
    rec = _cache.get(symbol)
    if not rec:
        return None
    if time.time() - rec["ts"] > CACHE_TTL:
        _cache.pop(symbol, None)
        return None
    return rec["data"]


def _set_cached(symbol: str, data: Dict):
    _cache[symbol] = {"data": data, "ts": time.time()}


def get_meta(symbol: str) -> Dict:
    symbol = symbol.upper()
    cached = _get_cached(symbol)
    if cached:
        return cached

    try:
        t = yf.Ticker(symbol)
        fast = t.get_fast_info
        meta = {
            "Price": fast["lastPrice"],
            "Day High": fast["dayHigh"],
            "Day Low": fast["dayLow"],
            "Average Volume": fast["averageVolume"],
            "Market Cap": fast["marketCap"],
            "Dividend Yield": fast["dividendYield"]
        }

        _set_cached(symbol, meta)
        return meta
    except Exception as e:
        print(f"[WARn] yfinance failed to fetch for {symbol}: {e}")
    