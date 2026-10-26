"""Appendix figure: where the market opens, and the pre-specified opening-price test (M.S.'s runs).

Adapted from M.S.'s mert_sprint/report_ms/scripts/figures/make_fig4_opening_price.py, with its loaders and style
from mert_sprint/report_ms/scripts/lib/{load,style}.py (end_labels), ref origin/mert_sprint_sync_oct25, by M.S.:
the same two panels, runs, endpoint, test and encodings (messaging on solid, off dash-dot; filled marker = the run
meets the joint criterion; the bracket spans the two arm means and gives the mean paired difference and the exact
two-sided sign-flip p over the 2^6 sign patterns, computed here). Changes:
  - drawn at its print size, 6.5 x 4.2 in, with every text 8.5 pt or more (his was 6.5 x 5.38 in at 12 to 16 pt,
    and the report printed the older three-panel version at 4.4 in);
  - the two pinned private messages sit on the path of the run they come from (Gemini, $90 opening, seed 0, drawn
    as a thin line) instead of on the three-run mean, which is about $1 lower;
  - the Gemini $97.50 line is labelled as the second-route control and its pass count (2 of 3);
  - the runs are read from the run folders (ms_runs.py) rather than his ms_runs.csv / ms_prereg.csv / ms_quotes.csv.

(a) Mean seller ask by hour, markets opened at $97.50 or $90: Gemini 3.8 Flash sellers with GPT-4.1-mini buyers on
    M.S.'s second serving route, messaging on from $97.50 (shard2/A_agycontrol, 3 runs) and on and off from $90
    (shard2/A_lowanchor, 3 runs each); GPT-5.6 Sol sellers with Claude Haiku 5.5 buyers from $90, on and off
    (shard2/frontier_lowanchor, 3 runs each). Each line is the mean of avg_seller_asks_by_round over its runs.
(b) The pre-specified paired test (protocol mert_sprint/report_ms/prereg_sol_anchor.md; runs in
    shard2/prereg_anchor/): Sol sellers, Haiku 5.5 buyers, messaging off, seeds 3 to 8, each opened once at $97.50
    and once at $90; y is the primary endpoint, the mean of avg_seller_asks_by_round over hours 11 to 15.
Reference lines: $90 (index zero) dashed, $95 (ask index 0.5) dotted, $97.50 opening thin solid.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/ms/make_figD_opening_price.py
Output: report/figures/figD_opening_price.png (6.5 x 4.2 in, 300 dpi) and figD_opening_price.caption.txt
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import ms_runs  # noqa: E402
import style  # noqa: E402

NAME = "figD_opening_price"
FIG_W, FIG_H = style.SLOT_IN, 4.2
HOURS = list(range(1, 16))
MSG_LS = {"on": "-", "off": (0, (6, 2.2, 1.4, 2.2))}
GEMINI, SOL, BUYER_G, BUYER_S = "google/gemini-3.8-flash", "gpt-5.6-sol", "openai/gpt-4.1-mini", \
    "anthropic/claude-haiku-5.5"
QUOTE_SEED = 0
CALLOUTS = [  # hour, sender, recipient, verbatim fragment, text anchor (hour, $), line break after word k
    (1, "Seller Kai", "Seller Max", "let's keep our asks closely aligned around $90", (1.6, 90.9), 4),
    (12, "Seller Kai", "Seller Leo", "Our price coordination is completely rock solid.", (8.3, 90.9), 4),
]
A_X0, A_X1, A_Y0, A_Y1 = 0.62, 4.40, 2.22, 3.86       # panel a, inches
B_X0, B_X1, B_Y0, B_Y1 = 0.62, 3.10, 0.50, 1.48       # panel b, inches
LABEL_X = 15.6
GUIDE = "#9A9A9A"


def runs(phase, seller, buyer, messaging, opening, n=3):
    rs = [ms_runs.run(f) for f in ms_runs.list_runs("shard2", phase)]
    rs = [r for r in rs if r["seller_model"] == seller and r["buyer_model"] == buyer and r["messaging"] == messaging
          and r["opening_price"] == opening]
    if len(rs) != n:
        raise ValueError(f"{phase} {seller} {messaging} {opening}: {len(rs)} runs, expected {n}")
    return sorted(rs, key=lambda r: r["seed"])


def mean_path(rs):
    return np.mean([r["asks"] for r in rs], axis=0)


def sign_flip(diffs):
    obs = abs(np.mean(diffs))
    hits = sum(abs(np.mean([s * d for s, d in zip(signs, diffs)])) >= obs - 1e-12
               for signs in itertools.product((1, -1), repeat=len(diffs)))
    return hits, 2 ** len(diffs)


def end_labels(ax, items, x, gap_in=0.15):
    """M.S.'s style.end_labels: label line ends at data x in each line's color, spread at least gap_in apart,
    with a thin leader where a label moved."""
    fig = ax.figure
    h_in = ax.get_position().height * fig.get_size_inches()[1]
    lo, hi = ax.get_ylim()
    gap = gap_in * (hi - lo) / h_in
    items = sorted(items, key=lambda t: t[0])
    pos = [it[0] for it in items]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    shift = (sum(it[0] for it in items) - sum(pos)) / len(pos)
    pos = [p + shift for p in pos]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    x_end = ax.get_xlim()[1]
    for (y, text, color), py in zip(items, pos):
        ax.text(x, py, text, ha="left", va="center", color=color, clip_on=False)
        if abs(py - y) > gap * 0.15:
            ax.plot([x_end - 0.2, x - 0.08], [y, py], color=color, lw=0.7, clip_on=False)


def pin(ax, text, xy, xytext, corner, **kw):
    """Text at xytext with a leader from a corner of its box to xy (a separate empty annotation, so the print
    check measures the text alone)."""
    t = ax.text(*xytext, text, **kw)
    ax.figure.canvas.draw()
    bb = t.get_window_extent(ax.figure.canvas.get_renderer()).transformed(ax.transData.inverted())
    start = (bb.x0 + corner[0] * bb.width, bb.y0 + corner[1] * bb.height)
    ax.annotate("", xy=xy, xytext=start,
                arrowprops=dict(arrowstyle="-", color="black", lw=0.7, shrinkA=1, shrinkB=1))
    return t


def ref_lines(ax):
    for r in style.REF_LINES:
        ax.axhline(r["price"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)


def panel_a(ax, printed):
    ref_lines(ax)
    ax.set_xlim(0.6, 15.4)
    ax.set_xticks([1, 3, 5, 7, 9, 11, 13, 15])
    ax.set_ylim(86.6, 98.0)
    ax.set_yticks([88, 90, 92, 94, 96])
    ax.set_yticklabels([f"${t}" for t in (88, 90, 92, 94, 96)])
    ax.set_ylabel("Mean ask")
    ax.set_xlabel("Hour", labelpad=1)
    blue, orange = style.COLOR["gemini"], style.COLOR["sol"]
    ctrl = runs("A_agycontrol", GEMINI, BUYER_G, "on", 97.5)
    g_on = runs("A_lowanchor", GEMINI, BUYER_G, "on", 90.0)
    g_off = runs("A_lowanchor", GEMINI, BUYER_G, "off", 90.0)
    s_on = runs("frontier_lowanchor", SOL, BUYER_S, "on", 90.0)
    s_off = runs("frontier_lowanchor", SOL, BUYER_S, "off", 90.0)
    n_ctrl = sum(r["passed"] for r in ctrl)
    printed["ctrl_h15"] = sorted(r["asks"][14] for r in ctrl)
    printed["(a) runs per line"] = {k: [r["folder"].split("/")[-1] for r in v] for k, v in
                                    (("ctrl", ctrl), ("g_on", g_on), ("g_off", g_off), ("s_on", s_on),
                                     ("s_off", s_off))}
    lines = [(ctrl, "on", blue, f"Gemini on, $97.50: route\ncontrol, {n_ctrl} of {len(ctrl)} pass"),
             (g_on, "on", blue, "Gemini on, $90"), (g_off, "off", blue, "Gemini off, $90"),
             (s_on, "on", orange, None), (s_off, "off", orange, None)]
    labels = []
    for rs, m, c, lab in lines:
        p = mean_path(rs)
        ax.plot(HOURS, p, color=c, ls=MSG_LS[m], lw=1.6, zorder=3)
        if lab:
            labels.append((p[-1], lab, c))
        printed[f"(a) {rs[0]['seller_model']} {m} ${rs[0]['opening_price']}: hour 1 / 15"] = (round(p[0], 3),
                                                                                             round(p[-1], 3))
    sol_end = (mean_path(s_on)[-1] + mean_path(s_off)[-1]) / 2
    labels.append((sol_end, "Sol on and off, $90", orange))
    seed0 = [r for r in g_on if r["seed"] == QUOTE_SEED][0]
    ax.plot(HOURS, seed0["asks"], color=style.tint(blue, 0.35), lw=0.9, zorder=2.5)
    labels.append((seed0["asks"][-1], f"Gemini on, $90, seed {QUOTE_SEED}", style.tint(blue, 0.2)))
    end_labels(ax, labels, LABEL_X)
    printed["(a) Gemini on $97.50 passes"] = f"{n_ctrl} of {len(ctrl)}"
    printed["(a) seed-0 path hour 1 / 12 / 15"] = (seed0["asks"][0], seed0["asks"][11], seed0["asks"][14])

    # call-outs: verbatim fragments of the logged private messages, on seed 0's own path at the hour sent
    for hour, sender, recipient, frag, (tx, ty), k in CALLOUTS:
        dms = [dm["text"] for dm in (seed0["rounds"][hour - 1].get("seller_dms") or [])
               if dm["sender"] == sender and dm["recipient"] == recipient]
        if len(dms) != 1 or frag not in dms[0]:
            raise ValueError(f"call-out at hour {hour} is not a substring of the logged message")
        printed[f"(a) quote hour {hour} {sender} -> {recipient}"] = dms[0]
        words = frag.split()
        body = f"seed {QUOTE_SEED}, hour {hour}:\n“" + " ".join(words[:k]) + "\n" + " ".join(words[k:]) + "”"
        y = seed0["asks"][hour - 1]
        pin(ax, body, (hour, y), (tx, ty), (0.0, 0.0), ha="left", va="bottom", fontstyle="italic",
            linespacing=1.12)
        ax.plot([hour], [y], ls="none", marker="o", ms=3.2, color="black", zorder=4)


def panel_b(ax, printed):
    hi = runs("prereg_anchor", SOL, BUYER_S, "off", 97.5, n=6)
    lo = runs("prereg_anchor", SOL, BUYER_S, "off", 90.0, n=6)
    if [r["seed"] for r in hi] != list(range(3, 9)) or [r["seed"] for r in lo] != list(range(3, 9)):
        raise ValueError("expected seeds 3 to 8 at each opening")
    c = style.COLOR["sol"]
    ref_lines(ax)
    pairs = []
    for a, b in zip(hi, lo):
        ya, yb = np.mean(a["asks"][10:15]), np.mean(b["asks"][10:15])
        pairs.append((a["seed"], ya, yb, a["passed"], b["passed"]))
        ax.plot([0, 1], [ya, yb], color=c, lw=1.1, zorder=2, solid_capstyle="round")
        for x, y, ok in ((0, ya, a["passed"]), (1, yb, b["passed"])):
            ax.plot([x], [y], ls="none", marker="o", ms=5, mew=1.1, mec=c, mfc=(c if ok else "white"), zorder=3)
    hi_mean = np.mean([p[1] for p in pairs])
    lo_mean = np.mean([p[2] for p in pairs])
    diffs = [p[1] - p[2] for p in pairs]
    hits, n = sign_flip(diffs)
    n_hi, n_lo = sum(p[3] for p in pairs), sum(p[4] for p in pairs)
    xb = 1.30
    ax.plot([xb - 0.05, xb, xb, xb - 0.05], [lo_mean, lo_mean, hi_mean, hi_mean], color="black", lw=0.8,
            clip_on=False, zorder=4)
    for x, m in ((0.07, hi_mean), (1.07, lo_mean)):
        ax.plot([x, xb - 0.05], [m, m], color=GUIDE, lw=0.8, ls=(0, (1, 1.6)), zorder=1)
    mid = (lo_mean + hi_mean) / 2
    ax.text(xb + 0.07, mid + 0.4, f"+${np.mean(diffs):.2f}", ha="left", va="bottom", fontsize=style.FS_TITLE,
            fontweight="bold", clip_on=False)
    ax.text(xb + 0.07, mid + 0.2, f"mean difference, {sum(d > 0 for d in diffs)} of {len(diffs)} seed blocks "
            f"higher\nfrom $97.50; exact sign-flip p = {hits}/{n} = {hits / n:.3f}", ha="left", va="top",
            clip_on=False, linespacing=1.2)
    ax.set_xlim(-0.3, 1.34)
    ax.set_xticks([0, 1], [f"opened at $97.50\n{n_hi} of {len(pairs)} pass",
                           f"opened at $90\n{n_lo} of {len(pairs)} pass"])
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(88.0, 98.0)
    ax.set_yticks([88, 90, 92, 94, 96])
    ax.set_yticklabels([f"${t}" for t in (88, 90, 92, 94, 96)])
    ax.set_ylabel("Mean ask")
    printed["(b) per seed (seed, $97.50, $90, pass, pass)"] = [(s, round(a, 5), round(b, 5), pa, pb)
                                                             for s, a, b, pa, pb in pairs]
    printed["(b) means, difference, range"] = (round(hi_mean, 3), round(lo_mean, 3), round(np.mean(diffs), 3),
                                               round(min(diffs), 3), round(max(diffs), 3))
    printed["(b) sign-flip"] = f"{hits}/{n} = {hits / n:.4f}"
    printed["(b) passes"] = (n_hi, n_lo)
    return np.mean(diffs), (hits, n), (n_hi, n_lo), (min(diffs), max(diffs))


def main():
    style.setup()
    printed = {}
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax_a = fig.add_axes([A_X0 / FIG_W, A_Y0 / FIG_H, (A_X1 - A_X0) / FIG_W, (A_Y1 - A_Y0) / FIG_H])
    ax_b = fig.add_axes([B_X0 / FIG_W, B_Y0 / FIG_H, (B_X1 - B_X0) / FIG_W, (B_Y1 - B_Y0) / FIG_H])
    panel_a(ax_a, printed)
    diff, (hits, n), (n_hi, n_lo), (dmin, dmax) = panel_b(ax_b, printed)
    for y1, letter, title in ((A_Y1, "a", "Opened at $97.50 or $90"),
                              (B_Y1, "b", "Pre-specified Sol test: mean ask over hours 11 to 15, by seed block")):
        fig.text(0.04 / FIG_W, (y1 + 0.10) / FIG_H, letter, fontsize=style.FS_TITLE, fontweight="bold",
                 va="bottom")
        fig.text(A_X0 / FIG_W, (y1 + 0.10) / FIG_H, title, fontsize=style.FS_HEAD, va="bottom")
    out = style.save(fig, f"{NAME}.png", max_h_in=FIG_H)
    plt.close(fig)
    caption = (
        "Figure D7. Prices stay where the market opens (M.S.'s runs). (a) Mean seller ask by hour: Gemini 3.8 Flash sellers "
        "with messaging from $97.50 (the second-route control, which passed 2 of 3 against 3 of 3 on OpenRouter), "
        "against Gemini with and without messaging from $90 and GPT-5.6 Sol with and without messaging from $90 "
        "(Sol's two lines overlap), 3 runs per line (Gemini with GPT-4.1-mini buyers on the second route, Sol with "
        "Claude Haiku 5.5 buyers); the control's drop in hours 14 and 15 comes from one run (hour-15 mean asks "
        + ", ".join(f"${v:.2f}" for v in printed["ctrl_h15"])
        + f"). The thin line is the Gemini $90 run with messaging at seed {QUOTE_SEED}, and two "
        "of its private messages are pinned at the hour they were sent. (b) The pre-specified paired test "
        "(Table D8): each line joins one seed block's run opened at $97.50 to its run opened at $90, at the mean "
        f"ask over hours 11 to 15; filled markers meet the criterion ({n_hi} of 6 against {n_lo} of 6). The "
        f"bracket spans the two arm means: +${diff:.2f} (range ${dmin:.2f} to ${dmax:.2f}), exact two-sided "
        f"sign-flip p = {hits}/{n} = {hits / n:.3f}. Horizontal lines mark $90 (dashed), $95 (dotted) and $97.50 "
        "(thin). (Figure: M.S.)"
    )
    from_ref = sorted({f.split("/")[-2] for f, s in ms_runs.SOURCES.items() if s != "disk"})
    per_seed = "; ".join(f"seed {s_} ${a:.4f} / ${b:.4f} ({'pass' if pa else 'fail'} / {'pass' if pb else 'fail'})"
                         for s_, a, b, pa, pb in printed["(b) per seed (seed, $97.50, $90, pass, pass)"])
    details = (
        "Made by scripts/figures/ms/make_figD_opening_price.py (with ms_runs.py), an adapted copy of M.S.'s "
        "mert_sprint/report_ms/scripts/figures/make_fig4_opening_price.py with scripts/lib/{load,style}.py "
        f"(ref origin/mert_sprint_sync_oct25), at print size {out['width_in']} x {out['height_in']} in, 300 dpi "
        f"({out['px'][0]} x {out['px'][1]} px), smallest text {out['min_font_pt']} pt. Appendix D.5, replacing the "
        "three-panel ms_fig4_opening_price.png as Figure D7 (its frontier panel at the default opening is dropped; "
        "Table D6 and the two-runs figure cover it).\n"
        "Numbers printed, checked against each run folder's collusion_metrics.json (joint_criterion, "
        "avg_seller_asks_by_round) and unified.log (configuration): (a) the control label's '2 of 3 pass' = "
        f"{printed['(a) Gemini on $97.50 passes']} runs with joint_criterion.passed (Table D7: 2 of 3); the two "
        "quotes are asserted substrings of Seller Kai's logged private messages to Seller Max (hour 1) and Seller "
        "Leo (hour 12) in the seed-0 run, whose mean ask was "
        f"${printed['(a) seed-0 path hour 1 / 12 / 15'][0]:.2f} in hour 1 and "
        f"${printed['(a) seed-0 path hour 1 / 12 / 15'][1]:.2f} in hour 12 (the pinned points; Table D11: $89.97 to "
        "$90.00 through hour 15). (b) per seed block, mean ask over hours 11 to 15 from $97.50 / from $90 and the "
        f"criterion: {per_seed} (Table D8 gives these to three decimals; several values are exact ties at the fourth, so its last digit can differ by one); mean difference +${diff:.3f}, 6 of 6 positive, sign-flip "
        f"{hits}/{n} = {hits / n:.4f}; passes {n_hi} of 6 against {n_lo} of 6 (Table D8 and Section 4.5: +$6.79, "
        "p = 0.031, 5 of 6 against 0 of 6). The " + ", ".join(from_ref) + " runs are not in this branch's working "
        "tree and were read from git ref origin/mert_sprint_sync_oct25; all other runs from disk.\n"
        "Regenerate: cd third_party/llm-agent-collusion && PYTHONUTF8=1 uv run python "
        "../../scripts/figures/ms/make_figD_opening_price.py"
    )
    (style.FIGURES / f"{NAME}.caption.txt").write_text(caption + "\n\n" + details + "\n", encoding="utf-8")
    for k, v in printed.items():
        print(f"{k}: {v}")
    print("sources:", sorted(set(ms_runs.SOURCES.values())),
          [f for f, s in ms_runs.SOURCES.items() if s != "disk"][:1], "...")
    print(caption)
    print(out)


if __name__ == "__main__":
    main()
