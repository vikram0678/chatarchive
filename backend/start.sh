#!/bin/bash
set -e

# Optimize memory consumption for constrained containers (<512MB RAM)
export MALLOC_ARENA_MAX=2
export OMP_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false

echo "Applying database migrations..."
alembic upgrade head

echo "Starting Celery background worker in solo thread mode..."
celery -A app.worker.celery_app worker --concurrency=1 --pool=solo --loglevel=warning &

PORT="${PORT:-8000}"
echo "Starting FastAPI server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
