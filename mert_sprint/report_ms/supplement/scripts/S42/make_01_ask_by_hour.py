"""Figure S42.1: mean ask of the four LLM sellers by hour, one panel per arm, Base overlaid.

The view of Agrawal et al. (2025, average seller ask over rounds), applied to Daniel's ten Gemini arms.
Line: arm mean over its 5 markets (market_by_hour.csv avg_ask, LLM sellers only). Band: 95% percentile
bootstrap over markets (whole market paths resampled, 10,000 draws). Gray: Base mean, in every other panel.
Row a: the five arms without the warning; row b: the five with it (pale warning band).
Output: supplement/figures/S42/S42_01_ask_by_hour.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
import numpy as np

import s42lib as L
from s42lib import style

FILE = "S42_01_ask_by_hour.png"


def make():
    style.setup()
    h = L.hours()
    mats = {a: L.arm_matrix(h, a, "avg_ask") for a in L.ARMS}
    fig, stats = L.hourly_grid(mats, ylim=(89.3, 98.2), yticks=[90, 95], yticklabels=["$90", "$95"],
                               ylabel="Mean ask", price_refs=True)
    L.save(fig, FILE)
    plt.close(fig)
    return numbers(h, stats)


def numbers(h, stats):
    """Every number the text quotes, computed here."""
    m = L.markets()
    base = stats["Base"][0]
    gap46 = {a: float(np.mean(stats[a][0][3:6] - base[3:6])) for a in L.ARMS}     # hours 4 to 6
    last = {a: float(np.mean(stats[a][0][10:15])) for a in L.ARMS}                  # hours 11 to 15
    plain = ["D", "E", "F", "F-sham"]                                                # plain offer, +- warning
    noffer_warn = ["G-warn", "G-prec"]
    warn_last = [last[a] for a in L.ARMS if a in L.WARN]
    base_ask = m[m.arm == "Base"]["ask_index"]
    return {"plain_gap_lo": min(-gap46[a] for a in plain), "plain_gap_hi": max(-gap46[a] for a in plain),
            "nooffer_gap_lo": min(-gap46[a] for a in noffer_warn),
            "nooffer_gap_hi": max(-gap46[a] for a in noffer_warn),
            "warn_last_min": min(warn_last), "warn_last_max": max(warn_last), "base_last": last["Base"],
            "base_seed_min": 90 + 10 * base_ask.min(), "base_seed_max": 90 + 10 * base_ask.max()}


def entry():
    n = make()
    return {
        "title": "The early dip in asks follows the offer, not the warning",
        "file": FILE,
        "caption": (
            "Mean ask of the four Gemini 3.8 Flash sellers by hour in D.E.'s undercover market, one panel per arm "
            "with 5 markets each, in the average-ask-by-round view of Agrawal et al. (2025). Blue line: arm mean. Blue band: 95% percentile bootstrap interval over the 5 "
            "markets, resampling whole market paths. Gray line: the Base mean, repeated in every other panel. "
            "Row a holds the five arms without the warning, row b the five with it (pale band). Horizontal lines "
            "mark $90 (dashed, competitive), $95 (dotted, ask index 0.5) and $97.50 (thin, the harness opening). "
            "Seat 5 sends its offer or placebo note at hour 3, and sellers see it from hour 4."),
        "shows": (
            f"In hours 4 to 6 the four plain-offer arms (D, E, F, F-sham) sit ${n['plain_gap_lo']:.2f} to "
            f"${n['plain_gap_hi']:.2f} below Base with or without the warning, while G-warn and G-prec, with the "
            f"warning but no offer, sit ${n['nooffer_gap_lo']:.2f} to ${n['nooffer_gap_hi']:.2f} below it. The early "
            f"dip therefore goes with the offer and seat 5's own cut to $96, not with the warning. Over hours 11 to "
            f"15 the warning arms average ${n['warn_last_min']:.2f} to ${n['warn_last_max']:.2f}, against "
            f"${n['base_last']:.2f} in Base, whose single markets span ${n['base_seed_min']:.2f} to "
            f"${n['base_seed_max']:.2f}. A bootstrap over 5 markets gives too narrow a band, so the figure "
            f"describes the paths and does not test them."),
        "source": f"`{L.SRC}/market_by_hour.csv` (avg_ask, LLM sellers only), `{L.SRC}/market_by_run.csv`. "
                  f"Script: `supplement/scripts/S42/make_01_ask_by_hour.py`.",
    }


if __name__ == "__main__":
    e = entry()
    print(e["shows"])
