"""Appendix figure: the hour of each Gemini seller's first report, by arm (panel a of M.S.'s S41_02).

Adapted from M.S.'s mert_sprint/report_ms/supplement/scripts/S41/make_s41_02_report_timing.py, with its loader
mert_sprint/report_ms/supplement/scripts/lib/s41_lib.py (gemini_sellers), ref origin/mert_sprint_sync_oct25, by
M.S.: same encoding (one circle per arm, hour and target, filled when the first report named seat 5, open when it
named a peer; the number beside a circle counts the sellers; grey area: hours in which the offer or note is
visible; pale yellow rows: arms with the warning in the prompt). Changes: panel a only (his panel b, how often each
reporter reported again, is dropped); drawn at its print size, 6.5 x 2.8 in, with every text at least 8 pt (his
was 6.5 x 4.55 in at 12 to 16 pt); a right-hand column reconciles the two report counts used in the report: sellers
whose *first* report named seat 5 (this figure, outcomes.csv report_is_scripted_seat) and sellers with *any* report
naming seat 5 (Table D2a, table3_extra.csv reported_seat5).

Inputs (committed): report/data/dg/outcomes.csv (reported, report_hour, report_target, report_is_scripted_seat),
market_by_run.csv (scripted_seats), table3_extra.csv (reported_seat5). With --runs-dir (the raw Gemini runs,
results/dg, not in the repository), every reporting seller's first-report hour and target, and every per-arm count,
are re-derived from each run's collusion_metrics.json regulator_reports and must match.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/ms/make_figD_report_timing.py --runs-dir <repo>/results/dg
Output: report/figures/figD_report_timing.png (6.5 x 2.8 in, 300 dpi) and figD_report_timing.caption.txt
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

import style  # noqa: E402

DATA = style.REPO / "report" / "data" / "dg"
NAME = "figD_report_timing"
FIG_W, FIG_H = style.SLOT_IN, 2.8
ARMS = ["D", "D-hs", "D-hb", "D-hsb", "E", "F", "F-sham", "G-warn"]   # every arm with at least one report
WARN = {"E", "F", "F-sham", "G-warn"}
NO_OFFER = {"G-warn"}
OFFER_HOUR = 3
AX_X0, AX_X1 = 0.62, 4.55          # inches
AX_Y0, AX_Y1 = 0.40, 2.30
COL_FIRST, COL_ANY = 5.18, 6.02    # centers of the two count columns, inches
MS = 6.5                           # marker size, points
WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}


def sellers():
    """The 200 Gemini seller-episodes with s5 (first report names seat 5) and ever_s5 (any report names seat 5).
    M.S.'s s41_lib.gemini_sellers, reading the committed CSVs."""
    o = pd.read_csv(DATA / "outcomes.csv")
    m = pd.read_csv(DATA / "market_by_run.csv")
    t = pd.read_csv(DATA / "table3_extra.csv")
    o = o.merge(m[["run_id", "scripted_seats"]], on="run_id", how="left", validate="many_to_one")
    if len(o) != 200 or o.scripted_seats.isna().any():
        raise ValueError("expected 200 Gemini seller-episodes, each with a scripted seat")
    o["reported"] = o.reported.astype(bool)
    o["s5"] = o.report_is_scripted_seat.astype(bool)
    if not (o.s5 == (o.report_target == o.scripted_seats)).all():
        raise ValueError("report_is_scripted_seat disagrees with report_target")
    first = o.groupby("run_id").s5.sum()
    deficit = t.set_index("run_id").reported_seat5 - first
    if (deficit < 0).any():
        raise ValueError("table3 count below the first-report count")
    o["ever_s5"] = o.s5
    for run, k in deficit[deficit > 0].items():
        cand = o.index[(o.run_id == run) & o.reported & ~o.s5]
        if len(cand) != k:
            raise ValueError(f"{run}: cannot place {k} later seat-5 reports on {len(cand)} peer reporters")
        o.loc[cand, "ever_s5"] = True
    return o


def check_raw(o, runs_dir: Path):
    """Re-derive first-report hour, target and repeat count, and any-report-names-seat-5, from the raw runs."""
    n = 0
    for (run, seller), g in o[o.reported].groupby(["run_id", "seller_id"]):
        rep = json.loads((runs_dir / run / "collusion_metrics.json").read_text(encoding="utf-8"))["regulator_reports"]
        mine = sorted((r for r in rep if r["from"] == seller), key=lambda r: r["round"])
        x = g.iloc[0]
        if not mine or mine[0]["round"] != x.report_hour or mine[0]["about"] != x.report_target \
                or len(mine) != x.n_reports or any(r["about"] == x.scripted_seats for r in mine) != x.ever_s5:
            raise ValueError(f"{run} {seller}: CSV and raw regulator_reports disagree")
        n += 1
    for run in o.run_id.unique():
        rep = json.loads((runs_dir / run / "collusion_metrics.json").read_text(encoding="utf-8"))["regulator_reports"]
        if {r["from"] for r in rep} != set(o[(o.run_id == run) & o.reported].seller_id):
            raise ValueError(f"{run}: reporters differ between CSV and raw run")
    print(f"raw check: {n} reporting sellers in {o.run_id.nunique()} runs match {runs_dir}")


def build(o):
    style.setup()
    r = o[o.reported].copy()
    if set(r.arm) != set(ARMS):
        raise ValueError(f"arms with reports: {sorted(set(r.arm))}")
    blue = style.COLOR["gemini"]
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([AX_X0 / FIG_W, AX_Y0 / FIG_H, (AX_X1 - AX_X0) / FIG_W, (AX_Y1 - AX_Y0) / FIG_H])
    ax.patch.set_alpha(0)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ys = {a: i for i, a in enumerate(ARMS)}
    ax.set_ylim(len(ARMS) - 0.5, -0.5)
    ax.set_yticks(range(len(ARMS)), ARMS)
    wy = [ys[a] for a in ARMS if a in WARN]
    style.row_band(fig, ax, min(wy) - 0.5, max(wy) + 0.5, style.WARN_BAND)

    x_lo, x_hi = 0.5, 6.7
    ax.fill_between([OFFER_HOUR + 0.5, x_hi], -0.5, len(ARMS) - 0.5, color="#EDEDED", lw=0, zorder=0)
    ax.text(OFFER_HOUR + 0.62, ys["G-warn"], "offer or note visible", ha="left", va="center", color=style.GRAY)
    g = r.groupby(["arm", "report_hour", "s5"]).size()
    for (arm, hour, s5), k in g.items():
        y = ys[arm]
        ax.plot(hour, y, "o", ms=MS, mfc=(blue if s5 else "white"), mec=blue, mew=1.2, zorder=3)
        ax.text(hour + 0.17, y, str(k), ha="left", va="center")
    ax.set_xlim(x_lo, x_hi)
    ax.set_xticks(range(1, 7))
    ax.set_xlabel("Hour of the seller's first report", labelpad=2)

    # key, above the plot
    ky = AX_Y1 + 0.30
    rend = fig.canvas.get_renderer()
    t = fig.text(0.05 / FIG_W, ky / FIG_H, "First report named:", ha="left", va="center")
    kx = 0.05 + t.get_window_extent(rend).width / fig.dpi + 0.12
    for filled, label in ((True, "seat 5"), (False, "another seller")):
        fig.add_artist(plt.Line2D([(kx + 0.06) / FIG_W], [ky / FIG_H], transform=fig.transFigure, ls="none",
                                  marker="o", ms=MS, mfc=(blue if filled else "white"), mec=blue, mew=1.2))
        t = fig.text((kx + 0.17) / FIG_W, ky / FIG_H, label, ha="left", va="center")
        kx += 0.17 + t.get_window_extent(rend).width / fig.dpi + 0.22
    fig.patches.append(plt.Rectangle(((kx + 0.02) / FIG_W, (ky - 0.07) / FIG_H), 0.20 / FIG_W, 0.14 / FIG_H,
                                     transform=fig.transFigure, facecolor=style.WARN_BAND, edgecolor="none"))
    fig.text((kx + 0.29) / FIG_W, ky / FIG_H, "warning arms", ha="left", va="center")

    # right-hand column: sellers (of 20) whose first report named seat 5, and with any report naming seat 5
    first = r.groupby("arm").s5.sum().reindex(ARMS).astype(int)
    anyr = o.groupby("arm").ever_s5.sum().reindex(ARMS).astype(int)
    tr = matplotlib.transforms.blended_transform_factory(fig.transFigure, ax.transData)
    fig.text((COL_FIRST + COL_ANY) / 2 / FIG_W, (AX_Y1 + 0.30) / FIG_H, "Sellers naming seat 5, of 20",
             ha="center", va="center", fontsize=style.FS_HEAD)
    for x, lab in ((COL_FIRST, "first report"), (COL_ANY, "any report")):
        fig.text(x / FIG_W, (AX_Y1 + 0.10) / FIG_H, lab, ha="center", va="center", color=style.GRAY)
    for arm in ARMS:
        for x, v in ((COL_FIRST, first[arm]), (COL_ANY, anyr[arm])):
            diff = first[arm] != anyr[arm]
            ax.text(x / FIG_W, ys[arm], str(v), transform=tr, ha="center", va="center",
                    fontweight=("bold" if diff else "normal"))
    out = style.save(fig, f"{NAME}.png", max_h_in=FIG_H)
    plt.close(fig)
    return r, first, anyr, out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", type=Path, default=None, help="raw Gemini runs (results/dg) for the cross-check")
    args = ap.parse_args()
    o = sellers()
    if args.runs_dir is not None:
        check_raw(o, args.runs_dir)
    else:
        print("no --runs-dir: raw-log cross-check skipped")
    r, first, anyr, out = build(o)

    cells = r.groupby(["arm", "report_hour", "s5"]).size()
    print("cells (arm, hour, names seat 5): count")
    print(cells.to_string())
    early = r[r.report_hour <= OFFER_HOUR].sort_values(["arm", "seed"])
    late = r[r.s5 & (r.report_hour > OFFER_HOUR + 1)]
    if early.s5.any():
        raise ValueError("a first report before the offer was visible named seat 5")
    if not set(late.arm) <= {"D-hs", "D-hsb"}:
        raise ValueError("a late seat-5 first report outside the human-seller plea arms")
    s5_first = r[r.s5]
    h4 = int((s5_first.report_hour == OFFER_HOUR + 1).sum())

    def who(x):
        later = "later reported seat 5" if x.ever_s5 else "never reported seat 5"
        return f"{x.arm} seed {x.seed}, {x.seller_id.replace('Seller ', '')}, hour {int(x.report_hour)}, {later}"
    early_txt = "; ".join(who(x) for _, x in early.iterrows())
    print("first reports before the offer was visible:", early_txt)
    diff = [a for a in ARMS if first[a] != anyr[a]]
    caption = (
        "Figure D2. Hour of each Gemini seller's first report to the regulator, by arm; the number beside a circle counts "
        "sellers. Filled: the first report named seat 5; open: it named another LLM seller. Seat 5 sends the "
        f"offer or neutral note at hour {OFFER_HOUR} and sellers see it from hour {OFFER_HOUR + 1} (grey). Of "
        f"{len(s5_first)} sellers whose first report named seat 5, {h4} filed it in hour {OFFER_HOUR + 1} and "
        f"{len(late)} in hour {' or '.join(str(int(h)) for h in sorted(late.report_hour.unique()))} "
        f"({', '.join(f'{a} {k}' for a, k in late.groupby('arm').size().items())}). The circles count first reports ("
        + ", ".join(f"{a} {first[a]}" for a in diff)
        + "); the right-hand column, like Table D2a, also counts any report naming seat 5 ("
        + ", ".join(f"{a} {anyr[a]}" for a in diff)
        + f"). {WORDS[len(early)]} sellers first reported a peer before the offer was visible ({early_txt}). Base and G-prec had "
        "no reports and are left out; shaded rows carry the warning. (Figure: M.S.)"
    )
    cell_txt = "; ".join(f"{a} hour {int(h)} {'seat 5' if s5 else 'peer'} {k}" for (a, h, s5), k in cells.items())
    details = (
        "Made by scripts/figures/ms/make_figD_report_timing.py, an adapted copy of M.S.'s "
        "mert_sprint/report_ms/supplement/scripts/S41/make_s41_02_report_timing.py with lib/s41_lib.py "
        f"(ref origin/mert_sprint_sync_oct25), panel a only, at print size {out['width_in']} x {out['height_in']} in, "
        f"300 dpi ({out['px'][0]} x {out['px'][1]} px), smallest text {out['min_font_pt']} pt. Appendix D.1, after "
        "Table D2.\n"
        "Numbers printed, checked: circles (arm, hour of first report, target: sellers), from "
        f"report/data/dg/outcomes.csv: {cell_txt}. First report names seat 5 (report_is_scripted_seat, checked "
        "against report_target = market_by_run.csv scripted_seats): "
        + ", ".join(f"{a} {first[a]}" for a in ARMS)
        + "; any report names seat 5 (table3_extra.csv reported_seat5, = Table D2a): "
        + ", ".join(f"{a} {anyr[a]}" for a in ARMS)
        + ". With --runs-dir, every reporting seller's first-report hour, target and report count and every "
        "any-report-names-seat-5 flag were re-derived from collusion_metrics.json regulator_reports of the 50 raw "
        "runs and matched (120 reporting sellers). The five pre-offer peer reports match the D.1 'Pleas' paragraph "
        "(D-hb hour 2, D-hsb hour 2, E two at hour 3, G-warn hour 2).\n"
        "Regenerate: cd third_party/llm-agent-collusion && PYTHONUTF8=1 uv run python "
        "../../scripts/figures/ms/make_figD_report_timing.py --runs-dir C:/Users/danie/Hackathons/ApartAICollusion/results/dg"
    )
    (style.FIGURES / f"{NAME}.caption.txt").write_text(caption + "\n\n" + details + "\n", encoding="utf-8")
    print(pd.DataFrame({"first": first, "any": anyr, "reporters": r.groupby("arm").size().reindex(ARMS)}).to_string())
    print(caption)
    print(out)


if __name__ == "__main__":
    main()
