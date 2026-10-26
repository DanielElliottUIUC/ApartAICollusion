"""S44.1: the last-third ask index of every market in each cell that ran at both openings ($97.50 and $90).

Reads data/s44/runs.csv. One dot per market; filled = joint criterion met. Writes figures/S44/S44_01_verdicts.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
import numpy as np  # noqa: E402

import s44lib as L  # noqa: E402

FILE = "S44_01_verdicts.png"
# (label, seller, messaging, buyer, phase at $97.50 or None, phase at $90, runs per opening)
CELLS = [
    ("Sol\nmessaging on", "sol", "on", "Haiku", "frontier", "frontier_lowanchor", 3),
    ("Sol\nmessaging off", "sol", "off", "Haiku", "frontier", "frontier_lowanchor", 3),
    ("Sol, off\nseeds 3 to 8,\npre-specified", "sol", "off", "Haiku", "prereg_anchor", "prereg_anchor", 6),
    ("Luna\nmessaging off", "luna", "off", "Haiku", "frontier", "frontier_lowanchor", 3),
    ("Gemini\nmessaging on", "gemini", "on", "GPT-4.1-mini", "A_agycontrol", "A_lowanchor", 3),
    ("Gemini\nmessaging off", "gemini", "off", "GPT-4.1-mini", None, "A_lowanchor", 3),
]


def build():
    L.setup()
    runs = L.load("runs")
    fig = plt.figure(figsize=(L.SLOT_IN, 6.4))
    ax = fig.add_axes([0.375, 0.085, 0.43, 0.80])
    for r in L.REF_LINES:
        ax.axvline(r["index"], color=L.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)

    y, ticks, labels, facts = 0.0, [], [], {"high": [0, 0], "low": [0, 0], "low_max": -9}
    rows = []
    for name, seller, msg, buyer, ph_hi, ph_lo, n in CELLS:
        c = L.COLOR[seller]
        group_top = y
        for opening, phase in ((97.5, ph_hi), (90.0, ph_lo)):
            if phase is None:
                ax.text(-0.83, y, "not run", ha="left", va="center", color=L.GRAY, fontsize=12)
            else:
                sub = L.cell(runs, n=n, phase=phase, seller=seller, messaging=msg, buyer=buyer, opening=opening)
                k = int(sub["passed"].sum())
                key = "high" if opening == 97.5 else "low"
                facts[key][0] += k
                facts[key][1] += len(sub)
                if opening == 90.0:
                    facts["low_max"] = max(facts["low_max"], sub["ask_index"].max())
                jit = np.linspace(-0.11, 0.11, len(sub))
                for (_, r), j in zip(sub.iterrows(), jit):
                    ax.plot(r["ask_index"], y + j, "o", ms=7, mec=c, mew=1.4,
                            mfc=c if r["passed"] else "white", zorder=3)
                ax.text(0.86, y, f"{k} of {len(sub)} pass", ha="left", va="center", fontsize=12, color="black")
                rows.append((name, opening, k, len(sub), sub["ask_index"].min(), sub["ask_index"].max()))
            ticks.append(y)
            labels.append("$97.50" if opening == 97.5 else "$90")
            y += 0.42
        mid = (group_top + y - 0.42) / 2
        ax.text(0.015, mid, name, ha="left", va="center", fontsize=12, color=c, linespacing=1.1,
                transform=blended_transform_factory(fig.transFigure, ax.transData), fontweight="bold")
        y += 0.38
    ax.set_yticks(ticks, labels)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(y - 0.38 + 0.1, -0.35)
    ax.set_xlim(-0.85, 0.82)
    ax.set_xticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75], ["", "-0.5", "", "0", "", "0.5", "0.75"])
    ax.set_xlabel("Ask index, hours 11 to 15")
    ax.spines["left"].set_visible(False)
    top = ax.secondary_xaxis("top", functions=(lambda i: 90 + 10 * i, lambda p: (p - 90) / 10))
    top.set_xticks([82, 86, 90, 94, 98], ["$82", "$86", "$90", "$94", "$98"])
    top.tick_params(labelsize=12)
    fig.text(0.015, 0.975, "Each market's verdict at the two openings", fontsize=16, ha="left", va="top")
    L.save(fig, FILE)
    plt.close(fig)

    hi, lo = facts["high"], facts["low"]
    caption = (
        "Last-third ask index (mean ask over hours 11 to 15, 0 = $90, 1 = $100) of every market in the cells that "
        "ran from the harness's default $97.50 opening and from $90 with nothing else changed. One dot per market; "
        "a filled dot meets the joint criterion, a hollow dot does not. The pass count of each opening is at the "
        "right. Sol, Luna and the pre-specified Sol test use Claude Haiku 5.5 buyers; Gemini uses GPT-4.1-mini "
        "buyers through the Antigravity route. Gemini without messaging was run only from $90. Vertical lines mark "
        "index 0 ($90, dashed), 0.5 ($95, dotted, the price condition of the criterion) and 0.75 ($97.50, thin)."
    )
    shows = (
        f"Across these cells {hi[0]} of {hi[1]} markets opened at $97.50 pass and {lo[0]} of {lo[1]} opened at "
        f"$90 pass, and no market opened at $90 has an index above {lo_fmt(facts['low_max'])}. "
        "Read each cell as a pair of rows: the high row is the default opening, the low row the low-anchor rerun. "
        "Luna fails at both openings, so the opening is necessary for a pass but not sufficient. "
        "Each cell has 3 markets per opening except the pre-specified test (6), so single cells are thin; the "
        "pooled pattern and the pre-specified test (Figures S44.3 and S44.4) carry the claim."
    )
    source = ("`supplement/data/s44/runs.csv` (from `collusion_metrics.json` `joint_criterion` of "
              "`experiments/runs/{box,shard2}/frontier/`, `shard2/frontier_lowanchor/`, `shard2/prereg_anchor/`, "
              "`shard2/A_agycontrol/`, `shard2/A_lowanchor/`); script `supplement/scripts/S44/make_S44_01_verdicts.py`.")
    return {"id": "S44.1", "title": "No market opened at $90 passes",
            "file": FILE, "caption": caption, "shows": shows, "source": source, "rows": rows}


def lo_fmt(x):
    return f"{x:.3f}"


if __name__ == "__main__":
    out = build()
    for r in out["rows"]:
        print(r)
    print(out["shows"])
