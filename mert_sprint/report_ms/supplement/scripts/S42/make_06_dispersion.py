"""Figure S42.6: ask dispersion among the four LLM sellers in three windows, by arm.

Dispersion is the standard deviation (numpy default, ddof = 0, as in Agrawal et al. 2025) across the four LLM
sellers of each seller's ask in the window, from outcomes.csv:
  hour 3      ask_pre        (the seller's ask in hour 3, the hour seat 5 writes)
  hours 4-6   ask_post_mean  (the seller's mean ask over hours 4 to 6, the first hours the message is visible)
  hours 11-15 last_third_ask (the seller's mean ask over the last third)
So the two later windows measure how far apart the sellers' window means are, not the hour-by-hour spread.
One dot per market, filled when it meets the joint criterion; black bar: arm mean; thin line: 95% bootstrap.
Output: supplement/figures/S42/S42_06_dispersion.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
import numpy as np

import s42lib as L
from s42lib import style

FILE = "S42_06_dispersion.png"
WINDOWS = [("ask_pre", "Hour 3"), ("ask_post_mean", "Hours 4 to 6"), ("last_third_ask", "Last third")]


def dispersion():
    o = L.sellers()
    m = L.markets()[["run_id", "arm", "seed", "passed", "private_msgs_peer", "public_msgs"]]
    if o.groupby("run_id").size().unique().tolist() != [4]:
        raise ValueError("expected four LLM sellers per market")
    sd = o.groupby("run_id")[[c for c, _ in WINDOWS]].agg(lambda v: float(np.std(v, ddof=0)))
    return m.join(sd, on="run_id")


def make():
    style.setup()
    d = dispersion()
    cols = [{"values": d[["arm", "seed", "passed"]].assign(value=d[c]), "xlim": (0, 1.3), "xticks": [0, 0.5, 1.0],
             "xticklabels": ["$0", "$0.50", "$1"], "xlabel": "", "title": t} for c, t in WINDOWS]
    fig, axes, rows = L.arm_dot_figure(cols, fig_h=5.1, col_gap=0.40, bottom=0.80)
    axes[1].set_xlabel("Standard deviation of the four sellers' asks")
    L.save(fig, FILE)
    plt.close(fig)
    return numbers(d)


def arm_counts(df):
    """'5 F, 5 G-prec and 1 F-sham markets' in arm order."""
    k = df.groupby("arm").size()
    parts = [f"{k[a]} {a}" for a in L.ARMS if a in k.index]
    return (", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]) + " markets"


def numbers(d):
    last = d["last_third_ask"]
    silent = d[(d["private_msgs_peer"] == 0) & (d["public_msgs"] == 0)]
    talk = d[d["private_msgs_peer"] > 0]
    return {"med": {c: float(d[c].median()) for c, _ in WINDOWS},
            "share10": float((last < 0.10).mean()), "n10": int((last < 0.10).sum()),
            "silent_n": len(silent), "silent_txt": arm_counts(silent),
            "silent_med": float(silent["last_third_ask"].median()),
            "talk_n": len(talk), "talk_med": float(talk["last_third_ask"].median()),
            "max_row": d.loc[last.idxmax()]}


def entry():
    n = make()
    md, mx = n["med"], n["max_row"]
    return {
        "title": "Sellers price within cents of each other, with or without talk",
        "file": FILE,
        "caption": (
            "Ask dispersion among the four Gemini 3.8 Flash sellers, the ask-dispersion measure of Agrawal et al. "
            "(2025), by arm and window. Each dot is one market, and its value is the standard deviation across "
            "the four sellers of each seller's ask in hour 3 (a), its mean ask over hours 4 to 6 (b) and its mean "
            "ask over hours 11 to 15 (c). Filled dots meet the joint criterion. Black bar: arm mean. Thin line: 95% percentile "
            "bootstrap interval over the 5 markets. Arms with the warning sit on the pale band."),
        "shows": (
            f"The median market has a spread of ${md['ask_pre']:.2f} in hour 3, ${md['ask_post_mean']:.2f} in "
            f"hours 4 to 6 and ${md['last_third_ask']:.2f} in the last third, and {n['n10']} of 50 markets end "
            f"below $0.10. The {n['silent_n']} markets with neither private messages between sellers nor public "
            f"posts ({n['silent_txt']}) have a median last-third spread of ${n['silent_med']:.2f}, "
            + (f"the same as in the {n['talk_n']} markets where sellers messaged each other. "
               if f"{n['silent_med']:.2f}" == f"{n['talk_med']:.2f}" else
               f"against ${n['talk_med']:.2f} in the {n['talk_n']} markets where sellers messaged each other. ")
            + f"Tight asks "
            f"therefore need no talk here, since every seller sees the ask queue and the last five hours of asks. "
            f"The later windows compare the sellers' window means, a snapshot rather than the hour-by-hour "
            f"measure of Agrawal et al."),
        "source": f"`{L.SRC}/outcomes.csv` (ask_pre, ask_post_mean, last_third_ask), `{L.SRC}/table3_extra.csv`, "
                  f"`{L.SRC}/market_by_run.csv`. Script: `supplement/scripts/S42/make_06_dispersion.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
