"""Figure: D's asks were already falling faster than Base's before the offer (new sprint code).

Mean ask of the four LLM sellers by hour (hours 1-8) for Base (placebo note) and D (plain undercover offer), each
the mean over 5 seeds with the min-max band over seeds. Vertical lines mark the hour seat 5 sends its message
(hour 3; in D its own ask also drops to $96 that hour) and the hour the message becomes visible (hour 4). The
inset table gives the change in the arm-mean ask per hour over hours 1-3 (before anything differs between the
arms: seller prompts are identical through hour 3) and over hours 3-6, as endpoint slopes:
(mean ask at the later hour - mean ask at the earlier hour) / (number of hours).

Source (nothing is taken from the report text): report/data/dg/market_by_hour.csv, column avg_ask (mean ask of
the four LLM sellers in that run-hour; seat 5 excluded).

Writes report/figures/fig_pretrend.{svg,png} and fig_pretrend.caption.txt (caption numbers computed here).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_pretrend.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "report" / "data" / "dg" / "market_by_hour.csv"
OUT = REPO / "report" / "figures"
NAME = "fig_pretrend"

# Reference palette from the dataviz skill (light mode), shared with scripts/make_dg_figures.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"     # the treated arm (D)
REFERENCE = "#8c8b86"  # Base, benchmarks
WASH = 0.12            # band opacity (a wash, never a block)

ARMS = [("D", "D (undercover offer)", SERIES), ("Base", "Base (placebo note)", REFERENCE)]
HOURS = range(1, 9)
OFFER_SENT, OFFER_VISIBLE, OFFER_PRICE = 3, 4, 96.0
WINDOWS = [(1, 3), (3, 6)]


def slope(mean: pd.Series, a: int, b: int) -> float:
    return (mean[b] - mean[a]) / (b - a)


def fmt(x: float) -> str:
    return f"{x:.2f}".replace("-", "−")


def main() -> None:
    df = pd.read_csv(DATA)
    df = df[df["arm"].isin([a for a, _, _ in ARMS]) & df["hour"].isin(HOURS)]
    stats = df.groupby(["arm", "hour"])["avg_ask"].agg(["mean", "min", "max", "count"])
    n_runs = df.groupby("arm")["run_id"].nunique()
    assert (stats["count"] == 5).all() and (n_runs == 5).all(), "expected 5 seeds per arm-hour"
    means = {arm: stats.loc[arm, "mean"] for arm, _, _ in ARMS}
    slopes = {(arm, w): slope(means[arm], *w) for arm, _, _ in ARMS for w in WINDOWS}
    gap = {h: means["D"][h] - means["Base"][h] for h in HOURS}

    plt.rcParams.update({"font.size": 8, "svg.fonttype": "path", "svg.hashsalt": NAME})  # reproducible SVG ids
    fig, ax = plt.subplots(figsize=(6.5, 3.1), layout="constrained")
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.grid(True, axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    lo = stats["min"].min() - 0.45
    hi = 98.75
    ax.set_xlim(0.7, 9.35)
    ax.set_ylim(lo, hi)

    # hours 1-3: identical seller prompts in both arms (a bracket, not a shaded span, so it is not read as a band)
    yb = 97.55
    ax.plot([1, 1, OFFER_SENT, OFFER_SENT], [yb - 0.1, yb, yb, yb - 0.1], color=MUTED, linewidth=0.9)
    ax.text((1 + OFFER_SENT) / 2, yb + 0.07, "identical seller prompts", fontsize=8, color=MUTED, ha="center",
            va="bottom")
    for h, label, ha, dx in [(OFFER_SENT, "offer sent", "right", -0.06), (OFFER_VISIBLE, "offer visible", "left", 0.06)]:
        ax.axvline(h, color=MUTED, linewidth=0.9, zorder=1)
        ax.text(h + dx, lo + 0.12, label, fontsize=8, color=MUTED, ha=ha, va="bottom")
    ax.axhline(OFFER_PRICE, color=REFERENCE, linewidth=0.9, linestyle=(0, (4, 3)), zorder=1)
    ax.text(9.3, OFFER_PRICE + 0.06, "offer price $96", fontsize=8, color=MUTED, ha="right", va="bottom")

    for arm, label, color in ARMS:
        s = stats.loc[arm]
        ax.fill_between(s.index, s["min"], s["max"], color=color, alpha=WASH, linewidth=0, zorder=2)
        ax.plot(s.index, s["mean"], color=color, linewidth=2, solid_capstyle="round", zorder=3)
        ax.plot(s.index, s["mean"], linestyle="none", marker="o", markersize=5, color=color,
                markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4)
        ax.text(8.15, s["mean"][8], label, fontsize=8, color=INK, va="center", ha="left")

    # slope table, top right (it is also the legend: a line key per arm)
    x0, y0, dy = 5.15, 98.5, 0.36
    ax.text(x0, y0, "Change in arm-mean ask ($ per hour)", fontsize=8, color=INK, va="center")
    cols = [7.15, 8.05]
    for c, (a, b) in zip(cols, WINDOWS):
        ax.text(c, y0 - dy, f"hours {a}–{b}", fontsize=8, color=MUTED, va="center", ha="right")
    for i, (arm, _, color) in enumerate(ARMS, start=2):
        y = y0 - i * dy
        ax.plot([x0, x0 + 0.22], [y, y], color=color, linewidth=2, solid_capstyle="round")
        ax.text(x0 + 0.3, y, arm, fontsize=8, color=INK, va="center")
        for c, w in zip(cols, WINDOWS):
            ax.text(c, y, fmt(slopes[(arm, w)]), fontsize=8, color=INK, va="center", ha="right")

    ax.set_xticks(list(HOURS))
    ax.set_xlabel("Hour", fontsize=8, color=MUTED)
    ax.set_ylabel("Mean ask of the 4 LLM sellers ($)", fontsize=8, color=MUTED)
    ax.set_yticks(range(int(lo) + 1, 98))  # no ticks in the headroom that holds the bracket and the table
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}")

    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"{NAME}.{ext}", format=ext, dpi=200, facecolor=SURFACE,
                    metadata={"Date": None} if ext == "svg" else None)
    plt.close(fig)

    d13, b13 = slopes[("D", (1, 3))], slopes[("Base", (1, 3))]
    d36, b36 = slopes[("D", (3, 6))], slopes[("Base", (3, 6))]
    caption = (
        "Mean ask of the four LLM sellers by hour in Base (placebo note) and D (undercover offer), Gemini 3.8 Flash "
        "sellers, 5 seeds per arm (line: mean; band: min-max over seeds); the offer is sent at hour 3, when seat 5's "
        "own ask also drops to $96, and is visible from hour 4. With identical seller prompts through hour 3, D's "
        f"mean ask already fell ${-d13:.2f} per hour over hours 1-3 against ${-b13:.2f} in Base (${-gap[3]:.2f} "
        f"below Base by hour 3), about as fast as after the offer (${-d36:.2f} vs ${-b36:.2f} per hour over hours "
        "3-6), so D's fall predates the offer. Slopes: endpoint change in the arm-mean ask divided by hours elapsed; "
        "source: report/data/dg/market_by_hour.csv (avg_ask)."
    )
    (OUT / f"{NAME}.caption.txt").write_text(caption + "\n", encoding="utf-8")
    print(stats.round(3).to_string())
    print({f"{a} h{w[0]}-{w[1]}": round(v, 4) for (a, w), v in slopes.items()})
    print({h: round(v, 3) for h, v in gap.items()})
    print(caption)


if __name__ == "__main__":
    main()
