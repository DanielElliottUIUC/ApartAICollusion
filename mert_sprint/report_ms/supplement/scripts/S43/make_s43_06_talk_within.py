"""S43.6: private messages against the last-third ask index, across and within seller models.

The 18 frontier runs with messaging on (data/s43/s43_runs.csv, phase frontier, messaging on): 6 Sol, 6 Luna,
6 Grok. Private messages = all seller-to-seller private messages in the run (unified.log seller_dms, equal to
collusion_metrics.json dm_summary.total). Spearman rho; exact two-sided p over all 720 orderings of the 6 runs
within a model. These tests were chosen after looking at the data (report_ms/pro_checks.md, item 4).
Output: figures/S43/S43_06_talk_within.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_06_talk_within.png"
MODELS = ["sol", "luna", "grok"]
ZERO_SHIFT = {"luna": -2.2, "sol": 2.2}        # sideways offset of runs with 0 messages, for legibility


def make():
    L.setup()
    on = L.frontier36()
    on = on[on.messaging == "on"]
    if len(on) != 18:
        raise ValueError("expected 18 messaging-on frontier runs")
    rho_all = spearmanr(on.private_messages, on.ask_index).correlation
    st = {m: L.spearman_exact(on[on.seller == m].private_messages, on[on.seller == m].ask_index)
          for m in ["sol", "grok"]}

    fig = plt.figure(figsize=(L.SLOT_IN, 6.9))
    ax1 = fig.add_axes([0.125, 0.585, 0.85, 0.37])
    ax2 = fig.add_axes([0.125, 0.085, 0.36, 0.37])
    ax3 = fig.add_axes([0.615, 0.085, 0.36, 0.37])

    def dots(ax, g, m, xshift=0.0):
        for _, r in g.iterrows():
            x = r.private_messages + (ZERO_SHIFT.get(m, 0.0) if r.private_messages == 0 else 0.0) + xshift
            ax.plot(x, r.ask_index, "o", ms=7.5, mec=L.COLOR[m], mew=1.5, zorder=3,
                    mfc=L.COLOR[m] if r.passed else "white")

    # (a) all 18
    L.ref_lines(ax1, unit="index", which=(90.0, 95.0))
    for m in MODELS:
        dots(ax1, on[on.seller == m], m)
    ax1.set_xlim(-8, 122)
    ax1.set_ylim(-0.9, 0.85)
    ax1.set_yticks([-0.5, 0, 0.5])
    ax1.set_xlabel("Private messages between sellers per run")
    ax1.set_ylabel("Ask index, hours 11 to 15")
    ax1.text(20, 0.78, f"all {len(on)} runs, rho = {L.num(rho_all)}", ha="left", va="top", fontsize=12)
    for m, (x, y, ha) in {"sol": (9, 0.43, "left"), "luna": (6, -0.55, "left"),
                          "grok": (98, -0.6, "right")}.items():
        ax1.text(x, y, L.NAME[m], ha=ha, va="center", fontsize=12, color=L.COLOR[m], fontweight="bold")
    L.panel_letter(ax1, "a", x=-0.1, y=1.0)

    # (b) Grok and (c) Sol, each on its own scale
    for ax, m, letter in [(ax2, "grok", "b"), (ax3, "sol", "c")]:
        g = on[on.seller == m].sort_values("ask_index")
        # runs that share a message count are offset sideways by 0.6 so that close markers stay visible
        shift = g.groupby("private_messages").cumcount().to_numpy() - (g.groupby("private_messages")
                                                                          .private_messages.transform("size")
                                                                          .to_numpy() - 1) / 2
        unit = 0.6 if m == "grok" else 3.0
        for (_, r), s in zip(g.iterrows(), shift):
            ax.plot(r.private_messages + s * unit, r.ask_index, "o", ms=7.5, mec=L.COLOR[m], mew=1.5,
                    zorder=3, mfc=L.COLOR[m] if r.passed else "white")
        rho, p, k, n = st[m]
        ax.set_xlabel("Private messages per run")
        L.panel_letter(ax, letter, x=-0.2, y=1.0)
        ax.text(0.03, 1.0, f"{L.NAME[m]}, 6 runs\nrho = {L.num(rho)}, exact p = {L.num(p, 3)}",
                transform=ax.transAxes, ha="left", va="top", fontsize=12, color=L.shade(L.COLOR[m], 0.2))
    ax2.set_xlim(102, 114)
    ax2.set_xticks([104, 108, 112])
    ax2.set_ylim(-0.9, 0.25)
    ax2.set_yticks([-0.8, -0.4, 0])
    L.ref_lines(ax2, unit="index", which=(90.0,))
    ax2.set_ylabel("Ask index, hours 11 to 15")
    ax3.set_xlim(-8, 90)
    ax3.set_xticks([0, 40, 80])
    ax3.set_ylim(0.15, 0.95)
    ax3.set_yticks([0.25, 0.5, 0.75])
    L.ref_lines(ax3, unit="index", which=(95.0, 97.5))
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    cnt = {m: on[on.seller == m].private_messages for m in MODELS}
    sol_zero = int((cnt["sol"] == 0).sum())
    caption = (
        "Private talk against price in the 18 frontier runs with messaging on. (a) All runs, private messages "
        "between sellers against the last-third ask index. Runs with no private messages are offset a little to "
        "either side of zero (Luna left, Sol right). (b) Grok 4.7's 6 runs and (c) GPT-5.6 Sol's 6 runs, each on "
        "its own scale, with runs that share a message count offset sideways. Filled markers meet the joint "
        f"criterion. Spearman rho, with an exact two-sided p over the {st['grok'][3]} orderings of 6 runs. Grey lines mark "
        "index 0 ($90, dashed), 0.5 ($95, dotted) and 0.75 ($97.50, thin solid).")
    shows = (
        f"Across the 18 runs the number of private messages does not rank markets by price "
        f"(rho = {L.num(rho_all)}). Luna sent {int(cnt['luna'].max())} in every run, Grok "
        f"{int(cnt['grok'].min())} to {int(cnt['grok'].max())}, and Sol 0 in {sol_zero} runs and "
        f"{int(cnt['sol'][cnt['sol'] > 0].min())} to {int(cnt['sol'].max())} in the others. Within Grok the ranks "
        f"line up (rho = {L.num(st['grok'][0])}, exact p = {L.num(st['grok'][1], 3)}), but every Grok run stays "
        f"below index 0, and within Sol the sign is the same and weaker (rho = {L.num(st['sol'][0])}, "
        f"p = {L.num(st['sol'][1], 3)}). The within-model tests were chosen after seeing the data, so they are "
        f"leads, and the figure supports only the claim across models.")
    return {"title": "Message volume does not rank markets by price", "file": FILE, "caption": caption,
            "shows": shows,
            "source": "data/s43/s43_runs.csv (phase frontier, messaging on; private_messages counted from "
                      "unified.log seller_dms and checked against dm_summary.total); the same Spearman values "
                      "appear in report_ms/pro_checks.md item 4; figure script scripts/S43/make_s43_06_talk_within.py.",
            "path": path}


if __name__ == "__main__":
    out = make()
    print(out["caption"])
    print(out["shows"])
