"""S44.3: the pre-specified Sol test, one panel per seed block, the $97.50 and $90 markets hour by hour.

Reads data/s44/runs.csv (phase prereg_anchor: 12 GPT-5.6 Sol markets, Claude Haiku 5.5 buyers, messaging off,
seeds 3 to 8, opened at $97.50 and at $90). Writes figures/S44/S44_03_prereg_pairs.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402

import s44lib as L  # noqa: E402

FILE = "S44_03_prereg_pairs.png"
LATE = [f"ask_h{h}" for h in range(11, 16)]


def pairs():
    """Per seed: (path at $97.50, path at $90, late mean at $97.50, late mean at $90, passed hi, passed lo)."""
    runs = L.load("runs")
    pre = L.cell(runs, n=12, phase="prereg_anchor", seller="sol", messaging="off", buyer="Haiku")
    out = {}
    for seed in range(3, 9):
        hi = L.cell(pre, n=1, seed=seed, opening=97.5).iloc[0]
        lo = L.cell(pre, n=1, seed=seed, opening=90.0).iloc[0]
        out[seed] = (hi[L.ASK_COLS].to_numpy(float), lo[L.ASK_COLS].to_numpy(float),
                     hi[LATE].mean(), lo[LATE].mean(), bool(hi["passed"]), bool(lo["passed"]))
    return out


def build():
    L.setup()
    P = pairs()
    c_hi, c_lo = L.COLOR["sol"], L.tint(L.COLOR["sol"], 0.45)
    fig, axes = plt.subplots(2, 3, figsize=(L.SLOT_IN, 5.6), sharex=True, sharey=True,
                             gridspec_kw=dict(left=0.12, right=0.975, top=0.775, bottom=0.11, hspace=0.42,
                                              wspace=0.10))
    for ax, seed in zip(axes.flat, range(3, 9)):
        hi, lo, mhi, mlo, phi, plo = P[seed]
        ax.axvspan(10.5, 15.5, color="#EEEEEE", zorder=0)
        L.ref_lines(ax)
        ax.plot(L.HOURS, hi, color=c_hi, lw=2.0)
        ax.plot(L.HOURS, lo, color=c_lo, lw=2.4)
        for y, p, c in ((hi[-1], phi, c_hi), (lo[-1], plo, c_lo)):
            ax.plot(15, y, "o", ms=6, mec=c_hi, mew=1.3, mfc=c_hi if p else "white", zorder=4, clip_on=False)
        ax.text(13.0, 92.6, f"+{mhi - mlo:.2f}", ha="center", va="center", fontsize=12, fontweight="bold")
        ax.set_title(f"Seed {seed}", fontsize=16, pad=4)
    ax = axes[0, 0]
    ax.set_ylim(87.0, 98.6)
    ax.set_yticks([90, 95])
    ax.set_xlim(0.5, 15.5)
    ax.set_xticks([1, 5, 10, 15])
    for a in axes[-1]:
        a.set_xlabel("Hour")
    fig.text(0.015, 0.46, "Mean seller ask ($)", rotation=90, ha="left", va="center", fontsize=14)
    # key, drawn once above the panels
    fig.text(0.12, 0.975, "Pre-specified test, GPT-5.6 Sol, messaging off", fontsize=16, ha="left", va="top")
    kx = 0.12
    fig.lines.append(plt.Line2D([kx, kx + 0.06], [0.905, 0.905], color=c_hi, lw=2.0, transform=fig.transFigure))
    fig.text(kx + 0.07, 0.905, "opened at $97.50", fontsize=12, va="center")
    kx2 = 0.47
    fig.lines.append(plt.Line2D([kx2, kx2 + 0.06], [0.905, 0.905], color=c_lo, lw=2.4,
                                transform=fig.transFigure))
    fig.text(kx2 + 0.07, 0.905, "opened at $90", fontsize=12, va="center")
    fig.text(0.12, 0.858, "grey band: hours 11 to 15, the test window", fontsize=12, va="center", ha="left",
             color=L.GRAY)
    L.save(fig, FILE)
    plt.close(fig)

    d = {s: P[s][2] - P[s][3] for s in P}
    n_hi = sum(P[s][4] for s in P)
    n_lo = sum(P[s][5] for s in P)
    h1_hi = [P[s][0][0] for s in P]
    h1_lo = [P[s][1][0] for s in P]
    caption = (
        "The 12 markets of the pre-specified opening-price test (protocol committed before launch): GPT-5.6 Sol "
        "sellers, Claude Haiku 5.5 buyers, messaging off, seeds 3 to 8, each seed run once from the default $97.50 "
        "opening (dark line) and once from $90 (light line). The grey band is the primary-endpoint window, hours 11 to "
        "15, and the bold number is that seed's paired difference of the mean ask over the window. A filled hour-15 "
        "marker meets the joint criterion. Horizontal lines mark $90 (dashed), $95 (dotted) and $97.50 (thin)."
    )
    above = all((P[s][0] > P[s][1]).all() for s in P)
    if not above:
        raise ValueError("a $97.50 path dips below its $90 pair; rewrite the sentence")
    g1 = {s: P[s][0][0] - P[s][1][0] for s in P}
    narrower = sum(d[s] < g1[s] for s in P)
    fails_hi = [s for s in P if not P[s][4]]
    runs = L.load("runs")
    fail_txt = "; ".join(
        f"seed {s} fails at $97.50 with a last-third ask index of "
        f"{L.cell(runs, n=1, phase='prereg_anchor', seed=s, opening=97.5).iloc[0]['ask_index']:.3f}, under the 0.5 bar"
        for s in fails_hi)
    shows = (
        f"In every seed block the market opened at $97.50 stays above the one opened at $90 in all 15 hours, and "
        f"the paired difference over hours 11 to 15 runs from +{min(d.values()):.2f} to +{max(d.values()):.2f} "
        f"dollars. The hour-1 gap is already +{min(g1.values()):.2f} to +{max(g1.values()):.2f} dollars and is "
        f"larger than the late gap in {narrower} of 6 seeds, so the gap is set in the first hour, not built later. "
        f"{n_hi} of 6 high-opening markets pass and {n_lo} of 6 low-opening markets pass; {fail_txt}. "
        "This tests one model, one buyer model and messaging off over 15 hours, and it does not decide whether "
        "the high-opening passes are collusion."
    )
    source = ("`supplement/data/s44/runs.csv` (phase `prereg_anchor`, from "
              "`experiments/runs/shard2/prereg_anchor/20261025_210228_frontierP{975,90}_gpt56sol_nocomms_haikuB-seed{3..8}/"
              "collusion_metrics.json`); protocol `report_ms/prereg_sol_anchor.md`; script "
              "`supplement/scripts/S44/make_S44_03_prereg_pairs.py`.")
    return {"id": "S44.3", "title": "The pre-specified test, seed by seed", "file": FILE, "caption": caption,
            "shows": shows, "source": source, "diffs": d}


if __name__ == "__main__":
    out = build()
    print(out["diffs"])
    print(out["shows"])
