"""Figure: run-to-run noise at hour 3, an A/A check (new sprint code).

Base, D, D-hs, D-hb and D-hsb give the Gemini sellers identical prompts through hour 3 (the offer or placebo note
is sent at hour 3 and visible from hour 4), so any difference in their hour-3 asks is noise. One dot per market
(seed) at the mean hour-3 ask of its four LLM sellers; within each arm the seeds sit on fixed sub-rows (seed 0 on
top), so the same seed can be followed across arms; a black tick marks the arm mean; the bracket spans the arm
means. For scale, the caption compares that spread with the largest arm-vs-Base difference in the per-seller ask
change (mean of hours 4-6 minus hour 3) over all ten Gemini arms.

Sources (nothing is taken from the report text):
  - report/data/dg/market_by_hour.csv, hour 3, column avg_ask (mean ask of the four LLM sellers; seat 5 excluded);
    cross-checked against report/data/dg/outcomes.csv ask_pre averaged per run (asserted equal).
  - report/data/dg/outcomes.csv, ask_change_post_offer (per seller-episode) for the ask-change comparison.

Writes report/figures/fig_aa_noise.{svg,png} and fig_aa_noise.caption.txt (caption numbers computed here).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_aa_noise.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "report" / "data" / "dg"
OUT = REPO / "report" / "figures"
NAME = "fig_aa_noise"

# Reference palette from the dataviz skill (light mode), shared with scripts/make_dg_figures.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"     # one market (seed)
REFERENCE = "#8c8b86"  # within-arm range

ARMS = ["Base", "D", "D-hs", "D-hb", "D-hsb"]   # identical seller prompts through hour 3
ARM_NOTE = {"Base": "placebo note", "D": "plain offer", "D-hs": "seller plea", "D-hb": "buyer plea",
            "D-hsb": "both pleas"}
HOUR = 3
SEEDS = range(5)
SUB = 0.15  # vertical step between seed sub-rows (row pitch = 1)


def money(x: float) -> str:
    return f"${x:.2f}"


def tex(text: str) -> str:
    """Escape dollar signs so matplotlib does not read a pair of them as mathtext."""
    return text.replace("$", r"\$")


def main() -> None:
    mbh = pd.read_csv(DATA / "market_by_hour.csv")
    h3 = mbh[(mbh["hour"] == HOUR) & mbh["arm"].isin(ARMS)].set_index(["arm", "seed"])["avg_ask"].sort_index()
    out = pd.read_csv(DATA / "outcomes.csv")
    pre = out[out["arm"].isin(ARMS)].groupby(["arm", "seed"])["ask_pre"].mean().sort_index()
    assert len(h3) == 25 and (h3 - pre).abs().max() < 1e-9, "hour-3 asks disagree between the two CSVs"

    arm_mean = h3.groupby("arm").mean().reindex(ARMS)
    arm_min, arm_max = h3.groupby("arm").min().reindex(ARMS), h3.groupby("arm").max().reindex(ARMS)
    spread = arm_mean.max() - arm_mean.min()
    by_seed = h3.unstack("arm")[ARMS]
    seed_range = by_seed.max(axis=1) - by_seed.min(axis=1)

    change = out.groupby("arm")["ask_change_post_offer"].mean()
    diff_vs_base = (change.drop("Base") - change["Base"])
    biggest_arm = diff_vs_base.abs().idxmax()
    biggest = diff_vs_base[biggest_arm]

    plt.rcParams.update({"font.size": 8, "svg.fonttype": "path", "svg.hashsalt": NAME})  # reproducible SVG ids
    fig, ax = plt.subplots(figsize=(6.5, 3.3), layout="constrained")
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.grid(True, axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    rows = {arm: len(ARMS) - 1 - i for i, arm in enumerate(ARMS)}  # Base on top
    for arm, y in rows.items():
        ax.plot([arm_min[arm], arm_max[arm]], [y, y], color=REFERENCE, linewidth=0.9, zorder=1)
        ax.plot([arm_mean[arm]] * 2, [y - 0.36, y + 0.36], color=INK, linewidth=1.6, solid_capstyle="butt",
                zorder=2)
        for s in SEEDS:
            ax.plot(h3[(arm, s)], y + (2 - s) * SUB, linestyle="none", marker="o", markersize=6.2, color=SERIES,
                    markeredgecolor=SURFACE, markeredgewidth=1.3, zorder=3)
        ax.text(97.55, y, tex(f"{money(arm_mean[arm])}  ({money(arm_max[arm] - arm_min[arm])})"), fontsize=8,
                color=INK, va="center", ha="left")

    # header row: how to read the dots (left) and the label column (right)
    head = len(ARMS) - 0.35
    ax.text(93.65, head, "within each arm, seeds 0 to 4 run top to bottom", fontsize=8,
            color=MUTED, va="center", ha="left")
    ax.text(97.55, head, "arm mean (range)", fontsize=8, color=MUTED, va="center", ha="left")

    # the spread of arm means (a bracket at its true position) and, for scale, the largest ask-change gap vs Base
    lo_m, hi_m = arm_mean.min(), arm_mean.max()
    for yb, x1, color, left, right in [
        (-0.8, hi_m, INK, "spread of arm means", money(spread)),
        (-1.3, lo_m + abs(biggest), MUTED, "largest arm-vs-Base gap in ask change", f"{money(abs(biggest))} ({biggest_arm})"),
    ]:
        ax.plot([lo_m, lo_m, x1, x1], [yb + 0.12, yb, yb, yb + 0.12], color=color, linewidth=0.9)
        ax.text(lo_m - 0.08, yb + 0.04, left, fontsize=8, color=MUTED, ha="right", va="center")
        ax.text(x1 + 0.08, yb + 0.04, tex(right), fontsize=8, color=INK, ha="left", va="center")

    ax.set_yticks(list(rows.values()))
    ax.set_yticklabels([f"{a} ({ARM_NOTE[a]})" for a in rows], fontsize=8, color=INK)
    ax.set_ylim(-1.55, len(ARMS) - 0.15)
    ax.set_xlim(93.6, 98.85)
    ax.set_xticks([94, 95, 96, 97])
    ax.xaxis.set_major_formatter(lambda v, _: f"${v:.0f}")
    ax.set_xlabel(f"Mean ask of the 4 LLM sellers at hour {HOUR} (one dot per market)", fontsize=8, color=MUTED)

    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"{NAME}.{ext}", format=ext, dpi=200, facecolor=SURFACE,
                    metadata={"Date": None} if ext == "svg" else None)
    plt.close(fig)

    lo_arm, hi_arm = arm_mean.idxmin(), arm_mean.idxmax()
    worst_seed = int(seed_range.idxmax())
    caption = (
        "Hour-3 mean ask of the four LLM sellers in each market (dots, one per seed; black tick: arm mean) in the five "
        "Gemini arms whose seller prompts are identical through hour 3: the arm means span "
        f"{money(spread)} ({money(arm_mean[lo_arm])} in {lo_arm} to {money(arm_mean[hi_arm])} in {hi_arm}), more "
        "than the largest arm-vs-Base difference in post-offer ask change in any Gemini arm "
        f"({money(abs(biggest))}, {biggest_arm}), and the same seed differs across these arms by up to "
        f"{money(seed_range[worst_seed])} (seed {worst_seed}), so differences of this size are run-to-run noise. "
        "Sources: report/data/dg/market_by_hour.csv (hour 3, avg_ask) and outcomes.csv "
        "(ask_change_post_offer: mean ask in hours 4-6 minus hour 3, averaged over each arm's seller-episodes)."
    )
    (OUT / f"{NAME}.caption.txt").write_text(caption + "\n", encoding="utf-8")
    print(by_seed.round(4).to_string())
    print(pd.DataFrame({"mean": arm_mean, "min": arm_min, "max": arm_max}).round(4).to_string())
    print("seed range across arms:", seed_range.round(4).to_dict())
    print("ask change minus Base:", diff_vs_base.round(4).to_dict())
    print(caption)


if __name__ == "__main__":
    main()
