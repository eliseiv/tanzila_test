from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.logging_config import setup_logging
from app.routes import router

setup_logging()

app = FastAPI(
    title="TATEST Observability App",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

app.include_router(router)

Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)
