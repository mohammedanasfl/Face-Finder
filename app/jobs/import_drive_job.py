import json
import os
from datetime import datetime, timezone

import redis


redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
kwargs = {}
if redis_url.startswith("rediss://"):
    kwargs["ssl_cert_reqs"] = "none"

redis_client = redis.from_url(redis_url, **kwargs)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_job(job_id: str, job_type: str):
    """Initializes a new job tracking record in Redis."""
    job_data = {
        "job_id": job_id,
        "job_type": job_type,
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
        "error": None,
        "total_files": 0,
        "images_received": 0,
        "images_downloaded": 0,
        "faces_indexed": 0,
        "status": "queued",
    }
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    redis_client.expire(f"job:{job_id}", 86400)


def update_job_progress(
    job_id: str,
    *,
    total_files: int = None,
    images_received: int = None,
    images_downloaded: int = None,
    faces_indexed: int = None,
    status: str = None,
    error: str = None,
):
    """Updates specific fields of the job tracker in Redis."""
    key = f"job:{job_id}"
    data = redis_client.get(key)
    if not data:
        return

    job_data = json.loads(data)

    if total_files is not None:
        job_data["total_files"] = total_files
    if images_received is not None:
        job_data["images_received"] = images_received
    if images_downloaded is not None:
        job_data["images_downloaded"] = images_downloaded
    if faces_indexed is not None:
        job_data["faces_indexed"] = faces_indexed
    if status is not None:
        job_data["status"] = status
    if error is not None:
        job_data["error"] = error

    job_data["updated_at"] = _timestamp()
    redis_client.set(key, json.dumps(job_data))
    redis_client.expire(key, 86400)


def fail_job(job_id: str, message: str):
    update_job_progress(job_id, status="failed", error=message)


def get_job_status(job_id: str) -> dict:
    """Retrieves the current job data."""
    data = redis_client.get(f"job:{job_id}")
    if data:
        return json.loads(data)
    return {
        "job_id": job_id,
        "job_type": None,
        "status": "not_found",
        "error": "Job not found",
        "total_files": 0,
        "images_received": 0,
        "images_downloaded": 0,
        "faces_indexed": 0,
    }
