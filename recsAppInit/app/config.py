import os
from dotenv import load_dotenv
from typing import Literal

load_dotenv()


class Settings:
    """Initialization service configuration"""

    # Database Configuration
    POSTGRES_USER: str = os.getenv("PG_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("PG_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("PG_HOST", "db")
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

    # Data Configuration
    DATA_PATH: str = os.getenv("DATA_PATH", "data.xlsx")
    EMBEDDINGS_PATH: str = os.getenv("EMBEDDINGS_PATH", "item_embeddings.pkl")
    TITLES_WITH_TAGS_PATH: str = os.getenv("TITLES_WITH_TAGS_PATH", "titles_with_tags_dict.pkl")
    TAGS_SET_PATH: str = os.getenv("TAGS_SET_PATH", "tags_set.pkl")

    # Vector Configuration
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    TAGS_VECTOR_DIMENSION: int = int(os.getenv("TAGS_VECTOR_DIMENSION", "1914"))

    # Model Configuration
    TRANSFORMER_MODEL: str = os.getenv(
        "TRANSFORMER_MODEL",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )

    # Validation Configuration
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "100"))
    SKIP_EMBEDDING: bool = (
        os.getenv("SKIP_EMBEDDING", "false").lower() == "true"
    )

    # Error Handling
    STOP_ON_ERROR: bool = (
        os.getenv("STOP_ON_ERROR", "false").lower() == "true"
    )

    # Admin Configuration
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "SYSTEM")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "change-me")

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = os.getenv(
        "LOG_LEVEL", "INFO"
    )


settings = Settings()