"""Redis job queue integration for async transcription jobs."""
from redis import Redis
from rq import Queue

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.project_service import ProjectService

settings = get_settings()
redis = Redis.from_url(settings.redis_url)
queue = Queue("transcription", connection=redis)


def run_transcription_job(project_id: int) -> None:
    db = SessionLocal()
    try:
        service = ProjectService(db)
        service.process_project(project_id)
    finally:
        db.close()
