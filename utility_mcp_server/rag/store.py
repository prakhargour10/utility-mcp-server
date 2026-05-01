"""Process-wide singleton accessors for the RAG vector store.

The store is expensive to build (it embeds every chunk via Bedrock Titan),
so we lazy-load it once per process. If a saved store JSON exists at
``settings.rag_embeddings_path`` we load that; otherwise we build it from
the markdown corpus on disk.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ..config import Settings, get_settings
from .embed import VectorStore, build_vector_store

logger = logging.getLogger(__name__)


_store: VectorStore | None = None
_lock = asyncio.Lock()


async def get_vector_store(
    settings: Settings | None = None,
    *,
    embeddings_path: Path | None = None,
) -> VectorStore:
    """Return the process-wide :class:`VectorStore`, building it on first use."""
    global _store
    if _store is not None:
        return _store

    settings = settings or get_settings()
    path = embeddings_path or settings.rag_embeddings_path

    async with _lock:
        if _store is not None:
            return _store

        if path.exists():
            logger.info("Loading vector store from %s", path)
            _store = VectorStore.load(path)
        else:
            logger.info(
                "No saved vector store at %s — building from local docs.", path
            )
            _store = await build_vector_store(settings)
            try:
                _store.save(path)
                logger.info("Persisted vector store to %s", path)
            except OSError as exc:
                logger.warning("Could not persist vector store: %s", exc)

        logger.info("Vector store ready (%d chunks)", len(_store))
        return _store


def reset_vector_store() -> None:
    """Drop the in-process cache (used in tests)."""
    global _store
    _store = None
