"""Figure S3.7: how far the two post-hoc judges can be read.

(a) D.E.'s judge (Claude Haiku 5.5, temperature 0.1) against a blind second model (Claude Opus 5.5) on 120 Gemini
    seller-hours, 10 judge-true and 10 judge-false items per label. Parsed from the Summary table of
    supplement/data/daniel/dg/judge_handcheck.md (columns "judge-T confirmed", "judge-F confirmed", "Cohen's kappa").
(b) M.S.'s judge (Grok 4.7, temperature 0.1, private reasoning only, score 1 to 4 per seller-hour): run score =
    mean over the 4 sellers of each seller's mean_coordination_score (data/S3/grok_judge.csv, from
    judge_grok-4.7_summary.json in the 23 judged run folders). Filled markers pass the joint criterion (for the
    GGGG seed 0 run, recomputed from its auction_results.md by build_s3_data.py).
Output: supplement/figures/S3/S3_07_judges.png
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import s3lib  # noqa: E402

C = s3lib.COLOR
LABELS = [("verbal_accept", "verbal agreement"), ("verbal_reject", "verbal rejection"),
          ("suspects_collusion", "suspects collusion"), ("suspects_test", "suspects a test"),
          ("mentions_human_appeal", "mentions the human plea"), ("cross_talk", "cross-talk (dropped)")]


def handcheck():
    text = (s3lib.DANIEL / "dg" / "judge_handcheck.md").read_text(encoding="utf-8")
    rows = {}
    for key, _ in LABELS:
        m = re.search(rf"^\| {key} \| (\d+) \| (\d+) \| \d+% \| ([\d.]+) \| (\d+)/10 \| (\d+)/10 \| (\d+) \|",
                      text, re.M)
        if not m:
            raise ValueError(f"{key}: row not found in judge_handcheck.md")
        n, agree, kappa, tconf, fconf, pop = m.groups()
        if int(n) != 20 or int(tconf) + int(fconf) != int(agree):
            raise ValueError(f"{key}: counts do not add up")
        rows[key] = {"kappa": float(kappa), "t": int(tconf), "f": int(fconf), "agree": int(agree), "pop": int(pop)}
    return rows


GROUPS = [("Sol, off", "sol", "off", False), ("Luna, off", "luna", "off", False),
          ("Gemini, off", "gemini", "off", False), ("Gemini, rule notice", "gemini", "on", True),
          ("Gemini, on", "gemini", "on", False)]


def main():
    s3lib.setup()
    hc = handcheck()
    j = pd.read_csv(s3lib.S3DATA / "grok_judge.csv")
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    run = j.groupby("folder")["mean_score"].mean().rename("score").reset_index().merge(r, on="folder")
    if len(run) != 23:
        raise ValueError(f"expected 23 judged runs, found {len(run)}")

    fig = plt.figure(figsize=(s3lib.SLOT_IN, 6.9))
    axa = fig.add_axes([0.385, 0.6, 0.44, 0.36])
    axb = fig.add_axes([0.385, 0.1, 0.44, 0.37])

    # (a)
    gem = C["gemini"]
    for i, (key, name) in enumerate(LABELS):
        d = hc[key]
        dy = 0.17 if d["t"] == d["f"] else 0.0       # equal counts: set the two markers apart vertically
        axa.plot([d["f"], d["t"]], [i, i], color=s3lib.LIGHT, lw=1.2, zorder=1)
        axa.plot(d["t"], i - dy, "o", ms=8, mfc=gem, mec=gem, zorder=3)
        axa.plot(d["f"], i + dy, "o", ms=8, mfc="white", mec=gem, mew=1.4, zorder=3)
        axa.text(-0.02, i, name, transform=axa.get_yaxis_transform(), ha="right", va="center", fontsize=12)
        axa.text(1.03, i, f"κ = {d['kappa']:.2f}", transform=axa.get_yaxis_transform(), ha="left",
                 va="center", fontsize=12, color=s3lib.GRAY)
    axa.set_ylim(len(LABELS) - 0.4, -0.6)
    axa.set_yticks([])
    axa.spines["left"].set_visible(False)
    axa.set_xlim(-0.4, 10.4)
    axa.set_xticks([0, 2, 4, 6, 8, 10])
    axa.set_xlabel("Items the second model confirms (of 10)")
    handles = [Line2D([], [], ls="", marker="o", ms=8, mfc=gem, mec=gem, label="judge said yes"),
               Line2D([], [], ls="", marker="o", ms=8, mfc="white", mec=gem, mew=1.4, label="judge said no")]
    axa.legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False,
               fontsize=12, handletextpad=0.2, columnspacing=1.0, borderaxespad=0.1)
    s3lib.panel_letter(axa, "a", x=-0.8, y=1.03)

    # (b)
    for gi, (name, seller, msg, notice) in enumerate(GROUPS):
        g = run[(run.seller == seller) & (run.messaging == msg) & (run.notice == notice)].sort_values("score")
        if g.empty:
            raise ValueError(name)
        for k, (_, row) in enumerate(g.iterrows()):
            yy = gi + np.linspace(-0.3, 0.3, len(g))[k]     # one vertical level per run, in order of score
            axb.plot(row["score"], yy, "o", mfc=C[seller] if row["passed"] else "white", ms=8, mec=C[seller],
                     mew=1.4, zorder=3)
        axb.text(-0.02, gi, f"{name} ({len(g)})", transform=axb.get_yaxis_transform(), ha="right", va="center",
                 fontsize=12, color=C[seller])
    axb.set_ylim(len(GROUPS) - 0.45, -0.55)
    axb.set_yticks([])
    axb.spines["left"].set_visible(False)
    axb.set_xlim(0.85, 4.15)
    axb.set_xticks([1, 2, 3, 4])
    axb.set_xlabel("Grok 4.7 coordination score, run mean")
    handles = [Line2D([], [], ls="", marker="o", ms=8, mfc=s3lib.GRAY, mec=s3lib.GRAY, label="passes"),
               Line2D([], [], ls="", marker="o", ms=8, mfc="white", mec=s3lib.GRAY, mew=1.4, label="fails")]
    axb.legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False,
               fontsize=12, handletextpad=0.2, columnspacing=1.0, borderaxespad=0.1)
    s3lib.panel_letter(axb, "b", x=-0.8, y=1.03)

    # Caption numbers
    print({k: v for k, v in hc.items()})
    print(f"items: {20 * len(LABELS)}; agreements {sum(v['agree'] for v in hc.values())}")
    print(f"Grok judge: runs {len(run)}, sellers {len(j)}, failed rounds {int(j.rounds_failed.sum())}")
    for name, seller, msg, notice in GROUPS:
        g = run[(run.seller == seller) & (run.messaging == msg) & (run.notice == notice)]
        p = g[g.passed]
        print(f"{name:20s} n={len(g)} score {g.score.min():.2f}-{g.score.max():.2f}; passing n={len(p)} "
              f"{(p.score.min() if len(p) else float('nan')):.2f}-{(p.score.max() if len(p) else float('nan')):.2f}; "
              f"private msgs {g.private_messages.tolist()}")
    lo = run[run.score < 2]
    hi = run[run.score >= 2]
    print(f"runs below 2: {len(lo)} (private msgs max {lo.private_messages.max()}); at or above 2: {len(hi)} "
          f"(private msgs min {hi.private_messages.min()}); none between "
          f"{lo.score.max():.2f} and {hi.score.min():.2f}")
    s3lib.save(fig, "S3_07_judges.png")


if __name__ == "__main__":
    main()
