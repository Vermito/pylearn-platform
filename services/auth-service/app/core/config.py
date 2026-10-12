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
    auth_db_user: str
    auth_db_password: str
    auth_db_name: str
    auth_db_host: str
    auth_db_port: int

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # API Gateway
    api_root_path: str = ""

    # Test PostgreSQL
    auth_test_db_user: str | None = None
    auth_test_db_password: str | None = None
    auth_test_db_name: str | None = None
    auth_test_db_host: str | None = None
    auth_test_db_port: int | None = None

    @property
    def database_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.auth_db_user}:"
            f"{self.auth_db_password}"
            f"@{self.auth_db_host}:"
            f"{self.auth_db_port}/"
            f"{self.auth_db_name}"
        )

    @property
    def test_database_url(
        self,
    ) -> str | None:
        if not all(
            [
                self.auth_test_db_user,
                self.auth_test_db_password,
                self.auth_test_db_name,
                self.auth_test_db_host,
                self.auth_test_db_port,
            ]
        ):
            return None

        return (
            "postgresql+asyncpg://"
            f"{self.auth_test_db_user}:"
            f"{self.auth_test_db_password}"
            f"@{self.auth_test_db_host}:"
            f"{self.auth_test_db_port}/"
            f"{self.auth_test_db_name}"
        )

    @property
    def auth_test_database_url(
        self,
    ) -> str | None:
        return self.test_database_url

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


settings = Settings()