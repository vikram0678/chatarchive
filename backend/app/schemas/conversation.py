"""
Pydantic schemas for the Conversation API.
These validate incoming requests and shape outgoing responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


# Input schemas (request bodies) 
class MessageCreate(BaseModel):
    sender: str
    timestamp: datetime
    text: str


class ConversationCreate(BaseModel):
    messages: List[MessageCreate] = Field(..., min_items=1)


# Output schemas (response bodies) 

class MessageOut(BaseModel):
    id: UUID
    sender: str
    timestamp: datetime
    text: str

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    status: str
    insights: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ConversationCreateResponse(BaseModel):
    conversation_id: UUID
    status: str


class ConversationListItem(BaseModel):
    id: UUID
    created_at: datetime
    message_count: int
    status: str


class ConversationListResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[ConversationListItem]


class ConversationDetailResponse(BaseModel):
    id: UUID
    messages: List[MessageOut]
    analysis: AnalysisOut