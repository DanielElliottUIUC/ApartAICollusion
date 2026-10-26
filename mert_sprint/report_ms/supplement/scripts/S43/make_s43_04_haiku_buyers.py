"""S43.4: five seller families against the same Claude Haiku 5.5 buyers, default $97.50 opening, no notice.

Runs (data/s43/s43_runs.csv, buyer 'haiku', notice False): Sol, Luna and Grok from the frontier phase (6 each,
messaging on and off), Claude Haiku 5.5 sellers from step A (on and off) and step B (CCCC, on), 9 runs, and
Gemini 3.8 Flash sellers from step A (on and off) and step B (GGGG, on), 9 runs. All share one configuration
except the seller model and the tag (checked by comparing the 'Auction configured with' blocks).
(a) Mean ask by hour over each family's runs (hours with no ask in a run are left out of that hour's mean).
(b) Last-third ask index of every run, messaging on (left column) and off (right column); filled = passes.
Output: figures/S43/S43_04_haiku_buyers.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_04_haiku_buyers.png"
FAMS = ["sol", "gemini", "luna", "grok", "haiku"]


def make():
    L.setup()
    df = L.runs()
    d = df[(df.buyer == "haiku") & (~df.notice) & (df.opening == 97.5)]
    n = d.groupby("seller").size().to_dict()
    expect = {"sol": 6, "luna": 6, "grok": 6, "haiku": 9, "gemini": 9}
    if n != expect:
        raise ValueError(f"run counts {n}")

    fig = plt.figure(figsize=(L.SLOT_IN, 7.3))
    ax1 = fig.add_axes([0.125, 0.585, 0.66, 0.37])
    ax2 = fig.add_axes([0.125, 0.075, 0.85, 0.38])
    hours = np.array(L.HOURS)

    # (a) mean ask by hour
    L.window(ax1)
    L.ref_lines(ax1)
    ends = []
    for f in FAMS:
        g = d[d.seller == f]
        y = np.nanmean(g[L.ASK_COLS].to_numpy(float), axis=0)
        ax1.plot(hours, y, color=L.COLOR[f], lw=2.0, zorder=3)
        ends.append((y[-1], f"{L.SHORT[f]} ({n[f]})", L.COLOR[f]))
    ax1.set_xlim(0.5, 15.5)
    ax1.set_ylim(82, 100)
    ax1.set_yticks([85, 90, 95, 100])
    ax1.set_xticks([1, 5, 10, 15])
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Mean seller ask ($)")
    _end_labels(ax1, ends, 16.0)
    L.panel_letter(ax1, "a", x=-0.13, y=1.0)

    # (b) last-third ask index per run
    L.ref_lines(ax2, unit="index", which=(90.0, 95.0))
    xs = {}
    for i, f in enumerate(FAMS):
        for dx, msg in [(-0.2, "on"), (0.2, "off")]:
            g = d[(d.seller == f) & (d.messaging == msg)].sort_values("ask_index")
            if g.empty:
                continue
            x0 = i + dx
            offs = _spread(g.ask_index.to_numpy(), 0.055)
            for (_, r), o in zip(g.iterrows(), offs):
                ax2.plot(x0 + o, r.ask_index, "o", ms=7, mec=L.COLOR[f], mew=1.4, zorder=3,
                         mfc=L.COLOR[f] if r.passed else "white")
            ax2.text(x0, -1.04, msg, ha="center", va="center", fontsize=12, color=L.GRAY)
            xs[(f, msg)] = x0
        g = d[d.seller == f]
        ax2.plot([i - 0.36, i + 0.36], [g.ask_index.mean()] * 2, color="black", lw=1.6, zorder=4)
        ax2.text(i, 0.93, f"{int(g.passed.sum())} of {len(g)}", ha="center", va="bottom", fontsize=12,
                 color=L.COLOR[f] if f != "haiku" else L.shade(L.COLOR[f], 0.3), fontweight="bold")
    ax2.set_xlim(-0.55, len(FAMS) - 0.45)
    ax2.set_ylim(-0.95, 1.08)
    ax2.set_xticks(range(len(FAMS)))
    ax2.set_xticklabels([L.SHORT[f] for f in FAMS])
    ax2.tick_params(axis="x", length=0, pad=22)
    ax2.set_yticks([-0.5, 0, 0.5])
    ax2.set_ylabel("Ask index, hours 11 to 15")
    ax2.spines["bottom"].set_visible(False)
    ax2.text(len(FAMS) - 0.47, 0.5, "0.5", ha="right", va="bottom", fontsize=12, color=L.GRAY)
    L.panel_letter(ax2, "b", x=-0.1, y=1.02)
    ax2.text(-0.5, 1.08, "runs passing", ha="left", va="bottom", fontsize=12, color=L.GRAY)
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    k = d.groupby("seller").passed.sum().astype(int).to_dict()
    mean = d.groupby("seller").ask_index.mean().to_dict()
    p_hs = L.fisher(k["haiku"], n["haiku"], k["sol"], n["sol"])
    p_hg = L.fisher(k["haiku"], n["haiku"], k["gemini"], n["gemini"])
    late = d.assign(late=d[[f"ask_h{h}" for h in L.LAST_THIRD]].mean(axis=1, skipna=True))
    hk_lt = late[late.seller == "haiku"].late
    width = late.groupby("seller").late.agg(lambda v: v.max() - v.min())
    if width.idxmin() != "haiku":
        raise ValueError("Haiku is not the narrowest band")
    h4 = {f: np.nanmean(d[d.seller == f]["ask_h4"]) for f in FAMS}
    rec = d[d.criterion_source.str.startswith("recomputed")]
    noask = d[d.sellers_asking_last_third == 0]
    ft = d[d.failed_turns > 0]
    caption = (
        "Five seller families against the same Claude Haiku 5.5 buyers in the same 4+4 market at the default "
        "$97.50 opening. (a) Mean seller ask by hour over each family's runs, with the number of runs in brackets. "
        "(b) The last-third ask index of every run, messaging on in the left column of each family and off in "
        "the right. Filled markers meet the joint criterion, the black bar is the family mean, and the count "
        "above gives passing runs. Sol, Luna and Grok are frontier runs, and Haiku and Gemini are our step A and "
        "B runs, which use the same configuration apart from the seller model. "
        f"Gemini GGGG seed {int(rec.seed.iloc[0])} is recomputed from its auction_results.md because its metrics "
        f"file holds hour 1 only, and GGGG seed {int(noask.seed.iloc[0])} posted no asks after hour 11 and fails "
        "on volume. Grey lines mark $90 or index 0 (dashed), $95 or index 0.5 (dotted) and $97.50 (thin solid).")
    shows = (
        f"With the buyers held fixed, Sol passes {L.kofn(k['sol'], n['sol'])} runs and Gemini "
        f"{L.kofn(k['gemini'], n['gemini'])}, while Luna, Grok and Haiku pass none of their "
        f"{n['luna']}, {n['grok']} and {n['haiku']} runs (family mean ask indices {L.num(mean['sol'])}, {L.num(mean['gemini'])}, "
        f"{L.num(mean['luna'])}, {L.num(mean['grok'])} and {L.num(mean['haiku'])}). Haiku sellers fall to "
        f"{L.usd(h4['haiku'])} by hour 4, and their runs end in the narrowest band of the five, with mean asks over "
        f"hours 11 to 15 of {L.usd(hk_lt.min())} to {L.usd(hk_lt.max())}. Haiku against Sol gives Fisher exact p = {L.pval(p_hs)}, and "
        f"Haiku against Gemini p = {L.pval(p_hg)}. The comparison is exploratory, because the Haiku and Gemini "
        f"runs were separate batches and the Gemini runs went through other serving routes (OpenRouter, and the "
        f"Antigravity CLI for the no-messaging run with seed 1, per notes/strategy_oct25/01_our_results.md, "
        f"section 3.2).")
    if k["luna"] or k["grok"] or k["haiku"]:
        raise ValueError("text says Luna, Grok and Haiku pass none")
    if not (len(rec) == 1 and len(noask) == 1 and len(ft) == 1):
        raise ValueError("the run notes in the text no longer match the data")
    return {"title": "Five seller families against the same Haiku buyers", "file": FILE,
            "caption": caption, "shows": shows,
            "source": "data/s43/s43_runs.csv (buyer haiku, no notice), built from experiments/runs/{box,shard2}/"
                      "frontier/, experiments/runs/{shard2,shard3}/A/ and experiments/runs/{shard2,shard3}/B/ "
                      "(CCCC and GGGG) by scripts/S43/build_s43_data.py; figure script "
                      "scripts/S43/make_s43_04_haiku_buyers.py.",
            "path": path}


def _spread(vals, step, close=0.07):
    """Horizontal offsets for sorted values: markers closer than `close` in y form a cluster,
    and the members of a cluster are centred side by side, `step` apart."""
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
