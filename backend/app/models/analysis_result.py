"""
AnalysisResult model — stores the NLP output for a conversation.
`insights` is JSONB because the shape of NLP output varies
(summary text, sentiment score, list of entities, list of topics, etc.)
"""

import enum
import uuid

from sqlalchemy import Column, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one-to-one with Conversation
        index=True,
    )
    
    status = Column(
        Enum(AnalysisStatus, name="analysis_status"),
        nullable=False,
        default=AnalysisStatus.pending,
    )
    insights = Column(JSONB, nullable=True)

    conversation = relationship("Conversation", back_populates="analysis_result")