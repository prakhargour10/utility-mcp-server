"""Stage 1 of the RAG pipeline: ingest raw docs as markdown files.

Fetches every documented endpoint from the Pine Labs docs site (each route
is also published as a raw ``.md`` document) and writes it to a local
directory mirroring the route layout::

    data/raw_docs/
        api/
            init.md
            do-transaction.md
        concepts/
            getting-started.md
            error-handling.md
            transports.md

These files become the input corpus for the chunking / embedding stages.

Usage::

    python -m utility_mcp_server.rag.ingest
    python -m utility_mcp_server.rag.ingest --force
    python -m utility_mcp_server.rag.ingest --route api/init --route api/do-transaction
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import httpx

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class IngestedDoc:
    """Metadata for a single fetched document."""

    route: str          # e.g. "api/init"
    url: str            # full upstream URL of the .md file
    path: Path          # local on-disk file path
    bytes_written: int  # size of the file written


@dataclass(frozen=True)
class IngestFailure:
    """Metadata for a route that failed to ingest."""

    route: str
    url: str
    error: str


@dataclass(frozen=True)
class IngestReport:
    """Result of an ingestion run."""

    docs: list[IngestedDoc]
    failures: list[IngestFailure]
    output_dir: Path

    @property
    def ok(self) -> bool:
        return not self.failures


# ---------------------------------------------------------------------------
# Core ingestion
# ---------------------------------------------------------------------------
def _route_to_url(base_url: str, route: str) -> str:
    return f"{base_url.rstrip('/')}/{route.strip('/')}.md"


def _route_to_path(output_dir: Path, route: str) -> Path:
    parts = [p for p in route.strip("/").split("/") if p]
    if not parts:
        raise ValueError(f"Invalid route: {route!r}")
    filename = parts[-1] + ".md"
    return output_dir.joinpath(*parts[:-1], filename)


async def _fetch_one(
    client: httpx.AsyncClient,
    base_url: str,
    route: str,
    output_dir: Path,
    *,
    force: bool,
) -> IngestedDoc | IngestFailure:
    url = _route_to_url(base_url, route)
    target = _route_to_path(output_dir, route)

    if target.exists() and not force:
        size = target.stat().st_size
        logger.info("skip (exists): %s -> %s (%d bytes)", route, target, size)
        return IngestedDoc(route=route, url=url, path=target, bytes_written=size)

    try:
        logger.info("fetch: %s", url)
        resp = await client.get(url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("failed: %s (%s)", url, exc)
        return IngestFailure(route=route, url=url, error=str(exc))

    body = resp.text
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    logger.info("wrote: %s (%d bytes)", target, len(body.encode("utf-8")))
    return IngestedDoc(
        route=route,
        url=url,
        path=target,
        bytes_written=len(body.encode("utf-8")),
    )


async def fetch_all_docs(
    *,
    routes: Sequence[str],
    base_url: str,
    output_dir: Path,
    force: bool = False,
    timeout: float = 15.0,
    concurrency: int = 5,
) -> IngestReport:
    """Fetch every ``route`` from ``base_url`` as markdown into ``output_dir``.

    Args:
        routes: Routes to fetch (e.g. ``"api/init"``), without ``.md`` suffix.
        base_url: Docs site base URL (e.g. ``https://.../pinelabs-docs``).
        output_dir: Local directory to write ``.md`` files into.
        force: Re-download even if the target file already exists.
        timeout: Per-request HTTP timeout in seconds.
        concurrency: Max number of concurrent fetches.

    Returns:
        :class:`IngestReport` summarising successes and failures.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(max(1, concurrency))

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(timeout),
        headers={
            "User-Agent": "utility-mcp-server-rag-ingest/1.0",
            "Accept": "text/markdown, text/plain, */*;q=0.5",
        },
        follow_redirects=True,
    ) as client:
        async def _bounded(route: str):
            async with sem:
                return await _fetch_one(
                    client, base_url, route, output_dir, force=force
                )

        results = await asyncio.gather(*(_bounded(r) for r in routes))

    docs = [r for r in results if isinstance(r, IngestedDoc)]
    failures = [r for r in results if isinstance(r, IngestFailure)]
    return IngestReport(docs=docs, failures=failures, output_dir=output_dir)


def fetch_all_docs_sync(
    *,
    settings: Settings | None = None,
    routes: Iterable[str] | None = None,
    force: bool = False,
) -> IngestReport:
    """Synchronous convenience wrapper around :func:`fetch_all_docs`."""
    settings = settings or get_settings()
    chosen_routes = list(routes) if routes is not None else list(settings.rag_doc_routes)
    return asyncio.run(
        fetch_all_docs(
            routes=chosen_routes,
            base_url=settings.docs_base_url,
            output_dir=settings.rag_raw_docs_dir,
            force=force,
        )
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m utility_mcp_server.rag.ingest",
        description=(
            "Fetch every Pine Labs docs endpoint as a .md file into the "
            "local raw-docs directory (RAG pipeline stage 1)."
        ),
    )
    parser.add_argument(
        "--route",
        action="append",
        dest="routes",
        metavar="ROUTE",
        help=(
            "A single route to ingest (e.g. 'api/init'). Repeat the flag to "
            "ingest multiple routes. Defaults to RAG_DOC_ROUTES from config."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if a target file already exists.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override the output directory (default: RAG_RAW_DOCS_DIR).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Python log level (default: INFO).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    settings = get_settings()
    routes = args.routes or list(settings.rag_doc_routes)
    output_dir = args.output_dir or settings.rag_raw_docs_dir

    if not routes:
        logger.error("No routes configured. Set RAG_DOC_ROUTES or pass --route.")
        return 2

    report = asyncio.run(
        fetch_all_docs(
            routes=routes,
            base_url=settings.docs_base_url,
            output_dir=output_dir,
            force=args.force,
        )
    )

    print()
    print(f"Ingested {len(report.docs)} document(s) into {report.output_dir}")
    for doc in report.docs:
        rel = doc.path.relative_to(report.output_dir)
        print(f"  + {rel}  ({doc.bytes_written:,} bytes)  <- {doc.url}")
    if report.failures:
        print(f"\n{len(report.failures)} failure(s):")
        for f in report.failures:
            print(f"  ! {f.route}  <- {f.url}\n      {f.error}")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
