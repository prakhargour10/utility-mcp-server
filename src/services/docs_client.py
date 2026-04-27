"""Async HTTP client for fetching Pine Labs SDK documentation pages.

Features:
- Single shared httpx.AsyncClient (connection pooling).
- In-memory TTL cache keyed by api_name.
- Bounded retries with exponential backoff for transient errors.
- HTML -> Markdown conversion via markdownify.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from markdownify import markdownify as html_to_markdown

from ..config import settings
from ..logging_config import logger


@dataclass
class _CacheEntry:
    markdown: str
    fetched_at: float
    source_url: str


class DocsClient:
    """Fetch and cache documentation markdown for known API names."""

    _RETRY_STATUS = {408, 425, 429, 500, 502, 503, 504}

    def __init__(self) -> None:
        self._cache: dict[str, _CacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._client: Optional[httpx.AsyncClient] = None

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            async with self._global_lock:
                if self._client is None or self._client.is_closed:
                    self._client = httpx.AsyncClient(
                        timeout=httpx.Timeout(settings.docs_http_timeout_s),
                        headers={"User-Agent": settings.docs_user_agent},
                        follow_redirects=True,
                    )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def known_apis(self) -> list[str]:
        return sorted(settings.api_doc_urls.keys())

    async def get_documentation(self, api_name: str) -> tuple[str, str]:
        """Return ``(markdown, source_url)`` for the given API name.

        Raises:
            KeyError: api_name is not in the configured mapping.
            httpx.HTTPError: Network failure after retries are exhausted.
        """
        if api_name not in settings.api_doc_urls:
            raise KeyError(api_name)

        # Serve from cache when fresh.
        cached = self._cache.get(api_name)
        if cached and (time.monotonic() - cached.fetched_at) < settings.docs_cache_ttl_s:
            logger.debug("docs cache hit: %s", api_name)
            return cached.markdown, cached.source_url

        # Per-key lock prevents thundering-herd on cold cache.
        lock = self._locks.setdefault(api_name, asyncio.Lock())
        async with lock:
            cached = self._cache.get(api_name)
            if cached and (time.monotonic() - cached.fetched_at) < settings.docs_cache_ttl_s:
                return cached.markdown, cached.source_url

            url = settings.api_doc_urls[api_name]
            html = await self._fetch_with_retry(url)
            markdown = self._html_to_markdown(html)
            self._cache[api_name] = _CacheEntry(
                markdown=markdown, fetched_at=time.monotonic(), source_url=url
            )
            logger.info("docs cached: %s (%d chars)", api_name, len(markdown))
            return markdown, url

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    async def _fetch_with_retry(self, url: str) -> str:
        client = await self._get_client()
        max_retries = max(0, settings.docs_http_max_retries)
        last_exc: Optional[BaseException] = None

        for attempt in range(max_retries + 1):
            try:
                response = await client.get(url)
                if response.status_code in self._RETRY_STATUS and attempt < max_retries:
                    raise httpx.HTTPStatusError(
                        f"retryable status {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                return response.text
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                if attempt >= max_retries:
                    break
                backoff = min(2 ** attempt * 0.5, 4.0)
                logger.warning(
                    "docs fetch failed (attempt %d/%d) for %s: %s — retrying in %.1fs",
                    attempt + 1,
                    max_retries + 1,
                    url,
                    exc,
                    backoff,
                )
                await asyncio.sleep(backoff)

        assert last_exc is not None
        raise last_exc

    @staticmethod
    def _html_to_markdown(html: str) -> str:
        markdown = html_to_markdown(
            html,
            heading_style="ATX",
            strip=["script", "style", "noscript"],
        )
        # Collapse excessive blank lines.
        lines = [ln.rstrip() for ln in markdown.splitlines()]
        cleaned: list[str] = []
        blank = 0
        for ln in lines:
            if not ln:
                blank += 1
                if blank <= 2:
                    cleaned.append(ln)
            else:
                blank = 0
                cleaned.append(ln)
        return "\n".join(cleaned).strip() + "\n"


# Module-level singleton.
docs_client = DocsClient()
