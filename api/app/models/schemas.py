from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ChatRequest(StrictModel):
    message: str = Field(min_length=2, max_length=500)

    @field_validator("message")
    @classmethod
    def meaningful_message(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("message must contain at least two characters")
        return value


class SearchRequest(StrictModel):
    query: str = Field(min_length=2, max_length=500)
    scope: Literal["public", "internal", "combined"] = "public"
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def meaningful_query(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("query must contain at least two characters")
        return value


class Source(BaseModel):
    id: str
    label: str
    category: str | None = None
    document_type: str


class RetrievalResult(BaseModel):
    content: str
    score: float
    metadata: dict[str, Any]
    citation: Source


class RelatedQuestion(BaseModel):
    question: str
    answer: str | None = None
    score: float
    category: str | None = None


class ChatResponse(BaseModel):
    answer: str
    response_type: Literal["direct_answer", "related_results", "no_reliable_answer"]
    confidence: float
    sources: list[Source] = Field(default_factory=list)
    related: list[RelatedQuestion] = Field(default_factory=list)
    response_mode: Literal["retrieval", "generative"]
    retrieval_details: list[dict[str, Any]] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    scope: Literal["public", "internal", "combined"]
    results: list[RetrievalResult]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    response_mode: Literal["retrieval", "generative"]
    vector_store_ready: bool
    collections: dict[str, int]
    version: str = "0.1.0"
