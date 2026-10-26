"""S4.5.12: a quote wall. Six markets on one price scale, each with one seller text pinned on the market's mean
ask at the hour it was written, and the market's verdict on the joint criterion.

Runs and call-outs (quotes.py entries):
  a  Gemini 3.8 Flash, opened at $90, messaging on, seed 0          g90_kai_h12
  b  Gemini 3.8 Flash, default opening, messaging on, seed 2       g2_mia_h9
  c  Grok 4.7, GPT-6 Luna buyers, seed 0                           k0_leo_h14
  d  Grok 4.7, Claude Haiku 5.5 buyers, seed 1                     k1_tara_h10
  e  GPT-5.6 Sol, no messaging, Claude Haiku 5.5 buyers, seed 0    s0_kai_h11
  f  GPT-6 Luna, Claude Haiku 5.5 buyers, seed 2                   lu2_yara_h2
Lines: mean of the posted asks by hour (unified.log).
Output: supplement/figures/S45/S45_12_quote_wall.png
"""
import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import G2, G90, K0, K1, LU2, S0, QUOTES as Q

DARK = {"gemini": style.COLOR["gemini"], "grok": "#8E3F6E", "sol": "#9A4300", "luna": "#00664B"}
# letter, title, run, model, quote key, box anchor (hour, $), box va, wrap, leader start, header below
CELLS = [
    ("a", "Gemini at $90", G90, "gemini", "g90_kai_h12", (1.0, 92.2), "bottom", 26, (0.84, 0.0), False),
    ("b", "Gemini at $97.50", G2, "gemini", "g2_mia_h9", (1.0, 93.4), "top", 26, (0.6, 1.0), True),
    ("c", "Grok, seed 0", K0, "grok", "k0_leo_h14", (3.2, 90.6), "bottom", 23, (0.86, 0.0), False),
    ("d", "Grok, seed 1", K1, "grok", "k1_tara_h10", (1.0, 89.6), "bottom", 22, (0.72, 0.0), False),
    ("e", "Sol, no channel", S0, "sol", "s0_kai_h11", (1.0, 95.5), "top", 25, (0.75, 1.0), True),
    ("f", "Luna, seed 2", LU2, "luna", "lu2_yara_h2", (1.6, 88.6), "bottom", 26, (0.0, 0.0), False),
]


def main():
    L.setup()
    fig = plt.figure(figsize=(style.SLOT_IN, 8.4))
    left, right, top, bottom, wgap, hgap = 0.115, 0.98, 0.955, 0.13, 0.055, 0.075
    w = (right - left - wgap) / 2
    h = (top - bottom - 2 * hgap) / 3
    axes = []
    for i, (letter, title, folder, model, key, xy, va, width, rel, below) in enumerate(CELLS):
        row, col = divmod(i, 2)
        ax = fig.add_axes([left + col * (w + wgap), top - (row + 1) * h - row * hgap, w, h],
                          sharey=axes[0] if axes else None)
        axes.append(ax)
        rec = L.run(folder)
        m = L.mean_ask_path(rec)
        q = Q[key]
        style.ref_lines(ax)
        ax.plot(L.HOURS, m, color=style.COLOR[model], lw=2.4, zorder=3)
        L.callout(ax, q, (q.hour, m[q.hour - 1]), xy, width, DARK[model], va=va, rel=rel, header_below=below)
        ax.text(15.3, 81.2, L.verdict(folder), fontsize=12, ha="right", va="bottom")
        ax.set_title(f"{letter}   {title}", loc="left", pad=5)
        L.hour_axis(ax, label=row == 2)
        ax.set_xticks([1, 5, 10, 15])
        if col == 1:
            plt.setp(ax.get_yticklabels(), visible=False)
    axes[0].set_ylim(80.6, 99.6)
    axes[0].set_yticks([82, 86, 90, 94, 98])
    fig.text(0.018, (top + bottom) / 2, "Mean ask ($)", rotation=90, fontsize=14, ha="left", va="center")
    L.channel_key(fig, 0.025, color="#444444")
    L.save(fig, "S45_12_quote_wall.png")


if __name__ == "__main__":
    main()
