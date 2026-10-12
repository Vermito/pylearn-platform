from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        candidate = parent / ".env"

        if candidate.exists():
            return candidate

    return None


ENV_FILE = find_env_file()


class Settings(BaseSettings):
    # PostgreSQL
    education_db_user: str
    education_db_password: str
    education_db_name: str
    education_db_host: str
    education_db_port: int

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    # API Gateway
    api_root_path: str = ""

    # Runner
    runner_service_url: str
    runner_api_key: str

    # RabbitMQ
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_vhost: str = "/"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    redis_cache_ttl_seconds: int = 300

    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.education_db_user}:"
            f"{self.education_db_password}"
            f"@{self.education_db_host}:"
            f"{self.education_db_port}/"
            f"{self.education_db_name}"
        )

    @property
    def rabbitmq_url(self) -> str:
        return (
            "amqp://"
            f"{self.rabbitmq_user}:"
            f"{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:"
            f"{self.rabbitmq_port}/"
        )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


settings = Settings()