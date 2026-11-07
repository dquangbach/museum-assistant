from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = ""
    postgres_host: str = "localhost"
    postgres_user: str = "museum"
    postgres_password: str = "museum_dev"
    postgres_db: str = "museum"
    dataset_dir: Path = Path(__file__).resolve().parents[3] / "Dataset"
    admin_api_key: str = ""
    cors_origins: list[str] = []

    @model_validator(mode="after")
    def configure_database_url(self):
        if not self.database_url:
            self.database_url = URL.create("postgresql+psycopg", username=self.postgres_user,
                password=self.postgres_password, host=self.postgres_host, port=5432,
                database=self.postgres_db).render_as_string(hide_password=False)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
