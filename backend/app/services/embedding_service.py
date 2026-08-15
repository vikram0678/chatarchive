"""
Embedding generation and Qdrant vector storage.
Kept separate from nlp_service.py since this handles vectors,
not text-analysis insights.
"""

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from app.core.config import settings

COLLECTION_NAME = "conversations"
VECTOR_SIZE = 384  # output size of all-MiniLM-L6-v2

# Loaded once at import time — expensive to reload per task
_embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
_qdrant_client = QdrantClient(url=settings.QDRANT_URL)


def _ensure_collection_exists():
    """Creates the Qdrant collection on first use, if it doesn't already exist."""
    existing = [c.name for c in _qdrant_client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        _qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def generate_embedding(text: str) -> list[float]:
    """Converts text into a 384-dimension vector."""
    vector = _embedding_model.encode(text)
    return vector.tolist()


def store_embedding(conversation_id: str, text: str):
    """Generates and stores an embedding in Qdrant, tagged with conversation_id."""
    _ensure_collection_exists()
    vector = generate_embedding(text)

    _qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=conversation_id,
                vector=vector,
                payload={"conversation_id": conversation_id},
            )
        ],
    )


def search_similar(query: str, top_k: int = 5) -> list[dict]:
    """
    Embeds the query, searches Qdrant, and returns matches with similarity scores.
    Each result: {"conversation_id": ..., "score": ...}
    """
    _ensure_collection_exists()
    query_vector = generate_embedding(query)

    results = _qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
    )

    return [
        {"conversation_id": r.payload["conversation_id"], "score": r.score}
        for r in results
    ]