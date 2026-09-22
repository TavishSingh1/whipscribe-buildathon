from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Podcast Clip Factory"
    environment: str = "development"
    frontend_origin: str = "http://localhost:5173"
    database_url: str = "sqlite+aiosqlite:///./podcast_clip_factory.db"
    jwt_secret: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60 * 24 * 7
    openai_api_key: str | None = None
    whipscribe_api_key: str | None = None
    encryption_key: str = Field(default="change-me-32-byte-minimum-secret", min_length=16)
    upload_dir: str = "uploads"
    max_upload_mb: int = 750
    free_episode_limit: int = 5
    free_generation_limit: int = 50
    free_processing_minutes: int = 300
    demo_mode_enabled: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
