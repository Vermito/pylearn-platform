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
    progress_db_user: str
    progress_db_password: str
    progress_db_name: str
    progress_db_host: str
    progress_db_port: int

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    # API Gateway
    api_root_path: str = ""

    # RabbitMQ
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_vhost: str = "/"

    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.progress_db_user}:"
            f"{self.progress_db_password}"
            f"@{self.progress_db_host}:"
            f"{self.progress_db_port}/"
            f"{self.progress_db_name}"
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