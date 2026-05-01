"""All MCP tools for the utility server.

Exposes exactly two tools:

* ``get_pinelabs_sdk_download_link`` — return public SDK download URL(s).
* ``ask_pinelabs_docs`` — RAG-grounded Q&A over the Pine Labs docs.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .rag.embed import BedrockEmbeddingError
from .rag.generate import BedrockClaudeError, answer_question
from .rag.store import get_vector_store

logger = logging.getLogger(__name__)

_SDK_EXTENSIONS = {".aar", ".jar", ".zip", ".tar.gz", ".tgz", ".whl"}


def _text_response(text: str) -> dict[str, Any]:
    """Wrap a plain string into the MCP tool text-content response shape."""
    return {"content": [{"type": "text", "text": text}]}


def _discover_sdks(sdk_dir: Path) -> list[Path]:
    if not sdk_dir.exists():
        return []
    return sorted(
        p
        for p in sdk_dir.iterdir()
        if p.is_file()
        and (p.suffix.lower() in _SDK_EXTENSIONS or p.name.lower().endswith(".tar.gz"))
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register(mcp: FastMCP, settings: Settings) -> None:
    """Attach all tools to the FastMCP server."""
    _register_sdk_download(mcp, settings.sdk_dir, settings.sdk_download_base_url)
    _register_rag(mcp, settings)


# ---------------------------------------------------------------------------
# SDK download tool
# ---------------------------------------------------------------------------
def _register_sdk_download(
    mcp: FastMCP, sdk_dir: Path, download_base_url: str
) -> None:
    base = download_base_url.rstrip("/")

    @mcp.tool(
        name="get_pinelabs_sdk_download_link",
        description=(
            "Return the official download link(s) for the Pine Labs SDK "
            "artifact(s) (e.g. the Android .aar). Use this whenever a "
            "client asks where/how to download the Pine Labs SDK, the "
            "AAR file, or the SDK binary. Optionally pass 'sdk_name' to "
            "match a specific artifact filename (substring match, case-"
            "insensitive); omit to list all available SDK downloads."
        ),
    )
    async def get_pinelabs_sdk_download_link(sdk_name: str = "") -> dict[str, Any]:
        logger.info(
            "Tool invoked: get_pinelabs_sdk_download_link(sdk_name=%r)", sdk_name
        )
        sdks = _discover_sdks(sdk_dir)
        if not sdks:
            return _text_response("No SDK artifacts are currently published.")

        if sdk_name and sdk_name.strip():
            needle = sdk_name.strip().lower()
            matched = [p for p in sdks if needle in p.name.lower()]
            if not matched:
                available = ", ".join(p.name for p in sdks)
                return _text_response(
                    f"No SDK matching '{sdk_name}' was found. "
                    f"Available SDKs: {available}"
                )
            sdks = matched

        lines = ["=== PINE LABS SDK DOWNLOAD LINKS ==="]
        for p in sdks:
            size_kb = p.stat().st_size / 1024
            url = f"{base}/{p.name}"
            lines.append(f"- {p.name} ({size_kb:,.1f} KB)\n  {url}")
        return _text_response("\n".join(lines))


# ---------------------------------------------------------------------------
# RAG: grounded Q&A
# ---------------------------------------------------------------------------
# Intent detection for "list documents" questions. Kept intentionally narrow
# so it only fires for clear enumeration intent and never swallows specific
# how-to questions (e.g. "list the parameters of init").
_LIST_DOCS_PATTERNS = (
    re.compile(
        r"\b(list|show|enumerate|what\s+are)\b.*"
        r"\b(docs?|documents?|pages?|topics?|guides?|articles?)\b",
        re.I,
    ),
    re.compile(
        r"\b(list|show|enumerate|what\s+are)\b.*"
        r"\b(all|available)\b.*\b(api|apis|endpoints?)\b",
        re.I,
    ),
    re.compile(
        r"\bavailable\s+(docs?|documents?|pages?|apis?|endpoints?)\b", re.I
    ),
    re.compile(
        r"\b(what|which)\s+(docs?|documents?|pages?|apis?|endpoints?)\b.*"
        r"\b(are|do|exist|available)\b",
        re.I,
    ),
)


def _is_list_documents_query(question: str) -> bool:
    q = question.strip()
    return any(p.search(q) for p in _LIST_DOCS_PATTERNS)


def _list_documents_response(store_items) -> str:
    routes = sorted({item.chunk.route for item in store_items})
    if not routes:
        return "No documents are currently indexed."
    lines = ["=== AVAILABLE PINE LABS SDK DOCUMENTS ==="]
    lines.extend(f"- {route}" for route in routes)
    lines.append(
        "\nAsk a follow-up question about any of these documents."
    )
    return "\n".join(lines)


def _register_rag(mcp: FastMCP, settings: Settings) -> None:
    @mcp.tool(
        name="ask_pinelabs_docs",
        description=(
            "Answer a free-form question about the Pine Labs SDK using "
            "Retrieval-Augmented Generation over the official docs. "
            "The answer is grounded in retrieved documentation chunks "
            "and includes inline citations like [api/init#0].\n\n"
            "Special intent: questions like 'list available documents', "
            "'what docs are available', or 'show all documents' are "
            "answered deterministically from the indexed routes — no "
            "LLM call — so the list is always accurate.\n\n"
            "Optional 'top_k' controls how many chunks are retrieved for "
            "regular questions (default 4, max 10)."
        ),
    )
    async def ask_pinelabs_docs(question: str, top_k: int = 4) -> dict[str, Any]:
        logger.info(
            "Tool invoked: ask_pinelabs_docs(question=%r, top_k=%d)",
            question,
            top_k,
        )
        if not question or not question.strip():
            return _text_response("Error: 'question' is required and cannot be empty.")
        top_k = max(1, min(int(top_k or 4), 10))

        try:
            store = await get_vector_store(settings)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to load vector store")
            return _text_response(f"Error preparing RAG store: {exc}")

        if not store.items:
            return _text_response(
                "RAG store is empty. Run the rag-rebuild pipeline first."
            )

        # Fast path: enumeration intent → answer deterministically from
        # the indexed routes, bypassing the LLM entirely. This avoids the
        # class of hallucinations where the model lists identifiers
        # mentioned in prose (e.g. `checkStatus`) as documented APIs.
        if _is_list_documents_query(question):
            logger.info("Intent: list documents (deterministic fast path)")
            return _text_response(_list_documents_response(store.items))

        try:
            result = await answer_question(
                question.strip(),
                store=store,
                settings=settings,
                top_k=top_k,
            )
        except (BedrockEmbeddingError, BedrockClaudeError) as exc:
            logger.warning("Bedrock error: %s", exc)
            return _text_response(f"Bedrock error: {exc}")

        sources_block = (
            "\n".join(
                f"- [{h.chunk.id}] score={h.score:.4f}  ({h.chunk.route})"
                for h in result.sources
            )
            or "(no sources)"
        )

        body = (
            "=== ANSWER (grounded in Pine Labs docs) ===\n"
            f"{result.answer}\n\n"
            "=== SOURCES ===\n"
            f"{sources_block}\n"
        )
        return _text_response(body)
