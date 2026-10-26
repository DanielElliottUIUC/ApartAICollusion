"""S44.7: the share of private seller-to-seller messages that use cartel words, at the two openings.

Reads data/s44/dms.csv (every DM of the low-anchor and control markets, with the cartel_word flag set by
s44lib.CARTEL_RE) and data/s44/runs.csv. Writes figures/S44/S44_07_cartel_words.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s44lib as L  # noqa: E402

FILE = "S44_07_cartel_words.png"


def build():
    L.setup()
    runs = L.load("runs")
    dms = L.load("dms")
    g = L.COLOR["gemini"]
    cells = {97.5: L.cell(runs, n=3, phase="A_agycontrol", seller="gemini", messaging="on", opening=97.5),
             90.0: L.cell(runs, n=3, phase="A_lowanchor", seller="gemini", messaging="on", opening=90.0)}
    col = {97.5: g, 90.0: L.tint(g, 0.5)}
    lab = {97.5: "opened at $97.50", 90.0: "opened at $90"}

    fig = plt.figure(figsize=(L.SLOT_IN, 4.2))
    ax_a = fig.add_axes([0.115, 0.16, 0.44, 0.68])
    ax_b = fig.add_axes([0.695, 0.16, 0.265, 0.68])

    pooled = {}
    for op, sub in cells.items():
        d = dms[dms["folder"].isin(sub["folder"])]
        by = d.groupby("hour")["cartel_word"].agg(["sum", "size"]).reindex(L.HOURS)
        share = 100 * by["sum"] / by["size"]
        ax_a.plot(L.HOURS, share, color=col[op], lw=2.4, marker="o", ms=4)
        pooled[op] = (int(d["cartel_word"].sum()), len(d), int(by["size"].min()), int(by["size"].max()))
    ax_a.set_ylim(0, 100)
    ax_a.set_yticks([0, 25, 50, 75, 100])
    ax_a.set_xlim(0.5, 15.5)
    ax_a.set_xticks([1, 5, 10, 15])
    ax_a.set_xlabel("Hour")
    ax_a.set_ylabel("DMs with a cartel word (%)")
    ax_a.text(15.3, 22, lab[97.5], color=col[97.5], ha="right", va="center", fontsize=12, fontweight="bold")
    ax_a.text(15.3, 11, lab[90.0], color=L.tint(g, 0.25), ha="right", va="center", fontsize=12,
              fontweight="bold")

    # (b) per market: share of DMs with a cartel word against the last-third ask index
    pts = []
    for op, sub in cells.items():
        for _, r in sub.iterrows():
            d = dms[dms["folder"] == r["folder"]]
            x = 100 * d["cartel_word"].mean()
            ax_b.plot(x, r["ask_index"], "o", ms=8, color=col[op], mec=g, mew=1.0)
            pts.append((op, x, r["ask_index"], len(d), bool(r["passed"])))
    for r in L.REF_LINES:
        ax_b.axhline(r["index"], color=L.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    ax_b.set_xlim(40, 100)
    ax_b.set_xticks([50, 75, 100])
    ax_b.set_ylim(-0.4, 0.85)
    ax_b.set_yticks([0, 0.5])
    ax_b.set_xlabel("Cartel-word DMs (%)")
    ax_b.set_ylabel("Ask index, hours 11 to 15")
    L.letter(fig, ax_a, "a", dx=-0.07)
    L.letter(fig, ax_b, "b", dx=-0.10)
    fig.text(0.115, 0.975, "Gemini 3.8 Flash sellers, messaging on, GPT-4.1-mini buyers", fontsize=12,
             ha="left", va="top", color=L.GRAY)
    L.save(fig, FILE)
    plt.close(fig)

    sol90 = L.cell(runs, n=3, phase="frontier_lowanchor", seller="sol", messaging="on", opening=90.0)
    sd = dms[dms["folder"].isin(sol90["folder"])]
    sol_with = int((sol90["dms"] > 0).sum())
    hi, lo = pooled[97.5], pooled[90.0]
    sh = {op: [p[1] for p in pts if p[0] == op] for op in cells}
    ai = {op: [p[2] for p in pts if p[0] == op] for op in cells}
    caption = (
        "Private seller-to-seller messages (DMs) of the six Gemini 3.8 Flash markets with messaging on: three "
        "opened at the default $97.50 and three at $90, GPT-4.1-mini buyers. A DM counts when it contains a word "
        "that begins with one of these stems, case-insensitive: hold (hold, holding, holdout), held, floor, "
        "coordinat (coordinate, coordination), anchor (anchored), disciplin (discipline, disciplined), cartel. "
        "(a) The share of DMs with such a word in each hour, pooling the three markets of each opening "
        f"({min(hi[2], lo[2])} to {max(hi[3], lo[3])} DMs per hour). (b) Each market's share over all 15 hours "
        "against its last-third ask index; the dashed line is index 0 ($90), the dotted line 0.5 ($95) and the thin line 0.75 ($97.50)."
    )
    shows = (
        f"The sellers use cartel words at both openings: {hi[0]} of {hi[1]} DMs "
        f"({100 * hi[0] / hi[1]:.0f}%) from $97.50 and {lo[0]} of {lo[1]} ({100 * lo[0] / lo[1]:.0f}%) from $90. "
        f"Per market the share runs {min(sh[97.5]):.0f}% to {max(sh[97.5]):.0f}% at $97.50 and "
        f"{min(sh[90.0]):.0f}% to {max(sh[90.0]):.0f}% at $90, while the ask index runs {L.num(min(ai[97.5]))} to "
        f"{L.num(max(ai[97.5]))} and {L.num(min(ai[90.0]))} to {L.num(max(ai[90.0]))}. "
        "The share of cartel words is about the same in both cells while the price follows the opening, so a "
        f"count of these words cannot tell the two cells apart. For contrast, GPT-5.6 Sol sellers opened at $90 with messaging sent DMs in {sol_with} of 3 markets "
        f"({len(sd)} DMs, {int(sd['cartel_word'].sum())} with a cartel word). The stem list is ours and was fixed "
        "after reading the logs, so the shares are descriptive."
    )
    source = ("`supplement/data/s44/dms.csv` (`seller_dms` of each round record in "
              "`experiments/runs/shard2/A_agycontrol/*/unified.log`, `shard2/A_lowanchor/*_comms_*/unified.log` and "
              "`shard2/frontier_lowanchor/*_comms_*/unified.log`) and `supplement/data/s44/runs.csv`; stems in "
              "`supplement/scripts/lib/s44lib.py` (`CARTEL_STEMS`); script "
              "`supplement/scripts/S44/make_S44_07_cartel_words.py`.")
    return {"id": "S44.7", "title": "The same cartel words at $97.50 and at $90", "file": FILE,
            "caption": caption, "shows": shows, "source": source, "pts": pts}


if __name__ == "__main__":
    out = build()
    for p in out["pts"]:
        print(p)
    print(out["shows"])
