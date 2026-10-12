import json
import logging
from typing import Any

import redis.asyncio as redis
from redis.exceptions import RedisError

from app.core.config import settings


logger = logging.getLogger(__name__)


COURSES_VERSION_KEY = (
    "pylearn:education:courses:version"
)


class RedisCache:
    def __init__(self) -> None:
        self.client: redis.Redis | None = None

    async def connect(self) -> None:
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

        try:
            await self.client.ping()

            logger.info(
                "Redis connection established"
            )

        except RedisError as exc:
            # Redis — необязательный слой.
            # education-service продолжает работать
            # через PostgreSQL.
            logger.warning(
                "Redis is unavailable at startup. "
                "Database fallback will be used. "
                "Error: %s",
                exc,
            )

    async def close(self) -> None:
        if self.client is not None:
            await self.client.aclose()

    async def get_json(
        self,
        key: str,
    ) -> Any | None:
        if self.client is None:
            return None

        try:
            value = await self.client.get(
                key
            )

            if value is None:
                return None

            return json.loads(value)

        except json.JSONDecodeError:
            logger.warning(
                "Invalid JSON found in Redis "
                "for key %s",
                key,
            )

            try:
                await self.client.delete(key)
            except RedisError:
                pass

            return None

        except RedisError as exc:
            logger.warning(
                "Redis GET failed. "
                "Falling back to PostgreSQL. "
                "Error: %s",
                exc,
            )

            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int | None = None,
    ) -> bool:
        if self.client is None:
            return False

        ttl = (
            ttl_seconds
            if ttl_seconds is not None
            else settings.redis_cache_ttl_seconds
        )

        try:
            serialized = json.dumps(
                value,
                ensure_ascii=False,
            )

            await self.client.set(
                key,
                serialized,
                ex=ttl,
            )

            return True

        except RedisError as exc:
            logger.warning(
                "Redis SET failed. "
                "Response will still be returned "
                "from PostgreSQL. Error: %s",
                exc,
            )

            return False

    async def get_courses_version(
        self,
    ) -> int | None:
        if self.client is None:
            return None

        try:
            value = await self.client.get(
                COURSES_VERSION_KEY
            )

            if value is None:
                await self.client.set(
                    COURSES_VERSION_KEY,
                    "1",
                    nx=True,
                )

                value = await self.client.get(
                    COURSES_VERSION_KEY
                )

            if value is None:
                return None

            return int(value)

        except (
            RedisError,
            ValueError,
        ) as exc:
            logger.warning(
                "Could not read courses cache "
                "version. Cache will be skipped. "
                "Error: %s",
                exc,
            )

            return None

    async def invalidate_courses(
        self,
    ) -> None:
        if self.client is None:
            return

        try:
            await self.client.incr(
                COURSES_VERSION_KEY
            )

            logger.info(
                "Courses cache invalidated"
            )

        except RedisError as exc:
            # Изменение данных уже успешно
            # прошло в PostgreSQL.
            # Ошибка Redis не должна превращать
            # успешный PATCH/POST/DELETE в 500.
            logger.warning(
                "Could not invalidate Redis cache. "
                "Continuing without cache. "
                "Error: %s",
                exc,
            )

    @staticmethod
    def build_courses_list_key(
        *,
        version: int,
        published_only: bool,
        limit: int,
        offset: int,
    ) -> str:
        visibility = (
            "published"
            if published_only
            else "admin"
        )

        return (
            "pylearn:education:"
            f"courses:v{version}:"
            f"{visibility}:"
            f"limit:{limit}:"
            f"offset:{offset}"
        )


redis_cache = RedisCache()