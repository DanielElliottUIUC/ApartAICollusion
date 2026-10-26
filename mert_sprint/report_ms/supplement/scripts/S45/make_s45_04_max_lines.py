"""S4.5.4: the double-dealer on the sellers' own ask lines. Max's public message and private plan of hour 14
are pinned on Max's hour-14 ask; Kai's private note of hour 15 is pinned on Kai's hour-15 ask.

Run: shard2/A_agycontrol/..._agy_gemini_comms_gpt41miniB-seed0 (as S4.5.3). Lines: each seller's posted ask
and the best posted bid by hour (unified.log). Call-outs: quotes.py entries g0_max_h14_pub,
g0_max_h14_plan, g0_kai_h15. Output: supplement/figures/S45/S45_04_max_lines.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import G0, QUOTES as Q


def main():
    L.setup()
    rec = L.run(G0)
    c = style.COLOR["gemini"]
    pale = style.tint(c, 0.55)
    ask = {s: L.ask_path(rec, f"Seller {s}") for s in ("Kai", "Leo", "Raj", "Max")}

    fig = plt.figure(figsize=(style.SLOT_IN, 6.3))
    ax = fig.add_axes([0.115, 0.17, 0.865, 0.75])
    style.ref_lines(ax)
    ax.plot(L.HOURS, L.best_bid_path(rec), color=style.GRAY, lw=1.4, zorder=2)
    for s in ("Kai", "Leo", "Raj"):
        ax.plot(L.HOURS, ask[s], color=pale, lw=1.8, zorder=3)
    ax.plot(L.HOURS, ask["Max"], color=c, lw=2.8, zorder=4)
    ax.text(1.0, 97.95, "Max", color=c, fontsize=12, ha="left", va="bottom", fontweight="bold")
    ax.text(14.0, ask["Kai"][13] + 0.45, f"Kai, Leo, Raj ${ask['Kai'][13]:.2f}", color=style.tint(c, 0.3),
            fontsize=12, ha="right", va="bottom")
    ax.text(3.0, 85.7, "best bid", color=style.GRAY, fontsize=12, ha="left", va="top")
    ax.set_ylim(77.6, 99.4)
    ax.set_yticks([80, 84, 88, 92, 96])
    ax.set_ylabel("Price ($)")
    L.hour_axis(ax)
    ax.set_title("Gemini 3.8 Flash sellers, default opening", pad=8)

    q = Q["g0_max_h14_pub"]
    L.callout(ax, q, (14, ask["Max"][13]), (2.4, 91.4), 24, c, rel=(1.0, 0.0),
              header_text=f"{q.header}\n(his own ask that hour: ${ask['Max'][13]:.2f})")
    L.callout(ax, Q["g0_max_h14_plan"], (14, ask["Max"][13]), (0.75, 79.4), 26, c, rel=(1.0, 0.8))
    L.callout(ax, Q["g0_kai_h15"], (15, ask["Kai"][14]), (15.4, 82.3), 28, c, ha="right", va="top",
              rel=(0.95, 1.0), header_side="right", header_below=True)
    L.channel_key(fig, 0.035, channels=("public", "note"), color=c)
    L.save(fig, "S45_04_max_lines.png")


if __name__ == "__main__":
    main()
