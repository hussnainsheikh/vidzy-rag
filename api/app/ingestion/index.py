from __future__ import annotations

import argparse
import json

from api.app.config import Settings
from api.app.embeddings import get_embeddings
from api.app.ingestion.loaders import document_id, load_all_documents
from api.app.vectorstore import VectorStoreManager


def index_knowledge(settings: Settings | None = None) -> dict[str, int]:
    settings = settings or Settings()
    documents = load_all_documents(settings.knowledge_path)
    manager = VectorStoreManager(
        settings,
        get_embeddings(settings.embedding_model, settings.embedding_device),
    )
    counts: dict[str, int] = {}
    for scope in ("public", "internal"):
        scoped = [doc for doc in documents if doc.metadata["scope"] == scope]
        counts[scope] = manager.replace_documents(scope, scoped, [document_id(doc) for doc in scoped])
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild Vidzy public/internal Chroma collections")
    parser.add_argument("--chroma-path", help="Override CHROMA_PATH")
    args = parser.parse_args()
    settings = Settings(chroma_path=args.chroma_path) if args.chroma_path else Settings()
    print(json.dumps(index_knowledge(settings), indent=2))


if __name__ == "__main__":
    main()
