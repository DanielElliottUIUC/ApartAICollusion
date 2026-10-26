"""Build the S3 tables from our run folders (read-only) into report_ms/supplement/data/S3/.

Writes:
  runs.csv        one row per run: folder, block, tag, seller, buyer, messaging, notice, opening, seed,
                  ask_index, trade_index, trades_per_round, passed (joint_criterion of collusion_metrics.json),
                  private_messages (dm_summary.total), public_messages and hours_logged (from unified.log),
                  failed_turns (summed over the rounds of unified.log)
  hours.csv       one row per run and hour: mean_ask (avg_seller_asks_by_round), private (len seller_dms),
                  public (non-empty seller_messages), trades (len trades)
  sellers_h1.csv  one row per seller: the ask the harness seeded for it (Hour 1 prompt of the seller file) and
                  the ask it posted in hour 1 (seller_asks of round 1 in unified.log)
  books.csv       the seeded opening book of every run: side (ask or bid), agent, price
  grok_judge.csv  per-seller mean coordination score of the Grok 4.7 judge (judge_grok-4.7_summary.json)

The run in s3lib.BROKEN_LOG has a unified.log and metrics file that stop after hour 1; it is kept in runs.csv
with hours_logged = 1 and gets no rows in hours.csv. experiments/invalid_429_shard3/ is never read.

Run from anywhere:  python report_ms/supplement/scripts/S3/build_s3_data.py
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s3lib  # noqa: E402


def write(name, rows):
    s3lib.S3DATA.mkdir(parents=True, exist_ok=True)
    with open(s3lib.S3DATA / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to data/S3/{name}")


def one(values, what, folder):
    vals = set(values)
    if len(vals) != 1:
        raise ValueError(f"{folder}: {what} not uniform: {vals}")
    return vals.pop()


def main():
    runs, hours, sellers, books, judge = [], [], [], [], []
    for rel, block in s3lib.run_folders():
        d = s3lib.RUNS / rel
        log = (d / "unified.log").read_text(encoding="utf-8")
        cfg = s3lib.read_config(log)
        rounds = s3lib.read_rounds(log)
        met = json.loads((d / "collusion_metrics.json").read_text(encoding="utf-8"))
        jc = met["joint_criterion"]
        comms = bool(cfg["seller_comms_enabled"])
        if comms != bool(cfg.get("seller_dms_enabled", False)):
            raise ValueError(f"{rel}: public and private messaging flags differ")
        broken = rel == s3lib.BROKEN_LOG
        if not broken and (len(rounds) != 15 or len(met["avg_seller_asks_by_round"]) != 15):
            raise ValueError(f"{rel}: expected 15 hours")
        if broken and len(rounds) != 1:
            raise ValueError(f"{rel}: expected the known 1-hour log")
        seller = s3lib.SELLER_KEY[one(cfg["seller_models"], "seller model", rel)]
        buyer = s3lib.BUYER_KEY[one(cfg["buyer_models"], "buyer model", rel)]
        runs.append({
            "folder": rel, "block": block, "tag": cfg["tag"], "seller": seller, "buyer": buyer,
            "messaging": "on" if comms else "off", "notice": bool(cfg.get("prohibition_notice", False)),
            "opening": float(cfg["initial_seller_ask_center"]), "seed": int(cfg["seed"]),
            "ask_index": jc["ask_index"], "trade_index": jc["trade_index"],
            "trades_per_round": jc["trades_per_round"], "passed": bool(jc["passed"]),
            "private_messages": int(met["dm_summary"]["total"]),
            "public_messages": sum(1 for r in rounds for v in (r.get("seller_messages") or {}).values() if v),
            "hours_logged": len(rounds),
            "failed_turns": sum(len(r.get("failed_turns") or []) for r in rounds),
        })
        if not broken:
            for r, a in zip(rounds, met["avg_seller_asks_by_round"]):
                hours.append({"folder": rel, "hour": r["round_number"], "mean_ask": a,
                              "private": len(r.get("seller_dms") or []),
                              "public": sum(1 for v in (r.get("seller_messages") or {}).values() if v),
                              "trades": len(r.get("trades") or [])})
        asks, bids = s3lib.seeded_book(d)
        for side, book in (("ask", asks), ("bid", bids)):
            for agent, p in book.items():
                books.append({"folder": rel, "seed": int(cfg["seed"]), "opening": float(cfg["initial_seller_ask_center"]),
                              "side": side, "agent": agent, "price": p})
        h1 = rounds[0]
        if h1["round_number"] != 1:
            raise ValueError(f"{rel}: first logged round is not hour 1")
        for name, seeded in asks.items():
            sellers.append({"folder": rel, "seller_name": name, "seeded_ask": seeded,
                            "h1_ask": h1["seller_asks"].get(name)})
        jf = d / "judge_grok-4.7_summary.json"
        if jf.exists():
            js = json.loads(jf.read_text(encoding="utf-8"))
            if js["judge_model"] != "grok-4.7":
                raise ValueError(f"{rel}: unexpected judge {js['judge_model']}")
            for sid, s in js["sellers"].items():
                judge.append({"folder": rel, "seller_id": sid, "rounds_scored": s["rounds_scored"],
                              "rounds_failed": s["rounds_failed"], "mean_score": s["mean_coordination_score"]})
    write("runs.csv", runs)
    write("hours.csv", hours)
    write("sellers_h1.csv", sellers)
    write("books.csv", books)
    write("grok_judge.csv", judge)


if __name__ == "__main__":
    main()
