"""S4.5.2: the $90 Gemini cartel as a chat strip. One lane per seller, six of the sellers' texts at the hour
they were written, each pinned down to the price panel below.

Run: shard2/A_lowanchor/..._L90_gemini_comms_gpt41miniB-seed0 (as S4.5.1). Price panel: each seller's posted
ask by hour (four thin lines, which overlap within one cent from hour 2) and the mean posted bid (unified.log).
Call-outs: quotes.py entries g90_kai_h1, g90_max_h2, g90_leo_h5, g90_leo_h12, g90_raj_h12, g90_kai_h13.
Output: supplement/figures/S45/S45_02_cartel90_chat.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import G90, QUOTES as Q

LANES = ["Kai", "Leo", "Max", "Raj"]          # top to bottom
# quote key, x of the box edge (hour), alignment, wrap width
BUBBLES = [("g90_kai_h1", 0.75, "left", 27), ("g90_kai_h13", 15.4, "right", 22),
           ("g90_leo_h5", 4.55, "left", 18), ("g90_leo_h12", 15.4, "right", 26),
           ("g90_max_h2", 1.75, "left", 34), ("g90_raj_h12", 15.4, "right", 30)]


def main():
    L.setup()
    rec = L.run(G90)
    c = style.COLOR["gemini"]
    bid = [sum(rec[h]["bids"].values()) / len(rec[h]["bids"]) for h in L.HOURS]

    fig = plt.figure(figsize=(style.SLOT_IN, 7.0))
    ax_c = L.chat_axes(fig, [0.115, 0.425, 0.865, 0.53], LANES, c)
    ax_p = fig.add_axes([0.115, 0.15, 0.865, 0.245], sharex=ax_c)
    n = len(LANES)

    asks = {s: L.ask_path(rec, f"Seller {s}") for s in LANES}
    style.ref_lines(ax_p)
    ax_p.plot(L.HOURS, bid, color=style.GRAY, lw=1.4, zorder=2)
    for s in LANES:
        ax_p.plot(L.HOURS, asks[s], color=c, lw=1.6, alpha=0.8, zorder=3)
    ax_p.text(2.25, 87.7, "mean bid", color=style.GRAY, fontsize=12, ha="left", va="center")
    ax_p.text(15.3, 90.6, "four asks", color=c, fontsize=12, ha="right", va="bottom")
    ax_p.set_ylim(86.4, 98.4)
    ax_p.set_yticks([88, 90, 92, 94, 96, 98])
    ax_p.set_ylabel("Price ($)")
    L.hour_axis(ax_p)

    for key, x, align, width in BUBBLES:
        q = Q[key]
        L.lane_bubble(ax_c, ax_p, q, n - 1 - LANES.index(q.speaker), asks[q.speaker][q.hour - 1], x, align,
                      width, c)

    ax_c.set_title("Gemini 3.8 Flash sellers, market opened at $90", pad=6)
    L.channel_key(fig, 0.03, color=c)
    L.save(fig, "S45_02_cartel90_chat.png")


if __name__ == "__main__":
    main()
