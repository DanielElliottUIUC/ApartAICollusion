"""S4.5.1: the $90 Gemini cartel, four messages pinned on the market's mean ask.

Run: shard2/A_lowanchor/..._L90_gemini_comms_gpt41miniB-seed0 (Gemini 3.8 Flash sellers, GPT-4.1-mini buyers,
opened at $90, messaging on). Lines: mean of the four posted asks and mean of the four posted bids by hour
(unified.log). Call-outs: quotes.py entries g90_kai_h1, g90_max_h2, g90_kai_h12, g90_kai_h13, pinned at the
hour the text was written. Output: supplement/figures/S45/S45_01_cartel90_pinned.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import G90, QUOTES as Q


def main():
    L.setup()
    rec = L.run(G90)
    ask, bid = L.mean_ask_path(rec), [sum(r["bids"].values()) / len(r["bids"]) for r in
                                      (rec[h] for h in L.HOURS)]
    c = style.COLOR["gemini"]

    fig = plt.figure(figsize=(style.SLOT_IN, 5.4))
    ax = fig.add_axes([0.115, 0.195, 0.865, 0.715])
    style.ref_lines(ax)
    ax.plot(L.HOURS, bid, color=style.GRAY, lw=1.4, zorder=2)
    ax.plot(L.HOURS, ask, color=c, lw=2.8, zorder=3)
    ax.text(2.25, 88.35, "mean bid", color=style.GRAY, fontsize=12, ha="left", va="center")
    ax.text(15.3, 90.45, "mean ask", color=c, fontsize=12, ha="right", va="bottom")
    L.hour_axis(ax)
    ax.set_ylim(85.6, 99.4)
    ax.set_yticks([86, 88, 90, 92, 94, 96, 98])
    ax.set_ylabel("Price ($)")
    ax.set_title("Gemini 3.8 Flash sellers, market opened at $90", pad=8)

    L.callout(ax, Q["g90_kai_h1"], (1, ask[0]), (0.75, 96.55), 27, c, rel=(0.03, 0.0))
    L.callout(ax, Q["g90_max_h2"], (2, ask[1]), (2.6, 92.0), 22, c, rel=(0.0, 0.0))
    L.callout(ax, Q["g90_kai_h13"], (13, ask[12]), (15.35, 96.35), 21, c, ha="right", rel=(0.62, 0.0),
              header_side="right")
    L.callout(ax, Q["g90_kai_h12"], (12, ask[11]), (15.35, 88.9), 26, c, ha="right", va="top",
              rel=(0.42, 1.0), header_side="right", header_below=True)
    ax.text(2.25, 86.85, f"Hour 15: mean ask ${ask[-1]:.2f}\nCriterion {L.verdict(G90)}", fontsize=12, ha="left",
            va="center", color="black")
    L.channel_key(fig, 0.04, color=c)
    L.save(fig, "S45_01_cartel90_pinned.png")


if __name__ == "__main__":
    main()
