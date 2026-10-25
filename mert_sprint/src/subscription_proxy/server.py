#!/usr/bin/env python3
"""
Portable OpenAI-compatible HTTP proxy server (http://127.0.0.1:8787/v1) that routes
chat/completions and responses calls to signed-in local CLI subscriptions ($0 API cost):
  - codex  -> OpenAI GPT-5.6 / GPT-6 / GPT-6.1 models
  - claude -> Anthropic Claude 5.5 (haiku-5-5, sonnet-5-5, opus-5-5, fable-5-1) & 4.5/4.6 models
  - agy    -> Gemini 3.8 Flash / Gemini 4 Argon & Claude 5.5 models
  - grok   -> xAI Grok models (grok CLI on a grok.com login serves grok-4.5, grok-4.6, grok-4.7-build-fast, grok-4.7; 4.7 last because it is slow)

Also records every call to <repo_root>/token-usage/proxy_usage.jsonl for LEDGER.md tracking.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
USAGE_DIR = REPO_ROOT / "token-usage"
USAGE_DIR.mkdir(parents=True, exist_ok=True)
# Each machine can log to its own file (run_all.sh sets proxy_usage.<shard>.jsonl) so git pushes never conflict.
PROXY_USAGE_LOG = Path(os.environ.get("PROXY_USAGE_LOG") or USAGE_DIR / "proxy_usage.jsonl")
USAGE_LOCK = threading.Lock()


def find_cli(name: str, extra_paths: List[str]) -> str:
    found = shutil.which(name)
    if found:
        return found
    for p in extra_paths:
        expanded = os.path.expanduser(p)
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            return expanded
    return name


CODEX_BIN = find_cli("codex", ["~/.local/bin/codex", "/opt/homebrew/bin/codex", "/usr/local/bin/codex"])
CLAUDE_BIN = find_cli("claude", ["~/.local/bin/claude", "/opt/homebrew/bin/claude", "/usr/local/bin/claude"])
AGY_BIN = find_cli("agy", ["~/.local/bin/agy", "/opt/homebrew/bin/agy", "/usr/local/bin/agy"])
GROK_BIN = find_cli("grok", ["~/.local/bin/grok", "~/.grok/bin/grok", "/opt/homebrew/bin/grok", "/usr/local/bin/grok"])

TMP_BASE = Path(tempfile.gettempdir())
EMPTY_WORKDIR = TMP_BASE / "subproxy_empty"
SCRATCH_DIR = TMP_BASE / "subproxy_work"
EMPTY_WORKDIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_SYSTEM_PROMPT = (
    "You are an autonomous decision-making agent in an economic market simulation experiment. "
    "Follow the user prompt instructions and output format strictly."
)

# Ordered sweep list for Grok: all pre-4.7 models first, then grok-4.7 last (since 4.7 is slower)
GROK_SWEEP_ORDER: List[str] = ["grok-4.5", "grok-4.6", "grok-4.7-build-fast", "grok-4.7"]

# Map requested model IDs (including OpenRouter / Nebius / paper aliases) -> (cli, target_model, effort)
MODEL_MAP: Dict[str, Tuple[str, str, str]] = {
    # Direct Codex subscription models
    "gpt-6-luna": ("codex", "gpt-6-luna", "low"),
    "gpt-5.6-luna": ("codex", "gpt-5.6-luna", "low"),
    "gpt-5.6-terra": ("codex", "gpt-5.6-terra", "low"),
    "gpt-5.6-sol": ("codex", "gpt-5.6-sol", "low"),
    "gpt-6-sol": ("codex", "gpt-6-sol", "low"),
    "gpt-6.1-sol": ("codex", "gpt-6.1-sol", "low"),
    "gpt-6-astra": ("codex", "gpt-6-astra", "low"),
    "gpt-reserve": ("codex", "gpt-reserve", "low"),
    # Requested OpenAI / paper aliases -> Codex subscription models
    "gpt-5.4-mini": ("codex", "gpt-6-luna", "low"),
    "openai/gpt-5.4-mini": ("codex", "gpt-6-luna", "low"),
    "gpt-5.4": ("codex", "gpt-5.6-sol", "low"),
    "openai/gpt-5.4": ("codex", "gpt-5.6-sol", "low"),
    "gpt-5.5": ("codex", "gpt-6-sol", "low"),
    "openai/gpt-5.5": ("codex", "gpt-6-sol", "low"),
    "openai/gpt-5.6-sol": ("codex", "gpt-5.6-sol", "low"),
    "openai/gpt-6-luna": ("codex", "gpt-6-luna", "low"),
    "openai/gpt-6.1-sol": ("codex", "gpt-6.1-sol", "low"),
    # Claude 5.5 (current default generation on Claude Code 2.1.309+)
    "haiku": ("claude", "claude-haiku-5-5", "low"),
    "claude-haiku-5-5": ("claude", "claude-haiku-5-5", "low"),
    "claude-haiku-5.5": ("claude", "claude-haiku-5-5", "low"),
    "anthropic/claude-haiku-5-5": ("claude", "claude-haiku-5-5", "low"),
    "anthropic/claude-haiku-5.5": ("claude", "claude-haiku-5-5", "low"),
    "claude-3-5-haiku-latest": ("claude", "claude-haiku-5-5", "low"),
    "anthropic/claude-3.5-haiku": ("claude", "claude-haiku-5-5", "low"),
    "claude": ("claude", "claude-sonnet-5-5", "low"),
    "sonnet": ("claude", "claude-sonnet-5-5", "low"),
    "claude-sonnet-5-5": ("claude", "claude-sonnet-5-5", "low"),
    "claude-sonnet-5.5": ("claude", "claude-sonnet-5-5", "low"),
    "anthropic/claude-sonnet-5-5": ("claude", "claude-sonnet-5-5", "low"),
    "anthropic/claude-sonnet-5.5": ("claude", "claude-sonnet-5-5", "low"),
    "claude-3-7-sonnet-latest": ("claude", "claude-sonnet-5-5", "low"),
    "anthropic/claude-3.7-sonnet": ("claude", "claude-sonnet-5-5", "low"),
    "claude-3-5-sonnet-latest": ("claude", "claude-sonnet-5-5", "low"),
    "anthropic/claude-3.5-sonnet": ("claude", "claude-sonnet-5-5", "low"),
    "opus": ("claude", "claude-opus-5-5", "low"),
    "claude-opus-5-5": ("claude", "claude-opus-5-5", "low"),
    "claude-opus-5.5": ("claude", "claude-opus-5-5", "low"),
    "anthropic/claude-opus-5-5": ("claude", "claude-opus-5-5", "low"),
    "anthropic/claude-opus-5.5": ("claude", "claude-opus-5-5", "low"),
    "fable": ("claude", "claude-fable-5-1", "low"),
    "claude-fable-5-1": ("claude", "claude-fable-5-1", "low"),
    "anthropic/claude-fable-5-1": ("claude", "claude-fable-5-1", "low"),
    # Explicit legacy Claude 4.5 / 4.6 slugs (kept for side-by-side generational comparisons)
    "claude-haiku-4-5": ("claude", "claude-haiku-4-5", "low"),
    "anthropic/claude-haiku-4-5": ("claude", "claude-haiku-4-5", "low"),
    "anthropic/claude-haiku-4.5": ("claude", "claude-haiku-4-5", "low"),
    "claude-sonnet-4-6": ("claude", "claude-sonnet-4-6", "low"),
    "anthropic/claude-sonnet-4-6": ("claude", "claude-sonnet-4-6", "low"),
    "claude-sonnet-4.5": ("claude", "claude-sonnet-4-6", "low"),
    "anthropic/claude-sonnet-4.5": ("claude", "claude-sonnet-4-6", "low"),
    # Agy CLI models (Gemini 3.8 / 4 Argon & Claude 5.5)
    "gemini-3.8-flash-low": ("agy", "gemini-3.8-flash-low", "low"),
    "gemini-3.8-flash": ("agy", "gemini-3.8-flash-low", "low"),
    "google/gemini-3.8-flash": ("agy", "gemini-3.8-flash-low", "low"),
    "google/gemini-3.8-flash-low": ("agy", "gemini-3.8-flash-low", "low"),
    "gemini-3.8-flash-medium": ("agy", "gemini-3.8-flash-medium", "medium"),
    "gemini-4-argon-low": ("agy", "gemini-4-argon-low", "low"),
    "claude-sonnet-5-5-low": ("agy", "claude-sonnet-5-5-low", "low"),
    "claude-opus-5-5-low": ("agy", "claude-opus-5-5-low", "low"),
    "gpt-oss-120b-medium": ("agy", "gpt-oss-120b-medium", "medium"),
    # Grok CLI models: pre-4.7 models first (4.20, 4.3, 4.5, 4.6), then grok-4.7 last (slow)
    "grok-4.20": ("grok", "grok-4.20", "low"),
    "x-ai/grok-4.20": ("grok", "grok-4.20", "low"),
    "grok-4.20-multi-agent": ("grok", "grok-4.20-multi-agent", "low"),
    "x-ai/grok-4.20-multi-agent": ("grok", "grok-4.20-multi-agent", "low"),
    "grok-4.3": ("grok", "grok-4.3", "low"),
    "x-ai/grok-4.3": ("grok", "grok-4.3", "low"),
    "grok-4.5": ("grok", "grok-4.5", "low"),
    "x-ai/grok-4.5": ("grok", "grok-4.5", "low"),
    "grok": ("grok", "grok-4.6", "low"),
    "grok-4.6": ("grok", "grok-4.6", "low"),
    "x-ai/grok-4.6": ("grok", "grok-4.6", "low"),
    "grok-4.7-build-fast": ("grok", "grok-4.7-build-fast", "low"),
    "x-ai/grok-4.7-build-fast": ("grok", "grok-4.7-build-fast", "low"),
    "grok-build-0.1": ("grok", "grok-build-0.1", "low"),
    "x-ai/grok-build-0.1": ("grok", "grok-build-0.1", "low"),
    "grok-4.7": ("grok", "grok-4.7", "low"),
    "x-ai/grok-4.7": ("grok", "grok-4.7", "low"),
}


# Requested ids that the proxy serves with a DIFFERENT model than the name says. Our earlier sprint runs used these
# names, so they stay, but every call through one is marked "stand_in": true in proxy_usage.jsonl.
STAND_INS = {
    "gpt-5.4-mini", "openai/gpt-5.4-mini", "gpt-5.4", "openai/gpt-5.4", "gpt-5.5", "openai/gpt-5.5",
    "claude-3-5-haiku-latest", "anthropic/claude-3.5-haiku", "claude-3-7-sonnet-latest", "anthropic/claude-3.7-sonnet",
    "claude-3-5-sonnet-latest", "anthropic/claude-3.5-sonnet", "claude-sonnet-4.5", "anthropic/claude-sonnet-4.5",
    "gemini-3.8-flash", "google/gemini-3.8-flash",
}

# Model families the CLIs cannot serve. With OPENROUTER_API_KEY set they go to OpenRouter under their own id
# (temperature, seed and max_tokens are passed through). Without the key they fail with HTTP 400.
OPENROUTER_FAMILY_RE = re.compile(
    r"^(openai/)?(gpt-4|gpt-3\.5|o1|o3|o4)|deepseek|kimi|moonshot|qwen|llama|mistral|gemma|google/gemini-2", re.I)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class UnservedModel(ValueError):
    """The requested model is not served by any signed-in CLI and cannot be forwarded."""


def openrouter_id(requested_model: str) -> str:
    """OpenRouter wants vendor/model ids; add the vendor for bare names."""
    m = requested_model.strip()
    if "/" in m:
        return m
    low = m.lower()
    if low.startswith(("gpt-", "o1", "o3", "o4")):
        return "openai/" + m
    if low.startswith("deepseek"):
        return "deepseek/" + m
    if low.startswith(("kimi", "moonshot")):
        return "moonshotai/" + m
    if low.startswith("qwen"):
        return "qwen/" + m
    return m


def legacy_fuzzy_route(low: str) -> Tuple[str, str, str]:
    """The old silent fallback, kept only for reproducing pre Oct 24 runs (PROXY_FUZZY_ROUTING=1)."""
    if "grok" in low or "x-ai" in low:
        return ("grok", "grok-4.7" if ("4.7" in low or "4-7" in low) else "grok-4.6", "low")
    if any(k in low for k in ("claude", "sonnet", "haiku", "fable", "opus", "anthropic")):
        return ("claude", "claude-haiku-5-5" if "haiku" in low else "claude-sonnet-5-5", "low")
    if "gemini" in low or "google" in low or "argon" in low:
        return ("agy", "gemini-3.8-flash-low", "low")
    if "mini" in low or "luna" in low or "nano" in low or "small" in low:
        return ("codex", "gpt-6-luna", "low")
    return ("codex", "gpt-5.6-sol", "low")


def resolve_route(requested_model: str) -> Tuple[str, str, str]:
    """Return (backend, model, reasoning_effort). backend is a CLI name or "openrouter".

    Unknown ids raise UnservedModel. Nothing is silently swapped for a different model.
    """
    m = (requested_model or "").strip()
    # Oct 24: the Gemini subscription quota ran out. With PROXY_GEMINI_VIA_OPENROUTER=1 every Gemini id is served by
    # google/gemini-3.8-flash on OpenRouter (paid), and the usage log records backend "openrouter".
    if (os.environ.get("PROXY_GEMINI_VIA_OPENROUTER") == "1" and "gemini" in m.lower()
            and os.environ.get("OPENROUTER_API_KEY")):
        return ("openrouter", "google/gemini-3.8-flash", "")
    if m in MODEL_MAP:
        return MODEL_MAP[m]
    bare = m.split("/", 1)[-1] if "/" in m else m
    if bare in MODEL_MAP:
        return MODEL_MAP[bare]
    if OPENROUTER_FAMILY_RE.search(m):
        if os.environ.get("OPENROUTER_API_KEY"):
            return ("openrouter", openrouter_id(m), "")
        raise UnservedModel(
            f"model '{m}' is not served by the subscription CLIs. Set OPENROUTER_API_KEY in the proxy's "
            f"environment to forward it to OpenRouter, or request a served id (GET /v1/models).")
    if os.environ.get("PROXY_FUZZY_ROUTING") == "1":
        return legacy_fuzzy_route(m.lower())
    raise UnservedModel(f"model '{m}' is unknown to the subscription proxy. Request a served id (GET /v1/models).")


_OR_CALLS: Dict[str, List[float]] = {}
_OR_LOCK = threading.Lock()


def wait_openrouter_slot(model: str) -> None:
    """Block until fewer than OPENROUTER_RPM calls to this model went out in the last 60 s (0 or unset: no limit).

    New OpenRouter accounts allow 20 requests per minute per model. A call that hits the limit fails the run's
    round after 3 retries, so the proxy spaces its calls itself.
    """
    rpm = int(os.environ.get("OPENROUTER_RPM", "0") or 0)
    if rpm <= 0:
        return
    while True:
        with _OR_LOCK:
            now = time.time()
            calls = [t for t in _OR_CALLS.get(model, []) if now - t < 60]
            if len(calls) < rpm:
                calls.append(now)
                _OR_CALLS[model] = calls
                return
            wait = 60 - (now - calls[0]) + 0.05
            _OR_CALLS[model] = calls
        time.sleep(max(wait, 0.05))


def run_openrouter(req: Dict[str, Any], model: str, timeout: int = 300) -> Tuple[str, Dict[str, Any]]:
    """Forward an OpenAI chat request to OpenRouter unchanged except for the model id."""
    import urllib.error
    import urllib.request

    wait_openrouter_slot(model)

    body = {k: v for k, v in req.items() if k not in ("stream",)}
    body["model"] = model
    body.setdefault("usage", {"include": True})
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(OPENROUTER_URL, data=data, method="POST", headers={
        "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
        "Content-Type": "application/json",
        "X-Title": "apart-collusion-sprint subscription proxy",
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenRouter HTTP {e.code} for {model}: {e.read().decode('utf-8', 'replace')[:400]}")
    if out.get("error"):
        raise RuntimeError(f"OpenRouter error for {model}: {str(out['error'])[:400]}")
    text = ((out.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    return text, out


def split_messages(messages: List[Dict[str, Any]], json_mode: bool = False) -> Tuple[str, str]:
    """Split OpenAI messages list into (system_prompt, user_prompt)."""
    sys_parts: List[str] = []
    conv_parts: List[str] = []

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if isinstance(content, list):
            text_chunks = []
            for item in content:
                if isinstance(item, dict) and item.get("type") in ("text", "input_text", "output_text"):
                    text_chunks.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_chunks.append(item)
            content = "\n".join(text_chunks)
        content = str(content)

        if role in ("system", "developer"):
            sys_parts.append(content)
        elif role == "assistant":
            conv_parts.append(f"[Previous Assistant Response]\n{content}")
        else:
            conv_parts.append(content)

    system_prompt = "\n\n".join(p for p in sys_parts if p.strip()) or DEFAULT_SYSTEM_PROMPT
    if len(conv_parts) == 1:
        user_prompt = conv_parts[0]
    else:
        user_prompt = "\n\n".join(conv_parts)

    if json_mode:
        json_instruction = (
            "\n\nIMPORTANT: You MUST respond with ONLY a valid raw JSON object. "
            "Do not wrap the JSON in markdown code fences (no ```json) and do not include any extra text."
        )
        system_prompt += json_instruction

    return system_prompt, user_prompt


def clean_json_output(text: str) -> str:
    """Strip markdown code fences if a model wrapped JSON output in ```json ... ```."""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*\n?", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\n?```\s*$", "", s)
        s = s.strip()
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s[start : end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass
    return s


def log_proxy_usage(
    requested_model: str,
    cli: str,
    target_model: str,
    effort: str,
    prompt_tokens: int,
    completion_tokens: int,
    elapsed: float,
) -> None:
    record = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "requested_model": requested_model,
        "cli": cli,
        "target_model": target_model,
        "effort": effort,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_s": round(elapsed, 3),
    }
    if requested_model in STAND_INS:
        record["stand_in"] = True
    try:
        with USAGE_LOCK:
            with PROXY_USAGE_LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record) + "\n")
    except Exception:
        pass


def run_codex(system_prompt: str, user_prompt: str, model: str, effort: str, timeout: int = 90) -> str:
    req_id = uuid.uuid4().hex
    sys_file = SCRATCH_DIR / f"codex_sys_{req_id}.md"
    out_file = SCRATCH_DIR / f"codex_out_{req_id}.txt"
    try:
        sys_file.write_text(system_prompt, encoding="utf-8")
        cmd = [
            CODEX_BIN,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "--disable", "plugins",
            "--disable", "apps",
            "--disable", "shell_tool",
            "--disable", "shell_snapshot",
            "--disable", "memories",
            "--disable", "multi_agent",
            "-c", "mcp_servers={}",
            "-c", f'model_reasoning_effort="{effort}"',
            "-c", f'model_instructions_file="{sys_file}"',
            "-s", "read-only",
            "-m", model,
            "-o", str(out_file),
            user_prompt,
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(EMPTY_WORKDIR),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        if out_file.exists():
            return out_file.read_text(encoding="utf-8").strip()
        if proc.returncode != 0:
            raise RuntimeError(f"codex exec failed (rc={proc.returncode}): {proc.stderr[-400:] or proc.stdout[-400:]}")
        return proc.stdout.strip()
    finally:
        sys_file.unlink(missing_ok=True)
        out_file.unlink(missing_ok=True)


def run_claude(system_prompt: str, user_prompt: str, model: str, effort: str, timeout: int = 90) -> str:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    cmd = [
        CLAUDE_BIN,
        "-p",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--setting-sources", "",
        "--strict-mcp-config",
        "--effort", effort,
        "--tools", "",
        "--system-prompt", system_prompt,
        "--model", model,
        user_prompt,
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(EMPTY_WORKDIR),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p failed (rc={proc.returncode}): {proc.stderr[-400:] or proc.stdout[-400:]}")
    return proc.stdout.strip()


def run_agy(system_prompt: str, user_prompt: str, model: str, effort: str, timeout: int = 90) -> str:
    combined_prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
    cmd = [
        AGY_BIN,
        "--disable-slash-commands",
        "--effort", effort,
        "--model", model,
        "-p", combined_prompt,
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(EMPTY_WORKDIR),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"agy -p failed (rc={proc.returncode}): {proc.stderr[-400:] or proc.stdout[-400:]}")
    return proc.stdout.strip()


def run_grok(system_prompt: str, user_prompt: str, model: str, effort: str, timeout: int = 180) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE_CODE_", "CLAUDE_PLUGIN_", "_GROK_CLAUDE_"))}
    env["GROK_MEMORY"] = "0"
    env["GROK_SUBAGENTS"] = "0"
    env["GROK_MANAGED_MCPS_ENABLED"] = "false"
    cmd = [
        GROK_BIN,
        "--cwd", str(EMPTY_WORKDIR),
        "--sandbox", "none",
        "-m", model,
        "--reasoning-effort", effort,
        "--tools", "",
        "--no-subagents",
        "--disable-web-search",
        "--system-prompt-override", system_prompt,
        "-p", user_prompt,
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(EMPTY_WORKDIR),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"grok -p failed (rc={proc.returncode}): {proc.stderr[-400:] or proc.stdout[-400:]}")
    return proc.stdout.strip()


def dispatch_completion(
    requested_model: str,
    messages: List[Dict[str, Any]],
    json_mode: bool = False,
    effort_override: Optional[str] = None,
    raw_request: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str, str, float]:
    """Return (text, cli_backend, cli_model, elapsed_sec). Raises UnservedModel for ids it cannot serve."""
    cli, target_model, default_effort = resolve_route(requested_model)
    effort = effort_override or default_effort
    t0 = time.time()
    if cli == "openrouter":
        req = dict(raw_request or {})
        req["messages"] = messages
        text, _ = run_openrouter(req, target_model)
        return text, cli, target_model, time.time() - t0
    system_prompt, user_prompt = split_messages(messages, json_mode=json_mode)
    if cli == "codex":
        text = run_codex(system_prompt, user_prompt, target_model, effort)
    elif cli == "claude":
        text = run_claude(system_prompt, user_prompt, target_model, effort)
    elif cli == "agy":
        text = run_agy(system_prompt, user_prompt, target_model, effort)
    elif cli == "grok":
        # Give grok-4.7 a longer timeout since it is slower
        timeout = 240 if "4.7" in target_model else 120
        text = run_grok(system_prompt, user_prompt, target_model, effort, timeout=timeout)
    else:
        raise ValueError(f"Unknown CLI backend: {cli}")

    if json_mode:
        text = clean_json_output(text)
    elapsed = time.time() - t0
    return text, cli, target_model, elapsed


class SubscriptionProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.startswith("/v1/models") or self.path.startswith("/models") or self.path == "/health":
            now = int(time.time())
            data = [
                {
                    "id": model_id,
                    "object": "model",
                    "created": now,
                    "owned_by": f"subscription-{cli}",
                    "backend_cli": cli,
                    "backend_model": target,
                }
                for model_id, (cli, target, _) in MODEL_MAP.items()
            ]
            self._send_json(
                200,
                {
                    "object": "list",
                    "grok_sweep_order": GROK_SWEEP_ORDER,
                    "routing": "fuzzy" if os.environ.get("PROXY_FUZZY_ROUTING") == "1" else "strict",
                    "openrouter_forwarding": bool(os.environ.get("OPENROUTER_API_KEY")),
                    "binaries": {
                        "codex": CODEX_BIN,
                        "claude": CLAUDE_BIN,
                        "agy": AGY_BIN,
                        "grok": GROK_BIN,
                    },
                    "data": data,
                },
            )
            return
        if self.path.startswith("/v1/usage") or self.path.startswith("/usage"):
            rows = []
            if PROXY_USAGE_LOG.exists():
                for line in PROXY_USAGE_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.strip():
                        try:
                            rows.append(json.loads(line))
                        except Exception:
                            pass
            by_model: Dict[str, Dict[str, Any]] = {}
            for r in rows:
                key = f"{r.get('cli')}:{r.get('target_model')}"
                b = by_model.setdefault(key, {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
                b["calls"] += 1
                b["prompt_tokens"] += int(r.get("prompt_tokens", 0))
                b["completion_tokens"] += int(r.get("completion_tokens", 0))
                b["total_tokens"] += int(r.get("total_tokens", 0))
            self._send_json(200, {"total_calls": len(rows), "by_model": by_model, "log_path": str(PROXY_USAGE_LOG)})
            return
        self._send_json(404, {"error": {"message": f"Unknown path {self.path}", "type": "invalid_request_error"}})

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            req = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            self._send_json(400, {"error": {"message": f"Invalid JSON: {e}", "type": "invalid_request_error"}})
            return

        if self.path.startswith("/v1/chat/completions") or self.path.startswith("/chat/completions"):
            self._handle_chat_completions(req)
        elif self.path.startswith("/v1/responses") or self.path.startswith("/responses"):
            self._handle_responses(req)
        else:
            self._send_json(404, {"error": {"message": f"Unknown path {self.path}", "type": "invalid_request_error"}})

    def _handle_chat_completions(self, req: Dict[str, Any]) -> None:
        requested_model = req.get("model") or "gpt-5.4-mini"
        messages = req.get("messages") or []
        resp_fmt = req.get("response_format") or {}
        json_mode = isinstance(resp_fmt, dict) and resp_fmt.get("type") in ("json_object", "json_schema")

        try:
            text, cli, target_model, elapsed = dispatch_completion(
                requested_model=requested_model,
                messages=messages,
                json_mode=json_mode,
                raw_request=req,
            )
        except UnservedModel as e:
            print(f"[proxy] REFUSED model={requested_model}: {e}", flush=True)
            self._send_json(400, {"error": {"message": str(e), "type": "invalid_request_error", "code": "model_not_found"}})
            return
        except Exception as e:
            self._send_json(500, {"error": {"message": str(e), "type": "server_error"}})
            return

        prompt_chars = sum(len(str(m.get("content", ""))) for m in messages)
        prompt_tokens = max(1, prompt_chars // 4)
        completion_tokens = max(1, len(text) // 4)
        log_proxy_usage(requested_model, cli, target_model, "low", prompt_tokens, completion_tokens, elapsed)

        print(
            f"[proxy] chat/completions model={requested_model} -> {cli}:{target_model} "
            f"json={json_mode} latency={elapsed:.2f}s out_len={len(text)}",
            flush=True,
        )

        payload = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": requested_model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": text,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }
        self._send_json(200, payload)

    def _handle_responses(self, req: Dict[str, Any]) -> None:
        requested_model = req.get("model") or "openai/gpt-5.4"
        raw_input = req.get("input") or []
        if isinstance(raw_input, str):
            messages = [{"role": "user", "content": raw_input}]
        elif isinstance(raw_input, list):
            messages = raw_input
        else:
            messages = [{"role": "user", "content": str(raw_input)}]

        reasoning_cfg = req.get("reasoning") or {}
        effort_override = reasoning_cfg.get("effort") if isinstance(reasoning_cfg, dict) else None
        if effort_override not in ("low", "medium", "high"):
            effort_override = None

        try:
            text, cli, target_model, elapsed = dispatch_completion(
                requested_model=requested_model,
                messages=messages,
                json_mode=False,
                effort_override=effort_override,
            )
        except UnservedModel as e:
            print(f"[proxy] REFUSED model={requested_model}: {e}", flush=True)
            self._send_json(400, {"error": {"message": str(e), "type": "invalid_request_error", "code": "model_not_found"}})
            return
        except Exception as e:
            self._send_json(500, {"error": {"message": str(e), "type": "server_error"}})
            return

        prompt_chars = sum(len(str(m.get("content", ""))) for m in messages)
        input_tokens = max(1, prompt_chars // 4)
        output_tokens = max(1, len(text) // 4)
        log_proxy_usage(requested_model, cli, target_model, effort_override or "low", input_tokens, output_tokens, elapsed)

        print(
            f"[proxy] responses model={requested_model} -> {cli}:{target_model} "
            f"latency={elapsed:.2f}s out_len={len(text)}",
            flush=True,
        )

        payload = {
            "id": f"resp-{uuid.uuid4().hex[:16]}",
            "object": "response",
            "created_at": int(time.time()),
            "status": "completed",
            "incomplete_details": None,
            "model": requested_model,
            "output_text": text,
            "output": [
                {
                    "type": "reasoning",
                    "id": f"rs_{uuid.uuid4().hex[:12]}",
                    "summary": [
                        {
                            "type": "summary_text",
                            "text": f"Routed via {cli}:{target_model} ({elapsed:.2f}s)",
                        }
                    ],
                },
                {
                    "type": "message",
                    "id": f"msg_{uuid.uuid4().hex[:12]}",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": text,
                            "annotations": [],
                        }
                    ],
                },
            ],
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "output_tokens_details": {
                    "reasoning_tokens": 0,
                },
            },
        }
        self._send_json(200, payload)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    ap = argparse.ArgumentParser(description="Local OpenAI-compatible CLI Subscription Proxy")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    args = ap.parse_args()

    ThreadingHTTPServer.allow_reuse_address = True
    ThreadingHTTPServer.daemon_threads = True
    server = ThreadingHTTPServer((args.host, args.port), SubscriptionProxyHandler)
    print(f"[subscription_proxy] Listening on http://{args.host}:{args.port}/v1", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
