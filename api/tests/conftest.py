from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app.config import Settings
from api.app.dependencies import get_rag_service, get_retrieval_service, get_store_manager
from api.app.embeddings import get_embeddings
from api.app.ingestion.index import index_knowledge
from api.app.main import create_app
from api.app.rag import RagService
from api.app.retrieval import RetrievalService
from api.app.vectorstore import VectorStoreManager


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def indexed_runtime(tmp_path_factory):
    chroma_path = tmp_path_factory.mktemp("chroma")
    settings = Settings(
        _env_file=None,
        app_env="test",
        knowledge_path=ROOT / "knowledge",
        chroma_path=chroma_path,
        internal_api_key="test-internal-key",
        direct_answer_threshold=0.68,
        related_results_threshold=0.35,
    )
    first = index_knowledge(settings)
    embeddings = get_embeddings(settings.embedding_model, settings.embedding_device)
    manager = VectorStoreManager(settings, embeddings)
    retrieval = RetrievalService(manager)
    rag = RagService(settings, retrieval)
    return settings, manager, retrieval, rag, first


@pytest.fixture(scope="session")
def client(indexed_runtime):
    settings, manager, retrieval, rag, _ = indexed_runtime
    app = create_app(settings)
    app.dependency_overrides[get_store_manager] = lambda: manager
    app.dependency_overrides[get_retrieval_service] = lambda: retrieval
    app.dependency_overrides[get_rag_service] = lambda: rag
    with TestClient(app) as test_client:
        yield test_client
