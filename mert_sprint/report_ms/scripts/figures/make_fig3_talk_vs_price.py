"""Figure 3: private talk between sellers against price, every market with a per-market message count.

x: private messages between sellers per market. Daniel: table3_extra.csv private_msgs_peer (messages to
   the scripted seat 5 excluded). Ours: collusion_metrics.json dm_summary.total (no scripted seat).
y: last-third ask index of the LLM sellers (Daniel: market_by_run.csv ask_index; ours: joint_criterion.ask_index).
Marker by seller model; filled when the market passes the joint criterion; a black ring marks markets opened
at $90 (our low-anchor runs). Daniel's Gemini markets (5+5 with seat 5) and our Gemini markets (4+4, served
through the Antigravity CLI) use different markers.
Markets with zero private messages are drawn in a separate strip on the left, one column per seller model,
because 68 of the 110 markets sit at zero; horizontal position inside the strip carries no value.
Daniel's zero-message Gemini markets are exactly his 25 warning-arm markets; their column carries the warning
band of Figures 1 and 2.
Daniel's GPT-4.1 and Haiku markets are not drawn: his CSVs give their message counts only as arm means.
The 12 runs of the pre-specified Sol test (data/ms_prereg.csv, Figure 4c) are not drawn: messaging was off.
Slot: full width, 6.5 in.  Output: report/figures/fig3_talk_vs_price.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

import load
import style

GROUPS = ["gemini_dg", "gemini_ms", "sol", "luna", "grok"]
MARKER = {"gemini_dg": "o", "gemini_ms": "D", "sol": "s", "luna": "^", "grok": "v"}
SIZE = {"gemini_dg": 7.0, "gemini_ms": 6.0, "sol": 6.5, "luna": 7.5, "grok": 7.5}
COLOR = {"gemini_dg": style.COLOR["gemini"], "gemini_ms": style.COLOR["gemini"], "sol": style.COLOR["sol"],
         "luna": style.COLOR["luna"], "grok": style.COLOR["grok"]}
LABEL = {"gemini_dg": "Gemini, Daniel's 5+5 market",
         "gemini_ms": "Gemini, our 4+4 market",
         "sol": style.NAME["sol"], "luna": style.NAME["luna"], "grok": style.NAME["grok"]}

FIG_H = 4.2
LEFT, RIGHT, BOTTOM, TOP = 0.115, 0.975, 0.143, 0.835
WSPACE_IN = 0.12        # gap between the zero strip and the right panel, inches
COL_GAP_IN = 0.07       # gap between columns inside the zero strip, inches
MARK_D_IN = 8.0 / 72    # minimum center distance between strip markers, inches
YLO, YHI = -0.9, 0.86


def markets():
    dg = load.daniel_markets()
    dg = dg.assign(msgs=dg["private_msgs_peer"], opening=97.5)
    ms = load.ms_runs()
    ms = ms.assign(msgs=ms["private_messages"], opening=ms["opening_price"])
    cols = ["seller", "msgs", "ask_index", "passed", "opening"]
    df = pd.concat([dg[cols], ms[cols]], ignore_index=True)
    df["passed"] = df["passed"].astype(bool)
    return df


def beeswarm(y_in, d, step=0.004):
    """Deterministic beeswarm in inches: each point, taken in order of y, moves sideways by the smallest
    offset (alternating sides) that keeps it at least d inches from every point already placed."""
    xs = np.zeros(len(y_in))
    placed = []
    for i in np.argsort(y_in, kind="stable"):
        k = 0
        while True:
            for x in ((0.0,) if k == 0 else (k * step, -k * step)):
                if all((x - px) ** 2 + (y_in[i] - py) ** 2 >= d * d for px, py in placed):
                    xs[i] = x
                    break
            else:
                k += 1
                continue
            break
        placed.append((xs[i], y_in[i]))
    return xs


def draw(ax, x, y, g, passed, ring):
    c = COLOR[g]
    ax.plot(x, y, ls="none", marker=MARKER[g], ms=SIZE[g], mec=c, mew=1.4,
            mfc=(c if passed else "white"), zorder=3)
    if ring:
        ax.plot(x, y, ls="none", marker="o", ms=SIZE[g] + 5.0, mfc="none", mec="black", mew=0.9, zorder=2)


def main():
    style.setup()
    df = markets()

    # left strip: zero private messages, one beeswarm column per seller model, x in inches
    h_in = FIG_H * (TOP - BOTTOM)
    zero = df[df["msgs"] == 0]
    cols, x_at = [], 0.0
    for g in GROUPS:
        sub = zero[zero["seller"] == g].reset_index(drop=True)
        y_in = (sub["ask_index"].to_numpy() - YLO) / (YHI - YLO) * h_in
        xs = beeswarm(y_in, MARK_D_IN)
        half = np.abs(xs).max() + MARK_D_IN / 2
        cols.append((g, sub, xs, x_at + half))
        x_at += 2 * half + COL_GAP_IN
    strip_w = x_at - COL_GAP_IN
    total_w = style.SLOT_IN * (RIGHT - LEFT)
    right_w = total_w - strip_w - WSPACE_IN

    fig = plt.figure(figsize=(style.SLOT_IN, FIG_H))
    ax0 = fig.add_axes([LEFT, BOTTOM, strip_w / style.SLOT_IN, TOP - BOTTOM])
    ax1 = fig.add_axes([LEFT + (strip_w + WSPACE_IN) / style.SLOT_IN, BOTTOM, right_w / style.SLOT_IN,
                        TOP - BOTTOM], sharey=ax0)

    dg = load.daniel_markets()
    base = dg.query("arm == 'Base'")["ask_index"]
    warn_arms = set(style.ARM_GROUPS[1][1])
    if set(dg.loc[dg["private_msgs_peer"] == 0, "arm"]) != warn_arms or (
            dg.loc[dg["arm"].isin(warn_arms), "private_msgs_peer"] != 0).any():
        raise ValueError("Daniel's zero-message markets are no longer exactly the warning arms")
    for ax in (ax0, ax1):
        ax.axhspan(base.min(), base.max(), color=style.BASE_BAND, alpha=style.BASE_BAND_ALPHA,
                   zorder=0.2, lw=0)
        style.ref_lines(ax, unit="index")
    ax0.set_ylim(YLO, YHI)

    # the warning arms' column of the zero strip carries the warning band of Figures 1 and 2
    g0, _, xs0, c0 = cols[0]
    half0 = np.abs(xs0).max() + MARK_D_IN / 2 + COL_GAP_IN / 2
    ax0.axvspan(c0 - half0, c0 + half0, color=style.WARN_BAND, lw=0, zorder=0)
    ax0.text(c0, YLO + 0.03, "warning\narms", ha="center", va="bottom", fontsize=12, color=style.WARN_INK,
             linespacing=1.0)

    for g, sub, xs, center in cols:
        for (_, r), x in zip(sub.iterrows(), xs):
            draw(ax0, center + x, r["ask_index"], g, r["passed"], r["opening"] == 90.0)
    ax0.set_xlim(0, strip_w)
    ax0.set_xticks([strip_w / 2], ["0"])
    tick_len = plt.rcParams["xtick.major.size"]
    ax0.tick_params(axis="x", length=0, pad=plt.rcParams["xtick.major.pad"] + tick_len)   # aligns with ax1's ticks
    ax0.set_ylabel("Ask index")
    ax0.set_yticks([-0.5, 0, 0.5], ["−0.5", "0", "0.5"])

    # right: markets with private messages
    talk = df[df["msgs"] > 0]
    for _, r in talk.iterrows():
        draw(ax1, r["msgs"], r["ask_index"], r["seller"], r["passed"], r["opening"] == 90.0)
    ax1.set_xlim(35, 124)
    ax1.set_xticks([40, 60, 80, 100, 120])
    ax1.tick_params(axis="y", left=False, labelleft=False)
    ax1.spines["left"].set_visible(False)
    tx = 54
    ax1.text(tx, 0.75 + 0.015, "0.75, $97.50 opening", ha="left", va="bottom", fontsize=12, color=style.GRAY)
    ax1.text(tx, 0.5 - 0.02, "0.5, $95", ha="left", va="top", fontsize=12, color=style.GRAY)
    ax1.text(tx, base.min() + 0.012, "Base range", ha="left", va="bottom", fontsize=12, color=style.GRAY)
    ax1.text(tx, 0.0 - 0.02, "0, $90", ha="left", va="top", fontsize=12, color=style.GRAY)

    # axis break marks on the shared baseline (drawn in inches from each panel edge)
    for ax, x_in, w_in in ((ax0, strip_w, strip_w), (ax1, 0.0, right_w)):
        sx, sy = 0.04 / w_in, 0.07 / h_in
        x = x_in / w_in
        ax.plot([x - sx, x + sx], [-sy, sy], transform=ax.transAxes, color="black", lw=0.9, clip_on=False)
    fig.text((LEFT + RIGHT) / 2, 0.02, "Private messages between sellers per market", ha="center",
             va="bottom", fontsize=14)

    # model legend on top; encoding legend in the empty lower left of the right panel
    mh = [Line2D([], [], ls="none", marker=MARKER[g], ms=SIZE[g], mec=COLOR[g], mfc=COLOR[g], mew=1.4)
          for g in GROUPS]
    order = [0, 1, 2, 3, 4]
    fig.legend([mh[i] for i in order], [LABEL[GROUPS[i]] for i in order], loc="upper left", ncol=3,
               frameon=False, bbox_to_anchor=(0.005, 1.0), handletextpad=0.2, columnspacing=0.9,
               labelspacing=0.3)
    eh = [Line2D([], [], ls="none", marker="s", ms=7, mec=style.GRAY, mfc=style.GRAY, mew=1.4),
          Line2D([], [], ls="none", marker="s", ms=7, mec=style.GRAY, mfc="white", mew=1.4),
          Line2D([], [], ls="none", marker="o", ms=12, mec="black", mfc="none", mew=0.9)]
    ax1.legend(eh, ["Meets the criterion", "Does not", "Opened at $90"], loc="lower left",
               bbox_to_anchor=(0.0, 0.0), frameon=False, handletextpad=0.3, labelspacing=0.3,
               borderaxespad=0.3)
    style.save(fig, "fig3_talk_vs_price.png")


if __name__ == "__main__":
    main()
