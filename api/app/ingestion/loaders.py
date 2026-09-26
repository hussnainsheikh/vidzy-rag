from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document


def deterministic_id(namespace: str, value: str) -> str:
    return hashlib.sha256(f"{namespace}:{value}".encode()).hexdigest()


def _common_metadata(*, scope: str, source: str, document_type: str, category: str = "general") -> dict:
    return {
        "scope": scope,
        "source_document": source,
        "source_label": Path(source).stem.replace("-", " ").title(),
        "document_type": document_type,
        "category": category,
    }


def load_markdown_documents(knowledge_path: Path) -> list[Document]:
    documents: list[Document] = []
    for scope in ("public", "internal"):
        for path in sorted((knowledge_path / scope).rglob("*.md")):
            relative = path.relative_to(knowledge_path).as_posix()
            text = path.read_text(encoding="utf-8")
            h1 = path.stem.replace("-", " ").title()
            sections = re.split(r"(?=^##\s+)", text, flags=re.MULTILINE)
            for position, section in enumerate(sections):
                section = section.strip()
                if not section or section.startswith("## Evidence"):
                    continue
                heading_match = re.search(r"^##\s+(.+)$", section, re.MULTILINE)
                heading = heading_match.group(1).strip() if heading_match else h1
                metadata = _common_metadata(
                    scope=scope,
                    source=relative,
                    document_type="markdown",
                    category=path.parent.name if path.parent.name not in {"public", "internal"} else "general",
                )
                metadata.update({"heading": heading, "chunk_index": position})
                documents.append(Document(page_content=section, metadata=metadata))
    return documents


def _read_jsonl(path: Path) -> Iterable[dict]:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def load_metadata_documents(knowledge_path: Path) -> list[Document]:
    metadata_path = knowledge_path / "metadata"
    documents: list[Document] = []

    for item in _read_jsonl(metadata_path / "facts.jsonl"):
        # Non-verified claims are quarantined even if a future dataset marks
        # them public accidentally.
        scope = item["scope"] if item.get("status") == "verified" else "internal"
        metadata = _common_metadata(
            scope=scope,
            source="metadata/facts.jsonl",
            document_type="fact",
            category=item.get("category", "general"),
        )
        metadata.update(
            {
                "fact_id": item["id"],
                "status": item["status"],
                "declared_scope": item["scope"],
                "tags": ",".join(item.get("tags", [])),
            }
        )
        documents.append(Document(page_content=item["fact"], metadata=metadata))

    for item in _read_jsonl(metadata_path / "questions.jsonl"):
        if item.get("scope") != "public" or item.get("status") != "verified":
            continue
        aliases = "\n".join(f"- {alias}" for alias in item.get("aliases", []))
        content = f"Question: {item['question']}\nAlternative phrasings:\n{aliases}\nAnswer: {item['answer']}"
        metadata = _common_metadata(
            scope="public",
            source="metadata/questions.jsonl",
            document_type="canonical_question",
            category=item.get("category", "general"),
        )
        metadata.update(
            {
                "question_id": item["id"],
                "canonical_question": item["question"],
                "canonical_answer": item["answer"],
                "status": item["status"],
                "source_fact_ids": ",".join(item["source_fact_ids"]),
                "tags": ",".join(item.get("tags", [])),
            }
        )
        documents.append(Document(page_content=content, metadata=metadata))

    # Source registry can expose implementation paths, so it is always internal.
    for item in _read_jsonl(metadata_path / "sources.jsonl"):
        metadata = _common_metadata(
            scope="internal",
            source="metadata/sources.jsonl",
            document_type="source_registry",
            category=item.get("type", "source"),
        )
        metadata.update({"source_id": item["id"], "registered_scope": item.get("scope", "unknown")})
        documents.append(
            Document(
                page_content=f"Source {item['id']}: {item['description']} ({item['path']})",
                metadata=metadata,
            )
        )
    return documents


def load_all_documents(knowledge_path: Path) -> list[Document]:
    return load_markdown_documents(knowledge_path) + load_metadata_documents(knowledge_path)


def document_id(document: Document) -> str:
    metadata = document.metadata
    identity = "|".join(
        str(metadata.get(key, ""))
        for key in ("scope", "source_document", "document_type", "question_id", "fact_id", "source_id", "chunk_index")
    )
    return deterministic_id("vidzy", identity)
