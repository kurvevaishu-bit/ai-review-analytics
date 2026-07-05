import { useState } from "react";
import { uploadReviews, getAnalytics, createProduct } from "./api";
import SentimentChart from "./components/SentimentChart";
import TopicsChart from "./components/TopicsChart";

export default function App() {
  const [productId, setProductId] = useState("");
  const [productName, setProductName] = useState("");
  const [category, setCategory] = useState("");
  const [file, setFile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCreateProduct = async () => {
    if (!productName) return;
    try {
      const res = await createProduct(productName, category);
      setProductId(String(res.data.id));
      setError("");
    } catch (err) {
      setError("Failed to create product. Check backend is running.");
    }
  };

  const handleLoadAnalytics = async () => {
    if (!productId) {
      setError("Enter a product ID first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res = await getAnalytics(productId);
      setAnalytics(res.data);
    } catch (err) {
      setError("Failed to load analytics. Check backend is running.");
    }
    setLoading(false);
  };

  const handleUpload = async () => {
    if (!file || !productId) {
      setError("Enter/select a product ID and choose a CSV file first.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await uploadReviews(productId, file);
      const res = await getAnalytics(productId);
      setAnalytics(res.data);
    } catch (err) {
      setError("Upload or analysis failed. Check backend terminal for details.");
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 950, margin: "40px auto", fontFamily: "sans-serif", padding: "0 16px" }}>
      <h1>AI Review Analytics Dashboard</h1>

      <div style={{ background: "#f8fafc", padding: 16, borderRadius: 8, marginBottom: 20 }}>
        <h3>1. Select an Existing Product or Create a New One</h3>

        <div style={{ marginBottom: 12 }}>
          <input
            placeholder="Existing Product ID (e.g. 16)"
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            style={{ marginRight: 8, padding: 6, width: 220 }}
          />
          <button onClick={handleLoadAnalytics}>Load Analytics for This Product</button>
          {productId && <span style={{ marginLeft: 10 }}>✅ Current Product ID: <strong>{productId}</strong></span>}
        </div>

        <div>
          <input
            placeholder="Or new product name"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            style={{ marginRight: 8, padding: 6 }}
          />
          <input
            placeholder="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{ marginRight: 8, padding: 6 }}
          />
          <button onClick={handleCreateProduct}>Create Product</button>
        </div>
      </div>

      <div style={{ background: "#f8fafc", padding: 16, borderRadius: 8, marginBottom: 20 }}>
        <h3>2. Upload Reviews CSV (optional, for a new product)</h3>
        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload} disabled={loading} style={{ marginLeft: 8 }}>
          {loading ? "Analyzing..." : "Upload & Analyze"}
        </button>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {analytics && !analytics.message && (
        <>
          <h2>Total Reviews: {analytics.total_reviews}</h2>

          <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>
            <SentimentChart data={analytics.sentiment_breakdown} title="VADER Sentiment" />
            <SentimentChart data={analytics.lexicon_breakdown} title="Lexicon Sentiment" />
          </div>

          <h3 style={{ marginTop: 30 }}>Top Topics</h3>
          <TopicsChart topics={analytics.top_topics} />

          <h3>AI Summary</h3>
          <p style={{ background: "#f1f5f9", padding: 16, borderRadius: 8 }}>
            {analytics.ai_summary}
          </p>
        </>
      )}

      {analytics && analytics.message && (
        <p style={{ color: "#888" }}>{analytics.message}</p>
      )}
    </div>
  );
}

