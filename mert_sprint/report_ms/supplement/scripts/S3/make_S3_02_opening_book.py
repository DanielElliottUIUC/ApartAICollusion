"""Figure S3.2: the opening order book the harness seeds, and the asks sellers post in hour 1.

(a) The seeded book for harness seeds 0 to 8 (books.csv): four seller asks per seed at the default opening
    ($97.50 centre) and at the low opening ($90 centre), and the four buyer bids. Shaded bands are the uniform
    supports the harness draws from (centre +/- spread/2, spread 2.5; cda_types.py defaults, upstream commit
    2bb2a7e, see report_ms/provenance.md). The script checks that every run with the same seed and opening shows
    the same book, and that the $90 book is the $97.50 book moved down by $7.50.
(b) Each seller's hour-1 ask (sellers_h1.csv), by seller model and opening; messages sent in hour 1 are read only
    from hour 2, so these asks precede any seller-to-seller communication.
Data: supplement/data/S3/books.csv, sellers_h1.csv, runs.csv (build_s3_data.py), from the Hour 1 prompt of each
Seller *.md file and round 1 of unified.log in every run folder of ours (93 runs).
Output: supplement/figures/S3/S3_02_opening_book.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import s3lib  # noqa: E402

C = s3lib.COLOR
SPREAD = 2.5
BAND = "#EDEDED"


def load():
    runs = pd.read_csv(s3lib.S3DATA / "runs.csv")
    books = pd.read_csv(s3lib.S3DATA / "books.csv")
    h1 = pd.read_csv(s3lib.S3DATA / "sellers_h1.csv").merge(
        runs[["folder", "seller", "opening", "seed"]], on="folder", validate="many_to_one")
    # One book per (seed, opening), whichever run it came from.
    canon = {}
    for (fold, seed, op), g in books.groupby(["folder", "seed", "opening"]):
        key = (tuple(sorted(g.loc[g.side == "ask", "price"])), tuple(sorted(g.loc[g.side == "bid", "price"])))
        if canon.setdefault((seed, op), key) != key:
            raise ValueError(f"seed {seed}, opening {op}: runs show different opening books")
    for (seed, op), (asks, bids) in canon.items():
        if op == 90.0:
            hi = canon[(seed, 97.5)]
            if bids != hi[1] or not np.allclose(np.array(asks) + 7.5, hi[0], atol=1e-9):
                raise ValueError(f"seed {seed}: $90 book is not the $97.50 book moved down by $7.50")
        lo_a, hi_a = op - SPREAD / 2, op + SPREAD / 2
        if min(asks) < lo_a or max(asks) > hi_a or min(bids) < 81.25 or max(bids) > 83.75:
            raise ValueError(f"seed {seed}, opening {op}: book outside the uniform support")
    nruns = books.drop_duplicates("folder").groupby(["seed", "opening"]).size()
    return runs, canon, nruns, h1


def panel_a(ax, canon, nruns):
    for lo, hi in ((96.25, 98.75), (88.75, 91.25), (81.25, 83.75)):
        ax.axhspan(lo, hi, color=BAND, lw=0, zorder=0)
    s3lib.ref_lines(ax)
    seeds = sorted({s for s, _ in canon})
    for s in seeds:
        hi_a, bids = canon[(s, 97.5)]
        lo_a, _ = canon[(s, 90.0)]
        ax.plot([s] * 4, hi_a, "o", ms=6, mfc=s3lib.GRAY, mec=s3lib.GRAY, zorder=3)
        ax.plot([s] * 4, lo_a, "o", ms=6, mfc="white", mec=s3lib.GRAY, mew=1.2, zorder=3)
        ax.plot([s] * 4, bids, "s", ms=4.5, mfc=s3lib.LIGHT, mec=s3lib.GRAY, mew=0.8, zorder=3)
    ax.set_xlim(-0.6, 8.6)
    ax.set_ylim(80, 100.5)
    ax.set_xticks(seeds)
    ax.set_xlabel("Harness seed")
    ax.set_ylabel("Price ($)")
    ax.set_yticks([80, 85, 90, 95, 100])
    kw = dict(fontsize=12, ha="left", va="center", color=s3lib.GRAY)
    ax.text(2.55, 99.6, "asks, opening $97.50", **kw)
    ax.text(2.55, 92.2, "asks, opening $90 (the same draws)", **kw)
    ax.text(2.55, 84.8, "bids (same at both openings)", **kw)
    lab = "  ".join(f"{int(nruns.loc[(s, 97.5)])}" for s in seeds)
    return lab


GROUPS = [(97.5, "sol"), (97.5, "gemini"), (97.5, "luna"), (97.5, "grok"), (97.5, "haiku"),
          (90.0, "sol"), (90.0, "gemini"), (90.0, "luna")]
SHORT = {"sol": "Sol", "gemini": "Gemini", "luna": "Luna", "grok": "Grok", "haiku": "Haiku"}


def panel_b(ax, h1):
    rng = np.random.default_rng(0)
    xs = []
    stats = []
    for i, (op, s) in enumerate(GROUPS):
        x = i + (0.6 if op == 90.0 else 0.0)
        xs.append(x)
        ax.add_patch(plt.Rectangle((x - 0.42, op - SPREAD / 2), 0.84, SPREAD, color=BAND, lw=0, zorder=0))
        g = h1[(h1.opening == op) & (h1.seller == s)]
        y = g["h1_ask"].to_numpy()
        jit = rng.uniform(-0.3, 0.3, len(y))
        ax.plot(x + jit, y, "o", ms=4.2, mfc=s3lib.tint(C[s], 0.35), mec=C[s], mew=0.7, alpha=0.9, zorder=3)
        med = float(np.median(y))
        inside = float(((y >= op - SPREAD / 2) & (y <= op + SPREAD / 2)).mean())
        stats.append({"opening": op, "seller": s, "sellers": len(y), "runs": g["folder"].nunique(),
                      "median": med, "min": y.min(), "max": y.max(), "inside_band": inside,
                      "at_or_below_91": int((y <= 91.0).sum()), "at_or_above_95_8": int((y >= 95.8).sum())})
    s3lib.ref_lines(ax)
    ax.set_xticks(xs)
    ax.set_xticklabels([SHORT[s] for _, s in GROUPS])
    for t, (_, s) in zip(ax.get_xticklabels(), GROUPS):
        t.set_color(C[s])
    ax.set_xlim(-0.6, xs[-1] + 0.6)
    ax.set_ylim(80, 100.5)
    ax.set_yticks([80, 85, 90, 95, 100])
    ax.set_ylabel("Hour-1 ask ($)")
    sep = (xs[4] + xs[5]) / 2
    ax.axvline(sep, color=s3lib.LIGHT, lw=0.9)
    ax.text((xs[0] + xs[4]) / 2, 101.3, "opened at $97.50", ha="center", va="bottom", fontsize=12)
    ax.text((xs[5] + xs[7]) / 2, 101.3, "opened at $90", ha="center", va="bottom", fontsize=12)
    return pd.DataFrame(stats)


def main():
    s3lib.setup()
    runs, canon, nruns, h1 = load()
    fig = plt.figure(figsize=(s3lib.SLOT_IN, 6.9))
    axa = fig.add_axes([0.125, 0.585, 0.855, 0.37])
    axb = fig.add_axes([0.125, 0.075, 0.855, 0.37])
    panel_a(axa, canon, nruns)
    st = panel_b(axb, h1)
    s3lib.panel_letter(axa, "a", x=-0.115, y=1.0)
    s3lib.panel_letter(axb, "b", x=-0.115, y=1.08)
    pd.set_option("display.width", 200)
    print(st.round(2).to_string(index=False))
    print("runs per seed at $97.50:", nruns.xs(97.5, level="opening").to_dict(),
          "at $90:", nruns.xs(90.0, level="opening").to_dict())
    print("sellers with an hour-1 ask:", len(h1), "in", h1.folder.nunique(), "runs")
    s3lib.save(fig, "S3_02_opening_book.png")


if __name__ == "__main__":
    main()
