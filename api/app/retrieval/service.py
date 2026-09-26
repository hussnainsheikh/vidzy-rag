from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import ConfigDict, Field

from api.app.vectorstore import VectorStoreManager


@dataclass(frozen=True)
class ScoredDocument:
    document: Document
    score: float


class ChromaScoredRetriever(BaseRetriever):
    """LangChain retriever that retains Chroma relevance scores."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    manager: VectorStoreManager = Field(exclude=True)
    scope: str
    k: int = 5
    metadata_filter: dict | None = None
    last_results: list[ScoredDocument] = Field(default_factory=list, exclude=True)

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> list[Document]:
        raw = self.manager.get_store(self.scope).similarity_search_with_relevance_scores(
            query,
            k=self.k,
            filter=self.metadata_filter,
        )
        self.last_results = [ScoredDocument(document=doc, score=max(0.0, min(1.0, float(score)))) for doc, score in raw]
        return [item.document for item in self.last_results]


class RetrievalService:
    def __init__(self, manager: VectorStoreManager):
        self.manager = manager

    def retrieve(
        self,
        query: str,
        *,
        scope: str,
        limit: int,
        metadata_filter: dict | None = None,
    ) -> list[ScoredDocument]:
        retriever = ChromaScoredRetriever(
            manager=self.manager,
            scope=scope,
            k=limit,
            metadata_filter=metadata_filter,
        )
        retriever.invoke(query)
        return retriever.last_results

    def retrieve_scopes(self, query: str, *, scopes: list[str], limit: int) -> list[ScoredDocument]:
        combined: list[ScoredDocument] = []
        for scope in scopes:
            combined.extend(self.retrieve(query, scope=scope, limit=limit))
        return sorted(combined, key=lambda item: item.score, reverse=True)[:limit]
