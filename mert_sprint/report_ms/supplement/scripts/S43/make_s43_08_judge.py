"""S43.8: the Grok 4.7 judge's coordination score against the last-third ask index, for the 23 judged runs.

Runs with judge_grok-4.7_summary.json (data/s43/s43_runs.csv, judge_mean not empty): Sol and Luna frontier runs
with messaging off (Haiku or Luna buyers) and Gemini step A and B runs with Haiku buyers (messaging on, off, or
on with the prohibition notice). x is the run mean of the four sellers' mean scores (1 = very low or no
coordination, 4 = very high), y the last-third ask index; filled markers pass the joint criterion.
Output: figures/S43/S43_08_judge.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_08_judge.png"
# group key -> (label, marker)
GROUPS = {
    ("sol", "off"): ("Sol, off", "o"),
    ("luna", "off"): ("Luna, off", "o"),
    ("gemini", "off"): ("Gemini, off", "o"),
    ("gemini", "notice"): ("Gemini, notice", "^"),
    ("gemini", "on"): ("Gemini, on", "s"),
}


def group(r):
    return (r.seller, "notice" if r.notice else r.messaging)


def make():
    L.setup()
    df = L.runs()
    j = df[df.judge_mean.notna()].copy()
    j["g"] = [group(r) for r in j.itertuples()]
    if len(j) != 23 or set(j.g) != set(GROUPS):
        raise ValueError(f"judged runs: {len(j)}, groups {set(j.g)}")

    from matplotlib.lines import Line2D
    lo_max = j[j.judge_mean < 2].judge_mean.max()
    hi_min = j[j.judge_mean >= 2].judge_mean.min()
    fig = plt.figure(figsize=(L.SLOT_IN, 5.4))
    axl = fig.add_axes([0.125, 0.27, 0.55, 0.7])
    axr = fig.add_axes([0.725, 0.27, 0.25, 0.7], sharey=axl)
    for ax in (axl, axr):
        L.ref_lines(ax, unit="index", which=(90.0, 95.0))
        for g, (label, mk) in GROUPS.items():
            c = L.COLOR[g[0]]
            for r in j[j.g == g].itertuples():
                ax.plot(r.judge_mean, r.ask_index, mk, ms=8.5 if mk != "^" else 9.5, mec=c, mew=1.5,
                        zorder=3, mfc=c if r.passed else "white", alpha=0.95)
    axl.set_xlim(0.97, lo_max + 0.06)
    axr.set_xlim(hi_min - 0.08, 4.02)
    axl.set_xticks([1.0, 1.1, 1.2, 1.3])
    axr.set_xticks([3.5, 4.0])
    axl.set_ylim(-0.92, 0.92)
    axl.set_yticks([-0.5, 0, 0.5])
    axl.set_ylabel("Ask index, hours 11 to 15")
    axr.spines["left"].set_visible(False)
    axr.tick_params(axis="y", left=False, labelleft=False)
    for ax, xs in ((axl, (1.0,)), (axr, (0.0,))):         # break marks on the x axis
        for x0 in xs:
            ax.plot([x0 - 0.012, x0 + 0.012], [-0.025, 0.025], transform=ax.transAxes, color="black",
                    lw=0.9, clip_on=False)
    fig.text(0.55, 0.165, "Grok 4.7 judge, mean coordination score (1 to 4)", ha="center", va="center",
             fontsize=14)
    handles = []
    for g, (label, mk) in GROUPS.items():
        handles.append(Line2D([], [], ls="none", marker=mk, ms=8.5 if mk != "^" else 9.5, mew=1.5,
                              mec=L.COLOR[g[0]], mfc=L.COLOR[g[0]], label=f"{label} ({int((j.g == g).sum())})"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.55, -0.01), ncol=3, frameon=False,
               fontsize=12, handletextpad=0.3, columnspacing=1.0)
    axl.text(lo_max + 0.05, -0.86, "filled: meets the criterion", ha="right", va="bottom", fontsize=12,
             color=L.GRAY)
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    rng = {g: (j[j.g == g].judge_mean.min(), j[j.g == g].judge_mean.max()) for g in GROUPS}
    k = {g: int(j[j.g == g].passed.sum()) for g in GROUPS}
    n = {g: int((j.g == g).sum()) for g in GROUPS}
    low = j[j.judge_mean < 2]
    hi = j[j.judge_mean >= 2]
    luna = j[j.g == ("luna", "off")]
    rec = j[j.criterion_source.str.startswith("recomputed")]
    vol = j[(j.trades_per_round < 1)]
    caption = (
        f"The Grok 4.7 judge's score against price for the {len(j)} runs it scored. The judge read each "
        f"seller-hour's private reflection, plan and notes and scored coordination from 1 (very low or none) to 4 "
        f"(very high). The horizontal axis is the run mean, broken where no run scored (between "
        f"{L.num(lo_max)} and {L.num(hi_min)}), and the vertical axis is the last-third ask index. Filled markers "
        f"meet the joint criterion. Circles have messaging off, squares messaging on, and triangles are Gemini "
        f"runs with messaging on and a prohibition notice, with run counts in brackets. Sol and Luna runs are "
        f"frontier runs with Haiku or Luna buyers, and Gemini runs are step A and B runs with Haiku buyers. "
        f"{int(j.judge_hours_failed.sum())} of {int(j.judge_hours_scored.sum() + j.judge_hours_failed.sum())} "
        f"seller-hours got no score and are left out. Gemini GGGG seed {int(rec.seed.iloc[0])} is recomputed "
        f"from auction_results.md, and GGGG seed {int(vol.seed.iloc[0])} fails on volume. The dotted line is "
        f"index 0.5 ($95) and the dashed line index 0 ($90).")
    shows = (
        f"The score separates runs where sellers talked from runs where they did not, and not high prices from "
        f"low ones. Gemini runs with messaging scored {L.num(rng[('gemini', 'on')][0])} to "
        f"{L.num(rng[('gemini', 'on')][1])}, and the other {len(low)} runs scored {L.num(low.judge_mean.min())} "
        f"to {L.num(low.judge_mean.max())} while their ask indices ran from {L.num(low.ask_index.min())} to "
        f"{L.num(low.ask_index.max())}, with {int(low.passed.sum())} passes. Sol and Luna without messaging score "
        f"alike ({L.num(rng[('sol', 'off')][0])} to {L.num(rng[('sol', 'off')][1])} and "
        f"{L.num(rng[('luna', 'off')][0])} to {L.num(rng[('luna', 'off')][1])}), yet Sol passes "
        f"{k[('sol', 'off')]} of {n[('sol', 'off')]} and Luna never rises above {L.num(luna.ask_index.max())}. The "
        f"judge was not checked against a second judge, and seller model and messaging change together between "
        f"the two clusters, so the figure is descriptive.")
    if not (len(rec) == 1 and len(vol) == 1 and len(hi) == n[("gemini", "on")]):
        raise ValueError("text assumptions no longer hold")
    return {"title": "A reasoning judge scores talk, not price", "file": FILE, "caption": caption,
            "shows": shows,
            "source": "data/s43/s43_runs.csv, judge columns from judge_grok-4.7_summary.json and "
                      "llm_eval_grok-4.7.json in each judged folder (experiments/runs/shard2/frontier/*nocomms*, "
                      "experiments/runs/shard3/A/*gemini*, experiments/runs/shard3/B/*GGGG*); figure script "
                      "scripts/S43/make_s43_08_judge.py.",
            "path": path}


if __name__ == "__main__":
    out = make()
    print(out["caption"])
    print(out["shows"])
