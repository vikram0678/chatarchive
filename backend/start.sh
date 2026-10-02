#!/bin/bash
set -e

echo "Applying database migrations..."
alembic upgrade head

echo "Starting Celery background worker..."
celery -A app.worker.celery_app worker --loglevel=info &

PORT="${PORT:-8000}"
echo "Starting FastAPI server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
