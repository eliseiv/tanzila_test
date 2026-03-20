import time

import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.metrics import LOG_EVENTS, REQUEST_COUNT, REQUEST_LATENCY
from app.models import Message
from app.schemas import (
    HealthResponse,
    MessageResponse,
    ProcessRequest,
    ProcessResponse,
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Redirect root to API docs."""
    return RedirectResponse(url="/docs")


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return application health status."""
    REQUEST_COUNT.labels(endpoint="/health", method="GET").inc()
    logger.info("health_check", status="healthy")
    return HealthResponse()


@router.get("/message/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    """Retrieve a message from the database by ID."""
    start = time.perf_counter()
    REQUEST_COUNT.labels(endpoint="/message", method="GET").inc()

    if message_id <= 0:
        LOG_EVENTS.labels(level="warning").inc()
        logger.warning("invalid_message_id", message_id=message_id)
        raise HTTPException(status_code=400, detail="Message ID must be positive")

    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        LOG_EVENTS.labels(level="warning").inc()
        logger.warning("message_not_found", message_id=message_id)
        raise HTTPException(status_code=404, detail="Message not found")

    latency = time.perf_counter() - start
    REQUEST_LATENCY.labels(endpoint="/message").observe(latency)
    logger.info("message_retrieved", message_id=message_id, latency=round(latency, 4))
    return MessageResponse.model_validate(message)


@router.post("/process", response_model=ProcessResponse)
def process_data(payload: ProcessRequest) -> ProcessResponse:
    """Simulate data processing with an artificial delay (bottleneck)."""
    start = time.perf_counter()
    REQUEST_COUNT.labels(endpoint="/process", method="POST").inc()

    logger.info("process_started", data_length=len(payload.data))

    time.sleep(settings.process_delay)

    latency = time.perf_counter() - start
    REQUEST_LATENCY.labels(endpoint="/process").observe(latency)
    logger.info("process_completed", latency=round(latency, 4))
    return ProcessResponse(received=payload.data)
