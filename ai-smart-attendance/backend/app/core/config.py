from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List
import os


class Settings(BaseSettings):
    APP_NAME: str = "AI Smart Attendance System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite+aiosqlite:///./attendance.db"

    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    FACE_RECOGNITION_THRESHOLD: float = 0.6
    EMOTION_DETECTION_ENABLED: bool = True
    ATTENTION_TRACKING_ENABLED: bool = True
    FRAME_SKIP: int = 3
    MIN_PRESENCE_SECONDS: int = 300

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    STORAGE_PATH: str = "./storage"
    IMAGES_PATH: str = "./storage/images"
    EMBEDDINGS_PATH: str = "./storage/embeddings"
    EXPORTS_PATH: str = "./storage/exports"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure storage dirs exist
for path in [settings.STORAGE_PATH, settings.IMAGES_PATH, 
             settings.EMBEDDINGS_PATH, settings.EXPORTS_PATH]:
    os.makedirs(path, exist_ok=True)
