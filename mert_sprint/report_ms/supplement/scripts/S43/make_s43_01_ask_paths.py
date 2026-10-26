"""S43.1: the mean seller ask by hour in each of the 36 frontier runs, one panel per seller model and condition.

Rows: GPT-5.6 Sol, GPT-6 Luna, Grok 4.7 sellers. Columns: messaging on or off, Claude Haiku 5.5 or GPT-6 Luna
buyers. Each panel holds its 3 seeds. The end marker is filled when the run passes the joint criterion.
Data: data/s43/s43_runs.csv, phase 'frontier' (ask_h1..ask_h15 = avg_seller_asks_by_round).
Output: figures/S43/S43_01_ask_paths.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_01_ask_paths.png"
MODELS = ["sol", "luna", "grok"]
COLS = [("on", "haiku"), ("on", "luna"), ("off", "haiku"), ("off", "luna")]


def make():
    L.setup()
    df = L.frontier36()
    fig, axes = plt.subplots(3, 4, figsize=(L.SLOT_IN, 6.9), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.115, right=0.935, top=0.855, bottom=0.085, wspace=0.12, hspace=0.16)
    hours = np.array(L.HOURS)
    counts = {}
    for i, m in enumerate(MODELS):
        for j, (msg, buy) in enumerate(COLS):
            ax = axes[i, j]
            cell = df[(df.seller == m) & (df.messaging == msg) & (df.buyer == buy)].sort_values("seed")
            if len(cell) != 3:
                raise ValueError(f"{m} {msg} {buy}: {len(cell)} runs")
            L.window(ax)
            L.ref_lines(ax)
            for _, r in cell.iterrows():
                y = r[L.ASK_COLS].to_numpy(float)
                ax.plot(hours, y, color=L.COLOR[m], lw=1.7 if r.passed else 1.0, zorder=3, clip_on=False)
                ax.plot(15, y[-1], "o", ms=5.5, mec=L.COLOR[m], mew=1.3, zorder=4, clip_on=False,
                        mfc=L.COLOR[m] if r.passed else "white")
            k = int(cell.passed.sum())
            counts[(m, msg, buy)] = k
            hi = cell[[f"ask_h{h}" for h in L.LAST_THIRD]].to_numpy().mean() > 92.5
            ax.text(14.6, 81.0 if hi else 102.0, f"{k} pass", ha="right", va="bottom" if hi else "top",
                    fontsize=12, color=L.GRAY)
            ax.set_xlim(0.5, 15.5)
            ax.set_ylim(80, 102.3)
            ax.set_xticks([5, 10, 15])
            ax.set_yticks([80, 90, 100])
            ax.tick_params(length=3)
            if j == 3:
                ax.text(1.06, 0.5, L.SHORT[m], transform=ax.transAxes, rotation=270, ha="left", va="center",
                        fontsize=14, color=L.COLOR[m], fontweight="bold")
            if i == 0:
                ax.text(0.5, 1.04, f"{L.BUYER_SHORT[buy]} buyers", transform=ax.transAxes, ha="center",
                        va="bottom", fontsize=12)
    # group header over each pair of columns, with a thin rule
    for j0, label in [(0, "Messaging on"), (2, "Messaging off")]:
        b0, b1 = axes[0, j0].get_position(), axes[0, j0 + 1].get_position()
        y = b0.y1 + 0.052
        fig.text((b0.x0 + b1.x1) / 2, y + 0.006, label, ha="center", va="bottom", fontsize=12, fontweight="bold")
        fig.add_artist(plt.Line2D([b0.x0 + 0.01, b1.x1 - 0.01], [y, y], color=L.GRAY, lw=0.8))
    fig.supylabel("Mean seller ask ($)", fontsize=14, x=0.012)
    fig.supxlabel("Hour", fontsize=14, y=0.012)
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    tot = {m: int(df[df.seller == m].passed.sum()) for m in MODELS}
    n = {m: int((df.seller == m).sum()) for m in MODELS}
    h1 = {m: df[df.seller == m]["ask_h1"].mean() for m in MODELS}
    h2 = {m: df[df.seller == m]["ask_h2"].mean() for m in MODELS}
    lt = {m: df[df.seller == m][[f"ask_h{h}" for h in L.LAST_THIRD]].mean(axis=1) for m in MODELS}
    sol_min_lt = lt["sol"].min()
    other_max_lt = max(lt["luna"].max(), lt["grok"].max())
    luna_hi = df[(df.seller == "luna")].sort_values("ask_index").iloc[-1]
    p_sl = L.fisher(tot["sol"], n["sol"], tot["luna"], n["luna"])
    cell_txt = "; ".join(
        f"{L.SHORT[m]} {', '.join(str(counts[(m, msg, b)]) for msg, b in COLS)}" for m in MODELS)
    caption = (
        f"Mean seller ask by hour in each of the 36 frontier runs at the default $97.50 opening. Rows give the "
        f"seller model and columns give messaging and the buyer model, with 3 seeds per panel. A filled end "
        f"marker and a thicker line mark a run that meets the joint criterion, an open marker one that does not, "
        f"and the number in each panel counts passing runs. The pale band covers hours 11 to 15, the last third "
        f"that the criterion reads. Grey lines mark $90 (dashed), $95 (dotted) and $97.50 (thin solid).")
    shows = (
        f"Passes sit in one row. Sol passes {L.kofn(tot['sol'], n['sol'])}, Luna {L.kofn(tot['luna'], n['luna'])} "
        f"and Grok {L.kofn(tot['grok'], n['grok'])} (per panel, in column order: {cell_txt}). "
        f"The rows already differ in hour 1, when the mean ask was {L.usd(h1['sol'])} for Sol, "
        f"{L.usd(h1['luna'])} for Luna and {L.usd(h1['grok'])} for Grok, and by hour 2 Luna and Grok averaged "
        f"{L.usd(h2['luna'])} and {L.usd(h2['grok'])}. "
        f"Within a row the four panels look alike, so neither messaging nor the buyer model moves the outcome at "
        f"3 seeds per panel. The lowest Sol run averaged {L.usd(sol_min_lt)} over hours 11 to 15, and the "
        f"highest Luna or Grok run {L.usd(other_max_lt)} (Luna, messaging {luna_hi.messaging}, "
        f"{L.BUYER_SHORT[luna_hi.buyer]} buyers, seed {luna_hi.seed}). Sol against Luna is Fisher exact "
        f"p = {L.pval(p_sl)}, and Sol against Grok gives the same p. This is the raw view behind Table B1 of the "
        f"report and does not show why the models differ.")
    return {
        "title": "Every frontier run, hour by hour",
        "file": FILE, "caption": caption, "shows": shows,
        "source": "data/s43/s43_runs.csv (phase frontier), built from collusion_metrics.json and unified.log in "
                  "experiments/runs/box/frontier/ and experiments/runs/shard2/frontier/ by "
                  "scripts/S43/build_s43_data.py; figure script scripts/S43/make_s43_01_ask_paths.py.",
        "path": path,
    }


if __name__ == "__main__":
    out = make()
    print(out["caption"])
    print(out["shows"])
