from flask import Flask, request, jsonify, redirect, url_for, session, Response
from flask_cors import CORS
import requests
import config
import secrets
import yfinance as yf
from services.hints import hints
from services.get_ticker import get_daily_ticker

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# load config & secret key
app.config.from_object(config)
app.secret_key = getattr(config, "SECRET_KEY", secrets.token_hex(32))

# check if all session variables are in place
def _ensure_game():
    session.setdefault("answer", get_daily_ticker())
    session.setdefault("guesses", 0)
    session.setdefault("finished", False)
    session.setdefault("won", False)

# check if ticker exists
def ticker_exists(symbol: str) -> bool:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # 'shortName' exists for valid tickers; for bad ones, info is often empty or minimal
        return bool(info and info.get("shortName"))
    except Exception:
        return False

# if user refreshes on the frontend /play url it redirects them to start over
@app.route("/play")
def return_home():
    return redirect("/")

@app.route("/api/start", methods=["POST"])
def start():
    daily_ticker = get_daily_ticker()
    session["answer"] = daily_ticker
    session["guesses"] = 0
    session["finished"] = False
    session["won"] = False

    return jsonify({
        "ok": True,
        "data": {
            "guesses": session["guesses"],
            "max_guesses": app.config["MAX_GUESSES"],
            "ticker": get_daily_ticker(),
        }
    }), 200

@app.route("/api/chart", methods=["GET"])
def chart():
    _ensure_game()
    ticker = session["answer"]
    url = f"https://finviz.com/chart.ashx?t={ticker}&p=d"

    # needed to make finviz request to look like a browser request
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://finviz.com/",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "image/png")
        return Response(r.content, mimetype=ctype)
    except Exception as e:
        print(f"[ERROR] Chart fetch failed: {e}")
        return jsonify({"ok": False, "error": "CHART_FAILED"}), 500


@app.route("/api/guess", methods=["POST"])
def guess():
    _ensure_game()

    payload = request.get_json(silent=True) or {}
    user_guess = (payload.get("ticker") or "").strip().upper()
    if not user_guess:
        return jsonify({"ok": False, "error": {"code": "EMPTY_TICKER", "message": "Ticker is required."}}), 400

    answer = session["answer"]

    # validate ticker existence
    if not ticker_exists(user_guess):
        return jsonify({
            "ok": False,
            "error": {"code": "INVALID_TICKER", "message": f"Ticker '{user_guess}' does not exist."}
        }), 422

    # win
    if user_guess == answer:
        session["guesses"] = int(session.get("guesses", 0)) + 1
        session["won"] = True
        session["finished"] = True
        return redirect(url_for("end"))

    # build hints. if this fails (e.g., no ticker), dont consume a guess.
    try:
        hint_data = hints(user_guess, answer)
    # case where we subtract something from none (will happen if no data can be got for a field)
    except TypeError as e:
        print(f"[ERROR] Hints TypeError for {user_guess}: {e}")
        return jsonify({
            "ok": False,
            "error": {"code": "INCOMPLETE_DATA", "message": f"Ticker '{user_guess}' is missing data. Try another ticker."}
        }), 422
    except Exception as e:
        print(f"[ERROR] Failed to get hints from {user_guess}: {e}")
        return jsonify({"ok": False, "error": {"code": "NO_HINTS", "message": str(e)}}), 500
    
    required = ("price", "day_high", "day_low", "avg_volume", "market_cap")
    if any(hint_data.get(k) is None for k in required):
        return jsonify({
            "ok": False,
            "error": {"code": "INCOMPLETE_DATA", "message": f"Ticker '{user_guess}' is missing data. Try another ticker."}
        }), 422

    # valid (but wrong) guess
    session["guesses"] = int(session.get("guesses", 0)) + 1
    guesses = session["guesses"]

    # lose
    if guesses >= app.config["MAX_GUESSES"]:
        session["won"] = False
        session["finished"] = True
        return redirect(url_for("end"))

    return jsonify({
        "ok": True,
        "guesses left": int(app.config["MAX_GUESSES"]) - guesses,
        "data": hint_data
    }), 200

@app.route("/api/end", methods=["GET", "POST"])
def end():
    _ensure_game()
    left = int(app.config["MAX_GUESSES"]) - int(session.get("guesses", 0))
    return jsonify({
        "ok": True,
        "message": "Game Over",
        "win": session["won"],
        "guesses": session["guesses"],
        "guesses left": left
    })

@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)