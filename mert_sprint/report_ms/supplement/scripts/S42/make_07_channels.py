"""Figure S42.7: the three message channels per market, by arm.

table3_extra.csv, counted by Daniel from each LLM seller's log (scripts/extract_dg_message_counts.py):
  private_msgs_peer      private messages from one LLM seller to another
  private_msgs_to_seat5  private messages from LLM sellers to the scripted seat 5
  public_msgs            LLM seller-hours with a public message (at most 4 sellers x 15 hours = 60)
One dot per market, filled when the market meets the joint criterion; black bar: arm mean.
Output: supplement/figures/S42/S42_07_channels.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt

import s42lib as L
from s42lib import style

FILE = "S42_07_channels.png"


def make():
    style.setup()
    m = L.markets()

    def vals(col):
        return m[["arm", "seed", "passed"]].assign(value=m[col])

    cols = [
        {"values": vals("private_msgs_peer"), "xlim": (-8, 120), "xticks": [0, 50, 100],
         "xlabel": "Private messages", "title": "To sellers"},
        {"values": vals("private_msgs_to_seat5"), "xlim": (-1.2, 18), "xticks": [0, 8, 16],
         "xlabel": "Private messages", "title": "To seat 5"},
        {"values": vals("public_msgs"), "xlim": (-4, 63), "xticks": [0, 30, 60],
         "xlabel": "Seller-hours\nwith a post", "title": "Public"},
    ]
    fig, axes, rows = L.arm_dot_figure(cols, fig_h=5.3, ci=False, col_gap=0.42)
    L.save(fig, FILE)
    plt.close(fig)
    return numbers(m)


def numbers(m):
    w, nw = m[m.warn], m[~m.warn]
    pub = m.set_index("arm")["public_msgs"]
    peer = m.set_index("arm")["private_msgs_peer"]
    prec = m[m.arm.isin(["F", "G-prec"])]
    sham = m[m.arm == "F-sham"]
    if w["private_msgs_peer"].max() != 0:
        raise ValueError("the text says no warning-arm market has a seller-to-seller private message")
    return {"w_n": len(w), "peer_w_max": int(w["private_msgs_peer"].max()),
            "prec_silent": int((prec["public_msgs"] == 0).sum()), "prec_n": len(prec), "peer_nw_min": int(nw["private_msgs_peer"].min()),
            "peer_nw_max": int(nw["private_msgs_peer"].max()),
            "s5_w_min": int(w["private_msgs_to_seat5"].min()), "s5_w_max": int(w["private_msgs_to_seat5"].max()),
            "s5_nw_min": int(nw["private_msgs_to_seat5"].min()), "s5_nw_max": int(nw["private_msgs_to_seat5"].max()),
            "pub_mean": m.groupby("arm")["public_msgs"].mean(),
            "prec_pub_max": int(prec["public_msgs"].max()),
            "sham_silent": int((sham["public_msgs"] == 0).sum()),
            "p_pub_F_sham": L.perm_p(pub["F"], pub["F-sham"]),
            "p_peer_B_Gw": L.perm_p(peer["Base"], peer["G-warn"])}


def entry():
    n = make()
    pm = n["pub_mean"]
    return {
        "title": "The warning closes the private channel between sellers; the precedent also closes the public one",
        "file": FILE,
        "caption": (
            "Messages per market in D.E.'s undercover market, by channel and arm. (a) Private messages from one "
            "Gemini 3.8 Flash seller to another. (b) Private messages from the sellers to the scripted seat 5. "
            "(c) Seller-hours with a public message, out of 4 sellers x 15 hours = 60. One dot per market, "
            "filled when the market meets the joint criterion. Black bar: arm mean. Arms with the warning sit on "
            "the pale band. Per market, (a) and (b) sum over 15 hours. The main report's Figure 2a shows the "
            "arm means of (a) only."),
        "shows": (
            f"No private message passed between sellers in any of the {n['w_n']} warning-arm markets, against "
            f"{n['peer_nw_min']} to {n['peer_nw_max']} per market without the warning (Base against G-warn "
            f"p = {L.fmt_p(n['p_peer_B_Gw'])}). Messages to seat 5 are few in every arm, {n['s5_nw_min']} to "
            f"{n['s5_nw_max']} per market without the warning and {n['s5_w_min']} to {n['s5_w_max']} with it. "
            f"Public posting survives the warning alone (E {pm['E']:.1f} and G-warn {pm['G-warn']:.1f} of 60 "
            f"seller-hours per market), stops in {n['prec_silent']} of {n['prec_n']} F and G-prec markets with the "
            f"precedent, and stops in {n['sham_silent']} of 5 F-sham markets with the sham history (F against "
            f"F-sham p = {L.fmt_p(n['p_pub_F_sham'])}, exact permutation over markets)."),
        "source": f"`{L.SRC}/table3_extra.csv` (public_msgs, private_msgs_peer, private_msgs_to_seat5), "
                  f"`{L.SRC}/market_by_run.csv` (passed). Script: `supplement/scripts/S42/make_07_channels.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
