from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

settings = Settings(_env_file=f".env.{os.getenv('ENV', 'development')}")
