# analysis/lexicon_sentiment.py
import os
import csv

LEXICON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lexicon_bing_local.csv")

_positive_words = set()
_negative_words = set()
_loaded = False

def _load_lexicon():
    global _loaded
    if _loaded:
        return
    with open(LEXICON_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row["word"].strip().lower()
            sentiment = row["sentiment"].strip().lower()
            if sentiment == "positive":
                _positive_words.add(word)
            elif sentiment == "negative":
                _negative_words.add(word)
    _loaded = True

def lexicon_score(text: str):
    _load_lexicon()
    words = [w.strip(".,!?;:\"'()") for w in text.lower().split()]
    pos_hits = sum(1 for w in words if w in _positive_words)
    neg_hits = sum(1 for w in words if w in _negative_words)
    total = pos_hits + neg_hits
    if total == 0:
        return "neutral", 0.0
    score = (pos_hits - neg_hits) / total
    label = "positive" if score > 0.1 else "negative" if score < -0.1 else "neutral"
    return label, score
