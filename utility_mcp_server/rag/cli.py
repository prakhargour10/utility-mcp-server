"""Top-level CLI commands for managing the RAG vector store.

Two entrypoints are exposed via ``pyproject.toml`` ``[project.scripts]``:

* ``rag-rebuild`` — Chunk the markdown corpus under ``docs/``, embed each
  chunk with the local sentence-transformers model and save
  ``embeddings.json`` (chunks + dense vectors). Use this whenever the
  docs change.

* ``rag-load`` — Load the existing ``embeddings.json`` into memory and
  report its size. Optionally runs a FAISS dense search via ``--query``
  to smoke-test retrieval.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Sequence

from ..config import Settings, get_settings
from .embed import (
    VectorStore,
    build_vector_store,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _embeddings_path(settings: Settings) -> Path:
    return settings.rag_embeddings_path


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# ---------------------------------------------------------------------------
# rag-rebuild
# ---------------------------------------------------------------------------
def _build_rebuild_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag-rebuild",
        description=(
            "Rebuild the RAG chunk store from scratch: chunk the local "
            "markdown corpus and persist to embeddings.json."
        ),
    )
    parser.add_argument(
        "--chunk-size", type=int, default=1024,
        help="Tokens per chunk (default: 1024).",
    )
    parser.add_argument(
        "--overlap", dest="chunk_overlap", type=int, default=128,
        help="Token overlap between chunks (default: 128).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Override the embeddings.json output path.",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser


async def _do_rebuild(args: argparse.Namespace) -> int:
    settings = get_settings()
    docs_dir = settings.rag_raw_docs_dir
    out_path = args.output or _embeddings_path(settings)

    if not docs_dir.exists():
        logger.error("Docs directory does not exist: %s", docs_dir)
        return 2

    if out_path.exists():
        logger.info("Removing stale chunk store at %s", out_path)
        out_path.unlink()

    logger.info("Building chunk store from %s", docs_dir)
    store = await build_vector_store(
        settings,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    store.save(out_path)
    logger.info("Saved %d chunk(s) to %s", len(store), out_path)
    print(f"\nrag-rebuild OK: {len(store)} chunks -> {out_path}")
    return 0


def rebuild_main(argv: Sequence[str] | None = None) -> int:
    args = _build_rebuild_parser().parse_args(argv)
    _configure_logging(args.log_level)
    try:
        return asyncio.run(_do_rebuild(args))
    except KeyboardInterrupt:
        return 130


# ---------------------------------------------------------------------------
# rag-load
# ---------------------------------------------------------------------------
def _build_load_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rag-load",
        description=(
            "Load the existing RAG vector database (embeddings.json) and "
            "print summary info. Optionally runs a similarity search."
        ),
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Override the embeddings.json path.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional smoke-test query — embeds it and prints top hits.",
    )
    parser.add_argument(
        "--top-k", type=int, default=5,
        help="Number of hits to print when --query is given (default: 5).",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser


async def _do_load(args: argparse.Namespace) -> int:
    settings = get_settings()
    path = args.path or _embeddings_path(settings)
    if not path.exists():
        logger.error(
            "No vector store found at %s. Run `rag-rebuild` first.", path
        )
        return 2

    logger.info("Loading vector store from %s", path)
    store = VectorStore.load(path)
    print(f"\nrag-load OK: {len(store)} chunk(s) loaded from {path}")

    if not args.query:
        return 0

    hits = await store.search(args.query, top_k=args.top_k)
    print(f"\nTop {len(hits)} FAISS hit(s) for query: {args.query!r}")
    for i, h in enumerate(hits, 1):
        preview = h.chunk.text.strip().replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:117] + "..."
        print(
            f"  {i:>2}. score={h.score:.4f}  route={h.chunk.route}  "
            f"chunk#{h.chunk.index}\n      {preview}"
        )
    return 0


def load_main(argv: Sequence[str] | None = None) -> int:
    args = _build_load_parser().parse_args(argv)
    _configure_logging(args.log_level)
    try:
        return asyncio.run(_do_load(args))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) < 2 or sys.argv[1] not in {"rebuild", "load"}:
        print("Usage: python -m utility_mcp_server.rag.cli {rebuild|load} [args...]")
        raise SystemExit(2)
    cmd, rest = sys.argv[1], sys.argv[2:]
    raise SystemExit(rebuild_main(rest) if cmd == "rebuild" else load_main(rest))
