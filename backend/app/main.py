"""FastAPI application entrypoint."""
import logging
from uuid import uuid4

from fastapi import FastAPI, Request

from app.api.routes import router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.include_router(router, prefix=settings.api_prefix)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_id=%s method=%s path=%s status_code=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
