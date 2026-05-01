"""Stage 4 of the RAG pipeline: ground a user question in retrieved chunks
and generate an answer with Bedrock Claude (Converse API).

Flow:

    question
      -> embed (Titan)
        -> similarity search over VectorStore (top-k)
          -> build grounded prompt with citations
            -> Bedrock Claude /converse
              -> answer + sources

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

import httpx

from ..config import Settings, get_settings
from .embed import (
    BedrockEmbeddingError,
    BedrockTitanEmbedder,
    SearchHit,
    VectorStore,
    build_vector_store,
    get_titan_embedder,
)

logger = logging.getLogger(__name__)


DEFAULT_TOP_K = 4
# Grounded RAG answers over 4 chunks rarely need more than a few hundred
# tokens. Bedrock generation latency scales roughly linearly with the
# number of tokens actually produced, so keep this tight. Override per
# call via the `max_tokens` argument if a user explicitly asks for a
# long-form answer.
DEFAULT_MAX_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT = 60.0

# Bounded answer cache. Identical (question, top_k) pairs return
# instantly without hitting Bedrock at all. Capped to prevent unbounded
# memory growth in long-running processes.
_ANSWER_CACHE_MAX = 128
_answer_cache: "OrderedDict[tuple[str, int], GenerationResult]" = OrderedDict()


def clear_answer_cache() -> None:
    """Drop all cached answers (used in tests and after reindex)."""
    _answer_cache.clear()


SYSTEM_PROMPT = (
    "You are the Pine Labs SDK documentation assistant.\n"
    "\n"
    "STRICT RULES — you MUST follow these:\n"
    "1. Answer ONLY using the CONTEXT chunks provided in the user message. "
    "Do NOT use prior knowledge, do NOT invent identifiers, parameters, "
    "return types, error variants, or code samples that are not present "
    "in the context.\n"
    "2. If the context does not contain the answer, reply exactly: "
    "\"This is not documented in the Pine Labs SDK docs I have access to.\"\n"
    "3. Quote identifiers (function names, parameter names, types, error "
    "variants) verbatim from the context.\n"
    "4. When you use a chunk, cite it inline using its bracketed source "
    "id, e.g. [api/init#0]. Place citations at the end of the sentence "
    "they support.\n"
    "5. Never produce code in a programming language that is not shown in "
    "the context's code examples.\n"
    "6. Be concise and factual. Prefer bullet points for parameter lists.\n"
    "\n"
    "DOCUMENT vs PROSE — IMPORTANT:\n"
    "Each chunk id has the form '<route>#<index>'. The route identifies\n"
    "the source DOCUMENT (e.g. 'api/init', 'concepts/getting-started').\n"
    "When the user asks to list available DOCUMENTS, list ONLY the "
    "distinct routes from the CONTEXT — never invent new routes and "
    "never list identifiers (like function names) as documents.\n"
    "Identifiers that appear only inside prose / sample code in a "
    "'concepts/*' chunk are background mentions; do NOT present them as "
    "first-class documented APIs unless an 'api/*' chunk also defines "
    "them."
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass
class GenerationResult:
    """Final RAG answer plus retrieval metadata."""

    question: str
    answer: str
    sources: list[SearchHit] = field(default_factory=list)
    model: str = ""
    stop_reason: str | None = None
    usage: dict | None = None

    def format_sources(self) -> str:
        if not self.sources:
            return "(no sources)"
        return "\n".join(
            f"  [{h.chunk.id}] score={h.score:.4f}  ({h.chunk.source_path})"
            for h in self.sources
        )


# ---------------------------------------------------------------------------
# Bedrock Claude (Converse API) client
# ---------------------------------------------------------------------------
class BedrockClaudeError(RuntimeError):
    """Raised when the Bedrock Converse API returns an error."""


class BedrockClaudeClient:
    """Async client for Bedrock Claude via the Converse API (bearer auth)."""

    def __init__(
        self,
        *,
        api_key: str,
        region: str,
        model: str,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            raise ValueError("BEDROCK_API_KEY is empty.")
        self._model = model
        self._url = (
            f"https://bedrock-runtime.{region}.amazonaws.com"
            f"/model/{model}/converse"
        )
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    @property
    def model(self) -> str:
        return self._model

    async def aclose(self) -> None:
        await self._client.aclose()

    async def converse(
        self,
        *,
        system_prompt: str,
        user_message: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> dict:
        payload = {
            "system": [{"text": system_prompt}],
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": user_message}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
            },
        }
        try:
            resp = await self._client.post(self._url, json=payload)
        except httpx.HTTPError as exc:
            raise BedrockClaudeError(f"Network error calling Bedrock: {exc}") from exc

        if resp.status_code >= 400:
            raise BedrockClaudeError(
                f"Bedrock converse failed ({resp.status_code}): {resp.text[:1000]}"
            )
        try:
            return resp.json()
        except ValueError as exc:
            raise BedrockClaudeError(
                f"Bedrock returned non-JSON body: {resp.text[:200]}"
            ) from exc


def _extract_text(converse_response: dict) -> str:
    """Pull the assistant text out of a Bedrock Converse API response."""
    output = converse_response.get("output") or {}
    message = output.get("message") or {}
    parts = message.get("content") or []
    chunks = [p.get("text", "") for p in parts if isinstance(p, dict) and "text" in p]
    return "".join(chunks).strip()


# Process-wide singleton Claude client. Reusing the underlying
# httpx.AsyncClient keeps the TLS connection to Bedrock warm across
# requests and avoids the handshake cost on every query.
_claude_singleton: BedrockClaudeClient | None = None


def get_claude_client(
    *,
    api_key: str,
    region: str,
    model: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> BedrockClaudeClient:
    """Return a process-wide cached Claude Converse client."""
    global _claude_singleton
    if (
        _claude_singleton is None
        or _claude_singleton.model != model
        or _claude_singleton._url.split("//", 1)[1].split(".", 2)[1] != region
    ):
        _claude_singleton = BedrockClaudeClient(
            api_key=api_key,
            region=region,
            model=model,
            timeout=timeout,
        )
    return _claude_singleton


# ---------------------------------------------------------------------------
# Prompt assembly
# ---------------------------------------------------------------------------
def build_grounded_prompt(question: str, hits: Sequence[SearchHit]) -> str:
    """Render retrieved chunks as a grounded prompt for Claude."""
    if not hits:
        return (
            f"QUESTION:\n{question}\n\n"
            "CONTEXT:\n(no relevant context was retrieved)\n"
        )

    blocks = []
    for hit in hits:
        blocks.append(
            f"--- BEGIN CHUNK [{hit.chunk.id}]"
            f" (route={hit.chunk.route}, score={hit.score:.4f}) ---\n"
            f"{hit.chunk.text}\n"
            f"--- END CHUNK [{hit.chunk.id}] ---"
        )
    context = "\n\n".join(blocks)
    return (
        f"QUESTION:\n{question}\n\n"
        "CONTEXT (authoritative; cite by [id]):\n"
        f"{context}\n\n"
        "Answer the QUESTION using ONLY the CONTEXT above. "
        "Cite chunks inline as [id]."
    )


# ---------------------------------------------------------------------------
# High-level pipeline
# ---------------------------------------------------------------------------
async def answer_question(
    question: str,
    *,
    store: VectorStore,
    settings: Settings | None = None,
    top_k: int = DEFAULT_TOP_K,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> GenerationResult:
    """Run a single grounded RAG query against ``store``."""
    if not question or not question.strip():
        raise ValueError("question must be a non-empty string")
    if not store.items:
        raise ValueError("VectorStore is empty — embed chunks first.")

    # Cache hit: identical question + top_k returns the previous answer
    # immediately without calling Bedrock at all.
    cache_key = (question.strip(), int(top_k))
    cached = _answer_cache.get(cache_key)
    if cached is not None:
        _answer_cache.move_to_end(cache_key)
        logger.info("RAG cache hit for question=%r top_k=%d", cache_key[0][:80], top_k)
        return cached

    settings = settings or get_settings()
    sample = store.items[0]

    embedder = get_titan_embedder(
        api_key=settings.bedrock_api_key,
        region=settings.bedrock_region,
        model=sample.model,
        dimensions=sample.dimensions,
    )
    t0 = time.perf_counter()
    qvec = await embedder.embed_one(question)
    t_embed = time.perf_counter() - t0

    t0 = time.perf_counter()
    hits = store.search(qvec, top_k=top_k)
    prompt = build_grounded_prompt(question, hits)
    t_search = time.perf_counter() - t0

    claude = get_claude_client(
        api_key=settings.bedrock_api_key,
        region=settings.bedrock_region,
        model=settings.bedrock_model,
    )
    t0 = time.perf_counter()
    response = await claude.converse(
        system_prompt=SYSTEM_PROMPT,
        user_message=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    t_gen = time.perf_counter() - t0

    usage = response.get("usage") or {}
    logger.info(
        "RAG timing: embed=%.0fms search=%.0fms generate=%.0fms "
        "(in=%s out=%s tokens, model=%s)",
        t_embed * 1000,
        t_search * 1000,
        t_gen * 1000,
        usage.get("inputTokens"),
        usage.get("outputTokens"),
        claude.model,
    )

    result = GenerationResult(
        question=question,
        answer=_extract_text(response),
        sources=hits,
        model=claude.model,
        stop_reason=response.get("stopReason"),
        usage=response.get("usage"),
    )

    # Populate the cache and evict oldest entries if we're over capacity.
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
            "Answer a question grounded in the embedded Pine Labs docs "
            "(RAG pipeline stage 4: retrieval + Claude generation)."
        ),
    )
    parser.add_argument("--question", required=True, help="The user question.")
    parser.add_argument(
        "--load",
        type=Path,
        default=None,
        help="Path to a saved vector store (data/embeddings.json). "
        "If omitted, the store is rebuilt from scratch.",
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--log-level", default="INFO")
    return parser


async def _amain(args) -> int:
    settings = get_settings()

    if args.load and args.load.exists():
        store = VectorStore.load(args.load)
        logger.info("Loaded %d embedded chunk(s) from %s", len(store), args.load)
    else:
        if args.load:
            logger.warning("--load path not found, rebuilding store: %s", args.load)
        store = await build_vector_store(settings)

    if not store.items:
        print("Vector store is empty — run stages 1-3 first.")
        return 1

    result = await answer_question(
        args.question,
        store=store,
        settings=settings,
        top_k=args.top_k,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    print("\n=== ANSWER ===")
    print(result.answer or "(empty)")
    print("\n=== SOURCES ===")
    print(result.format_sources())
    print(f"\nmodel={result.model}  stop_reason={result.stop_reason}")
    if result.usage:
        print(f"usage={result.usage}")
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
