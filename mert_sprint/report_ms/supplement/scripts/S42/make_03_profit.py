"""Figure S42.3: seller profit per market and its two factors, trades and margin per trade, by arm.

Per market, over the four LLM sellers and all 15 hours (market_by_hour.csv):
  trades  = sum of LLM-seller trades;
  profit  = sum over hours of trades x (mean LLM trade price - $80 cost);
  margin  = profit / trades, the mean price over cost per trade.
An analog of the profit table of Agrawal et al. (2025). Dots: markets (filled when the market meets the joint
criterion, market_by_run.csv passed). Black bar: arm mean. Thin line: 95% percentile bootstrap over markets.
Output: supplement/figures/S42/S42_03_profit.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt

import s42lib as L
from s42lib import style

FILE = "S42_03_profit.png"


def make():
    style.setup()
    m = L.markets()

    def vals(col):
        return m[["arm", "seed", "passed"]].assign(value=m[col])

    cols = [
        {"values": vals("trades"), "xlim": (0, 60), "xticks": [0, 25, 50], "xlabel": "Trades per market",
         "title": "Volume"},
        {"values": vals("margin"), "xlim": (8, 18), "xticks": [10, 13, 16],
         "xticklabels": ["$10", "$13", "$16"], "xlabel": "Price over cost\nper trade", "title": "Margin"},
        {"values": vals("profit"), "xlim": (0, 950), "xticks": [0, 400, 800],
         "xticklabels": ["$0", "$400", "$800"], "xlabel": "Profit per market", "title": "Profit"},
    ]
    fig, axes, rows = L.arm_dot_figure(cols, fig_h=5.4)
    L.save(fig, FILE)
    plt.close(fig)
    return numbers(m)


def numbers(m):
    g = m.groupby("arm")
    prof = m.set_index("arm")["profit"]
    ci = {a: L.boot_mean_ci(prof[a]) for a in L.ARMS}
    return {"profit_mean": g["profit"].mean(), "ci": ci, "margin_mean": g["margin"].mean(),
            "margin_min": m["margin"].min(), "margin_max": m["margin"].max(),
            "trades_min": m["trades"].min(), "trades_max": m["trades"].max(),
            "cv_trades": m["trades"].std() / m["trades"].mean(), "cv_margin": m["margin"].std() / m["margin"].mean(),
            "warn_mean": m[m.warn]["profit"].mean(), "nowarn_mean": m[~m.warn]["profit"].mean(),
            "p_E_D": L.perm_p(prof["E"], prof["D"]), "p_F_D": L.perm_p(prof["F"], prof["D"]),
            "p_Gw_B": L.perm_p(prof["G-warn"], prof["Base"]), "p_Gp_B": L.perm_p(prof["G-prec"], prof["Base"])}


def entry():
    n = make()
    pm, ci = n["profit_mean"], n["ci"]
    return {
        "title": "Profit per market follows volume, not the margin per trade",
        "file": FILE,
        "caption": (
            "Seller profit per market and its two factors, by arm, as an analog of the seller-profit measure that "
            "Agrawal et al. (2025) report. The market is D.E.'s undercover market, with four Gemini 3.8 Flash "
            "sellers over all 15 hours. (a) Trades by the four sellers. (b) Mean trade price minus the $80 "
            "cost. (c) Profit, the sum of trade price minus cost over their trades. One dot per market, filled "
            "when the market meets the joint criterion. Black bar: arm mean. Thin line: 95% percentile bootstrap "
            "interval over the 5 markets. Arms with the warning sit on the pale band. Seat 5's trades are left out."),
        "shows": (
            f"Trades per market range from {n['trades_min']} to {n['trades_max']}, while the margin stays between "
            f"${n['margin_min']:.2f} and ${n['margin_max']:.2f} (coefficient of variation {n['cv_trades']:.2f} "
            f"against {n['cv_margin']:.2f}), so profit follows volume. The 25 warning-arm markets average "
            f"${n['warn_mean']:.0f} against ${n['nowarn_mean']:.0f} for the 25 without the warning, so markets "
            f"without talk earned at least as much. Matched contrasts do not separate. Base earned "
            f"${pm['Base']:.0f} against ${pm['G-warn']:.0f} in G-warn and ${pm['G-prec']:.0f} in G-prec "
            f"(p = {L.fmt_p(n['p_Gw_B'])} and {L.fmt_p(n['p_Gp_B'])}), and D earned ${pm['D']:.0f} against "
            f"${pm['E']:.0f} in E and ${pm['F']:.0f} in F (p = {L.fmt_p(n['p_E_D'])} and {L.fmt_p(n['p_F_D'])}, "
            f"exact permutation over 5 against 5 markets)."),
        "source": f"`{L.SRC}/market_by_hour.csv` (trades, avg_trade_price), `{L.SRC}/market_by_run.csv` "
                  f"(passed). Script: `supplement/scripts/S42/make_03_profit.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
