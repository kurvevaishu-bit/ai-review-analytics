# analysis/pipeline.py
from analysis.sentiment import analyze_sentiment
from analysis.lexicon_sentiment import lexicon_score
from analysis.free_topics import extract_topics_free

def process_review(review):
    label, score = analyze_sentiment(review.text)
    review.sentiment_label = label
    review.sentiment_score = score

    lex_label, lex_score = lexicon_score(review.text)
    review.lexicon_label = lex_label
    review.lexicon_score = lex_score

    topics = extract_topics_free(review.text)
    review.topics = ",".join(topics)
    return review

