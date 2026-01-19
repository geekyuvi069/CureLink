from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Doctor Appointment Assistant"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/doctor_appointments"
    
    # LLM Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # External APIs
    SLACK_WEBHOOK_URL: Optional[str] = None
    WHATSAPP_API_TOKEN: Optional[str] = None
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    
    # Email SMTP Settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
