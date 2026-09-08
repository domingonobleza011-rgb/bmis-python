import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://bmis_user:bmis_pass@localhost:5432/bmis"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    # Kept as a plain comma-separated string, not list[str] — pydantic-settings
    # tries to JSON-parse env vars typed as list[str], which breaks on a plain
    # value like "*" or "https://a.com,https://b.com". Split it where it's used.
    cors_origins: str = "*"
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
