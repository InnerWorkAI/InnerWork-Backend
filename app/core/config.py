from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    ENV: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    # Reset password
    RESET_TOKEN_EXPIRE_MINUTES: int

    # Resend
    RESEND_API_KEY: str
    EMAIL_FROM: str

    FRONTEND_URL: str

    GROQ_API_KEY: str

    ADMIN_PASSWORD: str

settings = Settings(_env_file=f".env.{os.getenv('ENV', 'development')}")