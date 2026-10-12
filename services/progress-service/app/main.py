from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.routes.progress import (
    router as progress_router,
)
from app.core.config import settings
from app.messaging.rabbitmq import (
    rabbitmq_consumer,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_consumer.connect()

    yield

    await rabbitmq_consumer.close()


app = FastAPI(
    title="PyLearn Progress Service",
    description=(
        "Progress and gamification service "
        "for PyLearn"
    ),
    version="1.0.0",
    root_path=settings.api_root_path,
    lifespan=lifespan,
)


metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)


app.include_router(progress_router)


@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():
    return {
        "status": "ok",
        "service": "progress-service",
    }