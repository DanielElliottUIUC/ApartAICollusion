"""S4.5.9: the same talk at two openings. Gemini 3.8 Flash sellers, GPT-4.1-mini buyers, messaging on, opened at
$97.50 (left, seed 2) and at $90 (right, seed 0). In both markets the sellers tell each other the buyers are
under their control; the asks stay near where the market opened.

Runs: shard2/A_agycontrol/..._agy_gemini_comms_gpt41miniB-seed2 and
      shard2/A_lowanchor/..._L90_gemini_comms_gpt41miniB-seed0.
Lines: each seller's posted ask by hour (unified.log); each call-out is pinned on the speaker's own ask at the
hour of the text. Call-outs: quotes.py entries g2_mia_h9, g2_amir_h10, g90_leo_h9, g90_kai_h12.
Output: supplement/figures/S45/S45_09_gemini_two_openings.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import G2, G90, QUOTES as Q


def panel(ax, folder, title, c, boxes, verdict_xy):
    rec = L.run(folder)
    style.ref_lines(ax)
    for s in L.sellers(rec):
        ax.plot(L.HOURS, L.ask_path(rec, s), color=c, lw=1.6, alpha=0.75, zorder=3)
    for key, xy, width, ha, va, rel, below in boxes:
        q = Q[key]
        own = L.ask_path(rec, f"Seller {q.speaker}")[q.hour - 1]
        L.callout(ax, q, (q.hour, own), xy, width, c, ha=ha, va=va, rel=rel, header_below=below, header_side=ha)
    ax.set_title(title, pad=6)
    ax.text(*verdict_xy, L.verdict(folder), fontsize=12, ha="right", va="bottom")
    L.hour_axis(ax)
    ax.set_xticks([1, 5, 10, 15])
    return rec


def main():
    L.setup()
    c = style.COLOR["gemini"]
    fig = plt.figure(figsize=(style.SLOT_IN, 6.6))
    ax_l = fig.add_axes([0.115, 0.255, 0.405, 0.665])
    ax_r = fig.add_axes([0.575, 0.255, 0.405, 0.665], sharey=ax_l)
    ax_l.set_ylim(87.4, 99.6)
    ax_l.set_yticks([88, 90, 92, 94, 96, 98])
    ax_l.set_ylabel("Ask ($)")
    plt.setp(ax_r.get_yticklabels(), visible=False)
    rl = panel(ax_l, G2, "Opened at $97.50", c,
               [("g2_amir_h10", (15.3, 96.35), 22, "right", "bottom", (0.55, 0.0), False),
                ("g2_mia_h9", (1.0, 94.45), 25, "left", "top", (0.85, 1.0), True)], (15.3, 87.7))
    rr = panel(ax_r, G90, "Opened at $90", c,
               [("g90_leo_h9", (1.0, 90.9), 18, "left", "bottom", (0.75, 0.0), False),
                ("g90_kai_h12", (15.3, 95.6), 25, "right", "bottom", (0.92, 0.0), False)], (15.3, 87.7))
    end_l, end_r = L.mean_ask_path(rl)[-1], L.mean_ask_path(rr)[-1]
    fig.text(0.5, 0.105, f"Gemini 3.8 Flash sellers, GPT-4.1-mini buyers, messaging on.\nHour-15 mean ask: "
             f"${end_l:.2f} (left) and ${end_r:.2f} (right).",
             fontsize=12, ha="center", va="center")
    L.channel_key(fig, 0.03, channels=("public", "dm"), color=c)
    L.save(fig, "S45_09_gemini_two_openings.png")


if __name__ == "__main__":
    main()
