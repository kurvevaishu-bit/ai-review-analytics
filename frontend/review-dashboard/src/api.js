import axios from "axios";
const API_BASE = "http://localhost:8001";

export const uploadReviews = (productId, file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_BASE}/reviews/bulk-upload/${productId}`, formData);
};

export const getAnalytics = (productId) =>
  axios.get(`${API_BASE}/products/${productId}/analytics`);

export const getReviews = (productId) =>
  axios.get(`${API_BASE}/products/${productId}/reviews`);

export const createProduct = (name, category) =>
  axios.post(`${API_BASE}/products`, { name, category });
