"""
Celery application setup.
This is the entry point Celery uses to know how to connect to Redis
and which task modules to load.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "chatarchive",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],  # tells Celery where to find task functions
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)