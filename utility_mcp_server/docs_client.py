"""Async client for fetching Pine Labs SDK markdown documentation.

The Pine Labs documentation site (Vite SPA) serves raw markdown when the
API path is requested with a ``.md`` suffix, e.g.::

    https://vnykumargoyal.github.io/pinelabs-docs/api/init.md

This module provides a thin, production-ready client around that endpoint
with:

* connection pooling via a single ``httpx.AsyncClient``
* configurable timeout
* bounded retries with exponential backoff for transient failures
* an in-memory TTL cache to avoid hammering the upstream
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Iterable

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Static API registry
# ---------------------------------------------------------------------------
# Maps the public ``api_name`` (as used by MCP clients) to:
#   (category, url-slug)
#
# ``url-slug`` is the path segment under ``/api/`` on the docs site. We keep
# it explicit because the docs site uses kebab-case slugs while api_name is
# camelCase (e.g. ``doTransaction`` -> ``do-transaction``).
API_REGISTRY: dict[str, tuple[str, str]] = {
    "init": ("lifecycle", "init"),
    "doTransaction": ("transaction", "do-transaction"),
}


@dataclass(frozen=True)
class ApiInfo:
    """Resolved metadata for a documented API."""

    name: str
    category: str
    url: str

    @property
    def qualified_name(self) -> str:
        return f"{self.category}/{self.name}"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class DocsError(Exception):
    """Base error raised by the docs client."""


class DocsNotFound(DocsError):
    """Raised when the requested api_name is not in the registry."""


class DocsFetchError(DocsError):
    """Raised when the upstream fetch fails after retries."""


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
@dataclass
class _CacheEntry:
    value: str
    expires_at: float


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------
class PinelabsDocsClient:
    """Async client that fetches Pine Labs SDK markdown docs over HTTP."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        retries: int = 2,
        cache_ttl_seconds: int = 300,
        registry: dict[str, tuple[str, str]] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = max(0, retries)
        self._cache_ttl = max(0, cache_ttl_seconds)
        self._registry = dict(registry or API_REGISTRY)

        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self._timeout),
            headers={
                "User-Agent": "utility-mcp-server/1.0 (+https://github.com/prakhargour10/utility-mcp-server)",
                "Accept": "text/markdown, text/plain, */*;q=0.5",
            },
            follow_redirects=True,
        )
        self._cache: dict[str, _CacheEntry] = {}
        self._lock = asyncio.Lock()

    # -- lifecycle ----------------------------------------------------------
    async def aclose(self) -> None:
        await self._client.aclose()

    def close_sync(self) -> None:
        """Best-effort sync close, safe to call from atexit handlers."""
        if self._client.is_closed:
            return
        try:
            asyncio.run(self._client.aclose())
        except RuntimeError:
            # Event loop is already running or closed; httpx will GC sockets.
            pass

    # -- registry helpers ---------------------------------------------------
    def list_apis(self) -> list[ApiInfo]:
        """Return the list of known APIs, sorted by qualified name."""
        infos = [self._resolve(name) for name in self._registry]
        infos.sort(key=lambda a: a.qualified_name)
        return infos

    def known_names(self) -> Iterable[str]:
        return self._registry.keys()

    def _resolve(self, api_name: str) -> ApiInfo:
        try:
            category, slug = self._registry[api_name]
        except KeyError as exc:
            raise DocsNotFound(api_name) from exc
        url = f"{self._base_url}/api/{slug}.md"
        return ApiInfo(name=api_name, category=category, url=url)

    # -- fetching -----------------------------------------------------------
    async def get_documentation(self, api_name: str) -> tuple[ApiInfo, str]:
        """Return (info, markdown) for the given api_name.

        Raises:
            DocsNotFound: if api_name is not in the registry.
            DocsFetchError: if the upstream cannot be reached after retries.
        """
        info = self._resolve(api_name)
        markdown = await self._fetch_cached(info.url)
        return info, markdown

    async def _fetch_cached(self, url: str) -> str:
        now = time.monotonic()
        entry = self._cache.get(url)
        if entry is not None and entry.expires_at > now:
            logger.debug("docs cache hit: %s", url)
            return entry.value

        async with self._lock:
            # re-check after acquiring the lock
            entry = self._cache.get(url)
            now = time.monotonic()
            if entry is not None and entry.expires_at > now:
                return entry.value

            text = await self._fetch_with_retry(url)
            if self._cache_ttl > 0:
                self._cache[url] = _CacheEntry(
                    value=text, expires_at=now + self._cache_ttl
                )
            return text

    async def _fetch_with_retry(self, url: str) -> str:
        last_exc: Exception | None = None
        for attempt in range(self._retries + 1):
            try:
                logger.info("Fetching docs (attempt %d): %s", attempt + 1, url)
                resp = await self._client.get(url)
                resp.raise_for_status()
                return resp.text
            except httpx.HTTPStatusError as exc:
                # 4xx are not retryable; 5xx are.
                status = exc.response.status_code
                last_exc = exc
                if 400 <= status < 500:
                    logger.warning("Non-retryable HTTP %s for %s", status, url)
                    break
                logger.warning(
                    "Retryable HTTP %s for %s (attempt %d)", status, url, attempt + 1
                )
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                logger.warning(
                    "Transport error for %s (attempt %d): %s", url, attempt + 1, exc
                )

            if attempt < self._retries:
                backoff = 0.5 * (2**attempt)
                await asyncio.sleep(backoff)

        raise DocsFetchError(f"Failed to fetch {url}: {last_exc}") from last_exc
