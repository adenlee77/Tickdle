from flask import Flask, request, jsonify, redirect, url_for, session, Response
from flask_cors import CORS
import requests
import config
import secrets
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

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise Exception(f"Bad status {r.status_code}")
        
        return Response(r.content, mimetype="image/png")
    except Exception as e:
        return jsonify({"ok": False, "error": "CHART_FAILED"}), 500


@app.route("/api/guess", methods=["POST"])
def guess():
    _ensure_game()

    # get the user input
    user_guess = request.get_json().get('ticker').upper()

    # get session variables and increment guesses
    answer = session["answer"]
    session["guesses"] = 1 + int(session.get("guesses", 0))
    guesses = session["guesses"]

    # win condition
    if user_guess == answer:
        session["won"] = True
        session["finished"] = True
        return redirect(url_for("end"))
    
    # lose condition
    if guesses >= app.config["MAX_GUESSES"]:
        session["won"] = False
        session["finished"] = True
        return redirect(url_for("end"))
    
    # produce hints
    try:
        hint_data = hints(user_guess, answer)
        return jsonify({"ok": True, "guesses left": int(app.config["MAX_GUESSES"]) - int(session["guesses"]), "data": hint_data}), 200
    except Exception as e:
        print(f"[ERROR] Failed to get hints from {user_guess}: {e}")
        return jsonify({"ok": False, "error": {"code": "NO_HINTS", "message": str(e)}}), 500

@app.route("/api/end", methods=["POST"])
def end():
    _ensure_game()
    return jsonify({"ok": True, "message": "Game Over", "win": session["won"], "guesses": session["guesses"]})

@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)