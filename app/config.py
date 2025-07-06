import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Settings
    API_TITLE: str
    API_DESCRIPTION: str
    VERSION: str
    OPEN_API_JSON_FILENAME: str
    DEBUG: bool

    # MongoDB Settings
    MONGODB_URL: str = "mongodb://localhost:27017/shrimahatapasvi"
    DB_NAME: str

    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Token URL
    TOKEN_URL: str = "/api/auth/login"

    # AWS Settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "shrimahatapasvifoundationdata")
    S3_URL_EXPIRY: int = 3600  # URL expiry in seconds

    class Config:
        env_file = ".env"

settings = Settings()
