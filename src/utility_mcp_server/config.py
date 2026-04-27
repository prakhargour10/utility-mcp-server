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


# Repository root: <repo>/src/utility_mcp_server/config.py -> parents[2]
REPO_ROOT: Path = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Server settings."""

    # HTTP server
    host: str = field(default_factory=lambda: os.environ.get("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _env_int("PORT", 8000))
    log_level: str = field(default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO"))

    # Pine Labs documentation source
    docs_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "PINELABS_DOCS_BASE_URL",
            "https://vnykumargoyal.github.io/pinelabs-docs",
        ).rstrip("/")
    )
    docs_http_timeout: float = field(
        default_factory=lambda: _env_float("PINELABS_DOCS_HTTP_TIMEOUT", 10.0)
    )
    docs_cache_ttl_seconds: int = field(
        default_factory=lambda: _env_int("PINELABS_DOCS_CACHE_TTL", 300)
    )
    docs_http_retries: int = field(
        default_factory=lambda: _env_int("PINELABS_DOCS_HTTP_RETRIES", 2)
    )

    # SDK download artifacts (still served from local repo)
    sdk_dir: Path = field(default_factory=lambda: REPO_ROOT / "api-docs" / "sdk")
    sdk_download_base_url: str = field(
        default_factory=lambda: os.environ.get(
            "SDK_DOWNLOAD_BASE_URL",
            "https://github.com/prakhargour10/utility-mcp-server/raw/main/api-docs/sdk",
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


def get_settings() -> Settings:
    """Return a fresh Settings instance (env is read at call time)."""
    return Settings()
