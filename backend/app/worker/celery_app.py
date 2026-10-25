from celery import Celery

from app.core.config import queue_settings

celery_app = Celery(
    "support_intelligence",
    broker=queue_settings.broker_url,
    backend=queue_settings.result_backend,
    include=[
        "app.worker.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
)
