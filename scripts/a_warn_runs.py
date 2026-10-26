"""
Step-A market with the one-sentence warning: per-run table (new sprint code, Oct 25).

Reads the raw runs (results/ is gitignored, so pass the main checkout's results folder) and writes one row per run
to report/data/a_warn/runs.csv: the four Oct 25 runs (warn seeds 0-2, a fresh messaging-on seed 0) and the step-A
comparators at the same seeds (messaging on, messaging off, prohibition notice; GPT-4.1-mini buyers, 4+4, no
scripted seat, so all-seller indices are LLM-only indices).

Every number is recomputed from the per-hour JSON lines in unified.log ("Auction round N completed with result:"),
with the harness's joint criterion (apartcollusion.runs.joint_criterion). The prohibition-notice seeds 0 and 1 ran at
the same time and wrote to one folder (20261024_230119_gemini_notice), so their round lines are split by seller
names (seed 0: Max/Leo/Kai/Raj, seed 1: Zoe/Tara/Amir/Maya, the names in their own console logs). Rate-limit waits
come from each run's console log in <batch>/logs/.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 PYTHONPATH=../../src uv run python ../../scripts/a_warn_runs.py \\
        --results-dir C:/Users/danie/Hackathons/ApartAICollusion/results --out ../../report/data/a_warn/runs.csv
"""

import argparse
import csv
import itertools
import json
import re
from pathlib import Path
from typing import Any, Optional

from apartcollusion.runs import joint_criterion, mean

SEED0 = {"Seller Max", "Seller Leo", "Seller Kai", "Seller Raj"}
SEED1 = {"Seller Zoe", "Seller Tara", "Seller Amir", "Seller Maya"}

# (condition, seed, run folder under results/, console log under results/, seller filter or None, batch note)
RUNS = [
    ("comms", 0, "buyer_probe/20261024_124959_comms_gpt-4.1-mini-seed0",
     "buyer_probe/logs/comms_gpt-4.1-mini-seed0.log", None, "buyer_probe clean rerun, Oct 24 12:49"),
    ("comms", 1, "buyer_probe/20261024_125924_comms_gpt-4.1-mini-seed1",
     "buyer_probe/logs/comms_gpt-4.1-mini-seed1.log", None, "buyer_probe clean rerun, Oct 24 12:59"),
    ("comms", 2, "phase0_v3/20261024_225306_gemini_comms",
     "phase0_v3/logs/gemini_comms-seed2.log", None, "phase0_v3, Oct 24 22:53"),
    ("nocomms", 0, "buyer_probe/20261024_124959_nocomms_gpt-4.1-mini-seed0",
     "buyer_probe/logs/nocomms_gpt-4.1-mini-seed0.log", None, "buyer_probe clean rerun, Oct 24 12:49"),
    ("nocomms", 1, "buyer_probe/20261024_125924_nocomms_gpt-4.1-mini-seed1",
     "buyer_probe/logs/nocomms_gpt-4.1-mini-seed1.log", None, "buyer_probe clean rerun, Oct 24 12:59"),
    ("nocomms", 2, "phase0_v3/20261024_225306_gemini_nocomms",
     "phase0_v3/logs/gemini_nocomms-seed2.log", None, "phase0_v3, Oct 24 22:53"),
    ("notice", 0, "phase0_v3/20261024_230119_gemini_notice",
     "phase0_v3/logs/gemini_notice-seed0.log", SEED0,
     "phase0_v3, Oct 24 23:01; folder shared with seed 1, rounds split by seller names"),
    ("notice", 1, "phase0_v3/20261024_230119_gemini_notice",
     "phase0_v3/logs/gemini_notice-seed1.log", SEED1,
     "phase0_v3, Oct 24 23:01; folder shared with seed 0, rounds split by seller names"),
    ("notice", 2, "phase0_v3/20261024_230729_gemini_notice",
     "phase0_v3/logs/gemini_notice-seed2.log", None, "phase0_v3, Oct 24 23:07"),
    ("warn", 0, "a_warn/20261025_214318_warn-seed0", "a_warn/logs/warn-seed0.log", None, "a_warn, Oct 25 21:43"),
    ("warn", 1, "a_warn/20261025_214318_warn-seed1", "a_warn/logs/warn-seed1.log", None, "a_warn, Oct 25 21:43"),
    ("warn", 2, "a_warn/20261025_214932_warn-seed2", "a_warn/logs/warn-seed2.log", None, "a_warn, Oct 25 21:49"),
    ("comms_oct25", 0, "a_warn/20261025_214932_comms_oct25-seed0", "a_warn/logs/comms_oct25-seed0.log", None,
     "a_warn, Oct 25 21:49; fresh rerun of the comms seed-0 configuration (day-drift check)"),
]

ROUND_RE = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")
CONFIG_KEYS = ("seller_comms_enabled", "seller_dms_enabled", "prohibition_notice", "warning", "report_tool", "seed")


def read_rounds(log: Path, sellers: Optional[set[str]]) -> list[dict[str, Any]]:
    rounds = []
    for line in log.read_text(encoding="utf-8").splitlines():
        m = ROUND_RE.search(line)
        if not m:
            continue
        r = json.loads(m.group(2))
        if sellers is not None and not set(r.get("seller_asks", {})) <= sellers:
            continue
        rounds.append(r)
    rounds.sort(key=lambda r: r["round_number"])
    hours = [r["round_number"] for r in rounds]
    if hours != list(range(1, len(hours) + 1)):
        raise SystemExit(f"{log}: unexpected round sequence {hours}")
    return rounds


def read_config(log: Path) -> list[dict[str, Any]]:
    """Every 'Auction configured with: {...}' block (two in the shared notice folder)."""
    text = log.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"Auction configured with: (\{.*?\n\})", text, flags=re.S):
        out.append(json.loads(m.group(1)))
    return out


def rate_limit_waits(console_log: Path) -> Optional[int]:
    if not console_log.is_file():
        return None
    waits = [int(x) for x in re.findall(r"(\d+) rate-limit waits", console_log.read_text(encoding="utf-8"))]
    return sum(waits) if waits else None


def fmt(x: Optional[float], nd: int = 4) -> str:
    return "" if x is None else f"{x:.{nd}f}"


def summarize(results: Path, cond: str, seed: int, folder: str, console: str, sellers, note: str) -> dict[str, Any]:
    run_dir = results / folder
    metrics = json.loads((run_dir / "collusion_metrics.json").read_text(encoding="utf-8"))
    ce, cartel = metrics["competitive_equilibrium_price"], metrics["joint_profit_maximization_price"]
    rounds = read_rounds(run_dir / "unified.log", sellers)
    configs = read_config(run_dir / "unified.log")
    config = next(c for c in configs if c.get("seed") == seed)

    asks = [mean(list(r["seller_asks"].values())) for r in rounds]
    trade_prices = [mean([t["price"] for t in r.get("trades", [])]) for r in rounds]
    trades = [len(r.get("trades", [])) for r in rounds]
    jc = joint_criterion(asks, trade_prices, trades, ce, cartel)
    idx = lambda p: None if p is None else (p - ce) / (cartel - ce)  # noqa: E731

    dms = [len(r.get("seller_dms") or []) for r in rounds]
    public = [sum(1 for v in (r.get("seller_messages") or {}).values() if v and str(v).strip()) for r in rounds]
    failed = sum(len(r.get("failed_turns") or []) for r in rounds)
    n = len(rounds)
    sellers_seen = sorted({s for r in rounds for s in r["seller_asks"]})
    return {
        "condition": cond,
        "seed": seed,
        "run_folder": folder,
        "batch": note,
        "sellers": ";".join(s.replace("Seller ", "") for s in sellers_seen),
        "seller_models": ";".join(sorted(set(config["seller_models"]))),
        "buyer_models": ";".join(sorted(set(config["buyer_models"]))),
        "messaging": "on" if config.get("seller_comms_enabled") else "off",
        "private_messages_enabled": "on" if config.get("seller_dms_enabled") else "off",
        "prohibition_notice": "on" if config.get("prohibition_notice") else "off",
        "warning": "on" if config.get("warning") else "off",
        "report_action": "on" if config.get("report_tool") else "off",
        "rounds": n,
        "last_third_ask_index": fmt(jc["ask_index"]),
        "last_third_trade_index": fmt(jc["trade_index"]),
        "last_third_trades_per_round": fmt(jc["trades_per_round"], 2),
        "joint_criterion_pass": "PASS" if jc["passed"] else "FAIL",
        "ask_index_all_hours": fmt(mean([idx(a) for a in asks])),
        "harness_ask_index": fmt((metrics.get("joint_criterion") or {}).get("ask_index")) if sellers is None else "",
        "private_messages_total": sum(dms),
        "private_messages_per_hour": fmt(sum(dms) / n, 2),
        "private_messages_by_hour": ";".join(map(str, dms)),
        "hours_with_private_messages": sum(1 for d in dms if d),
        "public_messages_total": sum(public),
        "public_messages_per_hour": fmt(sum(public) / n, 2),
        "public_messages_by_hour": ";".join(map(str, public)),
        "mean_ask_hour1": fmt(asks[0], 2),
        "mean_ask_hour3": fmt(asks[2], 2),
        "mean_ask_hour15": fmt(asks[-1], 2),
        "failed_turns": failed,
        "rate_limit_waits": rate_limit_waits(results / console),
    }


def perm_p(a: list[float], b: list[float]) -> float:
    """Exact two-sided permutation p for a difference in means (all relabelings of the pooled values)."""
    pooled, k = a + b, len(a)
    obs = abs(sum(a) / len(a) - sum(b) / len(b))
    hits = total = 0
    for idx in itertools.combinations(range(len(pooled)), k):
        xa = [pooled[i] for i in idx]
        xb = [pooled[i] for i in range(len(pooled)) if i not in idx]
        total += 1
        hits += abs(sum(xa) / len(xa) - sum(xb) / len(xb)) >= obs - 1e-12
    return hits / total


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = [summarize(args.results_dir, *spec) for spec in RUNS]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {args.out} ({len(rows)} rows)")

    # Condition means over seeds 0-2 and the share of the communication premium kept.
    ask = {c: [float(r["last_third_ask_index"]) for r in rows if r["condition"] == c]
           for c in ("comms", "nocomms", "notice", "warn")}
    m = {c: sum(v) / len(v) for c, v in ask.items()}
    for c, v in ask.items():
        print(f"{c:8s} seeds 0-2 ask index {', '.join(f'{x:+.3f}' for x in v)}  mean {m[c]:+.4f}")
    premium = m["comms"] - m["nocomms"]
    for c in ("warn", "notice"):
        print(f"share of the comms premium kept, {c}: ({m[c]:+.4f} - {m['nocomms']:+.4f}) / {premium:.4f} = "
              f"{(m[c] - m['nocomms']) / premium:.2f}")
    oct25 = next(float(r["last_third_ask_index"]) for r in rows if r["condition"] == "comms_oct25")
    m_alt = (oct25 + sum(ask["comms"][1:])) / 3
    print(f"  with comms seed 0 = comms_oct25 ({oct25:+.4f}): comms mean {m_alt:+.4f}, warn share "
          f"{(m['warn'] - m['nocomms']) / (m_alt - m['nocomms']):.2f}")
    for a, b in (("warn", "comms"), ("warn", "nocomms"), ("warn", "notice"), ("notice", "nocomms"),
                 ("comms", "nocomms")):
        print(f"exact permutation p (two-sided, 3 vs 3, 20 splits), {a} vs {b}: {perm_p(ask[a], ask[b]):.2f}")


if __name__ == "__main__":
    main()
