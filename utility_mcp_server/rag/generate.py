"""Final stage of the RAG pipeline: FAISS dense-vector retrieval.

There is no LLM call. The "answer" returned to the caller is the
concatenation of the top-k retrieved chunks, prefixed with their
``[route#index]`` ids so downstream callers can cite them.

Flow:

    question
      -> local sentence-transformers embedding
        -> FAISS IndexFlatIP top-k search over VectorStore
          -> stitched answer (chunk text + citations)

Usage::

    python -m utility_mcp_server.rag.generate \\
        --load data/embeddings.json \\
        --question "How do I initialize the Pine Labs SDK?"
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from ..config import Settings, get_settings
from .embed import (
    SearchHit,
    VectorStore,
    build_vector_store,
)

logger = logging.getLogger(__name__)


DEFAULT_TOP_K = 25
RETRIEVER_NAME = "faiss"

# Bounded answer cache. Identical (question, top_k) pairs return the
# previous result without re-running BM25. Capped to prevent unbounded
# memory growth in long-running processes.
_ANSWER_CACHE_MAX = 128
_answer_cache: "OrderedDict[tuple[str, int], GenerationResult]" = OrderedDict()


def clear_answer_cache() -> None:
    """Drop all cached answers (used in tests and after reindex)."""
    _answer_cache.clear()


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass
class GenerationResult:
    """Final RAG answer plus retrieval metadata.

    The shape is preserved from the previous LLM-backed implementation
    so existing callers (tools.py, CLIs) keep working unchanged. With
    FAISS-only retrieval, ``answer`` is a deterministic stitching of the
    retrieved chunks rather than an LLM-synthesized prose answer.
    """

    question: str
    answer: str
    sources: list[SearchHit] = field(default_factory=list)
    model: str = RETRIEVER_NAME
    stop_reason: str | None = None
    usage: dict | None = None

    def format_sources(self) -> str:
        if not self.sources:
            return "(no sources)"
        return "\n".join(
            f"  [{h.chunk.id}] score={h.score:.4f}  ({h.chunk.source_path})"
            for h in self.sources
        )


# Kept as a module-level symbol because external code may import it.
class BedrockClaudeError(RuntimeError):
    """Deprecated. Retained as an importable symbol for back-compat.

    The pipeline runs fully locally and never calls Bedrock, so this
    exception is never raised internally. Callers can stop catching it.
    """


# ---------------------------------------------------------------------------
# Answer assembly
# ---------------------------------------------------------------------------
def build_answer(question: str, hits: Sequence[SearchHit]) -> str:
    """Render retrieved chunks as a deterministic answer block."""
    if not hits:
        return (
            "No relevant content was found in the Pine Labs SDK docs for "
            f"the question: {question!r}."
        )

    blocks: list[str] = []
    for hit in hits:
        blocks.append(
            f"--- [{hit.chunk.id}] (route={hit.chunk.route}, "
            f"score={hit.score:.4f}) ---\n{hit.chunk.text}"
        )
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# High-level pipeline
# ---------------------------------------------------------------------------
async def answer_question(
    question: str,
    *,
    store: VectorStore,
    settings: Settings | None = None,
    top_k: int = DEFAULT_TOP_K,
    **_unused: object,
) -> GenerationResult:
    """Run a single BM25 retrieval against ``store`` and return the top-k.

    Extra keyword arguments (``max_tokens``, ``temperature``, ...) are
    silently ignored to preserve the previous LLM-era call signature.
    """
    if not question or not question.strip():
        raise ValueError("question must be a non-empty string")
    if not store.items:
        raise ValueError("VectorStore is empty — run rag-rebuild first.")

    cache_key = (question.strip(), int(top_k))
    cached = _answer_cache.get(cache_key)
    if cached is not None:
        _answer_cache.move_to_end(cache_key)
        logger.info("RAG cache hit for question=%r top_k=%d", cache_key[0][:80], top_k)
        return cached

    t0 = time.perf_counter()
    hits = await store.search(question, top_k=top_k)
    answer_text = build_answer(question, hits)
    t_search = time.perf_counter() - t0

    logger.info(
        "RAG timing: search=%.0fms hits=%d (retriever=%s)",
        t_search * 1000,
        len(hits),
        RETRIEVER_NAME,
    )

    result = GenerationResult(
        question=question,
        answer=answer_text,
        sources=hits,
        model=RETRIEVER_NAME,
        stop_reason="faiss_top_k",
        usage=None,
    )

    _answer_cache[cache_key] = result
    while len(_answer_cache) > _ANSWER_CACHE_MAX:
        _answer_cache.popitem(last=False)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m utility_mcp_server.rag.generate",
        description=(
            "Answer a question grounded in the Pine Labs docs using "
            "FAISS dense-vector retrieval (no LLM)."
        ),
    )
    parser.add_argument("--question", required=True, help="The user question.")
    parser.add_argument(
        "--load",
        type=Path,
        default=None,
        help="Path to a saved chunk store (data/embeddings.json). "
        "If omitted, the store is rebuilt from scratch.",
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--log-level", default="INFO")
    return parser


async def _amain(args) -> int:
    settings = get_settings()

    if args.load and args.load.exists():
        store = VectorStore.load(args.load)
        logger.info("Loaded %d chunk(s) from %s", len(store), args.load)
    else:
        if args.load:
            logger.warning("--load path not found, rebuilding store: %s", args.load)
        store = await build_vector_store(settings)

    if not store.items:
        print("Chunk store is empty — run rag-rebuild first.")
        return 1

    result = await answer_question(
        args.question,
        store=store,
        settings=settings,
        top_k=args.top_k,
    )

    print("\n=== ANSWER ===")
    print(result.answer or "(empty)")
    print("\n=== SOURCES ===")
    print(result.format_sources())
    print(f"\nretriever={result.model}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return asyncio.run(_amain(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
