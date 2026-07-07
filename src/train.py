"""
train.py
--------
Trains a phishing/fake-email classifier that combines:
  1. TF-IDF features over the email text
  2. Hand-crafted heuristic features (URLs, urgency words, etc.)

Usage:
    python src/train.py
"""

import os
import joblib
import pandas as pd
import numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from features import featurize_batch, FEATURE_NAMES

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "emails.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# Heuristic features are scaled up relative to TF-IDF so a strong phishing
# signal (e.g. "asks for credentials" + urgent language + a raw-IP URL)
# can't get drowned out by thousands of sparse word-frequency columns.
HEURISTIC_WEIGHT = 4.0


def build_heuristic_matrix(texts, scaler, fit=False):
    heur_dicts = featurize_batch(texts)
    raw = np.array([[d[f] for f in FEATURE_NAMES] for d in heur_dicts], dtype=float)
    scaled = scaler.fit_transform(raw) if fit else scaler.transform(raw)
    return scaled * HEURISTIC_WEIGHT


def build_feature_matrix(texts, vectorizer, scaler, fit=False):
    """Combine TF-IDF sparse matrix with scaled heuristic numeric features."""
    if fit:
        tfidf = vectorizer.fit_transform(texts)
    else:
        tfidf = vectorizer.transform(texts)

    heur_matrix = build_heuristic_matrix(texts, scaler, fit=fit)
    combined = hstack([tfidf, csr_matrix(heur_matrix)])
    return combined


def main():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows ({df['label'].sum()} phishing, {(df['label']==0).sum()} legit)")

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        df["text"].tolist(), df["label"].tolist(),
        test_size=0.2, random_state=42, stratify=df["label"]
    )

    vectorizer = TfidfVectorizer(
        max_features=1500,
        ngram_range=(1, 2),
        stop_words="english",
        lowercase=True,
        min_df=2,           # ignore words seen in only one email (reduces
                            # overfitting to one-off template artifacts)
        sublinear_tf=True,
    )
    scaler = StandardScaler()

    print("Building features...")
    X_train = build_feature_matrix(X_train_text, vectorizer, scaler, fit=True)
    X_test = build_feature_matrix(X_test_text, vectorizer, scaler, fit=False)

    print("Training model...")
    # Lower C = stronger regularization, so the model relies less on narrow
    # template-specific word combos and more on broadly recurring signal.
    clf = LogisticRegression(max_iter=1000, class_weight="balanced", C=0.5)
    clf.fit(X_train, y_train)

    print("\nEvaluating on held-out test set...")
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}\n")
    print(classification_report(y_test, y_pred, target_names=["legit", "phishing"]))
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(y_test, y_pred))

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(clf, os.path.join(MODEL_DIR, "classifier.joblib"))
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))
    print(f"\nSaved model + vectorizer + scaler to {MODEL_DIR}/")


if __name__ == "__main__":
    main()
