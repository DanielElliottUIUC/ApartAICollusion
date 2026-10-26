"""Figure 1 (offer), variant with two GPT-4.1 rows added to panel b.

Same as report_ms/scripts/figures/make_fig1_offer.py (which is not edited; report_ms is written only by the
shard 2 session), except panel b has five rows:
  Gemini D, GPT-4.1 D, GPT-4.1 F (warning and precedent), GPT-4.1 D at $99, Haiku D.
Sources (Daniel's data):
  GPT-4.1 F: report_ms/data/daniel/dg_gpt41/outcomes_by_arm.csv row F (report 12/12, echo 0/12, reject 8/12).
  GPT-4.1 $99: data/dg_gpt41_99_outcomes.csv, a copy of report/data/dg_gpt41_99/outcomes.csv from Daniel's
  PR #41 (identical on report-v2). Rows arm == D99: reported_seat5 (1 of 12); rose_ge_1 (0 of 12 raised asks
  by $1 or more in hours 4 to 6); tone_all_msgs (10 of 10 messages to seat 5 declining, hand coded).
  The judge was not run on D99, so its two judge columns show the hand read instead, marked as such.
Output: figures_extra/fig1_offer_gpt41/fig1_offer_gpt41.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "report_ms" / "scripts" / "lib"))
sys.path.insert(0, str(REPO / "report_ms" / "scripts" / "figures"))

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.transforms import blended_transform_factory

import load
import style
import make_fig1_offer as f1

B_ROWS = 5
B_Y0, B_Y1 = 0.10, 0.10 + 0.44 * B_ROWS
SHIFT = (B_Y1 - f1.B_Y1)          # panel (a) moves up by the extra height of panel (b)
FIG_H = f1.FIG_H + SHIFT


def d99_counts():
    d = pd.read_csv(HERE / "data" / "dg_gpt41_99_outcomes.csv")
    e = d[d["arm"] == "D99"]
    tones = [t for cell in e["tone_all_msgs"].dropna() for t in str(cell).split(";")]
    return {"n": len(e), "reported": int(e["reported_seat5"].sum()), "rose": int(e["rose_ge_1"].sum()),
            "declining": sum(t == "declining" for t in tones), "msgs": len(tones)}


def panel_b_rows():
    base = {r["short"]: r for r in f1.panel_b_data()}
    o = load.daniel_outcomes("dg_gpt41").loc["F"]
    n = int(o["n_seller_episodes"])
    f_row = {"family": "gpt41", "short": "GPT-4.1,\nprecedent", "n": n,
             "reported": load.count(o["report_is_scripted_seat_rate"], n),
             "agreed": load.count(o["verbal_accept_rate"], n),
             "rejected": load.count(o["verbal_reject_rate"], n)}
    d = d99_counts()
    d99_row = {"family": "gpt41", "short": "GPT-4.1,\noffer $99", "n": d["n"], "reported": d["reported"],
               "d99": d}
    g = dict(base["Gemini"]); g["short"] = "Gemini"
    gd = dict(base["GPT-4.1"]); gd["short"] = "GPT-4.1"
    h = dict(base["Haiku 5.5"])
    return [g, gd, f_row, d99_row, h]


def main():
    style.setup()
    a_data, b_rows = f1.panel_a_data(), panel_b_rows()
    rows, heads, (w0, w1) = style.arm_rows()
    blue = style.COLOR["gemini"]
    fig = plt.figure(figsize=(f1.FIG_W, FIG_H))
    f1.FIG_H = FIG_H                              # columns() places axes in figure fractions of FIG_H

    a_y0, a_y1 = f1.A_Y0 + SHIFT, f1.A_Y1 + SHIFT
    spans = []
    for group, _ in style.ARM_GROUPS:
        ys = [y for g, _, y in rows if g == group]
        spans.append((ys[0] - 0.5, ys[-1] + 0.5))
    axa, wa = f1.columns(fig, 2, a_y0, a_y1, spans)
    axa[0].set_ylim(rows[-1][2] + 0.5, 0.0)
    style.row_band(fig, axa[0], w0, w1, style.WARN_BAND)
    axa[0].set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    axa[0].tick_params(axis="y", pad=(f1.X0 - f1.LAB_X) * 72)
    lab_tr = blended_transform_factory(fig.transFigure, axa[0].transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        axa[0].text(0.06 / f1.FIG_W, y, group, transform=lab_tr, ha="left", va="center", fontsize=12,
                    fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY))
    for ax, kind in zip(axa, ("reported", "agreed")):
        for _, arm, y in rows:
            d = a_data[arm]
            f1.bar(ax, wa, y, d[kind], d["n"], blue, str(d[kind]))
            if kind == "reported" and arm in style.NO_OFFER:
                ax.text(0.11, y, "no offer", ha="left", va="center", fontsize=12, fontstyle="italic",
                        color=style.GRAY)
        f1.head(ax, f1.HEAD[kind])
    fig.text(0.06 / f1.FIG_W, (a_y1 + 0.64) / FIG_H, "a", fontsize=16, fontweight="bold", ha="left", va="bottom")
    fig.text(0.40 / f1.FIG_W, (a_y1 + 0.64) / FIG_H, "Gemini 3.8 Flash sellers by arm, of 20", fontsize=16,
             ha="left", va="bottom")

    axb, wb = f1.columns(fig, 3, B_Y0, B_Y1, [(0.0, float(B_ROWS))])
    yb = [i + 0.5 for i in range(B_ROWS)]
    axb[0].set_ylim(float(B_ROWS), 0.0)
    axb[0].set_yticks(yb, [f"{r['short']}\nn = {r['n']}" if "\n" not in r["short"] else r["short"]
                           for r in b_rows])
    axb[0].tick_params(axis="y", pad=(f1.X0 - f1.LAB_X) * 72, labelsize=12)
    for ax, kind in zip(axb, ("reported", "agreed", "rejected")):
        for r, y in zip(b_rows, yb):
            if "d99" in r and kind != "reported":
                d = r["d99"]
                text = (f"{d['rose']} of {d['n']} raised asks\n(hand read)" if kind == "agreed"
                        else f"{d['declining']} of {d['msgs']} declined\n(hand read)")
                ax.text(0.02, y, text, ha="left", va="center", fontsize=12, fontstyle="italic", color="black")
                continue
            f1.bar(ax, wb, y, r[kind], r["n"], style.COLOR[r["family"]], f"{r[kind]} of {r['n']}")
        f1.head(ax, f1.HEAD_B[kind])
    fig.text(0.06 / f1.FIG_W, (B_Y1 + 0.90) / FIG_H, "b", fontsize=16, fontweight="bold", ha="left", va="bottom")
    fig.text(0.40 / f1.FIG_W, (B_Y1 + 0.90) / FIG_H, "The offer to three seller families, and GPT-4.1 variants",
             fontsize=16, ha="left", va="bottom")
    fig.savefig(HERE / "fig1_offer_gpt41.png", dpi=style.DPI)


if __name__ == "__main__":
    main()
