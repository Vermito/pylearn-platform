from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.routes.articles import (
    router as articles_router,
)
from app.api.routes.categories import (
    router as categories_router,
)
from app.api.routes.courses import (
    router as courses_router,
)
from app.api.routes.materials import (
    router as materials_router,
)
from app.api.routes.modules import (
    router as modules_router,
)
from app.api.routes.tasks import (
    router as tasks_router,
)
from app.api.routes.tests import (
    router as tests_router,
)
from app.api.routes.topics import (
    router as topics_router,
)
from app.cache.redis import redis_cache
from app.core.config import settings
from app.messaging.rabbitmq import (
    rabbitmq_publisher,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_publisher.connect()

    await redis_cache.connect()

    yield

    await redis_cache.close()

    await rabbitmq_publisher.close()


app = FastAPI(
    title="PyLearn Education Service",
    description=(
        "Educational content service "
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


app.include_router(courses_router)
app.include_router(modules_router)
app.include_router(topics_router)
app.include_router(categories_router)
app.include_router(articles_router)
app.include_router(materials_router)
app.include_router(tasks_router)
app.include_router(tests_router)


@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():
    return {
        "status": "ok",
        "service": "education-service",
    }