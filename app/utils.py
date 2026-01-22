from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    # app/utils.py -> app/ -> project root
    return Path(__file__).resolve().parent.parent
