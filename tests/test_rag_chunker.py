"""Tests for the dependency-free chunker (no model load required)."""

from __future__ import annotations

from pathlib import Path

from utility_mcp_server.rag.chunker import chunk_docs_dir


def test_chunker_emits_chunks_with_metadata() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs_dir = repo_root / "docs"

    chunks = chunk_docs_dir(docs_dir)
    assert chunks, "expected at least one chunk from the bundled docs"

    # Every chunk has the required metadata fields populated.
    categories = {c.category for c in chunks}
    assert categories.issubset({"apis", "concepts", "languages", "models"})

    # Every chunk_id is unique and sequential from 0.
    ids = [c.chunk_id for c in chunks]
    assert ids == list(range(len(chunks)))

    # ``embed_text`` always prepends the [category/doc_key] header.
    sample = chunks[0]
    assert sample.embed_text().startswith(f"[{sample.category}/{sample.doc_key}]")


def test_chunker_handles_nested_language_keys() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs_dir = repo_root / "docs"

    chunks = chunk_docs_dir(docs_dir)
    language_keys = {c.doc_key for c in chunks if c.category == "languages"}
    # All language doc keys follow ``<binding>/<file>``.
    assert all("/" in key for key in language_keys), language_keys
