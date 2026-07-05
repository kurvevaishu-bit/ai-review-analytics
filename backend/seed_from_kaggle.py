# seed_from_kaggle.py
"""
Reads the Kaggle Amazon reviews CSV, groups reviews by product,
creates a Product + bulk-uploads its reviews via your own running API.
Run this while your FastAPI server (uvicorn) is already running.
"""

import pandas as pd
import requests
import time

API_BASE = "http://localhost:8001"
CSV_PATH = "data/1429_1.csv"

# Limit how many products / reviews per product to keep AI API usage small.
# Increase these once you have more Anthropic credits.
MAX_PRODUCTS = 5
MAX_REVIEWS_PER_PRODUCT = 15

def clean_name(raw_name: str) -> str:
    # Some product names in this dataset repeat themselves with \r\n — clean that up
    return raw_name.split("\r\n")[0].split(",,,")[0].strip()[:150]

def main():
    df = pd.read_csv(CSV_PATH, low_memory=False)
    df = df.dropna(subset=["reviews.text", "name"])

    top_products = df["name"].value_counts().head(MAX_PRODUCTS).index.tolist()

    for product_name_raw in top_products:
        clean = clean_name(product_name_raw)
        subset = df[df["name"] == product_name_raw].head(MAX_REVIEWS_PER_PRODUCT)

        # 1. Create the product
        resp = requests.post(f"{API_BASE}/products", json={
            "name": clean,
            "category": "Amazon Devices"
        })
        if resp.status_code != 200:
            print(f"Failed to create product '{clean}': {resp.text}")
            continue

        product_id = resp.json()["id"]
        print(f"Created product_id={product_id}: {clean}")

        # 2. Prepare a mini CSV in-memory for this product's reviews
        mini_df = subset[["reviews.text", "reviews.rating"]].rename(
            columns={"reviews.text": "text", "reviews.rating": "rating"}
        )
        csv_bytes = mini_df.to_csv(index=False).encode("utf-8")

        # 3. Bulk upload via your existing endpoint
        files = {"file": (f"{product_id}_reviews.csv", csv_bytes, "text/csv")}
        upload_resp = requests.post(f"{API_BASE}/reviews/bulk-upload/{product_id}", files=files)
        print(f"  Uploaded: {upload_resp.json()}")

        time.sleep(1)  # small delay to avoid hammering the AI API

    print("\nDone. Test with: GET /products/{id}/analytics for each product_id printed above.")

if __name__ == "__main__":
    main()
    