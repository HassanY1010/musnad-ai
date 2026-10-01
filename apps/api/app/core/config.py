"""
MUSNAD AI - Application Configuration
All settings are loaded from environment variables.
No secrets are hard-coded.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change_this_in_production"
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    KB_VERSION: str = "KB-001"
    PROMPT_VERSION: str = "v1"
    ALLOWED_ORIGINS: str = "https://musnad-ai-1.onrender.com,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/musnad_ai"
    DATABASE_TEST_URL: Optional[str] = None

    # AI / LLM
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.1

    # RAG & Retrieval
    RETRIEVAL_TOP_K: int = 5
    SEMANTIC_THRESHOLD: float = 0.65
    ABSTENTION_THRESHOLD: float = 0.50
    MAX_CLAIMS_PER_ANALYSIS: int = 20
    RERANKER_TOP_K: int = 10
    BM25_WEIGHT: float = 0.4
    SEMANTIC_WEIGHT: float = 0.6

    # Security & Limits
    MAX_UPLOAD_MB: int = 10
    RATE_LIMIT_ANONYMOUS: str = "20/minute"
    RATE_LIMIT_AUTHENTICATED: str = "100/minute"
    RATE_LIMIT_ADMIN: str = "1000/minute"
    DEMO_MODE: bool = True
    ADMIN_EMAIL: str = "admin@musnad.ai"
    ADMIN_PASSWORD: str = "change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
