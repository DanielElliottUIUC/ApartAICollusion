"""S43.3: where the split starts and what does not separate the models. Frontier runs only (36).

(a) Every seller's hour-1 ask (4 sellers x 12 runs per model), as a dot histogram in $0.50 bins.
(b) For each hour, the number of the 12 runs per model in which all asking sellers posted asks within $0.05
    of each other (max ask minus min ask <= $0.05).
Data: data/s43/s43_seller_asks.csv joined to data/s43/s43_runs.csv (phase frontier).
Output: figures/S43/S43_03_matching_asks.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_03_matching_asks.png"
MODELS = ["sol", "luna", "grok"]
TOL = 0.05
BIN = 0.4          # asks within $0.40 of a group's lowest ask are stacked side by side at the group median


def make():
    L.setup()
    f = L.frontier36()
    a = L.seller_asks()
    a = a[a.folder.isin(f.folder)].merge(f[["folder", "seller"]], on="folder")
    h1 = a[a.hour == 1]
    if not (h1.groupby("seller").size() == 48).all():
        raise ValueError("expected 48 hour-1 asks per model")
    spread = a.groupby(["seller", "folder", "hour"]).ask.agg(lambda v: v.max() - v.min()).reset_index()
    spread["tight"] = spread.ask <= TOL + 1e-9
    tight = spread.groupby(["seller", "hour"]).tight.sum().unstack()
    nask = a.groupby(["folder", "hour"]).size()
    short = nask[nask < 4]

    fig = plt.figure(figsize=(L.SLOT_IN, 7.0))
    ax1 = fig.add_axes([0.13, 0.555, 0.84, 0.405])
    ax2 = fig.add_axes([0.13, 0.08, 0.66, 0.36])

    # (a) dot histogram of hour-1 asks
    L.ref_lines(ax1)
    dx = 0.026
    for i, m in enumerate(MODELS):
        v = np.sort(h1[h1.seller == m].ask.to_numpy())
        for c in _clusters(v, BIN):
            k = len(c)
            xs = i + (np.arange(k) - (k - 1) / 2) * dx
            ax1.plot(xs, [np.median(c)] * k, "o", ms=4.2, color=L.COLOR[m], mew=0, zorder=3)
    ax1.set_xlim(-0.55, 2.55)
    ax1.set_ylim(80, 100)
    ax1.set_xticks(range(3))
    ax1.set_xticklabels([L.NAME[m] for m in MODELS])
    ax1.tick_params(axis="x", length=0)
    for lab, m in zip(ax1.get_xticklabels(), MODELS):
        lab.set_color(L.COLOR[m])
    ax1.set_yticks([80, 85, 90, 95, 100])
    ax1.set_ylabel("Hour-1 ask ($)")
    ax1.spines["bottom"].set_visible(False)
    L.panel_letter(ax1, "a", x=-0.1, y=1.0)

    # (b) runs with matching asks, by hour
    L.window(ax2)
    hours = np.array(L.HOURS)
    ends = []
    for m in MODELS:
        y = tight.loc[m, L.HOURS].to_numpy(float)
        ax2.plot(hours, y, color=L.COLOR[m], lw=2.0, marker="o", ms=4, zorder=3)
        ends.append((y[-1], L.SHORT[m], L.COLOR[m]))
    ax2.set_xlim(0.5, 15.5)
    ax2.set_ylim(-0.5, 12.5)
    ax2.set_yticks([0, 4, 8, 12])
    ax2.set_xticks([1, 5, 10, 15])
    ax2.set_xlabel("Hour")
    ax2.set_ylabel("Runs with asks\nwithin 5 cents")
    _end_labels(ax2, ends, 16.0)
    L.panel_letter(ax2, "b", x=-0.13, y=1.0)
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    q = {m: h1[h1.seller == m].ask for m in MODELS}
    ge95 = {m: int((q[m] >= 95).sum()) for m in MODELS}
    below90 = {m: int((q[m] < 90).sum()) for m in MODELS}
    t = {m: tight.loc[m] for m in MODELS}
    last5 = {m: int(t[m][L.LAST_THIRD].min()) for m in MODELS}
    if len(short) and set(short.index.get_level_values(0)) - set(f.folder):
        raise ValueError("unexpected short hours")
    short_runs = sorted(set(short.index.get_level_values(0)))
    caption = (
        f"Where the split starts, in the 36 frontier runs. (a) Every seller's ask in hour 1, its first decision "
        f"after the harness seeds the book near $97.50, for 48 sellers per model (4 in each of 12 runs). Asks "
        f"within ${BIN:.2f} of each other are stacked side by side at their median. (b) For each hour, the number "
        f"of a model's 12 runs in which all asks lay within $0.05 of each other. In one Sol run "
        f"({Path(short_runs[0]).name.split('_', 2)[2]}) one seller posted no ask in hours "
        f"{min(h for (fo, h) in short.index)} to {max(h for (fo, h) in short.index)}, and its spread uses the "
        f"three sellers who did. Grey lines mark $90 (dashed), $95 (dotted) and $97.50 (thin solid), and the "
        f"pale band covers hours 11 to 15.")
    shows = (
        f"In hour 1 all {ge95['sol']} Sol sellers asked $95 or more ({L.usd(q['sol'].min())} to "
        f"{L.usd(q['sol'].max())}), while {below90['luna']} Luna and {below90['grok']} Grok sellers already asked "
        f"below $90. Luna splits in two, with {ge95['luna']} sellers at $95 or more and "
        f"{int((q['luna'] < 85).sum())} below $85, near the buyers' seeded bids. Matching asks do not separate "
        f"the models, because in hours 11 to 15 at least {last5['sol']}, {last5['luna']} and {last5['grok']} of "
        f"12 runs match for Sol, Luna and Grok, whether the price is near $86 or near $97. Tight clustering of "
        f"asks is therefore no evidence of a high price.")
    if len(short_runs) != 1 or ge95["sol"] != 48:
        raise ValueError("text assumptions no longer hold")
    return {"title": "Sol starts high, and every model ends with matching asks", "file": FILE,
            "caption": caption, "shows": shows,
            "source": "data/s43/s43_seller_asks.csv (seller_asks of each hour in unified.log) and "
                      "data/s43/s43_runs.csv, phase frontier; figure script scripts/S43/make_s43_03_matching_asks.py.",
            "path": path}


def _clusters(v, width):
    """Split sorted values into groups whose members lie within `width` of the group's first value."""
    out, cur = [], [v[0]]
    for x in v[1:]:
        if x - cur[0] <= width:
            cur.append(x)
        else:
            out.append(cur)
            cur = [x]
    out.append(cur)
    return out


def _end_labels(ax, items, x, gap_in=0.2):
    fig = ax.figure
    h_in = ax.get_position().height * fig.get_size_inches()[1]
    lo, hi = ax.get_ylim()
    gap = gap_in * (hi - lo) / h_in
    items = sorted(items, key=lambda t: t[0])
    pos = [it[0] for it in items]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    shift = (sum(it[0] for it in items) - sum(pos)) / len(pos)
    pos = [p + shift for p in pos]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    for (y, text, color), py in zip(items, pos):
        ax.text(x, py, text, ha="left", va="center", fontsize=12, color=color, clip_on=False)
        if abs(py - y) > gap * 0.15:
            ax.plot([15.6, x - 0.1], [y, py], color=color, lw=0.8, clip_on=False)


if __name__ == "__main__":
    out = make()
    print(out["caption"])
    print(out["shows"])
