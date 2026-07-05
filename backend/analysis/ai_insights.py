# analysis/ai_insights.py
import os, json, anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def extract_topics(review_text: str) -> list:
    try:
        prompt = f"""Extract up to 3 short topic keywords (e.g. "battery life", "price", "delivery") 
from this product review. Return ONLY a JSON array of strings, nothing else.

Review: "{review_text}" """
        resp = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
        return json.loads(resp.content[0].text)
    except Exception as e:
        print(f"[extract_topics] AI call failed: {e}")
        return []

def summarize_reviews(review_texts: list) -> str:
    try:
        joined = "\n".join(f"- {t}" for t in review_texts[:50])
        prompt = f"""Summarize the overall customer sentiment from these reviews in 4-5 sentences.
Highlight top complaints and top praises.

Reviews:
{joined}"""
        resp = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.content[0].text
    except Exception as e:
        print(f"[summarize_reviews] AI call failed: {e}")
        return "AI summary unavailable (API error)."