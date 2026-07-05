# backfill_topics.py
"""
Re-runs free topic extraction on ALL existing reviews in the database
and updates their 'topics' column. Useful for reviews that were inserted
before the free (yake-based) pipeline was in place.
Run this directly with Python (does NOT need the server running).
"""

from database import SessionLocal, Review
from analysis.free_topics import extract_topics_free

def main():
    db = SessionLocal()
    try:
        reviews = db.query(Review).all()
        print(f"Found {len(reviews)} reviews total.")

        updated = 0
        for review in reviews:
            # Only update if topics are missing/empty, to avoid redoing work unnecessarily
            if not review.topics:
                topics = extract_topics_free(review.text)
                review.topics = ",".join(topics)
                updated += 1

        db.commit()
        print(f"Updated topics for {updated} reviews (skipped {len(reviews) - updated} that already had topics).")
    finally:
        db.close()

if __name__ == "__main__":
    main()
    