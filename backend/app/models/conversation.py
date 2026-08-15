"""
Conversation model — represents a single chat thread.
Each conversation has many messages and exactly one analysis result.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # One conversation -> many messages
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )

    # One conversation -> one analysis result
    analysis_result = relationship(
        "AnalysisResult",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )