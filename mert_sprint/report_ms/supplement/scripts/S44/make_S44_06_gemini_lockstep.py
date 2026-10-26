"""S44.6: how tightly the four Gemini 3.8 Flash sellers hold their asks, with and without messaging.

Reads data/s44/seller_asks.csv (each seller's posted ask per hour, from unified.log) and data/s44/runs.csv.
Gemini sellers, GPT-4.1-mini buyers: A_lowanchor (opened at $90, messaging on and off) and A_agycontrol
(opened at $97.50, messaging on). Writes figures/S44/S44_06_gemini_lockstep.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s44lib as L  # noqa: E402

FILE = "S44_06_gemini_lockstep.png"
CELLS = [("A_lowanchor", "on", 90.0, "On, $90"), ("A_lowanchor", "off", 90.0, "Off, $90"),
         ("A_agycontrol", "on", 97.5, "On, $97.50")]
CAP = 1.6       # top of the range axis ($); larger ranges are drawn at the cap and labelled


def build():
    L.setup()
    runs = L.load("runs")
    sa = L.load("seller_asks")
    c = L.COLOR["gemini"]
    shades = [L.tint(c, a) for a in (0.0, 0.3, 0.5, 0.65)]

    fig = plt.figure(figsize=(L.SLOT_IN, 6.6))
    gs_top = fig.add_gridspec(1, 2, left=0.125, right=0.975, top=0.86, bottom=0.555, wspace=0.10)
    gs_bot = fig.add_gridspec(1, 3, left=0.125, right=0.975, top=0.39, bottom=0.085, wspace=0.10)
    ax_on, ax_off = fig.add_subplot(gs_top[0]), fig.add_subplot(gs_top[1])
    ax_off.sharey(ax_on)

    # (a) the four sellers' asks, seed 0, opened at $90, messaging on and off
    for ax, msg, ttl in ((ax_on, "on", "Messaging on"), (ax_off, "off", "Messaging off")):
        f = L.cell(runs, n=1, phase="A_lowanchor", seller="gemini", messaging=msg, opening=90.0, seed=0)
        folder = f["folder"].iloc[0]
        s = sa[sa["folder"] == folder]
        L.ref_lines(ax, which=(90.0,))
        for shade, (name, g) in zip(shades, s.groupby("seller")):
            g = g.sort_values("hour")
            ax.plot(g["hour"], g["ask"], color=shade, lw=1.8, marker="o", ms=3)
        ax.set_title(ttl, fontsize=16, pad=6)
        ax.set_xlim(0.5, 15.5)
        ax.set_xticks([1, 5, 10, 15])
        ax.set_xlabel("Hour")
    ax_on.set_ylim(86.4, 91.0)
    ax_on.set_yticks([87, 88, 89, 90])
    ax_on.set_ylabel("Seller ask ($)")
    plt.setp(ax_off.get_yticklabels(), visible=False)

    # (b) range of the four asks by hour, every Gemini market of the cell
    stats = {}
    axes_b = [fig.add_subplot(gs_bot[i]) for i in range(3)]
    for ax, (phase, msg, opening, ttl) in zip(axes_b, CELLS):
        sub = L.cell(runs, n=3, phase=phase, seller="gemini", messaging=msg, opening=opening)
        allr = []
        for _, r in sub.iterrows():
            s = sa[sa["folder"] == r["folder"]]
            rng = s.groupby("hour")["ask"].agg(lambda a: a.max() - a.min()).reindex(L.HOURS).to_numpy()
            allr.append(rng)
            shown = np.minimum(rng, CAP)
            ax.plot(L.HOURS, shown, color=c, lw=1.4, alpha=0.85, clip_on=False)
            for h, v in zip(L.HOURS, rng):
                if v > CAP:
                    ax.plot(h, CAP, "^", ms=7, color=c, clip_on=False)
                    ax.text(h - 0.4, CAP - 0.05, f"{L.money(v)}\nhour {h}", ha="right", va="top", fontsize=12)
        allr = np.array(allr)
        late = allr[:, 1:]                      # hours 2 to 15
        stats[ttl] = (int((late <= 0.01 + 1e-9).sum()), late.size, float(np.median(late)),
                      float(allr[:, 1:8].max()), float(allr[:, 9:].max()))
        ax.set_title(ttl, fontsize=16, pad=6)
        ax.set_ylim(0, CAP)
        ax.set_xlim(0.5, 15.5)
        ax.set_xticks([1, 8, 15])
        ax.set_xlabel("Hour")
        if ax is not axes_b[0]:
            plt.setp(ax.get_yticklabels(), visible=False)
    axes_b[0].set_ylabel("Ask range ($)")
    axes_b[0].set_yticks([0, 0.5, 1.0, 1.5])
    for ax in axes_b[1:]:
        ax.set_yticks([0, 0.5, 1.0, 1.5])
    L.letter(fig, ax_on, "a", dx=-0.06)
    L.letter(fig, axes_b[0], "b", dx=-0.06)
    fig.text(0.125, 0.975, "Gemini 3.8 Flash sellers, opened at $90, seed 0", fontsize=12, ha="left", va="top",
             color=L.GRAY)
    L.save(fig, FILE)
    plt.close(fig)

    on, off, hi = stats["On, $90"], stats["Off, $90"], stats["On, $97.50"]
    g90 = runs[(runs["phase"] == "A_lowanchor")]["folder"]
    top90 = sa[sa["folder"].isin(g90) & (sa["hour"] >= 10)]["ask"].max()
    caption = (
        "Gemini 3.8 Flash sellers with GPT-4.1-mini buyers. (a) Each of the four sellers' posted asks by hour in "
        "seed 0 opened at $90, with messaging on (left) and off (right). Each seller has its own shade. The dashed line is "
        "$90. (b) The range of the four asks (highest minus lowest posted ask) in each hour, one line per seed, "
        "for the three Gemini cells: messaging on from $90, messaging off from $90, and messaging on from the "
        f"default $97.50. Ranges above ${CAP:.2f} are drawn at the top edge and labelled."
    )
    shows = (
        f"Opened at $90 with messaging, the four asks sit within one cent of each other in {on[0]} of {on[1]} market-hours from "
        f"hour 2 to hour 15 (median range {L.money(on[2], 3)}). Without messaging the asks spread by up to "
        f"{L.money(off[3])} in hours 2 to 8 and narrow to at most {L.money(off[4])} from hour 10 "
        f"({off[0]} of {off[1]} market-hours within one cent). "
        "Talk makes the lockstep immediate, but it does not lift it. No Gemini seller opened at $90 posts an ask "
        f"above {L.money(top90)} from hour 10 on. "
        f"From $97.50 the messaging markets stay within one cent in {hi[0]} of {hi[1]} market-hours, and in hour 14 "
        f"one seller undercuts the others by {L.money(hi[4])} (Figure S44.8). Each cell has three seeds, so this "
        "describes these runs only."
    )
    source = ("`supplement/data/s44/seller_asks.csv` (`seller_asks` of each round record in "
              "`experiments/runs/shard2/A_lowanchor/*/unified.log` and `shard2/A_agycontrol/*/unified.log`); "
              "script `supplement/scripts/S44/make_S44_06_gemini_lockstep.py`.")
    return {"id": "S44.6", "title": "Gemini sellers move in lockstep at $90 when they can talk", "file": FILE,
            "caption": caption, "shows": shows, "source": source, "stats": stats}


if __name__ == "__main__":
    out = build()
    print(out["stats"])
    print(out["shows"])
