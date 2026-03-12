import os
import ssl
from celery import Celery


broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
ssl_kwargs = {}

if broker_url.startswith("rediss://"):
    if "?" in broker_url:
        broker_url = broker_url.split("?", 1)[0]
    ssl_kwargs = {"ssl_cert_reqs": ssl.CERT_NONE}


celery_app = Celery(
    "workers",
    broker=broker_url,
    backend=broker_url,
    broker_use_ssl=ssl_kwargs if ssl_kwargs else None,
    redis_backend_use_ssl=ssl_kwargs if ssl_kwargs else None,
)
