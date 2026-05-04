"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if not raw:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# Repository root: <repo>/utility_mcp_server/config.py -> parents[1]
REPO_ROOT: Path = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Server settings."""

    # HTTP server
    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _env_int("PORT", 8000))
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))

    # Local Pine Labs documentation bundle. The bundle layout is:
    #   <docs_dir>/get_documentation_list.json   <- master registry
    #   <docs_dir>/doc_list/{apis,concepts,models,languages}/*.md
    #   <docs_dir>/sdk_list/*.{zip,aar,jar,...}
    docs_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("PINELABS_DOCS_DIR", str(REPO_ROOT / "docs"))
        )
    )

    # SDK download artifacts (served from local repo, under docs/sdk_list).
    sdk_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "PINELABS_SDK_DIR", str(REPO_ROOT / "docs" / "sdk_list")
            )
        )
    )
    sdk_download_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "SDK_DOWNLOAD_BASE_URL",
            "https://github.com/prakhargour10/utility-mcp-server/raw/main/docs/sdk_list",
        ).rstrip("/")
    )

    # RAG / vector search
    #
    # ``data_dir`` holds the persisted FAISS index and its sidecar JSON.
    # ``embedding_model`` is the sentence-transformers model id; small &
    # CPU-friendly by default. ``rag_top_k`` is the default fan-out for
    # the ``search_documentation`` tool.
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get("PINELABS_DATA_DIR", str(REPO_ROOT / "data"))
        )
    )
    embedding_model: str = field(
        default_factory=lambda: os.environ.get(
            "PINELABS_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
    )
    rag_top_k: int = field(
        default_factory=lambda: _env_int("PINELABS_RAG_TOP_K", 5)
    )
    # Auto-build the FAISS index on first server startup if missing.
    # Set to "0" to require an explicit ``python -m utility_mcp_server.rag.build_index``.
    rag_autobuild: bool = field(
        default_factory=lambda: os.environ.get(
            "PINELABS_RAG_AUTOBUILD", "1"
        ).strip()
        not in ("0", "false", "False", "")
    )

    # Transport security
    allowed_hosts: list[str] = field(
        default_factory=lambda: _env_list(
            "ALLOWED_HOSTS",
            [
                "utility-mcp-server-production.up.railway.app",
                "localhost:*",
                "127.0.0.1:*",
            ],
        )
    )


def get_settings() -> Settings:
    """Return a fresh Settings instance (env is read at call time)."""
    return Settings()
