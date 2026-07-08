"""
Centralized application configuration.

All environment-driven settings are declared here and nowhere else, so the
rest of the codebase imports `settings` instead of calling os.getenv directly.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # --- OpenAI ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # --- Semantic Scholar ---
    semantic_scholar_api_key: str = ""
    semantic_scholar_base_url: str = "https://api.semanticscholar.org/graph/v1"

    # --- arXiv ---
    arxiv_base_url: str = "https://export.arxiv.org/api/query"
    arxiv_request_delay_seconds: float = 3.0

    # --- Database ---
    database_url: str = "sqlite:///./data/app.db"

    # --- Vector store ---
    faiss_index_dir: str = "./data/faiss_indexes"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384  # all-MiniLM-L6-v2 output size

    # --- Collection limits ---
    max_papers_per_source: int = 20

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def ensure_data_dirs(self) -> None:
        Path(self.faiss_index_dir).mkdir(parents=True, exist_ok=True)
        db_path = self.database_url.replace("sqlite:///", "")
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

