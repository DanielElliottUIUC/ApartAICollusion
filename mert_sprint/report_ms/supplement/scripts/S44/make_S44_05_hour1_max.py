"""S44.5: the first hour is the market's highest mean ask almost everywhere.

Reads data/s44/runs.csv (81 markets: 36 frontier, 6 Sol with GPT-4.1-mini buyers, 9 Claude Haiku 5.5 seller markets,
15 low-anchor, 3 Gemini control, 12 pre-specified). Writes figures/S44/S44_05_hour1_max.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s44lib as L  # noqa: E402

FILE = "S44_05_hour1_max.png"
ORDER = ["sol", "luna", "grok", "gemini", "haiku"]


def build():
    L.setup()
    runs = L.load("runs")
    n = len(runs)
    fig = plt.figure(figsize=(L.SLOT_IN, 4.3))
    ax_a = fig.add_axes([0.11, 0.155, 0.33, 0.66])
    ax_b = fig.add_axes([0.60, 0.155, 0.375, 0.375 * 6.5 / 4.3])

    # (a) first hour that holds the market's highest hourly mean ask, stacked by seller model
    bottom = np.zeros(15)
    for g in ORDER:
        sub = runs[runs["seller"] == g]
        cnt = np.array([(sub["max_hour"] == h).sum() for h in L.HOURS])
        ax_a.bar(L.HOURS, cnt, bottom=bottom, color=L.COLOR[g], width=0.8, edgecolor="white", lw=0.4)
        bottom += cnt
    h1 = int((runs["max_hour"] == 1).sum())
    ax_a.text(1.6, h1 - 2, f"{h1} of {n} markets", ha="left", va="top", fontsize=12)
    exc = runs[runs["max_hour"] != 1]
    for _, r in exc.iterrows():
        ax_a.annotate(f"{L.SHORT[r['seller']]}, hour {int(r['max_hour'])}", xy=(r["max_hour"], 1.5),
                      xytext=(r["max_hour"] + 0.6, 16), ha="center", va="bottom", fontsize=12,
                      arrowprops=dict(arrowstyle="-", color="black", lw=0.8))
    ax_a.set_xlim(0.3, 15.7)
    ax_a.set_xticks([1, 5, 10, 15])
    ax_a.set_ylim(0, n + 4)
    ax_a.set_xlabel("Hour of highest mean ask")
    ax_a.set_ylabel("Markets")

    # (b) hour-1 mean ask against mean ask over hours 11 to 15
    ax_b.plot([80, 100], [80, 100], color=L.GRAY, lw=0.8, zorder=0.5)
    for g in ORDER:
        sub = runs[runs["seller"] == g]
        for opening, filled in ((97.5, True), (90.0, False)):
            s = sub[sub["opening"] == opening]
            ax_b.plot(s["ask_h1"], s["late_ask"], "o", ms=5.5, mec=L.COLOR[g], mew=1.1,
                      mfc=L.COLOR[g] if filled else "white", ls="none", alpha=0.9)
    ax_b.set_xlim(81, 99)
    ax_b.set_ylim(81, 99)
    ax_b.set_xticks([85, 90, 95])
    ax_b.set_yticks([85, 90, 95])
    ax_b.set_xlabel("Hour-1 mean ask ($)")
    ax_b.set_ylabel("Hours 11 to 15 ($)")
    ax_b.text(85.0, 86.0, "equal", ha="left", va="bottom", fontsize=12, color=L.GRAY, rotation=45,
              rotation_mode="anchor")
    above = int((runs["late_ask"] > runs["ask_h1"]).sum())

    # key: one entry per seller model, then the open/filled convention
    ky = 0.975
    x = 0.11
    for g in ORDER:
        fig.text(x, ky, L.SHORT[g], color=L.COLOR[g], fontsize=12, fontweight="bold", ha="left", va="top")
        x += 0.035 + 0.0135 * len(L.SHORT[g])
    fig.text(0.975, ky - 0.055, "filled: opened at $97.50, hollow: at $90", fontsize=12, ha="right", va="top")
    L.letter(fig, ax_a, "a", dx=-0.06)
    fig.text(ax_b.get_position().x0 - 0.09, ax_a.get_position().y1 + 0.012, "b", fontsize=16,
             fontweight="bold", ha="right", va="bottom")
    L.save(fig, FILE)
    plt.close(fig)

    fh = runs[(runs["phase"].isin(["frontier", "A", "B"]))]
    fh1 = int((fh["max_hour"] == 1).sum())
    sol = runs[runs["seller"] == "sol"]
    r = exc.iloc[0]
    drop = (runs["ask_h1"] - runs["late_ask"])
    caption = (
        f"All {n} of our double-auction markets in this section: the 36 frontier markets, 6 GPT-5.6 Sol markets "
        "with GPT-4.1-mini buyers, 9 Claude Haiku 5.5 seller markets, 15 low-anchor markets, 3 Gemini control "
        "markets and the 12 pre-specified markets. (a) The first hour in which the market's mean seller ask "
        "reaches its 15-hour maximum, stacked by seller model. (b) Each market's hour-1 mean ask against its mean "
        "ask over hours 11 to 15 (the window of the joint criterion); filled markers opened at $97.50, hollow at "
        "$90. The grey diagonal marks equal values, so points below it ended lower than they started."
    )
    shows = (
        f"In {h1} of {n} markets the highest mean ask is the hour-1 ask ({fh1} of {len(fh)} frontier and Haiku-seller "
        f"markets, and all {len(sol)} Sol markets). The one exception is a GPT-6 Luna market with messaging and "
        f"Luna buyers (seed {int(r['seed'])}), whose hour-{int(r['max_hour'])} mean ask exceeds hour 1 by "
        f"{L.money(r[f'ask_h{int(r.max_hour)}'] - r['ask_h1'])}. "
        f"In (b), {n - above} of {n} markets sit on or below the diagonal; the median fall from hour 1 to the "
        f"last third is {L.money(float(np.median(drop)))}. "
        "Apart from that market, no mean ask ever rose above its hour-1 value, so a pass reflects how much of the "
        "first-hour price was kept. "
        "The hour-1 ask is the sellers' first own choice after seeing the seeded book, not the seeded book itself."
    )
    source = ("`supplement/data/s44/runs.csv` (`avg_seller_asks_by_round` of every run folder under "
              "`experiments/runs/{box,shard2}/frontier/`, `shard2/frontier_b41/`, `shard2/frontier_lowanchor/`, "
              "`shard2/A_lowanchor/`, `shard2/A_agycontrol/`, `shard2/prereg_anchor/`, and the Haiku-seller folders "
              "of `shard2/A/`, `shard3/A/`, `shard2/B/`, `shard3/B/`); script "
              "`supplement/scripts/S44/make_S44_05_hour1_max.py`.")
    return {"id": "S44.5", "title": "Hour 1 is the high point of almost every market", "file": FILE,
            "caption": caption, "shows": shows, "source": source}


if __name__ == "__main__":
    print(build()["shows"])
