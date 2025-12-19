from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "RentMachine"
    API_V1_STR: str = "/api/v1"
    
    # MongoDB
    MONGODB_URL: str
    DATABASE_NAME: str = "rentmachine"
    
    # AWS Defaults (Can be overridden per account in DB, but global defaults here if needed)
    AWS_DEFAULT_REGION: str = "us-east-1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    
    # Proxy (Optional)
    PROXY_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
