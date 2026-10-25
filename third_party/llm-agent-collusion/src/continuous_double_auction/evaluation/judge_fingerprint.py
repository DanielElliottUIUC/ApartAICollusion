"""
Judge fingerprints (ApartAICollusion sprint addition, Oct 2026; not part of the original harness).

A fingerprint is a short hash of everything that determines what an LLM judge outputs: judge kind, model id,
temperature, the exact template text, what the judge is shown (its "view") and the version of the code that
builds its input. Judge outputs are stored under their fingerprint, so a changed judge can never silently reuse
scores produced by an older one. Freezing the judge before the main runs (README "Design rules") means freezing
this hash; report it with the results.
"""

import hashlib
import json
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "prompt_templates"

# Bump when the code that turns logs into judge input changes in a way the templates don't show.
JUDGE_INPUT_VERSION = 2  # 1 = original harness (reasoning fields only); 2 = adds messages and DM threads

SELLER_TEMPLATE = "seller_individual_eval.jinja2"
THREAD_TEMPLATE = "dm_thread_eval.jinja2"
DG_TEMPLATE = "seller_dg_eval.jinja2"  # D-G seller judge: offer acceptance, suspicion, cross-talk
SELLER_VIEWS = ("messages", "reasoning")  # "reasoning" reproduces the original harness judge's input


def fingerprint(kind: str, model: str, temperature: float, template: str, view: str = "") -> str:
    """12-hex-digit hash of the judge configuration."""
    payload = {
        "kind": kind,
        "model": model,
        "temperature": temperature,
        # CRLF -> LF: a Windows checkout (git autocrlf) and a Linux one must give the same fingerprint
        "template_sha256": hashlib.sha256((TEMPLATE_DIR / template).read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "view": view,
        "input_version": JUDGE_INPUT_VERSION,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]
