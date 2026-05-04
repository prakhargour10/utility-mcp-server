"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv as _load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    _load_dotenv = None


# Repository root: <repo>/utility_mcp_server/config.py -> parents[1]
REPO_ROOT: Path = Path(__file__).resolve().parents[1]

# Load .env from the repo root (and the current working directory as a
# fallback) the first time this module is imported. Existing OS env vars
# always win over .env values.
if _load_dotenv is not None:
    _env_file = REPO_ROOT / ".env"
    if _env_file.exists():
        _load_dotenv(_env_file, override=False)
    else:
        _load_dotenv(override=False)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.environ.get(name)
    if not raw:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    """Server settings."""

    # HTTP server
    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _env_int("PORT", 8000))
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))

    # SDK download artifacts (still served from local repo)
    sdk_dir: Path = field(default_factory=lambda: REPO_ROOT / "docs" / "sdk_list")
    sdk_download_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "SDK_DOWNLOAD_BASE_URL",
            "https://github.com/prakhargour10/utility-mcp-server/raw/main/docs/sdk_list",
        ).rstrip("/")
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

    # ------------------------------------------------------------------
    # RAG (Retrieval-Augmented Generation)
    # ------------------------------------------------------------------
    # Local directory containing the markdown documentation corpus. This
    # is the single source of truth for chunking + embedding -- docs are
    # committed to the repo under ``docs/`` rather than fetched at build
    # time.
    rag_raw_docs_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "RAG_RAW_DOCS_DIR",
                str(REPO_ROOT / "docs" / "doc_list"),
            )
        )
    )
    # Persisted vector store output. Kept under ``data/`` (which is
    # gitignored) so embeddings rebuilds don't pollute the docs corpus.
    rag_embeddings_path: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "RAG_EMBEDDINGS_PATH",
                str(REPO_ROOT / "data" / "embeddings.json"),
            )
        )
    )

    # ------------------------------------------------------------------
    # Local embeddings (sentence-transformers)
    # ------------------------------------------------------------------
    embedding_model: str = field(
        default_factory=lambda: os.environ.get(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
    )


def get_settings() -> Settings:
    """Return a fresh Settings instance (env is read at call time)."""
    return Settings()
