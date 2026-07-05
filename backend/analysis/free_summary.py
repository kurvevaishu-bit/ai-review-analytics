# analysis/free_summary.py
import re
from collections import Counter

STOPWORDS = set("""
the a an is are was were be been being to of and in on for with as at by
this that these those it its it's from or but not have has had do does did
i you he she we they my your his her our their this product item very
""".split())

def summarize_reviews_free(review_texts: list, max_sentences: int = 5) -> str:
    if not review_texts:
        return "No reviews available to summarize."

    full_text = " ".join(review_texts)
    sentences = re.split(r'(?<=[.!?])\s+', full_text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if not sentences:
        return "Not enough content to summarize."

    words = re.findall(r'\b[a-z]{3,}\b', full_text.lower())
    words = [w for w in words if w not in STOPWORDS]
    freq = Counter(words)

    def score(sentence):
        sent_words = re.findall(r'\b[a-z]{3,}\b', sentence.lower())
        if not sent_words:
            return 0
        return sum(freq.get(w, 0) for w in sent_words) / len(sent_words)

    ranked = sorted(sentences, key=score, reverse=True)
    top_sentences = ranked[:max_sentences]

    # Preserve original order for readability
    ordered = [s for s in sentences if s in top_sentences][:max_sentences]

    pos_count = sum(1 for s in sentences if any(w in s.lower() for w in ["great", "love", "excellent", "amazing", "good", "perfect"]))
    neg_count = sum(1 for s in sentences if any(w in s.lower() for w in ["bad", "poor", "terrible", "broke", "disappointed", "worst"]))

    summary = " ".join(ordered)
    tone_note = f"\n\n(Based on {len(sentences)} review sentences: roughly {pos_count} positive-leaning and {neg_count} negative-leaning mentions detected.)"
    return summary + tone_note
