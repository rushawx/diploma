import os
from typing import Literal


class Settings:
    """Frontend configuration settings"""

    def __init__(self):
        self._load_streamlit_available()

    def _load_streamlit_available(self):
        """Check if streamlit is available and can load secrets"""
        try:
            import streamlit as st

            self._st = st
            self._use_secrets = True
        except Exception:
            self._st = None
            self._use_secrets = False

    def _get_secret(self, key: str, default: str = "") -> str:
        """Get configuration value from streamlit secrets or environment variables"""
        if self._use_secrets and self._st:
            return self._st.secrets.get(key, os.getenv(key, default))
        return os.getenv(key, default)

    @property
    def BACKEND_URL(self) -> str:
        return self._get_secret("BACKEND_URL", "back:8080")

    @property
    def BACKEND_TIMEOUT(self) -> int:
        return int(self._get_secret("BACKEND_TIMEOUT", "10"))

    @property
    def USE_HTTPS(self) -> bool:
        return self._to_bool(self._get_secret("USE_HTTPS", "false") == "true")

    def _to_bool(self, value: str) -> bool:
        """Convert string value to boolean"""
        return value.lower() == "true" if isinstance(value, str) else bool(value)

    @property
    def BACKEND_BASE_URL(self) -> str:
        protocol = "https" if self.USE_HTTPS else "http"
        return f"{protocol}://{self.BACKEND_URL}"

    @property
    def TOKEN_EXPIRE_MINUTES(self) -> int:
        return int(self._get_secret("TOKEN_EXPIRE_MINUTES", "30"))

    @property
    def AUTO_LOGOUT_ENABLED(self) -> bool:
        return self._to_bool(self._get_secret("AUTO_LOGOUT_ENABLED", "true"))

    @property
    def APP_TITLE(self) -> str:
        return self._get_secret("APP_TITLE", "Student Projects Recommender System")

    @property
    def PAGE_ICON(self) -> str:
        return self._get_secret("PAGE_ICON", "🎓")

    @property
    def LAYOUT(self) -> str:
        return self._get_secret("LAYOUT", "wide")

    @property
    def TRANSFORMER_MODEL(self) -> str:
        return self._get_secret(
            "TRANSFORMER_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        )

    @property
    def TRANSFORMER_CACHE_TTL(self) -> str:
        return self._get_secret("TRANSFORMER_CACHE_TTL", "10m")

    @property
    def TAGS_SET_FILE(self) -> str:
        return self._get_secret("TAGS_SET_FILE", "app/resources/tags_set.pkl")

    @property
    def ALS_MODEL_FILE(self) -> str:
        return self._get_secret(
            "ALS_MODEL_FILE", "app/resources/als_model_implicit.pkl"
        )

    @property
    def DATA_CACHE_TTL(self) -> str:
        return self._get_secret("DATA_CACHE_TTL", "10m")

    @property
    def DEFAULT_TOP_K(self) -> int:
        return int(self._get_secret("DEFAULT_TOP_K", "5"))

    @property
    def MIN_SIMILARITY_THRESHOLD(self) -> float:
        return float(self._get_secret("MIN_SIMILARITY_THRESHOLD", "0.1"))

    @property
    def LOADING_DATA_MESSAGE(self) -> str:
        return self._get_secret("LOADING_DATA_MESSAGE", "Loading data...")

    @property
    def LOADING_EMBEDDINGS_MESSAGE(self) -> str:
        return self._get_secret(
            "LOADING_EMBEDDINGS_MESSAGE", "Loading vector representations..."
        )

    @property
    def LOADING_TRANSFORMER_MESSAGE(self) -> str:
        return self._get_secret("LOADING_TRANSFORMER_MESSAGE", "Loading transformer...")

    @property
    def CONNECTION_ERROR_MESSAGE(self) -> str:
        return self._get_secret("CONNECTION_ERROR_MESSAGE", "Connection error: {}")

    @property
    def AUTH_ERROR_MESSAGE(self) -> str:
        return self._get_secret(
            "AUTH_ERROR_MESSAGE", "Authentication failed. Please login again."
        )

    @property
    def SESSION_EXPIRED_MESSAGE(self) -> str:
        return self._get_secret(
            "SESSION_EXPIRED_MESSAGE", "Session expired. Please login again."
        )

    @property
    def SESSION_STATE_KEYS(self) -> list:
        return [
            "access_token",
            "token_type",
            "username",
            "login_time",
            "user_profile",
        ]

    @property
    def ENABLE_CACHING(self) -> bool:
        return self._to_bool(self._get_secret("ENABLE_CACHING", "true"))

    @property
    def ENABLE_DEBUG_MODE(self) -> bool:
        return self._to_bool(self._get_secret("ENABLE_DEBUG_MODE", "false"))

    @property
    def LOG_LEVEL(self) -> Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        return self._get_secret("LOG_LEVEL", "INFO")

    @property
    def PYTORCH_DEVICE(self) -> str:
        return self._get_secret("PYTORCH_DEVICE", "")

    @property
    def FORCE_CPU(self) -> bool:
        return self._to_bool(self._get_secret("FORCE_CPU", "false"))

    @property
    def PYTORCH_THREADS(self) -> int:
        return int(self._get_secret("PYTORCH_THREADS", str(os.cpu_count())))

    def validate(self) -> None:
        """Validate critical configuration values"""
        if not self.BACKEND_URL:
            raise ValueError("BACKEND_URL must be configured")
        if self.BACKEND_TIMEOUT <= 0:
            raise ValueError("BACKEND_TIMEOUT must be positive")
        if self.DEFAULT_TOP_K <= 0:
            raise ValueError("DEFAULT_TOP_K must be positive")
        if not 0 <= self.MIN_SIMILARITY_THRESHOLD <= 1:
            raise ValueError("MIN_SIMILARITY_THRESHOLD must be between 0 and 1")


# Global settings instance
settings = Settings()
