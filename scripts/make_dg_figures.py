"""D-G figures for the report (new sprint code). Reads the CSVs the analysis CLIs write (README "Analysis"):

    <analysis-dir>/market_by_hour.csv   python -m apartcollusion.market_indices  (LLM sellers only)
    <analysis-dir>/outcomes_by_arm.csv  python -m apartcollusion.outcomes

and writes SVG + PNG to --out-dir (default report/figures/):

    fig_dg_ask_index   ask index vs hour, one panel per arm: mean over seeds with the min-max band, Base's mean
                       as a grey reference in every panel, competitive (0) and cartel (1) lines, offer hour marked
    fig_dg_outcomes    rate of each seller-episode outcome by arm, with 95% cluster-bootstrap CIs (runs resampled)

Small multiples rather than eleven overlaid lines: past ~8 series no colour set stays distinguishable, and each
arm is read against Base anyway. The exact numbers are in the CSVs.

    PYTHONPATH=src uv run --project third_party/llm-agent-collusion python scripts/make_dg_figures.py \\
        --analysis-dir results/dg --out-dir report/figures
"""

import argparse
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from apartcollusion.runs import arm_sort_key  # noqa: E402

# Reference palette from the dataviz skill (light mode): one series hue, text inks, a recessive grid.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"   # the arm in each panel
REFERENCE = "#8c8b86"  # Base mean, benchmarks
OUTCOMES = [  # (column in outcomes_by_arm.csv, label)
    ("verbal_accept", "Agreement to a peer's\nprice proposal"),
    ("behavioral_accept", "Ask within $1 of $96, h4-5\n(vs Base; uninformative)"),
    ("suspects_collusion", "Suspects collusion"),
    ("suspects_test", "Suspects a test"),
    ("reported", "Reported anyone"),
    ("false_report", "Report naming someone\nother than seat 5"),
    ("mentions_human_appeal", "Mentions human appeal"),
]


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _save(fig, out_dir: Path, name: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("svg", "png"):
        p = out_dir / f"{name}.{ext}"
        fig.savefig(p, format=ext, dpi=200, bbox_inches="tight", facecolor=SURFACE, pad_inches=0.15)
        paths.append(p)
    plt.close(fig)
    return paths


def ask_index_figure(by_hour: pd.DataFrame, out_dir: Path, base_arm: str = "Base") -> list[Path]:
    arms = sorted(by_hour["arm"].unique(), key=arm_sort_key)
    per_seed = by_hour.groupby(["arm", "hour"])["ask_index"]
    stats = per_seed.agg(["mean", "min", "max"]).reset_index()
    offer_hour = by_hour["offer_hour"].dropna().mode()
    offer_hour = float(offer_hour.iloc[0]) if len(offer_hour) else None
    base = stats[stats["arm"] == base_arm]
    lo = min(-0.2, math.floor(stats["min"].min() * 5) / 5)
    hi = max(1.2, math.ceil(stats["max"].max() * 5) / 5)

    cols = min(4, len(arms))
    rows = math.ceil(len(arms) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(2.6 * cols + 0.6, 2.2 * rows + 0.8), sharex=True, sharey=True,
                             squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for ax in axes.flat[len(arms):]:
        ax.set_visible(False)
    for ax, arm in zip(axes.flat, arms):
        _style(ax)
        s = stats[stats["arm"] == arm]
        n = by_hour[by_hour["arm"] == arm]["run_id"].nunique()
        ax.axhline(0, color=REFERENCE, linewidth=0.9, linestyle=(0, (4, 3)))
        ax.axhline(1, color=REFERENCE, linewidth=0.9, linestyle=(0, (4, 3)))
        if offer_hour is not None:
            ax.axvline(offer_hour, color=MUTED, linewidth=0.9)
        if arm != base_arm and len(base):
            ax.plot(base["hour"], base["mean"], color=REFERENCE, linewidth=1.5)
        ax.fill_between(s["hour"], s["min"], s["max"], color=SERIES, alpha=0.18, linewidth=0)
        ax.plot(s["hour"], s["mean"], color=SERIES, linewidth=2)
        ax.set_title(f"{arm}  (n={n})", fontsize=9.5, color=INK, loc="left")
        ax.set_ylim(lo, hi)
    for ax in axes[:, 0]:
        ax.set_ylabel("Ask index (LLM sellers)", fontsize=8.5, color=MUTED)
    for ax in axes[-1, :]:
        ax.set_xlabel("Hour", fontsize=8.5, color=MUTED)
    for ax in axes.flat:
        ax.set_xticks([1, 3, 5, 10, 15])
    first = axes.flat[0]
    first.text(first.get_xlim()[0], 1.02, "cartel", fontsize=7, color=MUTED, va="bottom")
    first.text(first.get_xlim()[0], 0.02, "competitive", fontsize=7, color=MUTED, va="bottom")
    if offer_hour is not None:
        first.text(offer_hour + 0.15, lo + 0.03, "hour-3 message", fontsize=7, color=MUTED, va="bottom")
    fig.legend(handles=[
        plt.Line2D([], [], color=SERIES, linewidth=2, label="arm: mean over seeds (band = min-max)"),
        plt.Line2D([], [], color=REFERENCE, linewidth=1.5, label=f"{base_arm}: mean over seeds"),
    ], loc="lower center", ncol=2, frameon=False, fontsize=8, labelcolor=INK, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Ask index by hour and arm (0 = competitive, 1 = cartel price)", fontsize=11, color=INK,
                 x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    return _save(fig, out_dir, "fig_dg_ask_index")


def outcomes_figure(by_arm: pd.DataFrame, out_dir: Path) -> list[Path]:
    by_arm = by_arm.sort_values("arm", key=lambda s: s.map(arm_sort_key)).reset_index(drop=True)
    arms = list(by_arm["arm"])
    panels = [(c, label) for c, label in OUTCOMES if f"{c}_rate" in by_arm]
    cols = min(4, len(panels))
    rows = math.ceil(len(panels) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(2.5 * cols + 0.8, 0.32 * len(arms) * rows + 1.2 * rows),
                             sharey=True, squeeze=False)
    fig.patch.set_facecolor(SURFACE)
    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    ys = list(range(len(arms)))[::-1]  # first arm on top
    for ax, (col, label) in zip(axes.flat, panels):
        _style(ax)
        ax.grid(True, axis="x", color=GRID, linewidth=0.6)
        ax.grid(False, axis="y")
        for y, (_, r) in zip(ys, by_arm.iterrows()):
            rate = r[f"{col}_rate"]
            if pd.isna(rate):
                ax.text(0.02, y, "n/a", fontsize=7, color=MUTED, va="center")
                continue
            ax.plot([r[f"{col}_ci_lo"], r[f"{col}_ci_hi"]], [y, y], color=SERIES, linewidth=2,
                    solid_capstyle="round", alpha=0.45)
            ax.plot([rate], [y], marker="o", markersize=6, color=SERIES, markeredgecolor=SURFACE,
                    markeredgewidth=1.5)
        ax.set_xlim(-0.03, 1.03)
        ax.set_xticks([0, 0.5, 1])
        ax.set_xticklabels(["0", "50%", "100%"])
        ax.set_title(label, fontsize=9, color=INK, loc="left")
        ax.set_yticks(ys)
        ax.set_yticklabels([f"{a} (n={int(n)})" for a, n in zip(arms, by_arm["n_seller_episodes"])], fontsize=8,
                           color=INK)
    fig.suptitle("Seller-episode outcomes by arm: rate with 95% CI (bootstrap over markets)", fontsize=11,
                 color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, out_dir, "fig_dg_outcomes")


def main(argv=None) -> list[Path]:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--analysis-dir", type=Path, required=True,
                   help="folder with market_by_hour.csv and outcomes_by_arm.csv")
    p.add_argument("--out-dir", type=Path, default=REPO / "report" / "figures")
    p.add_argument("--base-arm", default="Base")
    args = p.parse_args(argv)
    written = []
    written += ask_index_figure(pd.read_csv(args.analysis_dir / "market_by_hour.csv"), args.out_dir, args.base_arm)
    written += outcomes_figure(pd.read_csv(args.analysis_dir / "outcomes_by_arm.csv"), args.out_dir)
    for path in written:
        print(f"wrote {path}")
    return written


if __name__ == "__main__":
    main()
