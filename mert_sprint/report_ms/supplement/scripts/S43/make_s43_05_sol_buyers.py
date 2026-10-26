"""S43.5: GPT-5.6 Sol sellers under three buyer models (Claude Haiku 5.5, GPT-6 Luna, GPT-4.1-mini).

Runs (data/s43/s43_runs.csv, seller sol, opening $97.50): 12 frontier runs (Haiku or Luna buyers) and 6
frontier_b41 runs (GPT-4.1-mini buyers), 3 seeds per buyer model and messaging setting.
(a) Mean ask by hour over the 6 runs of each buyer model. (b) Last-third ask index of each run; filled = passes.
Output: figures/S43/S43_05_sol_buyers.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_05_sol_buyers.png"
BUYERS = ["haiku", "luna", "gpt41mini"]
SHADE = {"haiku": L.COLOR["sol"], "luna": L.tint(L.COLOR["sol"], 0.4), "gpt41mini": L.shade(L.COLOR["sol"], 0.45)}


def make():
    L.setup()
    df = L.runs()
    s = df[(df.seller == "sol") & (df.opening == 97.5)]
    if s.groupby(["buyer", "messaging"]).size().to_dict() != {(b, m): 3 for b in BUYERS for m in ("off", "on")}:
        raise ValueError("expected 3 Sol runs per buyer model and messaging setting")

    fig = plt.figure(figsize=(L.SLOT_IN, 7.0))
    ax1 = fig.add_axes([0.125, 0.585, 0.6, 0.375])
    ax2 = fig.add_axes([0.125, 0.125, 0.85, 0.33])
    hours = np.array(L.HOURS)

    L.window(ax1)
    L.ref_lines(ax1)
    ends = []
    for b in BUYERS:
        y = s[s.buyer == b][L.ASK_COLS].to_numpy(float).mean(axis=0)
        ax1.plot(hours, y, color=SHADE[b], lw=2.2, zorder=3)
        ends.append((y[-1], L.BUYER_SHORT[b], SHADE[b]))
    ax1.set_xlim(0.5, 15.5)
    ax1.set_ylim(89, 99)
    ax1.set_yticks([90, 92.5, 95, 97.5])
    ax1.set_yticklabels(["90", "92.5", "95", "97.5"])
    ax1.set_xticks([1, 5, 10, 15])
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Mean seller ask ($)")
    _end_labels(ax1, ends, 16.0)
    L.panel_letter(ax1, "a", x=-0.13, y=1.0)

    L.ref_lines(ax2, unit="index", which=(90.0, 95.0, 97.5))
    for i, b in enumerate(BUYERS):
        for dx, msg in [(-0.18, "on"), (0.18, "off")]:
            g = s[(s.buyer == b) & (s.messaging == msg)].sort_values("ask_index")
            offs = _spread(g.ask_index.to_numpy(), 0.07)
            for (_, r), o in zip(g.iterrows(), offs):
                ax2.plot(i + dx + o, r.ask_index, "o", ms=8, mec=SHADE[b], mew=1.6, zorder=3,
                         mfc=SHADE[b] if r.passed else "white")
            ax2.text(i + dx, -0.17, msg, ha="center", va="center", fontsize=12, color=L.GRAY)
        g = s[s.buyer == b]
        ax2.plot([i - 0.34, i + 0.34], [g.ask_index.mean()] * 2, color="black", lw=1.6, zorder=4)
        ax2.text(i, 0.86, f"{int(g.passed.sum())} of {len(g)} pass", ha="center", va="bottom", fontsize=12,
                 color=L.shade(SHADE[b], 0.15), fontweight="bold")
    ax2.set_xlim(-0.55, len(BUYERS) - 0.45)
    ax2.set_ylim(-0.08, 0.97)
    ax2.set_xticks(range(len(BUYERS)))
    ax2.set_xticklabels([L.BUYER_NAME[b] + chr(10) + "buyers" for b in BUYERS])
    ax2.tick_params(axis="x", length=0, pad=24)
    ax2.set_yticks([0, 0.25, 0.5, 0.75])
    ax2.set_ylabel("Ask index, hours 11 to 15")
    ax2.spines["bottom"].set_visible(False)
    L.panel_letter(ax2, "b", x=-0.1, y=1.07)
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    k = {b: int(s[s.buyer == b].passed.sum()) for b in BUYERS}
    n = {b: int((s.buyer == b).sum()) for b in BUYERS}
    mean = {b: s[s.buyer == b].ask_index.mean() for b in BUYERS}
    ti = {b: s[s.buyer == b].trade_index.mean() for b in BUYERS}
    p_b41 = L.fisher(k["gpt41mini"], n["gpt41mini"], k["haiku"] + k["luna"], n["haiku"] + n["luna"])
    near = s[(~s.passed) & ((s.ask_index - 0.5).abs() < 0.001)]
    if len(near) != 1:
        raise ValueError("expected one near miss")
    nr = near.iloc[0]
    caption = (
        "GPT-5.6 Sol sellers under three buyer models at the default $97.50 opening, 6 runs per buyer model "
        "(3 seeds with messaging on and 3 with it off). (a) Mean seller ask by hour over each buyer model's 6 "
        "runs, labelled by buyer model. (b) The last-third ask index of each run, messaging on in the left column "
        "of each group and off in the right. Filled markers meet the joint criterion and the black bar is the "
        "group mean. GPT-4.1-mini is the buyer model of the undercover market. Grey lines mark $90 or index 0 "
        "(dashed), $95 or index 0.5 (dotted) and $97.50 or index 0.75 (thin solid).")
    shows = (
        f"Sol passes {k['haiku']} of {n['haiku']} runs with Haiku buyers, {k['luna']} of {n['luna']} with Luna "
        f"buyers and {k['gpt41mini']} of {n['gpt41mini']} with GPT-4.1-mini buyers (Fisher exact p = "
        f"{L.pval(p_b41)} for GPT-4.1-mini against the other two). Mean ask indices are {L.num(mean['haiku'])}, "
        f"{L.num(mean['luna'])} and {L.num(mean['gpt41mini'])}, and the mean trade indices "
        f"({L.num(ti['haiku'])}, {L.num(ti['luna'])} and {L.num(ti['gpt41mini'])}) show that every buyer model "
        f"paid close to Sol's asks. One GPT-4.1-mini run (messaging {nr.messaging}, seed {nr.seed}) fails at "
        f"{nr.ask_index:.4f}. With 3 runs per cell the figure rules out a large buyer effect but not a small "
        f"one, and Luna and Grok sellers were not run with GPT-4.1-mini buyers.")
    return {"title": "Sol passes under all three buyer models", "file": FILE, "caption": caption,
            "shows": shows,
            "source": "data/s43/s43_runs.csv (seller sol, opening 97.5), built from experiments/runs/{box,shard2}/"
                      "frontier/*gpt56sol* and experiments/runs/shard2/frontier_b41/; figure script "
                      "scripts/S43/make_s43_05_sol_buyers.py.",
            "path": path}


def _spread(vals, step, close=0.05):
    offs = np.zeros(len(vals))
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[j + 1] - vals[j] < close:
            j += 1
        m = j - i + 1
        offs[i:j + 1] = (np.arange(m) - (m - 1) / 2) * step
        i = j + 1
    return offs


def _end_labels(ax, items, x, gap_in=0.2):
    fig = ax.figure
    h_in = ax.get_position().height * fig.get_size_inches()[1]
    lo, hi = ax.get_ylim()
    gap = gap_in * (hi - lo) / h_in
    items = sorted(items, key=lambda t: t[0])
    pos = [it[0] for it in items]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    shift = (sum(it[0] for it in items) - sum(pos)) / len(pos)
    pos = [p + shift for p in pos]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    for (y, text, color), py in zip(items, pos):
        ax.text(x, py, text, ha="left", va="center", fontsize=12, color=color, clip_on=False)
        if abs(py - y) > gap * 0.15:
            ax.plot([15.6, x - 0.1], [y, py], color=color, lw=0.8, clip_on=False)


if __name__ == "__main__":
    out = make()
    print(out["caption"])
    print(out["shows"])
