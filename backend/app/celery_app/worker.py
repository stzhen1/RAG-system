from celery import Celery
from app.config import settings

celery_app = Celery(
    "rag",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_queues={
        "queue_parse": {"exchange": "rag", "routing_key": "parse"},
        "queue_chunk": {"exchange": "rag", "routing_key": "chunk"},
        "queue_embedding": {"exchange": "rag", "routing_key": "embedding"},
        "queue_index": {"exchange": "rag", "routing_key": "index"},
    },
    task_routes={
        "app.celery_app.tasks.parse_document": {"queue": "queue_parse"},
        "app.celery_app.tasks.chunk_document": {"queue": "queue_chunk"},
        "app.celery_app.tasks.embed_chunks": {"queue": "queue_embedding"},
        "app.celery_app.tasks.index_chunks": {"queue": "queue_index"},
    },
)
