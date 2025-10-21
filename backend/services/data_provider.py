import redis
import yfinance as yf
import json
from config import REDIS_URL, CACHE_TTL

r = redis.from_url(REDIS_URL, decode_responses=True)

def get_meta(symbol: str):
    symbol = symbol.upper()
    key = f"meta:{symbol}"

    # try Redis cache
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    # fetch fresh data
    t = yf.Ticker(symbol)
    fast = t.get_fast_info()
    info = {}
    try:
        info = t.info
    except Exception:
        pass

    meta = {
        "Price": fast.get("lastPrice"),
        "Day High": fast.get("dayHigh"),
        "Day Low": fast.get("dayLow"),
        "Average Volume": info.get("averageVolume"),
        "Market Cap": fast.get("marketCap"),
    }

    # store result in Redis with TTL
    r.setex(key, CACHE_TTL, json.dumps(meta))
    return meta