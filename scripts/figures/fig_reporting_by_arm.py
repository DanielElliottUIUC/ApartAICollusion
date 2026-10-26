"""Figure: distinct reporters of seat 5 and private messages per market, for all ten Gemini D-G arms.

New sprint code (figures-oct25). Reads only committed CSVs:
  report/data/dg/table3_extra.csv      per run (5 per arm): reported_seat5 (distinct LLM sellers, of 4, with at least
                                       one report naming seat 5, counted from the run logs) and private_msgs_llm_total
                                       (private messages sent by the four LLM sellers, including those to seat 5)
  report/data/dg/permutation_tests.csv exact two-sided permutation p-values over markets (5 vs 5)

Top panel: sellers reporting seat 5 per market (bar = mean of the 5 markets, dots = each seed; the label is the arm
total out of 20), with p-values for Base vs D, D vs D-hs and D vs D-hsb. Bottom panel: private messages per market on
the same arm axis. Blue = seat 5 sends the $96 offer; grey = seat 5 sends a neutral placebo note.

Usage:
    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_reporting_by_arm.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "report" / "data" / "dg"
OUT = REPO / "report" / "figures"
NAME = "fig_reporting_by_arm"

# Reference palette from the dataviz skill (light mode), as in scripts/make_dg_figures.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"      # arms where seat 5 makes the offer
REFERENCE = "#8c8b86"   # placebo arms (no offer)

# Arm order: no warning (Base, the plain offer, the plea 2x2), then warning arms with an offer, then without.
ARMS = ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "F-sham", "G-warn", "G-prec"]
PLACEBO = {"Base", "G-warn", "G-prec"}
PAIRS = [("Base", "D"), ("D", "D-hs"), ("D", "D-hsb")]   # annotated in the top panel


def _style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.grid(True, axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def _bars(ax, bars, width, r_in=0.03):
    """Bars with a rounded data end and a square baseline (dataviz mark spec). Call after the layout is final: the
    corner radius is set in inches and converted to each axis's data units."""
    fig = ax.figure
    box = ax.get_window_extent()
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    rx = r_in * fig.dpi / (box.width / (x1 - x0))
    ry = r_in * fig.dpi / (box.height / (y1 - y0))
    for x, h, color in bars:
        if h <= 0:
            continue
        if h < 2 * ry:  # too short to round
            ax.add_patch(Rectangle((x - width / 2, 0), width, h, facecolor=color, linewidth=0, zorder=2))
            continue
        ax.add_patch(FancyBboxPatch((x - width / 2, 0), width, h, boxstyle=f"round,pad=0,rounding_size={rx}",
                                    mutation_aspect=ry / rx, facecolor=color, linewidth=0, zorder=2))
        ax.add_patch(Rectangle((x - width / 2, 0), width, ry, facecolor=color, linewidth=0, zorder=2))


def _dots(ax, x, values, offsets):
    ax.scatter(x + offsets, values, s=16, color=INK, edgecolor=SURFACE, linewidth=0.8, zorder=4)


def _jitter(values, step=0.07):
    """Spread tied per-seed values side by side so every seed's dot is visible."""
    out = np.zeros(len(values))
    for v in set(values):
        idx = [i for i, u in enumerate(values) if u == v]
        out[idx] = (np.arange(len(idx)) - (len(idx) - 1) / 2) * step
    return out


def _fmt_p(p: float) -> str:
    return f"p = {p:.3f}" if p < 0.1 else f"p = {p:.2f}"


def main() -> list[Path]:
    t3 = pd.read_csv(DATA / "table3_extra.csv")
    perm = pd.read_csv(DATA / "permutation_tests.csv")
    assert sorted(t3.arm.unique()) == sorted(ARMS), sorted(t3.arm.unique())
    assert (t3.groupby("arm").size() == 5).all()

    plt.rcParams.update({"svg.fonttype": "path", "svg.hashsalt": NAME})  # reproducible SVG ids
    fig, (top, bot) = plt.subplots(2, 1, figsize=(6.5, 4.6), sharex=True,
                                   gridspec_kw=dict(height_ratios=[1.25, 1]))
    fig.patch.set_facecolor(SURFACE)
    for ax in (top, bot):
        _style(ax)
    xs = np.arange(len(ARMS))
    width = 0.5
    rep_mean, top_bars, bot_bars = {}, [], []
    for x, arm in zip(xs, ARMS):
        runs = t3[t3.arm == arm].sort_values("seed")
        color = REFERENCE if arm in PLACEBO else SERIES
        rep = runs.reported_seat5.tolist()
        rep_mean[arm] = np.mean(rep)
        top_bars.append((x, np.mean(rep), color))
        _dots(top, x, rep, _jitter(rep))
        top.text(x, max(rep) + 0.22, f"{sum(rep)}/20", ha="center", va="bottom", fontsize=8, color=INK)
        msgs = runs.private_msgs_llm_total.tolist()
        m = np.mean(msgs)
        bot_bars.append((x, m, color))
        _dots(bot, x, msgs, _jitter(msgs))
        label = f"{m:.0f}" if m >= 10 or m == int(m) else f"{m:.1f}"
        bot.text(x, max(msgs) + 4, label, ha="center", va="bottom", fontsize=8, color=INK)

    # p-value brackets (exact permutation over markets, from permutation_tests.csv)
    y0 = 4.85
    for i, (a, b) in enumerate(PAIRS):
        row = perm[(perm.measure == "reported_seat5") & (perm.arm_a == a) & (perm.arm_b == b)]
        assert len(row) == 1, (a, b)
        assert abs(row.mean_a.iloc[0] - rep_mean[a]) < 1e-9 and abs(row.mean_b.iloc[0] - rep_mean[b]) < 1e-9
        p = float(row.p_two_sided.iloc[0])
        xa, xb = ARMS.index(a), ARMS.index(b)
        y = y0 + i * 0.62
        top.plot([xa + 0.04, xa + 0.04, xb - 0.04, xb - 0.04], [y - 0.14, y, y, y - 0.14], color=MUTED,
                 linewidth=0.8, solid_capstyle="butt")
        top.text((xa + xb) / 2, y + 0.06, f"{a} vs {b}: {_fmt_p(p)}", ha="center", va="bottom", fontsize=8,
                 color=INK)

    top.set_ylim(0, 7.5)
    top.set_yticks([0, 1, 2, 3, 4])
    top.set_ylabel("Sellers reporting seat 5\nper market (of 4)", fontsize=8.5, color=MUTED)
    bot.set_ylim(0, 135)
    bot.set_yticks([0, 50, 100])
    bot.set_ylabel("Private messages\nper market", fontsize=8.5, color=MUTED)
    bot.set_xticks(xs)
    bot.set_xticklabels(ARMS, fontsize=8, color=INK)
    bot.set_xlim(-0.6, len(ARMS) - 0.4)
    for ax in (top, bot):  # divider between the no-warning and warning arms
        ax.axvline(4.5, color=GRID, linewidth=1.0, zorder=1)
    top.text(2.0, 7.45, "no warning", ha="center", va="top", fontsize=8, color=MUTED)
    top.text(7.0, 7.45, "warning in the prompt from hour 1", ha="center", va="top", fontsize=8, color=MUTED)
    # private-message contrasts (exact permutation over markets)
    pm = perm[perm.measure == "private_msgs_llm_total"].set_index(["arm_a", "arm_b"]).p_two_sided
    bot.text(7.0, 70, f"Base vs G-warn: {_fmt_p(pm[('Base', 'G-warn')])}\nD vs E: {_fmt_p(pm[('D', 'E')])}",
             ha="center", va="center", fontsize=8, color=INK)

    fig.legend(handles=[Patch(facecolor=SERIES, label="seat 5 offers \\$96 (hour 3)"),
                        Patch(facecolor=REFERENCE, label="seat 5 sends a placebo note"),
                        plt.Line2D([], [], marker="o", linestyle="", markersize=4.5, color=INK,
                                   markeredgecolor=SURFACE, label="one market (seed); bar = mean of 5")],
               loc="lower center", ncol=3, frameon=False, fontsize=8, labelcolor=INK, bbox_to_anchor=(0.5, -0.01),
               handlelength=1.2, columnspacing=1.4)
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=0.6)
    _bars(top, top_bars, width)
    _bars(bot, bot_bars, width)

    OUT.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("svg", "png"):
        p = OUT / f"{NAME}.{ext}"
        fig.savefig(p, format=ext, dpi=200, facecolor=SURFACE, metadata={"Date": None} if ext == "svg" else None)
        paths.append(p)
    plt.close(fig)

    summary = t3.groupby("arm").agg(reported=("reported_seat5", "sum"), per_seed=("reported_seat5", list),
                                    priv=("private_msgs_llm_total", "mean"), priv_seeds=("private_msgs_llm_total", list),
                                    to5=("private_msgs_to_seat5", "mean"), peer=("private_msgs_peer", "mean"))
    print(summary.loc[ARMS].to_string())
    for path in paths:
        print(f"wrote {path}")
    return paths


if __name__ == "__main__":
    main()
