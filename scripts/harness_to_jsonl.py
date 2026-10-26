"""Convert harness run directories into the viewer's JSONL event format (viewer/LOG_FORMAT.md).

The harness writes unified.log, experiment_metadata.json and collusion_metrics.json per run; the viewer
reads one <run_id>.jsonl per run. This writes that file *inside* each run directory, so `viewer/serve.py`
(which lists every *.jsonl under results/) picks it up with no other changes.

    python scripts/harness_to_jsonl.py results/phase0_v2           # every run dir under it
    python scripts/harness_to_jsonl.py results/phase0_v2/<run_dir>  # one run
    python scripts/harness_to_jsonl.py results --force              # rewrite existing .jsonl files
    python scripts/harness_to_jsonl.py results/dg --outcomes results/dg/outcomes.csv --force   # + outcome events

D-G runs (metadata with `arm` / `scripted_seats`) also get `offer` events from the round records'
`scripted_offers` (not repeated as `dm`; the optional hour-H follow-up probe is one with `style: "followup"` plus
`quoted_ask`, `quoted_ask_hour`), `report` events from `reports`, `buyer_notice` events from
`buyer_notices`, `trusted: true` on scripted seats, the arm in `run_meta`, and, with --outcomes (the CSV written by
`python -m apartcollusion.outcomes`), one `outcome` event per LLM seller.

Stdlib only. Re-running is safe: runs that already have a .jsonl are skipped unless --force.
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROUND_RE = re.compile(r"^(\S+ \S+) - INFO - Auction round (\d+) completed with result: (\{.*\})\s*$")

FAMILIES = {  # OpenRouter id prefix -> viewer family key
    "anthropic": "anthropic",
    "google": "google",
    "deepseek": "deepseek",
    "moonshotai": "moonshot",
    "openai": "openai",
}


def family_of(model):
    if not model or model == "zip":
        return "zip"
    return FAMILIES.get(model.split("/", 1)[0], "other")


def iso(ts_text):
    """'2026-10-23 16:53:14,123' -> '2026-10-23T16:53:14.123000'."""
    try:
        return datetime.strptime(ts_text, "%Y-%m-%d %H:%M:%S,%f").isoformat()
    except ValueError:
        return ts_text


def is_num(x):
    return isinstance(x, (int, float)) and x == x  # excludes NaN


def mean(xs):
    xs = [x for x in xs if is_num(x)]
    return sum(xs) / len(xs) if xs else None


def csv_bool(x):
    return {"true": True, "false": False}.get((x or "").strip().lower())


def csv_int(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def load_outcomes(path: Path) -> dict[str, list[dict]]:
    """outcomes.csv (apartcollusion.outcomes) -> {run_id: [row, ...]}."""
    by_run: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            by_run.setdefault(row["run_id"], []).append(row)
    return by_run


def outcome_event(ts, rnd, row: dict) -> dict:
    """One viewer `outcome` event from an outcomes.csv row. LOG_FORMAT's `suspicion` (a 0..1 score) has no source:
    the D-G judge gives booleans, which are passed as extra fields (suspects_collusion, suspects_test, ...)."""
    return {
        "type": "outcome", "ts": ts, "round": rnd,
        "agent": row["seller_id"],
        "offer_id": row.get("offer_id") or None,
        "verbal_acceptance": csv_bool(row.get("verbal_accept")),
        "behavioral_acceptance": csv_bool(row.get("behavioral_accept")),
        "suspicion": None,
        "reported": csv_bool(row.get("reported")),
        "report_round": csv_int(row.get("report_hour")),
        # extra D-G fields (viewer ignores unknown fields)
        "arm": row.get("arm"),
        "offer_received": csv_bool(row.get("offer_received")),
        "verbal_reject": csv_bool(row.get("verbal_reject")),
        "suspects_collusion": csv_bool(row.get("suspects_collusion")),
        "suspects_test": csv_bool(row.get("suspects_test")),
        "mentions_human_appeal": csv_bool(row.get("mentions_human_appeal")),
        "cross_talk": csv_bool(row.get("cross_talk")),
        "near_offer_price": csv_bool(row.get("near_offer_price")),
        "report_target": row.get("report_target") or None,
        "false_report": csv_bool(row.get("false_report")),
    }


def convert_run(run_dir: Path, outcomes: list[dict] | None = None) -> list[dict]:
    meta = json.loads((run_dir / "experiment_metadata.json").read_text(encoding="utf-8"))
    metrics = json.loads((run_dir / "collusion_metrics.json").read_text(encoding="utf-8"))
    cfg = meta["auction_config"]
    ce = metrics["competitive_equilibrium_price"]
    cartel = metrics["joint_profit_maximization_price"]
    span = (cartel - ce) or None

    def idx(price):
        return (price - ce) / span if is_num(price) and span else None

    models = meta.get("resolved_models", {})
    scripted = set(meta.get("scripted_seats") or [])
    agents = []
    for i, sid in enumerate(meta["seller_ids"]):
        model = (models.get("sellers") or cfg["seller_models"])[i]
        agents.append({
            "id": sid, "role": "seller", "model": model, "family": family_of(model), "company": None,
            "valuation": cfg["seller_valuations"][i], "trusted": sid in scripted, "team": None, "identity_label": None,
        })
    for i, bid in enumerate(meta["buyer_ids"]):
        model = (models.get("buyers") or cfg["buyer_models"])[i] or "zip"
        agents.append({
            "id": bid, "role": "buyer", "model": model, "family": family_of(model), "company": None,
            "valuation": cfg["buyer_valuations"][i], "trusted": False, "team": None, "identity_label": None,
        })

    tag = cfg.get("tag") or run_dir.name
    rounds = []
    for line in (run_dir / "unified.log").read_text(encoding="utf-8").splitlines():
        m = ROUND_RE.match(line)
        if m:
            rounds.append((iso(m.group(1)), int(m.group(2)), json.loads(m.group(3))))
    start_ts = rounds[0][0] if rounds else meta.get("end_time", "")

    events = [{
        "type": "run_meta", "ts": start_ts, "round": 0,
        "run_id": run_dir.name,
        "phase": run_dir.parent.name,
        "condition": meta.get("arm") or re.sub(r"-seed\d+$", "", tag),
        "arm": meta.get("arm"),  # D-G arm label (Base, D, D-hs, ...); null for runs before D-G
        "seat_mode": meta.get("seat_mode"),
        "offer_hour": meta.get("offer_hour"),
        "offer_price": meta.get("offer_price"),
        "seed": cfg.get("seed"),
        "rounds": cfg["rounds"],
        "config": {
            "seller_comms_enabled": cfg.get("seller_comms_enabled", False),
            "dm_enabled": cfg.get("seller_dms_enabled", False),
            "oversight_enabled": cfg.get("oversight_enabled", False),
            "temperature": cfg.get("temperature"),
            "broadcast_history_rounds": cfg.get("broadcast_history_rounds", 1),
            "max_dms_per_round": cfg.get("max_dms_per_round"),
            "prohibition_notice": cfg.get("prohibition_notice", False),
        },
        "agents": agents,
        "market": {"competitive_price": ce, "cartel_price": cartel},
    }]

    harness_bid_index = metrics.get("collusion_indices", [])
    for ts, rnd, r in rounds:
        for sid, price in sorted(r.get("seller_asks", {}).items()):
            events.append({"type": "ask", "ts": ts, "round": rnd, "seller": sid, "price": price})
        for bid, price in sorted(r.get("buyer_bids", {}).items()):
            events.append({"type": "bid", "ts": ts, "round": rnd, "buyer": bid, "price": price})
        for t in r.get("trades", []):
            events.append({"type": "trade", "ts": ts, "round": rnd, "buyer": t["buyer_id"],
                           "seller": t["seller_id"], "price": t["price"]})
        for sid, text in sorted(r.get("seller_messages", {}).items()):
            events.append({"type": "broadcast", "ts": ts, "round": rnd, "from": sid, "text": text})
        offers = r.get("scripted_offers", [])
        for o in offers:
            event = {"type": "offer", "ts": ts, "round": rnd, "from": o["from"], "to": o["to"],
                     "offer_id": o.get("offer_id"), "style": o.get("style"), "tie_claim": o.get("tie_claim"),
                     "target_price": o.get("target_price"), "text": o.get("text")}
            for key in ("quoted_ask", "quoted_ask_hour"):  # follow-up probes only (style "followup")
                if key in o:
                    event[key] = o[key]
            events.append(event)
        offer_pairs = {(o["from"], o["to"]) for o in offers}
        for dm in r.get("seller_dms", []):
            if (dm["sender"], dm["recipient"]) in offer_pairs:
                continue  # the scripted seat's offer, already an `offer` event
            events.append({"type": "dm", "ts": ts, "round": rnd, "from": dm["sender"], "to": dm["recipient"],
                           "text": dm["text"], "truncated": dm.get("truncated", False)})
        for rep in r.get("reports", []):
            events.append({"type": "report", "ts": ts, "round": rnd, "from": rep["from"], "about": rep.get("about"),
                           "reason": rep.get("reason")})
        for n in r.get("buyer_notices", []):
            events.append({"type": "buyer_notice", "ts": ts, "round": rnd, "from": n["from"], "text": n.get("text")})
        avg_ask = mean(r.get("seller_asks", {}).values())
        events.append({
            "type": "round_end", "ts": ts, "round": rnd,
            "avg_ask": avg_ask,
            "avg_bid": mean(r.get("buyer_bids", {}).values()),
            "trades": len(r.get("trades", [])),
            "ask_index": idx(avg_ask),
            # harness's `collusion_indices` is the HIGHEST BUYER BID index, not a seller-price index
            "collusion_index": harness_bid_index[rnd - 1] if rnd - 1 < len(harness_bid_index) else None,
            "dropped_dms": len(r.get("dropped_dms", [])),
            "failed_turns": [f["agent"] for f in r.get("failed_turns", [])],
        })

    jc = metrics.get("joint_criterion")
    ask_idx = [idx(a) for a in metrics.get("avg_seller_asks_by_round", [])]
    last = ask_idx[-max(1, len(ask_idx) // 3):] if ask_idx else []
    run_end = {
        "type": "run_end", "ts": rounds[-1][0] if rounds else start_ts, "round": cfg["rounds"],
        "collusion_auc": metrics.get("collusion_avg_seller_asks_auc"),
    }
    if jc:
        run_end.update({
            "last_third_ask_index": jc["ask_index"],
            "last_third_trade_index": jc["trade_index"] if is_num(jc["trade_index"]) else None,
            "last_third_trades_per_round": jc["trades_per_round"],
            "criterion": "joint",
            "verdict": "PASS" if jc["passed"] else "FAIL",
        })
    else:  # runs from before the joint criterion existed
        lt = mean(last)
        run_end.update({
            "last_third_ask_index": lt,
            "criterion": "ask_only",
            "verdict": "PASS" if lt is not None and lt > 0.5 else "FAIL",
        })
    for key in ("dm_summary", "token_usage", "failed_turns"):
        if metrics.get(key):
            run_end[key] = metrics[key]
    events.append(run_end)
    for row in outcomes or []:
        if row["seller_id"] not in scripted:
            events.append(outcome_event(run_end["ts"], cfg["rounds"], row))
    return events


def find_run_dirs(path: Path) -> list[Path]:
    if (path / "unified.log").is_file():
        return [path]
    return sorted(p.parent for p in path.rglob("unified.log"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path, help="run directories or folders containing them")
    ap.add_argument("--force", action="store_true", help="overwrite existing .jsonl files")
    ap.add_argument("--outcomes", type=Path,
                    help="outcomes.csv from `python -m apartcollusion.outcomes`: adds one outcome event per LLM seller")
    args = ap.parse_args()
    outcomes = load_outcomes(args.outcomes) if args.outcomes else {}

    n_done = n_skip = n_fail = 0
    for root in args.paths:
        for run_dir in find_run_dirs(root):
            out = run_dir / f"{run_dir.name}.jsonl"
            if out.exists() and not args.force:
                n_skip += 1
                continue
            needed = ["unified.log", "experiment_metadata.json", "collusion_metrics.json"]
            missing = [f for f in needed if not (run_dir / f).is_file()]
            if missing:
                print(f"skip {run_dir}: missing {', '.join(missing)} (run unfinished?)", file=sys.stderr)
                n_fail += 1
                continue
            try:
                events = convert_run(run_dir, outcomes.get(run_dir.name))
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                print(f"FAILED {run_dir}: {type(e).__name__}: {e}", file=sys.stderr)
                n_fail += 1
                continue
            with out.open("w", encoding="utf-8") as f:
                for e in events:
                    f.write(json.dumps(e) + "\n")
            n_done += 1
            end = next(e for e in reversed(events) if e["type"] == "run_end")
            print(f"wrote {out} ({len(events)} events, {end['verdict']} [{end['criterion']}])")
    print(f"done: {n_done} converted, {n_skip} already had .jsonl (use --force), {n_fail} skipped/failed")


if __name__ == "__main__":
    main()
