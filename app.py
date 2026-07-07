"""
app.py
------
Simple Flask web app to paste an email and see whether it's classified as
phishing (fake) or legitimate, with an explanation of red flags.

Run with:
    python app.py
Then open http://localhost:5000
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from flask import Flask, render_template, request
from predict import EmailClassifier

app = Flask(__name__)

try:
    model = EmailClassifier()
except FileNotFoundError:
    model = None


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    email_text = ""
    error = None

    if not model:
        error = "Model not trained yet. Run `python src/train.py` first."

    if request.method == "POST" and model:
        email_text = request.form.get("email_text", "").strip()
        if email_text:
            result = model.predict(email_text)

    return render_template("index.html", result=result, email_text=email_text, error=error)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
