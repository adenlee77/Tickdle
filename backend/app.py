from flask import Flask, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import config
from services.hints import hints

app = Flask(__name__)
CORS(app)

GUESSES = 0 # temp for testing
TODAY_ANSWER = "AAPL" # temp for testing

@app.route("/start", methods=["POST"])
def start():
    pass

@app.route("/guess", methods=["POST"])
def guess():

    # get the user input
    user_guess = request.get_json().get('ticker').upper()

    # increment guess count
    global GUESSES
    GUESSES += 1

    # win/lose condition
    if user_guess == TODAY_ANSWER or GUESSES >= app.config["MAX_GUESSES"]:
        return redirect(url_for("end"))
    
    # produce hints
    try:
        hint_data = hints(user_guess, TODAY_ANSWER)
        return jsonify({"ok": True, "data": hint_data}), 200
    except Exception as e:
        print(f"[ERROR] Failed to get hints from {user_guess}: {e}")
        return jsonify({"ok": False, "error": {"code": "NO_HINTS", "message": str(e)}}), 500

@app.route("/end", methods=["POST"])
def end():
    return jsonify({"ok": True, "message": "Game Over"})

if __name__ == "__main__":
    app.run()