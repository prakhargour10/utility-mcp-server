"""Stage 2 of the RAG pipeline: chunk raw markdown docs into nodes.

Reads every ``.md`` file under the raw-docs directory written by
:mod:`utility_mcp_server.rag.ingest` and splits them into overlapping
sentence-aware chunks using LlamaIndex's :class:`SentenceSplitter`.

The output is a list of :class:`Chunk` objects, each carrying:

* the chunk text
* metadata identifying the source route + file path
* a deterministic chunk id (``"<route>#<index>"``)

Usage::

    python -m utility_mcp_server.rag.chunk
    python -m utility_mcp_server.rag.chunk --chunk-size 800 --overlap 100
    python -m utility_mcp_server.rag.chunk --json out.json
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


DEFAULT_CHUNK_SIZE = 1024
DEFAULT_CHUNK_OVERLAP = 128


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Chunk:
    """A single chunk produced from a source markdown document."""

    id: str
    text: str
    route: str
    source_path: str
    index: int
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
def _discover_markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def _path_to_route(path: Path, root: Path) -> str:
    """Convert ``data/raw_docs/api/init.md`` -> ``api/init``."""
    rel = path.relative_to(root).with_suffix("")
    return rel.as_posix()


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def _build_splitter(chunk_size: int, chunk_overlap: int):
    """Lazily import LlamaIndex so it's only required when chunking is used."""
    try:
        from llama_index.core.node_parser import SentenceSplitter
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "LlamaIndex is required for chunking. Install it with:\n"
            "    pip install llama-index-core"
        ) from exc

    return SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        paragraph_separator="\n\n",
    )


def chunk_documents(
    *,
    raw_docs_dir: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Chunk every ``.md`` file under ``raw_docs_dir`` into :class:`Chunk` items.

    Args:
        raw_docs_dir: Directory containing the markdown produced by stage 1.
        chunk_size: Target chunk size in tokens (LlamaIndex default tokenizer).
        chunk_overlap: Token overlap between consecutive chunks.

    Returns:
        Flat list of :class:`Chunk` objects in stable (route, index) order.
    """
    files = _discover_markdown_files(raw_docs_dir)
    if not files:
        logger.warning("No markdown files found under %s", raw_docs_dir)
        return []

    splitter = _build_splitter(chunk_size, chunk_overlap)
    chunks: list[Chunk] = []

    for path in files:
        route = _path_to_route(path, raw_docs_dir)
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            logger.warning("Empty file skipped: %s", path)
            continue

        pieces = splitter.split_text(text)
        logger.info("chunked: %s -> %d chunk(s)", route, len(pieces))

        for i, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    id=f"{route}#{i}",
                    text=piece,
                    route=route,
                    source_path=str(path),
                    index=i,
                    metadata={
                        "route": route,
                        "source_path": str(path),
                        "chunk_index": i,
                        "chunk_count": len(pieces),
                    },
                )
            )

    logger.info(
        "Produced %d chunk(s) from %d file(s) (size=%d, overlap=%d)",
        len(chunks),
        len(files),
        chunk_size,
        chunk_overlap,
    )
    return chunks


def chunks_to_llama_nodes(chunks: Iterable[Chunk]) -> list[Any]:
    """Convert :class:`Chunk` items to LlamaIndex ``TextNode`` objects.

    Useful when feeding chunks directly into a LlamaIndex embedding /
    vector-store pipeline downstream.
    """
    from llama_index.core.schema import TextNode

    return [
        TextNode(id_=c.id, text=c.text, metadata=dict(c.metadata)) for c in chunks
    ]


def chunk_documents_from_settings(
    settings: Settings | None = None,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Convenience wrapper that resolves the raw-docs dir from settings."""
    settings = settings or get_settings()
    return chunk_documents(
        raw_docs_dir=settings.rag_raw_docs_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m utility_mcp_server.rag.chunk",
        description=(
            "Chunk ingested raw markdown docs into sentence-aware nodes "
            "(RAG pipeline stage 2)."
        ),
    )
    parser.add_argument(
        "--raw-docs-dir",
        type=Path,
        default=None,
        help="Override the input directory (default: RAG_RAW_DOCS_DIR).",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Target chunk size in tokens (default: {DEFAULT_CHUNK_SIZE}).",
    )
    parser.add_argument(
        "--overlap",
        dest="chunk_overlap",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help=f"Token overlap between chunks (default: {DEFAULT_CHUNK_OVERLAP}).",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Optional path to dump all chunks as a JSON array.",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=120,
        help="Characters of each chunk to print in the summary (default: 120).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python log level (default: INFO).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    settings = get_settings()
    raw_dir = args.raw_docs_dir or settings.rag_raw_docs_dir

    if not raw_dir.exists():
        logger.error(
            "Raw-docs directory does not exist: %s\n"
            "Run stage 1 first: python -m utility_mcp_server.rag.ingest",
            raw_dir,
        )
        return 2

    chunks = chunk_documents(
        raw_docs_dir=raw_dir,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    if not chunks:
        print(f"No chunks produced from {raw_dir}.")
        return 1

    print()
    print(
        f"Produced {len(chunks)} chunk(s) "
        f"(chunk_size={args.chunk_size}, overlap={args.chunk_overlap}) "
        f"from {raw_dir}"
    )
    by_route: dict[str, int] = {}
    for c in chunks:
        by_route[c.route] = by_route.get(c.route, 0) + 1
    for route, n in sorted(by_route.items()):
        print(f"  - {route}: {n} chunk(s)")

    preview = max(0, args.preview)
    if preview:
        print("\nFirst chunk preview:")
        head = chunks[0]
        snippet = head.text[:preview].replace("\n", " ")
        print(f"  [{head.id}] {snippet}{'...' if len(head.text) > preview else ''}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(c) for c in chunks]
        args.json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nWrote {len(chunks)} chunk(s) to {args.json}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
