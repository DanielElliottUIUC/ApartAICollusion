"""S44.4: the pre-specified test's paired differences and their exact sign-flip null distribution.

Primary endpoint (report_ms/prereg_sol_anchor.md): per seed, the mean ask over hours 11 to 15 opened at $97.50
minus the same opened at $90. The null flips the sign of each of the six differences (2^6 = 64 patterns).
Reads data/s44/runs.csv through make_S44_03_prereg_pairs.pairs(). Writes figures/S44/S44_04_signflip.png.
"""
import itertools
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import s44lib as L  # noqa: E402
from make_S44_03_prereg_pairs import pairs  # noqa: E402

FILE = "S44_04_signflip.png"


def build():
    L.setup()
    P = pairs()
    seeds = sorted(P)
    d = np.array([P[s][2] - P[s][3] for s in seeds])
    obs = d.mean()
    null = np.array([np.dot(signs, d) / len(d) for signs in itertools.product((1, -1), repeat=len(d))])
    hits = int(np.sum(np.abs(null) >= abs(obs) - 1e-9))
    p = hits / len(null)

    c = L.COLOR["sol"]
    fig = plt.figure(figsize=(L.SLOT_IN, 3.9))
    ax_a = fig.add_axes([0.125, 0.17, 0.30, 0.66])
    ax_b = fig.add_axes([0.575, 0.17, 0.40, 0.66])

    # (a) the six paired differences
    ax_a.axhline(0, color=L.GRAY, lw=0.8)
    ax_a.plot(seeds, d, "o", ms=8, color=c, zorder=3)
    ax_a.axhline(obs, color=c, lw=1.4, ls=(0, (4, 2)))
    ax_a.text(2.6, obs - 0.4, f"mean +{obs:.2f}", ha="left", va="top", fontsize=12, color=c)
    ax_a.set_xlim(2.5, 8.5)
    ax_a.set_xticks(seeds)
    ax_a.set_ylim(-1.0, 9.5)
    ax_a.set_yticks([0, 2, 4, 6, 8])
    ax_a.set_xlabel("Seed")
    ax_a.set_ylabel("Difference ($)")
    ax_a.set_title("Paired differences", fontsize=16, pad=8, loc="left")

    # (b) exact null: the 64 sign-flip means as a dot histogram, one dot per pattern, bins of BIN dollars
    BIN = 0.5
    bins = np.round(null / BIN).astype(int)
    stack = Counter()
    top = 0
    for v, b in sorted(zip(null, bins)):
        stack[b] += 1
        top = max(top, stack[b])
        ext = abs(v) >= abs(obs) - 1e-9
        ax_b.plot(b * BIN, stack[b], "o", ms=5.5, color=c if ext else L.LIGHT, mec="none", zorder=3)
    ax_b.set_ylim(0.2, top + 2.6)
    ax_b.set_xlim(-8.6, 8.6)
    ax_b.set_xticks([-6, -3, 0, 3, 6])
    ax_b.set_yticks([1, top])
    ax_b.set_xlabel("Sign-flipped mean ($)")
    ax_b.set_ylabel("Sign patterns")
    ax_b.set_title("Exact null", fontsize=16, pad=8, loc="left")
    ax_b.annotate(f"observed\n+{obs:.2f}", xy=(round(obs / BIN) * BIN, 1.4), xytext=(8.5, top * 0.5),
                  ha="right", va="bottom", fontsize=12, color=c,
                  arrowprops=dict(arrowstyle="-", color=c, lw=0.9, relpos=(0.85, 0.0)))
    ax_b.text(-8.4, top + 1.6, f"p = {hits}/{len(null)} = {p:.3f}", ha="left", va="center", fontsize=12)
    L.letter(fig, ax_a, "a", dx=-0.075)
    L.letter(fig, ax_b, "b", dx=-0.075)
    L.save(fig, FILE)
    plt.close(fig)

    caption = (
        "The primary endpoint of the pre-specified test. (a) Each dot is one seed block. It gives the mean ask over "
        "hours 11 to 15 of the GPT-5.6 Sol market opened at $97.50 minus that of the market opened at $90 (Claude "
        "Haiku 5.5 buyers, messaging off). The dashed line is their mean. (b) The exact two-sided paired sign-flip "
        f"test. Each dot is the mean difference under one of the {len(null)} ways of flipping the signs of the six "
        "differences, and the dots are stacked in $0.50 bins. Coloured dots are at least as far from zero as the "
        "observed mean."
    )
    shows = (
        f"All six differences are positive (+{d.min():.2f} to +{d.max():.2f} dollars) and their mean is "
        f"+{obs:.2f} dollars. Only the all-positive and all-negative patterns reach that size, so p = "
        f"{hits}/{len(null)} = {p:.3f}, the smallest p this test can give with six pairs. "
        "The test is exact and assumes only that, without an opening effect, each difference is as likely to be "
        "negative as positive. Its floor of 2/64 means it shows direction and consistency, not a precise effect "
        "size. "
        "The protocol was committed before the runs started (commit c5a14aa), so this is confirmatory for Sol "
        "with Haiku buyers and messaging off only."
    )
    source = ("`supplement/data/s44/runs.csv` (phase `prereg_anchor`); protocol `report_ms/prereg_sol_anchor.md`, "
              "result `report_ms/prereg_result.md`; script `supplement/scripts/S44/make_S44_04_signflip.py`.")
    return {"id": "S44.4", "title": "Six of six paired differences are positive", "file": FILE,
            "caption": caption, "shows": shows, "source": source, "p": (hits, len(null), obs)}


if __name__ == "__main__":
    out = build()
    print(out["p"])
    print(out["shows"])
