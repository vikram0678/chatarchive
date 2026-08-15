"""
API route for semantic search.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem
from app.services.embedding_service import search_similar
from app.services.conversation_service import get_conversations_by_ids

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResponse)
def semantic_search(payload: SearchRequest, db: Session = Depends(get_db)):
    """
    Embeds the query, finds the top_k closest conversations by meaning
    (not keywords), and returns them with similarity scores.
    """
    matches = search_similar(payload.query, payload.top_k)

    if not matches:
        return SearchResponse(query=payload.query, results=[])

    match_ids = [m["conversation_id"] for m in matches]
    scores_by_id = {m["conversation_id"]: m["score"] for m in matches}

    rows = get_conversations_by_ids(db, match_ids)

    results = [
        SearchResultItem(
            conversation_id=row.id,
            score=scores_by_id.get(str(row.id), 0.0),
            message_count=row.message_count,
            status=row.status.value if row.status else "pending",
        )
        for row in rows
    ]

    # Keep results sorted by similarity score, highest first
    results.sort(key=lambda r: r.score, reverse=True)

    return SearchResponse(query=payload.query, results=results)