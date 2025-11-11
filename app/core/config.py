"""
ADA.MARINA Configuration
Aviation-grade configuration management for West Istanbul Marina
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    APP_NAME: str = "ADA.MARINA West Istanbul"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4

    # Database - PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "marina"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "ada_marina_wim"
    DATABASE_URL: str

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str
    REDIS_URL: str

    # Neo4j
    NEO4J_HOST: str = "neo4j"
    NEO4J_PORT: int = 7687
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str
    NEO4J_URL: str

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"

    # Parasut (Turkish E-Invoice)
    PARASUT_CLIENT_ID: str = ""
    PARASUT_CLIENT_SECRET: str = ""
    PARASUT_USERNAME: str = ""
    PARASUT_PASSWORD: str = ""
    PARASUT_COMPANY_ID: str = ""

    # VHF Radio
    VHF_CHANNEL: int = 72
    VHF_FREQUENCY: str = "156.625"
    VHF_SUPPORTED_LANGUAGES: str = "tr,en,el"

    # Marina Configuration
    MARINA_NAME: str = "West Istanbul Marina"
    TOTAL_BERTHS: int = 600
    MARINA_LOCATION: str = "41.0082° N, 28.9784° E"
    MARINA_TIMEZONE: str = "Europe/Istanbul"

    # Compliance
    WIM_REGULATION_VERSION: str = "2025-v1"
    COMPLIANCE_THRESHOLD: float = 0.98

    # Monitoring
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    GRAFANA_PASSWORD: str = "admin_secure_2025"

    # SEAL Learning
    SEAL_LEARNING_ENABLED: bool = True
    SEAL_CONFIDENCE_THRESHOLD: float = 0.85
    SEAL_UPDATE_INTERVAL: int = 3600

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
