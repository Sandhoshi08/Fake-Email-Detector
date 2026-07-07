# Fake / Phishing Email Detector

A complete, runnable project that classifies emails as **phishing (fake)** or
**legitimate**, combining a machine-learning text classifier with
explainable, rule-based heuristics (suspicious links, urgency language,
credential requests, etc). Includes a CLI and a local web app.

## How it works

1. **`data/emails.csv`** — a labeled dataset of emails (`text`, `label`).
   A synthetic dataset generator is included so the project runs
   out-of-the-box, but you should swap in a real dataset for serious use
   (see "Using a real dataset" below).
2. **`src/features.py`** — extracts hand-crafted heuristic signals from
   an email: number of links, raw-IP URLs, URL shorteners, urgency
   language, requests for credentials, generic greetings, etc.
3. **`src/train.py`** — builds a TF-IDF representation of the email text,
   combines it with the scaled heuristic features, and trains a Logistic
   Regression classifier. Prints accuracy/precision/recall on a held-out
   test set and saves the model to `models/`.
4. **`src/predict.py`** — loads the trained model and scores new email
   text, returning a label, a confidence score, and a human-readable list
   of red flags.
5. **`app.py`** — a small Flask web app so you can paste an email and see
   the verdict in a browser.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

**1. Generate the training data (synthetic, ~800 emails):**
```bash
python src/generate_dataset.py
```

**2. Train the model:**
```bash
cd src
python train.py
```
This prints accuracy and a classification report, and saves the trained
model, vectorizer, and scaler into `models/`.

**3a. Classify an email from the command line:**
```bash
python predict.py "Dear customer, your account will be suspended unless you verify your password at http://secure-login-check.com within 24 hours."
```

**3b. Or run the web app:**
```bash
cd ..
python app.py
```
Then open **http://localhost:5000** and paste an email to scan it.

## Using a real dataset

The synthetic dataset is intentionally simple so the project trains fast
and demonstrates the pipeline end-to-end. For a stronger, production-grade
model, replace `data/emails.csv` with a real labeled dataset, keeping the
same two columns:

```
text,label
"Subject: ... email body ...",1
"Subject: ... email body ...",0
```

(`label = 1` for phishing/fake, `0` for legitimate). Good public sources
include Kaggle's "Phishing Email Dataset" and the classic Enron-Spam
corpus. Once replaced, just re-run `python src/train.py`.

## Project structure

```
fake_email_detector/
├── app.py                  # Flask web app
├── requirements.txt
├── data/
│   └── emails.csv           # training data (generated or your own)
├── models/                  # saved classifier/vectorizer/scaler (after training)
├── templates/
│   └── index.html            # web UI
└── src/
    ├── generate_dataset.py  # synthetic dataset generator
    ├── features.py           # heuristic feature extraction
    ├── train.py               # model training
    └── predict.py             # inference (CLI + used by app.py)
```

## Ideas for extending this project

- Swap Logistic Regression for a Random Forest or Gradient Boosting model
  and compare performance.
- Add features based on the sender's domain, SPF/DKIM headers, or
  attachment types if you have access to raw `.eml` files.
- Add a browser extension or Gmail add-on that calls this model via a
  small API.
- Track false positives/negatives over time and retrain periodically.
- Add explainability with SHAP values instead of hand-written red flags.

## Notes on limitations

This project is built for learning and experimentation. The included
synthetic dataset captures common phishing patterns but is not a
substitute for a large, real-world labeled corpus, and no classifier here
is a substitute for security tools like spam filters, email authentication
(SPF/DKIM/DMARC), and user training in a real deployment.
