"""
Application Configuration - Settings from Environment Variables
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_ENV: str = "dev"
    DEMO_MODE: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./recircle.db"
    
    # Authentication
    JWT_SECRET: str = "dev-secret-change-in-production-min-32-chars"
    JWT_ACCESS_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Model
    MODEL_PATH: str = "./app/data/weights/model.pt"
    MODEL_CONFIG_PATH: str = "./app/data/weights/model_config.json"
    CONFIDENCE_THRESHOLD: float = 0.60
    
    # Upload & Rate Limits
    MAX_UPLOAD_MB: int = 5
    RATE_LIMIT_PER_MIN: int = 15

    # LLM Primary (NVIDIA NIM - OpenAI compatible)
    LLM_PRIMARY_PROVIDER: str = "openai"
    LLM_PRIMARY_MODEL: str = "nvidia/nemotron-3-ultra"
    LLM_PRIMARY_API_KEY: str = ""
    LLM_PRIMARY_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # LLM Fallback (NVIDIA NIM - OpenAI compatible)
    LLM_FALLBACK_PROVIDER: str = "openai"
    LLM_FALLBACK_MODEL: str = "nvidia/llama-3.1-nemotron-70b-instruct"
    LLM_FALLBACK_API_KEY: str = ""
    LLM_FALLBACK_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # LLM Timeout
    LLM_TIMEOUT_SECONDS: int = 60


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()