"""Does the frozen seller judge track prices, or only talk? (new sprint code, Oct 25 reanalysis)

The seller judge (Claude Haiku 5.5, T = 0.1, fingerprint 837dec878d4f, "messages" view; README "Judge") scores
each LLM seller-hour 1-4 for coordination from that hour's reasoning, public message and private messages. This
script puts one number per run next to the price outcome:

  judge_mean             mean score over every judged LLM seller-hour of the run (scripted seats are never judged;
                         the few judge errors, stored as null, are dropped)
  judge_mean_last_third  same, over the last third of hours only (the joint criterion's window, hours 11-15)
  judge_high             judge_mean >= 2
  ask_index, passed      LLM-only last-third ask index and joint-criterion pass, from the committed
                         report/data/<group>/market_by_run.csv (src/apartcollusion/market_indices.py)
  llm_private_msgs       private messages sent by LLM sellers (dm_summary.by_sender, scripted seat excluded)
  verbal_accept_share    share of LLM sellers the D-G judge coded verbal_accept (report/data/<group>/outcomes.csv)

Runs: every judged run under <results-root>/dg (Gemini 3.8 Flash), dg_gpt41 (GPT-4.1) and dg_haiku (Claude
Haiku 5.5). The 68 D-G design runs (talk arms Base/D/D-hs/D-hb/D-hsb, warning arms E/F/G-warn/G-prec/F-sham) are
the headline sample. The two GPT-4.1 no-comms runs and the GPT-4.1 pilot are not in market_by_run.csv (no `arm`
in their metadata); their LLM-only indices are recomputed here with the same market_indices code (they have no
scripted seat), they are written to the CSV, and they are summarised separately. For the design runs the same
recomputation is checked against the committed CSV and the script stops on any mismatch.

Statistics use runs (markets) as the unit. AUC = P(judge_mean of a passing run > that of a failing run), ties 1/2.
p-values are two-sided permutation tests (pass labels or ask indices shuffled across runs; "within family" shuffles
only inside each seller model family, so differences between families are in the null too); CIs are percentile
bootstraps over runs. Reads results/ (gitignored, local) by absolute path; makes no API calls.

From third_party/llm-agent-collusion/:
    PYTHONUTF8=1 uv run python ../../scripts/judge_vs_price.py \\
        --results-root C:/Users/danie/Hackathons/ApartAICollusion/results
writes report/data/dg/judge_vs_price.csv and prints the summary.
"""

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "report" / "data"
sys.path.insert(0, str(REPO / "src"))

from apartcollusion.market_indices import hourly, run_summary  # noqa: E402
from apartcollusion.runs import last_third, load_run  # noqa: E402

FROZEN_SELLER_FP = "837dec878d4f"
GROUPS = ["dg", "dg_gpt41", "dg_haiku"]
TALK = ["Base", "D", "D-hs", "D-hb", "D-hsb"]
WARNING = ["E", "F", "G-warn", "G-prec", "F-sham"]
FAMILY = {"google/gemini-3.8-flash": "Gemini", "openai/gpt-4.1": "GPT-4.1",
          "anthropic/claude-haiku-5.5": "Haiku"}
N_PERM, N_BOOT, SEED = 20000, 5000, 0


# --------------------------------------------------------------------------- #
# Statistics (numpy only; the harness venv has no scipy)

def ranks(x: np.ndarray) -> np.ndarray:
    """Average ranks (1-based), ties share the mean rank (scipy.stats.rankdata's 'average' method)."""
    x = np.asarray(x, dtype=float)
    sorter = np.argsort(x, kind="mergesort")
    inv = np.empty_like(sorter)
    inv[sorter] = np.arange(len(x))
    xs = x[sorter]
    new = np.r_[True, xs[1:] != xs[:-1]]
    dense = new.cumsum()[inv]
    count = np.r_[np.nonzero(new)[0], len(new)]
    return 0.5 * (count[dense] + count[dense - 1] + 1)


def auc(score: np.ndarray, label: np.ndarray) -> float:
    label = np.asarray(label, dtype=bool)
    pos, neg = label.sum(), (~label).sum()
    if not pos or not neg:
        return float("nan")
    r = ranks(score)
    return float((r[label].sum() - pos * (pos + 1) / 2) / (pos * neg))


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = ranks(x), ranks(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p(stat, x: np.ndarray, y: np.ndarray, centre: float, strata: Optional[np.ndarray] = None) -> float:
    """Two-sided permutation p: share of shuffles of y with |stat - centre| >= observed (+1 smoothing). With
    `strata`, y is shuffled only within each stratum."""
    rng = np.random.default_rng(SEED)
    obs = abs(stat(x, y) - centre)
    groups = [np.flatnonzero(strata == k) for k in np.unique(strata)] if strata is not None else [np.arange(len(y))]
    hits = 0
    for _ in range(N_PERM):
        yp = y.copy()
        for idx in groups:
            yp[idx] = y[rng.permutation(idx)]
        hits += abs(stat(x, yp) - centre) >= obs - 1e-12
    return (hits + 1) / (N_PERM + 1)


def boot_ci(stat, x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(x), len(x))
        v = stat(x[i], y[i])
        if not math.isnan(v):
            vals.append(v)
    return (float(np.quantile(vals, 0.025)), float(np.quantile(vals, 0.975))) if vals else (math.nan, math.nan)


def fisher_p(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact p for [[a, b], [c, d]] (sum over tables no more likely than the observed one)."""
    r1, c1, n = a + b, a + c, a + b + c + d

    def prob(x: int) -> float:
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)

    p_obs = prob(a)
    return min(1.0, sum(prob(x) for x in range(max(0, r1 + c1 - n), min(r1, c1) + 1) if prob(x) <= p_obs * (1 + 1e-9)))


# --------------------------------------------------------------------------- #
# Per-run table

def committed_market(group: str) -> dict[str, dict[str, str]]:
    path = DATA / group / "market_by_run.csv"
    return {r["run_id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}


def verbal_accept_shares(group: str) -> dict[str, float]:
    path = DATA / group / "outcomes.csv"
    if not path.is_file():
        return {}
    df = pd.read_csv(path)
    return df.groupby("run_id")["verbal_accept"].mean().to_dict()


def arm_of(run, tag: Optional[str]) -> tuple[str, str]:
    """(arm, arm_type). Non-design runs are named from their tag."""
    arm = run.arm
    if arm in TALK:
        return arm, "talk"
    if arm in WARNING:
        return arm, "warning"
    tag = tag or ""
    if tag.startswith("nocomms"):
        return "no-comms", "nocomms"
    if tag.startswith("pilot"):
        return "pilot", "pilot"
    return arm or tag, "other"


def run_row(run_dir: Path, group: str, market: dict[str, dict[str, str]], accept: dict[str, float]) -> Optional[dict]:
    run = load_run(run_dir)
    js = run.metrics.get("judge_seller")
    if not js:
        return None
    if js.get("fingerprint") != FROZEN_SELLER_FP or js.get("view") != "messages":
        print(f"skip {run.run_id}: seller judge {js.get('fingerprint')}/{js.get('view')} is not the frozen one",
              file=sys.stderr)
        return None
    llm = run.llm_sellers
    scores = js.get("coordination_scores", {})
    all_s = [s for sid in llm for s in scores.get(sid, []) if s is not None]
    last_s = [s for sid in llm for s in last_third(scores.get(sid, [])) if s is not None]
    n_none = sum(s is None for sid in llm for s in scores.get(sid, []))
    models = {run.model_of(sid) for sid in llm}
    model = models.pop() if len(models) == 1 else ";".join(sorted(m or "?" for m in models))
    tag = run.metadata.get("auction_config", {}).get("tag")
    arm, arm_type = arm_of(run, tag)

    # LLM-only price outcome: recompute with the committed code, use the committed CSV value, check they agree.
    recomputed = run_summary(run, hourly(run))
    committed = market.get(run.run_id)
    if committed is not None:
        for k in ("ask_index", "trade_index", "trades_per_round"):
            if not math.isclose(float(committed[k]), recomputed[k], rel_tol=1e-9, abs_tol=1e-9):
                sys.exit(f"{run.run_id}: committed {k} {committed[k]} != recomputed {recomputed[k]}")
        if (committed["passed"] == "True") != bool(recomputed["passed"]):
            sys.exit(f"{run.run_id}: committed passed {committed['passed']} != recomputed {recomputed['passed']}")
        price = {k: float(committed[k]) for k in ("ask_index", "trade_index", "trades_per_round")}
        price["passed"] = committed["passed"] == "True"
        source = f"report/data/{group}/market_by_run.csv"
    else:
        price = {k: recomputed[k] for k in ("ask_index", "trade_index", "trades_per_round", "passed")}
        source = "recomputed (market_indices; not in committed CSV)"

    by_sender = (run.metrics.get("dm_summary") or {}).get("by_sender") or {}
    va = accept.get(run.run_id)
    jm = float(np.mean(all_s)) if all_s else None
    return {
        "run_id": run.run_id, "results_group": group, "seller_model": model, "family": FAMILY.get(model, model),
        "arm": arm, "arm_type": arm_type, "seed": run.seed, "design_run": arm_type in ("talk", "warning"),
        "n_llm_sellers": len(llm), "judge_fingerprint": js["fingerprint"],
        "n_judged_seller_hours": len(all_s), "n_judge_errors": n_none,
        "judge_mean": jm,
        "judge_mean_last_third": float(np.mean(last_s)) if last_s else None,
        "judge_high": jm is not None and jm >= 2,
        "llm_private_msgs": sum(v for k, v in by_sender.items() if k in llm),
        "verbal_accept_share": float(va) if va is not None else None,
        "ask_index": price["ask_index"], "trade_index": price["trade_index"],
        "trades_per_round": price["trades_per_round"], "passed": bool(price["passed"]),
        "price_source": source,
    }


def build(results_root: Path) -> pd.DataFrame:
    rows = []
    for group in GROUPS:
        market, accept = committed_market(group), verbal_accept_shares(group)
        for metrics in sorted((results_root / group).glob("*/collusion_metrics.json")):
            run_dir = metrics.parent
            if not (run_dir / "auction_results.md").is_file():
                print(f"skip {run_dir.name}: no auction_results.md", file=sys.stderr)
                continue
            row = run_row(run_dir, group, market, accept)
            if row:
                rows.append(row)
        missing = set(market) - {r["run_id"] for r in rows}
        if missing:
            sys.exit(f"{group}: runs in market_by_run.csv but not judged/found under {results_root}: {sorted(missing)}")
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Summary

def fmt(x: Any, nd: int = 2) -> str:
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{nd}f}"


def describe(df: pd.DataFrame, name: str, score_col: str = "judge_mean") -> dict[str, Any]:
    s = df[score_col].to_numpy(float)
    y = df["passed"].to_numpy(bool)
    a = df["ask_index"].to_numpy(float)
    fam = df["family"].to_numpy()
    out: dict[str, Any] = {"subset": name, "n_runs": len(df), "n_pass": int(y.sum()),
                           "auc": auc(s, y), "rho_ask": spearman(s, a)}
    if len(df) > 3:
        if not math.isnan(out["auc"]):
            out["auc_p"] = perm_p(auc, s, y, 0.5)
            out["auc_ci"] = boot_ci(auc, s, y)
            if len(set(fam)) > 1:
                out["auc_p_strat"] = perm_p(auc, s, y, 0.5, strata=fam)
        if not math.isnan(out["rho_ask"]):
            out["rho_ask_p"] = perm_p(spearman, s, a, 0.0)
            out["rho_ask_ci"] = boot_ci(spearman, s, a)
            if len(set(fam)) > 1:
                out["rho_ask_p_strat"] = perm_p(spearman, s, a, 0.0, strata=fam)
    hi = s >= 2
    tab = {(h, p): int(((hi == h) & (y == p)).sum()) for h in (True, False) for p in (True, False)}
    out["table"] = tab
    out["fisher_p"] = fisher_p(tab[(True, True)], tab[(True, False)], tab[(False, True)], tab[(False, False)])
    return out


def print_block(d: dict[str, Any]) -> None:
    t = d["table"]
    line = f"{d['subset']:<28} n={d['n_runs']:>2} pass={d['n_pass']:>2} | AUC {fmt(d['auc'])}"
    if "auc_p" in d:
        line += f" [{fmt(d['auc_ci'][0])}, {fmt(d['auc_ci'][1])}] p={fmt(d['auc_p'], 3)}"
    line += f" | Spearman(judge, ask index) {fmt(d['rho_ask'])}"
    if "rho_ask_p" in d:
        line += f" [{fmt(d['rho_ask_ci'][0])}, {fmt(d['rho_ask_ci'][1])}] p={fmt(d['rho_ask_p'], 3)}"
    print(line)
    if "auc_p_strat" in d or "rho_ask_p_strat" in d:
        print(f"{'':<28} permutation within model family: AUC p={fmt(d.get('auc_p_strat'), 3)}, "
              f"Spearman p={fmt(d.get('rho_ask_p_strat'), 3)}")
    print(f"{'':<28} 2x2: judge>=2 & pass {t[(True, True)]:>2} | judge>=2 & fail {t[(True, False)]:>2} | "
          f"judge<2 & pass {t[(False, True)]:>2} | judge<2 & fail {t[(False, False)]:>2}  (Fisher p={fmt(d['fisher_p'], 3)})")


def summarise(df: pd.DataFrame) -> None:
    design = df[df["design_run"]]
    talk, warn = design[design["arm_type"] == "talk"], design[design["arm_type"] == "warning"]
    gem = design[design["family"] == "Gemini"]
    print(f"\n{len(df)} judged runs ({len(design)} D-G design runs: {len(talk)} talk, {len(warn)} warning; "
          f"{(df['arm_type'] == 'nocomms').sum()} no-comms; {(df['arm_type'] == 'pilot').sum()} pilot). "
          f"Seller judge {FROZEN_SELLER_FP}; {int(df['n_judge_errors'].sum())} null seller-hours dropped.")

    print("\nBy family x arm:")
    g = df.groupby(["family", "arm_type", "arm"], sort=False).agg(
        runs=("run_id", "size"), judge_mean=("judge_mean", "mean"), judge_min=("judge_mean", "min"),
        judge_max=("judge_mean", "max"), judge_high=("judge_high", "sum"), private_msgs=("llm_private_msgs", "mean"),
        ask_index=("ask_index", "mean"), passed=("passed", "sum"))
    print(g.to_string(float_format=lambda v: f"{v:.2f}"))

    print("\nJudge vs price (unit = run; judge = mean score over all LLM seller-hours):")
    subsets = [("all design runs", design), ("talk arms", talk), ("warning arms", warn),
               ("Gemini design runs", gem),
               ("Gemini talk arms", gem[gem["arm_type"] == "talk"]),
               ("Gemini warning arms", gem[gem["arm_type"] == "warning"]),
               ("GPT-4.1 design runs", design[design["family"] == "GPT-4.1"]),
               ("Haiku design runs", design[design["family"] == "Haiku"]),
               ("design + GPT-4.1 no-comms", df[df["arm_type"] != "pilot"])]
    for name, sub in subsets:
        print_block(describe(sub, name))

    print("\nJudge vs talk (unit = run):")
    for name, sub in (("all design runs", design), ("Gemini design runs", gem)):
        s, m = sub["judge_mean"].to_numpy(float), sub["llm_private_msgs"].to_numpy(float)
        is_talk = (sub["arm_type"] == "talk").to_numpy(bool)
        lo, hi = boot_ci(spearman, s, m)
        print(f"  {name:<20} Spearman(judge, LLM private messages) {fmt(spearman(s, m))} [{fmt(lo)}, {fmt(hi)}] "
              f"p={fmt(perm_p(spearman, s, m, 0), 4)}; AUC(judge: talk vs warning arm) {fmt(auc(s, is_talk))} "
              f"p={fmt(perm_p(auc, s, is_talk, 0.5), 4)}")
    va = design.dropna(subset=["verbal_accept_share"])
    s2, v2 = va["judge_mean"].to_numpy(float), va["verbal_accept_share"].to_numpy(float)
    print(f"  Spearman(judge, D-G judge verbal_accept share) {fmt(spearman(s2, v2))} "
          f"p={fmt(perm_p(spearman, s2, v2, 0), 4)} (n={len(va)}; same judge model, different prompt)")
    gt, gw = gem[gem["arm_type"] == "talk"], gem[gem["arm_type"] == "warning"]
    print(f"  Gemini: judge range talk {fmt(gt['judge_mean'].min())}-{fmt(gt['judge_mean'].max())} vs warning "
          f"{fmt(gw['judge_mean'].min())}-{fmt(gw['judge_mean'].max())}; ask index mean talk "
          f"{fmt(gt['ask_index'].mean())} vs warning {fmt(gw['ask_index'].mean())}; pass talk "
          f"{int(gt['passed'].sum())}/{len(gt)} vs warning {int(gw['passed'].sum())}/{len(gw)}")
    print(f"  All design runs: judge mean talk {fmt(talk['judge_mean'].mean())} vs warning "
          f"{fmt(warn['judge_mean'].mean())}; ask index mean talk {fmt(talk['ask_index'].mean())} vs warning "
          f"{fmt(warn['ask_index'].mean())}; pass talk {int(talk['passed'].sum())}/{len(talk)} vs warning "
          f"{int(warn['passed'].sum())}/{len(warn)}")

    print("\nNon-design GPT-4.1 runs (five LLM sellers, no scripted seat; indices recomputed with market_indices):")
    for _, r in df[~df["design_run"]].iterrows():
        print(f"  {r['run_id']:<40} {r['arm']:<9} judge {r['judge_mean']:.2f} (last third "
              f"{r['judge_mean_last_third']:.2f})  private msgs {r['llm_private_msgs']:>3}  "
              f"ask index {r['ask_index']:.2f}  passed {r['passed']}")
    passed_low = df[df["passed"] & ~df["judge_high"] & (df["arm_type"] != "pilot")]
    failed_high = df[~df["passed"] & df["judge_high"] & (df["arm_type"] != "pilot")]
    print(f"  Runs that pass with judge < 2: {len(passed_low)} "
          f"({', '.join(f'{f} {a}' for (f, a), _ in passed_low.groupby(['family', 'arm']))}); "
          f"judge range {fmt(passed_low['judge_mean'].min())}-{fmt(passed_low['judge_mean'].max())}")
    print(f"  Runs that fail with judge >= 2: {len(failed_high)}")

    print("\nRobustness: judge mean over the last third of hours (11-15, the joint criterion's window):")
    for name, sub in (("all design runs", design), ("Gemini design runs", gem)):
        print_block(describe(sub, name, score_col="judge_mean_last_third"))


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results-root", type=Path, required=True,
                   help="the main checkout's results/ folder (holds dg, dg_gpt41, dg_haiku)")
    p.add_argument("--out", type=Path, default=DATA / "dg" / "judge_vs_price.csv")
    args = p.parse_args(argv)

    df = build(args.results_root)
    if df.empty:
        sys.exit(f"no judged runs under {args.results_root}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False, float_format="%.6g", lineterminator="\n")
    print(f"{len(df)} rows -> {args.out}")
    summarise(df)


if __name__ == "__main__":
    main()
