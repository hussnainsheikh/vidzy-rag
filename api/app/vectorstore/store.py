from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from api.app.config import Settings


class VectorStoreManager:
    """Owns physically separate public and internal Chroma collections."""

    def __init__(self, settings: Settings, embeddings: Embeddings):
        self.settings = settings
        self.embeddings = embeddings
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
        self._stores: dict[str, Chroma] = {}

    def collection_name(self, scope: str) -> str:
        if scope == "public":
            return self.settings.public_collection
        if scope == "internal":
            return self.settings.internal_collection
        raise ValueError(f"unsupported collection scope: {scope}")

    def get_store(self, scope: str) -> Chroma:
        if scope not in self._stores:
            self._stores[scope] = Chroma(
                collection_name=self.collection_name(scope),
                embedding_function=self.embeddings,
                persist_directory=str(self.settings.chroma_path),
                collection_metadata={"hnsw:space": "cosine"},
            )
        return self._stores[scope]

    def reset_collection(self, scope: str) -> Chroma:
        store = self.get_store(scope)
        try:
            store.delete_collection()
        except ValueError:
            pass
        self._stores.pop(scope, None)
        return self.get_store(scope)

    def replace_documents(self, scope: str, documents: list[Document], ids: list[str]) -> int:
        store = self.get_store(scope)
        existing_ids = store.get(include=[]).get("ids", [])
        if existing_ids:
            store.delete(ids=existing_ids)
        if documents:
            store.add_documents(documents, ids=ids)
        return len(documents)

    def count(self, scope: str) -> int:
        return int(self.get_store(scope)._collection.count())
