"""All MCP tools for the utility server.

Exposes exactly two tools:

* ``get_pinelabs_sdk_download_link`` — return public SDK download URL(s).
* ``ask_pinelabs_docs`` — RAG-grounded Q&A over the Pine Labs docs.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .rag.generate import answer_question
from .rag.store import get_vector_store

logger = logging.getLogger(__name__)

_SDK_EXTENSIONS = {".aar", ".jar", ".zip", ".tar.gz", ".tgz", ".whl"}

# Subdirectory under ``docs_dir`` that holds the markdown corpus.
_DOC_LIST_SUBDIR = "doc_list"

# Filename of the master registry under ``docs_dir``.
_DOC_INDEX_FILENAME = "get_documentation_list.json"

# Order matters for ambiguity reporting: APIs before models, etc.
_DOC_CATEGORIES: tuple[str, ...] = ("apis", "models", "languages", "concepts")

# Allowed characters for a single path segment in a doc key. Blocks any
# traversal sequence (``..``) and shell/path metacharacters.
_SAFE_SEGMENT_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")


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


def _doc_list_dir(docs_dir: Path) -> Path:
    return docs_dir / _DOC_LIST_SUBDIR


def _list_md_keys(category_dir: Path) -> list[str]:
    """List doc keys under a category directory.

    For flat categories (apis/concepts/models) the key is the markdown
    file's stem (e.g. ``do_transaction``). For nested categories
    (languages/<binding>/<file>.md) the key is ``<binding>/<stem>``.
    """
    if not category_dir.exists():
        return []
    keys: list[str] = []
    for entry in sorted(category_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() == ".md":
            keys.append(entry.stem)
        elif entry.is_dir():
            for sub in sorted(entry.iterdir()):
                if sub.is_file() and sub.suffix.lower() == ".md":
                    keys.append(f"{entry.name}/{sub.stem}")
    return keys


def _safe_join(category_dir: Path, name: str) -> Path | None:
    """Resolve ``<category_dir>/<name>.md`` while preventing path traversal.

    ``name`` may contain at most one forward slash, used for nested
    categories such as ``languages/<binding>/<file>``. Backslashes,
    absolute paths, multiple slashes, ``.`` / ``..`` segments, and any
    metacharacter outside ``[A-Za-z0-9_.\\-]`` are rejected.

    Returns the resolved path iff it is a regular file inside
    ``category_dir``; otherwise ``None``.
    """
    if not name or "\\" in name:
        return None
    parts = name.split("/")
    if len(parts) > 2:
        return None
    if any(part in ("", ".", "..") or not _SAFE_SEGMENT_RE.match(part) for part in parts):
        return None

    candidate = (category_dir.joinpath(*parts[:-1]) / f"{parts[-1]}.md").resolve()
    try:
        candidate.relative_to(category_dir.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return candidate


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register(mcp: FastMCP, settings: Settings) -> None:
    """Attach all tools to the FastMCP server."""
    _register_sdk_download(mcp, settings.sdk_dir, settings.sdk_download_base_url)
    _register_rag(mcp, settings)


def _suggest_doc_keys(
    rag_loader,
    query: str,
    *,
    category_filter: str | None = None,
    limit: int = 5,
) -> list[tuple[str, str, float]]:
    """Return ``[(category, doc_key, score), ...]`` deduped suggestions."""
    rag = rag_loader()
    if rag is None:
        return []
    try:
        hits = rag.search(
            query, top_k=limit * 3, category=category_filter
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("RAG suggest failed: %s", exc)
        return []
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str, float]] = []
    for h in hits:
        key = (h.category, h.doc_key)
        if key in seen:
            continue
        seen.add(key)
        out.append((h.category, h.doc_key, h.score))
        if len(out) >= limit:
            break
    return out


# ---------------------------------------------------------------------------
# search_documentation (RAG)
# ---------------------------------------------------------------------------
def _register_search_documentation(
    mcp: FastMCP,
    rag_loader,
    *,
    default_top_k: int,
) -> None:
    """Register the semantic-search tool over the docs corpus."""

    category_alias = {
        "": None,
        "api": "apis",
        "apis": "apis",
        "model": "models",
        "models": "models",
        "language": "languages",
        "languages": "languages",
        "concept": "concepts",
        "concepts": "concepts",
    }

    @mcp.tool(
        name="search_documentation",
        description=(
            "Semantic search across the Pine Labs SDK documentation "
            "corpus (APIs, models, language guides, concepts) using a "
            "local FAISS vector index. Use this when the user describes "
            "a behaviour, error, or concept in natural language and you "
            "do NOT yet know the exact doc key.\n\n"
            "Args:\n"
            "  query (required): natural-language search phrase.\n"
            "  top_k (optional, default 5): number of hits to return "
            "(clamped to 1..20).\n"
            "  category (optional): one of 'api', 'model', 'language', "
            "'concept' to restrict the search.\n\n"
            "Returns: a ranked list of matches with category, doc_key, "
            "heading, similarity score, and a short snippet. After "
            "choosing a hit, call get_documentation(name=<doc_key>, "
            "category=<category>) to retrieve the full authoritative "
            "markdown.\n\n"
            "STRICT RULES:\n"
            "1. Snippets are TRUNCATED for display only — do NOT answer "
            "the user from a snippet alone. Always follow up with "
            "get_documentation for the full body.\n"
            "2. Do NOT invent doc_keys. Only use values returned by this "
            "tool or by get_documentation_list."
        ),
    )
    async def search_documentation(
        query: str,
        top_k: int = default_top_k,
        category: str = "",
    ) -> dict[str, Any]:
        logger.info(
            "Tool invoked: search_documentation(query=%r, top_k=%r, category=%r)",
            query,
            top_k,
            category,
        )
        if not query or not query.strip():
            return _text_response("Error: 'query' is required and cannot be empty.")

        cat_key = (category or "").strip().lower()
        if cat_key not in category_alias:
            return _text_response(
                f"Error: unknown category '{category}'. "
                "Use one of: api, model, language, concept (or omit)."
            )
        cat_folder = category_alias[cat_key]

        # Clamp top_k defensively.
        try:
            k = int(top_k)
        except (TypeError, ValueError):
            k = default_top_k
        k = max(1, min(k, 20))

        rag = rag_loader()
        if rag is None:
            return _text_response(
                "Error: RAG index is not available on this server. "
                "Ask the operator to run "
                "`python -m utility_mcp_server.rag.build_index`."
            )

        try:
            hits = rag.search(query.strip(), top_k=k, category=cat_folder)
        except Exception as exc:  # noqa: BLE001
            logger.exception("search_documentation failed")
            return _text_response(f"Error during semantic search: {exc}")

        if not hits:
            scope = cat_folder or "all categories"
            return _text_response(
                f"No matches for '{query}' in {scope}. "
                "Try rephrasing or removing the category filter."
            )

        lines = [
            "=== PINE LABS SDK SEMANTIC SEARCH RESULTS ===",
            f"query: {query}",
            f"top_k: {k}"
            + (f"  category: {cat_folder}" if cat_folder else ""),
            f"index_size: {rag.size} chunks  model: {rag.model_name}",
            "",
            "RULES FOR THE ASSISTANT:",
            "- These are RANKED candidates with TRUNCATED snippets.",
            "- To answer the user, call get_documentation(name=<doc_key>, "
            "category=<category>) for the most relevant hit(s) and use "
            "the full markdown returned there.",
            "- Do NOT answer from snippets alone.",
            "",
            "--- BEGIN HITS ---",
        ]
        for rank, h in enumerate(hits, start=1):
            lines.append(
                f"[{rank}] score={h.score:.4f}  category={h.category}  "
                f"doc_key={h.doc_key}"
                + (f"  heading={h.heading!r}" if h.heading else "")
            )
            lines.append(f"    snippet: {h.snippet}")
            lines.append("")
        lines.append("--- END HITS ---")
        return _text_response("\n".join(lines))


# ---------------------------------------------------------------------------
# SDK download tool
# ---------------------------------------------------------------------------
# Maps the registry-facing artifact_key (as listed in
# get_documentation_list.json -> key_registries.artifact_keys) to the
# on-disk filename prefix used in docs/sdk_list/, which follows the
# ARTIFACT_STORE_FORMAT.md §2 convention "<binding>-<lang>".
#
# Both registry keys ("android-aar") and on-disk prefixes
# ("android-kotlin") are accepted as input, plus a few short aliases
# the user is likely to type ("android", "jvm", "java").
_SDK_KEY_ALIASES: dict[str, str] = {
    # registry artifact_keys (shipping)
    "android-aar": "android-kotlin",
    "jvm-jar": "jvm-java",
    # on-disk / spec-§2 keys (identity)
    "android-kotlin": "android-kotlin",
    "jvm-java": "jvm-java",
    # short aliases
    "android": "android-kotlin",
    "kotlin": "android-kotlin",
    "java-android": "android-kotlin",
    "jvm": "jvm-java",
    "java": "jvm-java",
    "kotlin-jvm": "jvm-java",
    "java-jvm": "jvm-java",
}

# Roadmap-only artifact keys (declared in the registry but not yet
# shipping). We surface a clear "not shipping" message instead of a 404
# so the LLM can tell the user before generating any code.
_SDK_ROADMAP_KEYS: frozenset[str] = frozenset(
    {
        "ios-xcframework",
        "python-wheel-manylinux-x86_64",
        "python-wheel-manylinux-aarch64",
        "python-wheel-macos-x86_64",
        "python-wheel-macos-arm64",
        "python-wheel-windows-x86_64",
        "nodejs-npm",
        "c-linux-x86_64",
        "c-linux-aarch64",
        "c-macos-universal",
        "c-windows-x86_64",
    }
)


def _load_doc_registry(docs_dir: Path) -> dict[str, Any]:
    """Read get_documentation_list.json and return parsed JSON, or {}.

    Reads on every call (the file is small and rarely accessed compared
    to RAG queries); avoids subtle staleness if the bundle is updated
    while the process runs.
    """
    index_path = docs_dir / _DOC_INDEX_FILENAME
    if not index_path.is_file():
        return {}
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Failed to parse %s: %s", index_path, exc)
        return {}


def _registry_artifact_keys(registry: dict[str, Any]) -> list[dict[str, Any]]:
    return list(
        ((registry.get("key_registries") or {}).get("artifact_keys") or [])
    )


def _registry_current_version(registry: dict[str, Any]) -> str | None:
    sdk = registry.get("sdk") or {}
    ver = sdk.get("current_version")
    return ver if isinstance(ver, str) and ver.strip() else None


# Allowed shape for an artifact_key / version: lowercase letters, digits,
# dot, dash, underscore. Blocks any path traversal or shell metacharacter
# in the value used to build a filename + URL.
_SAFE_TOKEN_RE = re.compile(r"^[A-Za-z0-9._\-]+$")


def _register_sdk_download(
    mcp: FastMCP,
    docs_dir: Path,
    sdk_dir: Path,
    download_base_url: str,
) -> None:
    base = download_base_url.rstrip("/")

    @mcp.tool(
        name="get_sdk",
        description=(
            "Resolve a downloadable Pine Labs SDK artifact for a given "
            "target.\n\n"
            "Args:\n"
            "  artifact_key (optional): one of the keys listed in "
            "get_documentation_list -> key_registries.artifact_keys "
            "(e.g. 'android-aar', 'jvm-jar'). Short aliases also "
            "accepted: 'android', 'jvm', 'java'. If omitted, every "
            "shipping artifact currently on disk is listed.\n"
            "  version (optional): defaults to "
            "sdk.current_version from the registry.\n\n"
            "Returns: a structured block with the resolved filename, "
            "size, full HTTPS download URL, and an install hint. Roadmap-"
            "only keys return a clear 'not shipping' notice instead of a "
            "URL. Never invent or guess an artifact key — call "
            "get_documentation_list first if unsure."
        ),
    )
    async def get_sdk(
        artifact_key: str = "",
        version: str = "",
    ) -> dict[str, Any]:
        logger.info(
            "Tool invoked: get_sdk(artifact_key=%r, version=%r)",
            artifact_key,
            version,
        )

        registry = _load_doc_registry(docs_dir)
        registry_keys = _registry_artifact_keys(registry)
        registry_key_set = {
            entry.get("key") for entry in registry_keys if entry.get("key")
        }
        default_version = _registry_current_version(registry)

        # No artifact_key -> list every shipping zip on disk. Useful for
        # discovery and keeps backward compatibility with the previous
        # behaviour.
        cleaned_key = (artifact_key or "").strip()
        if not cleaned_key:
            sdks = _discover_sdks(sdk_dir)
            if not sdks:
                return _text_response(
                    "No SDK artifacts are currently published on this server."
                )
            lines = ["=== PINE LABS SDK DOWNLOAD LINKS (all shipping) ==="]
            for p in sdks:
                size_kb = p.stat().st_size / 1024
                url = f"{base}/{p.name}"
                lines.append(f"- {p.name} ({size_kb:,.1f} KB)\n  {url}")
            if default_version:
                lines.append(f"\nRegistry current_version: {default_version}")
            return _text_response("\n".join(lines))

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
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("RAG retrieval failed")
            return _text_response(f"Error: {exc}")

        sources_block = (
            "\n".join(
                f"- [{h.chunk.id}] score={h.score:.4f}  ({h.chunk.route})"
                for h in result.sources
            )
            or "(no sources)"
        )

        body = (
            "=== RETRIEVED CHUNKS (Pine Labs docs, FAISS) ===\n"
            f"{result.answer}\n\n"
            "=== SOURCES ===\n"
            f"{sources_block}\n"
        )
        return _text_response(body)
