"""Read M.S.'s run folders (mert_sprint/experiments/runs/) for the appendix figures adapted from his scripts.

Adapted from M.S.'s mert_sprint/report_ms/scripts/build_ms_runs.py (ref origin/mert_sprint_sync_oct25), by M.S.:
the same fields, read the same way (unified.log: the "Auction configured with" block and the per-hour
"completed with result" records; collusion_metrics.json: joint_criterion, avg_seller_asks_by_round and
dm_summary.total), with his checks (15 hours, no failed turns, public and private messaging flags equal). Change:
his script wrote ms_runs.csv / ms_prereg.csv / ms_quotes.csv under report_ms/data/, which this branch does not
carry; these figures read the run folders directly instead. A folder that is not in the working tree (the
pre-specified test's shard2/prereg_anchor/ is only on ref origin/mert_sprint_sync_oct25 at the time of writing) is
read from that git ref with `git show`, and the source of every folder is reported.
"""
import json
import subprocess
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RUNS = "mert_sprint/experiments/runs"
REF = "origin/mert_sprint_sync_oct25"
SOURCES = {}          # folder -> "disk" or the git ref it was read from


def _git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True, text=True,
                          encoding="utf-8").stdout


def read_text(folder: str, name: str) -> str:
    """A file of a run folder (folder relative to the repository root)."""
    p = REPO / folder / name
    if p.exists():
        SOURCES[folder] = "disk"
        return p.read_text(encoding="utf-8")
    SOURCES[folder] = REF
    return _git("show", f"{REF}:{folder}/{name}")


def list_runs(machine: str, phase: str) -> list[str]:
    """Run folders of one phase, sorted, relative to the repository root."""
    rel = f"{RUNS}/{machine}/{phase}"
    d = REPO / rel
    if d.is_dir():
        return sorted(f"{rel}/{p.name}" for p in d.iterdir() if p.is_dir())
    out = _git("ls-tree", "-d", "--name-only", f"{REF}:{rel}")
    return sorted(f"{rel}/{n}" for n in out.split())


def config(log_text: str) -> dict:
    start = log_text.index("Auction configured with:") + len("Auction configured with:")
    obj, _ = json.JSONDecoder().raw_decode(log_text[start:].lstrip())
    return obj


def rounds(log_text: str) -> list[dict]:
    return [json.loads(x.split("completed with result: ", 1)[1]) for x in log_text.splitlines()
            if "completed with result: " in x]


def one_value(values, what, folder):
    vals = set(values)
    if len(vals) != 1:
        raise ValueError(f"{folder}: {what} is not uniform: {vals}")
    return vals.pop()


@lru_cache(maxsize=None)
def run(folder: str) -> dict:
    """One run: configuration, hourly records, metrics and M.S.'s ms_runs.csv fields."""
    log = read_text(folder, "unified.log")
    cfg = config(log)
    recs = rounds(log)
    met = json.loads(read_text(folder, "collusion_metrics.json"))
    jc = met["joint_criterion"]
    asks = met["avg_seller_asks_by_round"]
    if len(asks) != 15 or len(recs) != 15:
        raise ValueError(f"{folder}: expected 15 hours")
    if met.get("failed_turns"):
        raise ValueError(f"{folder}: failed turns present")
    comms = cfg["seller_comms_enabled"]
    if comms != cfg.get("seller_dms_enabled", False):
        raise ValueError(f"{folder}: public and private messaging flags differ")
    return {
        "folder": folder, "cfg": cfg, "rounds": recs, "metrics": met,
        "seller_model": one_value(cfg["seller_models"], "seller model", folder),
        "buyer_model": one_value(cfg["buyer_models"], "buyer model", folder),
        "messaging": "on" if comms else "off",
        "opening_price": float(cfg["initial_seller_ask_center"]),
        "seed": int(cfg["seed"]),
        "ask_index": jc["ask_index"], "trade_index": jc["trade_index"],
        "trades_per_round": jc["trades_per_round"], "passed": bool(jc["passed"]),
        "private_messages": int(met["dm_summary"]["total"]),
        "asks": list(asks),
    }


def seller_asks(r: dict) -> dict:
    """{seller name: [ask in hour 1..15]} from the hourly records of a run (None where no ask was posted)."""
    names = sorted({s for rec in r["rounds"] for s in rec["seller_asks"]})
    return {s: [rec["seller_asks"].get(s) for rec in r["rounds"]] for s in names}


def plan(r: dict, seller: str, hour: int) -> str:
    """plan_for_this_hour of one seller's response in one hour (the '<seller>.md' file of the run)."""
    text = read_text(r["folder"], f"{seller}.md")
    block = text.split(f"## Response: Round {hour} - ", 1)[1]
    obj, _ = json.JSONDecoder().raw_decode(block[block.index("{"):])
    return obj["plan_for_this_hour"]
