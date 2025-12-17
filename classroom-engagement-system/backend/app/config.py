import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # FastAPI
    app_name: str = "Classroom Engagement System"
    debug: bool = False
    
    # MongoDB
    mongodb_url: str = os.getenv(
        "MONGODB_URL",
        "mongodb://root:rootpassword@localhost:27017/classroom?authSource=admin"
    )
    db_name: str = "classroom"
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379")
    
    # Pyannote
    pyannote_model: str = "pyannote/speaker-diarization-3.1"
    pyannote_segmentation: str = "pyannote/segmentation-3.0"
    
    # Storage
    upload_dir: str = os.path.join(os.path.dirname(__file__), "../../uploads")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
