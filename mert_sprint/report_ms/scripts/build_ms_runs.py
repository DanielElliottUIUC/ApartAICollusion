"""Build report_ms/data/ms_runs.csv, ms_prereg.csv and ms_quotes.csv from our run folders.

One row per run of ours that the report uses (60 runs):
  experiments/runs/{box,shard2}/frontier/*            36 frontier runs (Sol, Luna, Grok sellers)
  experiments/runs/shard2/frontier_b41/*               6 Sol runs with GPT-4.1-mini buyers
  experiments/runs/shard2/frontier_lowanchor/*         9 runs with asks opened at $90 (Sol off/on, Luna off)
  experiments/runs/shard2/A_lowanchor/*                6 Gemini runs (agy route) opened at $90
  experiments/runs/shard2/A_agycontrol/*               3 Gemini runs (agy route) at the default $97.50 opening

One row per run of the pre-specified Sol opening-price test, same columns (12 runs, data/ms_prereg.csv):
  experiments/runs/shard2/prereg_anchor/*              Sol sellers, Haiku 5.5 buyers, messaging off,
                                                       opened at $97.50 or $90, seeds 3 to 8 (Figure 4c)

Sources inside each run folder:
  unified.log             the "Auction configured with" block gives seller and buyer models, messaging flags,
                          seed and initial_seller_ask_center (the opening price, 90.0 or 97.5); the per-round
                          "completed with result" lines give the seller private messages used for the quotes.
  collusion_metrics.json  joint_criterion (ask_index, trade_index, trades_per_round, passed),
                          avg_seller_asks_by_round (mean ask by hour 1..15) and dm_summary.total.

experiments/invalid_429_shard3/ is never read.

Run from anywhere:  python report_ms/scripts/build_ms_runs.py
"""
import csv
import glob
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "experiments" / "runs"
OUT = REPO / "report_ms" / "data"

PHASES = [
    ("box", "frontier"),
    ("shard2", "frontier"),
    ("shard2", "frontier_b41"),
    ("shard2", "frontier_lowanchor"),
    ("shard2", "A_lowanchor"),
    ("shard2", "A_agycontrol"),
]
PREREG_PHASES = [("shard2", "prereg_anchor")]

# The two Figure 4b call-outs: (run folder, hour, sender, recipient). The full message text is copied
# from unified.log into ms_quotes.csv; the figure script checks that each call-out is a substring of it.
QUOTES = [
    ("shard2/A_lowanchor/20261025_191318_danielA_L90_gemini_comms_gpt41miniB-seed0", 1, "Seller Kai", "Seller Max"),
    ("shard2/A_lowanchor/20261025_191318_danielA_L90_gemini_comms_gpt41miniB-seed0", 12, "Seller Kai", "Seller Leo"),
]


def read_config(log_text):
    """Return the JSON object that follows 'Auction configured with:' in unified.log."""
    start = log_text.index("Auction configured with:") + len("Auction configured with:")
    obj, _ = json.JSONDecoder().raw_decode(log_text[start:].lstrip())
    return obj


def read_rounds(log_text):
    rounds = []
    for line in log_text.splitlines():
        if "completed with result: " in line:
            rounds.append(json.loads(line.split("completed with result: ", 1)[1]))
    return rounds


def one_value(values, what, folder):
    vals = set(values)
    if len(vals) != 1:
        raise ValueError(f"{folder}: {what} is not uniform: {vals}")
    return vals.pop()


def build_runs(phases):
    rows = []
    for machine, phase in phases:
        for d in sorted(glob.glob(str(RUNS / machine / phase / "*"))):
            d = Path(d)
            log = (d / "unified.log").read_text(encoding="utf-8")
            cfg = read_config(log)
            met = json.loads((d / "collusion_metrics.json").read_text(encoding="utf-8"))
            jc = met["joint_criterion"]
            asks = met["avg_seller_asks_by_round"]
            if len(asks) != 15 or len(read_rounds(log)) != 15:
                raise ValueError(f"{d}: expected 15 hours")
            if met.get("failed_turns"):
                raise ValueError(f"{d}: failed turns present")
            comms = cfg["seller_comms_enabled"]
            if comms != cfg.get("seller_dms_enabled", False):
                raise ValueError(f"{d}: public and private messaging flags differ")
            row = {
                "folder": d.relative_to(REPO).as_posix(),
                "phase": phase,
                "seller_model": one_value(cfg["seller_models"], "seller model", d),
                "buyer_model": one_value(cfg["buyer_models"], "buyer model", d),
                "messaging": "on" if comms else "off",
                "opening_price": float(cfg["initial_seller_ask_center"]),
                "seed": int(cfg["seed"]),
                "ask_index": jc["ask_index"],
                "trade_index": jc["trade_index"],
                "trades_per_round": jc["trades_per_round"],
                "passed": bool(jc["passed"]),
                "private_messages": int(met["dm_summary"]["total"]),
            }
            for h, a in enumerate(asks, start=1):
                row[f"ask_h{h}"] = a
            rows.append(row)
    return rows


def build_quotes():
    rows = []
    for folder, hour, sender, recipient in QUOTES:
        log = (RUNS / folder / "unified.log").read_text(encoding="utf-8")
        hits = [
            dm["text"]
            for r in read_rounds(log) if r["round_number"] == hour
            for dm in (r.get("seller_dms") or [])
            if dm["sender"] == sender and dm["recipient"] == recipient
        ]
        if len(hits) != 1:
            raise ValueError(f"{folder} hour {hour}: expected one message {sender} -> {recipient}, found {len(hits)}")
        rows.append({
            "folder": f"experiments/runs/{folder}",
            "hour": hour,
            "sender": sender,
            "recipient": recipient,
            "channel": "private",
            "text": hits[0],
        })
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    runs = build_runs(PHASES)
    prereg = build_runs(PREREG_PHASES)
    write_csv(OUT / "ms_runs.csv", runs)
    write_csv(OUT / "ms_prereg.csv", prereg)
    write_csv(OUT / "ms_quotes.csv", build_quotes())
    print(f"wrote {len(runs)} runs to {OUT / 'ms_runs.csv'}, {len(prereg)} runs to {OUT / 'ms_prereg.csv'} "
          f"and {len(QUOTES)} quotes to {OUT / 'ms_quotes.csv'}")
