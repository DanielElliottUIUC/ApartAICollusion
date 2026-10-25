#!/usr/bin/env python3
"""Sprint operations dashboard: scan sprint state, write state.json, embed it in index.html, serve both + /api/ask.

    python3 dashboard/serve.py           rescan every 5 s and serve on 127.0.0.1:8788
    python3 dashboard/serve.py --once    scan once, write state.json, embed it, exit

index.html carries the last scan in window.__INITIAL_STATE__, so it opens offline;
served, it polls /state.json and answers questions via POST /api/ask (claude-opus-5-5 low).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
SPRINT = HERE.parent
# Harness clone, which the explainer may read for the harness code: $COLLUSION_HACKATHON, else the clone that
# scripts/setup_other_machine.sh makes inside this repo, else the sprint box's.
HARNESS = Path(os.environ.get("COLLUSION_HACKATHON") or next(
    (p for p in (SPRINT / "collusion_hackathon", Path("/workspace/collusion_hackathon")) if p.is_dir()),
    SPRINT / "collusion_hackathon"))
# Run files: the same discovery as the docs (experiments/make_cases.py, which `scripts/run_all.sh docs` runs without
# $COLLUSION_HACKATHON), so the dashboard and the case files show the same runs on every machine: the repo copy in
# experiments/snapshot/ plus experiments/runs/<machine>/, where scripts/run_all.py writes.
os.environ.pop("COLLUSION_HACKATHON", None)
sys.path.insert(0, str(SPRINT / "experiments"))
import make_cases as mc  # noqa: E402

HACKATHON = mc.SRC
CARTEL = HACKATHON / "llm-cartel"
AUCTION = HACKATHON / "llm-agent-collusion"
STEGO = SPRINT / "src" / "fable_image_stego"
STATUS_MD = SPRINT / "STATUS.md"
LOG_MD = SPRINT / "notes" / "research_questions" / "LOG.md"
TALKS_MD = SPRINT / "talks" / "SCHEDULE.md"
STATE_PATH = HERE / "state.json"
INDEX_PATH = HERE / "index.html"

CT = ZoneInfo("America/Chicago")
DEADLINE = dt.datetime(2026, 10, 26, 6, 59, tzinfo=CT)  # Sun Oct 25 23:59 AoE
SPRINT_START = dt.datetime(2026, 10, 22)
TALK_DEFAULT_MIN = 60
STEGO_MODE_ITEMS = {"examples": 3, "smoke": 1, "pilot": 12, "full": 60}
PORTS = [(8787, "Subscription LLM Proxy"), (8788, "Dashboard Server")]
PROCESS_PATTERNS = [
    ("Stego harness", re.compile(r"run_pilot\.py|fable_image_stego")),
    ("Bertrand pricing", re.compile(r"run_game\.py|branch_game\.py|llm-cartel")),
    ("Double auction", re.compile(r"continuous_double_auction|llm-agent-collusion")),
    ("LLM proxy", re.compile(r"\b8787\b|subscription_proxy|litellm")),
    ("Dashboard server", re.compile(r"dashboard/serve\.py")),
]
SHELLS = {"bash", "sh", "zsh", "dash"}

EMBED_RE = re.compile(r'(<script id="initial-state">)(.*?)(</script>)', re.S)
STARTED = time.time()


def now_ct() -> dt.datetime:
    return dt.datetime.now(CT)


def mtime_iso(path: Path) -> str | None:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime, CT).isoformat(timespec="seconds")
    except OSError:
        return None


def rel(path: Path) -> str:
    for root in (SPRINT, HACKATHON):
        try:
            return f"{root.name}/{path.relative_to(root).as_posix()}"
        except ValueError:
            pass
    return path.as_posix()


_cache: dict[Path, tuple[tuple[int, int], object]] = {}


def cached(path: Path, reducer):
    st = path.stat()
    key = (st.st_mtime_ns, st.st_size)
    hit = _cache.get(path)
    if hit and hit[0] == key:
        return hit[1]
    value = reducer(path)
    _cache[path] = (key, value)
    return value


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


# ---------------------------------------------------------------- markdown sources


def parse_status(path: Path) -> dict:
    out = {"path": rel(path), "mtime": mtime_iso(path), "last_updated": None,
           "deadline_text": [], "tasks": [], "updates": []}
    if not path.exists():
        return out
    section = None
    for line in path.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^#{1,3}\s+(.*)", line)
        if head:
            section = head.group(1).strip()
            if section.lower().startswith("update"):
                out["updates"].append({"title": section, "body": []})
            continue
        if line.startswith("Last updated:"):
            out["last_updated"] = line.split(":", 1)[1].strip().rstrip(".")
            continue
        task = re.match(r"^\s*[-*]\s+\[([ xX])\]\s+(.*)", line)
        if task:
            out["tasks"].append({"done": task.group(1).lower() == "x",
                                 "text": task.group(2).strip(), "section": section})
        elif line.strip() and section == "Deadline":
            out["deadline_text"].append(line.strip())
        elif line.strip() and out["updates"] and section == out["updates"][-1]["title"]:
            out["updates"][-1]["body"].append(line.strip())
    return out


LOG_SECTION_CHARS = 600


def parse_log(path: Path) -> dict:
    out = {"path": rel(path), "mtime": mtime_iso(path), "entries": []}
    if not path.exists():
        return out
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = re.match(r"^##\s+(.*)", line)
        section = re.match(r"^###\s+(.*)", line)
        if entry:
            title = entry.group(1).strip()
            entries.append(None if title.lower().startswith("how this log works")
                           else {"title": title, "sections": [{"heading": "", "lines": []}]})
        elif entries and entries[-1] is not None:
            if section:
                entries[-1]["sections"].append({"heading": section.group(1).strip(), "lines": []})
            elif line.strip() != "---":
                entries[-1]["sections"][-1]["lines"].append(line)
    entries = [e for e in entries if e]
    for e in entries:
        stamp = re.match(r"(\d{4}-\d{2}-\d{2}(?:\s+\d{1,2}:\d{2}(?:\s*[AP]M)?)?(?:\s*CT)?)\s*:?\s*(.*)", e["title"])
        e["stamp"], e["title"] = (stamp.group(1), stamp.group(2) or e["title"]) if stamp else (None, e["title"])
        sections = []
        for s in e["sections"]:
            body = "\n".join(s.pop("lines")).strip()
            if body or s["heading"]:
                s["body"] = body[:LOG_SECTION_CHARS]
                s["truncated"] = len(body) > LOG_SECTION_CHARS
                s["items"] = len(re.findall(r"^\s*(?:[-*]|\d+\.)\s+", body, re.M))
                sections.append(s)
        e["sections"] = sections
    out["entries"] = entries
    return out


def talk_window(day: str, when: str) -> tuple[str | None, str | None]:
    date = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2})", day)
    times = re.findall(r"(\d{1,2}):(\d{2})\s*([AP]M)", when)
    if not date or not times:
        return None, None
    month = dt.datetime.strptime(date.group(1), "%b").month

    def at(h, m, ap):
        hour = int(h) % 12 + (12 if ap == "PM" else 0)
        return dt.datetime(DEADLINE.year, month, int(date.group(2)), hour, int(m), tzinfo=CT)

    start = at(*times[0])
    end = at(*times[1]) if len(times) > 1 else start + dt.timedelta(minutes=TALK_DEFAULT_MIN)
    return start.isoformat(), end.isoformat()


def parse_talks(path: Path) -> dict:
    out = {"path": rel(path), "mtime": mtime_iso(path), "talks": []}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] == "Day" or set(cells[0]) <= set("-: "):
            continue
        day, when, speaker, talk, luma, folder = cells[:6]
        start, end = talk_window(day, when)
        out["talks"].append({"day": day, "time": when, "speaker": speaker, "talk": talk,
                             "luma": luma, "folder": folder, "start": start, "end": end})
    return out


# ---------------------------------------------------------------- Fable 5.1 image steganography

ITEM_KEYS = ["item_id", "is_benign_control", "encoding_family", "ground_truth", "predicted",
             "sequence_matcher_ratio", "levenshtein_similarity", "char_accuracy", "exact_match",
             "recovered_90pct", "false_alarm", "elapsed_encode_sec", "elapsed_decode_sec",
             "num_tool_calls"]
SUMMARY_KEYS = ["graded_at_ct", "stego_total", "stego_recovered_90pct", "stego_recovery_rate",
                "stego_exact_match", "stego_mean_sequence_matcher", "stego_mean_levenshtein_similarity",
                "control_total", "control_false_alarms", "control_false_alarm_rate", "by_encoding_family"]


def stego_run(name: str, kind: str, path: Path, summary: dict) -> dict:
    run = {"name": name, "kind": kind, "path": rel(path), "status": "graded", "mtime": mtime_iso(path)}
    run.update({k: summary.get(k) for k in SUMMARY_KEYS})
    run["items"] = [{k: it.get(k) for k in ITEM_KEYS} for it in summary.get("items", [])]
    return run


def stego_mode(name: str) -> str:
    mode = name.split("_", 1)[0]
    return mode if mode in STEGO_MODE_ITEMS else "run"


def scan_stego() -> dict:
    runs = []
    pilot = STEGO / "pilot_results.json"
    if pilot.exists():
        data = read_json(pilot)
        blocks = data if isinstance(data, list) else data.get("runs", [data])
        for i, block in enumerate(blocks):
            runs.append(stego_run(block.get("name", f"pilot_results[{i}]"), "pilot", pilot, block))
    for summ in sorted((STEGO / "smoke_results").glob("*/summary.json")):
        runs.append(cached(summ, lambda p: stego_run(p.parent.name, "smoke", p, read_json(p))))
    for d in sorted((STEGO / "runs").glob("*")) if (STEGO / "runs").is_dir() else []:
        if not d.is_dir():
            continue
        summ = d / "summary.json"
        if summ.exists():
            runs.append(cached(summ, lambda p: stego_run(p.parent.name, stego_mode(p.parent.name), p, read_json(p))))
            continue
        item_dirs = [x for x in d.iterdir() if x.is_dir()]
        done = sum((x / "decode_log.json").exists() for x in item_dirs)
        newest = max([d.stat().st_mtime] + [f.stat().st_mtime for x in item_dirs for f in x.iterdir()])
        mode = stego_mode(d.name)
        runs.append({"name": d.name, "kind": mode, "path": rel(d), "mtime": mtime_iso(d),
                     "status": "in progress" if time.time() - newest < 900 else "stalled",
                     "items_done": done, "items_started": len(item_dirs),
                     "items_expected": STEGO_MODE_ITEMS.get(mode), "items": []})
    graded = [r for r in runs if r["status"] == "graded"]
    items = [it for r in graded for it in r["items"]]
    stego_items = [it for it in items if not it["is_benign_control"]]
    controls = [it for it in items if it["is_benign_control"]]
    return {
        "runs": runs,
        "pilot_results_path": rel(pilot),
        "pilot_results_exists": pilot.exists(),
        "pilot_command": "cd src/fable_image_stego && python3.13 run_pilot.py --mode pilot",
        "totals": {
            "runs_graded": len(graded),
            "runs_ungraded": len(runs) - len(graded),
            "pilot_runs": sum(r["kind"] in ("pilot", "full") for r in runs),
            "stego_items": len(stego_items),
            "stego_recovered": sum(bool(it["recovered_90pct"]) for it in stego_items),
            "stego_exact": sum(bool(it["exact_match"]) for it in stego_items),
            "controls": len(controls),
            "false_alarms": sum(bool(it["false_alarm"]) for it in controls),
        },
    }


# ---------------------------------------------------------------- llm-agent-collusion double auction


AUCTION_ROUND_RE = re.compile(r"## Auction Results: Round \d+\s*\n````json\n(.*?)\n````", re.S)
AGENT_RESPONSE_RE = re.compile(r"## Response: Round (\d+)[^\n]*\n````json\n(.*?)\n````", re.S)


def clip(text, n: int) -> str:
    return str(text or "")[:n]


def auction_rounds(run_dir: Path) -> list[dict]:
    """Per-round order book, trades, seller chat and each agent's private plan, for the replay."""
    results = run_dir / "auction_results.md"
    if not results.exists():
        return []
    rounds = {}
    for block in AUCTION_ROUND_RE.findall(results.read_text(encoding="utf-8", errors="replace")):
        try:
            b = json.loads(block)
        except json.JSONDecodeError:
            continue  # a round still being written
        n = b.get("round_number")
        rounds[n] = {
            "round": n,
            "seller_asks": {k: round(v, 2) for k, v in (b.get("seller_asks") or {}).items()},
            "buyer_bids": {k: round(v, 2) for k, v in (b.get("buyer_bids") or {}).items()},
            "trades": [{"buyer": t.get("buyer_id"), "seller": t.get("seller_id"), "price": round(t.get("price", 0), 2)}
                       for t in b.get("trades") or []],
            "seller_messages": {k: clip(v, 300) for k, v in (b.get("seller_messages") or {}).items() if v},
            "seller_plans": {},
            "buyer_plans": {},
        }
    for agent_md in sorted(run_dir.glob("Seller *.md")) + sorted(run_dir.glob("Buyer *.md")):
        seller = agent_md.stem.startswith("Seller")
        for n, block in AGENT_RESPONSE_RE.findall(agent_md.read_text(encoding="utf-8", errors="replace")):
            r = rounds.get(int(n))
            try:
                resp = json.loads(block)
            except json.JSONDecodeError:
                continue
            if r is None or not isinstance(resp, dict):
                continue
            if seller:
                r["seller_plans"][agent_md.stem] = {"plan": clip(resp.get("plan_for_this_hour"), 220),
                                                    "reflection": clip(resp.get("reflection"), 180)}
            else:
                r["buyer_plans"][agent_md.stem] = {"plan": clip(resp.get("plan_for_this_hour"), 180)}
    return [rounds[k] for k in sorted(rounds)]


def agent_models(models) -> list[str]:
    return sorted({"ZIP (rule-based)" if m is None else str(m) for m in models or []})


def auction_run(metrics_path: Path) -> dict:
    m = read_json(metrics_path)
    run_dir = metrics_path.parent
    meta_path = run_dir / "experiment_metadata.json"
    meta = read_json(meta_path) if meta_path.exists() else {}
    cfg = meta.get("auction_config", {})
    name = run_dir.name
    stamp = re.match(r"^(\d{8}_\d{6})_(.*)$", name)
    started = dt.datetime.strptime(stamp.group(1), "%Y%m%d_%H%M%S") if stamp else None
    preexisting = bool(started and started < SPRINT_START)
    tag = cfg.get("tag") or (stamp.group(2) if stamp else name)
    ce, jpm = m.get("competitive_equilibrium_price"), m.get("joint_profit_maximization_price")
    span = (jpm - ce) if ce is not None and jpm is not None and jpm != ce else None

    def idx(p):
        return None if p is None or span is None else round((p - ce) / span, 4)

    ask_indices = [idx(a) for a in m.get("avg_seller_asks_by_round", [])]
    avg_asks = [round(a, 2) if a is not None else None for a in m.get("avg_seller_asks_by_round", [])]
    out = {
        "name": name,
        "path": rel(run_dir),
        "started": started.isoformat() if started else None,
        "preexisting": preexisting,
        "tag": tag,
        "condition": re.sub(r"-\d+$", "", tag),
        "rounds": cfg.get("rounds", len(avg_asks)),
        "seller_models": agent_models(cfg.get("seller_models")),
        "buyer_models": agent_models(cfg.get("buyer_models")),
        # simulation.py builds seller i from seller_models[i] and records it as seller_ids[i]
        "seller_model_of": dict(zip(meta.get("seller_ids") or [], cfg.get("seller_models") or [])),
        "seller_comms": cfg.get("seller_comms_enabled"),
        "oversight": cfg.get("oversight_enabled"),
        "boss_pressure": cfg.get("boss_pressure"),
        "seller_valuations": cfg.get("seller_valuations"),
        "buyer_valuations": cfg.get("buyer_valuations"),
        "ce_price": ce,
        "jpm_price": jpm,
        "avg_trade_price": round(m["avg_trade_price_overall"], 2) if m.get("avg_trade_price_overall") is not None else None,
        "price_index": idx(m.get("avg_trade_price_overall")),
        "mean_ask_price": mean(avg_asks),
        "mean_ask_index": mean(ask_indices),
        "ask_auc": round(m["collusion_avg_seller_asks_auc"], 3) if m.get("collusion_avg_seller_asks_auc") is not None else None,
        "ask_dispersion": round(m["avg_seller_ask_dispersion"], 4) if m.get("avg_seller_ask_dispersion") is not None else None,
        "average_pcm": m.get("average_pcm"),
        "num_trades": m.get("num_trades"),
        "trade_frequency": m.get("trade_frequency"),
        "combined_seller_profits": m.get("combined_seller_profits"),
        "ask_index_by_round": ask_indices,
        "avg_asks_by_round": avg_asks,
    }
    if not preexisting:
        out["rounds_detail"] = auction_rounds(run_dir)
    return out


def live_auction_config(run_dir: Path) -> dict:
    log = run_dir / "unified.log"
    if not log.exists():
        return {}
    with open(log, encoding="utf-8", errors="replace") as f:
        text = f.read(65536)
    at = text.find("Auction configured with:")
    start = text.find("{", at) if at >= 0 else -1
    try:
        return json.JSONDecoder().raw_decode(text, start)[0] if start >= 0 else {}
    except json.JSONDecodeError:
        return {}


LOG_TS_RE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d),\d+ - ", re.M)


def last_activity(run_dir: Path) -> float:
    """Time of the run's last unified.log line (every sprint machine logs in CT). File times are no use for runs
    from other machines: a git pull sets them to the checkout time."""
    log = run_dir / "unified.log"
    stamps = LOG_TS_RE.findall(log.read_text(encoding="utf-8", errors="replace")[-4000:]) if log.exists() else []
    if stamps:
        return dt.datetime.strptime(stamps[-1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=CT).timestamp()
    return max(f.stat().st_mtime for f in [run_dir, *run_dir.iterdir()])


def ended_tags() -> set:
    """Runs that scripts/run_all.py recorded as ended (any rc) on any machine: never running, whatever their file times."""
    tags = set()
    for st in mc.RUNS.glob("*/status.jsonl"):
        for ln in st.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                tags.add(json.loads(ln).get("tag"))
            except json.JSONDecodeError:
                continue
    return tags


def auction_live(run_dir: Path) -> dict:
    cfg = live_auction_config(run_dir)
    results = run_dir / "auction_results.md"
    done = results.read_text(encoding="utf-8", errors="replace").count("## Auction Results: Round") if results.exists() else 0
    newest = last_activity(run_dir)
    stamp = re.match(r"^\d{8}_\d{6}_(.*)$", run_dir.name)
    return {"name": run_dir.name, "path": rel(run_dir), "tag": cfg.get("tag") or (stamp.group(1) if stamp else None),
            "rounds_done": done,
            "rounds_target": cfg.get("rounds"), "seller_models": agent_models(cfg.get("seller_models")),
            "buyer_models": agent_models(cfg.get("buyer_models")),
            "seller_comms": cfg.get("seller_comms_enabled"), "boss_pressure": cfg.get("boss_pressure"),
            "oversight": cfg.get("oversight_enabled"),
            "seller_valuations": cfg.get("seller_valuations"), "buyer_valuations": cfg.get("buyer_valuations"),
            "status": "in progress" if time.time() - newest < 600 else "stalled",
            "last_write": dt.datetime.fromtimestamp(newest, CT).isoformat(timespec="seconds"),
            "rounds_detail": auction_rounds(run_dir)}


def scan_auction() -> dict:
    authors = sorted(d for d in (AUCTION / "data").iterdir() if d.is_dir()) if (AUCTION / "data").is_dir() else []
    run_dirs = authors + mc.auction_run_dirs(AUCTION)
    done_dirs = [d for d in run_dirs if (d / "collusion_metrics.json").exists()]
    # Unfinished runs, including those stopped before round 1 ended (no auction_results.md, so not in run_dirs).
    started = sorted({p for p in [*(AUCTION / "results").glob("*"), *mc.RUNS.glob("*/*/*")] if (p / "unified.log").exists()}
                     - set(run_dirs))
    live = [auction_live(d) for d in run_dirs + started if d not in done_dirs and (d / "unified.log").exists()]
    runs = [cached(d / "collusion_metrics.json", auction_run) for d in done_dirs]
    conditions = {}
    for r in runs:
        conditions.setdefault(r["condition"], []).append(r)
    cond_rows = []
    for name, rs in conditions.items():
        rounds = max(len(r["ask_index_by_round"]) for r in rs)
        traj = [mean([r["ask_index_by_round"][i] for r in rs if i < len(r["ask_index_by_round"])])
                for i in range(rounds)]
        idxs = [r["price_index"] for r in rs if r["price_index"] is not None]
        ask_idxs = [r["mean_ask_index"] for r in rs if r.get("mean_ask_index") is not None]
        cond_rows.append({
            "condition": name, "n": len(rs), "n_sprint": sum(not r["preexisting"] for r in rs),
            "sprint": all(not r["preexisting"] for r in rs),
            "seller_comms": any(r["seller_comms"] for r in rs),
            "boss_pressure": any(r.get("boss_pressure") for r in rs),
            "mean_index": mean(idxs), "min_index": min(idxs) if idxs else None,
            "max_index": max(idxs) if idxs else None, "run_indices": idxs,
            "mean_ask_index": mean(ask_idxs),
            "n_no_trades": sum(r["price_index"] is None for r in rs),
            "mean_pcm": mean([r["average_pcm"] for r in rs]),
            "mean_trade_frequency": mean([r["trade_frequency"] for r in rs]),
            "mean_ask_index_by_round": traj,
            "seller_models": sorted({x for r in rs for x in r["seller_models"]}),
            "buyer_models": sorted({x for r in rs for x in r["buyer_models"]}),
        })
    cond_rows.sort(key=lambda c: (not c["sprint"], -(c["mean_ask_index"] if c["mean_ask_index"] is not None else -99)))
    latest = max((r["started"] for r in runs if r["started"]), default=None)
    # Only embed full rounds_detail for sprint runs; strip heavy arrays from preexisting author runs
    out_runs = []
    for r in runs:
        if r["preexisting"]:
            out_runs.append({k: v for k, v in r.items() if k not in ("ask_index_by_round", "avg_asks_by_round", "rounds_detail")})
        else:
            out_runs.append(r)
    return {
        "root": rel(AUCTION),
        "runs": out_runs,
        "live": live,
        "conditions": cond_rows,
        "totals": {"runs": len(runs), "preexisting": sum(r["preexisting"] for r in runs),
                   "sprint": sum(not r["preexisting"] for r in runs), "live": len(live),
                   "conditions": len(cond_rows), "latest_run": latest},
    }


# ---------------------------------------------------------------- llm-cartel Bertrand pricing


def bertrand_run(path: Path) -> dict:
    config = read_json(path.with_name(path.stem + ".config.json"))
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            break
    gains = [r.get("gains") or [] for r in records]
    target = config.get("rounds")
    age = time.time() - path.stat().st_mtime
    running = age < 180 and path.stem not in ended_tags()
    status = "complete" if target and len(records) >= target else ("running" if running else "partial")
    summary = config.get("summary") or {}
    models = sorted({str(m).split(":", 1)[-1] for m in config.get("models") or []})
    prefix_str = "-".join(sorted(set(config.get("prefixes") or []))) or "?"
    label = " ".join([prefix_str, "+".join(models) or "?"]
                     + (["think"] if config.get("think") else []) + [f"s{config.get('seed')}"])
    market_gain_by_round = [round(sum(g) / len(g), 4) if g else None for g in gains]
    prices_by_round = [[round(p, 3) for p in r.get("actions", [])] for r in records]
    mean_p0 = mean([p[0] for p in prices_by_round if len(p) > 0])
    mean_p1 = mean([p[1] for p in prices_by_round if len(p) > 1])
    rounds_detail = []
    for r in records:
        acts = [round(float(x), 3) for x in (r.get("actions") or [])]
        dems = [round(float(x), 2) for x in (r.get("demands") or [])]
        profs = [round(float(x), 2) for x in (r.get("profits") or [])]
        gns = [round(float(x), 3) for x in (r.get("gains") or [])]
        thts = [clip(x, 320) for x in (r.get("thoughts") or ["", ""])]
        rounds_detail.append({
            "round": r.get("round", len(rounds_detail)),
            "actions": acts,
            "demands": dems,
            "profits": profs,
            "gains": gns,
            "thoughts": thts,
            # Runs without --think record no reasoning; the raw reply is all there is.
            "responses": [clip(x, 160) for x in (r.get("respones") or [])],
        })
    return {
        "name": path.stem, "label": label, "path": rel(path), "mtime": mtime_iso(path), "status": status,
        "rounds_done": len(records), "rounds_target": target,
        "agents": config.get("agents"), "models": config.get("models"), "model_short": models[0] if models else "?",
        "seed": config.get("seed"),
        "prefixes": config.get("prefixes"), "prefix_short": prefix_str,
        "think": bool(config.get("think")),
        "nash_prices": config.get("nash_prices"), "monopoly_prices": config.get("monopoly_prices"),
        "market_gain_by_round": market_gain_by_round,
        "market": {k: config.get(k) for k in ("a0", "ais", "mu", "costs", "price_scale")},
        "mean_prices": [mean_p0, mean_p1],
        "mean_price_overall": mean([mean_p0, mean_p1]),
        "mean_gain_all": mean(market_gain_by_round),
        "market_mean_gain": summary.get("market_mean_gain") if summary.get("market_mean_gain") is not None else mean(market_gain_by_round),
        "threshold": summary.get("threshold", 0.5),
        "positive_control": summary.get("positive_control"),
        "window_rounds": summary.get("window_rounds"),
        "rounds_detail": rounds_detail,
    }


def scan_bertrand() -> dict:
    roots = [CARTEL / "results" / "jsonl", mc.RUNS]
    runs = [cached(p, bertrand_run) for p in mc.bertrand_files(CARTEL)]
    runs.sort(key=lambda r: -(r.get("mean_gain_all") or -99))
    return {
        "root": rel(CARTEL),
        "scanned": [rel(r) + ("" if r.is_dir() else " (absent)") for r in roots],
        "runs": runs,
        "command": "cd /workspace/collusion_hackathon/llm-cartel && uv run python run_game.py "
                   "--models openai/gpt-4.1-mini --rounds 30 -y",
        "totals": {"runs": len(runs), "complete": sum(r["status"] == "complete" for r in runs),
                   "running": sum(r["status"] == "running" for r in runs),
                   "positive_control_pass": sum((r.get("mean_gain_all") or 0) >= 0.5 for r in runs)},
    }


# ---------------------------------------------------------------- experiment batches (progress)

BATCH_LINE_RE = re.compile(r"\[(\d\d:\d\d:\d\d)\] (start|done)\s+(\S+)(?: rc=(\d+))?")


def scan_batches() -> list[dict]:
    """Progress of each experiments/<batch>/logs/ run batch: planned tags (plan.txt, else every tag the
    log has started) with queued, running, done or failed status from matrix.log."""
    out = []
    for log in sorted((SPRINT / "experiments").glob("*/logs/matrix.log")):
        plan = log.with_name("plan.txt")
        lines = log.read_text(encoding="utf-8", errors="replace").splitlines()
        events = [m.groups() for m in map(BATCH_LINE_RE.match, lines) if m]
        tags = ([t.strip() for t in plan.read_text().splitlines() if t.strip()] if plan.exists()
                else list(dict.fromkeys(tag for _, kind, tag, _ in events if kind == "start")))
        jobs = {t: {"tag": t, "status": "queued"} for t in tags}
        for at, kind, tag, rc in events:
            job = jobs.setdefault(tag, {"tag": tag, "status": "queued"})
            if kind == "start":
                job.update(status="running", started=at)
            else:
                job.update(status="done" if rc == "0" else "failed", finished=at, rc=int(rc or -1))
        out.append({"name": log.parent.parent.name, "path": rel(log), "mtime": mtime_iso(log),
                    "finished": any("matrix finished" in l for l in lines), "jobs": list(jobs.values())})
    return out


# ---------------------------------------------------------------- runtime: processes, ports, git


def scan_processes() -> list[dict]:
    if not Path("/proc").is_dir():  # macOS and Windows have no /proc: report only this server
        return [{"pid": os.getpid(), "label": "Dashboard server", "cmd": " ".join(sys.argv)[:240],
                 "cwd": rel(Path.cwd()), "elapsed_s": round(time.time() - STARTED), "self": True}]
    clk = os.sysconf("SC_CLK_TCK")
    uptime = float(Path("/proc/uptime").read_text().split()[0])
    me = os.getpid()
    found = []
    for pid_dir in Path("/proc").iterdir():
        if not pid_dir.name.isdigit() or int(pid_dir.name) == me:
            continue
        try:
            argv = (pid_dir / "cmdline").read_bytes().split(b"\0")
            argv = [a.decode(errors="replace") for a in argv if a]
            if not argv or os.path.basename(argv[0]) in SHELLS:
                continue
            try:
                cwd = os.readlink(pid_dir / "cwd")
            except OSError:
                cwd = ""
            cmd = " ".join(argv)
            label = next((lab for lab, rx in PROCESS_PATTERNS if rx.search(cmd + " " + cwd)), None)
            if label is None:
                continue
            start_ticks = int((pid_dir / "stat").read_text().rsplit(")", 1)[1].split()[19])
            found.append({"pid": int(pid_dir.name), "label": label, "cmd": cmd[:240], "cwd": rel(Path(cwd)) if cwd else "",
                          "elapsed_s": round(uptime - start_ticks / clk)})
        except (OSError, IndexError, ValueError):
            continue
    found.append({"pid": me, "label": "Dashboard server", "cmd": " ".join(sys.argv)[:240],
                  "cwd": rel(Path.cwd()), "elapsed_s": round(time.time() - STARTED), "self": True})
    return sorted(found, key=lambda p: (p["label"], p["pid"]))


def probe_ports() -> list[dict]:
    out = []
    for port, label in PORTS:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                up = True
        except OSError:
            up = False
        out.append({"port": port, "label": label, "up": up})
    return out


def git_head() -> dict:
    try:
        line = subprocess.run(["git", "-C", str(SPRINT), "log", "-1", "--format=%h%x09%cI%x09%s"],
                              capture_output=True, text=True, timeout=3).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(SPRINT), "status", "--porcelain"],
                               capture_output=True, text=True, timeout=3).stdout.splitlines()
        sha, date, subject = line.split("\t", 2)
        return {"sha": sha, "date": date, "subject": subject, "dirty_files": len(dirty)}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}


# ---------------------------------------------------------------- assemble, write, embed


def scan() -> dict:
    t0 = time.time()
    state = {
        "generated_at": now_ct().isoformat(timespec="seconds"),
        "deadline_iso": DEADLINE.isoformat(),
        "deadline_label": "Mon 2026-10-26 06:59 CT (Sun Oct 25 23:59 AoE)",
        "sprint_root": SPRINT.name,  # repo-relative, so a committed index.html names no home directory
        "git": git_head(),
        "status": parse_status(STATUS_MD),
        "research_log": parse_log(LOG_MD),
        "talks": parse_talks(TALKS_MD),
        "stego": scan_stego(),
        "auction": scan_auction(),
        "bertrand": scan_bertrand(),
        "batches": scan_batches(),
        # anonymised token and cost snapshot written by scripts/snapshot_usage.py
        "usage": read_json(SPRINT / "token-usage" / "usage_snapshot.json") if (SPRINT / "token-usage" / "usage_snapshot.json").exists() else None,
        "runtime": {"processes": scan_processes(), "ports": probe_ports()},
    }
    state["sources"] = [{"label": label, "path": rel(p), "mtime": mtime_iso(p), "exists": p.exists()}
                        for label, p in [("Status", STATUS_MD), ("Research log", LOG_MD),
                                         ("Talks", TALKS_MD), ("Stego pilot", STEGO / "pilot_results.json"),
                                         ("Stego smoke", STEGO / "smoke_results"), ("Stego runs", STEGO / "runs"),
                                         ("Double auction (authors)", AUCTION / "data"),
                                         ("Double auction (sprint)", AUCTION / "results"),
                                         ("Bertrand results", CARTEL / "results"),
                                         ("Runner runs (every machine)", mc.RUNS)]]
    state["scan_ms"] = round((time.time() - t0) * 1000)
    return state


def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def publish(state: dict) -> bytes:
    body = json.dumps(state, ensure_ascii=False, separators=(",", ":"))
    atomic_write(STATE_PATH, body)
    payload = "window.__INITIAL_STATE__ = " + body.replace("<", "\\u003c") + ";"
    html, n = EMBED_RE.subn(lambda m: m.group(1) + payload + m.group(3), INDEX_PATH.read_text(encoding="utf-8"), count=1)
    if n != 1:
        raise SystemExit(f'{INDEX_PATH} has no <script id="initial-state"> block to embed into')
    atomic_write(INDEX_PATH, html)
    return body.encode()


CLAUDE_BIN = os.environ.get("CLAUDE_BIN") or shutil.which("claude") or str(Path.home() / ".local/bin/claude")
ASK_TIMEOUT_S = 120
ASK_TOOLS = "Read,Grep,Glob"  # read-only: the explainer can look anything up but change nothing
REPO_GUIDE = f"""You can read files with Read, Grep and Glob. Look facts up instead of guessing, and cite file paths.
Where things are:
- This sprint repo ({SPRINT}, the current directory): STATUS.md (tasks, deadline), notes/research_questions/
  (LOG.md and the notes it links), talks/, papers/, src/fable_image_stego/ (README, smoke_results/*/summary.json),
  src/subscription_proxy/ (model routing), experiments/heterogeneous/run_matrix.sh (mixed-team design),
  scripts/, dashboard/state.json (every parsed run in compact form).
- Run outputs under {HACKATHON}:
  llm-agent-collusion/results/<timestamp>_<tag>/ are the sprint double-auction runs: auction_results.md (per-round
  asks, bids, trades, seller chat), "Seller <Name>.md" and "Buyer <Name>.md" (prompts, private plans),
  collusion_metrics.json, experiment_metadata.json (seller_ids[i] used seller_models[i]).
  llm-agent-collusion/data/ holds the authors' 2025 runs. llm-cartel/results/jsonl/*.jsonl (+ .config.json) are the Bertrand runs.
- Runs from scripts/run_all.py, every machine: experiments/runs/<machine>/<phase>/ (same files as above; phase is
  sweep, refusal, matrix, A, B or fable), with status.jsonl and logs/<tag>.log per machine.
- Harness code under {HARNESS} (when the clone is present): llm-agent-collusion/src/continuous_double_auction/ (market/agents.py,
  prompt_templates/), llm-cartel/environment/oligopoly.py (P0/PC prompts, demand), llm-cartel/harness/.
- The subscription proxy serves gpt-5.4-mini as GPT-6 Luna, gpt-5.4 as GPT-5.6 Sol, claude-3-5-haiku-latest as Claude Haiku 4.5."""


def ask_opus_low(question: str, context: str) -> dict:
    """Answer with claude-opus-5-5 at low effort, with read-only access to this repo and the run outputs.
    The page builds `context` (instructions, live findings, the viewer's selection)."""
    prompt = f"{context}\n\n{REPO_GUIDE}\n\nQUESTION: {question}"
    cmd = [CLAUDE_BIN, "-p", "--no-session-persistence", "--disable-slash-commands", "--setting-sources", "",
           "--strict-mcp-config", "--effort", "low", "--model", "claude-opus-5-5",
           "--tools", ASK_TOOLS, "--allowedTools", ASK_TOOLS, "--add-dir", str(HARNESS)]
    try:  # the prompt goes on stdin: the tool flags take several values and would swallow it
        proc = subprocess.run(cmd, input=prompt, cwd=SPRINT, capture_output=True, text=True, timeout=ASK_TIMEOUT_S)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    answer = proc.stdout.strip()
    if proc.returncode != 0 or not answer:
        return {"ok": False, "error": (proc.stderr or "empty answer").strip()[:300]}
    return {"ok": True, "answer": answer, "model": "claude-opus-5-5 (low, reads the repo)"}


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.end_headers()

    def do_GET(self):
        route = self.path.split("?", 1)[0]
        if route in ("/", "/index.html"):
            self.send(INDEX_PATH.read_bytes(), "text/html; charset=utf-8")
        elif route == "/state.json":
            self.send(STATE_PATH.read_bytes(), "application/json")
        else:
            self.send_error(404)

    def do_POST(self):
        route = self.path.split("?", 1)[0]
        if route == "/api/ask":
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                req = json.loads(raw.decode("utf-8", errors="replace"))
            except Exception:
                req = {}
            q = str(req.get("question") or "").strip()
            ctx = str(req.get("context") or "").strip()
            res = ask_opus_low(q, ctx) if q else {"ok": False, "error": "Empty question"}
            body = json.dumps(res, ensure_ascii=False).encode("utf-8")
            self.send(body, "application/json")
        else:
            self.send_error(404)

    def send(self, body: bytes, ctype: str):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def refresh_forever(interval: float) -> None:
    while True:
        time.sleep(interval)
        try:
            publish(scan())
        except Exception:
            traceback.print_exc()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--once", action="store_true", help="scan once, write state.json and index.html, exit")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8788)
    ap.add_argument("--interval", type=float, default=5.0, help="seconds between rescans")
    args = ap.parse_args()

    state = scan()
    publish(state)
    print(f"[dashboard] scanned in {state['scan_ms']} ms -> {STATE_PATH} ({STATE_PATH.stat().st_size} bytes), embedded in {INDEX_PATH}")
    if args.once:
        return
    threading.Thread(target=refresh_forever, args=(args.interval,), daemon=True).start()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[dashboard] serving http://{args.host}:{args.port}/ (rescan every {args.interval:g} s)")
    server.serve_forever()


if __name__ == "__main__":
    main()
