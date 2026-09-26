from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Runtime configuration. Paid generation is enabled only by response_mode."""

    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "Vidzy RAG"
    knowledge_path: Path = REPOSITORY_ROOT / "knowledge"
    chroma_path: Path = REPOSITORY_ROOT / ".data" / "chroma"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    public_collection: str = "vidzy_public"
    internal_collection: str = "vidzy_internal"
    rag_response_mode: Literal["retrieval", "generative"] = "retrieval"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4.1-mini"
    openai_api_key: str | None = Field(default=None, repr=False)
    llm_fallback_to_retrieval: bool = True
    direct_answer_threshold: float = 0.68
    related_results_threshold: float = 0.35
    ambiguity_margin: float = 0.035
    retrieval_k: int = 5
    max_question_length: int = 500
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]
    internal_api_key: str | None = Field(default=None, repr=False)
    static_dir: Path = REPOSITORY_ROOT / "web" / "dist"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("direct_answer_threshold", "related_results_threshold", "ambiguity_margin")
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("retrieval thresholds must be between 0 and 1")
        return value

    @field_validator("retrieval_k")
    @classmethod
    def validate_retrieval_k(cls, value: int) -> int:
        if not 1 <= value <= 20:
            raise ValueError("retrieval_k must be between 1 and 20")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
