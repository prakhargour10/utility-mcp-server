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

    # Pine Labs documentation source (used by the RAG ingest stage)
    docs_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "PINELABS_DOCS_BASE_URL",
            "https://portal.tms.uat.pinelabs.com/pinelabs-doc/docs",
        ).rstrip("/")
    )

    # SDK download artifacts (still served from local repo)
    sdk_dir: Path = field(default_factory=lambda: REPO_ROOT / "sdk")
    sdk_download_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "SDK_DOWNLOAD_BASE_URL",
            "https://github.com/prakhargour10/utility-mcp-server/raw/main/sdk",
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
    # Local directory where ingested raw markdown is written. Used as the
    # source of truth for chunking + embedding.
    rag_raw_docs_dir: Path = field(
        default_factory=lambda: Path(
            os.environ.get(
                "RAG_RAW_DOCS_DIR",
                str(REPO_ROOT / "data" / "raw_docs"),
            )
        )
    )
    # Routes (relative to docs_base_url, without the .md suffix) that
    # expose raw markdown content. Override with a comma-separated list.
    rag_doc_routes: list[str] = field(
        default_factory=lambda: _env_list(
            "RAG_DOC_ROUTES",
            [
                "overview",
                "concepts/lifecycle",
                "concepts/transports",
                "concepts/capabilities",
                "concepts/eventid",
                "concepts/error-handling",
                "concepts/result-payload",
                "concepts/versioning",
                "languages/android",
                "languages/ios",
                "languages/python",
                "languages/nodejs",
                "languages/c",
                "wire-formats/csv",
                "wire-formats/pad-controller-frame",
            ],
        )
    )

    # ------------------------------------------------------------------
    # AWS Bedrock (Claude + Titan embeddings)
    # ------------------------------------------------------------------
    bedrock_api_key: str = field(
        default_factory=lambda: os.environ.get("BEDROCK_API_KEY", "")
    )
    bedrock_model: str = field(
        default_factory=lambda: os.environ.get(
            "BEDROCK_MODEL", "global.anthropic.claude-opus-4-6-v1"
        )
    )
    bedrock_region: str = field(
        default_factory=lambda: os.environ.get("BEDROCK_REGION", "us-east-1")
    )
    bedrock_embedding_model: str = field(
        default_factory=lambda: os.environ.get(
            "BEDROCK_EMBEDDING_MODEL", "amazon.titan-embed-text-v2:0"
        )
    )

    @property
    def bedrock_converse_url(self) -> str:
        return (
            f"https://bedrock-runtime.{self.bedrock_region}.amazonaws.com"
            f"/model/{self.bedrock_model}/converse"
        )

    @property
    def bedrock_embedding_url(self) -> str:
        return (
            f"https://bedrock-runtime.{self.bedrock_region}.amazonaws.com"
            f"/model/{self.bedrock_embedding_model}/invoke"
        )


def get_settings() -> Settings:
    """Return a fresh Settings instance (env is read at call time)."""
    return Settings()
