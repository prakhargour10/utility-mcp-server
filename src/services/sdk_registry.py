"""Discovery of downloadable SDK artifacts on disk."""

from __future__ import annotations

from pathlib import Path

from ..config import settings


_SDK_EXTS = {".aar", ".jar", ".zip", ".tgz", ".whl"}


def discover_sdks() -> list[Path]:
    """Return all downloadable SDK artifacts present in the configured sdk/ folder."""
    root = settings.sdk_root
    if not root.exists():
        return []
    return sorted(
        p
        for p in root.iterdir()
        if p.is_file()
        and (p.suffix.lower() in _SDK_EXTS or p.name.lower().endswith(".tar.gz"))
    )
