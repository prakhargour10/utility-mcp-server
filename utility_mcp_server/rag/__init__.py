"""RAG (Retrieval-Augmented Generation) subsystem.

Embeds the local Pine Labs documentation bundle into a FAISS vector
index and exposes semantic search on top of it.

Public surface:

* ``RagIndex`` — load/search/build a FAISS index over the docs.
* ``DocChunk``  — a single retrievable unit of documentation.
* ``build_and_save_index`` — CLI/programmatic index builder.
"""

from __future__ import annotations

from .chunker import DocChunk, chunk_docs_dir
from .index import RagIndex, SearchHit, build_and_save_index

__all__ = [
    "DocChunk",
    "RagIndex",
    "SearchHit",
    "build_and_save_index",
    "chunk_docs_dir",
]
