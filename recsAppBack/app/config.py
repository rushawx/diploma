import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration settings"""

    # Database Configuration
    POSTGRES_USER: str = os.getenv("PG_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("PG_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("PG_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("PG_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("PG_DATABASE", "postgres")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Database Connection Pooling
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    DB_AUTOCOMMIT: bool = os.getenv("DB_AUTOCOMMIT", "false").lower() == "true"
    DB_AUTOFLUSH: bool = os.getenv("DB_AUTOFLUSH", "false").lower() == "true"

    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # OAuth2 Configuration
    OAUTH2_TOKEN_URL: str = os.getenv("OAUTH2_TOKEN_URL", "token")

    # API Configuration
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Student Projects Recommender System")
    VERSION: str = os.getenv("VERSION", "1.0.0")

    # Security Configuration
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    ALLOWED_METHODS: list[str] = os.getenv("ALLOWED_METHODS", "*").split(",")
    ALLOWED_HEADERS: list[str] = os.getenv("ALLOWED_HEADERS", "*").split(",")

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = os.getenv(
        "LOG_LEVEL", "INFO"
    )
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", "1"))

    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = (
        os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    )
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

    # Admin Configuration
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "SYSTEM")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "change-me")

    # ML/Embedding Configuration
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))

    # Recommendation Configuration
    DEFAULT_RECOMMENDATION_COUNT: int = int(
        os.getenv("DEFAULT_RECOMMENDATION_COUNT", "10")
    )
    MIN_SIMILARITY_THRESHOLD: float = float(
        os.getenv("MIN_SIMILARITY_THRESHOLD", "0.1")
    )

    def validate(self) -> None:
        """Validate critical configuration values"""
        if self.SECRET_KEY == "your-secret-key-change-in-production":
            if not self.DEBUG:
                raise ValueError("SECRET_KEY must be set in production")
        if self.POSTGRES_PASSWORD == "postgres":
            if not self.DEBUG:
                raise ValueError("POSTGRES_PASSWORD must be changed in production")


settings = Settings()
