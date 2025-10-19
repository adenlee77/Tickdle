from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import config
from services.hints import hints

app = Flask(__name__)
CORS(app, supports_credentials=True)

# load config & secret key
app.config.from_object(config)
app.secret_key = getattr(config, "SECRET_KEY", "change-me")

# check if all session variables are in place
def _ensure_game():
    session.setdefault("answer", app.config["DEFAULT_ANSWER"])
    session.setdefault("guesses", 0)
    session.setdefault("finished", False)
    session.setdefault("won", False)

@app.route("/start", methods=["POST"])
def start():
    # TO DO: get random ticker for day

    session["answer"] = app.config["DEFAULT_ANSWER"]
    session["guesses"] = 0
    session["finished"] = False
    session["won"] = False

    return jsonify({
        "ok": True,
        "data": {
            "guesses": session["guesses"],
            "max_guesses": app.config["MAX_GUESSES"],
        }
    }), 200


@app.route("/guess", methods=["POST"])
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
        return jsonify({"ok": True, "data": hint_data}), 200
    except Exception as e:
        print(f"[ERROR] Failed to get hints from {user_guess}: {e}")
        return jsonify({"ok": False, "error": {"code": "NO_HINTS", "message": str(e)}}), 500

@app.route("/end")
def end():
    _ensure_game()
    return jsonify({"ok": True, "message": "Game Over"})

@app.post("/reset")
def reset():
    session.clear()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)