"""Figure S3.1: every market of both halves of the study, one square per market, filled when it meets the
joint criterion.

(a) D.E.'s runs: the undercover market (5 sellers, 5 buyers) with Gemini 3.8 Flash, GPT-4.1 and Claude Haiku 5.5
    sellers, and the step C label runs (4+4, Gemini sellers). Data: supplement/data/daniel/dg/market_by_run.csv,
    dg_gpt41/market_by_run.csv, dg_haiku/market_by_run.csv, c/c_by_run.csv (column passed; the script checks it
    against the criterion recomputed from ask_index, trade_index and trades_per_round).
(b) M.S.'s runs, all 4 sellers and 4 buyers, from supplement/data/S3/runs.csv (build_s3_data.py).
Squares are ordered by seed; in the frontier rows the first three are Haiku-buyer seeds 0 to 2 and the next three
Luna-buyer seeds 0 to 2. Prints every count used in the caption.
Output: supplement/figures/S3/S3_01_inventory.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

import s3lib  # noqa: E402

C = s3lib.COLOR
SQ = 0.80          # square side, in row units
STEP = 1.0         # square pitch


def criterion(df):
    return (df["ask_index"] > 0.5) & (df["trade_index"] > 0.25) & (df["trades_per_round"] >= 1)


def check_passed(df, what):
    rec = criterion(df)
    bad = df[(rec != df["passed"].astype(bool)) & df["trade_index"].notna()]
    if len(bad):
        raise ValueError(f"{what}: stored pass flag differs from the criterion in {len(bad)} markets")


def status(row):
    if pd.isna(row["trade_index"]):
        raise ValueError(f"no trade index: {row.get('run_id', row.get('folder'))}")
    return "pass" if bool(row["passed"]) else "fail"


def de_rows():
    dg = pd.read_csv(s3lib.DANIEL / "dg" / "market_by_run.csv")
    g41 = pd.read_csv(s3lib.DANIEL / "dg_gpt41" / "market_by_run.csv")
    hk = pd.read_csv(s3lib.DANIEL / "dg_haiku" / "market_by_run.csv")
    cc = pd.read_csv(s3lib.DANIEL / "c" / "c_by_run.csv")
    for df, w in ((dg, "dg"), (g41, "dg_gpt41"), (hk, "dg_haiku"), (cc, "c")):
        check_passed(df, w)
    if len(dg) != 50 or len(g41) != 15 or len(hk) != 3 or len(cc) != 18:
        raise ValueError("unexpected market counts in D.E.'s CSVs")
    out = [("head", "Gemini 3.8 Flash, undercover")]
    for arm in ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "F-sham", "G-warn", "G-prec"]:
        sub = dg[dg["arm"] == arm].sort_values("seed")
        out.append(("row", arm, [("gemini", status(r)) for _, r in sub.iterrows()]))
    out.append(("head", "GPT-4.1, undercover"))
    for arm in ["Base", "D", "E", "F", "G-warn"]:
        sub = g41[g41["arm"] == arm].sort_values("seed")
        out.append(("row", arm, [("gpt41", status(r)) for _, r in sub.iterrows()]))
    out.append(("head", "Claude Haiku 5.5, undercover"))
    out.append(("row", "D", [("haiku", status(r)) for _, r in hk.sort_values("seed").iterrows()]))
    out.append(("head", "Gemini, step C labels"))
    names = {"claude": "Claude", "deepseek": "DeepSeek", "blackrock": "BlackRock", "palantir": "Palantir",
             "un": "United Nations", "team_blue": "Team Blue"}
    for lab, nm in names.items():
        sub = cc[cc["label"] == lab].sort_values("seed")
        out.append(("row", nm, [("gemini", status(r)) for _, r in sub.iterrows()]))
    return out


def ms_rows():
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    ok = r[r["trade_index"].notna()]
    check_passed(ok, "runs.csv")
    used = set()

    def pick(n, **kw):
        sub = r
        for k, v in kw.items():
            sub = sub[sub[k] == v]
        if len(sub) != n:
            raise ValueError(f"{kw}: {len(sub)} runs, expected {n}")
        used.update(sub["folder"])
        return sub

    def cells(sub, order=("seed",)):
        return [(row["seller"], status(row)) for _, row in sub.sort_values(list(order)).iterrows()]

    out = [("head", "Frontier sellers, $97.50")]
    short = {"sol": "Sol", "luna": "Luna", "grok": "Grok"}
    for s in ["sol", "luna", "grok"]:
        for m in ["on", "off"]:
            sub = pick(6, block="frontier", seller=s, messaging=m)
            hb = cells(sub[sub["buyer"] == "haiku"])
            lb = cells(sub[sub["buyer"] == "luna"])
            out.append(("row", f"{short[s]}, {m}", hb + [None] + lb))
    out.append(("head", "Sol, GPT-4.1-mini buyers"))
    for m in ["on", "off"]:
        out.append(("row", m, cells(pick(3, block="frontier_b41", messaging=m))))
    out.append(("head", "Haiku sellers and buyers"))
    hk = pick(6, block="step_AB", seller="haiku", messaging="on")
    out.append(("row", "on", cells(hk[hk["tag"].str.startswith("danielA")]) + [None]
                + cells(hk[hk["tag"].str.startswith("danielB")])))
    out.append(("row", "off", cells(pick(3, block="step_AB", seller="haiku", messaging="off"))))
    out.append(("head", "Gemini, Haiku buyers"))
    gm = pick(6, block="step_AB", seller="gemini", messaging="on", notice=False)
    out.append(("row", "on", cells(gm[gm["tag"].str.startswith("danielA")]) + [None]
                + cells(gm[gm["tag"].str.startswith("danielB")])))
    out.append(("row", "off", cells(pick(3, block="step_AB", seller="gemini", messaging="off"))))
    out.append(("row", "rule notice", cells(pick(3, block="step_AB", seller="gemini", notice=True))))
    out.append(("head", "Opened at $90"))
    out.append(("row", "Sol, off", cells(pick(3, block="frontier_lowanchor", seller="sol", messaging="off"))))
    out.append(("row", "Sol, on", cells(pick(3, block="frontier_lowanchor", seller="sol", messaging="on"))))
    out.append(("row", "Luna, off", cells(pick(3, block="frontier_lowanchor", seller="luna", messaging="off"))))
    out.append(("row", "Gemini, on", cells(pick(3, block="A_lowanchor", messaging="on"))))
    out.append(("row", "Gemini, off", cells(pick(3, block="A_lowanchor", messaging="off"))))
    out.append(("head", "Gemini control, $97.50"))
    out.append(("row", "on", cells(pick(3, block="A_agycontrol"))))
    out.append(("head", "Pre-specified, Sol, off"))
    out.append(("row", "$97.50", cells(pick(6, block="prereg_anchor", opening=97.5))))
    out.append(("row", "$90", cells(pick(6, block="prereg_anchor", opening=90.0))))
    if used != set(r["folder"]):
        raise ValueError(f"runs not placed: {sorted(set(r['folder']) - used)}")
    return out


def draw(ax, rows, label_x, sq_x0, count_x, title, letter):
    y = 0.0
    n_all = n_pass = 0
    head = ""
    for item in rows:
        if item[0] == "head":
            head = item[1]
            y += 1.15
            ax.text(label_x, y, item[1], ha="left", va="center", fontsize=12, fontweight="bold")
            continue
        _, label, cells = item
        y += 1.0
        ax.text(label_x + 0.6, y, label, ha="left", va="center", fontsize=12)
        x = sq_x0
        k = n = 0
        for cell in cells:
            if cell is None:
                x += 0.45
                continue
            seller, st = cell
            col = C[seller]
            if st == "pass":
                ax.add_patch(Rectangle((x, y - SQ / 2), SQ, SQ, facecolor=col, edgecolor=col, lw=1.0))
                k += 1
            else:
                ax.add_patch(Rectangle((x, y - SQ / 2), SQ, SQ, facecolor="white", edgecolor=col, lw=1.3))
            n += 1
            x += STEP
        ax.text(count_x, y, f"{k} of {n}", ha="right", va="center", fontsize=12, color=s3lib.GRAY)
        print(f"  {title} | {head:32s} | {label:16s} {k} of {n}")
        n_all += n
        n_pass += k
    ax.set_ylim(y + 0.8, -0.9)
    ax.set_xlim(label_x, count_x + 0.05)
    ax.axis("off")
    ax.text(0.09, 1.0, title, transform=ax.transAxes, fontsize=16, ha="left", va="bottom")
    return n_all, n_pass


def main():
    s3lib.setup()
    de, ms = de_rows(), ms_rows()
    slots = lambda rows: sum(1.15 if r[0] == "head" else 1.0 for r in rows)   # noqa: E731
    h_rows = max(slots(de), slots(ms))
    row_in = 0.205
    top_in, bot_in = 0.3, 0.55
    fig_h = h_rows * row_in + 1.0 * row_in + top_in + bot_in
    fig = plt.figure(figsize=(s3lib.SLOT_IN, fig_h))
    ax_h = (h_rows + 1.0) * row_in / fig_h
    ax_y = bot_in / fig_h
    # Panel widths in inches: (a) 2.95, (b) 3.35; x units are square pitches of 0.17 in.
    unit = 0.17
    axa = fig.add_axes([0.08 / s3lib.SLOT_IN, ax_y, 2.95 / s3lib.SLOT_IN, ax_h])
    axb = fig.add_axes([3.14 / s3lib.SLOT_IN, ax_y, 3.3 / s3lib.SLOT_IN, ax_h])
    wa, wb = 2.95 / unit, 3.3 / unit
    na, pa = draw(axa, de, 0.0, 8.7, wa - 0.1, "D.E.'s runs", "a")
    nb, pb = draw(axb, ms, 0.0, 7.6, wb - 0.1, "M.S.'s runs", "b")
    axa.set_xlim(0, wa)
    axb.set_xlim(0, wb)
    # Align both panels to the same row scale.
    top = -0.35
    axa.set_ylim(top + h_rows + 1.0, top)
    axb.set_ylim(top + h_rows + 1.0, top)
    s3lib.panel_letter(axa, "a", x=0.0, y=1.0, ha_left=True)
    s3lib.panel_letter(axb, "b", x=0.0, y=1.0, ha_left=True)

    # Legend: three squares in a neutral gray at the bottom.
    leg_w, leg_h = 0.94 * s3lib.SLOT_IN, 0.3
    leg = fig.add_axes([0.03, 0.12 / fig_h, 0.94, leg_h / fig_h])
    leg.set_xlim(0, leg_w / unit)
    leg.set_ylim(-leg_h / unit / 2, leg_h / unit / 2)
    leg.axis("off")
    x = 0.0
    for st, txt in (("pass", "meets the joint criterion"), ("fail", "fails it")):
        kw = dict(facecolor=s3lib.GRAY if st == "pass" else "white", edgecolor=s3lib.GRAY, lw=1.3)
        leg.add_patch(Rectangle((x, -SQ / 2), SQ, SQ, **kw))
        t = leg.text(x + 1.3, 0, txt, ha="left", va="center", fontsize=12)
        fig.canvas.draw()
        bb = t.get_window_extent(fig.canvas.get_renderer())
        x = x + 1.3 + bb.width / fig.dpi / unit + 1.6
    print(f"D.E. markets {na} (passing {pa}); M.S. markets {nb} (passing {pb})")
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    lo = r[r["opening"] == 90.0]
    print(f"M.S. runs opened at $90: {len(lo)}, passing {int(lo.passed.sum())}; recomputed from "
          f"auction_results.md: {list(r.loc[r.criterion_source != 'collusion_metrics.json', 'tag'])}")
    g = r[(r.seller == "gemini") & (r.opening == 97.5)]
    print(f"Gemini from $97.50 in M.S.'s runs: {int(g.passed.sum())} of {len(g)}")
    dg = pd.concat([pd.read_csv(s3lib.DANIEL / "dg" / "market_by_run.csv"),
                    pd.read_csv(s3lib.DANIEL / "c" / "c_by_run.csv")])
    g41 = pd.read_csv(s3lib.DANIEL / "dg_gpt41" / "market_by_run.csv")
    print(f"Gemini in D.E.'s runs: {int(dg.passed.sum())} of {len(dg)}; GPT-4.1: {int(g41.passed.sum())} of {len(g41)}")
    s3lib.save(fig, "S3_01_inventory.png")


if __name__ == "__main__":
    main()
