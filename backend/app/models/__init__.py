"""
Import all models here so Alembic's autogenerate can detect them
via a single `from app.models import *` in env.py.
"""

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.analysis_result import AnalysisResult, AnalysisStatus

__all__ = ["Conversation", "Message", "AnalysisResult", "AnalysisStatus"]