"""Embed chunks via AWS Bedrock Titan (RAG pipeline stage 2).

Sends each :class:`Chunk` text through the Bedrock Titan embedding model
(``amazon.titan-embed-text-v2:0`` by default) and returns dense float
vectors, plus an in-memory store with similarity search.

Bedrock invocation uses the bearer-token auth mode (``BEDROCK_API_KEY``)
against::

    POST https://bedrock-runtime.<region>.amazonaws.com/model/<model>/invoke

Usage::

    python -m utility_mcp_server.rag.embed
    python -m utility_mcp_server.rag.embed --query "how do I init the SDK?"
    python -m utility_mcp_server.rag.embed --save data/embeddings.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import httpx
import numpy as np

try:
    import faiss  # type: ignore
except ImportError as _faiss_exc:  # pragma: no cover - faiss is required at runtime
    faiss = None  # type: ignore
    _FAISS_IMPORT_ERROR = _faiss_exc
else:
    _FAISS_IMPORT_ERROR = None

from ..config import Settings, get_settings
from .chunk import Chunk, chunk_documents

logger = logging.getLogger(__name__)


DEFAULT_EMBED_DIMENSIONS = 1024  # Titan v2 supports 256 / 512 / 1024
DEFAULT_CONCURRENCY = 4
DEFAULT_TIMEOUT = 30.0

# Process-wide singleton embedder. Reusing the underlying httpx.AsyncClient
# keeps the TLS connection to Bedrock warm across requests and avoids the
# ~100–300 ms handshake cost on every query.
_titan_singleton: "BedrockTitanEmbedder | None" = None


def get_titan_embedder(
    *,
    api_key: str,
    region: str,
    model: str,
    dimensions: int = DEFAULT_EMBED_DIMENSIONS,
    timeout: float = DEFAULT_TIMEOUT,
) -> "BedrockTitanEmbedder":
    """Return a process-wide cached Titan embedder.

    A new instance is created only if the (model, region, dimensions) tuple
    changes, which should never happen at runtime.
    """
    global _titan_singleton
    if (
        _titan_singleton is None
        or _titan_singleton.model != model
        or _titan_singleton._region != region
        or _titan_singleton.dimensions != dimensions
    ):
        _titan_singleton = BedrockTitanEmbedder(
            api_key=api_key,
            region=region,
            model=model,
            dimensions=dimensions,
            timeout=timeout,
        )
    return _titan_singleton


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass
class EmbeddedChunk:
    """A :class:`Chunk` paired with its dense embedding vector."""

    chunk: Chunk
    embedding: list[float]
    model: str
    dimensions: int

    def to_dict(self) -> dict:
        return {
            "id": self.chunk.id,
            "route": self.chunk.route,
            "source_path": self.chunk.source_path,
            "index": self.chunk.index,
            "text": self.chunk.text,
            "metadata": dict(self.chunk.metadata),
            "model": self.model,
            "dimensions": self.dimensions,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmbeddedChunk":
        chunk = Chunk(
            id=data["id"],
            text=data["text"],
            route=data["route"],
            source_path=data["source_path"],
            index=int(data["index"]),
            metadata=dict(data.get("metadata") or {}),
        )
        return cls(
            chunk=chunk,
            embedding=list(data["embedding"]),
            model=data["model"],
            dimensions=int(data["dimensions"]),
        )


# ---------------------------------------------------------------------------
# Bedrock client
# ---------------------------------------------------------------------------
class BedrockEmbeddingError(RuntimeError):
    """Raised when the Bedrock embeddings API returns an error."""


class BedrockTitanEmbedder:
    """Async client for Bedrock Titan text embeddings (bearer-token auth)."""

    def __init__(
        self,
        *,
        api_key: str,
        region: str,
        model: str,
        dimensions: int = DEFAULT_EMBED_DIMENSIONS,
        timeout: float = DEFAULT_TIMEOUT,
        normalize: bool = True,
    ) -> None:
        if not api_key:
            raise ValueError(
                "BEDROCK_API_KEY is empty. Set it in your environment / .env."
            )
        self._api_key = api_key
        self._region = region
        self._model = model
        self._dimensions = dimensions
        self._normalize = normalize
        self._url = (
            f"https://bedrock-runtime.{region}.amazonaws.com"
            f"/model/{model}/invoke"
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

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def aclose(self) -> None:
        await self._client.aclose()

    async def embed_one(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text.")
        payload = {
            "inputText": text,
            "dimensions": self._dimensions,
            "normalize": self._normalize,
        }
        try:
            resp = await self._client.post(self._url, json=payload)
        except httpx.HTTPError as exc:
            raise BedrockEmbeddingError(f"Network error calling Bedrock: {exc}") from exc

        if resp.status_code >= 400:
            raise BedrockEmbeddingError(
                f"Bedrock embed failed ({resp.status_code}): {resp.text[:500]}"
            )
        try:
            body = resp.json()
        except ValueError as exc:
            raise BedrockEmbeddingError(
                f"Bedrock returned non-JSON body: {resp.text[:200]}"
            ) from exc

        embedding = body.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise BedrockEmbeddingError(
                f"Bedrock response missing 'embedding': {body!r}"
            )
        return [float(x) for x in embedding]

    async def embed_many(
        self,
        texts: Sequence[str],
        *,
        concurrency: int = DEFAULT_CONCURRENCY,
    ) -> list[list[float]]:
        sem = asyncio.Semaphore(max(1, concurrency))

        async def _bounded(t: str) -> list[float]:
            async with sem:
                return await self.embed_one(t)

        return await asyncio.gather(*(_bounded(t) for t in texts))


# ---------------------------------------------------------------------------
# In-memory vector store
# ---------------------------------------------------------------------------
@dataclass
class SearchHit:
    """A single similarity-search result."""

    chunk: Chunk
    score: float


@dataclass
class VectorStore:
    """In-memory vector store backed by a FAISS ``IndexFlatIP`` index.

    Titan v2 embeddings are L2-normalized by default, so inner-product
    similarity over normalized vectors is equivalent to cosine similarity.
    The FAISS index is built lazily on the first :meth:`search` call (and
    invalidated on every :meth:`add` / :meth:`extend`).
    """

    items: list[EmbeddedChunk] = field(default_factory=list)
    _index: Any = field(default=None, init=False, repr=False)
    _index_size: int = field(default=0, init=False, repr=False)

    def add(self, item: EmbeddedChunk) -> None:
        self.items.append(item)
        self._index = None

    def extend(self, items: Iterable[EmbeddedChunk]) -> None:
        self.items.extend(items)
        self._index = None

    def __len__(self) -> int:
        return len(self.items)

    def _ensure_index(self) -> Any:
        if not self.items:
            return None
        if self._index is not None and self._index_size == len(self.items):
            return self._index
        if faiss is None:  # pragma: no cover - defensive
            raise RuntimeError(
                "faiss is not installed. Install it with `pip install faiss-cpu`."
            ) from _FAISS_IMPORT_ERROR

        dim = self.items[0].dimensions
        matrix = np.asarray(
            [item.embedding for item in self.items], dtype="float32"
        )
        if matrix.shape[1] != dim:
            raise ValueError(
                f"Embedding dim mismatch: expected {dim}, got {matrix.shape[1]}"
            )
        index = faiss.IndexFlatIP(dim)
        index.add(matrix)
        self._index = index
        self._index_size = len(self.items)
        logger.info("Built FAISS IndexFlatIP (n=%d, dim=%d)", index.ntotal, dim)
        return index

    def search(self, query_embedding: Sequence[float], top_k: int = 5) -> list[SearchHit]:
        index = self._ensure_index()
        if index is None:
            return []
        k = max(1, min(int(top_k), len(self.items)))
        query = np.asarray([list(query_embedding)], dtype="float32")
        if query.shape[1] != self.items[0].dimensions:
            raise ValueError(
                f"Vector dim mismatch: {query.shape[1]} vs "
                f"{self.items[0].dimensions}"
            )
        scores, idxs = index.search(query, k)
        hits: list[SearchHit] = []
        for score, i in zip(scores[0].tolist(), idxs[0].tolist()):
            if i < 0:
                continue
            hits.append(SearchHit(chunk=self.items[i].chunk, score=float(score)))
        return hits

    # -- persistence ----------------------------------------------------
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [item.to_dict() for item in self.items]
        path.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: Path) -> "VectorStore":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(items=[EmbeddedChunk.from_dict(d) for d in data])


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Pure-Python cosine similarity (kept for tests / non-FAISS callers)."""
    if len(a) != len(b):
        raise ValueError(f"Vector dim mismatch: {len(a)} vs {len(b)}")
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# ---------------------------------------------------------------------------
# High-level pipeline
# ---------------------------------------------------------------------------
async def embed_chunks(
    chunks: Sequence[Chunk],
    *,
    embedder: BedrockTitanEmbedder,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> list[EmbeddedChunk]:
    if not chunks:
        return []
    logger.info(
        "Embedding %d chunk(s) with %s (dim=%d, concurrency=%d)",
        len(chunks),
        embedder.model,
        embedder.dimensions,
        concurrency,
    )
    vectors = await embedder.embed_many(
        [c.text for c in chunks], concurrency=concurrency
    )
    return [
        EmbeddedChunk(
            chunk=c,
            embedding=v,
            model=embedder.model,
            dimensions=embedder.dimensions,
        )
        for c, v in zip(chunks, vectors)
    ]


async def build_vector_store(
    settings: Settings | None = None,
    *,
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
    dimensions: int = DEFAULT_EMBED_DIMENSIONS,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> VectorStore:
    """End-to-end: read raw docs -> chunk -> embed -> in-memory store."""
    settings = settings or get_settings()
    chunks = chunk_documents(
        raw_docs_dir=settings.rag_raw_docs_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    embedder = BedrockTitanEmbedder(
        api_key=settings.bedrock_api_key,
        region=settings.bedrock_region,
        model=settings.bedrock_embedding_model,
        dimensions=dimensions,
    )
    try:
        embedded = await embed_chunks(chunks, embedder=embedder, concurrency=concurrency)
    finally:
        await embedder.aclose()

    store = VectorStore()
    store.extend(embedded)
    return store


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m utility_mcp_server.rag.embed",
        description=(
            "Embed chunked Pine Labs docs with Bedrock Titan and "
            "(optionally) run a similarity-search query (RAG stage 3)."
        ),
    )
    parser.add_argument("--chunk-size", type=int, default=1024)
    parser.add_argument("--overlap", dest="chunk_overlap", type=int, default=128)
    parser.add_argument(
        "--dimensions",
        type=int,
        default=DEFAULT_EMBED_DIMENSIONS,
        help=f"Embedding dimensions (default: {DEFAULT_EMBED_DIMENSIONS}).",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Max concurrent Bedrock requests (default: {DEFAULT_CONCURRENCY}).",
    )
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Persist the in-memory vector store as JSON to this path.",
    )
    parser.add_argument(
        "--load",
        type=Path,
        default=None,
        help="Load a previously saved vector store JSON instead of re-embedding.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional query text — runs FAISS similarity search over the store.",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--log-level", default="INFO")
    return parser


async def _amain(args) -> int:
    settings = get_settings()

    if args.load:
        store = VectorStore.load(args.load)
        logger.info("Loaded %d embedded chunk(s) from %s", len(store), args.load)
    else:
        store = await build_vector_store(
            settings,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            dimensions=args.dimensions,
            concurrency=args.concurrency,
        )

    if not store.items:
        print("No chunks were embedded \u2014 is the docs directory populated?")
        return 1

    sample = store.items[0]
    print(
        f"\nEmbedded {len(store)} chunk(s) "
        f"(model={sample.model}, dim={sample.dimensions})"
    )
    by_route: dict[str, int] = {}
    for item in store.items:
        by_route[item.chunk.route] = by_route.get(item.chunk.route, 0) + 1
    for route, n in sorted(by_route.items()):
        print(f"  - {route}: {n} vector(s)")

    if args.save:
        store.save(args.save)
        print(f"\nSaved vector store -> {args.save}")

    if args.query:
        embedder = BedrockTitanEmbedder(
            api_key=settings.bedrock_api_key,
            region=settings.bedrock_region,
            model=settings.bedrock_embedding_model,
            dimensions=sample.dimensions,
        )
        try:
            qvec = await embedder.embed_one(args.query)
        finally:
            await embedder.aclose()
        hits = store.search(qvec, top_k=args.top_k)
        print(f"\nTop {len(hits)} result(s) for: {args.query!r}")
        for rank, hit in enumerate(hits, 1):
            preview = hit.chunk.text[:140].replace("\n", " ")
            print(
                f"  {rank}. [{hit.chunk.id}] score={hit.score:.4f}\n"
                f"     {preview}{'...' if len(hit.chunk.text) > 140 else ''}"
            )

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
