import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", BACKEND_DIR / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="Xinming Backend", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    mysql_host: str = Field(default="127.0.0.1", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="123456", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="xinming", alias="MYSQL_DATABASE")

    github_client_id: str = Field(default="", alias="GITHUB_CLIENT_ID")
    github_client_secret: str = Field(default="", alias="GITHUB_CLIENT_SECRET")
    jwt_secret: str = Field(default="change-me-in-production", alias="JWT_SECRET")
    frontend_url: str = Field(default="http://localhost:9002", alias="FRONTEND_URL")
    csv_storage_dir: str = Field(default=str(BACKEND_DIR / "storage" / "csv"), alias="CSV_STORAGE_DIR")
    csv_max_upload_mb: int = Field(default=20, alias="CSV_MAX_UPLOAD_MB")
    csv_retention_days: int = Field(default=30, alias="CSV_RETENTION_DAYS")
    csv_user_max_files: int = Field(default=50, alias="CSV_USER_MAX_FILES")
    csv_user_max_storage_mb: int = Field(default=500, alias="CSV_USER_MAX_STORAGE_MB")

    cors_origins: list[str] | str = Field(
        default=[
            "http://localhost:9002",
            "http://127.0.0.1:9002",
            "http://localhost:9003",
            "http://127.0.0.1:9003",
        ],
        alias="CORS_ORIGINS",
    )

    @computed_field
    @property
    def mysql_url(self) -> str:
        return (
            f"mysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @computed_field
    @property
    def csv_max_upload_bytes(self) -> int:
        return self.csv_max_upload_mb * 1024 * 1024

    @computed_field
    @property
    def csv_user_max_storage_bytes(self) -> int:
        return self.csv_user_max_storage_mb * 1024 * 1024

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        if isinstance(self.cors_origins, list):
            return self.cors_origins

        raw = self.cors_origins.strip()
        if not raw:
            return []

        if raw.startswith("["):
            return json.loads(raw)

        return [item.strip() for item in raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
