from celery import Celery
from app.config import settings

celery_app = Celery(
    "classroom_engagement",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.diarization"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Tasks are loaded via the `include` setting above to avoid circular imports.
