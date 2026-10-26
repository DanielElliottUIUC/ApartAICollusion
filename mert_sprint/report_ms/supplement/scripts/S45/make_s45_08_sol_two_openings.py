"""S4.5.8: the same private reasoning at two openings. GPT-5.6 Sol, no messaging channel, Claude Haiku 5.5
buyers, seed 0, opened at $97.50 (left) and at $90 (right). In both runs Seller Raj writes at hour 3 that every
rival matched his one-cent undercut; the asks stay where the market opened.

Runs: shard2/frontier/..._gpt56sol_nocomms_haikuB-seed0 and
      shard2/frontier_lowanchor/..._frontierL90_gpt56sol_nocomms_haikuB-seed0.
Lines: each seller's posted ask by hour, Raj's highlighted (unified.log). Call-outs: quotes.py entries s0_raj_h3
and s90_raj_h3. Count in the footer: sellers in the pre-specified test (shard2/prereg_anchor, seeds 3 to 8, six
runs per opening) with at least one private-note sentence that contains "matched" and one of "undercut",
"one-cent" or "penny".
Output: supplement/figures/S45/S45_08_sol_two_openings.png
"""
import re

import matplotlib.pyplot as plt

import s45lib as L
import style
from quotes import S0, S90, QUOTES as Q

SELLERS = ["Kai", "Leo", "Max", "Raj"]
MATCHED = re.compile(r"matched", re.I)
UNDERCUT = re.compile(r"undercut|one-cent|penny", re.I)


def matched_writers(tag):
    """(sellers with a 'rivals matched my undercut' sentence, sellers) over the six pre-specified runs."""
    runs = sorted((L.RUNS / "shard2" / "prereg_anchor").glob(f"*_frontier{tag}_gpt56sol_nocomms_haikuB-seed*"))
    if len(runs) != 6:
        raise ValueError(f"{tag}: {len(runs)} pre-specified runs, expected 6")
    hit = total = 0
    for r in runs:
        for f in sorted(r.glob("Seller *.md")):
            total += 1
            sents = L.private_sentences(r.relative_to(L.RUNS).as_posix(), f.name)
            hit += any(MATCHED.search(s) and UNDERCUT.search(s) for _, _, _, s in sents)
    return hit, total


def panel(ax, folder, q, title, c, dark, box_xy, box_va, rel, header_below):
    rec = L.run(folder)
    style.ref_lines(ax)
    for s in SELLERS:
        ax.plot(L.HOURS, L.ask_path(rec, f"Seller {s}"), color=dark if s == "Raj" else style.tint(c, 0.45),
                lw=2.6 if s == "Raj" else 1.6, zorder=4 if s == "Raj" else 3)
    raj = L.ask_path(rec, "Seller Raj")
    L.callout(ax, q, (q.hour, raj[q.hour - 1]), box_xy, 25, dark, va=box_va, rel=rel, header_below=header_below)
    ax.set_title(title, pad=6)
    ax.text(15.3, 99.35, L.verdict(folder), fontsize=12, ha="right", va="top")
    L.hour_axis(ax)
    ax.set_xticks([1, 5, 10, 15])


def main():
    L.setup()
    c = style.COLOR["sol"]
    dark = "#9A4300"                       # Sol orange, darkened for Raj's line and the text
    n975, t975 = matched_writers("P975")
    n90, t90 = matched_writers("P90")
    print(f"pre-specified runs: {n975} of {t975} sellers at $97.50, {n90} of {t90} at $90")

    fig = plt.figure(figsize=(style.SLOT_IN, 6.4))
    ax_l = fig.add_axes([0.115, 0.285, 0.405, 0.64])
    ax_r = fig.add_axes([0.575, 0.285, 0.405, 0.64], sharey=ax_l)
    ax_l.set_ylim(88.6, 99.6)
    ax_l.set_yticks([90, 92, 94, 96, 98])
    ax_l.set_ylabel("Ask ($)")
    plt.setp(ax_r.get_yticklabels(), visible=False)
    panel(ax_l, S0, Q["s0_raj_h3"], "Opened at $97.50", c, dark, (1.0, 96.7), "top", (0.25, 1.0), True)
    panel(ax_r, S90, Q["s90_raj_h3"], "Opened at $90", c, dark, (1.0, 91.1), "bottom", (0.25, 0.0), False)
    fig.text(0.5, 0.118, f"Pre-specified runs, seeds 3 to 8, no messaging: {n975} of {t975} sellers\n"
             f"at $97.50 and {n90} of {t90} at $90 wrote in private that rivals\nmatched their undercut.",
             fontsize=12, ha="center", va="center")
    L.channel_key(fig, 0.028, channels=("note",), color=dark)
    L.save(fig, "S45_08_sol_two_openings.png")


if __name__ == "__main__":
    main()
