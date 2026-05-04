"""FAISS index lifecycle: build / save / load / search.

Storage layout (under ``settings.data_dir``)::

    data/
      faiss.index      ← binary FAISS index (IndexFlatIP, dim=384)
      chunks.json      ← sidecar JSON with chunk metadata + manifest

The sidecar manifest pins the embedding model + dimension so a stale
index built with a different model is rejected at load time.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from .chunker import DocChunk, chunk_docs_dir
from .embedder import Embedder

if TYPE_CHECKING:  # pragma: no cover
    import faiss  # type: ignore

logger = logging.getLogger(__name__)

# Bump when the on-disk index format changes in a non-backward-compatible
# way (e.g. metric, sidecar schema). Loaders refuse mismatched versions.
_INDEX_SCHEMA_VERSION = 1

_INDEX_FILENAME = "faiss.index"
_SIDECAR_FILENAME = "chunks.json"


@dataclass(frozen=True)
class SearchHit:
    """A single retrieval result."""

    chunk_id: int
    score: float  # cosine similarity in [-1, 1]; higher = more similar
    category: str
    doc_key: str
    heading: str
    snippet: str  # truncated chunk text suitable for an LLM-visible blurb
    source_path: str


def _import_faiss():
    try:
        import faiss  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "faiss-cpu is required for RAG. "
            "Install with: pip install -r requirements.txt"
        ) from exc
    return faiss


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_and_save_index(
    docs_dir: Path,
    data_dir: Path,
    *,
    model_name: str,
) -> tuple[int, int]:
    """Build the FAISS index from scratch and persist it.

    Returns ``(num_chunks, dim)``.
    """
    faiss = _import_faiss()

    chunks = chunk_docs_dir(docs_dir)
    if not chunks:
        raise RuntimeError(
            f"No markdown chunks found under {docs_dir}/doc_list — "
            "nothing to index."
        )

    embedder = Embedder.get(model_name)
    logger.info("Embedding %d chunks with %s …", len(chunks), model_name)
    vectors = embedder.encode(
        [c.embed_text() for c in chunks], show_progress=False
    )
    dim = embedder.dimension

    # IndexFlatIP + L2-normalized vectors == cosine similarity.
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    data_dir.mkdir(parents=True, exist_ok=True)
    index_path = data_dir / _INDEX_FILENAME
    sidecar_path = data_dir / _SIDECAR_FILENAME

    faiss.write_index(index, str(index_path))

    sidecar = {
        "schema_version": _INDEX_SCHEMA_VERSION,
        "model_name": model_name,
        "dimension": dim,
        "metric": "cosine",  # ip + normalized == cosine
        "num_chunks": len(chunks),
        "chunks": [asdict(c) for c in chunks],
    }
    sidecar_path.write_text(
        json.dumps(sidecar, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    logger.info(
        "RAG index built: %d chunks, dim=%d, model=%s -> %s",
        len(chunks),
        dim,
        model_name,
        index_path,
    )
    return len(chunks), dim


# ---------------------------------------------------------------------------
# Load + search
# ---------------------------------------------------------------------------
class RagIndex:
    """Loaded FAISS index + chunk metadata, ready for similarity search.

    Use ``RagIndex.load_or_build`` to get a ready-to-query instance.
    """

    def __init__(
        self,
        index,
        chunks: list[DocChunk],
        *,
        model_name: str,
        dimension: int,
    ) -> None:
        self._index = index
        self._chunks = chunks
        self._model_name = model_name
        self._dimension = dimension

    # --- factories -------------------------------------------------------
    @classmethod
    def load(cls, data_dir: Path, *, expected_model: str) -> "RagIndex":
        faiss = _import_faiss()
        index_path = data_dir / _INDEX_FILENAME
        sidecar_path = data_dir / _SIDECAR_FILENAME

        if not index_path.is_file() or not sidecar_path.is_file():
            raise FileNotFoundError(
                f"RAG index not found at {data_dir} "
                f"(expected {_INDEX_FILENAME} and {_SIDECAR_FILENAME})."
            )

        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        if sidecar.get("schema_version") != _INDEX_SCHEMA_VERSION:
            raise RuntimeError(
                f"RAG sidecar schema version mismatch "
                f"(got {sidecar.get('schema_version')!r}, "
                f"expected {_INDEX_SCHEMA_VERSION}). Rebuild the index."
            )
        if sidecar.get("model_name") != expected_model:
            raise RuntimeError(
                "RAG index was built with a different embedding model "
                f"({sidecar.get('model_name')!r}) than the server is "
                f"configured to use ({expected_model!r}). Rebuild the index."
            )

        index = faiss.read_index(str(index_path))
        chunks = [DocChunk(**c) for c in sidecar.get("chunks", [])]
        return cls(
            index,
            chunks,
            model_name=sidecar["model_name"],
            dimension=int(sidecar["dimension"]),
        )

    @classmethod
    def load_or_build(
        cls,
        docs_dir: Path,
        data_dir: Path,
        *,
        model_name: str,
    ) -> "RagIndex":
        try:
            return cls.load(data_dir, expected_model=model_name)
        except (FileNotFoundError, RuntimeError) as exc:
            logger.warning(
                "RAG index unusable (%s). Rebuilding from %s …",
                exc,
                docs_dir,
            )
            build_and_save_index(docs_dir, data_dir, model_name=model_name)
            return cls.load(data_dir, expected_model=model_name)

    # --- query -----------------------------------------------------------
    @property
    def size(self) -> int:
        return len(self._chunks)

    @property
    def model_name(self) -> str:
        return self._model_name

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        category: str | None = None,
        snippet_chars: int = 400,
    ) -> list[SearchHit]:
        """Return up to ``top_k`` best matches for ``query``.

        ``category`` (one of ``apis|models|languages|concepts``)
        post-filters results. Because the index is small (~hundreds of
        chunks) we just over-fetch and filter in Python rather than
        maintaining per-category sub-indexes.
        """
        if not query or not query.strip():
            return []

        embedder = Embedder.get(self._model_name)
        qvec = embedder.encode([query.strip()])
        # Over-fetch when filtering so the post-filter still has enough
        # candidates to fill top_k.
        fetch_k = top_k * 5 if category else top_k
        fetch_k = min(max(fetch_k, top_k), self.size)
        if fetch_k == 0:
            return []

        scores, idxs = self._index.search(qvec, fetch_k)
        hits: list[SearchHit] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx < 0 or idx >= len(self._chunks):
                continue
            chunk = self._chunks[idx]
            if category and chunk.category != category:
                continue
            snippet = chunk.text
            if len(snippet) > snippet_chars:
                snippet = snippet[:snippet_chars].rstrip() + " …"
            hits.append(
                SearchHit(
                    chunk_id=chunk.chunk_id,
                    score=float(score),
                    category=chunk.category,
                    doc_key=chunk.doc_key,
                    heading=chunk.heading,
                    snippet=snippet,
                    source_path=chunk.source_path,
                )
            )
            if len(hits) >= top_k:
                break
        return hits


# ---------------------------------------------------------------------------
# Process-wide accessor
# ---------------------------------------------------------------------------
_index_lock = threading.Lock()
_loaded_index: RagIndex | None = None


def get_or_load_index(
    docs_dir: Path,
    data_dir: Path,
    *,
    model_name: str,
) -> RagIndex:
    """Return a cached, lazily-built ``RagIndex`` for the running process."""
    global _loaded_index
    if _loaded_index is not None:
        return _loaded_index
    with _index_lock:
        if _loaded_index is None:
            _loaded_index = RagIndex.load_or_build(
                docs_dir, data_dir, model_name=model_name
            )
    return _loaded_index


def reset_index_cache() -> None:
    """Drop the cached index (used by tests / after a rebuild)."""
    global _loaded_index
    with _index_lock:
        _loaded_index = None
