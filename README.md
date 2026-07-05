# AI-Powered Product Review Analytics System

A full-stack analytics platform that ingests product reviews, runs multi-method sentiment analysis, extracts key topics, and generates summaries — all through a FastAPI backend and a React dashboard.

## Features

- **Dual sentiment analysis** — VADER (rule-based NLP) and a Bing Liu opinion lexicon, run side-by-side for comparison
- **Free topic extraction** — powered by YAKE (Yet Another Keyword Extractor), fully offline, no API costs
- **Free extractive summarization** — frequency-based sentence ranking to generate review summaries
- **Bulk CSV upload** — ingest large review datasets per product
- **Multi-product support** — track and compare analytics across different products independently
- **Interactive dashboard** — sentiment pie charts, topic bar charts, and AI-style summaries, built in React + Recharts

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, SQLite, pandas, VADER Sentiment, YAKE
**Frontend:** React, Axios, Recharts

## Project Structure

```bash

ai_review_analytics/
├── backend/
│   ├── main.py                  # FastAPI app & routes
│   ├── database.py              # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   ├── seed_from_kaggle.py       # Bulk-seeds products from Kaggle dataset
│   ├── backfill_topics.py         # Re-runs topic extraction on existing reviews
│   ├── requirements.txt
│   ├── data/
│   │   ├── lexicon_bing_local.csv    # Bing Liu opinion lexicon
│   │   └── 1429_1.csv                # Kaggle Amazon reviews dataset
│   └── analysis/
│       ├── sentiment.py           # VADER sentiment scoring
│       ├── lexicon_sentiment.py    # Lexicon-based sentiment scoring
│       ├── free_topics.py          # YAKE-based topic extraction
│       ├── free_summary.py         # Extractive summarization
│       └── pipeline.py             # Orchestrates per-review processing
│
└── frontend/
└── review-dashboard/
└── src/
├── App.jsx
├── api.js
└── components/
├── SentimentChart.jsx
└── TopicsChart.jsx
```

## Setup & Installation

### Backend

```bash
cd backend
python -m venv env
.\env\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
pip install requests yake
```

Run the server:
```bash
uvicorn main:app --reload --port 8001
```

API docs available at: `http://127.0.0.1:8001/docs`

### Frontend

```bash
cd frontend/review-dashboard
npm install axios recharts
npm start
```

Dashboard available at: `http://localhost:3000`

## Seeding Sample Data

To populate the database with real product reviews from a Kaggle Amazon reviews dataset:

```bash
cd backend
python seed_from_kaggle.py
```

This creates multiple distinct products, each with its own set of real reviews, sentiment analysis, and extracted topics.

To backfill topics for reviews inserted before the topic-extraction pipeline was added:

```bash
python backfill_topics.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/products` | Create a new product |
| POST | `/reviews` | Add a single review |
| POST | `/reviews/bulk-upload/{product_id}` | Bulk upload reviews via CSV |
| GET | `/products/{product_id}/reviews` | List all reviews for a product |
| GET | `/products/{product_id}/analytics` | Get sentiment breakdown, topics, and summary |

## Data Sources

- **Bing Liu Opinion Lexicon** — ~6,800 English words tagged positive/negative
- **Consumer Reviews of Amazon Products** (Datafiniti, via Kaggle) — real reviews across 48 distinct Amazon products

# AI-Powered Product Review Analytics System

🔗 **Live Demo:** [https://ai-review-analytics-wryeielflwf7u3glcnutee.streamlit.app/](https://ai-review-analytics-wryeielflwf7u3glcnutee.streamlit.app/)

*Note: The database resets on app restarts. Click "🌱 Load Sample Data" in the sidebar to populate it with sample Kaggle reviews.*

A full-stack analytics platform that ingests product reviews, runs multi-method sentiment analysis, extracts key topics, and generates summaries — all through a FastAPI backend and a React dashboard.

## Notes

- All NLP processing (sentiment, topics, summarization) runs **locally and free of cost** — no external AI API required
- SQLite is used for simplicity; swap `DATABASE_URL` in `database.py` for PostgreSQL in production
- CORS is configured to allow requests from `localhost`/`127.0.0.1` on any port

## Future Improvements

- Move to PostgreSQL for production use
- Add background job processing (Celery/RQ) for large bulk uploads
- Add authentication for multi-user support
- Add trend-over-time analytics using review timestamps
- Optional: re-enable Claude/Anthropic-powered topic extraction and summarization for higher-quality insights when API credits are available
