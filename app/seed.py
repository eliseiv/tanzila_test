import structlog
from sqlalchemy.orm import Session

import app.database as db_module
from app.models import Base, Message

logger = structlog.get_logger(__name__)

SEED_MESSAGES: list[str] = [
    "Hello, World! Welcome to the observability demo.",
    "Monitoring is not optional — it is essential.",
    "Structured logging makes debugging 10x easier.",
    "Prometheus collects metrics so you can sleep at night.",
    "Grafana dashboards turn data into insight.",
    "Latency percentiles matter more than averages.",
    "Alerting on symptoms, not causes, reduces noise.",
    "Every request tells a story — metrics help you read it.",
    "Docker Compose: one command to rule them all.",
    "PostgreSQL is the database that just works.",
    "Loki + Promtail: logs without the complexity.",
    "Observability = Metrics + Logs + Traces.",
]


def init_db() -> None:
    """Create tables and insert seed data if the messages table is empty."""
    Base.metadata.create_all(bind=db_module.engine)
    logger.info("database_tables_created")

    db: Session = db_module.SessionLocal()
    try:
        existing = db.query(Message).count()
        if existing > 0:
            logger.info("seed_skipped", existing_messages=existing)
            return

        for text in SEED_MESSAGES:
            db.add(Message(text=text))
        db.commit()
        logger.info("seed_completed", messages_inserted=len(SEED_MESSAGES))
    except Exception:
        db.rollback()
        logger.exception("seed_failed")
        raise
    finally:
        db.close()
