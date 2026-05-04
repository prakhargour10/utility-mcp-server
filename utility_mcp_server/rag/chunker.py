"""Markdown chunking for the Pine Labs docs corpus.

Strategy
--------
1. Walk ``docs_dir/doc_list/{apis,concepts,languages,models}/**/*.md``.
2. For each file, split by top-level markdown headings (``#``, ``##``,
   ``###``). Each heading section is a candidate chunk.
3. If a section exceeds ``max_chars`` it is further split on paragraph
   boundaries with a small overlap so semantic context is preserved.
4. Each chunk carries enough metadata (``doc_key``, ``category``,
   ``heading``) for the search tool to point the LLM back at
   ``get_documentation`` for the full markdown body.

The chunker is intentionally dependency-free so it can be unit-tested
without loading any ML model.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

# Categories on disk under ``docs/doc_list/``. Keep in sync with
# ``tools._DOC_CATEGORIES``.
_CATEGORIES: tuple[str, ...] = ("apis", "models", "languages", "concepts")

# Matches a markdown ATX heading at start of line: 1–6 ``#`` followed
# by a space then heading text.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class DocChunk:
    """A single retrievable slice of documentation."""

    chunk_id: int
    category: str  # e.g. "apis", "models", "languages", "concepts"
    doc_key: str  # e.g. "do_transaction" or "android/setup"
    heading: str  # nearest enclosing markdown heading, or "" for preamble
    text: str  # raw chunk text (no metadata header)
    source_path: str  # absolute path of the source .md file

    def embed_text(self) -> str:
        """Return the text actually fed to the embedding model.

        Prepending the category/doc_key/heading gives the model lexical
        context that pure body text would lack — small but consistently
        improves retrieval quality on short technical docs.
        """
        header = f"[{self.category}/{self.doc_key}]"
        if self.heading:
            header += f" {self.heading}"
        return f"{header}\n\n{self.text}"


@dataclass
class _ChunkConfig:
    max_chars: int = 1200
    overlap_chars: int = 150
    min_chars: int = 40  # drop anything tinier (likely just whitespace)


def _iter_markdown_files(doc_list_dir: Path) -> Iterable[tuple[str, str, Path]]:
    """Yield ``(category, doc_key, path)`` for every *.md under doc_list/.

    Mirrors the key derivation in ``tools._list_md_keys`` so search
    results align with what ``get_documentation`` accepts.
    """
    for category in _CATEGORIES:
        cat_dir = doc_list_dir / category
        if not cat_dir.is_dir():
            continue
        for entry in sorted(cat_dir.iterdir()):
            if entry.is_file() and entry.suffix.lower() == ".md":
                yield category, entry.stem, entry
            elif entry.is_dir():
                for sub in sorted(entry.iterdir()):
                    if sub.is_file() and sub.suffix.lower() == ".md":
                        yield category, f"{entry.name}/{sub.stem}", sub


def _split_by_headings(markdown: str) -> list[tuple[str, str]]:
    """Return ``[(heading, body), ...]`` sections.

    The first section's heading is ``""`` (preamble before any heading).
    """
    sections: list[tuple[str, str]] = []
    matches = list(_HEADING_RE.finditer(markdown))
    if not matches:
        return [("", markdown.strip())]

    # Preamble before the first heading.
    if matches[0].start() > 0:
        preamble = markdown[: matches[0].start()].strip()
        if preamble:
            sections.append(("", preamble))

    for i, m in enumerate(matches):
        heading = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        body = markdown[body_start:body_end].strip()
        # Always emit even an empty body — heading itself is signal.
        sections.append((heading, body))

    return sections


def _split_long_section(body: str, cfg: _ChunkConfig) -> list[str]:
    """Split a long body into <= ``max_chars`` pieces with small overlap.

    Splits on blank lines (paragraph boundary) first; falls back to
    hard char slicing only if a single paragraph itself exceeds
    ``max_chars`` (rare for Pine Labs docs).
    """
    if len(body) <= cfg.max_chars:
        return [body] if body.strip() else []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for para in paragraphs:
        if len(para) > cfg.max_chars:
            # Flush buffer first.
            if buf:
                chunks.append(buf.strip())
                buf = ""
            # Hard-slice the giant paragraph.
            for i in range(0, len(para), cfg.max_chars - cfg.overlap_chars):
                chunks.append(para[i : i + cfg.max_chars])
            continue
        if len(buf) + len(para) + 2 <= cfg.max_chars:
            buf = f"{buf}\n\n{para}" if buf else para
        else:
            chunks.append(buf.strip())
            # Start next buffer with a small tail of the previous one.
            tail = buf[-cfg.overlap_chars :] if cfg.overlap_chars else ""
            buf = f"{tail}\n\n{para}".strip() if tail else para
    if buf.strip():
        chunks.append(buf.strip())
    return chunks


def chunk_docs_dir(
    docs_dir: Path,
    *,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[DocChunk]:
    """Return all retrievable chunks under ``docs_dir/doc_list``."""
    doc_list_dir = docs_dir / "doc_list"
    if not doc_list_dir.is_dir():
        logger.warning("doc_list directory not found at %s", doc_list_dir)
        return []

    cfg = _ChunkConfig(max_chars=max_chars, overlap_chars=overlap_chars)
    chunks: list[DocChunk] = []
    next_id = 0

    for category, doc_key, path in _iter_markdown_files(doc_list_dir):
        try:
            markdown = path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Skipping %s: %s", path, exc)
            continue

        for heading, body in _split_by_headings(markdown):
            if not body and not heading:
                continue
            pieces = _split_long_section(body, cfg) or ([heading] if heading else [])
            for piece in pieces:
                # Always include the heading inside the chunk text so a
                # standalone paragraph keeps its semantic anchor.
                if heading and not piece.lstrip().startswith(heading):
                    piece_text = f"{heading}\n\n{piece}".strip()
                else:
                    piece_text = piece.strip()
                if len(piece_text) < cfg.min_chars and not heading:
                    continue
                chunks.append(
                    DocChunk(
                        chunk_id=next_id,
                        category=category,
                        doc_key=doc_key,
                        heading=heading,
                        text=piece_text,
                        source_path=str(path.resolve()),
                    )
                )
                next_id += 1

    logger.info(
        "Chunked %d markdown files into %d chunks under %s",
        sum(1 for _ in _iter_markdown_files(doc_list_dir)),
        len(chunks),
        doc_list_dir,
    )
    return chunks
