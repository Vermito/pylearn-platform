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
    runner_api_key: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore",
    )


settings = Settings()