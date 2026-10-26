"""Figure S3.8: what the seed counts can detect.

(a) Fisher's exact two-sided p for k passing runs out of n against 0 out of n, for the cell sizes in the report
    (n = 3, 6, 12). Markers are the report's pass-count contrasts of this shape, with counts taken from the run
    data (data/S3/runs.csv): GPT-5.6 Sol against GPT-6 Luna and against Grok 4.7 at the default opening (frontier
    phase, 12 runs each); Sol with Haiku buyers from $97.50 against $90 (frontier and frontier_lowanchor, 6 each);
    the pre-specified Sol test (prereg_anchor, 6 each); Gemini with messaging from $97.50 against $90
    (A_agycontrol and A_lowanchor, 3 each).
(b) D.E.'s exact permutation tests over markets (5 against 5 markets, 252 relabellings), from
    supplement/data/daniel/dg/permutation_tests.csv. The script recomputes each p from the per-market data
    (table3_extra.csv, market_by_run.csv, outcomes.csv) and refuses to draw if any differs by more than 0.001.
    The dashed line is the smallest two-sided p the design allows, 2/252.
Output: supplement/figures/S3/S3_08_resolution.png
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import fisher_exact  # noqa: E402

import s3lib  # noqa: E402

C = s3lib.COLOR
NS = [3, 6, 12]
N_STYLE = {3: (0, (1, 1.5)), 6: (0, (4, 2)), 12: "-"}
MEASURE = {"reported_seat5": "sellers reporting seat 5", "private_msgs_llm_total": "private messages",
           "public_msgs": "public messages", "ask_index": "ask index", "ask_change_post_offer": "ask change after offer",
           "suspects_test": "suspects a test"}


def fisher_p(k1, n1, k2, n2):
    return fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="two-sided")[1]


def contrasts():
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")

    def cell(**kw):
        sub = r
        for k, v in kw.items():
            sub = sub[sub[k] == v]
        return int(sub["passed"].sum()), len(sub)

    out = [
        ("Sol vs Luna", cell(block="frontier", seller="sol"), cell(block="frontier", seller="luna")),
        ("Sol vs Grok", cell(block="frontier", seller="sol"), cell(block="frontier", seller="grok")),
        ("Sol, $97.50 vs $90", cell(block="frontier", seller="sol", buyer="haiku"),
         cell(block="frontier_lowanchor", seller="sol")),
        ("pre-specified Sol test", cell(block="prereg_anchor", opening=97.5), cell(block="prereg_anchor", opening=90.0)),
        ("Gemini, $97.50 vs $90", cell(block="A_agycontrol"), cell(block="A_lowanchor", messaging="on")),
    ]
    rows = []
    for name, (k1, n1), (k2, n2) in out:
        if k2 != 0 or n1 != n2:
            raise ValueError(f"{name}: not a k of n against 0 of n contrast ({k1}/{n1} vs {k2}/{n2})")
        rows.append((name, k1, n1, fisher_p(k1, n1, k2, n2)))
    return rows


def perm_p(a, b):
    x = np.r_[a, b]
    obs = abs(a.mean() - b.mean())
    hits = total = 0
    for idx in itertools.combinations(range(len(x)), len(a)):
        m = np.zeros(len(x), bool)
        m[list(idx)] = True
        hits += abs(x[m].mean() - x[~m].mean()) >= obs - 1e-12
        total += 1
    return hits / total, total


def permutation_rows():
    dg = s3lib.DANIEL / "dg"
    pt = pd.read_csv(dg / "permutation_tests.csv")
    t3 = pd.read_csv(dg / "table3_extra.csv")
    mk = pd.read_csv(dg / "market_by_run.csv")
    oc = pd.read_csv(dg / "outcomes.csv")
    per = oc.groupby("run_id").agg(suspects_test=("suspects_test", "sum"),
                                   ask_change_post_offer=("ask_change_post_offer", "mean"))
    oc2 = oc.assign(change=oc["ask_post_mean"] - oc["ask_pre"])
    per["ask_change_alt"] = oc2.groupby("run_id")["change"].mean()
    d = t3.merge(mk[["run_id", "ask_index"]], on="run_id").merge(per, on="run_id")
    rows, nperm = [], None
    for r in pt.itertuples():
        col = r.measure
        if col == "ask_change_post_offer" and d.loc[d.arm == r.arm_a, col].isna().any():
            col = "ask_change_alt"     # Base has no offer; D.E. uses the same hour-4-to-6 change for every arm
        a = d.loc[d.arm == r.arm_a, col].to_numpy(float)
        b = d.loc[d.arm == r.arm_b, col].to_numpy(float)
        p, nperm = perm_p(a, b)
        if abs(p - r.p_two_sided) > 0.001:
            raise ValueError(f"{r.measure} {r.arm_a} vs {r.arm_b}: recomputed p {p:.3f}, CSV {r.p_two_sided}")
        rows.append((f"{MEASURE[r.measure]}, {r.arm_a} vs {r.arm_b}", p, r.measure))
    return rows, nperm


def main():
    s3lib.setup()
    cs = contrasts()
    prow, nperm = permutation_rows()
    floor = 2 / nperm
    fig = plt.figure(figsize=(s3lib.SLOT_IN, 8.4))
    axa = fig.add_axes([0.125, 0.665, 3.0 / s3lib.SLOT_IN, 0.3])
    axb = fig.add_axes([0.5, 0.075, 0.47, 0.475])

    # (a)
    for n in NS:
        ks = np.arange(1, n + 1)
        ps = [fisher_p(k, n, 0, n) for k in ks]
        axa.plot(ks, ps, color=s3lib.GRAY, ls=N_STYLE[n], lw=1.3, zorder=2, label=f"n = {n} per cell")
    axa.axhline(0.05, color=s3lib.LIGHT, lw=1.0, zorder=1)
    col = {"Sol vs Luna": C["sol"], "Sol vs Grok": C["sol"], "pre-specified Sol test": C["sol"],
           "Gemini, $97.50 vs $90": C["gemini"]}
    for name, k, n, p in cs:
        axa.plot(k, p, "o", ms=8, mfc=col.get(name, C["sol"]), mec="white", mew=0.8, zorder=4)
    axa.set_yscale("log")
    axa.set_ylim(3e-7, 1.6)
    axa.set_yticks([1e-6, 1e-4, 1e-2, 1])
    axa.legend(loc="lower left", frameon=False, fontsize=12, handlelength=2.6, labelspacing=0.25, borderaxespad=0.2)
    axa.set_yticklabels(["10⁻⁶", "10⁻⁴", "0.01", "1"])
    axa.minorticks_off()
    axa.set_xlim(0.5, 12.5)
    axa.set_xticks([1, 3, 6, 9, 12])
    axa.set_xlabel("Passing runs in the better cell (k of n)")
    axa.set_ylabel("Fisher exact p")
    s3lib.panel_letter(axa, "a", x=-0.2, y=1.0)
    # Number each contrast marker (top to bottom) and list the contrasts in a column right of the panel.
    lab = {}
    for name, k, n, p in cs:
        lab.setdefault((k, n, round(p, 6)), []).append(name)
    spots = sorted(lab.items(), key=lambda kv: -kv[0][2])
    if len(spots) != 4:
        raise ValueError(f"expected 4 distinct contrast points, found {len(spots)}")
    for i, (((k, n, p), names), fy) in enumerate(zip(spots, (0.93, 0.7, 0.47, 0.24)), start=1):
        axa.annotate(str(i), xy=(k, p), xytext=(5, 4), textcoords="offset points", ha="left", va="bottom",
                     fontsize=12, fontweight="bold")
        axa.text(1.08, fy, f"{i}", transform=axa.transAxes, ha="left", va="center", fontsize=12,
                 fontweight="bold")
        axa.text(1.15, fy, f"{', '.join(names)}\n{k}/{n} vs 0/{n}, p = {s3lib.fmt_p(p)}", transform=axa.transAxes,
                 ha="left", va="center", fontsize=12)
    axa.text(12.4, 0.062, "p = 0.05", ha="right", va="bottom", fontsize=12, color=s3lib.GRAY)

    # (b)
    ys = np.arange(len(prow))
    axb.axvline(floor, color=s3lib.GRAY, ls=(0, (5, 3)), lw=1.0, zorder=1)
    axb.axvline(0.05, color=s3lib.LIGHT, lw=1.0, zorder=1)
    for y, (name, p, meas) in zip(ys, prow):
        axb.plot(p, y, "o", ms=7.5, mfc=C["gemini"] if p <= 0.05 else "white", mec=C["gemini"], mew=1.3, zorder=3)
        axb.text(-0.02, y, name, transform=axb.get_yaxis_transform(), ha="right", va="center", fontsize=12)
    axb.set_xscale("log")
    axb.set_xlim(0.005, 1.4)
    axb.set_xticks([0.01, 0.05, 0.2, 1.0])
    axb.set_xticklabels(["0.01", "0.05", "0.2", "1"])
    axb.set_ylim(len(prow) - 0.4, -1.4)
    axb.set_yticks([])
    axb.spines["left"].set_visible(False)
    axb.set_xlabel("Permutation p, 5 vs 5 markets")
    axb.text(floor * 1.12, -1.05, f"floor 2/{nperm}", ha="left", va="center", fontsize=12, color=s3lib.GRAY)
    s3lib.panel_letter(axb, "b", x=-0.99, y=1.0)

    # Caption numbers
    for n in NS:
        print(f"n={n}: smallest p (n of n vs 0 of n) {fisher_p(n, n, 0, n):.2g}; smallest k with p<0.05: "
              f"{min((k for k in range(1, n + 1) if fisher_p(k, n, 0, n) < 0.05), default=None)}")
    for name, k, n, p in cs:
        print(f"{name}: {k}/{n} vs 0/{n}, p = {p:.4f}")
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    hrs = pd.read_csv(s3lib.S3DATA / "hours.csv")
    late = hrs[hrs.hour >= 11].groupby("folder")["mean_ask"].mean()
    pre = r[r.block == "prereg_anchor"].assign(late=lambda d: d.folder.map(late))
    diffs = np.array([pre[(pre.seed == sd) & (pre.opening == 97.5)].late.iloc[0]
                      - pre[(pre.seed == sd) & (pre.opening == 90.0)].late.iloc[0] for sd in sorted(pre.seed.unique())])
    pats = list(itertools.product([1, -1], repeat=len(diffs)))
    sf = np.mean([abs((diffs * np.array(sg)).mean()) >= abs(diffs.mean()) - 1e-12 for sg in pats])
    print(f"pre-specified primary endpoint: {len(diffs)} paired differences, mean {diffs.mean():+.2f}, sign-flip p "
          f"{sf:.4f} over {len(pats)} patterns; floor 2/{len(pats)} = {2 / len(pats):.4f}")
    print(f"permutations {nperm}, floor {floor:.4f}; tests {len(prow)}; at floor "
          f"{sum(abs(p - floor) < 1e-9 for _, p, _ in prow)}; p <= 0.05: {sum(p <= 0.05 for _, p, _ in prow)}")
    for name, p, _ in prow:
        print(f"  {name}: {p:.3f}")
    s3lib.save(fig, "S3_08_resolution.png")


if __name__ == "__main__":
    main()
