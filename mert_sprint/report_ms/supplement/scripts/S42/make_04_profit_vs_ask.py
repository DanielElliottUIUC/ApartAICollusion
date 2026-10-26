"""Figure S42.4: profit per market against the last-third ask index (a) and against trades (b), 50 markets.

Profit and trades as in Figure S42.3 (LLM sellers, all 15 hours, market_by_hour.csv). Ask index: last third,
LLM sellers only (market_by_run.csv ask_index). Circles: arms without the warning; diamonds: arms with it.
Filled: the market meets the joint criterion. Markets with an ask index above 0.5 and profit under $100 get a black ring.
Output: supplement/figures/S42/S42_04_profit_vs_ask.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import s42lib as L
from s42lib import style

FILE = "S42_04_profit_vs_ask.png"
FIG_H = 3.9


def marker(ax, x, y, warn, passed):
    ax.plot([x], [y], ls="none", marker=("D" if warn else "o"), ms=(6 if warn else 7), mew=1.2, mec=L.BLUE,
            mfc=(L.BLUE if passed else "white"), zorder=3)


def make():
    style.setup()
    m = L.markets()
    W = style.SLOT_IN
    fig = plt.figure(figsize=(W, FIG_H))
    y0, y1 = 0.80, FIG_H - 0.78
    ax_a = fig.add_axes([0.98 / W, y0 / FIG_H, 2.45 / W, (y1 - y0) / FIG_H])
    ax_b = fig.add_axes([3.85 / W, y0 / FIG_H, 2.45 / W, (y1 - y0) / FIG_H], sharey=ax_a)
    for r in style.REF_LINES:
        ax_a.axvline(r["index"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    for _, r in m.iterrows():
        marker(ax_a, r["ask_index"], r["profit"], r["warn"], r["passed"])
        marker(ax_b, r["trades"], r["profit"], r["warn"], r["passed"])
    named = m[(m["ask_index"] > 0.5) & (m["profit"] < 100)].sort_values("ask_index")
    for _, r in named.iterrows():
        ax_a.plot([r["ask_index"]], [r["profit"]], ls="none", marker="o", ms=14, mew=1.0, mec="black",
                  mfc="none", zorder=4)
    ax_a.set_xlim(-0.03, 0.8)
    ax_a.set_xticks([0, 0.25, 0.5, 0.75], ["0", "0.25", "0.5", "0.75"])
    ax_a.set_xlabel("Ask index, hours 11 to 15")
    ax_a.set_ylim(0, 950)
    ax_a.set_yticks([0, 400, 800], ["$0", "$400", "$800"])
    ax_a.set_ylabel("Profit per market")
    ax_b.set_xlim(0, 58)
    ax_b.set_xticks([0, 25, 50])
    ax_b.set_xlabel("Trades per market")
    plt.setp(ax_b.get_yticklabels(), visible=False)
    r_a, r_b = L.pearson(m["ask_index"], m["profit"]), L.pearson(m["trades"], m["profit"])
    ax_a.set_title(f"Price, r = {r_a:.2f}", pad=8)
    ax_b.set_title(f"Volume, r = {r_b:.2f}", pad=8)
    for ax, letter in ((ax_a, "a"), (ax_b, "b")):
        x_in = ax.get_position().x0 * W
        fig.text((x_in - 0.75 if letter == "a" else x_in - 0.30) / W, (y1 + 0.10) / FIG_H, letter,
                 fontsize=16, fontweight="bold", ha="left", va="bottom")
    handles = [Line2D([], [], ls="none", marker="o", ms=7, mew=1.2, mec=L.BLUE, mfc="white"),
               Line2D([], [], ls="none", marker="D", ms=6, mew=1.2, mec=L.BLUE, mfc="white"),
               Line2D([], [], ls="none", marker="o", ms=7, mew=1.2, mec=L.BLUE, mfc=L.BLUE)]
    fig.legend(handles, ["No warning", "Warning", "Filled: meets the criterion"], loc="upper center",
               ncol=3,
               frameon=False, bbox_to_anchor=(0.5, 1.0), handletextpad=0.3, columnspacing=1.2)
    L.save(fig, FILE)
    plt.close(fig)
    return {"r_a": r_a, "r_b": r_b, "named": named, "m": m}


def entry():
    n = make()
    m, named = n["m"], n["named"]
    hi = m[m["ask_index"] > 0.5]
    lo = m[m["ask_index"] <= 0.5]
    names = "; ".join(f"{r['arm']} seed {r['seed']}, index {r['ask_index']:.2f}, ${r['profit']:.0f} from "
                      f"{r['trades']} trades" for _, r in named.iterrows())
    return {
        "title": "Higher asks did not earn more; trades did",
        "file": FILE,
        "caption": (
            "Profit of the four Gemini 3.8 Flash sellers per market against (a) the last-third ask index and "
            "(b) the number of their trades, for all 50 markets of D.E.'s ten arms. Circles: arms without the "
            "warning. Diamonds: arms with it. Filled markers meet the joint criterion. In (a), vertical lines "
            "mark index 0 ($90, dashed), 0.5 ($95, dotted) and 0.75 ($97.50, thin). Black rings mark the markets "
            "with an ask index above 0.5 that earned under $100. r: Pearson correlation over the 50 markets."),
        "shows": (
            f"Across markets, profit is unrelated to the ask index (r = {n['r_a']:.2f}) and almost "
            f"proportional to volume (r = {n['r_b']:.2f}). Markets above index 0.5 earned ${hi['profit'].mean():.0f} "
            f"on average, those at or below it ${lo['profit'].mean():.0f}. The ringed markets held high asks "
            f"and barely traded ({names}). An ask-based collusion index therefore says little about what the "
            f"sellers earned in this market, which is why the joint criterion also requires trades."),
        "source": f"`{L.SRC}/market_by_hour.csv`, `{L.SRC}/market_by_run.csv`. "
                  f"Script: `supplement/scripts/S42/make_04_profit_vs_ask.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
