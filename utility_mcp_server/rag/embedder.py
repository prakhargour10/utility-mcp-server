"""Thin wrapper around the sentence-transformers embedding model.

The model is loaded **lazily** on first use so importing the package
(e.g. for unit tests that don't touch RAG) stays cheap.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np

logger = logging.getLogger(__name__)


class Embedder:
    """Singleton-ish embedder. One model per ``model_name`` per process."""

    _instances: dict[str, "Embedder"] = {}
    _lock = threading.Lock()

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None  # loaded on first call to .encode()
        self._dim: int | None = None
        self._load_lock = threading.Lock()

    @classmethod
    def get(cls, model_name: str) -> "Embedder":
        with cls._lock:
            inst = cls._instances.get(model_name)
            if inst is None:
                inst = cls(model_name)
                cls._instances[model_name] = inst
            return inst

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:
                return
            try:
                # Imported lazily so the package stays importable when
                # the optional RAG dependencies aren't installed.
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "sentence-transformers is required for RAG. "
                    "Install with: pip install -r requirements.txt"
                ) from exc

            logger.info("Loading embedding model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
            # Probe dimension cheaply.
            probe = self._model.encode(
                ["dimension probe"], normalize_embeddings=True
            )
            self._dim = int(probe.shape[1])
            logger.info(
                "Embedding model loaded (dim=%d): %s", self._dim, self.model_name
            )

    @property
    def dimension(self) -> int:
        self._ensure_loaded()
        assert self._dim is not None
        return self._dim

    def encode(
        self,
        texts: Sequence[str],
        *,
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> "np.ndarray":
        """Return an ``(n, dim)`` float32 array of L2-normalized vectors."""
        import numpy as np  # local: keep top-level import light

        self._ensure_loaded()
        assert self._model is not None
        if not texts:
            return np.zeros((0, self.dimension), dtype="float32")

        vectors = self._model.encode(
            list(texts),
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return vectors.astype("float32", copy=False)
