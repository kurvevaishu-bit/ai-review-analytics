# main.py
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd

from database import SessionLocal, init_db, Product, Review
from schemas import ReviewIn, ReviewOut, ProductIn
from analysis.pipeline import process_review
from analysis.free_summary import summarize_reviews_free

app = FastAPI(title="AI Review Analytics API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products")
def create_product(product: ProductIn, db: Session = Depends(get_db)):
    p = Product(**product.dict())
    db.add(p); db.commit(); db.refresh(p)
    return p

@app.post("/reviews", response_model=ReviewOut)
def add_review(review: ReviewIn, db: Session = Depends(get_db)):
    r = Review(**review.dict())
    r = process_review(r)
    db.add(r); db.commit(); db.refresh(r)
    return r

@app.post("/reviews/bulk-upload/{product_id}")
def bulk_upload(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    df = pd.read_csv(file.file)
    df.columns = [c.strip().lower() for c in df.columns]

    text_col = "text" if "text" in df.columns else "review" if "review" in df.columns else None
    if text_col is None:
        return {"error": "CSV must have a 'text' or 'review' column"}

    rating_col = "rating" if "rating" in df.columns else None

    count = 0
    for _, row in df.iterrows():
        rating_val = row[rating_col] if rating_col else None
        r = Review(product_id=product_id, text=str(row[text_col]), rating=rating_val)
        r = process_review(r)
        db.add(r)
        count += 1
    db.commit()
    return {"inserted": count}

@app.get("/products/{product_id}/analytics")
def get_analytics(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    if not reviews:
        return {"message": "No reviews found"}

    total = len(reviews)
    pos = sum(1 for r in reviews if r.sentiment_label == "positive")
    neg = sum(1 for r in reviews if r.sentiment_label == "negative")
    neu = total - pos - neg

    lex_pos = sum(1 for r in reviews if r.lexicon_label == "positive")
    lex_neg = sum(1 for r in reviews if r.lexicon_label == "negative")
    lex_neu = total - lex_pos - lex_neg

    topic_counts = {}
    for r in reviews:
        for t in (r.topics or "").split(","):
            t = t.strip()
            if t:
                topic_counts[t] = topic_counts.get(t, 0) + 1

    summary = summarize_reviews_free([r.text for r in reviews]) 

    return {
        "total_reviews": total,
        "sentiment_breakdown": {"positive": pos, "negative": neg, "neutral": neu},
        "lexicon_breakdown": {"positive": lex_pos, "negative": lex_neg, "neutral": lex_neu},
        "top_topics": sorted(topic_counts.items(), key=lambda x: -x[1])[:10],
        "ai_summary": summary
    }

@app.get("/products/{product_id}/reviews", response_model=list[ReviewOut])
def list_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.product_id == product_id).all()
