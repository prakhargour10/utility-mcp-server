"""Thin entrypoint. The real server lives in ``utility_mcp_server``.

Kept at the repo root so existing deployment commands (``python main.py``
and uvicorn ``main:app``) continue to work unchanged.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make ``src`` importable when running directly (no editable install).
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from utility_mcp_server import build_app  # noqa: E402
from utility_mcp_server.config import get_settings  # noqa: E402

app = build_app()


def main() -> None:
    import uvicorn

    settings = get_settings()
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run("main:app", host=settings.host, port=port)


if __name__ == "__main__":
    main()
