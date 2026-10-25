"""Exact permutation tests over markets for the D-G report (Table 3).

Each test compares two arms using one number per market (run): the statistic is the
difference in arm means, and the p-value is two-sided over every relabelling of the
pooled markets (5 vs 5 markets gives C(10,5) = 252 relabellings, so the smallest
possible p is 2/252 ~ 0.008). Markets, not sellers, are the unit, because sellers in
one market talk to each other.

Reads only committed files:
  report/data/dg/table3_extra.csv   per-run message, reply and report counts (from the run logs)
  report/data/dg/market_by_run.csv  per-run ask index over the LLM sellers
  report/data/dg/outcomes.csv       per-seller ask change (hours 4-6 minus hour 3) and judge suspects_test

Usage: python scripts/permutation_tests.py [--out report/data/dg/permutation_tests.csv]
"""
import argparse
import csv
import itertools
from collections import defaultdict
from pathlib import Path
from statistics import mean

DATA = Path(__file__).resolve().parents[1] / "report" / "data" / "dg"

CONTRASTS = [
    # (measure, arm A, arm B)
    ("reported_seat5", "Base", "D"),
    ("reported_seat5", "D", "D-hs"),
    ("reported_seat5", "D", "D-hb"),
    ("reported_seat5", "D", "D-hsb"),
    ("private_msgs_llm_total", "Base", "G-warn"),
    ("private_msgs_llm_total", "D", "E"),
    ("public_msgs", "E", "F"),
    ("public_msgs", "F", "F-sham"),
    ("ask_index", "Base", "D"),
    ("ask_index", "Base", "G-warn"),
    ("ask_index", "Base", "G-prec"),
    ("ask_index", "Base", "E"),
    ("ask_change_post_offer", "Base", "D"),
    ("suspects_test", "F", "F-sham"),
    ("suspects_test", "G-warn", "G-prec"),
]


def load():
    per_run = defaultdict(dict)  # (arm, seed) -> measure -> value
    for r in csv.DictReader(open(DATA / "table3_extra.csv", encoding="utf-8")):
        k = (r["arm"], int(r["seed"]))
        for m in ("reported_seat5", "private_msgs_llm_total", "public_msgs", "replied_to_seat5_from_h4"):
            per_run[k][m] = float(r[m])
    for r in csv.DictReader(open(DATA / "market_by_run.csv", encoding="utf-8")):
        per_run[(r["arm"], int(r["seed"]))]["ask_index"] = float(r["ask_index"])
    changes = defaultdict(list)
    for r in csv.DictReader(open(DATA / "outcomes.csv", encoding="utf-8")):
        k = (r["arm"], int(r["seed"]))
        per_run[k]["suspects_test"] = per_run[k].get("suspects_test", 0.0) + (r["suspects_test"] == "True")
        if r["ask_change_post_offer"]:
            changes[(r["arm"], int(r["seed"]))].append(float(r["ask_change_post_offer"]))
    for k, v in changes.items():
        per_run[k]["ask_change_post_offer"] = mean(v)
    return per_run


def exact_perm(a, b):
    pooled = a + b
    obs = abs(mean(a) - mean(b))
    n, hits, total = len(a), 0, 0
    for idx in itertools.combinations(range(len(pooled)), n):
        xa = [pooled[i] for i in idx]
        xb = [pooled[i] for i in range(len(pooled)) if i not in idx]
        total += 1
        if abs(mean(xa) - mean(xb)) >= obs - 1e-12:
            hits += 1
    return hits / total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DATA / "permutation_tests.csv"))
    args = ap.parse_args()
    per_run = load()
    rows = []
    for measure, arm_a, arm_b in CONTRASTS:
        a = [v[measure] for (arm, _), v in sorted(per_run.items()) if arm == arm_a and measure in v]
        b = [v[measure] for (arm, _), v in sorted(per_run.items()) if arm == arm_b and measure in v]
        p = exact_perm(a, b)
        rows.append(dict(measure=measure, arm_a=arm_a, arm_b=arm_b, n_a=len(a), n_b=len(b),
                         mean_a=round(mean(a), 3), mean_b=round(mean(b), 3), p_two_sided=round(p, 3)))
        print(f"{measure:24s} {arm_a:6s} vs {arm_b:7s}  {mean(a):8.3f} vs {mean(b):8.3f}  p = {p:.3f}")
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
