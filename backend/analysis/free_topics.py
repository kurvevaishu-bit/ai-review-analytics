# analysis/free_topics.py
import yake

_extractor = yake.KeywordExtractor(
    lan="en",
    n=2,              # only 2-word phrases (bigrams) — filters out single generic words
    top=5,
    dedupLim=0.6,
    windowsSize=1
)

GENERIC_WORDS = {
    "great", "good", "nice", "product", "friend", "people", "sales",
    "really", "very", "much", "thing", "things", "item", "buy", "bought"
}

def extract_topics_free(text: str) -> list:
    try:
        keywords = _extractor.extract_keywords(text)
        results = []
        for phrase, score in keywords:
            words = phrase.lower().split()
            # Skip if ALL words in the phrase are generic filler
            if all(w in GENERIC_WORDS for w in words):
                continue
            # Skip single-word results entirely (n=2 should prevent most, but just in case)
            if len(words) < 2:
                continue
            results.append(phrase)
        return results[:3]
    except Exception as e:
        print(f"[extract_topics_free] failed: {e}")
        return []
    
    