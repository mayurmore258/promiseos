"""PromiseOS Application Configuration.

Loads environment variables using pydantic-settings.
Keeps sensitive API keys safe and defaults to mock/local development mode.
"""

from pathlib import Path
from typing import Any, List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    APP_NAME: str = "PromiseOS"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", description="development | testing | production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    MOCK_LLM: bool = Field(default=True, description="Force deterministic local mock LLM provider")
    ML_COMMITMENT_ENABLED: bool = Field(
        default=True,
        description="Enable local ML commitment classification for extracted candidates",
    )
    ML_MODEL_PATH: str = Field(
        default="ml/models/commitment_classifier_v2_calibrated.joblib",
        description="Path to the active production ML model artifact (relative to backend root)",
    )

    # Database
    # Defaults to SQLite with aiosqlite for zero-config local testing.
    # Set to postgresql+psycopg://user:pass@host:5432/dbname for PostgreSQL / Supabase.
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./promiseos.db",
        description="SQLAlchemy database URL",
    )
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase project URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, description="Supabase anon/service key")

    # LLM Provider Keys (Empty by default for local development)
    GROQ_API_KEY: Optional[str] = Field(default=None, description="Groq API Key")
    NVIDIA_API_KEY: Optional[str] = Field(default=None, description="NVIDIA NIM API Key")
    SAMBANOVA_API_KEY: Optional[str] = Field(default=None, description="SambaNova API Key")
    GEMINI_API_KEY: Optional[str] = Field(default=None, description="Google Gemini API Key")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, description="OpenRouter API Key")

    # Optional External Evidence Services
    COHERE_API_KEY: Optional[str] = Field(default=None, description="Cohere Rerank / Embedding Key")
    EXA_API_KEY: Optional[str] = Field(default=None, description="Exa Search Key")
    FIRECRAWL_API_KEY: Optional[str] = Field(default=None, description="Firecrawl Web Scraping Key")

    # File Uploads
    MAX_UPLOAD_SIZE_MB: int = Field(default=25, description="Maximum upload size in Megabytes")
    UPLOAD_DIR: str = Field(default="./data/uploads", description="Directory to store uploaded evidence files")

    # CORS
    CORS_ORIGINS: Any = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        description="Allowed origins for CORS",
    )

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, (list, tuple)):
            return [str(origin).strip() for origin in v if str(origin).strip()]
        return ["http://localhost:5173", "http://localhost:3000"]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def upload_path(self) -> Path:
        path = Path(self.UPLOAD_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def active_llm_providers(self) -> List[str]:
        """Returns list of real providers that have API keys configured."""
        providers = []
        if self.GROQ_API_KEY:
            providers.append("groq")
        if self.NVIDIA_API_KEY:
            providers.append("nvidia")
        if self.SAMBANOVA_API_KEY:
            providers.append("sambanova")
        if self.GEMINI_API_KEY:
            providers.append("gemini")
        if self.OPENROUTER_API_KEY:
            providers.append("openrouter")
        return providers

    def should_use_mock_llm(self) -> bool:
        """Determines whether mock LLM should be used.
        True if explicitly set or if no real API keys are present.
        """
        if self.MOCK_LLM:
            return True
        return len(self.active_llm_providers) == 0


settings = Settings()
