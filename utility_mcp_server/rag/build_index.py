"""CLI entrypoint to (re)build the FAISS RAG index.

Usage::

    python -m utility_mcp_server.rag.build_index
"""

from __future__ import annotations

import logging
import sys

from ..config import get_settings
from .index import build_and_save_index, reset_index_cache


def main() -> int:
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    settings = get_settings()
    logger = logging.getLogger("utility_mcp_server.rag.build_index")
    logger.info("Building RAG index")
    logger.info("  docs_dir = %s", settings.docs_dir)
    logger.info("  data_dir = %s", settings.data_dir)
    logger.info("  model    = %s", settings.embedding_model)

    try:
        n_chunks, dim = build_and_save_index(
            settings.docs_dir,
            settings.data_dir,
            model_name=settings.embedding_model,
        )
    except Exception as exc:  # noqa: BLE001 — surface any build error
        logger.exception("Index build failed: %s", exc)
        return 1

    reset_index_cache()
    logger.info("Done: %d chunks, dim=%d", n_chunks, dim)
    return 0


if __name__ == "__main__":
    sys.exit(main())
