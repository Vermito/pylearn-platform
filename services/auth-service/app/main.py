from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.routes.admin import (
    router as admin_router,
)
from app.api.routes.auth import (
    router as auth_router,
)
from app.api.routes.users import (
    router as users_router,
)
from app.core.config import settings

app = FastAPI(
    title="PyLearn Auth Service",
    description=(
        "Authentication and user management "
        "service for PyLearn"
    ),
    version="1.0.0",
    root_path=settings.api_root_path,
)


metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)


@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():
    return {
        "status": "ok",
        "service": "auth-service",
    }