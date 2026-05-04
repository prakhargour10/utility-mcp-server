"""FAISS dense vector retrieval over the chunked Pine Labs docs corpus.

Embeddings are computed **locally** via
``sentence-transformers`` (default model:
``sentence-transformers/all-MiniLM-L6-v2``, 384-dim). No external API
calls, no API keys, no network egress at query time.

Pipeline:

    docs/doc_list/**/*.md
        -> SentenceSplitter chunking (chunk.py, LlamaIndex; ~1024 tokens)
            -> SentenceTransformer embeddings (float32[dim], L2-normalized)
                -> VectorStore (in-memory list[Chunk] + faiss.IndexFlatIP)
                    -> store.search(query, top_k)
                        -> tools.py / generate.py

Persistence: a JSON file at ``settings.rag_embeddings_path`` containing
chunk metadata plus the dense embedding vector for each chunk. The FAISS
index itself is rebuilt in-memory from these vectors on load -- this
keeps the on-disk artifact portable across FAISS versions / architectures.

Usage::

    python -m utility_mcp_server.rag.embed --save data/embeddings.json
    python -m utility_mcp_server.rag.embed --query "doTransaction" --top-k 5
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

try:
    import faiss  # type: ignore
except ImportError as _faiss_exc:  # pragma: no cover - faiss is required at runtime
    faiss = None  # type: ignore
    _FAISS_IMPORT_ERROR: Exception | None = _faiss_exc
else:
    _FAISS_IMPORT_ERROR = None

from ..config import Settings, get_settings
from .chunk import Chunk, chunk_documents

logger = logging.getLogger(__name__)


DEFAULT_EMBED_DIM = 384
DEFAULT_EMBED_BATCH = 32


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass
class SearchHit:
    """A single FAISS retrieval result.

    ``score`` is the inner product between the query and chunk vectors.
    Both are L2-normalized at embed time, so this is equivalent to
    cosine similarity in ``[-1, 1]``.
    """

    chunk: Chunk
    score: float


# ---------------------------------------------------------------------------
# Local sentence-transformers embedder
# ---------------------------------------------------------------------------
class LocalSentenceTransformerEmbedder:
    """Embedder backed by a local ``sentence-transformers`` model.

    The model is loaded lazily on first use and cached on the instance.
    ``encode`` runs in a worker thread (``asyncio.to_thread``) to keep the
    public ``async`` API surface unchanged from the previous remote
    implementation.
    """

    _model_cache: dict[str, Any] = {}

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        dimensions: int | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._model_name = self._settings.embedding_model
        # Dimensions are determined by the model itself; the optional
        # argument is accepted for back-compat but ignored unless it
        # matches the model's native dimension.
        self._requested_dim = int(dimensions) if dimensions is not None else None
        self._model: Any = None
        self._dimensions: int = 0

    @property
    def dimensions(self) -> int:
        if self._dimensions == 0:
            self._load_model()
        return self._dimensions

    @property
    def model(self) -> str:
        return self._model_name

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model
        cached = self._model_cache.get(self._model_name)
        if cached is None:
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional dep guard
                raise RuntimeError(
                    "sentence-transformers is not installed. "
                    "Install it with `pip install sentence-transformers`."
                ) from exc
            logger.info("Loading local embedding model: %s", self._model_name)
            cached = SentenceTransformer(self._model_name)
            self._model_cache[self._model_name] = cached
        self._model = cached
        # `get_embedding_dimension` is the v5+ name; fall back to the
        # deprecated `get_sentence_embedding_dimension` for older installs.
        get_dim = getattr(
            cached, "get_embedding_dimension", None
        ) or cached.get_sentence_embedding_dimension
        self._dimensions = int(get_dim())
        if (
            self._requested_dim is not None
            and self._requested_dim != self._dimensions
        ):
            logger.warning(
                "Requested embedding dim %d does not match model dim %d; "
                "using model dim.",
                self._requested_dim,
                self._dimensions,
            )
        return self._model

    def _encode_sync(self, texts: Sequence[str]) -> np.ndarray:
        model = self._load_model()
        arr = model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(arr, dtype=np.float32)

    async def embed_one(self, text: str, client: Any = None) -> np.ndarray:
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text.")
        arr = await asyncio.to_thread(self._encode_sync, [text])
        return arr[0]

    async def embed_many(
        self,
        texts: Sequence[str],
        *,
        batch_size: int = DEFAULT_EMBED_BATCH,
    ) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimensions), dtype=np.float32)

        batch_size = max(1, int(batch_size))
        out_chunks: list[np.ndarray] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            arr = await asyncio.to_thread(self._encode_sync, batch)
            out_chunks.append(arr)
            done = min(start + batch_size, len(texts))
            logger.info(
                "embedded %d/%d chunks (model=%s, dim=%d)",
                done,
                len(texts),
                self._model_name,
                self.dimensions,
            )
        return np.vstack(out_chunks).astype(np.float32, copy=False)


# Backwards-compat alias so any external import keeps working.
BedrockTitanEmbedder = LocalSentenceTransformerEmbedder


# ---------------------------------------------------------------------------
# Vector store (FAISS)
# ---------------------------------------------------------------------------
@dataclass
class VectorStore:
    """In-memory chunk store with a lazy FAISS ``IndexFlatIP`` index."""

    items: list[Chunk] = field(default_factory=list)
    vectors: np.ndarray = field(
        default_factory=lambda: np.zeros((0, DEFAULT_EMBED_DIM), dtype=np.float32)
    )
    dim: int = DEFAULT_EMBED_DIM
    _index: Any = field(default=None, init=False, repr=False)
    _index_size: int = field(default=0, init=False, repr=False)
    _embedder: LocalSentenceTransformerEmbedder | None = field(
        default=None, init=False, repr=False
    )

    # -- mutation -------------------------------------------------------
    def add(self, chunk: Chunk, vector: np.ndarray) -> None:
        v = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        if v.shape[1] != self.dim:
            raise ValueError(f"Vector dim {v.shape[1]} != store dim {self.dim}")
        self.items.append(chunk)
        self.vectors = (
            v if self.vectors.size == 0 else np.vstack([self.vectors, v])
        )
        self._index = None

    def extend(self, chunks: Sequence[Chunk], vectors: np.ndarray) -> None:
        vectors = np.asarray(vectors, dtype=np.float32)
        if len(chunks) != vectors.shape[0]:
            raise ValueError("chunks and vectors must have the same length")
        if vectors.shape[1] != self.dim:
            raise ValueError(
                f"Vector dim {vectors.shape[1]} != store dim {self.dim}"
            )
        self.items.extend(chunks)
        self.vectors = (
            vectors
            if self.vectors.size == 0
            else np.vstack([self.vectors, vectors])
        )
        self._index = None

    def __len__(self) -> int:
        return len(self.items)

    # -- FAISS ----------------------------------------------------------
    def _ensure_index(self) -> Any:
        if not self.items:
            return None
        if self._index is not None and self._index_size == len(self.items):
            return self._index
        if faiss is None:  # pragma: no cover - defensive
            raise RuntimeError(
                "faiss is not installed. Install it with `pip install faiss-cpu`."
            ) from _FAISS_IMPORT_ERROR
        index = faiss.IndexFlatIP(self.dim)
        index.add(np.ascontiguousarray(self.vectors, dtype=np.float32))
        self._index = index
        self._index_size = len(self.items)
        logger.info(
            "Built FAISS IndexFlatIP (n=%d, dim=%d)", len(self.items), self.dim
        )
        return index

    def _get_embedder(self) -> LocalSentenceTransformerEmbedder:
        if self._embedder is None:
            self._embedder = LocalSentenceTransformerEmbedder(dimensions=self.dim)
        return self._embedder

    async def embed_query(self, query_text: str) -> np.ndarray:
        embedder = self._get_embedder()
        return await embedder.embed_one(query_text)

    async def search(self, query_text: str, top_k: int = 5) -> list[SearchHit]:
        """Embed ``query_text`` and run FAISS top-k inner-product search."""
        index = self._ensure_index()
        if index is None:
            return []
        if not query_text or not query_text.strip():
            return []
        qvec = await self.embed_query(query_text)
        return self.search_by_vector(qvec, top_k=top_k)

    def search_by_vector(
        self, query_vec: np.ndarray, top_k: int = 5
    ) -> list[SearchHit]:
        index = self._ensure_index()
        if index is None:
            return []
        q = np.asarray(query_vec, dtype=np.float32).reshape(1, -1)
        if q.shape[1] != self.dim:
            raise ValueError(f"Query dim {q.shape[1]} != store dim {self.dim}")
        k = max(1, min(int(top_k), len(self.items)))
        scores, idxs = index.search(np.ascontiguousarray(q), k)
        hits: list[SearchHit] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx < 0:
                continue
            hits.append(SearchHit(chunk=self.items[int(idx)], score=float(score)))
        return hits

    # -- persistence ---------------------------------------------------
    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dim": int(self.dim),
            "items": [
                {
                    "id": c.id,
                    "route": c.route,
                    "source_path": c.source_path,
                    "index": c.index,
                    "text": c.text,
                    "metadata": dict(c.metadata),
                    "embedding": self.vectors[i].astype(np.float32).tolist(),
                }
                for i, c in enumerate(self.items)
            ],
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    @classmethod
    def load(cls, path: Path) -> "VectorStore":
        data = json.loads(path.read_text(encoding="utf-8"))

        # Tolerate the legacy BM25-only format (a flat list of chunk dicts
        # without embeddings). In that case we return an empty store so
        # the caller can detect it and trigger a rebuild.
        if isinstance(data, list):
            logger.warning(
                "Legacy chunk store detected at %s -- embeddings missing. "
                "Run `rag-rebuild` to regenerate the FAISS index.",
                path,
            )
            return cls(
                items=[],
                vectors=np.zeros((0, DEFAULT_EMBED_DIM), dtype=np.float32),
            )

        dim = int(data.get("dim", DEFAULT_EMBED_DIM))
        raw_items = data.get("items") or []
        items: list[Chunk] = []
        vectors: list[list[float]] = []
        for d in raw_items:
            emb = d.get("embedding")
            if not emb:
                logger.warning(
                    "Item %s in %s has no embedding -- treating store as empty.",
                    d.get("id"),
                    path,
                )
                return cls(
                    items=[],
                    vectors=np.zeros((0, dim), dtype=np.float32),
                    dim=dim,
                )
            items.append(
                Chunk(
                    id=d["id"],
                    text=d["text"],
                    route=d["route"],
                    source_path=d["source_path"],
                    index=int(d["index"]),
                    metadata=dict(d.get("metadata") or {}),
                )
            )
            vectors.append(emb)
        mat = (
            np.asarray(vectors, dtype=np.float32)
            if vectors
            else np.zeros((0, dim), dtype=np.float32)
        )
        return cls(items=items, vectors=mat, dim=dim)


# ---------------------------------------------------------------------------
# High-level pipeline
# ---------------------------------------------------------------------------
async def build_vector_store(
    settings: Settings | None = None,
    *,
    chunk_size: int = 1024,
    chunk_overlap: int = 128,
    embed_dim: int = DEFAULT_EMBED_DIM,
    embed_batch: int = DEFAULT_EMBED_BATCH,
    **_unused: Any,
) -> VectorStore:
    """Read raw docs -> chunk -> embed -> populate FAISS-backed store."""
    settings = settings or get_settings()
    chunks = chunk_documents(
        raw_docs_dir=settings.rag_raw_docs_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    store = VectorStore(dim=embed_dim)
    if not chunks:
        return store

    embedder = LocalSentenceTransformerEmbedder(settings, dimensions=embed_dim)
    vectors = await embedder.embed_many(
        [c.text for c in chunks], batch_size=embed_batch
    )
    # Reconcile store dim with the model's native dim if they differ.
    if vectors.size and vectors.shape[1] != store.dim:
        store = VectorStore(dim=int(vectors.shape[1]))
    store.extend(chunks, vectors)
    return store


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m utility_mcp_server.rag.embed",
        description=(
            "Build the FAISS dense-vector store for the Pine Labs SDK docs "
            "and (optionally) run a similarity search."
        ),
    )
    parser.add_argument("--chunk-size", type=int, default=1024)
    parser.add_argument("--overlap", dest="chunk_overlap", type=int, default=128)
    parser.add_argument("--embed-dim", type=int, default=DEFAULT_EMBED_DIM)
    parser.add_argument("--embed-batch", type=int, default=DEFAULT_EMBED_BATCH)
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Persist the store (chunks + embeddings) as JSON to this path.",
    )
    parser.add_argument(
        "--load",
        type=Path,
        default=None,
        help="Load a previously saved store JSON instead of re-chunking/embedding.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Optional query text -- runs FAISS search over the store.",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--log-level", default="INFO")
    return parser


async def _amain(args) -> int:
    settings = get_settings()

    if args.load:
        store = VectorStore.load(args.load)
        logger.info("Loaded %d chunk(s) from %s", len(store), args.load)
    else:
        store = await build_vector_store(
            settings,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            embed_dim=args.embed_dim,
            embed_batch=args.embed_batch,
        )

    if not store.items:
        print("No chunks were produced -- is the docs directory populated?")
        return 1

    print(f"\nIndexed {len(store)} chunk(s) (dim={store.dim})")
    by_route: dict[str, int] = {}
    for item in store.items:
        by_route[item.route] = by_route.get(item.route, 0) + 1
    for route, n in sorted(by_route.items()):
        print(f"  - {route}: {n} chunk(s)")

    if args.save:
        store.save(args.save)
        print(f"\nSaved vector store -> {args.save}")

    if args.query:
        hits = await store.search(args.query, top_k=args.top_k)
        print(f"\nTop {len(hits)} FAISS result(s) for: {args.query!r}")
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


__all__ = [
    "LocalSentenceTransformerEmbedder",
    "BedrockTitanEmbedder",
    "SearchHit",
    "VectorStore",
    "build_vector_store",
    "DEFAULT_EMBED_DIM",
]
