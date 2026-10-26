"""Primary and secondary endpoints of the pre-specified Sol opening-price test.

Protocol: report_ms/prereg_sol_anchor.md (committed c5a14aa before launch).
Runs: experiments/runs/shard2/prereg_anchor/ (tags frontierP975_* and frontierP90_*, seeds 3 to 8).

Primary endpoint per run: mean of avg_seller_asks_by_round over hours 11 to 15.
Test: per-seed difference (opened at $97.50 minus opened at $90), exact two-sided
paired sign-flip test over the 2^6 = 64 sign patterns of the six differences.

Usage: python report_ms/scripts/prereg_result.py   (prints a Markdown block)
"""
import itertools
import json
import pathlib
import re
import statistics

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNS = REPO / "experiments" / "runs" / "shard2" / "prereg_anchor"
TAG = re.compile(r"frontierP(975|90)_gpt56sol_nocomms_haikuB-seed(\d+)$")


def load():
    rows = {}
    for d in sorted(RUNS.iterdir()):
        m = TAG.search(d.name)
        if not m:
            continue
        cm = json.loads((d / "collusion_metrics.json").read_text(encoding="utf-8"))
        meta = json.loads((d / "experiment_metadata.json").read_text(encoding="utf-8"))
        cfg = meta["auction_config"]
        asks = cm["avg_seller_asks_by_round"]
        jc = cm["joint_criterion"]
        arm = "high" if m.group(1) == "975" else "low"
        assert cfg["rounds"] == 15 and len(asks) == 15, d.name
        assert cfg["initial_seller_ask_center"] == (97.5 if arm == "high" else 90.0), d.name
        assert not cfg["seller_comms_enabled"] and not cfg["seller_dms_enabled"], d.name
        assert not cfg["prohibition_notice"], d.name
        assert set(cfg["seller_models"]) == {"gpt-5.6-sol"}, d.name
        assert set(cfg["buyer_models"]) == {"anthropic/claude-haiku-5.5"}, d.name
        assert cm["failed_turns"] == [], d.name
        tp = [p for p in cm["avg_trade_prices_by_round"][10:] if p is not None]
        rows[(int(m.group(2)), arm)] = dict(
            folder=d.name,
            primary=statistics.mean(asks[10:15]),
            h1=asks[0],
            h15=asks[14],
            ask_index=jc["ask_index"],
            trade_index=jc["trade_index"],
            tpr=jc["trades_per_round"],
            passed=jc["passed"],
            trades=cm["num_trades"],
            late_trade_price=statistics.mean(tp) if tp else None,
            dms=cm["dm_summary"]["total"],
        )
    return rows


def sign_flip_p(diffs):
    obs = abs(statistics.mean(diffs))
    hits = 0
    for signs in itertools.product((1, -1), repeat=len(diffs)):
        if abs(statistics.mean([s * x for s, x in zip(signs, diffs)])) >= obs - 1e-12:
            hits += 1
    return hits, 2 ** len(diffs)


def main():
    rows = load()
    seeds = sorted({s for s, _ in rows})
    complete = [s for s in seeds if (s, "high") in rows and (s, "low") in rows]
    print(f"Runs found: {len(rows)}; complete blocks: {complete}")
    print()
    print("| Seed | Primary, opened $97.50 | Primary, opened $90 | Difference | "
          "Hour-1 ask, $97.50 / $90 | Ask index, $97.50 / $90 | Joint criterion, $97.50 / $90 |")
    print("|---|---|---|---|---|---|---|")
    diffs = []
    for s in complete:
        h, l = rows[(s, "high")], rows[(s, "low")]
        d = h["primary"] - l["primary"]
        diffs.append(d)
        v = lambda r: "pass" if r["passed"] else "fail"
        print(f"| {s} | ${h['primary']:.3f} | ${l['primary']:.3f} | {d:+.3f} | "
              f"${h['h1']:.2f} / ${l['h1']:.2f} | {h['ask_index']:.3f} / {l['ask_index']:.3f} | "
              f"{v(h)} / {v(l)} |")
    hits, n = sign_flip_p(diffs)
    print()
    print(f"Mean difference: {statistics.mean(diffs):+.4f} dollars")
    print(f"Positive differences: {sum(d > 0 for d in diffs)} of {len(diffs)}")
    print(f"Exact two-sided sign-flip p: {hits}/{n} = {hits / n:.5f}")
    for arm in ("high", "low"):
        rs = [rows[(s, arm)] for s in complete]
        print(f"{arm}: passes {sum(r['passed'] for r in rs)} of {len(rs)}; "
              f"primary range ${min(r['primary'] for r in rs):.2f} to ${max(r['primary'] for r in rs):.2f}; "
              f"ask index range {min(r['ask_index'] for r in rs):.3f} to {max(r['ask_index'] for r in rs):.3f}; "
              f"trade index range {min(r['trade_index'] for r in rs):.3f} to {max(r['trade_index'] for r in rs):.3f}; "
              f"trades per hour (last third) {min(r['tpr'] for r in rs):.1f} to {max(r['tpr'] for r in rs):.1f}; "
              f"total trades {min(r['trades'] for r in rs)} to {max(r['trades'] for r in rs)}; "
              f"DMs {sum(r['dms'] for r in rs)}")
    print()
    for (s, arm), r in sorted(rows.items()):
        ltp = "none" if r["late_trade_price"] is None else f"${r['late_trade_price']:.2f}"
        print(f"seed {s} {arm}: {r['folder']}  h15 ${r['h15']:.2f}  late trade price {ltp}  "
              f"trade index {r['trade_index']:.3f}  trades/h {r['tpr']}")


if __name__ == "__main__":
    main()
