"""
Configuration settings for the application.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "ResearchPilot"
    app_version: str = "1.0.0"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-flash-latest"
    upload_max_size_mb: int = 25
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 100
    rag_top_k: int = 5

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")


def get_settings() -> Settings:
    """Get application settings dynamically."""
    return Settings()
