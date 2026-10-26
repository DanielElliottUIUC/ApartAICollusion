"""Shared loaders, statistics and layout helpers for the S4.2 supplement figures (Daniel's 50 Gemini markets).

Inputs, all in report_ms/supplement/data/daniel/dg/ (copies of ApartAICollusion origin/main report/data/dg/,
commit e8c48ed, whose report/data is identical to b7cbccd, the copy the main report uses):
  market_by_hour.csv   one row per market-hour: LLM sellers' mean ask, LLM sellers' trades and mean trade price
  market_by_run.csv    one row per market: last-third ask index, trade index, joint criterion
  table3_extra.csv     one row per market: public and private message counts
  outcomes.csv         one row per LLM seller-episode: judge labels and their first hour, per-seller asks

Style (colors, reference lines, font floors, arm order) comes from s42style.py, a frozen copy of
report_ms/scripts/lib/style.py. Every figure script returns its caption numbers from these loaders, so the text and the figure share data.
"""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SUPP = HERE.parents[1]                                 # report_ms/supplement/
MS = SUPP.parent                                       # report_ms/
DATA = SUPP / "data" / "daniel" / "dg"
FIGURES = SUPP / "figures" / "S42"
SRC = "supplement/data/daniel/dg"                      # how Source lines name the data folder

import s42style as style  # noqa: E402  (frozen copy of report_ms/scripts/lib/style.py)

HOURS = list(range(1, 16))
LAST_THIRD = list(range(11, 16))
COST = 80.0                                            # seller cost per lot, $
ARMS = [a for _, arms in style.ARM_GROUPS for a in arms]
WARN = set(style.ARM_GROUPS[1][1])                     # E, F, F-sham, G-warn, G-prec
NO_OFFER = style.NO_OFFER                              # Base, G-warn, G-prec
BLUE = style.COLOR["gemini"]
N_BOOT = 10_000
SEED = 20261025


# ---------------------------------------------------------------- data

def hours():
    """market_by_hour.csv with a per-hour LLM-seller profit column: trades x (mean trade price - $80)."""
    h = pd.read_csv(DATA / "market_by_hour.csv")
    if len(h) != 750 or sorted(h["hour"].unique()) != HOURS:
        raise ValueError("expected 50 markets x 15 hours")
    h["profit"] = h["trades"] * (h["avg_trade_price"] - COST)
    h.loc[h["trades"] == 0, "profit"] = 0.0
    if h["profit"].isna().any():
        raise ValueError("an hour with trades has no trade price")
    return h


def markets():
    """One row per market: arm, seed, last-third indices, passed, message counts, trades, profit, margin,
    hour-3 mean ask and first trading hour."""
    run = pd.read_csv(DATA / "market_by_run.csv")
    t3 = pd.read_csv(DATA / "table3_extra.csv")
    h = hours()
    agg = h.groupby("run_id").agg(trades=("trades", "sum"), profit=("profit", "sum")).reset_index()
    ask3 = h[h["hour"] == 3].set_index("run_id")["avg_ask"].rename("ask_h3")
    first = h[h["trades"] > 0].groupby("run_id")["hour"].min().rename("first_trade_hour")
    df = (run.merge(t3.drop(columns=["arm", "seed"]), on="run_id", validate="one_to_one")
          .merge(agg, on="run_id", validate="one_to_one")
          .join(ask3, on="run_id").join(first, on="run_id"))
    if len(df) != 50 or sorted(df.groupby("arm").size().unique()) != [5]:
        raise ValueError("expected 10 arms x 5 markets")
    df["margin"] = df["profit"] / df["trades"]
    df["warn"] = df["arm"].isin(WARN)
    return df


def sellers():
    """outcomes.csv: one row per LLM seller-episode (20 per arm)."""
    o = pd.read_csv(DATA / "outcomes.csv")
    if len(o) != 200 or sorted(o.groupby("arm").size().unique()) != [20]:
        raise ValueError("expected 10 arms x 20 seller-episodes")
    return o


# ---------------------------------------------------------------- statistics

def boot_mean_ci(values, n_boot=N_BOOT, seed=SEED):
    """Percentile 95% interval of the mean, resampling the given values (markets) with replacement."""
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), size=(n_boot, len(v)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def boot_band(matrix, n_boot=N_BOOT, seed=SEED):
    """matrix: markets x hours. Resamples whole markets (rows), so each draw keeps a market's path intact.
    Returns (mean, lo, hi) per column."""
    m = np.asarray(matrix, dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, m.shape[0], size=(n_boot, m.shape[0]))
    means = m[idx].mean(axis=1)                         # n_boot x hours
    return m.mean(axis=0), np.percentile(means, 2.5, axis=0), np.percentile(means, 97.5, axis=0)


def perm_p(a, b):
    """Exact two-sided permutation p for a difference in means between two small groups of markets
    (all C(n_a + n_b, n_a) relabellings; 252 for 5 vs 5)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    pool = np.concatenate([a, b])
    obs = abs(a.mean() - b.mean())
    n, k = len(pool), len(a)
    hits = total = 0
    for idx in combinations(range(n), k):
        mask = np.zeros(n, bool)
        mask[list(idx)] = True
        d = abs(pool[mask].mean() - pool[~mask].mean())
        hits += d >= obs - 1e-12
        total += 1
    return hits / total


def pearson(x, y):
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


# ---------------------------------------------------------------- layout

def save(fig, name):
    """Save at 300 dpi into supplement/figures/S42/, refusing any width but the 6.5 in slot."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    w, h = fig.get_size_inches()
    if abs(w - style.SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {style.SLOT_IN} in")
    check_text(fig, name)
    path = FIGURES / name
    fig.savefig(path, dpi=style.DPI)
    print(f"wrote {path} ({w:.2f} x {h:.2f} in)")
    return path


def check_text(fig, name):
    """Owner font rule (axis labels >= 14 pt, ticks >= 12, titles >= 16, all other text >= 12) and no text
    outside the canvas. Raises on the first breach."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    for ax in fig.axes:
        for t, floor in ((ax.xaxis.label, 14), (ax.yaxis.label, 14), (ax.title, 16)):
            if t.get_text() and t.get_fontsize() < floor:
                raise ValueError(f"{name}: '{t.get_text()}' at {t.get_fontsize()} pt, floor {floor}")
        for t in ax.get_xticklabels() + ax.get_yticklabels():
            if t.get_text() and t.get_fontsize() < 12:
                raise ValueError(f"{name}: tick '{t.get_text()}' under 12 pt")
    hidden = set()                                     # tick labels outside the view are never drawn
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            lo, hi = sorted(axis.get_view_interval())
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                if not lo - 1e-9 <= tick.get_loc() <= hi + 1e-9:
                    hidden.update({id(tick.label1), id(tick.label2)})
    for t in fig.findobj(lambda a: hasattr(a, "get_fontsize") and hasattr(a, "get_text")):
        if not t.get_text() or not t.get_visible() or id(t) in hidden:
            continue
        if t.get_fontsize() < 12:
            raise ValueError(f"{name}: '{t.get_text()}' at {t.get_fontsize()} pt, floor 12")
        e = t.get_window_extent(r)
        if e.x0 < -0.5 or e.y0 < -0.5 or e.x1 > W + 0.5 or e.y1 > H + 0.5:
            raise ValueError(f"{name}: '{t.get_text()}' runs off the canvas")


def small_multiples(fig, left, right, bottom, top, wgap, hgap, nrows=2, ncols=5):
    """A grid of axes placed in inches; returns axes[row][col]."""
    W, H = fig.get_size_inches()
    pw = (W - left - right - (ncols - 1) * wgap) / ncols
    ph = (H - bottom - top - (nrows - 1) * hgap) / nrows
    axes = []
    for r in range(nrows):
        row = []
        for c in range(ncols):
            x0 = left + c * (pw + wgap)
            y0 = H - top - (r + 1) * ph - r * hgap
            row.append(fig.add_axes([x0 / W, y0 / H, pw / W, ph / H]))
        axes.append(row)
    return axes


def warn_face(ax):
    """Pale warning band behind an axes whose arm carries the warning (as in the main report's Figure 2)."""
    ax.set_facecolor(style.WARN_BAND)


def fmt_p(p):
    """Three decimals below 0.1 (as the main report writes 0.008 and 0.048), two above."""
    return f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def arm_matrix(h, arm, col):
    """markets x hours matrix of one market_by_hour column for one arm (5 x 15)."""
    w = h[h["arm"] == arm].pivot(index="run_id", columns="hour", values=col)
    if w.shape != (5, 15):
        raise ValueError(f"{arm}: expected 5 markets x 15 hours")
    return w[HOURS].to_numpy(dtype=float)


def hourly_grid(mats, ylim, yticks, yticklabels, ylabel, fig_h=5.3, price_refs=False, left=0.86):
    """Ten panels (rows: no warning, warning), one per arm: arm mean over markets (blue), a 95% bootstrap band
    over markets, and the Base mean in gray in every other panel. mats: arm -> markets x hours matrix.
    Returns (fig, stats) with stats[arm] = (mean, lo, hi) per hour."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig = plt.figure(figsize=(style.SLOT_IN, fig_h))
    axes = small_multiples(fig, left=left, right=0.14, bottom=0.66, top=0.80, wgap=0.10, hgap=0.56)
    base_mean = mats["Base"].mean(axis=0)
    stats = {}
    for r, (_, arms) in enumerate(style.ARM_GROUPS):
        for c, arm in enumerate(arms):
            ax = axes[r][c]
            mean, lo, hi = boot_band(mats[arm])
            stats[arm] = (mean, lo, hi)
            if arm in WARN:
                warn_face(ax)
            if price_refs:
                style.ref_lines(ax, "price")
            if arm != "Base":
                ax.plot(HOURS, base_mean, color=style.GRAY, lw=1.3, zorder=2)
            ax.fill_between(HOURS, lo, hi, color=style.tint(BLUE, 0.6), lw=0, zorder=1)
            ax.plot(HOURS, mean, color=BLUE, lw=2.0, zorder=3)
            ax.set_xlim(0.5, 15.5)
            ax.set_ylim(*ylim)
            ax.set_xticks([3, 9, 15])
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticklabels if c == 0 else [])
            ax.set_title(arm, pad=4)
        pos = axes[r][0].get_position()
        fig.text(0.06 / style.SLOT_IN, pos.y1 + 0.04 / fig_h, "ab"[r], fontsize=16, fontweight="bold",
                 ha="left", va="bottom")
        fig.text(0.10 / style.SLOT_IN, (pos.y0 + pos.y1) / 2, ylabel, rotation=90, ha="left", va="center",
                 fontsize=14)
    x_mid = (axes[0][0].get_position().x0 + axes[0][4].get_position().x1) / 2
    fig.text(x_mid, 0.10 / fig_h, "Hour", ha="center", va="bottom", fontsize=14)
    handles = [Line2D([], [], color=BLUE, lw=2.0), Patch(color=style.tint(BLUE, 0.6)),
               Line2D([], [], color=style.GRAY, lw=1.3), Patch(facecolor=style.WARN_BAND, edgecolor=style.LIGHT)]
    fig.legend(handles, ["Arm mean", "95% band", "Base mean", "Warning in the prompt"], loc="upper center",
               ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.0), handlelength=1.6, handletextpad=0.4,
               columnspacing=1.0)
    return fig, stats


def draw_arm_dots(ax, v, rows, ci=True):
    """One dot per market (offset by seed), filled when it meets the joint criterion; a black bar at the arm
    mean and, when ci is True, a thin black line over its 95% percentile bootstrap interval over markets.
    v: DataFrame with columns arm, seed, value, passed."""
    for _, arm, y in rows:
        sub = v[v["arm"] == arm].sort_values("seed")
        if list(sub["seed"]) != [0, 1, 2, 3, 4]:
            raise ValueError(f"{arm}: expected seeds 0 to 4")
        for _, r in sub.iterrows():
            ax.plot([r["value"]], [y + (r["seed"] - 2) * 0.12], ls="none", marker="o", ms=6, mew=1.2, mec=BLUE,
                    mfc=(BLUE if r["passed"] else "white"), zorder=3, clip_on=False)
        if ci:
            lo, hi = boot_mean_ci(sub["value"])
            ax.plot([lo, hi], [y, y], color="black", lw=1.0, zorder=2)
        ax.plot([sub["value"].mean()] * 2, [y - 0.36, y + 0.36], color="black", lw=2.0, solid_capstyle="butt",
                zorder=4)


def setup_arm_axes(fig, axes, band_x1=1.0):
    """Arm labels on axes[0], group headers in the left margin and the pale warning band behind the warning
    rows, from the figure's left edge to band_x1 (figure fraction). Every axes shares the arm rows."""
    from matplotlib.transforms import blended_transform_factory
    rows, heads, (w0, w1) = style.arm_rows()
    for i, ax in enumerate(axes):
        ax.patch.set_alpha(0.0)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_ylim(rows[-1][2] + 0.5, 0.0)
        ax.set_yticks([y for _, _, y in rows], ([arm for _, arm, _ in rows] if i == 0 else []))
    axes[0].tick_params(axis="y", pad=4)
    style.row_band(fig, axes[0], w0, w1, style.WARN_BAND, x0=0.0, x1=band_x1)
    tr = blended_transform_factory(fig.transFigure, axes[0].transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        axes[0].text(0.06 / style.SLOT_IN, y, group, transform=tr, ha="left", va="center", fontsize=12,
                     fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY), zorder=6,
                     bbox={"facecolor": (style.WARN_BAND if warn else "white"), "edgecolor": "none", "pad": 0.5})
    return rows


def dots_legend(fig, ci=True, handles=(), labels=()):
    from matplotlib.lines import Line2D
    h = [Line2D([], [], ls="none", marker="o", ms=6, mew=1.2, mec=BLUE, mfc=BLUE),
         Line2D([], [], ls="none", marker="o", ms=6, mew=1.2, mec=BLUE, mfc="white"),
         Line2D([], [], ls="none", marker="|", ms=11, mew=2.0, color="black")]
    lab = ["Meets the criterion", "Does not", "Mean"]
    if ci:
        h.append(Line2D([], [], color="black", lw=1.0))
        lab.append("95% interval")
    h, lab = h + list(handles), lab + list(labels)
    fig.legend(h, lab, loc="upper center", ncol=len(lab), frameon=False, bbox_to_anchor=(0.5, 1.0),
               handletextpad=0.25, columnspacing=1.0, handlelength=1.2)


def arm_dot_figure(cols, fig_h=5.2, ci=True, col_gap=0.45, lab_w=0.98, right=0.16, top=0.78, bottom=0.98):
    """Arm rows (the main report's order, warning arms on the pale band) by several dot panels.

    cols: list of dicts with keys values (DataFrame: arm, seed, value, passed), xlim, xticks, xlabel, title and
    optionally xticklabels. Returns (fig, axes, rows)."""
    import matplotlib.pyplot as plt
    W = style.SLOT_IN
    n = len(cols)
    y0_in, y1_in = bottom, fig_h - top
    pw = (W - lab_w - right - (n - 1) * col_gap) / n
    fig = plt.figure(figsize=(W, fig_h))
    axes = [fig.add_axes([(lab_w + i * (pw + col_gap)) / W, y0_in / fig_h, pw / W, (y1_in - y0_in) / fig_h])
            for i in range(n)]
    rows = setup_arm_axes(fig, axes)
    for i, (ax, col) in enumerate(zip(axes, cols)):
        draw_arm_dots(ax, col["values"], rows, ci)
        ax.set_xlim(*col["xlim"])
        ax.set_xticks(col["xticks"])
        if "xticklabels" in col:
            ax.set_xticklabels(col["xticklabels"])
        ax.set_xlabel(col["xlabel"])
        ax.set_title(col["title"], pad=6)
        x_in = ax.get_position().x0 * W
        fig.text((x_in - 0.02 if i else 0.06) / W, (y1_in + 0.08) / fig_h, "abcdef"[i], fontsize=16,
                 fontweight="bold", ha=("right" if i else "left"), va="bottom")
    dots_legend(fig, ci)
    return fig, axes, rows
