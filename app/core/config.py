from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    ENV: str = "development"

    DATABASE_URL: str
    REDIS_URL: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    # Reset password
    RESET_TOKEN_EXPIRE_MINUTES: int

    # Mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    FRONTEND_URL: str

    GROQ_API_KEY: str

settings = Settings(_env_file=f".env.{os.getenv('ENV', 'development')}")