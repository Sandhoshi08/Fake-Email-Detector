"""
features.py
------------
Hand-crafted heuristic features that are well known indicators of phishing
emails. These are combined with TF-IDF text features in train.py to build a
stronger, more interpretable model than text-only approaches.
"""

import re

URGENT_WORDS = [
    "urgent", "immediately", "verify", "suspend", "suspended", "confirm",
    "act now", "final notice", "limited time", "click here", "act immediately",
    "locked", "restricted", "unusual activity", "act fast", "expire",
    "expires", "winner", "won", "congratulations", "free", "prize", "claim",
]

MONEY_PATTERN = re.compile(r"\$\s?\d+|\d+\s?(usd|dollars)", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s]+")
IP_URL_PATTERN = re.compile(r"https?://\d{1,3}(\.\d{1,3}){3}")
SHORTENER_PATTERN = re.compile(r"(bit\.ly|tinyurl|goo\.gl|t\.co|is\.gd)", re.IGNORECASE)


def extract_heuristic_features(text: str) -> dict:
    """Return a dict of numeric heuristic features for a single email body."""
    text_lower = text.lower()

    urls = URL_PATTERN.findall(text)
    num_urls = len(urls)
    has_ip_url = 1 if IP_URL_PATTERN.search(text) else 0
    has_shortener = 1 if SHORTENER_PATTERN.search(text) else 0

    urgent_word_count = sum(1 for w in URGENT_WORDS if w in text_lower)
    has_money_mention = 1 if MONEY_PATTERN.search(text) else 0

    exclamation_count = text.count("!")
    num_caps_words = len(re.findall(r"\b[A-Z]{3,}\b", text))

    generic_greeting = 1 if re.search(
        r"\b(dear customer|dear user|dear valued|dear account holder)\b",
        text_lower,
    ) else 0

    asks_for_credentials = 1 if re.search(
        r"\b(password|login|credentials|ssn|social security|card number|pin)\b",
        text_lower,
    ) else 0

    return {
        "num_urls": num_urls,
        "has_ip_url": has_ip_url,
        "has_shortener": has_shortener,
        "urgent_word_count": urgent_word_count,
        "has_money_mention": has_money_mention,
        "exclamation_count": exclamation_count,
        "num_caps_words": num_caps_words,
        "generic_greeting": generic_greeting,
        "asks_for_credentials": asks_for_credentials,
        "length": len(text),
    }


FEATURE_NAMES = [
    "num_urls", "has_ip_url", "has_shortener", "urgent_word_count",
    "has_money_mention", "exclamation_count", "num_caps_words",
    "generic_greeting", "asks_for_credentials", "length",
]


def featurize_batch(texts):
    """Turn a list of raw email strings into a list of feature-dicts."""
    return [extract_heuristic_features(t) for t in texts]
