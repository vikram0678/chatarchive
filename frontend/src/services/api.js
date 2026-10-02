/**
 * Central Axios instance — every component calls the backend through this,
 * so the base URL only lives in one place.
 */
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

export const getConversations = (page = 1, size = 20) =>
  api.get("/api/conversations", { params: { page, size } });

export const getConversationDetail = (id) =>
  api.get(`/api/conversations/${id}`);

export const searchConversations = (query, top_k = 5) =>
  api.post("/api/search", { query, top_k });

export const createConversation = (messages) =>
  api.post("/api/conversations", { messages });

export const checkHealth = () =>
  api.get("/");

export default api;