import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://bmis_user:bmis_pass@localhost:5432/bmis")
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")

    class Config:
        env_file = ".env"


settings = Settings()
os.makedirs(settings.upload_dir, exist_ok=True)
