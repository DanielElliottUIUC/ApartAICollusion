"""S4.5.6: "The cartel held" below $90. Grok's hour-1 conditional promise and its hour-14 private note, each
pinned on the speaker's own ask line; the four asks start $14 apart and end at $87.99.

Run: box/frontier/..._grok47_comms_lunaB-seed0 (Grok 4.7 sellers, GPT-6 Luna buyers, default opening,
messaging on). Lines: each seller's posted ask by hour (unified.log). Call-outs: quotes.py entries k0_kai_h1,
k0_kai_h1_dm, k0_leo_h14. Output: supplement/figures/S45/S45_06_grok_held.png
"""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import s45lib as L
import style
from quotes import K0, QUOTES as Q

SELLERS = ["Kai", "Leo", "Max", "Raj"]


def main():
    L.setup()
    rec = L.run(K0)
    c = style.COLOR["grok"]
    dark = "#8E3F6E"                       # Grok pink, darkened for highlighted lines and text
    ask = {s: L.ask_path(rec, f"Seller {s}") for s in SELLERS}

    fig = plt.figure(figsize=(style.SLOT_IN, 5.7))
    ax = fig.add_axes([0.115, 0.185, 0.865, 0.735])
    style.ref_lines(ax)
    for s in SELLERS:
        hi = s in ("Kai", "Leo")
        ax.plot(L.HOURS, ask[s], color=dark if hi else style.tint(c, 0.35), lw=2.4 if hi else 1.6,
                ls="-" if s != "Leo" else (0, (5, 1.5)), zorder=4 if hi else 3)
    L.hour_axis(ax)
    ax.set_ylim(81.6, 99.2)
    ax.set_yticks([82, 86, 90, 94, 98])
    ax.set_ylabel("Price ($)")
    ax.set_title("Grok 4.7 sellers, default opening", pad=8)

    L.callout(ax, Q["k0_kai_h1"], (1, ask["Kai"][0]), (2.4, 92.5), 26, dark, rel=(0.0, 0.0))
    L.callout(ax, Q["k0_kai_h1_dm"], (1, ask["Kai"][0]), (2.4, 82.5), 30, dark, rel=(0.0, 1.0))
    L.callout(ax, Q["k0_leo_h14"], (14, ask["Leo"][13]), (15.4, 89.1), 25, dark, ha="right", rel=(0.8, 0.0),
              header_side="right")
    h0, p0 = L.settle_hour(rec)
    ax.text(15.4, 87.25, f"Hours {h0} to 15: all four asks ${p0:.2f}\nCriterion {L.verdict(K0)}",
            fontsize=12, ha="right", va="top")
    handles = [Line2D([], [], color=dark, lw=2.4), Line2D([], [], color=dark, lw=2.4, ls=(0, (5, 1.5))),
               Line2D([], [], color=style.tint(c, 0.35), lw=1.6)]
    ax.legend(handles, ["Kai", "Leo", "Max, Raj"], loc="lower right", frameon=False, handlelength=2.2,
              borderaxespad=0.3)
    L.channel_key(fig, 0.035, color=dark)
    L.save(fig, "S45_06_grok_held.png")


if __name__ == "__main__":
    main()
