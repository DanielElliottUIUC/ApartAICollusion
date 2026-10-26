"""S41_02. When sellers first reported, and how often they reported again (Gemini, Daniel's data).

Data: supplement/data/daniel/dg/outcomes.csv (report_hour, n_reports, report_target), table3_extra.csv.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 4.55
NAME = "S41_02_report_timing.png"
ARMS = ["D", "D-hs", "D-hb", "D-hsb", "E", "F", "F-sham", "G-warn"]   # every arm with at least one report
WARN = {"E", "F", "F-sham", "G-warn"}


def make():
    style.setup()
    o = L.gemini_sellers()
    t = L.gemini_markets()
    r = o[o.reported].copy()
    if set(r.arm) != set(ARMS):
        raise ValueError(f"arms with reports: {sorted(set(r.arm))}")
    left = 16 - r.report_hour                     # hours from the first report through hour 15
    if (r.n_reports > left).any():
        raise ValueError("a seller filed more reports than hours left")
    r["cat"] = "several"
    r.loc[r.n_reports == 1, "cat"] = "once"
    r.loc[r.n_reports == left, "cat"] = "every"
    blue = style.COLOR["gemini"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    y0, y1 = 0.62, FIG_H - 0.72                    # two key rows sit above y1
    key_y = FIG_H - 0.22
    ya = fig.add_axes([1.0 / FIG_W, y0 / FIG_H, 2.45 / FIG_W, (y1 - y0) / FIG_H])
    yb = fig.add_axes([3.95 / FIG_W, y0 / FIG_H, 2.45 / FIG_W, (y1 - y0) / FIG_H], sharey=ya)
    for ax in (ya, yb):
        ax.patch.set_alpha(0)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    ys = {a: i for i, a in enumerate(ARMS)}
    ya.set_ylim(len(ARMS) - 0.5, -0.6)
    ya.set_yticks(range(len(ARMS)), ARMS)
    plt.setp(yb.get_yticklabels(), visible=False)
    wy = [ys[a] for a in ARMS if a in WARN]
    style.row_band(fig, ya, min(wy) - 0.5, max(wy) + 0.5, style.WARN_BAND)

    # (a) hour of first report
    ya.fill_between([3.5, 6.6], -0.5, len(ARMS) - 0.5, color="#EDEDED", lw=0, zorder=0)
    ya.text(4.1, ys["G-warn"], "offer visible", ha="left", va="center", fontsize=12, color=style.GRAY)
    g = r.groupby(["arm", "report_hour", "s5"]).size()
    for (arm, hour, s5), k in g.items():
        y = ys[arm]
        ya.plot(hour, y, "o", ms=8, mfc=(blue if s5 else "white"), mec=blue, mew=1.4, zorder=3)
        ya.text(hour + 0.27, y, str(k), ha="left", va="center", fontsize=12)
    ya.set_xlim(1.4, 6.6)
    ya.set_xticks(range(2, 7))
    ya.set_xlabel("Hour of first report")
    L.key_row(fig, 1.0, key_y, [("marker", dict(marker="o", ms=8, mfc=blue, mec=blue), "seat 5"),
                                ("marker", dict(marker="o", ms=8, mfc="white", mec=blue, mew=1.4), "a peer")])
    fig.text(0.05 / FIG_W, key_y / FIG_H, "a", fontsize=16, fontweight="bold", ha="left", va="center")

    # (b) reports per reporting seller, stacked counts
    cats = [("once", "once", style.tint(blue, 0.75)), ("several", "2 or more", style.tint(blue, 0.4)),
            ("every", "every hour", blue)]
    w_in = 2.45
    yb.set_xlim(0, 27)
    for arm in ARMS:
        s = r[r.arm == arm]
        x = 0
        for key, _, col in cats:
            k = int((s.cat == key).sum())
            if k:
                yb.barh(ys[arm], k, left=x, height=0.62, color=col, lw=0)
                if k * w_in / 27 >= (0.15 if k < 10 else 0.25):
                    ink = "white" if key == "every" else "black"
                    yb.text(x + k / 2, ys[arm], str(k), ha="center", va="center", fontsize=12, color=ink)
                x += k
        yb.text(x + 0.4, ys[arm], f"of {len(s)}", ha="left", va="center", fontsize=12, color=style.GRAY)
    L.key_row(fig, 3.95, key_y, [("patch", dict(facecolor=col), lab) for _, lab, col in cats[:2]])
    L.key_row(fig, 3.95, key_y - 0.27, [("patch", dict(facecolor=cats[2][2]), "every hour from the first")])
    fig.text(3.62 / FIG_W, key_y / FIG_H, "b", fontsize=16, fontweight="bold", ha="left", va="center")
    yb.set_xticks([0, 10, 20])
    yb.set_xlabel("Reporting sellers")
    L.save(fig, NAME)

    # numbers for the text
    n_rep = len(r)
    h4 = int((r.report_hour == 4).sum())
    before = r[r.report_hour < 4]
    after = r[r.report_hour > 4]
    every = r.groupby("arm").cat.apply(lambda c: int((c == "every").sum()))
    once = r.groupby("arm").cat.apply(lambda c: int((c == "once").sum()))
    nrep = r.groupby("arm").size()
    per_mkt = t.groupby("arm").reports_total.mean()
    if not set(after.arm) <= {"D-hs", "D-hsb"}:
        raise ValueError("a late first report outside the human-seller plea arms")
    if before.s5.any():
        raise ValueError("a first report before hour 4 named seat 5")
    before_txt = (f"The {len(before)} first reports before hour 4 all named a peer "
                  f"({', '.join(f'{a} {k}' for a, k in before.groupby('arm').size().items())}).")
    return {
        "id": "S41.2",
        "title": "Reports came in the first hour the offer was visible",
        "file": NAME,
        "caption": (
            "(a) Hour of each Gemini seller's first report, by arm. Filled circles are first reports that named "
            "seat 5, open circles first reports that named a peer, and the number beside each circle counts the "
            "sellers. Seat 5 sent its note at hour 3, and sellers could read it from hour 4 (gray area). "
            "(b) The same reporting sellers by how many reports each filed over the run: one, two or more, or "
            "one for every hour from the first report to hour 15. Shaded rows carry the warning. Base and "
            "G-prec had no reports and are left out."
        ),
        "shows": (
            f"Of the {n_rep} sellers who reported anyone, {h4} filed their first report in hour 4, the first "
            f"hour seat 5's message could be read. {before_txt} The other {len(after)} came in hour "
            f"{' or '.join(str(int(h)) for h in sorted(after.report_hour.unique()))}, all in the arms with the "
            f"human-seller plea. Without the warning, "
            f"many reporters kept reporting: in D, {every['D']} of {nrep['D']} filed a report in every hour from "
            f"their first, and D markets logged {per_mkt['D']:.1f} reports each, repeats included. Under the "
            f"warning and precedent (F), {once['F']} of {nrep['F']} reporters filed exactly one report, and F "
            f"markets logged {per_mkt['F']:.1f}. Reports were free and had no effect on the market, so repeat "
            f"counts measure persistence rather than strength of belief."
        ),
        "source": "supplement/data/daniel/dg/outcomes.csv (reported, report_hour, n_reports, "
                  "report_is_scripted_seat), table3_extra.csv (reports_total).",
    }


if __name__ == "__main__":
    print(make())
