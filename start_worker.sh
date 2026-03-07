#!/bin/bash

# Start the Celery queue worker in the background
celery -A app.workers.celery_worker worker --loglevel=info &

# Start a dummy HTTP server in the foreground so Render doesn't crash the Web Service
# Render automatically injects the $PORT variable (usually 10000)
PORT=${PORT:-10000}
python3 -m http.server $PORT
