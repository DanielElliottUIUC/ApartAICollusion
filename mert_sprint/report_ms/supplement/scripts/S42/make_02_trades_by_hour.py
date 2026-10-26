"""Figure S42.2: trades per hour made by the four LLM sellers, one panel per arm, Base overlaid.

market_by_hour.csv `trades` counts trades whose seller is an LLM seller (seat 5's trades excluded), so the
maximum is 4 per hour. Line: arm mean over 5 markets. Band: 95% percentile bootstrap over markets.
Output: supplement/figures/S42/S42_02_trades_by_hour.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
import numpy as np

import s42lib as L
from s42lib import style

FILE = "S42_02_trades_by_hour.png"


def make():
    style.setup()
    h = L.hours()
    mats = {a: L.arm_matrix(h, a, "trades") for a in L.ARMS}
    fig, stats = L.hourly_grid(mats, ylim=(-0.2, 4.3), yticks=[0, 2, 4], yticklabels=["0", "2", "4"],
                               ylabel="Trades per hour")
    L.save(fig, FILE)
    plt.close(fig)
    return numbers(mats)


def numbers(mats):
    m = L.markets()
    early = {a: float(mats[a][:, :10].mean()) for a in L.ARMS}           # hours 1 to 10
    first = m.groupby("arm")["first_trade_hour"]
    tot = m.set_index("arm")["trades"]
    return {"h1_max": max(mats[a][:, 0].mean() for a in L.ARMS),
            "h15_min": min(mats[a][:, 14].mean() for a in L.ARMS),
            "early": early, "first_min": first.min(), "first_max": first.max(), "first_mean": first.mean(),
            "late_markets": int((m["first_trade_hour"] >= 10).sum()),
            "p_E_D": L.perm_p(tot["E"], tot["D"]), "p_Gw_B": L.perm_p(tot["G-warn"], tot["Base"]),
            "p_Gp_B": L.perm_p(tot["G-prec"], tot["Base"]),
            "tot_mean": m.groupby("arm")["trades"].mean()}


def entry():
    n = make()
    e, tm = n["early"], n["tot_mean"]
    return {
        "title": "Trading starts slowly in every arm, with or without the warning",
        "file": FILE,
        "caption": (
            "Trades per hour made by the four Gemini 3.8 Flash sellers (at most 4 per hour, with seat 5's trades left out), "
            "one panel per arm, 5 markets per arm. Blue line: arm mean. Blue band: 95% percentile bootstrap "
            "interval over markets. Gray line: the Base mean. Row a: no warning. Row b: warning in the prompt "
            "(pale band)."),
        "shows": (
            f"Volume rises through the hours in every arm, from at most {n['h1_max']:.1f} trades per hour in hour 1 "
            f"to at least {n['h15_min']:.1f} in hour 15. Over hours 1 to 10, Base averages {e['Base']:.1f} trades "
            f"per hour, the plain-offer arms D, E, F and F-sham {min(e[a] for a in ['D', 'E', 'F', 'F-sham']):.1f} "
            f"to {max(e[a] for a in ['D', 'E', 'F', 'F-sham']):.1f}, and D-hs and G-prec only {e['D-hs']:.1f} and "
            f"{e['G-prec']:.1f}. In {n['late_markets']} of the 50 markets the four sellers made no trade before "
            f"hour 10. Total trades per market do not separate the warning arms from their matched arms, with "
            f"E at {tm['E']:.1f} against D at {tm['D']:.1f} (p = {L.fmt_p(n['p_E_D'])}) and G-warn at "
            f"{tm['G-warn']:.1f} and G-prec at {tm['G-prec']:.1f} against Base at {tm['Base']:.1f} "
            f"(p = {L.fmt_p(n['p_Gw_B'])} and {L.fmt_p(n['p_Gp_B'])}, exact permutation over markets)."),
        "source": f"`{L.SRC}/market_by_hour.csv` (trades, LLM sellers only). "
                  f"Script: `supplement/scripts/S42/make_02_trades_by_hour.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
