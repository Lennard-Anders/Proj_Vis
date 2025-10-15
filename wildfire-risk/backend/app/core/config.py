from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field(default="Wildfire Risk API")
    model_bundle_path: str = Field(default="models/bundles/current")
    enable_cors: bool = True
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
