# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from .env
    )

    HF_TOKEN: str = ""
    
    AZURE_OPENAI_API_VERSION: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4-o"
    AZURE_OPENAI_TARGET_URI: str = ""
    
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"

settings = Settings()
