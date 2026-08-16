# ChatArchive 💬

A full-stack conversation intelligence platform. FastAPI and Celery handle asynchronous NLP (summarization, sentiment analysis, entity extraction), Qdrant powers semantic vector search, and a modern Vue 3 dashboard visualizes it all. 

ChatArchive ingests raw customer chat transcripts, processes them in the background with AI, and allows you to search across all your historical conversations by **meaning** — not just exact keywords.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI (Python) |
| **Async Task Queue** | Celery + Redis |
| **NLP** | spaCy, VADER Sentiment |
| **Semantic Search** | Sentence-Transformers + Qdrant |
| **Relational Database** | PostgreSQL |
| **Frontend** | Vue 3 + Chart.js |
| **Migrations** | Alembic |
| **Orchestration** | Docker Compose |

---

## ✨ Features

- **Real-Time Ingestion:** Ingest chat conversations via a simple JSON API without blocking the application.
- **Background NLP Pipeline:** Automatic summarization, sentiment analysis, named entity recognition, and key phrase extraction.
- **Semantic Search:** Find conversations by their meaning (e.g., searching "money back issue" instantly matches a conversation about "refunds").
- **Reactive Dashboard:** A beautiful UI with a conversation list, split-pane detail view, and live sentiment analytics pie chart.
- **Fully Containerized:** One single command starts the entire stack cleanly.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vikram0678/chatarchive.git
cd chatarchive

# 2. Launch the entire stack
docker-compose up -d --build
```
*(That single command builds and starts: PostgreSQL, Redis, Qdrant, the FastAPI API, the Celery worker, and the Vue frontend.)*

### Access Points

| Service | URL |
|---|---|
| **Frontend Dashboard** | [http://localhost:5173](http://localhost:5173) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## 🧪 Testing the Platform

### 1. Ingest Seed Data
Since the database starts empty, you can simulate an incoming customer chat using `curl` (or by using the Swagger UI at `/docs`).

```bash
curl -X POST http://localhost:8000/api/conversations \
-H "Content-Type: application/json" \
-d '{
  "messages": [
    {"sender": "customer", "timestamp": "2026-08-15T10:00:00", "text": "I want a refund for my broken laptop! I am very angry."},
    {"sender": "agent", "timestamp": "2026-08-15T10:01:00", "text": "I am sorry to hear that, let me check your order."}
  ]
}'
```

### 2. Semantic Search
```bash
curl -X POST http://localhost:8000/api/search \
-H "Content-Type: application/json" \
-d '{"query": "money back issue", "top_k": 5}'
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| **POST** | `/api/conversations` | Ingest a conversation, trigger background NLP |
| **GET** | `/api/conversations` | Paginated list of all conversations |
| **GET** | `/api/conversations/{id}` | Full transcript + NLP insights for one conversation |
| **POST** | `/api/search` | Semantic search across all processed conversations |

*(Full interactive documentation is available at `/docs` once the API is running).*

---

## 📂 Project Structure

```text
chatarchive/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   ├── core/          # Config and database setup
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic validation schemas
│   │   ├── services/      # NLP, embedding, and business logic
│   │   └── worker/        # Celery task definitions
│   ├── alembic/           # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Vue UI components
│   │   ├── views/         # Page layouts
│   │   ├── services/      # Axios API client
│   │   └── router/        # Vue Router config
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── ARCHITECTURE.md
└── EVALUATION.md
```
