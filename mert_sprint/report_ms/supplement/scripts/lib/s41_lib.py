"""Loaders, style hooks and exact tests for the S41 supplement figures (report section 4.1, Daniel's data).

Style comes from the main report's scripts/lib/style.py, imported read-only. Inputs are the copies of Daniel's
CSVs in supplement/data/daniel/ (ApartAICollusion origin/main report/data/, see SOURCE_COMMIT.txt there).

Measure used for "reported seat 5" per seller: the seller's first report names seat 5
(`report_is_scripted_seat` in outcomes.csv), as in the main report's Figure 1. Three Gemini sellers first reported
a peer and reported seat 5 later (D-hb seed 1, E seed 0); `ever_s5` adds them back, using the per-market counts
of sellers who reported seat 5 at least once (`reported_seat5` in table3_extra.csv).
"""
import sys
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SUPP = Path(__file__).resolve().parents[2]               # report_ms/supplement/
sys.path.insert(0, str(SUPP.parent / "scripts" / "lib"))  # the main report's style.py, read-only
import style  # noqa: E402

DANIEL = SUPP / "data" / "daniel"
FIG_DIR = SUPP / "figures" / "S41"

NO_WARN = ["Base", "D", "D-hs", "D-hb", "D-hsb"]
ALL_ARMS = [a for _, arms in style.ARM_GROUPS for a in arms]


def gemini_sellers():
    """Daniel's 200 Gemini seller-episodes with seat 5's name, s5 (first report names seat 5) and ever_s5."""
    o = pd.read_csv(DANIEL / "dg" / "outcomes.csv")
    m = pd.read_csv(DANIEL / "dg" / "market_by_run.csv")
    t = pd.read_csv(DANIEL / "dg" / "table3_extra.csv")
    o = o.merge(m[["run_id", "scripted_seats"]], on="run_id", how="left", validate="many_to_one")
    if len(o) != 200 or o.scripted_seats.isna().any():
        raise ValueError("expected 200 Gemini seller-episodes, each with a scripted seat")
    o["s5"] = o.report_is_scripted_seat.astype(bool)
    if not (o.s5 == (o.report_target == o.scripted_seats)).all():
        raise ValueError("report_is_scripted_seat disagrees with report_target")
    # ever_s5: a seller whose first report named a peer counts if its market's table3 count is higher
    first = o.groupby("run_id").s5.sum()
    deficit = t.set_index("run_id").reported_seat5 - first
    if (deficit < 0).any():
        raise ValueError("table3 count below the first-report count")
    o["ever_s5"] = o.s5
    for run, k in deficit[deficit > 0].items():
        cand = o.index[(o.run_id == run) & o.reported & ~o.s5]
        if len(cand) != k:
            raise ValueError(f"{run}: cannot place {k} later seat-5 reports on {len(cand)} peer reporters")
        o.loc[cand, "ever_s5"] = True
    for c in ["verbal_accept", "verbal_reject", "suspects_collusion", "suspects_test", "mentions_human_appeal",
              "reported", "false_report"]:
        o[c] = o[c].astype(bool)
    return o


def gemini_markets():
    """Daniel's 50 Gemini markets: table3 counts merged with the market criterion."""
    t = pd.read_csv(DANIEL / "dg" / "table3_extra.csv")
    m = pd.read_csv(DANIEL / "dg" / "market_by_run.csv")
    df = t.merge(m[["run_id", "ask_index", "trade_index", "trades_per_round", "passed"]], on="run_id",
                 validate="one_to_one")
    if len(df) != 50:
        raise ValueError("expected 50 Gemini markets")
    return df


def gemini_hours():
    return pd.read_csv(DANIEL / "dg" / "market_by_hour.csv")


def family_sellers(family):
    """Seller-episodes of 'dg_gpt41' or 'dg_haiku', with s5 as above."""
    o = pd.read_csv(DANIEL / family / "outcomes.csv")
    m = pd.read_csv(DANIEL / family / "market_by_run.csv")
    o = o.merge(m[["run_id", "scripted_seats", "ask_index"]], on="run_id", how="left", validate="many_to_one")
    o["s5"] = o.report_is_scripted_seat.astype(bool)
    if not (o.s5 == (o.report_target == o.scripted_seats)).all():
        raise ValueError(f"{family}: report_is_scripted_seat disagrees with report_target")
    for c in ["verbal_accept", "verbal_reject", "suspects_collusion", "suspects_test", "reported"]:
        o[c] = o[c].astype(bool)
    return o


def exact_perm_p(a, b):
    """Exact two-sided permutation p for the difference in means of two groups of markets."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    pool = np.concatenate([a, b])
    n, obs = len(a), abs(a.mean() - b.mean())
    hits = total = 0
    for idx in combinations(range(len(pool)), n):
        mask = np.zeros(len(pool), bool)
        mask[list(idx)] = True
        hits += abs(pool[mask].mean() - pool[~mask].mean()) >= obs - 1e-12
        total += 1
    return hits / total, hits, total


def save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    w, h = fig.get_size_inches()
    if abs(w - style.SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {style.SLOT_IN} in")
    path = FIG_DIR / name
    fig.savefig(path, dpi=style.DPI)
    print(f"wrote {path} ({w:.2f} x {h:.2f} in)")


def frac(k, n):
    return f"{k} of {n}"


def key_row(fig, x_in, y_in, items, gap_in=0.22, size=12):
    """A one-line key in figure inches, placed left to right from (x_in, y_in) (vertical center).
    items: (kind, style dict, label) with kind 'marker' (plot kwargs), 'patch' (facecolor) or 'line' (plot kwargs).
    Text widths are measured, so items never overlap. Returns the x (inches) where the row ends."""
    W, H = fig.get_size_inches()
    r = fig.canvas.get_renderer()
    x = x_in
    for kind, kw, label in items:
        if kind == "marker":
            fig.add_artist(plt.Line2D([(x + 0.06) / W], [y_in / H], transform=fig.transFigure, ls="none", **kw))
            x += 0.17
        elif kind == "patch":
            fig.add_artist(plt.Rectangle((x / W, (y_in - 0.06) / H), 0.18 / W, 0.12 / H,
                                         transform=fig.transFigure, **({"lw": 0} | kw)))
            x += 0.24
        elif kind == "line":
            fig.add_artist(plt.Line2D([x / W, (x + 0.34) / W], [y_in / H, y_in / H], transform=fig.transFigure,
                                      **kw))
            x += 0.42
        t = fig.text(x / W, y_in / H, label, ha="left", va="center", fontsize=size)
        x += t.get_window_extent(renderer=r).width / fig.dpi + gap_in
    return x - gap_in
