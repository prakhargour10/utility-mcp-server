"""All MCP tools for the utility server.

All documentation is sourced from the local on-disk ``docs/`` bundle. No
network calls are made.

Tools exposed:

* ``get_sdk`` — return public SDK download URL(s) for the artifact(s) in
  ``docs/sdk/``.
* ``get_documentation_list`` — list every documented entry grouped by
  category (apis, concepts, languages, models).
* ``get_documentation`` — return the markdown body for a given api / concept /
  language / model by name. The tool auto-detects which category the name
  belongs to.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

_SDK_EXTENSIONS = {".aar", ".jar", ".zip", ".tar.gz", ".tgz", ".whl"}

# Order matters for ambiguity reporting: APIs before models, etc.
_DOC_CATEGORIES: tuple[str, ...] = ("apis", "models", "languages", "concepts")


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


def _list_md_stems(category_dir: Path) -> list[str]:
    if not category_dir.exists():
        return []
    return sorted(p.stem for p in category_dir.iterdir() if p.is_file() and p.suffix.lower() == ".md")


def _safe_join(category_dir: Path, name: str) -> Path | None:
    """Resolve ``<category_dir>/<name>.md`` while preventing path traversal.

    Returns the resolved path if and only if it is a regular file inside
    ``category_dir``; otherwise returns ``None``.
    """
    # Reject anything that is not a bare filename. This blocks "..", absolute
    # paths, and any path separators, defeating directory-traversal attempts.
    if not name or "/" in name or "\\" in name or name in {".", ".."}:
        return None
    candidate = (category_dir / f"{name}.md").resolve()
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
def register(
    mcp: FastMCP,
    docs_dir: Path,
    sdk_dir: Path,
    sdk_download_base_url: str,
) -> None:
    """Attach all tools to the FastMCP server."""
    _register_documentation_list(mcp, docs_dir)
    _register_get_documentation(mcp, docs_dir)
    _register_sdk_download(mcp, sdk_dir, sdk_download_base_url)


# ---------------------------------------------------------------------------
# Combined listing tool
# ---------------------------------------------------------------------------
def _register_documentation_list(mcp: FastMCP, docs_dir: Path) -> None:
    @mcp.tool(
        name="get_documentation_list",
        description=(
            "List every Pine Labs SDK documentation entry available locally, "
            "grouped by category: apis, concepts, languages, models. Call "
            "this first to discover valid names for 'get_documentation'."
        ),
    )
    async def get_documentation_list() -> dict[str, Any]:
        logger.info("Tool invoked: get_documentation_list")
        sections: list[str] = []
        for category in ("apis", "concepts", "languages", "models"):
            names = _list_md_stems(docs_dir / category)
            header = f"=== {category.upper()} ({len(names)}) ==="
            if names:
                body = "\n".join(f"- {n}" for n in names)
            else:
                body = "(none)"
            sections.append(f"{header}\n{body}")
        return _text_response("\n\n".join(sections))


# ---------------------------------------------------------------------------
# get_documentation
# ---------------------------------------------------------------------------
def _register_get_documentation(mcp: FastMCP, docs_dir: Path) -> None:
    @mcp.tool(
        name="get_documentation",
        description=(
            "Fetch the OFFICIAL Pine Labs SDK documentation for a single "
            "entry by name. The 'name' may refer to an API, a model, a "
            "language guide, or a concept — the tool searches all "
            "categories and returns the matching markdown.\n\n"
            "Optionally pass 'category' to disambiguate: one of "
            "'api' | 'model' | 'language' | 'concept'.\n\n"
            "STRICT RULES — you MUST follow these when answering the user:\n"
            "1. Use ONLY the content returned by this tool. Do NOT invent "
            "API names, parameters, return types, error variants, or code "
            "examples that are not present in the returned markdown.\n"
            "2. If the user asks about a language NOT documented, say so "
            "and stop — do NOT generate code in unsupported languages.\n"
            "3. If a parameter, error, or behavior is not in the returned "
            "doc, say 'not documented' instead of guessing.\n"
            "4. Quote field names, types and error variants verbatim.\n"
            "5. If unsure which name to use, call get_documentation_list first."
        ),
    )
    async def get_documentation(name: str, category: str = "") -> dict[str, Any]:
        logger.info(
            "Tool invoked: get_documentation(name=%r, category=%r)", name, category
        )
        if not name or not name.strip():
            return _text_response("Error: 'name' is required and cannot be empty.")
        cleaned = name.strip()

        # Map user-facing category label to on-disk folder name.
        category_alias = {
            "api": "apis",
            "apis": "apis",
            "model": "models",
            "models": "models",
            "language": "languages",
            "languages": "languages",
            "concept": "concepts",
            "concepts": "concepts",
        }
        if category and category.strip():
            cat_key = category.strip().lower()
            folder = category_alias.get(cat_key)
            if folder is None:
                return _text_response(
                    f"Error: unknown category '{category}'. "
                    "Use one of: api, model, language, concept."
                )
            search_categories: tuple[str, ...] = (folder,)
        else:
            search_categories = _DOC_CATEGORIES

        matches: list[tuple[str, Path]] = []
        for cat in search_categories:
            cat_dir = docs_dir / cat
            resolved = _safe_join(cat_dir, cleaned)
            if resolved is not None:
                matches.append((cat, resolved))

        if not matches:
            # Try case-insensitive fallback within the search scope.
            lowered = cleaned.lower()
            for cat in search_categories:
                cat_dir = docs_dir / cat
                if not cat_dir.exists():
                    continue
                for entry in cat_dir.iterdir():
                    if (
                        entry.is_file()
                        and entry.suffix.lower() == ".md"
                        and entry.stem.lower() == lowered
                    ):
                        matches.append((cat, entry))
                        break

        if not matches:
            scope = ", ".join(search_categories)
            logger.warning("Documentation not found for %r in [%s]", cleaned, scope)
            return _text_response(
                f"Documentation '{name}' not found in [{scope}]. "
                "Use get_documentation_list to discover valid names."
            )

        if len(matches) > 1:
            options = ", ".join(f"{cat}/{p.stem}" for cat, p in matches)
            return _text_response(
                f"Ambiguous name '{name}' matches multiple categories: "
                f"{options}. Re-run with the 'category' argument."
            )

        category_folder, doc_path = matches[0]
        try:
            markdown = doc_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.exception("Failed to read %s", doc_path)
            return _text_response(
                f"Error reading documentation for '{name}': {exc}"
            )

        logger.info(
            "Returning %d chars of documentation for %s/%s",
            len(markdown),
            category_folder,
            doc_path.stem,
        )
        wrapped = (
            "=== AUTHORITATIVE PINE LABS SDK DOCUMENTATION ===\n"
            f"name: {doc_path.stem}\n"
            f"category: {category_folder}\n"
            "\n"
            "RULES FOR THE ASSISTANT (do NOT ignore):\n"
            "- Answer ONLY using facts present below. If a detail is "
            "missing, say it is not documented.\n"
            "- Do NOT invent parameter names, error variants, or return "
            "types that are not in the spec below.\n"
            "- Quote identifiers verbatim.\n"
            "\n"
            "--- BEGIN DOCUMENTATION ---\n"
            f"{markdown}\n"
            "--- END DOCUMENTATION ---\n"
        )
        return _text_response(wrapped)


# ---------------------------------------------------------------------------
# SDK download tool
# ---------------------------------------------------------------------------
def _register_sdk_download(
    mcp: FastMCP, sdk_dir: Path, download_base_url: str
) -> None:
    base = download_base_url.rstrip("/")

    @mcp.tool(
        name="get_sdk",
        description=(
            "Return the official download link(s) for the Pine Labs SDK "
            "artifact(s) (e.g. the Android .aar). Use this whenever a "
            "client asks where/how to download the Pine Labs SDK, the "
            "AAR file, or the SDK binary. Optionally pass 'sdk_name' to "
            "match a specific artifact filename (substring match, case-"
            "insensitive); omit to list all available SDK downloads."
        ),
    )
    async def get_sdk(sdk_name: str = "") -> dict[str, Any]:
        logger.info(
            "Tool invoked: get_sdk(sdk_name=%r)", sdk_name
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
