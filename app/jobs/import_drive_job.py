import redis
import json
import os

# Connect to Redis
redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
kwargs = {}
if redis_url.startswith("rediss://"):
    kwargs["ssl_cert_reqs"] = "none"

redis_client = redis.from_url(redis_url, **kwargs)

def initialize_job(job_id: str):
    """Initializes a new job tracking hash in Redis."""
    job_data = {
        "job_id": job_id,
        "images_downloaded": 0,
        "faces_detected": 0,
        "status": "processing"
    }
    redis_client.set(f"job:{job_id}", json.dumps(job_data))
    # Automatically expire jobs after 24 hours to prevent memory leaks
    redis_client.expire(f"job:{job_id}", 86400) 

def update_job_progress(job_id: str, images_downloaded: int = None, faces_detected: int = None, status: str = None):
    """Updates specific fields of the job tracker in Redis."""
    key = f"job:{job_id}"
    data = redis_client.get(key)
    if not data:
        return
        
    job_data = json.loads(data)
    
    if images_downloaded != None:
        job_data["images_downloaded"] = images_downloaded
    if faces_detected != None:
        job_data["faces_detected"] = faces_detected
    if status is not None:
        job_data["status"] = status
        
    redis_client.set(key, json.dumps(job_data))

def get_job_status(job_id: str) -> dict:
    """Retrieves the current job data."""
    data = redis_client.get(f"job:{job_id}")
    if data:
        return json.loads(data)
    return {"job_id": job_id, "status": "not_found", "images_downloaded": 0, "faces_detected": 0}
