from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # API Configuration
    APP_NAME: str = "CallerWatch API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/callerwatch"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600

    # External APIs
    ABUSEIPDB_API_KEY: Optional[str] = None
    OTX_API_KEY: Optional[str] = None
    GOOGLE_SAFE_BROWSING_API_KEY: Optional[str] = None

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_SUSPICIOUS_CALLS: str = "suspicious-calls"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
