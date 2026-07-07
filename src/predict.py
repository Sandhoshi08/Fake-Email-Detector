"""
predict.py
----------
Loads the trained model + vectorizer and scores new/unseen email text.

CLI usage:
    python src/predict.py "Dear customer, your account will be suspended..."
"""

import os
import sys
import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix

from features import extract_heuristic_features, FEATURE_NAMES

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
HEURISTIC_WEIGHT = 4.0  # must match the value used in train.py


class EmailClassifier:
    def __init__(self):
        clf_path = os.path.join(MODEL_DIR, "classifier.joblib")
        vec_path = os.path.join(MODEL_DIR, "vectorizer.joblib")
        scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
        if not (os.path.exists(clf_path) and os.path.exists(vec_path) and os.path.exists(scaler_path)):
            raise FileNotFoundError(
                "Model not found. Run `python src/train.py` first to train it."
            )
        self.clf = joblib.load(clf_path)
        self.vectorizer = joblib.load(vec_path)
        self.scaler = joblib.load(scaler_path)

    def predict(self, text: str) -> dict:
        tfidf = self.vectorizer.transform([text])
        heur = extract_heuristic_features(text)
        heur_vec = np.array([[heur[f] for f in FEATURE_NAMES]], dtype=float)
        heur_scaled = self.scaler.transform(heur_vec) * HEURISTIC_WEIGHT
        combined = hstack([tfidf, csr_matrix(heur_scaled)])

        label = int(self.clf.predict(combined)[0])
        proba = self.clf.predict_proba(combined)[0]
        phishing_confidence = float(proba[1])

        # Which heuristic red flags fired, for an explainable result
        red_flags = []
        if heur["num_urls"] > 0:
            red_flags.append(f"Contains {heur['num_urls']} link(s)")
        if heur["has_ip_url"]:
            red_flags.append("Link uses a raw IP address instead of a domain")
        if heur["has_shortener"]:
            red_flags.append("Uses a URL shortener")
        if heur["urgent_word_count"] > 0:
            red_flags.append(f"Contains {heur['urgent_word_count']} urgency/pressure word(s)")
        if heur["has_money_mention"]:
            red_flags.append("Mentions a specific dollar amount")
        if heur["generic_greeting"]:
            red_flags.append("Uses a generic greeting (e.g. 'Dear Customer')")
        if heur["asks_for_credentials"]:
            red_flags.append("Asks for password/credentials/personal info")
        if heur["num_caps_words"] > 2:
            red_flags.append("Excessive use of ALL-CAPS words")

        return {
            "label": "phishing" if label == 1 else "legit",
            "phishing_confidence": round(phishing_confidence, 4),
            "red_flags": red_flags,
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python src/predict.py "email text here"')
        sys.exit(1)

    text = " ".join(sys.argv[1:])
    model = EmailClassifier()
    result = model.predict(text)

    print(f"\nPrediction: {result['label'].upper()}")
    print(f"Phishing confidence: {result['phishing_confidence']*100:.1f}%")
    if result["red_flags"]:
        print("Red flags detected:")
        for flag in result["red_flags"]:
            print(f"  - {flag}")
    else:
        print("No obvious red flags detected.")
