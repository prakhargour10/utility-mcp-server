"""Top-level CLI commands for managing the RAG vector database.

Two entrypoints are exposed via ``pyproject.toml`` ``[project.scripts]``:

* ``rag-rebuild`` — Run the full pipeline from scratch:
  ingest raw markdown → chunk → embed via Bedrock Titan → save
  ``embeddings.json``. Use this whenever the docs change or the
  embedding model / dimensions change.

* ``rag-load`` — Load the existing ``embeddings.json`` into memory and
  report its size. Use this to verify that a prebuilt vector store is
  available without spending Bedrock calls. Optionally runs a similarity
  search via ``--query`` to smoke-test retrieval.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import shutil
import sys
from pathlib import Path
from typing import Sequence

from ..config import Settings, get_settings
from .embed import (
    BedrockTitanEmbedder,
    DEFAULT_CONCURRENCY,
    DEFAULT_EMBED_DIMENSIONS,
    VectorStore,
    build_vector_store,
)
from .ingest import fetch_all_docs

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _embeddings_path(settings: Settings) -> Path:
    return settings.rag_raw_docs_dir.parent / "embeddings.json"


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
            "Rebuild the RAG vector database from scratch: ingest raw docs, "
            "chunk, embed via Bedrock Titan, and persist to embeddings.json."
        ),
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Reuse existing raw markdown on disk; do not re-fetch from the docs site.",
    )
    parser.add_argument(
        "--keep-raw",
        action="store_true",
        help="Do not delete existing raw_docs before re-ingesting (default: wipe).",
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
        "--dimensions", type=int, default=DEFAULT_EMBED_DIMENSIONS,
        help=f"Embedding dimensions (default: {DEFAULT_EMBED_DIMENSIONS}).",
    )
    parser.add_argument(
        "--concurrency", type=int, default=DEFAULT_CONCURRENCY,
        help=f"Max concurrent Bedrock requests (default: {DEFAULT_CONCURRENCY}).",
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
    raw_dir = settings.rag_raw_docs_dir
    out_path = args.output or _embeddings_path(settings)

    # 1. Wipe + re-ingest raw markdown (unless skipped)
    if not args.skip_ingest:
        if raw_dir.exists() and not args.keep_raw:
            logger.info("Wiping existing raw_docs at %s", raw_dir)
            shutil.rmtree(raw_dir)
        raw_dir.mkdir(parents=True, exist_ok=True)

        routes = list(settings.rag_doc_routes)
        if not routes:
            logger.error(
                "No routes configured. Set RAG_DOC_ROUTES or update config."
            )
            return 2
        logger.info(
            "Ingesting %d route(s) from %s", len(routes), settings.docs_base_url
        )
        report = await fetch_all_docs(
            routes=routes,
            base_url=settings.docs_base_url,
            output_dir=raw_dir,
            force=True,
        )
        if report.failures:
            for f in report.failures:
                logger.error("ingest failure: %s -> %s (%s)", f.route, f.url, f.error)
            logger.error(
                "%d ingest failure(s); aborting rebuild.", len(report.failures)
            )
            return 1
        logger.info("Ingested %d document(s).", len(report.docs))
    else:
        logger.info("--skip-ingest set; reusing raw docs at %s", raw_dir)

    # 2. Drop any stale embeddings file
    if out_path.exists():
        logger.info("Removing stale embeddings file %s", out_path)
        out_path.unlink()

    # 3. Chunk + embed + build the in-memory store
    store = await build_vector_store(
        settings,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        dimensions=args.dimensions,
        concurrency=args.concurrency,
    )

    # 4. Persist
    store.save(out_path)
    logger.info("Saved %d embedded chunk(s) to %s", len(store), out_path)
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

    embedder = BedrockTitanEmbedder(
        api_key=settings.bedrock_api_key,
        region=settings.bedrock_region,
        model=settings.bedrock_embedding_model,
        dimensions=store.items[0].dimensions if store.items else DEFAULT_EMBED_DIMENSIONS,
    )
    try:
        [vec] = await embedder.embed_many([args.query], concurrency=1)
    finally:
        await embedder.aclose()

    hits = store.search(vec, top_k=args.top_k)
    print(f"\nTop {len(hits)} hit(s) for query: {args.query!r}")
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
    # Allow `python -m utility_mcp_server.rag.cli rebuild|load ...`
    if len(sys.argv) < 2 or sys.argv[1] not in {"rebuild", "load"}:
        print("Usage: python -m utility_mcp_server.rag.cli {rebuild|load} [args...]")
        raise SystemExit(2)
    cmd, rest = sys.argv[1], sys.argv[2:]
    raise SystemExit(rebuild_main(rest) if cmd == "rebuild" else load_main(rest))
