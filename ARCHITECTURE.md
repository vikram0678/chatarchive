# Architecture

## Overview

ChatArchive uses a decoupled architecture so the API stays fast while
NLP processing (which is slow) happens in the background.

## Data Flow

1. **Vue Frontend** sends `POST /api/conversations` with raw chat messages.
2. **FastAPI** validates the payload, saves the `Conversation` and `Message`
   rows to PostgreSQL, creates an `AnalysisResult` row with `status=pending`,
   then publishes a job to **Redis** and responds immediately with `202 Accepted`.
   The API never waits for NLP to finish.
3. **Celery Worker** consumes the job from Redis, marks the analysis
   `status=processing`, fetches the conversation's messages, and runs 4 NLP
   tasks: Summarization, Sentiment Analysis, Named Entity Recognition, and
   Key Phrase Extraction.
4. The worker also generates a vector **embedding** of the conversation text
   and stores it in **Qdrant**, tagged with the `conversation_id`.
5. Results are saved into the `insights` JSONB column in PostgreSQL, and
   status is updated to `completed` (or `failed` if an error occurred).
6. **Semantic Search:** when a user submits `POST /api/search`, FastAPI
   embeds the query text the same way, asks Qdrant for the closest vectors
   by cosine similarity, then fetches the matching conversations from
   PostgreSQL to return full details alongside each similarity score.
7. **Vue Frontend** polls `GET /api/conversations` and
   `GET /api/conversations/{id}` to display the list, detail view, and
   sentiment analytics chart.

## Why This Design

- **API/Worker separation:** NLP models take seconds to run. If this happened
  inside the API request, every ingestion call would time out under load.
  Celery isolates this so the API responds in milliseconds regardless of
  NLP processing time.
- **JSONB for insights:** Different NLP tasks produce different shaped output
  (a list of entities vs. a single sentiment string). JSONB stores this
  flexibly without needing a rigid, ever-changing table schema.
- **Separate vector DB:** PostgreSQL is excellent for structured, relational
  data but not built for high-speed similarity search across embeddings.
  Qdrant is purpose-built for that, enabling meaning-based search that
  keyword search cannot do (e.g., "money back issue" matching a
  conversation that says "refund").

## Service Map (Docker Compose)

| Service | Technology | Responsibility |
|---|---|---|
| `frontend` | Vue 3 | User interface |
| `api` | FastAPI | HTTP endpoints, validation, DB reads/writes |
| `worker` | Celery | Background NLP + embedding generation |
| `db` | PostgreSQL | Conversations, messages, analysis results |
| `redis` | Redis | Message broker between API and worker |
| `qdrant` | Qdrant | Vector storage for semantic search |