#!/bin/bash

# Start the Celery queue worker in the background
celery -A app.workers.celery_worker worker --loglevel=info &

# Start the FastAPI web server in the foreground on Hugging Face's required port (7860)
uvicorn app.app:app --host 0.0.0.0 --port 7860
