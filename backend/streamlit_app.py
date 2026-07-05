# streamlit_app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px

from database import SessionLocal, init_db, Product, Review
from analysis.pipeline import process_review
from analysis.free_summary import summarize_reviews_free

st.set_page_config(page_title="AI Review Analytics", layout="wide")
init_db()


def get_db():
    return SessionLocal()


def get_all_products(db):
    return db.query(Product).all()


def products_with_review_counts(db, products):
    result = {}
    for p in products:
        count = db.query(Review).filter(Review.product_id == p.id).count()
        if count > 0:
            result[f"{p.id} — {p.name} ({count} reviews)"] = p.id
    return result


def compute_analytics(db, product_id):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()

    if not reviews:
        return None

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
        "ai_summary": summary,
        "reviews": reviews,
    }


def pie_chart(data_dict, title):
    df = pd.DataFrame(list(data_dict.items()), columns=["Sentiment", "Count"])
    df = df[df["Count"] > 0]
    if df.empty:
        st.info(f"No data for {title}")
        return
    fig = px.pie(
        df, names="Sentiment", values="Count", title=title,
        color="Sentiment",
        color_discrete_map={"positive": "#22c55e", "negative": "#ef4444", "neutral": "#94a3b8"}
    )
    st.plotly_chart(fig, use_container_width=True)


def seed_sample_data(db, max_products=5, max_reviews_per_product=15):
    csv_path = os.path.join(os.path.dirname(__file__), "data", "1429_1.csv")
    if not os.path.exists(csv_path):
        st.sidebar.error(f"Sample dataset not found at {csv_path}")
        return None

    df = pd.read_csv(csv_path, low_memory=False)
    df = df.dropna(subset=["reviews.text", "name"])

    top_products = df["name"].value_counts().head(max_products).index.tolist()

    created = []
    for product_name_raw in top_products:
        clean = product_name_raw.split("\r\n")[0].split(",,,")[0].strip()[:150]

        p = Product(name=clean, category="Amazon Devices")
        db.add(p)
        db.commit()
        db.refresh(p)

        subset = df[df["name"] == product_name_raw].head(max_reviews_per_product)
        for _, row in subset.iterrows():
            r = Review(
                product_id=p.id,
                text=str(row["reviews.text"]),
                rating=row.get("reviews.rating")
            )
            r = process_review(r)
            db.add(r)
        db.commit()
        created.append((p.id, clean))

    st.sidebar.success(f"Created {len(created)} sample products!")
    return created


# ---------------- Sidebar ----------------
st.sidebar.title("📊 AI Review Analytics")

db = get_db()
products = get_all_products(db)

st.sidebar.subheader("Quick Start")
if st.sidebar.button("🌱 Load Sample Data (Kaggle Amazon Reviews)"):
    with st.spinner("Seeding sample products..."):
        seed_sample_data(db)
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("Select a Product")
product_options = products_with_review_counts(db, products)
selected_label = st.sidebar.selectbox(
    "Existing products (with reviews)",
    options=["-- none --"] + list(product_options.keys())
)
selected_product_id = product_options.get(selected_label)

st.sidebar.subheader("Create New Product")
new_name = st.sidebar.text_input("Product name")
new_category = st.sidebar.text_input("Category")
if st.sidebar.button("Create Product"):
    if new_name:
        p = Product(name=new_name, category=new_category)
        db.add(p)
        db.commit()
        db.refresh(p)
        st.sidebar.success(f"Created product ID {p.id}")
        st.rerun()
    else:
        st.sidebar.error("Enter a product name first.")

st.sidebar.subheader("Upload Reviews CSV")
upload_target_id = st.sidebar.number_input(
    "Target Product ID", min_value=1, step=1, value=selected_product_id or 1
)
uploaded_file = st.sidebar.file_uploader("Choose CSV", type=["csv"])
if st.sidebar.button("Upload & Analyze"):
    if uploaded_file is None:
        st.sidebar.error("Choose a CSV file first.")
    else:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        text_col = "text" if "text" in df.columns else "review" if "review" in df.columns else None
        if text_col is None:
            st.sidebar.error("CSV must have a 'text' or 'review' column.")
        else:
            rating_col = "rating" if "rating" in df.columns else None
            count = 0
            for _, row in df.iterrows():
                rating_val = row[rating_col] if rating_col else None
                r = Review(product_id=int(upload_target_id), text=str(row[text_col]), rating=rating_val)
                r = process_review(r)
                db.add(r)
                count += 1
            db.commit()
            st.sidebar.success(f"Inserted {count} reviews into product {upload_target_id}")
            st.rerun()

# ---------------- Main area ----------------
st.title("AI-Powered Product Review Analytics")

if not selected_product_id:
    st.info("👈 Select or create a product from the sidebar to view analytics.")
else:
    analytics = compute_analytics(db, selected_product_id)
    if analytics is None:
        st.warning("No reviews found for this product yet. Upload a CSV from the sidebar.")
    else:
        st.metric("Total Reviews", analytics["total_reviews"])

        col1, col2 = st.columns(2)
        with col1:
            pie_chart(analytics["sentiment_breakdown"], "VADER Sentiment")
        with col2:
            pie_chart(analytics["lexicon_breakdown"], "Lexicon Sentiment")

        st.subheader("Top Topics")
        if analytics["top_topics"]:
            topics_df = pd.DataFrame(analytics["top_topics"], columns=["Topic", "Count"])
            fig = px.bar(topics_df, x="Count", y="Topic", orientation="h")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No topics extracted yet for this product.")

        st.subheader("Summary")
        st.info(analytics["ai_summary"])

        with st.expander("View all reviews"):
            reviews_df = pd.DataFrame([{
                "text": r.text,
                "rating": r.rating,
                "sentiment": r.sentiment_label,
                "lexicon": r.lexicon_label,
                "topics": r.topics
            } for r in analytics["reviews"]])
            st.dataframe(reviews_df, use_container_width=True)

db.close()