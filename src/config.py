"""Centralized configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# Canonical mapping of api_name -> remote documentation URL.
_DEFAULT_API_DOC_URLS: Mapping[str, str] = MappingProxyType(
    {
        "init": "https://vnykumargoyal.github.io/pinelabs-docs/api/init",
        "checkStatus": "https://vnykumargoyal.github.io/pinelabs-docs/api/check-status",
        "doTransaction": "https://vnykumargoyal.github.io/pinelabs-docs/api/do-transaction",
    }
)


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the MCP server."""

    # ----- Server -----
    server_name: str = "utility-mcp-server"
    server_instructions: str = (
        "A utility MCP server providing IST time, date, stock prices, "
        "and Pine Labs SDK API documentation."
    )
    allowed_hosts: tuple[str, ...] = (
        "utility-mcp-server-production.up.railway.app",
        "localhost:*",
        "127.0.0.1:*",
    )
    port: int = field(default_factory=lambda: _env_int("PORT", 8000))

    # ----- API documentation source -----
    api_doc_urls: Mapping[str, str] = field(default_factory=lambda: _DEFAULT_API_DOC_URLS)
    docs_http_timeout_s: float = field(
        default_factory=lambda: _env_float("DOCS_HTTP_TIMEOUT_S", 10.0)
    )
    docs_http_max_retries: int = field(
        default_factory=lambda: _env_int("DOCS_HTTP_MAX_RETRIES", 3)
    )
    docs_cache_ttl_s: int = field(
        default_factory=lambda: _env_int("DOCS_CACHE_TTL_S", 3600)
    )
    docs_user_agent: str = field(
        default_factory=lambda: os.environ.get(
            "DOCS_USER_AGENT", "utility-mcp-server/1.0 (+https://github.com/prakhargour10/utility-mcp-server)"
        )
    )

    # ----- SDK download -----
    sdk_root: Path = field(default_factory=lambda: PROJECT_ROOT / "api-docs" / "sdk")
    sdk_download_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "SDK_DOWNLOAD_BASE_URL",
            "https://github.com/prakhargour10/utility-mcp-server/raw/main/api-docs/sdk",
        )
    )

    # ----- Logging -----
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))


settings = Settings()
