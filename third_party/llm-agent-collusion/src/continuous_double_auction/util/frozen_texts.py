"""
Frozen prompt texts for the D–G arms (ApartAICollusion sprint addition, Oct 2026; not part of the original harness).

The texts live as plain files in the sprint repo's `configs/texts/` (warning.txt, precedent.txt, sham_history.txt,
buyer_plea_human.txt) so they can be frozen, diffed and quoted in the report. They are read verbatim, minus
surrounding whitespace.
"""

import hashlib
import re
from functools import lru_cache
from pathlib import Path

# <repo>/third_party/llm-agent-collusion/src/continuous_double_auction/util/frozen_texts.py -> <repo>/configs/texts
TEXTS_DIR = Path(__file__).resolve().parents[5] / "configs" / "texts"

_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def text_path(name: str) -> Path:
    """Path of the frozen text `name` (a bare file stem such as "warning"; no paths or extensions)."""
    if not _NAME.match(name or ""):
        raise ValueError(f"frozen text name must be a bare file stem like 'buyer_plea_human', got {name!r}")
    return TEXTS_DIR / f"{name}.txt"


@lru_cache(maxsize=None)
def load_text(name: str) -> str:
    path = text_path(name)
    if not path.is_file():
        raise ValueError(f"frozen text {name!r} not found at {path}")
    return path.read_text(encoding="utf-8").strip()


def text_sha256(name: str) -> str:
    """Hash of the text as rendered, recorded in run metadata so results can be tied to a frozen version."""
    return hashlib.sha256(load_text(name).encode("utf-8")).hexdigest()[:12]
