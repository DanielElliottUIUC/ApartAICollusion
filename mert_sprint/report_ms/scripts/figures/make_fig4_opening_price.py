"""Figure 4: prices stay where the market opens (our runs).

(a) Mean seller ask by hour, default $97.50 opening, frontier phase (36 runs): GPT-5.6 Sol, GPT-6 Luna and
    Grok 4.7 sellers, messaging on (solid) and off (dash-dot); each line is the mean over 6 runs
    (2 buyer models x 3 seeds).
(b) The low-anchor test. Gemini 3.8 Flash sellers with GPT-4.1-mini buyers, served through the Antigravity CLI:
    messaging on from $97.50 (A_agycontrol, 3 runs) and messaging on and off from $90 (A_lowanchor, 3 runs
    each). GPT-5.6 Sol sellers with Claude Haiku 5.5 buyers from $90, messaging on and off
    (frontier_lowanchor, 3 runs each). Two private messages from one $90 Gemini run (seed 0, Seller Kai) are
    pinned at the hour they were sent; their full text is in data/ms_quotes.csv and each call-out is checked
    to be a verbatim substring of it.
In (a) and (b) each line is the mean of avg_seller_asks_by_round over its runs (data/ms_runs.csv,
ask_h1..ask_h15).
(c) The pre-specified paired test (protocol report_ms/prereg_sol_anchor.md; runs in data/ms_prereg.csv, built
    from experiments/runs/shard2/prereg_anchor/): Sol sellers, Haiku 5.5 buyers, messaging off, seeds 3 to 8,
    each seed opened once at $97.50 and once at $90. One line per seed from its $97.50 run to its $90 run;
    y is the primary endpoint, the mean of avg_seller_asks_by_round over hours 11 to 15. A marker is filled
    when the run passes the joint criterion. The bracket spans the two arm means (dotted guides join each
    mean to its column) and gives the mean paired difference and the exact two-sided sign-flip p over the 2^6 sign patterns, both computed here
    (they reproduce report_ms/prereg_result.md).
Reference lines: $90 dashed, $95 (ask index 0.5) dotted, $97.50 opening thin solid.
Slot: full width, 6.5 in.  Output: report/figures/fig4_opening_price.png
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
import numpy as np

import load
import style

QUOTE_RUN = "experiments/runs/shard2/A_lowanchor/20261025_191318_danielA_L90_gemini_comms_gpt41miniB-seed0"
CALLOUTS = [  # hour, verbatim fragment (at most 8 words), text anchor (hour, $), line break after word k,
              # point of the text box the leader leaves from (fraction of width, height)
    (1, "let's keep our asks closely aligned around $90", (1.35, 92.85), 4, (0.0, 0.0)),
    (12, "Our price coordination is completely rock solid.", (6.6, 90.55), 4, (0.84, 0.0)),
]
SHORT = {"sol": "Sol", "luna": "Luna", "grok": "Grok"}
LABEL_X = 15.75

FIG_H = 8.75
AX_X0, AX_X1 = 0.81, 4.68               # left and right edge of all three panels, inches
PANEL_Y = {"a": (6.36, 8.36), "b": (3.34, 5.59), "c": (0.62, 2.29)}     # bottom, top, inches
LATE = [f"ask_h{h}" for h in range(11, 16)]     # the primary endpoint: hours 11 to 15
GUIDE = "#9A9A9A"                               # dotted guides from each arm's mean to the bracket in (c)


def mean_path(df):
    return df[load.ASK_COLS].mean(axis=0).to_numpy()


def pick(runs, phase, seller, messaging, opening, n):
    sub = runs[(runs["phase"] == phase) & (runs["seller"] == seller) & (runs["messaging"] == messaging)
               & (runs["opening_price"] == opening)]
    if len(sub) != n:
        raise ValueError(f"{phase} {seller} {messaging} {opening}: {len(sub)} runs, expected {n}")
    return mean_path(sub)


def prereg_pairs():
    """Per seed: primary endpoint and pass flag at each opening, from data/ms_prereg.csv."""
    df = load.ms_prereg()
    df = df.assign(primary=df[LATE].mean(axis=1))
    pairs = []
    for seed in sorted(df["seed"].unique()):
        hi = df[(df["seed"] == seed) & (df["opening_price"] == 97.5)]
        lo = df[(df["seed"] == seed) & (df["opening_price"] == 90.0)]
        if len(hi) != 1 or len(lo) != 1 or (df.loc[df["seed"] == seed, "messaging"] != "off").any():
            raise ValueError(f"seed {seed}: expected one messaging-off run at each opening")
        pairs.append({"seed": int(seed), "hi": hi["primary"].iloc[0], "lo": lo["primary"].iloc[0],
                      "hi_pass": bool(hi["passed"].iloc[0]), "lo_pass": bool(lo["passed"].iloc[0])})
    if [p["seed"] for p in pairs] != [3, 4, 5, 6, 7, 8]:
        raise ValueError("expected seeds 3 to 8")
    return pairs


def sign_flip_p(diffs):
    """Exact two-sided paired sign-flip test: share of the 2^n sign patterns whose |mean| reaches the observed."""
    obs = abs(np.mean(diffs))
    hits = sum(abs(np.mean([s * d for s, d in zip(signs, diffs)])) >= obs - 1e-12
               for signs in itertools.product((1, -1), repeat=len(diffs)))
    return hits, 2 ** len(diffs)


def panel_c(ax):
    pairs = prereg_pairs()
    c = style.COLOR["sol"]
    style.ref_lines(ax)
    for p in pairs:
        ax.plot([0, 1], [p["hi"], p["lo"]], color=c, lw=1.4, zorder=2, solid_capstyle="round")
        for x, y, ok in ((0, p["hi"], p["hi_pass"]), (1, p["lo"], p["lo_pass"])):
            ax.plot([x], [y], ls="none", marker="o", ms=7, mew=1.4, mec=c, mfc=(c if ok else "white"), zorder=3)
    hi_mean = np.mean([p["hi"] for p in pairs])
    lo_mean = np.mean([p["lo"] for p in pairs])
    diffs = [p["hi"] - p["lo"] for p in pairs]
    hits, n = sign_flip_p(diffs)
    print(f"(c) mean at $97.50 {hi_mean:.3f}, at $90 {lo_mean:.3f}, mean difference {np.mean(diffs):+.3f}, "
          f"{sum(d > 0 for d in diffs)} of {len(diffs)} positive, sign-flip p = {hits}/{n}")

    # bracket between the two arm means, each joined to its column by a dotted guide, with the test result
    xb = 1.27
    ax.plot([xb - 0.04, xb, xb, xb - 0.04], [lo_mean, lo_mean, hi_mean, hi_mean], color="black", lw=0.9,
            clip_on=False, zorder=4)
    for x, m in ((0.06, hi_mean), (1.06, lo_mean)):
        ax.plot([x, xb - 0.04], [m, m], color=GUIDE, lw=0.9, ls=(0, (1, 1.6)), zorder=1)
    mid = (lo_mean + hi_mean) / 2
    ax.text(xb + 0.06, mid + 0.35, f"+${np.mean(diffs):.2f}", ha="left", va="bottom", fontsize=14,
            fontweight="bold", clip_on=False)
    ax.text(xb + 0.06, mid + 0.15, f"mean difference,\n{sum(d > 0 for d in diffs)} of {len(diffs)} seeds "
            f"higher,\np = {hits / n:.3f} ({hits}/{n})", ha="left", va="top", fontsize=12, clip_on=False,
            linespacing=1.2)

    n_hi, n_lo = sum(p["hi_pass"] for p in pairs), sum(p["lo_pass"] for p in pairs)
    ax.set_xlim(-0.32, 1.32)
    ax.set_xticks([0, 1], [f"Opened at $97.50\n{n_hi} of {len(pairs)} pass",
                           f"Opened at $90\n{n_lo} of {len(pairs)} pass"])
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(88.0, 98.4)
    ax.set_yticks([88, 90, 92, 94, 96])
    ax.set_ylabel("Mean ask ($)")
    ax.set_title("Pre-specified Sol test, hours 11 to 15", pad=6)


def main():
    style.setup()
    runs = load.ms_runs()
    hours = load.HOURS

    fig = plt.figure(figsize=(style.SLOT_IN, FIG_H))
    ax_a, ax_b, ax_c = (fig.add_axes([AX_X0 / style.SLOT_IN, y0 / FIG_H, (AX_X1 - AX_X0) / style.SLOT_IN,
                                      (y1 - y0) / FIG_H]) for y0, y1 in PANEL_Y.values())
    for ax in (ax_a, ax_b):
        style.ref_lines(ax)
        ax.set_xlim(0.6, 15.4)
        ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15])
        ax.set_ylabel("Mean ask ($)")

    # (a) default opening, frontier phase
    ax_a.set_ylim(83.0, 98.4)
    ax_a.set_yticks([85, 90, 95])
    labels_a = []
    for g in ("sol", "luna", "grok"):
        for m in ("on", "off"):
            path = pick(runs, "frontier", g, m, 97.5, 6)
            ax_a.plot(hours, path, color=style.COLOR[g], ls=style.MSG_LS[m], lw=2.2)
            labels_a.append((path[-1], f"{SHORT[g]}, {m}", style.COLOR[g]))
    ax_a.set_title("Default opening, $97.50", pad=6)

    # (b) low-anchor test
    ax_b.set_ylim(85.6, 98.4)
    ax_b.set_yticks([86, 88, 90, 92, 94, 96])
    lines_b = [("A_agycontrol", "gemini_ms", "on", 97.5, "gemini", "Gemini on, $97.50"),
               ("A_lowanchor", "gemini_ms", "on", 90.0, "gemini", "Gemini on, $90"),
               ("A_lowanchor", "gemini_ms", "off", 90.0, "gemini", "Gemini off, $90"),
               ("frontier_lowanchor", "sol", "on", 90.0, "sol", None),
               ("frontier_lowanchor", "sol", "off", 90.0, "sol", None)]
    paths, labels_b = {}, []
    for phase, seller, m, opening, c, lab in lines_b:
        path = pick(runs, phase, seller, m, opening, 3)
        paths[(seller, m, opening)] = path
        ax_b.plot(hours, path, color=style.COLOR[c], ls=style.MSG_LS[m], lw=2.2)
        if lab:
            labels_b.append((path[-1], lab, style.COLOR[c]))
    sol_end = (paths[("sol", "on", 90.0)][-1] + paths[("sol", "off", 90.0)][-1]) / 2
    labels_b.append((sol_end, "Sol on, off, $90", style.COLOR["sol"]))
    ax_b.set_title("Opened at $97.50 or $90", pad=6)
    ax_b.set_xlabel("Hour")

    # call-outs: verbatim fragments of the logged messages, pinned at the hour sent
    quotes = load.ms_quotes()
    gem90 = paths[("gemini_ms", "on", 90.0)]
    for hour, frag, (tx, ty), k, rel in CALLOUTS:
        q = quotes[(quotes["folder"] == QUOTE_RUN) & (quotes["hour"] == hour)]
        if len(q) != 1 or frag not in q["text"].iloc[0]:
            raise ValueError(f"call-out at hour {hour} is not a substring of the logged message")
        words = frag.split()
        if len(words) > 8:
            raise ValueError("call-out longer than 8 words")
        body = "“" + " ".join(words[:k]) + "\n" + " ".join(words[k:]) + "”"
        ax_b.annotate(body, xy=(hour, gem90[hour - 1]), xytext=(tx, ty), ha="left", va="bottom",
                      fontsize=12, fontstyle="italic", color="black", linespacing=1.15,
                      arrowprops=dict(arrowstyle="-", color="black", lw=0.8, shrinkA=1, shrinkB=1,
                                      relpos=rel))
        ax_b.plot([hour], [gem90[hour - 1]], ls="none", marker="o", ms=4.5, color="black", zorder=4)

    for ax, items in ((ax_a, labels_a), (ax_b, labels_b)):
        style.end_labels(ax, items, x=LABEL_X, gap_in=0.19)

    panel_c(ax_c)
    for ax, letter in ((ax_a, "a"), (ax_b, "b"), (ax_c, "c")):
        bb = ax.get_position()
        fig.text(0.015, bb.y1 + 0.048 / FIG_H, letter, fontsize=16, fontweight="bold", ha="left", va="bottom")
    style.save(fig, "fig4_opening_price.png")


if __name__ == "__main__":
    main()
