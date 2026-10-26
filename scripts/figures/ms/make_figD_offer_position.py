"""Appendix figure: where the $96 offer sat in each seller family's market, arm D, seller by seller (M.S.'s S41_05).

Adapted from M.S.'s mert_sprint/report_ms/supplement/scripts/S41/make_s41_05_offer_position.py, with its loaders
in mert_sprint/report_ms/supplement/scripts/lib/s41_lib.py (gemini_sellers, family_sellers), ref
origin/mert_sprint_sync_oct25, by M.S.: same panels, data and encodings (each line joins one seller's ask at hour 3,
when seat 5 sends the offer, to its mean ask over hours 11 to 15; a point is filled when the seller's first report
named seat 5; black line: the offer; grey lines: $90 dashed, $95 dotted, the $97.50 opening thin solid). Changes:
drawn at its print size, 6.5 x 2.8 in, with every text 8.5 pt or more (his was 6.5 x 4.2 in at 12 pt); the
sideways spread of the points is a little wider (uniform +-0.13 instead of +-0.09, same generator seed) so the
Gemini points hide each other less; within each family the rarer marker (filled or open) is drawn on top, so the
one Gemini seller who did not report seat 5 is not hidden under the 19 who did (new sprint code); the family names
in the headers are the report's.

Inputs (committed): report/data/dg/outcomes.csv, dg_gpt41/outcomes.csv, dg_haiku/outcomes.csv (ask_pre = the
seller's ask at hour 3, last_third_ask = its mean ask over hours 11 to 15, report_is_scripted_seat), arm D rows;
GPT-4.1 Base rows of dg_gpt41/outcomes.csv for the caption. With --results-dir (the raw runs, results/, not in the
repository), every plotted ask is re-derived from the runs' round records, and seat 5's own asks are read per family
for the caption; the script stops on any difference.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/ms/make_figD_offer_position.py --results-dir <repo>/results
Output: report/figures/figD_offer_position.png (6.5 x 2.8 in, 300 dpi) and figD_offer_position.caption.txt
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import style  # noqa: E402

DATA = style.REPO / "report" / "data"
NAME = "figD_offer_position"
FIG_W, FIG_H = style.SLOT_IN, 2.8
OFFER = 96.0
FAMILIES = [("dg", "gemini", "Gemini 3.8 Flash"), ("dg_gpt41", "gpt41", "GPT-4.1"),
            ("dg_haiku", "haiku", "Claude Haiku 5.5")]
XS = [0.0, 2.3, 4.6]
JIT = 0.13
MS = 4.8
WORDS = {k: w for k, w in enumerate(["None", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                                     "Ten", "Eleven", "Twelve"])}


def load(fam):
    o = pd.read_csv(DATA / fam / "outcomes.csv")
    m = pd.read_csv(DATA / fam / "market_by_run.csv")
    o = o.merge(m[["run_id", "scripted_seats"]], on="run_id", how="left", validate="many_to_one")
    o["s5"] = o.report_is_scripted_seat.astype(bool)
    if not (o.s5 == (o.report_target == o.scripted_seats)).all():
        raise ValueError(f"{fam}: report_is_scripted_seat disagrees with report_target")
    return o


def check_raw(fam, o, results: Path):
    """Re-derive ask_pre and last_third_ask from the raw round records; return seat 5's asks by arm."""
    sys.path.insert(0, str(style.REPO / "src"))
    from apartcollusion.runs import find_runs
    runs = {r.run_id: r for r in find_runs(results / fam, warn=lambda m: None)}
    for _, x in o.iterrows():
        r = runs[x.run_id]
        late = [a for a in (r.ask(x.seller_id, h) for h in range(11, 16)) if a is not None]
        if abs(r.ask(x.seller_id, 3) - x.ask_pre) > 1e-9 or abs(np.mean(late) - x.last_third_ask) > 1e-9:
            raise ValueError(f"{fam} {x.run_id} {x.seller_id}: CSV and raw asks disagree")
    import json
    for run_id, g in o[o.arm == "D"].groupby("run_id"):
        rep = json.loads((results / fam / run_id / "collusion_metrics.json").read_text(encoding="utf-8"))
        named = {x["from"] for x in rep["regulator_reports"] if x["about"] == g.scripted_seats.iloc[0]}
        if named != set(g[g.s5].seller_id):
            raise ValueError(f"{fam} {run_id}: sellers with any report naming seat 5 differ from first reports")
    paths = {}
    for r in runs.values():
        p = tuple(r.ask(next(iter(r.scripted_seats)), h) for h in range(1, 16))
        if paths.setdefault(r.arm, p) != p:
            raise ValueError(f"{fam} {r.arm}: seat-5 path differs between runs")
    print(f"raw check {fam}: {len(o)} sellers in {len(runs)} runs match; seat-5 paths {paths}")
    return paths


def build(fams):
    style.setup()
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    x0, x1, y0, y1 = 0.62, 5.15, 0.62, 2.36
    ax = fig.add_axes([x0 / FIG_W, y0 / FIG_H, (x1 - x0) / FIG_W, (y1 - y0) / FIG_H])
    for r in style.REF_LINES:
        ax.axhline(r["price"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    ax.axhline(OFFER, color="black", lw=1.3, zorder=1)
    rng = np.random.default_rng(0)
    for (fam, key, label, d), xg in zip(fams, XS):
        col = style.COLOR[key]
        jit = rng.uniform(-JIT, JIT, len(d))
        rare_filled = 2 * int(d.s5.sum()) < len(d)      # the rarer marker kind is drawn on top
        for (_, r), j in zip(d.iterrows(), jit):
            ax.plot([xg + j, xg + 1 + j], [r.ask_pre, r.last_third_ask], color=col, lw=0.8, alpha=0.6, zorder=2)
            z = 3.5 if bool(r.s5) == rare_filled else 3
            for xx, yy in ((xg + j, r.ask_pre), (xg + 1 + j, r.last_third_ask)):
                ax.plot(xx, yy, "o", ms=MS, mfc=(col if r.s5 else "white"), mec=col, mew=1.0, zorder=z)
        ax.text(xg + 0.5, 99.3, f"{label}\n{int(d.s5.sum())} of {len(d)} reported seat 5", ha="center",
                va="bottom", fontsize=style.FS, linespacing=1.15)
    ax.set_xlim(-0.45, 6.05)
    ax.set_ylim(83.2, 99.0)
    ax.set_xticks([x + k for x in XS for k in (0, 1)], ["hour 3", "hours\n11 to 15"] * 3)
    ax.set_yticks([85, 90, 95])
    ax.set_yticklabels(["$85", "$90", "$95"])
    ax.set_ylabel("Seller's ask")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    for y, dy, lab, c in ((OFFER, 0.0, "offer $96", "black"), (97.5, 0.45, "opening $97.50", style.GRAY),
                          (95.0, -0.45, "$95", style.GRAY), (90.0, 0.0, "$90", style.GRAY)):
        ax.text(6.15, y + dy, lab, ha="left", va="center", color=c, clip_on=False)
    # key, bottom left
    ky = 0.12
    kx = x0
    rend = fig.canvas.get_renderer()
    for filled, lab in ((True, "reported seat 5 (first report)"), (False, "did not")):
        fig.add_artist(plt.Line2D([(kx + 0.06) / FIG_W], [ky / FIG_H], transform=fig.transFigure, ls="none",
                                  marker="o", ms=MS, mfc=(style.GRAY if filled else "white"), mec=style.GRAY,
                                  mew=1.0))
        t = fig.text((kx + 0.16) / FIG_W, ky / FIG_H, lab, ha="left", va="center")
        kx += 0.16 + t.get_window_extent(rend).width / fig.dpi + 0.25
    out = style.save(fig, f"{NAME}.png", max_h_in=FIG_H)
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results-dir", type=Path, default=None, help="raw runs (results/) for the cross-check")
    args = ap.parse_args()
    data = {fam: load(fam) for fam, _, _ in FAMILIES}
    paths = {}
    if args.results_dir is not None:
        for fam, _, _ in FAMILIES:
            paths[fam] = check_raw(fam, data[fam], args.results_dir)
    else:
        print("no --results-dir: raw-log cross-check skipped")
    fams = [(fam, key, label, data[fam][data[fam].arm == "D"]) for fam, key, label in FAMILIES]
    out = build(fams)

    st = {}
    for fam, key, label, d in fams:
        st[key] = dict(n=len(d), lo=d.ask_pre.min(), hi=d.ask_pre.max(), pre=d.ask_pre.mean(),
                       late_lo=d.last_third_ask.min(), late_hi=d.last_third_ask.max(), late=d.last_third_ask.mean(),
                       rep=int(d.s5.sum()), near96=int((abs(d.last_third_ask - OFFER) <= 0.03).sum()))
        print(key, {k: round(v, 3) for k, v in st[key].items()})
    gb = data["dg_gpt41"][data["dg_gpt41"].arm == "Base"]
    base_lo, base_hi = gb.last_third_ask.min(), gb.last_third_ask.max()
    base_spread = gb.groupby("run_id").last_third_ask.agg(lambda v: v.max() - v.min()).max()
    q_d = fams[1][3]
    print(f"GPT-4.1 Base hours 11-15: {base_lo:.3f} to {base_hi:.3f} (n={len(gb)})")
    g, q, h = st["gemini"], st["gpt41"], st["haiku"]
    seat5 = ""
    if paths:
        def two(fam):
            p = paths[fam]["D"]
            if any(a != OFFER for a in p[2:]):
                raise ValueError(f"{fam}: seat 5 does not hold $96 from hour 3")
            return f"${p[0]:.2f} and ${p[1]:.2f}"
        seat5 = (f" In hours 1 and 2 seat 5 asked {two('dg')} (Gemini), {two('dg_gpt41')} (GPT-4.1) and "
                 f"{two('dg_haiku')} (Haiku), each family's own replayed path, and $96 from hour 3 in all three.")
    caption = (
        "Figure D5. Arm D, the plain $96 offer, put to three seller families. Each line joins one seller's ask at hour 3, "
        "when seat 5 sent the offer, to its mean ask over hours 11 to 15; filled points mark sellers whose first "
        "report named seat 5, and points are spread sideways so they hide each other less. Black line: the offer; "
        "grey lines: $90 (dashed), $95 (dotted) and the $97.50 opening (thin). Hour-3 asks ran "
        f"${g['lo']:.2f} to ${g['hi']:.2f} for Gemini, ${q['lo']:.2f} to ${q['hi']:.2f} for GPT-4.1 and "
        f"${h['lo']:.2f} to ${h['hi']:.2f} for Haiku, so the offer sat at about the going price for the first two "
        f"and about ${OFFER - h['pre']:.0f} above it for Haiku. {WORDS[q['near96']]} of {q['n']} GPT-4.1 sellers "
        f"ended hours 11 to 15 within $0.03 of $96, but GPT-4.1 Base sellers, who got no offer, also ended at "
        f"${base_lo:.2f} to ${base_hi:.2f}, in lockstep within each market (within ${base_spread:.2f}), so ending "
        "near $96 is not evidence of holding the offer."
        + seat5 +
        " Each family has its own seat-5 path and 3 to 5 markets, and there is no Haiku Base arm, so the comparison "
        "is qualitative. (Figure: M.S.)"
    )
    near = q_d[(q_d.last_third_ask - OFFER).abs() <= 0.03]
    details = (
        "Made by scripts/figures/ms/make_figD_offer_position.py, an adapted copy of M.S.'s "
        "mert_sprint/report_ms/supplement/scripts/S41/make_s41_05_offer_position.py with lib/s41_lib.py "
        f"(ref origin/mert_sprint_sync_oct25), at print size {out['width_in']} x {out['height_in']} in, 300 dpi "
        f"({out['px'][0]} x {out['px'][1]} px), smallest text {out['min_font_pt']} pt. Appendix D.2, next to Table D3.\n"
        "Numbers printed, checked: headers, sellers whose first report named seat 5 (outcomes.csv "
        f"report_is_scripted_seat, arm D): Gemini {g['rep']} of {g['n']}, GPT-4.1 {q['rep']} of {q['n']}, Haiku "
        f"{h['rep']} of {h['n']}; these equal the any-report counts of Table D3 (19/20, 0/12, 3/12; with --results-dir the script checks that, in arm D, the sellers with any "
        "report naming seat 5 in the raw regulator_reports are exactly these). Reference labels $96, $97.50, $95, $90 are constants. Plotted points: ask_pre "
        "and last_third_ask from report/data/{dg,dg_gpt41,dg_haiku}/outcomes.csv"
        + (", each re-derived from the raw round records with --results-dir (all 272 seller-episodes matched)"
           if paths else "")
        + f". Caption: hour-3 ranges as stated; GPT-4.1 D sellers within $0.03 of $96 over hours 11 to 15: "
        + ", ".join(f"seed {x.seed} {x.seller_id.replace('Seller ', '')} ${x.last_third_ask:.3f}"
                    for _, x in near.iterrows())
        + f"; GPT-4.1 Base hours 11 to 15 ${base_lo:.3f} to ${base_hi:.3f} (largest within-market spread "
        f"${base_spread:.3f}); Haiku mean hour-3 ask ${h['pre']:.2f} (offer ${OFFER - h['pre']:.2f} above).\n"
        "Regenerate: cd third_party/llm-agent-collusion && PYTHONUTF8=1 uv run python "
        "../../scripts/figures/ms/make_figD_offer_position.py --results-dir C:/Users/danie/Hackathons/ApartAICollusion/results"
    )
    (style.FIGURES / f"{NAME}.caption.txt").write_text(caption + "\n\n" + details + "\n", encoding="utf-8")
    print(caption)
    print(out)


if __name__ == "__main__":
    main()
