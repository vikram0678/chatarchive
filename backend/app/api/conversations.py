"""
API routes for conversations: ingest, list, and detail endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationCreateResponse,
    ConversationListResponse,
    ConversationListItem,
    ConversationDetailResponse,
    MessageOut,
    AnalysisOut,
)
from app.services import conversation_service
from app.worker.tasks import process_conversation

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConversationCreateResponse, status_code=202)
def ingest_conversation(payload: ConversationCreate, db: Session = Depends(get_db)):
    """
    Accepts raw messages, saves them, triggers background NLP processing,
    and returns immediately — does NOT wait for NLP to finish.
    """
    conversation = conversation_service.create_conversation(db, payload)

    # Hand off to Celery — this returns instantly, doesn't block the API
    process_conversation.delay(str(conversation.id))

    return ConversationCreateResponse(
        conversation_id=conversation.id,
        status="processing",
    )


@router.get("", response_model=ConversationListResponse)
def list_conversations(page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    """
    Returns a paginated list of conversations with message count and status.
    """
    total, rows = conversation_service.list_conversations(db, page, size)

    items = [
        ConversationListItem(
            id=row.id,
            created_at=row.created_at,
            message_count=row.message_count,
            status=row.status.value if row.status else "pending",
        )
        for row in rows
    ]

    return ConversationListResponse(total=total, page=page, size=size, items=items)


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """
    Returns the full transcript and NLP analysis for one conversation.
    """
    conversation = conversation_service.get_conversation_detail(db, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    analysis = conversation.analysis_result

    return ConversationDetailResponse(
        id=conversation.id,
        messages=[MessageOut.model_validate(m) for m in conversation.messages],
        analysis=AnalysisOut(
            status=analysis.status.value if analysis else "pending",
            insights=analysis.insights if analysis else None,
        ),
    )