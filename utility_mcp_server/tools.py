"""All MCP tools for the utility server.

All documentation is sourced from the local on-disk ``docs/`` bundle. No
network calls are made.

Docs bundle layout::

    docs/
      get_documentation_list.json    ← master registry returned by
                                       ``get_documentation_list``
      doc_list/
        apis/<key>.md
        concepts/<key>.md
        models/<Name>.md
        languages/<binding>/{requirements,setup,integration,
                             examples,errors,distribution}.md
      sdk_list/<artifact>.zip

Tools exposed:

* ``get_sdk`` — return public SDK download URL(s) for the artifact(s) in
  ``docs/sdk_list/``.
* ``get_documentation_list`` — return the master registry JSON
  (``docs/get_documentation_list.json``). The client LLM should call this
  once per session and cache it.
* ``get_documentation`` — return the markdown body for a given api /
  concept / language / model by name. For language docs the key is
  ``<binding>/<file>`` (e.g. ``android/setup``).
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

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
def register(
    mcp: FastMCP,
    docs_dir: Path,
    sdk_dir: Path,
    sdk_download_base_url: str,
) -> None:
    """Attach all tools to the FastMCP server."""
    _register_documentation_list(mcp, docs_dir)
    _register_get_documentation(mcp, docs_dir)
    _register_sdk_download(mcp, docs_dir, sdk_dir, sdk_download_base_url)


# ---------------------------------------------------------------------------
# Combined listing tool
# ---------------------------------------------------------------------------
def _register_documentation_list(mcp: FastMCP, docs_dir: Path) -> None:
    index_path = docs_dir / _DOC_INDEX_FILENAME

    @mcp.tool(
        name="get_documentation_list",
        description=(
            "Return the master Pine Labs SDK documentation registry as JSON "
            "(schema_version, sdk metadata, mcp_setup, tools, key_registries, "
            "…). The client LLM SHOULD call this once per session and cache "
            "the result. Every valid 'name' / key for 'get_documentation' is "
            "discoverable from the returned payload (api_keys, model_keys, "
            "language_keys with '<binding>/<file>' shape, concept_keys)."
        ),
    )
    async def get_documentation_list() -> dict[str, Any]:
        logger.info(
            "Tool invoked: get_documentation_list (index=%s)", index_path
        )
        if not index_path.is_file():
            logger.error("Documentation registry not found at %s", index_path)
            return _text_response(
                f"Error: documentation registry not found at {index_path.name}."
            )
        try:
            payload = index_path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.exception("Failed to read %s", index_path)
            return _text_response(
                f"Error reading documentation registry: {exc}"
            )

        # Also surface the on-disk doc keys actually present, so callers can
        # cross-check the registry against what the server can serve.
        doc_root = _doc_list_dir(docs_dir)
        present_lines: list[str] = []
        for category in _DOC_CATEGORIES:
            keys = _list_md_keys(doc_root / category)
            present_lines.append(
                f"  {category} ({len(keys)}): "
                + (", ".join(keys) if keys else "(none)")
            )

        wrapped = (
            "=== PINE LABS SDK DOCUMENTATION REGISTRY (JSON) ===\n"
            f"{payload}\n"
            "=== ON-DISK DOC KEYS ===\n" + "\n".join(present_lines)
        )
        return _text_response(wrapped)


# ---------------------------------------------------------------------------
# get_documentation
# ---------------------------------------------------------------------------
def _register_get_documentation(mcp: FastMCP, docs_dir: Path) -> None:
    doc_root = _doc_list_dir(docs_dir)

    @mcp.tool(
        name="get_documentation",
        description=(
            "Fetch the OFFICIAL Pine Labs SDK documentation for a single "
            "entry by name. The 'name' may refer to an API, a model, a "
            "language guide, or a concept — the tool searches all "
            "categories and returns the matching markdown.\n\n"
            "Naming rules:\n"
            "- api / concept / model: a bare key (e.g. 'do_transaction', "
            "'lifecycle', 'TransactionRequest').\n"
            "- language: '<binding>/<file>' (e.g. 'android/setup', "
            "'jvm/integration'). Valid bindings and files are listed in "
            "get_documentation_list.\n\n"
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
            cat_dir = doc_root / cat
            resolved = _safe_join(cat_dir, cleaned)
            if resolved is not None:
                matches.append((cat, resolved))

        if not matches:
            # Case-insensitive fallback. Walks one level deep to also cover
            # the languages/<binding>/<file> shape.
            lowered = cleaned.lower()
            for cat in search_categories:
                cat_dir = doc_root / cat
                if not cat_dir.exists():
                    continue
                found: Path | None = None
                for entry in cat_dir.iterdir():
                    if (
                        entry.is_file()
                        and entry.suffix.lower() == ".md"
                        and entry.stem.lower() == lowered
                    ):
                        found = entry
                        break
                    if entry.is_dir():
                        for sub in entry.iterdir():
                            if (
                                sub.is_file()
                                and sub.suffix.lower() == ".md"
                                and f"{entry.name}/{sub.stem}".lower() == lowered
                            ):
                                found = sub
                                break
                        if found is not None:
                            break
                if found is not None:
                    matches.append((cat, found))

        if not matches:
            scope = ", ".join(search_categories)
            logger.warning("Documentation not found for %r in [%s]", cleaned, scope)
            return _text_response(
                f"Documentation '{name}' not found in [{scope}]. "
                "Use get_documentation_list to discover valid names."
            )

        if len(matches) > 1:
            def _label(cat: str, p: Path) -> str:
                # For nested doc_list/<cat>/<binding>/<file>.md, surface the
                # full key (<binding>/<stem>) so the caller can disambiguate.
                try:
                    rel = p.relative_to(doc_root / cat).with_suffix("")
                    return f"{cat}/{rel.as_posix()}"
                except ValueError:
                    return f"{cat}/{p.stem}"

            options = ", ".join(_label(cat, p) for cat, p in matches)
            return _text_response(
                f"Ambiguous name '{name}' matches multiple categories: "
                f"{options}. Re-run with the 'category' argument."
            )

        category_folder, doc_path = matches[0]
        try:
            doc_key = doc_path.relative_to(doc_root / category_folder).with_suffix("").as_posix()
        except ValueError:
            doc_key = doc_path.stem
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
            doc_key,
        )
        wrapped = (
            "=== AUTHORITATIVE PINE LABS SDK DOCUMENTATION ===\n"
            f"name: {doc_key}\n"
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

        if not _SAFE_TOKEN_RE.match(cleaned_key):
            return _text_response(
                f"Error: invalid artifact_key '{artifact_key}'. "
                "Allowed characters: letters, digits, '.', '-', '_'."
            )

        # Roadmap-only keys: explicit, friendly refusal so the client LLM
        # tells the user the binding isn't shipping yet.
        normalized_key = cleaned_key.lower()
        if normalized_key in _SDK_ROADMAP_KEYS:
            return _text_response(
                f"Artifact '{artifact_key}' is on the roadmap and is NOT "
                "shipping in the current release. No download link is "
                "available. See get_documentation_list -> "
                "key_registries.artifact_keys for status."
            )

        on_disk_prefix = _SDK_KEY_ALIASES.get(normalized_key)
        if on_disk_prefix is None:
            valid = sorted(registry_key_set | set(_SDK_KEY_ALIASES.keys()))
            return _text_response(
                f"Unknown artifact_key '{artifact_key}'. "
                f"Valid keys: {', '.join(valid)}."
            )

        # Resolve version. Explicit > registry default. Validated through
        # the same safe-token check as artifact_key.
        resolved_version = (version or "").strip() or default_version
        if not resolved_version:
            return _text_response(
                "Error: no 'version' provided and the registry does not "
                "declare sdk.current_version. Pass version explicitly."
            )
        if not _SAFE_TOKEN_RE.match(resolved_version):
            return _text_response(
                f"Error: invalid version '{version}'. "
                "Allowed characters: letters, digits, '.', '-', '_'."
            )

        filename = f"{on_disk_prefix}-{resolved_version}.zip"
        artifact_path = sdk_dir / filename
        if not artifact_path.is_file():
            available = ", ".join(p.name for p in _discover_sdks(sdk_dir))
            return _text_response(
                f"Artifact '{filename}' not found in the local SDK store. "
                f"Available: {available or '(none)'}."
            )

        size_bytes = artifact_path.stat().st_size
        url = f"{base}/{filename}"

        # Per ARTIFACT_STORE_FORMAT.md §11, v1 ships no integrity
        # sidecars: no sha256, no sigstore. Surface that explicitly so
        # the client LLM does not pretend a hash exists.
        install_hint = _install_hint_for(on_disk_prefix, resolved_version)

        body = (
            "=== PINE LABS SDK DOWNLOAD ===\n"
            f"artifact_key: {cleaned_key}\n"
            f"resolved_to:  {on_disk_prefix}\n"
            f"version:      {resolved_version}\n"
            f"filename:     {filename}\n"
            f"size_bytes:   {size_bytes}\n"
            f"size:         {size_bytes / 1024:,.1f} KB\n"
            f"url:          {url}\n"
            "sha256:       (not shipped in v1; see ARTIFACT_STORE_FORMAT.md §11)\n"
            "license:      Pine Labs proprietary — distribute via Pinelabs only\n"
            "\n"
            "install_hint:\n"
            f"{install_hint}"
        )
        return _text_response(body)


def _install_hint_for(on_disk_prefix: str, version: str) -> str:
    """Per-binding install snippet, mirroring the spec §4 example."""
    if on_disk_prefix == "android-kotlin":
        return (
            "  // 1. Unzip and copy payload/pine-billing-sdk-"
            + version
            + ".aar into <module>/libs/\n"
            "  // 2. In <module>/build.gradle.kts:\n"
            "  repositories { flatDir { dirs(\"libs\") } }\n"
            "  dependencies { implementation(files(\"libs/pine-billing-sdk-"
            + version
            + ".aar\")) }"
        )
    if on_disk_prefix == "jvm-java":
        return (
            "  // 1. Unzip and put payload/pine-billing-sdk-"
            + version
            + ".jar on the classpath\n"
            "  // 2. Ensure JNA 5.14+ is on the classpath at runtime\n"
            "  // 3. Launch via:  java -cp pine-billing-sdk-"
            + version
            + ".jar:jna-5.14.0.jar your.Main"
        )
    return "  (See the README.md inside the zip for installation steps.)"
