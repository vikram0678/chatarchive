"""
Business logic for conversations — kept separate from the API routes
so the routes stay thin and this logic is reusable/testable.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.analysis_result import AnalysisResult, AnalysisStatus
from app.schemas.conversation import ConversationCreate


def create_conversation(db: Session, payload: ConversationCreate) -> Conversation:
    """
    Saves a new Conversation + its Messages + a pending AnalysisResult
    in a single database transaction.
    """
    conversation = Conversation()
    db.add(conversation)
    db.flush()  # generates conversation.id without committing yet

    for msg in payload.messages:
        db.add(
            Message(
                conversation_id=conversation.id,
                sender=msg.sender,
                timestamp=msg.timestamp,
                text=msg.text,
            )
        )

    db.add(
        AnalysisResult(
            conversation_id=conversation.id,
            status=AnalysisStatus.pending,
        )
    )

    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, page: int, size: int):
    """
    Returns a paginated list of conversations with message count + status.
    """
    offset = (page - 1) * size

    total = db.query(Conversation).count()

    rows = (
        db.query(
            Conversation.id,
            Conversation.created_at,
            func.count(Message.id).label("message_count"),
            AnalysisResult.status,
        )
        .outerjoin(Message, Message.conversation_id == Conversation.id)
        .outerjoin(AnalysisResult, AnalysisResult.conversation_id == Conversation.id)
        .group_by(Conversation.id, AnalysisResult.status)
        .order_by(Conversation.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    return total, rows


def get_conversation_detail(db: Session, conversation_id: str):
    """
    Fetches a single conversation with its messages and analysis result.
    Returns None if not found.
    """
    return (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )



def get_conversations_by_ids(db: Session, conversation_ids: list[str]):
    """
    Fetches multiple conversations by their IDs, with message count and status —
    used by semantic search to hydrate Qdrant's vector matches with real DB data.
    """
    rows = (
        db.query(
            Conversation.id,
            func.count(Message.id).label("message_count"),
            AnalysisResult.status,
        )
        .outerjoin(Message, Message.conversation_id == Conversation.id)
        .outerjoin(AnalysisResult, AnalysisResult.conversation_id == Conversation.id)
        .filter(Conversation.id.in_(conversation_ids))
        .group_by(Conversation.id, AnalysisResult.status)
        .all()
    )
    return rows