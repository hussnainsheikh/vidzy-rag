from __future__ import annotations

import os
from functools import lru_cache

# This must be set before importing huggingface_hub through the LangChain
# integration because the hub snapshots transfer flags during import.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache(maxsize=4)
def _cached_embeddings(model_name: str, device: str) -> Embeddings:
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )


def get_embeddings(model_name: str, device: str = "cpu") -> Embeddings:
    """Return one shared embedding-model instance per process/configuration."""
    return _cached_embeddings(model_name, device)
