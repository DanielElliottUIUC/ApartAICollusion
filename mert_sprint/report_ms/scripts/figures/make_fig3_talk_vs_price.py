"""Figure 3: private talk between sellers against price, every market with a per-market message count.

x: private messages between sellers per market. Daniel: table3_extra.csv private_msgs_peer (messages to
   the scripted seat 5 excluded). Ours: collusion_metrics.json dm_summary.total (no scripted seat).
y: last-third ask index of the LLM sellers (Daniel: market_by_run.csv ask_index; ours: joint_criterion.ask_index).
Marker by seller model; filled when the market passes the joint criterion; a black ring marks markets opened
at $90 (our low-anchor runs). Gemini in Daniel's 5+5 market (with seat 5) and in our 4+4 market (served
through the Antigravity CLI) use different markers; the legend names the market, not the person.
Markers are drawn hollow first and filled on top, so a filled marker is never hidden by a hollow one.
Markets with zero private messages are drawn in a separate strip on the left, one named column per seller
model and market, because 68 of the 110 markets sit at zero. A bracket under the column names says
"0 messages"; horizontal position inside a column carries no value.
Daniel's zero-message Gemini markets are exactly his 25 warning-arm markets; their column carries the warning
band of Figures 1 and 2.
Both legends sit above the plot, so no data marker falls inside a legend.
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
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.textpath import TextPath
from matplotlib.transforms import blended_transform_factory

import load
import style

GROUPS = ["gemini_dg", "gemini_ms", "sol", "luna", "grok"]
MARKER = {"gemini_dg": "o", "gemini_ms": "D", "sol": "s", "luna": "^", "grok": "v"}
SIZE = {"gemini_dg": 5.6, "gemini_ms": 4.8, "sol": 5.2, "luna": 6.0, "grok": 6.0}     # points
RING = 4.0              # a ring is this many points wider than its marker
MEW = 1.2
COLOR = {"gemini_dg": style.COLOR["gemini"], "gemini_ms": style.COLOR["gemini"], "sol": style.COLOR["sol"],
         "luna": style.COLOR["luna"], "grok": style.COLOR["grok"]}
LABEL = {"gemini_dg": "Gemini, 5+5 market", "gemini_ms": "Gemini, 4+4 market",
         "sol": style.NAME["sol"], "luna": style.NAME["luna"], "grok": style.NAME["grok"]}
COLNAME = {"gemini_dg": "Gemini\n5+5", "gemini_ms": "Gemini\n4+4", "sol": "Sol", "luna": "Luna",
           "grok": "Grok"}     # names under the zero-message columns, 12 pt

FIG_H = 4.86
AX_X0, AX_X1 = 0.76, 6.36    # left and right edge of the two panels together, inches
AX_Y0, AX_Y1 = 1.06, 3.96    # bottom and top of both panels, inches
WSPACE_IN = 0.16             # gap between the zero strip and the right panel, inches
COL_GAP_IN = 0.06            # gap between columns inside the zero strip, inches
COL_PAD_IN = 0.12            # room around a column name, inches
SEP_IN = 0.012               # clearance between strip markers (rings included), inches
YLO, YHI = -0.9, 0.86
XLIM = (35, 122)             # right panel, private messages


def markets():
    dg = load.daniel_markets()
    dg = dg.assign(msgs=dg["private_msgs_peer"], opening=97.5)
    ms = load.ms_runs()
    ms = ms.assign(msgs=ms["private_messages"], opening=ms["opening_price"])
    cols = ["seller", "msgs", "ask_index", "passed", "opening"]
    df = pd.concat([dg[cols], ms[cols]], ignore_index=True)
    df["passed"] = df["passed"].astype(bool)
    df["ring"] = df["opening"] == 90.0
    return df


def radius_in(g, ring):
    """Half the drawn width of a marker (its ring when it has one), edge included, in inches."""
    return ((SIZE[g] + (RING if ring else 0.0)) / 2 + MEW / 2) / 72


def beeswarm(y_in, r_in, step=0.004):
    """Deterministic beeswarm in inches: each point, taken in order of y, moves sideways by the smallest
    offset (alternating sides) that keeps it clear of every point already placed (radii plus SEP_IN)."""
    xs = np.zeros(len(y_in))
    placed = []
    for i in np.argsort(y_in, kind="stable"):
        k = 0
        while True:
            for x in ((0.0,) if k == 0 else (k * step, -k * step)):
                if all((x - px) ** 2 + (y_in[i] - py) ** 2 >= (r_in[i] + pr + SEP_IN) ** 2
                       for px, py, pr in placed):
                    xs[i] = x
                    break
            else:
                k += 1
                continue
            break
        placed.append((xs[i], y_in[i], r_in[i]))
    return xs


def text_width_in(text, size=12):
    """Width in inches of the widest line of text in DejaVu Sans."""
    prop = FontProperties(family="DejaVu Sans", size=size)
    return max(TextPath((0, 0), line, prop=prop).get_extents().width for line in text.split("\n")) / 72


def draw(ax, x, y, g, passed, ring):
    c = COLOR[g]
    ax.plot(x, y, ls="none", marker=MARKER[g], ms=SIZE[g], mec=c, mew=MEW,
            mfc=(c if passed else "white"), zorder=(4 if passed else 3))
    if ring:
        ax.plot(x, y, ls="none", marker="o", ms=SIZE[g] + RING, mfc="none", mec="black", mew=0.9, zorder=2)


def main():
    style.setup()
    df = markets()
    W = style.SLOT_IN

    # left strip: zero private messages, one beeswarm column per seller model, x in inches.
    # A column is as wide as its swarm or its name, whichever is wider.
    h_in = AX_Y1 - AX_Y0
    zero = df[df["msgs"] == 0]
    cols, x_at = [], 0.0
    for g in GROUPS:
        sub = zero[zero["seller"] == g].reset_index(drop=True)
        y_in = (sub["ask_index"].to_numpy() - YLO) / (YHI - YLO) * h_in
        r_in = np.array([radius_in(g, ring) for ring in sub["ring"]])
        xs = beeswarm(y_in, r_in)
        half = max(np.max(np.abs(xs) + r_in), text_width_in(COLNAME[g]) / 2 + COL_PAD_IN / 2)
        cols.append((g, sub, xs, x_at + half, half))
        x_at += 2 * half + COL_GAP_IN
    strip_w = x_at - COL_GAP_IN
    right_w = (AX_X1 - AX_X0) - strip_w - WSPACE_IN

    fig = plt.figure(figsize=(W, FIG_H))
    ax0 = fig.add_axes([AX_X0 / W, AX_Y0 / FIG_H, strip_w / W, h_in / FIG_H])
    ax1 = fig.add_axes([(AX_X0 + strip_w + WSPACE_IN) / W, AX_Y0 / FIG_H, right_w / W, h_in / FIG_H],
                       sharey=ax0)

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
    _, _, _, c0, half0 = cols[0]
    ax0.axvspan(c0 - half0 - COL_GAP_IN / 2, c0 + half0 + COL_GAP_IN / 2, color=style.WARN_BAND, lw=0,
                zorder=0)
    ax0.text(c0, YLO + 0.03, "warning\narms", ha="center", va="bottom", fontsize=12, color=style.WARN_INK,
             linespacing=1.0)

    for g, sub, xs, center, _ in cols:
        for (_, r), x in zip(sub.iterrows(), xs):
            draw(ax0, center + x, r["ask_index"], g, r["passed"], r["ring"])
    ax0.set_xlim(0, strip_w)
    ax0.set_xticks([c for _, _, _, c, _ in cols], [COLNAME[g] for g, *_ in cols])
    tick_len = plt.rcParams["xtick.major.size"]
    ax0.tick_params(axis="x", length=0, pad=plt.rcParams["xtick.major.pad"] + tick_len)   # aligns with ax1's ticks
    ax0.set_ylabel("Ask index")
    ax0.set_yticks([-0.5, 0, 0.5], ["−0.5", "0", "0.5"])

    # bracket under the column names: every strip column sits at 0 messages
    tr = blended_transform_factory(ax0.transData, fig.dpi_scale_trans)
    yb = AX_Y0 - 0.53
    ax0.plot([0.02, 0.02, strip_w - 0.02, strip_w - 0.02], [yb + 0.06, yb, yb, yb + 0.06], transform=tr,
             color="black", lw=0.9, clip_on=False)
    ax0.text(strip_w / 2, yb - 0.04, "0 messages", transform=tr, ha="center", va="top", fontsize=12)

    # right: markets with private messages
    talk = df[df["msgs"] > 0]
    for _, r in talk.iterrows():
        draw(ax1, r["msgs"], r["ask_index"], r["seller"], r["passed"], r["ring"])
    ax1.set_xlim(*XLIM)
    ax1.set_xticks([40, 60, 80, 100, 120])
    ax1.tick_params(axis="y", left=False, labelleft=False)
    ax1.spines["left"].set_visible(False)
    tx = 54
    ax1.text(tx, 0.75 + 0.015, "0.75, $97.50", ha="left", va="bottom", fontsize=12, color=style.GRAY)
    ax1.text(tx, 0.5 - 0.02, "0.5, $95", ha="left", va="top", fontsize=12, color=style.GRAY)
    ax1.text(tx, base.min() + 0.012, "Base range", ha="left", va="bottom", fontsize=12, color=style.GRAY)
    ax1.text(tx, 0.0 - 0.02, "0, $90", ha="left", va="top", fontsize=12, color=style.GRAY)

    # axis break marks on the shared baseline (drawn in inches from each panel edge)
    for ax, x_in, w_in in ((ax0, strip_w, strip_w), (ax1, 0.0, right_w)):
        sx, sy = 0.04 / w_in, 0.07 / h_in
        x = x_in / w_in
        ax.plot([x - sx, x + sx], [-sy, sy], transform=ax.transAxes, color="black", lw=0.9, clip_on=False)
    fig.text((AX_X0 + AX_X1) / 2 / W, 0.06 / FIG_H, "Private messages between sellers per market",
             ha="center", va="bottom", fontsize=14)

    # legends above the plot, clear of every marker: seller model and market on the left, encoding on the right
    mh = [Line2D([], [], ls="none", marker=MARKER[g], ms=SIZE[g] + 1.0, mec=COLOR[g], mfc=COLOR[g], mew=MEW)
          for g in GROUPS]
    fig.legend(mh, [LABEL[g] for g in GROUPS], loc="upper left", ncol=2, frameon=False,
               bbox_to_anchor=(0.02 / W, 1 - 0.02 / FIG_H), handletextpad=0.3, columnspacing=1.2,
               labelspacing=0.3, borderaxespad=0.0)
    eh = [Line2D([], [], ls="none", marker="s", ms=6.2, mec=style.GRAY, mfc=style.GRAY, mew=MEW),
          Line2D([], [], ls="none", marker="s", ms=6.2, mec=style.GRAY, mfc="white", mew=MEW),
          Line2D([], [], ls="none", marker="o", ms=6.2 + RING, mec="black", mfc="none", mew=0.9)]
    fig.legend(eh, ["Meets the criterion", "Does not", "Opened at $90"], loc="upper right", frameon=False,
               bbox_to_anchor=(1 - 0.02 / W, 1 - 0.02 / FIG_H), handletextpad=0.3, labelspacing=0.3,
               borderaxespad=0.0)
    style.save(fig, "fig3_talk_vs_price.png")


if __name__ == "__main__":
    main()
