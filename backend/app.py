from flask import Flask
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app)

GUESSES = 0

@app.route("/start", methods=["POST"])

@app.route("/guess", methods=["POST"])

@app.route("/end", methods=["POST"])

if __name__ == "__main__":
    app.run()