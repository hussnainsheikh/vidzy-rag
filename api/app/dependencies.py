from __future__ import annotations

from functools import lru_cache

from api.app.config import get_settings
from api.app.embeddings import get_embeddings
from api.app.rag import RagService
from api.app.retrieval import RetrievalService
from api.app.vectorstore import VectorStoreManager


@lru_cache(maxsize=1)
def get_store_manager() -> VectorStoreManager:
    settings = get_settings()
    return VectorStoreManager(settings, get_embeddings(settings.embedding_model, settings.embedding_device))


@lru_cache(maxsize=1)
def get_retrieval_service() -> RetrievalService:
    return RetrievalService(get_store_manager())


@lru_cache(maxsize=1)
def get_rag_service() -> RagService:
    return RagService(get_settings(), get_retrieval_service())


def clear_runtime_caches() -> None:
    get_rag_service.cache_clear()
    get_retrieval_service.cache_clear()
    get_store_manager.cache_clear()
