"""Diagram 3: our frontier and opening-price tests, as a left-to-right workflow with result tags.

Every run uses the step A market: four sellers of one model, four LLM buyers, 15 hours, no scripted seat, no report
action. (1) Frontier sellers GPT-5.6 Sol, GPT-6 Luna and Grok 4.7, messaging on and off, two buyer models (Claude
Haiku 5.5, GPT-6 Luna), three seeds: 36 runs; Sol passes the joint criterion in 8 of 12, Luna and Grok in 0 of 12.
(2) The harness, like the original Agrawal et al. harness, seeds seller asks near $97.50; we open the book at $90
and change nothing else: 0 of 21 runs pass (Sol 12, Luna 3, Gemini 3.8 Flash 6). (3) The pre-specified test:
protocol committed before the runs, seed blocks 3 to 8, Sol (Haiku 5.5 buyers, messaging off) opened at $97.50
and at $90, endpoint the mean ask over hours 11 to 15, exact paired sign-flip test over 64 sign patterns: all 6
pairs higher at $97.50, mean +$6.79, p = 0.031.
Sources: report_ms/prereg_sol_anchor.md, report_ms/prereg_result.md, notes/strategy_oct25/README.md and
01_our_results.md, data/ms_runs.csv.
Slot: full width, 6.5 in.  Output: report/figures/diag3_our_tests.png
"""
import kit
from kit import COLOR, INK, text, runs, box, chevron

H = 3.84
X0, GAP = 0.06, 0.22
COL_W = [1.86, 1.86, 2.22]                      # the third step has the longest lines
COL_X = [X0, X0 + COL_W[0] + GAP, X0 + COL_W[0] + COL_W[1] + 2 * GAP]
B = dict(weight="bold")
SOL, LUNA, GROK, GEM = (dict(color=COLOR[k]) for k in ("sol", "luna", "grok", "gemini"))

COLUMNS = [
    [[("1  Frontier sellers", B)],
     [("GPT-5.6 Sol", SOL)], [("GPT-6 Luna", LUNA)], [("Grok 4.7", GROK)],
     [("messaging on, off", {})], [("2 buyer models", {})], [("3 seeds per cell", {})], [("36 runs", {})]],
    [[("2  Opening price", B)],
     [("harness default,", {})], [("as in Agrawal et al.:", {})], [("asks near $97.50", {})],
     [("we open at $90,", {})], [("all else unchanged", {})]],
    [[("3  Pre-specified test", B)],
     [("protocol committed", {})], [("before the runs", {})], [("seed blocks 3 to 8", {})],
     [("Sol", SOL), (": $97.50 vs $90", {})], [("mean ask, hours 11–15", {})], [("paired sign-flip test,", {})],
     [("64 sign patterns", {})]],
]
TAGS = [
    [[("$97.50 opening:", {})], [("Sol", SOL), (" 8 of 12 pass", B)], [("Luna", LUNA), (", ", {}), ("Grok", GROK),
                                                                         (" 0 of 12", B)]],
    [[("$90 opening:", {})], [("0 of 21 pass", B)], [("Sol", SOL), (", ", {}), ("Luna", LUNA), (", ", {}),
                                                     ("Gemini", GEM)]],
    [[("all 6 pairs higher", B)], [("mean ", {}), ("+$6.79", B), (" at $97.50", {})], [("p = 0.031", B)]],
]


def build():
    fig, ax = kit.figure(H)
    top = H - 0.06
    # the market every run uses
    bh = 0.62
    box(ax, X0, top - bh, 6.44 - X0, bh, fc="white", ec=INK, lw=1.3)
    yl = top - 0.2
    runs(ax, X0 + 0.14, yl, [("Step A market, every run: ", B), ("four sellers of one model, four LLM buyers,", {})])
    text(ax, X0 + 0.14, yl - kit.LINE, "15 hours, no scripted seat, no report action")
    # three steps, left to right
    ch = 0.2 + 7 * kit.LINE + 0.2                 # eight rows
    yt = top - bh - 0.22
    for i, (x, W, rows) in enumerate(zip(COL_X, COL_W, COLUMNS)):
        ax.plot([x + W / 2] * 2, [top - bh, yt], color=INK, lw=1.2, zorder=2)
        box(ax, x, yt - ch, W, ch, fc="white", ec=INK, lw=1.3)
        for j, parts in enumerate(rows):
            runs(ax, x + 0.12, yt - 0.2 - j * kit.LINE, parts)
        if i < 2:
            chevron(ax, x + W + 0.03, yt - ch / 2, w=GAP - 0.06, h=0.38)
    # result tags under each step
    th = 0.2 + 2 * kit.LINE + 0.14
    ty = yt - ch - 0.2
    for x, W, rows in zip(COL_X, COL_W, TAGS):
        ax.plot([x + W / 2] * 2, [yt - ch, ty], color=INK, lw=1.2, zorder=2)
        box(ax, x, ty - th, W, th, fc="#F2F2F2", ec=INK, lw=1.0, r=0.14)
        for j, parts in enumerate(rows):
            runs(ax, x + 0.12, ty - 0.2 - j * kit.LINE, parts)
    return fig


if __name__ == "__main__":
    kit.save(build(), "diag3_our_tests.png")
