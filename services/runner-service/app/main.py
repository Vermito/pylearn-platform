import asyncio
import secrets

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    status,
)
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.observability.metrics import (
    CODE_EXECUTION_DURATION_SECONDS,
    CODE_EXECUTIONS_TOTAL,
)
from app.schemas.runner import (
    RunRequest,
    RunResponse,
)
from app.services.docker_runner import DockerRunner


app = FastAPI(
    title="PyLearn Runner Service",
    description=(
        "Internal sandbox service "
        "for Python code execution"
    ),
    version="1.0.0",
)


metrics_app = make_asgi_app()

app.mount(
    "/metrics",
    metrics_app,
)


runner = DockerRunner()


@app.get(
    "/health",
    tags=["Health"],
)
async def health():
    return {
        "status": "ok",
        "service": "runner-service",
    }


@app.post(
    "/run",
    response_model=RunResponse,
    tags=["Runner"],
)
async def run_code(
    data: RunRequest,
    x_runner_key: str = Header(
        alias="X-Runner-Key"
    ),
):
    if not secrets.compare_digest(
        x_runner_key,
        settings.runner_api_key,
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="Invalid runner key",
        )

    result = await asyncio.to_thread(
        runner.run,
        data,
    )

    CODE_EXECUTIONS_TOTAL.labels(
        status=result.status,
        mode=data.mode,
    ).inc()

    CODE_EXECUTION_DURATION_SECONDS.labels(
        status=result.status,
        mode=data.mode,
    ).observe(
        max(
            result.execution_time_ms
            / 1000,
            0,
        )
    )

    return result