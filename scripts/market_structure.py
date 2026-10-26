"""Effective market structure of the 5+5 D-G markets (new sprint code; reads raw runs, no API calls).

Every D-G market has five sellers (four LLM sellers plus the scripted seat 5, `scripted_seats` in
experiment_metadata.json) and five buyers, each trading at most one unit per hour: the harness matches the
lowest ask with the highest bid, removes both, and repeats while they cross (market/market.py,
resolve_trades_if_any). With seller cost $80 and buyer value $100 for every agent, the harness calls $90
(the midpoint of the $80-100 clearing range) the competitive price. This script asks what the runs
actually look like:

- who trades: total trades, trades by seat (seats 1-4 = LLM sellers in `seller_ids` order, seat 5 = scripted),
  seat 5's share, trades per hour and how many of the five buyers trade each hour (all hours and last third);
- whether the LLM sellers are the short side: hours in which all four LLM sellers sold, and the best bid of
  the buyers left unmatched in that hour (from that hour's submitted bids) against seat 5's ask;
- seat 5's ask path against the LLM sellers' asks (seat 5's ask is the price of the marginal fifth unit, so it
  is a lower bound on any price at which all five buyers are served);
- price direction: per-seller ask changes between consecutive hours (raises > $0 and > $1, cuts, unchanged);
- the pre-trend check: slope of the hourly mean LLM ask over hours 1-3 (before the offer is visible) and
  hours 3-6 (after), by OLS on the hourly means and by endpoints.

Round records are read from unified.log ("Auction round N completed with result: {json}"), so this does not
depend on auction_results.md or on the analysis package.

    PYTHONUTF8=1 uv run --project third_party/llm-agent-collusion python scripts/market_structure.py \\
        --results-root C:/Users/danie/Hackathons/ApartAICollusion/results/dg

writes report/data/dg/market_structure.csv (one row per run; --out to change) and prints the pooled numbers,
per-arm pre-trend slopes and an exact permutation test of the D-vs-Base difference in slope change.
"""

import argparse
import itertools
import json
import re
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Optional

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
ARM_ORDER = ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "G-warn", "G-prec", "F-sham", "Base-hb"]
ROUND_RE = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")


def load_rounds(log: Path) -> list[dict[str, Any]]:
    rounds = []
    for line in log.read_text(encoding="utf-8").splitlines():
        m = ROUND_RE.search(line)
        if m:
            rec = json.loads(m.group(2))
            assert rec["round_number"] == int(m.group(1)), log
            rounds.append(rec)
    return sorted(rounds, key=lambda r: r["round_number"])


def last_third(n: int) -> int:
    """Rounds in the last third, as the harness's joint criterion counts them (15 hours -> 5)."""
    return max(1, n // 3) if n else 0


def ols_slope(hours: list[int], values: list[Optional[float]]) -> Optional[float]:
    pts = [(h, v) for h, v in zip(hours, values) if v is not None]
    if len(pts) < 2:
        return None
    x, y = np.array([p[0] for p in pts], float), np.array([p[1] for p in pts], float)
    return float(np.polyfit(x, y, 1)[0])


def avg(xs) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return float(mean(xs)) if xs else None


def analyze(run_dir: Path) -> dict[str, Any]:
    meta = json.loads((run_dir / "experiment_metadata.json").read_text(encoding="utf-8"))
    rounds = load_rounds(run_dir / "unified.log")
    sellers = list(meta["seller_ids"])
    buyers = list(meta["buyer_ids"])
    scripted = list(meta.get("scripted_seats") or [])
    assert len(scripted) == 1, f"{run_dir.name}: expected one scripted seat, got {scripted}"
    s5 = scripted[0]
    llm = [s for s in sellers if s != s5]
    hours = [r["round_number"] for r in rounds]
    n = len(rounds)
    lt = rounds[-last_third(n):]
    lt_hours = {r["round_number"] for r in lt}

    def ask(r, s):
        v = r.get("seller_asks", {}).get(s)
        return float(v) if isinstance(v, (int, float)) else None

    trades = [t for r in rounds for t in r.get("trades", [])]
    by_seller = {s: sum(t["seller_id"] == s for t in trades) for s in sellers}
    row: dict[str, Any] = {
        "run_id": run_dir.name, "arm": meta.get("arm"), "seed": meta["auction_config"]["seed"]
        if isinstance(meta.get("auction_config"), dict) else None,
        "seat_mode": meta.get("seat_mode"), "offer_hour": meta.get("offer_hour"),
        "offer_price": meta.get("offer_price"), "scripted_seat": s5,
        "scripted_seat_position": sellers.index(s5) + 1, "seller_order": ";".join(sellers), "n_hours": n,
        "trades_total": len(trades), "trades_llm": len(trades) - by_seller[s5], "trades_seat5": by_seller[s5],
        "seat5_trade_share": by_seller[s5] / len(trades) if trades else None,
        "seat5_trade_hours": ";".join(str(r["round_number"]) for r in rounds
                                      for t in r.get("trades", []) if t["seller_id"] == s5),
    }
    for i, s in enumerate(sellers, 1):  # by position in seller_ids (the scripted seat is position 5 in every D-G run)
        row[f"trades_pos{i}"] = by_seller[s]

    per_hour = []
    for r in rounds:
        tr = r.get("trades", [])
        traded_buyers = {t["buyer_id"] for t in tr}
        llm_sold = {t["seller_id"] for t in tr if t["seller_id"] in llm}
        bids = {b: float(v) for b, v in r.get("buyer_bids", {}).items() if isinstance(v, (int, float))}
        unmatched = [v for b, v in bids.items() if b not in traded_buyers]
        a5 = ask(r, s5)
        llm_asks = [a for a in (ask(r, s) for s in llm) if a is not None]
        per_hour.append({
            "hour": r["round_number"], "trades": len(tr), "llm_trades": len(llm_sold),
            "buyers_trading": len(traded_buyers), "all4_llm_sold": len(llm_sold) == len(llm),
            "seat5_traded": any(t["seller_id"] == s5 for t in tr),
            "best_unmatched_bid": max(unmatched) if unmatched else None,
            "seat5_ask": a5, "llm_mean_ask": avg(llm_asks), "llm_min_ask": min(llm_asks) if llm_asks else None,
            "llm_max_ask": max(llm_asks) if llm_asks else None,
        })
    ph = pd.DataFrame(per_hour)
    phl = ph[ph["hour"].isin(lt_hours)]
    after = ph[ph["hour"] >= (meta.get("offer_hour") or 3)]
    row.update({
        "trades_per_hour": ph["trades"].mean(),
        "trades_per_hour_last_third": phl["trades"].mean(),
        "llm_trades_per_hour_last_third": phl["llm_trades"].mean(),
        "buyers_trading_per_hour": ph["buyers_trading"].mean(),
        "buyers_trading_per_hour_last_third": phl["buyers_trading"].mean(),
        "hours_with_trade": int((ph["trades"] > 0).sum()),
        "hours_5_buyers_traded": int((ph["buyers_trading"] == len(buyers)).sum()),
        "hours_5_buyers_traded_last_third": int((phl["buyers_trading"] == len(buyers)).sum()),
        "hours_all4_llm_sold": int(ph["all4_llm_sold"].sum()),
        "hours_all4_llm_sold_last_third": int(phl["all4_llm_sold"].sum()),
        "hours_seat5_traded": int(ph["seat5_traded"].sum()),
        "distinct_buyers_traded": len({t["buyer_id"] for t in trades}),
        "seat5_ask_h1": ph["seat5_ask"].iloc[0], "seat5_ask_h3": ph.loc[ph["hour"] == 3, "seat5_ask"].squeeze(),
        "seat5_ask_last_third": phl["seat5_ask"].mean(),
        "llm_mean_ask_last_third": phl["llm_mean_ask"].mean(),
        "llm_min_ask_last_third": phl["llm_min_ask"].mean(),
        "seat5_minus_llm_mean_ask_last_third": (phl["seat5_ask"] - phl["llm_mean_ask"]).mean(),
        # hours from the offer hour on in which seat 5's ask is at or above every LLM seller's ask
        "hours_seat5_highest_ask_from_offer": int((after["seat5_ask"] >= after["llm_max_ask"] - 1e-9).sum()),
        "hours_from_offer": len(after),
        # best bid among buyers who did not trade this hour, vs seat 5's ask (the fifth unit's price)
        "best_unmatched_bid_last_third": phl["best_unmatched_bid"].mean(),
        "hours_unmatched_bid_ge_seat5_ask": int((ph["best_unmatched_bid"] >= ph["seat5_ask"]).sum()),
        "llm_mean_avg_trade_price_last_third": avg(
            [t["price"] for r in lt for t in r.get("trades", []) if t["seller_id"] in llm]),
    })

    # per-seller consecutive-hour ask changes
    def changes(group):
        out = []
        for s in group:
            for r0, r1 in zip(rounds, rounds[1:]):
                a0, a1 = ask(r0, s), ask(r1, s)
                if a0 is not None and a1 is not None:
                    out.append(a1 - a0)
        return out
    d_llm, d_s5 = changes(llm), changes([s5])
    row.update({
        "llm_ask_transitions": len(d_llm),
        "llm_ask_missing_transitions": len(llm) * (n - 1) - len(d_llm),
        "llm_ask_raises_any": sum(d > 1e-9 for d in d_llm),
        "llm_ask_raises_gt1": sum(d > 1 + 1e-9 for d in d_llm),
        "llm_ask_unchanged": sum(abs(d) <= 1e-9 for d in d_llm),
        "llm_ask_cuts": sum(d < -1e-9 for d in d_llm),
        "llm_ask_max_raise": max(d_llm) if d_llm else None,
        "seat5_ask_raises_any": sum(d > 1e-9 for d in d_s5),
    })

    # pre-trend: hourly mean LLM ask, hours 1-3 (offer not yet visible) vs 3-6
    m = dict(zip(ph["hour"], ph["llm_mean_ask"]))
    row.update({
        "llm_ask_h1": m.get(1), "llm_ask_h3": m.get(3), "llm_ask_h6": m.get(6),
        "slope_pre_ols": ols_slope([1, 2, 3], [m.get(h) for h in (1, 2, 3)]),
        "slope_post_ols": ols_slope([3, 4, 5, 6], [m.get(h) for h in (3, 4, 5, 6)]),
        "slope_pre_endpoints": (m[3] - m[1]) / 2 if m.get(1) is not None and m.get(3) is not None else None,
        "slope_post_endpoints": (m[6] - m[3]) / 3 if m.get(3) is not None and m.get(6) is not None else None,
    })
    return row


def exact_perm(a: list[float], b: list[float]) -> float:
    """Two-sided exact permutation p for a difference in means (same test as scripts/permutation_tests.py)."""
    pooled, obs, hits, total = a + b, abs(mean(a) - mean(b)), 0, 0
    for idx in itertools.combinations(range(len(pooled)), len(a)):
        xa = [pooled[i] for i in idx]
        xb = [pooled[i] for i in range(len(pooled)) if i not in idx]
        total += 1
        hits += abs(mean(xa) - mean(xb)) >= obs - 1e-12
    return hits / total


def summarize(df: pd.DataFrame) -> None:
    def pooled(sub: pd.DataFrame, label: str) -> None:
        t, t5 = sub["trades_total"].sum(), sub["trades_seat5"].sum()
        tr, r1 = sub["llm_ask_transitions"].sum(), sub["llm_ask_raises_gt1"].sum()
        print(f"\n== {label}: {len(sub)} runs ==")
        print(f"trades {t}; seat 5 {t5} ({t5 / t:.1%}); LLM {t - t5}; "
              f"runs where seat 5 never traded: {(sub['trades_seat5'] == 0).sum()}")
        print(f"trades/hour {sub['trades_per_hour'].mean():.2f} (last third {sub['trades_per_hour_last_third'].mean():.2f}); "
              f"buyers trading/hour last third {sub['buyers_trading_per_hour_last_third'].mean():.2f} of 5; "
              f"hours with all 5 buyers served {sub['hours_5_buyers_traded'].sum()} of {sub['n_hours'].sum()} "
              f"(last third {sub['hours_5_buyers_traded_last_third'].sum()} of {len(sub) * 5})")
        print("trades by position: " + ", ".join(
            f"{i}: {sub[f'trades_pos{i}'].sum()}" for i in range(1, 6) if f"trades_pos{i}" in sub))
        print(f"LLM trades/hour last third {sub['llm_trades_per_hour_last_third'].mean():.2f}; "
              f"last-third LLM trade price {sub['llm_mean_avg_trade_price_last_third'].mean():.2f}")
        print(f"hours all 4 LLM sellers sold: {sub['hours_all4_llm_sold'].sum()} of {sub['n_hours'].sum()} "
              f"(last third {sub['hours_all4_llm_sold_last_third'].sum()} of {len(sub) * 5})")
        print(f"LLM ask transitions {tr}: raises >$1 {r1}, raises >$0 {sub['llm_ask_raises_any'].sum()}, "
              f"unchanged {sub['llm_ask_unchanged'].sum()}, cuts {sub['llm_ask_cuts'].sum()}, "
              f"missing {sub['llm_ask_missing_transitions'].sum()}")
        print(f"last third: seat-5 ask {sub['seat5_ask_last_third'].mean():.2f}, LLM mean ask "
              f"{sub['llm_mean_ask_last_third'].mean():.2f}, LLM min ask {sub['llm_min_ask_last_third'].mean():.2f}, "
              f"best unmatched bid {sub['best_unmatched_bid_last_third'].mean():.2f}; seat 5 highest ask in "
              f"{sub['hours_seat5_highest_ask_from_offer'].sum()} of {sub['hours_from_offer'].sum()} hours from the offer")

    pooled(df, "all D-G runs")
    pooled(df[df["arm"] != "F-sham"], "the 45 runs of the nine main arms (F-sham excluded)")

    cols = ["trades_total", "trades_seat5", "trades_per_hour_last_third", "buyers_trading_per_hour_last_third",
            "seat5_ask_last_third", "llm_mean_ask_last_third", "llm_ask_raises_gt1",
            "slope_pre_ols", "slope_post_ols", "slope_pre_endpoints", "slope_post_endpoints"]
    agg = df.groupby("arm")[cols].mean()
    agg[["trades_total", "trades_seat5", "llm_ask_raises_gt1"]] = df.groupby("arm")[
        ["trades_total", "trades_seat5", "llm_ask_raises_gt1"]].sum()
    agg = agg.loc[[a for a in ARM_ORDER if a in agg.index]]
    print("\n== by arm (trade and raise columns summed over runs; others are run means) ==")
    print(agg.to_string(float_format=lambda v: f"{v:.2f}"))

    print("\n== pre-trend: D vs Base (exact permutation over runs) ==")
    for kind in ("ols", "endpoints"):
        g = {a: df[df["arm"] == a].sort_values("seed") for a in ("Base", "D")}
        pre = {a: g[a][f"slope_pre_{kind}"].tolist() for a in g}
        post = {a: g[a][f"slope_post_{kind}"].tolist() for a in g}
        chg = {a: [q - p for p, q in zip(pre[a], post[a])] for a in g}
        did = mean(chg["D"]) - mean(chg["Base"])
        print(f"{kind}: pre D {mean(pre['D']):+.2f}/h vs Base {mean(pre['Base']):+.2f}/h (p {exact_perm(pre['D'], pre['Base']):.2f}); "
              f"post D {mean(post['D']):+.2f}/h vs Base {mean(post['Base']):+.2f}/h (p {exact_perm(post['D'], post['Base']):.2f}); "
              f"DiD (post-pre, D-Base) {did:+.2f}/h, p {exact_perm(chg['D'], chg['Base']):.2f}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results-root", type=Path, required=True, help="folder of D-G run directories (results/dg)")
    p.add_argument("--out", type=Path, default=REPO / "report" / "data" / "dg" / "market_structure.csv")
    args = p.parse_args(argv)

    rows = []
    for meta in sorted(args.results_root.glob("*/experiment_metadata.json")):
        run_dir = meta.parent
        if not (run_dir / "unified.log").is_file():
            print(f"skip {run_dir.name}: no unified.log", file=sys.stderr)
            continue
        if not json.loads(meta.read_text(encoding="utf-8")).get("arm"):
            print(f"skip {run_dir.name}: no `arm` (not a D-G run)", file=sys.stderr)
            continue
        rows.append(analyze(run_dir))
    if not rows:
        sys.exit(f"no D-G runs under {args.results_root}")
    df = pd.DataFrame(rows)
    df["_arm"] = df["arm"].map(lambda a: ARM_ORDER.index(a) if a in ARM_ORDER else len(ARM_ORDER))
    df = df.sort_values(["_arm", "seed"]).drop(columns="_arm").reset_index(drop=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"{len(df)} run(s) -> {args.out}")
    summarize(df)


if __name__ == "__main__":
    main()
