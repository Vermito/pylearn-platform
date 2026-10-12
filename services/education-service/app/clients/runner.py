import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.runner import (
    RunnerRequest,
    RunnerResponse,
)


class RunnerClient:
    async def run(
        self,
        data: RunnerRequest,
    ) -> RunnerResponse:
        timeout_seconds = (
            data.time_limit_ms / 1000
            + 5
        )

        timeout = httpx.Timeout(
            timeout=timeout_seconds,
            connect=2.0,
        )

        try:
            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:
                response = await client.post(
                    f"{settings.runner_service_url}/run",
                    json=data.model_dump(),
                    headers={
                        "X-Runner-Key": (
                            settings.runner_api_key
                        )
                    },
                )

                response.raise_for_status()

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=(
                    status.HTTP_504_GATEWAY_TIMEOUT
                ),
                detail="Runner service timed out",
            )

        except httpx.ConnectError:
            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail="Runner service is unavailable",
            )

        except httpx.HTTPStatusError:
            raise HTTPException(
                status_code=(
                    status.HTTP_502_BAD_GATEWAY
                ),
                detail="Runner service returned an error",
            )

        except httpx.RequestError:
            raise HTTPException(
                status_code=(
                    status.HTTP_503_SERVICE_UNAVAILABLE
                ),
                detail="Runner service is unavailable",
            )

        return RunnerResponse.model_validate(
            response.json()
        )