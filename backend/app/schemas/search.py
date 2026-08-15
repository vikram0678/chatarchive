"""
Pydantic schemas for the semantic search endpoint.
"""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResultItem(BaseModel):
    conversation_id: UUID
    score: float
    message_count: int
    status: str


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]