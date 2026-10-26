"""S4.5.3: the double-dealer as two tracks. What Seller Max told the other sellers (public lane) and what he
wrote in his own notes (private lane), above every seller's posted ask. Hour 14 is shaded in all panels.

Run: shard2/A_agycontrol/..._agy_gemini_comms_gpt41miniB-seed0 (Gemini 3.8 Flash sellers, GPT-4.1-mini buyers,
default $97.50 opening, messaging on). Price panel: each seller's posted ask and the best posted bid by hour,
and every trade (unified.log). Call-outs: quotes.py entries g0_max_h1, g0_max_h14_pub, g0_max_h9,
g0_max_h14_plan. Output: supplement/figures/S45/S45_03_max_two_track.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import G0, QUOTES as Q

OTHERS = ["Kai", "Leo", "Raj"]


def main():
    L.setup()
    rec = L.run(G0)
    c = style.COLOR["gemini"]
    pale = style.tint(c, 0.55)
    max_ask = L.ask_path(rec, "Seller Max")

    fig = plt.figure(figsize=(style.SLOT_IN, 6.9))
    ax_c = L.chat_axes(fig, [0.115, 0.535, 0.865, 0.405], ["public", "private"], c, rotate=True)
    ax_p = fig.add_axes([0.115, 0.15, 0.865, 0.355], sharex=ax_c)
    ax_p.axvspan(13.55, 14.45, color=L.HOUR_BAND, zorder=0, lw=0)

    style.ref_lines(ax_p)
    ax_p.plot(L.HOURS, L.best_bid_path(rec), color=style.GRAY, lw=1.4, zorder=2)
    for s in OTHERS:
        ax_p.plot(L.HOURS, L.ask_path(rec, f"Seller {s}"), color=pale, lw=1.8, zorder=3)
    ax_p.plot(L.HOURS, max_ask, color=c, lw=2.8, zorder=4)
    tr = L.trades(rec)
    ax_p.plot([t[0] for t in tr], [t[2] for t in tr], ls="none", marker="D", ms=5, mfc="black", mec="black",
              zorder=5)
    ax_p.text(2.0, 98.15, "Kai, Leo, Raj", color=pale, fontsize=12, ha="left", va="bottom")
    ax_p.text(7.0, 97.0, "Max", color=c, fontsize=12, ha="center", va="top", fontweight="bold")
    ax_p.text(5.0, 86.4, "best bid", color=style.GRAY, fontsize=12, ha="left", va="top")
    ax_p.text(15.45, 87.4, "trades", color="black", fontsize=12, ha="right", va="top")
    ax_p.annotate(f"${max_ask[13]:.2f}", xy=(14, max_ask[13]), xytext=(12.9, 85.6), ha="right", va="center",
                  fontsize=12, color=c, fontweight="bold",
                  arrowprops=dict(arrowstyle="-", color=c, lw=1.0, shrinkA=1, shrinkB=4))
    ax_p.set_ylim(82.6, 99.6)
    ax_p.set_yticks([84, 88, 92, 96])
    ax_p.set_ylabel("Price ($)")
    L.hour_axis(ax_p)

    L.lane_bubble(ax_c, ax_p, Q["g0_max_h1"], 1, max_ask[0], 0.75, "left", 34, c)
    L.lane_bubble(ax_c, ax_p, Q["g0_max_h14_pub"], 1, max_ask[13], 15.4, "right", 24, c)
    L.lane_bubble(ax_c, ax_p, Q["g0_max_h9"], 0, max_ask[8], 9.35, "right", 26, c)
    L.lane_bubble(ax_c, ax_p, Q["g0_max_h14_plan"], 0, max_ask[13], 15.4, "right", 25, c)

    ax_c.set_title("Seller Max, Gemini 3.8 Flash, default opening", pad=6)
    L.channel_key(fig, 0.03, channels=("public", "note"), color=c)
    L.save(fig, "S45_03_max_two_track.png")


if __name__ == "__main__":
    main()
