"""S4.5.11: D.E.'s double-dealer. Seller Leo's private reasoning in D.E.'s arm D, seed 0, shown on that
market's path. Daniel's logs, quoted from his report: his raw transcripts are not in his repository, so the quote
is checked against his REPORT.md and carries no hour.

Data: ApartAICollusion origin/main:report/data/dg/market_by_hour.csv, run 20261025_003014_D-seed0 (git show,
read only): avg_ask (mean ask of the four LLM sellers), avg_trade_price, offer_hour. Quote: quotes.DANIEL_LEO,
checked to be in his REPORT.md (section 4.2) on origin/main. The two dashed lines are the two prices the quote
names ($96.00 and $95.65), not data.
Output: supplement/figures/S45/S45_11_daniel_leo.png
"""
from types import SimpleNamespace

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import s45lib as L
import style
from quotes import DANIEL_LEO, DANIEL_RUN, daniel_report_source


def main():
    L.setup()
    c = style.COLOR["gemini"]
    commit, line = daniel_report_source()
    print(f"Daniel's quote: REPORT.md line {line} at origin/main {commit}")
    d = L.daniel_market(DANIEL_RUN)
    offer = int(d["offer_hour"].iloc[0])
    hours, ask, trade = list(d["hour"]), list(d["avg_ask"]), list(d["avg_trade_price"])

    fig = plt.figure(figsize=(style.SLOT_IN, 5.6))
    ax = fig.add_axes([0.115, 0.19, 0.865, 0.725])
    style.ref_lines(ax)
    ax.plot(hours, ask, color=c, lw=2.8, zorder=4)
    ax.plot(hours, trade, ls="none", marker="D", ms=5, mfc=style.GRAY, mec=style.GRAY, zorder=5)
    ax.plot([offer, offer], [95.15, 98.1], color=style.GRAY, lw=1.0, ls=(0, (4, 3)), zorder=1)
    named = style.tint(c, 0.25)
    for price, label in ((96.00, "Mia's $96.00"), (95.65, "Leo's $95.65")):
        ax.plot([offer + 0.5, 15.5], [price, price], color=named, lw=1.3, ls=(0, (6, 2)), zorder=2)
        ax.text(15.4, price + 0.04, label, color=named, fontsize=12, ha="right", va="bottom")
    ax.text(offer + 0.12, 97.95, f"hour {offer}: seat 5 offers to hold asks at $96", fontsize=12, ha="left",
            va="top", color=style.GRAY)
    L.hour_axis(ax)
    ax.set_ylim(93.6, 98.1)
    ax.set_yticks([94, 95, 96, 97, 98])
    ax.set_ylabel("Price ($)")
    ax.set_title("D.E.'s arm D, seed 0, Gemini 3.8 Flash sellers", pad=8)

    q = SimpleNamespace(channel="note", frag=DANIEL_LEO, check_fragment=lambda f: f,
                        header="Leo, private reasoning (hour not given in the report)")
    L.callout(ax, q, None, (1.0, 93.75), 36, c, dot=False)
    ax.text(15.4, 94.15, "D.E.'s logs, quoted from\nhis report (section 4.2)", fontsize=12, ha="right",
            va="center", fontstyle="italic", color=style.GRAY)
    handles = [Line2D([], [], color=c, lw=2.8),
               Line2D([], [], ls="none", marker="D", ms=5, mfc=style.GRAY, mec=style.GRAY),
               Line2D([], [], color=named, lw=1.3, ls=(0, (6, 2)))]
    ax.legend(handles, ["mean ask, four LLM sellers", "mean trade price", "prices named in the quote"],
              loc="upper right", bbox_to_anchor=(1.0, 0.88), frameon=False, handlelength=2.0)
    L.channel_key(fig, 0.035, channels=("note",), color=c)
    L.save(fig, "S45_11_daniel_leo.png")


if __name__ == "__main__":
    main()
