#!/bin/bash

# Start Redis server in the background (required for Celery on single-container HuggingFace)
redis-server --daemonize yes

# Wait until Redis is ready before starting dependent services
until redis-cli ping | grep -q PONG; do
  echo "Waiting for Redis to start..."
  sleep 1
done
echo "Redis is ready."

# Start the Celery queue worker in the background
celery -A app.workers.celery_worker worker --loglevel=info &

# Start the FastAPI web server in the foreground on Hugging Face's required port (7860)
uvicorn app.app:app --host 0.0.0.0 --port 7860
