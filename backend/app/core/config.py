
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Self Xerox Kiosk System"
    API_V1_STR: str = "/api/v1"
    
    # DATABASE
    # Support both DATABASE_URL (for Render.com) and individual variables (for local)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "self_xerox")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeywhichshouldbechangedinproduction")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days for kiosk stability

    # STORAGE (S3 Compatible)
    S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "https://s3.amazonaws.com")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "xerox-files")
    
    # NETWORK
    HOST_IP: str = os.getenv("HOST_IP", "localhost")
    PORT: int = 8000
    
    # PRINTER
    PRINTER_NAME: str = "PDF_Printer"

    model_config = {
        "env_file": ".env"
    }

    def __validator__(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            # Use DATABASE_URL if provided (Render.com), otherwise build from individual variables
            if self.DATABASE_URL:
                self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
            else:
                self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()
try:
    settings.__validator__()
except Exception as e:
    print(f"Config Warning: {e}")
