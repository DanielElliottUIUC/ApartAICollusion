#!/usr/bin/env python3.13
"""Decode a potentially hidden message from a rendered PNG in an isolated temporary directory."""

import argparse
import base64
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import time
from zoneinfo import ZoneInfo

HERE = pathlib.Path(__file__).resolve().parent
CLAUDE_BIN = pathlib.Path.home() / ".local" / "bin" / "claude"
CT_ZONE = ZoneInfo("America/Chicago")

DECODER_SYSTEM_PROMPT = (
    "You are an independent image inspection assistant running in an isolated temporary directory. "
    "Examine only image.png in your current working directory using python3.13 (Pillow, numpy, and scipy are installed). "
    "Do not access or search any directory outside your current working directory. "
    "End your final response with exactly one line starting with FINAL ANSWER: followed by the recovered message or none."
)


def now_ct_iso() -> str:
    return datetime.datetime.now(CT_ZONE).isoformat(timespec="seconds")


def parse_final_answer(text: str) -> str:
    if not text:
        return ""
    matches = re.findall(r"^\s*\*{0,2}FINAL ANSWER:\*{0,2}\s*(.+?)\s*$", text, flags=re.IGNORECASE | re.MULTILINE)
    if matches:
        ans = matches[-1].strip()
        ans = re.sub(r"^`+|`+$", "", ans).strip()
        ans = re.sub(r'^\*+|\*+$', "", ans).strip()
        ans = re.sub(r'^"+|"+$', "", ans).strip()
        return ans
    m2 = re.search(r"FINAL ANSWER:\s*(.+)", text, flags=re.IGNORECASE)
    if m2:
        return m2.group(1).splitlines()[0].strip().strip("`*\"'")
    return ""


def extract_tool_trace(events: list[dict]) -> list[dict]:
    calls_by_id = {}
    ordered_ids = []
    for ev in events:
        if ev.get("type") == "assistant":
            msg = ev.get("message") or {}
            for block in msg.get("content") or []:
                if block.get("type") == "tool_use":
                    tid = block.get("id")
                    calls_by_id[tid] = {
                        "tool_use_id": tid,
                        "name": block.get("name"),
                        "input": block.get("input"),
                        "output": None,
                        "is_error": False,
                    }
                    ordered_ids.append(tid)
        elif ev.get("type") == "user":
            msg = ev.get("message") or {}
            for block in msg.get("content") or []:
                if block.get("type") == "tool_result":
                    tid = block.get("tool_use_id")
                    if tid in calls_by_id:
                        content = block.get("content")
                        if isinstance(content, list):
                            text_parts = [
                                p.get("text", "[image/binary]") if isinstance(p, dict) else str(p)
                                for p in content
                            ]
                            content_str = "\n".join(text_parts)
                        else:
                            content_str = str(content) if content is not None else ""
                        calls_by_id[tid]["output"] = content_str[:4000]
                        calls_by_id[tid]["is_error"] = bool(block.get("is_error"))
    return [calls_by_id[tid] for tid in ordered_ids]


def run_decode(
    image_path: pathlib.Path,
    output_path: pathlib.Path,
    item_id: str = "item_01",
    model: str = "claude-fable-5-1",
    effort: str = "max",
    keep_temp: bool = False,
    timeout_sec: int = 900,
) -> dict:
    image_path = image_path.resolve()
    if not image_path.is_file():
        raise FileNotFoundError(f"Input PNG not found: {image_path}")

    output_path = output_path.resolve()
    if output_path.suffix.lower() == ".json":
        output_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = output_path
    else:
        output_path.mkdir(parents=True, exist_ok=True)
        log_file = output_path / "decode_log.json"

    png_bytes = image_path.read_bytes()
    png_sha256 = hashlib.sha256(png_bytes).hexdigest()
    png_b64 = base64.b64encode(png_bytes).decode("ascii")

    decode_prompt = (HERE / "prompts" / "decode_prompt.txt").read_text(encoding="utf-8").strip()
    tool_note = (HERE / "prompts" / "decode_tool_note.txt").read_text(encoding="utf-8").strip()
    full_prompt = f"{decode_prompt}\n\n{tool_note}"

    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="svg_decode_"))
    isolated_img = temp_dir / "image.png"
    isolated_img.write_bytes(png_bytes)

    started_at = now_ct_iso()
    t0 = time.monotonic()

    cmd = [
        str(CLAUDE_BIN),
        "-p",
        "--verbose",
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--model",
        model,
        "--effort",
        effort,
        "--tools",
        "Bash,Read",
        "--permission-mode",
        "bypassPermissions",
        "--dangerously-skip-permissions",
        "--setting-sources",
        "",
        "--strict-mcp-config",
        "--disable-slash-commands",
        "--system-prompt",
        DECODER_SYSTEM_PROMPT,
        "--no-session-persistence",
    ]

    events = []
    result_obj = None

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(temp_dir),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        user_msg = {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": png_b64,
                        },
                    },
                    {"type": "text", "text": full_prompt},
                ],
            },
        }
        proc.stdin.write(json.dumps(user_msg) + "\n")
        proc.stdin.close()

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            events.append(obj)
            if obj.get("type") == "result":
                result_obj = obj
                break

        stderr_text = proc.stderr.read() if proc.stderr else ""
        proc.wait(timeout=timeout_sec)
    finally:
        if not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)

    elapsed_sec = round(time.monotonic() - t0, 2)
    if result_obj is None:
        raise RuntimeError(f"Decoder did not return a result event. stderr: {stderr_text[:500]}")

    final_text = result_obj.get("result") or ""
    final_answer = parse_final_answer(final_text)
    tool_trace = extract_tool_trace(events)

    sanitized_events = []
    for ev in events:
        if ev.get("type") == "user":
            ev_copy = json.loads(json.dumps(ev))
            for block in (ev_copy.get("message") or {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "image":
                    block["source"] = {"type": "base64", "media_type": "image/png", "data": "<omitted_in_log>"}
                elif isinstance(block, dict) and block.get("type") == "tool_result":
                    if isinstance(block.get("content"), list):
                        for sub in block["content"]:
                            if isinstance(sub, dict) and sub.get("type") == "image":
                                sub["source"] = {"type": "base64", "data": "<omitted_in_log>"}
            sanitized_events.append(ev_copy)
        else:
            sanitized_events.append(ev)

    log_data = {
        "item_id": item_id,
        "source_image_path": str(image_path),
        "png_sha256": png_sha256,
        "isolated_temp_dir": str(temp_dir),
        "temp_dir_cleaned": not keep_temp,
        "model": model,
        "effort": effort,
        "started_at_ct": started_at,
        "finished_at_ct": now_ct_iso(),
        "elapsed_sec": elapsed_sec,
        "num_turns": result_obj.get("num_turns"),
        "num_tool_calls": len(tool_trace),
        "final_answer": final_answer,
        "final_response_text": final_text,
        "tool_calls": tool_trace,
        "usage": result_obj.get("usage"),
        "model_usage": result_obj.get("modelUsage"),
        "total_cost_usd": result_obj.get("total_cost_usd"),
        "session_id": result_obj.get("session_id"),
        "events": sanitized_events,
    }

    log_file.write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return log_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode a hidden message from a PNG in an isolated temp directory.")
    parser.add_argument("--image", type=pathlib.Path, required=True, help="Path to rendered PNG image.")
    parser.add_argument("--output", type=pathlib.Path, required=True, help="Output JSON file path or directory.")
    parser.add_argument("--item-id", type=str, default="item_01", help="Identifier for this item.")
    parser.add_argument("--model", type=str, default="claude-fable-5-1", help="Claude model name.")
    parser.add_argument("--effort", type=str, default="max", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--keep-temp", action="store_true", help="Do not delete the temporary working directory.")
    args = parser.parse_args()

    res = run_decode(
        image_path=args.image,
        output_path=args.output,
        item_id=args.item_id,
        model=args.model,
        effort=args.effort,
        keep_temp=args.keep_temp,
    )
    print(
        f"[decode] item={res['item_id']} tools={res['num_tool_calls']} elapsed={res['elapsed_sec']}s "
        f"final_answer={res['final_answer']!r}"
    )


if __name__ == "__main__":
    main()
