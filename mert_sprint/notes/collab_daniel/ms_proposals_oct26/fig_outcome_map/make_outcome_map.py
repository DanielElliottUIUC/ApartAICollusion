"""Outcome map: every market of the joint sprint study, by setup, on the last-third ask index.

One marker per market. x is the last-third (hours 11 to 15) ask index of the LLM sellers, with the mean ask in
dollars on the top axis ($90 = 0, $100 = 1). Filled markers meet the joint criterion. Circles have messaging on,
squares have it off. In a row with both, circles sit in the upper lane and squares in the lower lane. Colour is
the seller family (Okabe-Ito palette of daniel/report-v2/scripts/figures/ms/style.py). The right column gives the
private messages the LLM sellers sent per market, averaged over the row's messaging-on markets (any sent to the
scripted seat 5 included, as in Tables D2 to D4 of the report).

Reads only the per-run tables and run folders under DE, DE_99, DE_PIN, MS and RUNS below. Writes outcome_map.png
(300 dpi) and outcome_map_data.csv next to this script.

    python notes/collab_daniel/desk/fig_outcome_map/make_outcome_map.py
"""
import glob
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.transforms import blended_transform_factory

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
DE = REPO / "daniel/report-v2/report/data"
DE_99 = REPO / "daniel/pr41_extension_runs_oct25/report/data/dg_gemini_99"   # not in the report-v2 mirror
DE_PIN = REPO / "daniel/pr44_pinned_price_oct26/report/data/pinned"          # not in the report-v2 mirror
MS = REPO / "report_ms/data"
RUNS = REPO / "experiments/runs"

# Seller families, colours from daniel/report-v2/scripts/figures/ms/style.py (COLOR).
COLOR = {"gemini": "#0072B2", "sol": "#D55E00", "luna": "#009E73", "grok": "#CC79A7", "gpt41": "#E69F00",
         "haiku": "#56B4E9"}
MS_FAMILY = {"gpt-5.6-sol": "sol", "gpt-6-luna": "luna", "grok-4.7": "grok", "google/gemini-3.8-flash": "gemini"}

# Blocks and rows, top to bottom. Each row: (key, label); (None, None) is a small gap. MERGED says what a
# row pools.
BLOCKS = [
    ("Undercover 5+5 market, Gemini 3.8 Flash sellers", [
        ("g_base", "Placebo note (Base)"),
        ("g_d", "$96 offer (D)"),
        ("g_plea", "Offer as human pleas"),
        ("g_d99", "$99 offer"),
        ("g_warn", "Warning"),
        ("g_prec", "Warning and precedent"),
    ]),
    ("Undercover 5+5 market, GPT-4.1 sellers (last row: Claude Haiku 5.5)", [
        ("o_base", "Placebo note (Base)"),
        ("o_d", "$96 offer (D)"),
        ("o_d99", "$99 offer"),
        ("o_warn", "Warning"),
        ("o_prec", "Warning and precedent"),
        ("h_d", "Haiku 5.5, $96 offer"),
    ]),
    ("4+4 market, opened at $97.50 unless the row says $90", [
        ("a_gem", "Gemini 3.8 Flash"),
        ("a_gem2", "Gemini, 2nd route"),
        ("a_notice", "Gemini, prohibition notice"),
        ("a_warn", "Gemini, warning"),
        ("a_sol", "GPT-5.6 Sol"),
        ("a_luna", "GPT-6 Luna"),
        ("a_grok", "Grok 4.7"),
        ("a_haiku", "Claude Haiku 5.5"),
        (None, None),
        ("l_gem2", "Gemini, 2nd route, $90"),
        ("l_sol", "Sol, from $90"),
        ("l_luna", "Luna, from $90"),
        ("p_test", "Sol test, $97.50 vs $90"),
    ]),
    ("$90 pinned as the competitive price (last two rows: 5+5 undercover)", [
        ("q_gem", "Gemini 3.8 Flash"),
        ("q_gem2", "Gemini, 2nd route"),
        ("q_gpt41", "GPT-4.1"),
        ("q_sol", "GPT-5.6 Sol"),
        ("q_luna", "GPT-6 Luna"),
        ("q_dg", "Gemini, no warning"),
        ("q_dgw", "Gemini, warning"),
    ]),
]
MERGED = {
    "g_plea": "D-hs, D-hb, D-hsb",
    "g_warn": "E, F-sham, G-warn",
    "g_prec": "F, G-prec",
    "o_warn": "E, G-warn",
    "o_base": "squares: five GPT-4.1 sellers, no seat 5, no messaging",
    "a_sol": "Haiku 5.5, Luna and GPT-4.1-mini buyers",
    "p_test": "pre-specified test, seed blocks 3 to 8, opened at $97.50 and at $90",
    "q_dg": "Base, D; squares: five Gemini sellers, no seat 5, no messaging",
}

points = []


def add(row, family, run_id, ask_index, passed, msgs, source, lane="on"):
    points.append({"row": row, "lane": lane, "family": family, "run_id": run_id, "ask_index": float(ask_index),
                   "passed": bool(passed), "private_msgs": int(msgs), "source": str(source)})


def rel(p):
    return Path(p).resolve().relative_to(REPO).as_posix()


def is_pass(v):
    return v is True or str(v).strip().upper() in ("TRUE", "PASS")


# 1. Undercover market, Gemini sellers: market_by_run (index, criterion) joined with table3_extra (messages).
mbr = pd.read_csv(DE / "dg/market_by_run.csv")
t3 = pd.read_csv(DE / "dg/table3_extra.csv").set_index("run_id")
GEM_ROW = {"Base": "g_base", "D": "g_d", "D-hs": "g_plea", "D-hb": "g_plea", "D-hsb": "g_plea", "E": "g_warn",
           "F-sham": "g_warn", "G-warn": "g_warn", "F": "g_prec", "G-prec": "g_prec"}
for r in mbr.itertuples():
    add(GEM_ROW[r.arm], "gemini", r.run_id, r.ask_index, r.passed, t3.loc[r.run_id, "private_msgs_llm_total"],
        f"{rel(DE / 'dg/market_by_run.csv')}; {rel(DE / 'dg/table3_extra.csv')}")
g99 = pd.read_csv(DE_99 / "market_by_run.csv")
for r in g99[g99.role == "extension"].itertuples():
    add("g_d99", "gemini", r.run_id, r.ask_index, r.passed, r.private_msgs_llm, rel(DE_99 / "market_by_run.csv"))

# 2. Undercover market, GPT-4.1 and Haiku sellers. Per-run message totals are in judge_vs_price.csv.
jvp = pd.read_csv(DE / "dg/judge_vs_price.csv")
jmsg = dict(zip(jvp.run_id, jvp.llm_private_msgs))
src_j = rel(DE / "dg/judge_vs_price.csv")
OAI_ROW = {"Base": "o_base", "D": "o_d", "E": "o_warn", "G-warn": "o_warn", "F": "o_prec"}
for r in pd.read_csv(DE / "dg_gpt41/market_by_run.csv").itertuples():
    add(OAI_ROW[r.arm], "gpt41", r.run_id, r.ask_index, r.passed, jmsg[r.run_id],
        f"{rel(DE / 'dg_gpt41/market_by_run.csv')}; {src_j}")
for r in jvp[(jvp.results_group == "dg_gpt41") & (jvp.arm == "no-comms")].itertuples():
    add("o_base", "gpt41", r.run_id, r.ask_index, r.passed, r.llm_private_msgs, src_j, lane="off")
o99 = pd.read_csv(DE / "dg_gpt41_99/market_by_run.csv")
for r in o99[o99.role == "extension"].itertuples():
    add("o_d99", "gpt41", r.run_id, r.ask_index, r.passed, r.private_msgs_llm,
        rel(DE / "dg_gpt41_99/market_by_run.csv"))
for r in pd.read_csv(DE / "dg_haiku/market_by_run.csv").itertuples():
    add("h_d", "haiku", r.run_id, r.ask_index, r.passed, jmsg[r.run_id],
        f"{rel(DE / 'dg_haiku/market_by_run.csv')}; {src_j}")

# 3. 4+4 market at $97.50. D.E.'s Gemini conditions (a_warn/runs.csv holds them all, with the seed-0 rerun).
aw = pd.read_csv(DE / "a_warn/runs.csv")
AW_ROW = {"comms": ("a_gem", "on"), "comms_oct25": ("a_gem", "on"), "nocomms": ("a_gem", "off"),
          "notice": ("a_notice", "on"), "warn": ("a_warn", "on")}
for r in aw.itertuples():
    row, lane = AW_ROW[r.condition]
    add(row, "gemini", r.run_folder, r.last_third_ask_index, is_pass(r.joint_criterion_pass),
        r.private_messages_total, rel(DE / "a_warn/runs.csv"), lane)

# M.S.'s runs: ms_runs.csv (frontier, buyer swap, low opening, second-route control) and ms_prereg.csv.
ms = pd.read_csv(MS / "ms_runs.csv")
MS_ROW = {("frontier", "gpt-5.6-sol"): "a_sol", ("frontier_b41", "gpt-5.6-sol"): "a_sol",
          ("frontier", "gpt-6-luna"): "a_luna", ("frontier", "grok-4.7"): "a_grok",
          ("A_agycontrol", "google/gemini-3.8-flash"): "a_gem2",
          ("A_lowanchor", "google/gemini-3.8-flash"): "l_gem2",
          ("frontier_lowanchor", "gpt-5.6-sol"): "l_sol", ("frontier_lowanchor", "gpt-6-luna"): "l_luna"}
for r in ms.itertuples():
    add(MS_ROW[(r.phase, r.seller_model)], MS_FAMILY[r.seller_model], Path(r.folder).name, r.ask_index, r.passed,
        r.private_messages, rel(MS / "ms_runs.csv"), "on" if r.messaging == "on" else "off")
for r in pd.read_csv(MS / "ms_prereg.csv").itertuples():
    add("p_test", "sol", Path(r.folder).name, r.ask_index, r.passed,
        r.private_messages, rel(MS / "ms_prereg.csv"), "off")


def metrics_runs(pattern, row, family, lane_of):
    """Runs read straight from collusion_metrics.json: joint_criterion and dm_summary.total."""
    for f in sorted(glob.glob(str(RUNS / pattern))):
        m = json.loads(Path(f).read_text(encoding="utf-8"))
        name = Path(f).parent.name
        add(row, family, name, m["joint_criterion"]["ask_index"], m["joint_criterion"]["passed"],
            m["dm_summary"]["total"], rel(f), lane_of(name))


# Claude Haiku 5.5 sellers in the 4+4 market (Table D6): not in ms_runs.csv, so read from their run folders.
messaging = lambda name: "off" if "nocomms" in name else "on"   # noqa: E731
metrics_runs("shard*/A/*_danielA_haiku_*/collusion_metrics.json", "a_haiku", "haiku", messaging)
metrics_runs("shard*/B/*_danielB_CCCC-*/collusion_metrics.json", "a_haiku", "haiku", messaging)

# 4. $90 pinned market. D.E.'s tables, then M.S.'s run folders.
for fname, row, fam in (("pinned_a_runs.csv", "q_gem", "gemini"), ("pinned_a_gpt41_runs.csv", "q_gpt41", "gpt41")):
    for r in pd.read_csv(DE_PIN / fname).itertuples():
        add(row, fam, r.run_id, r.last_third_ask_index, is_pass(r.joint_criterion_pass), r.private_messages,
            rel(DE_PIN / fname), "on" if r.messaging == "on" else "off")
# 5+5 undercover pinned arms: seats 1 to 4 (the LLM sellers comparable across arms, as in Table D9).
for r in pd.read_csv(DE_PIN / "pinned_dg_runs.csv").itertuples():
    row = "q_dgw" if r.arm == "G-warn" else "q_dg"
    add(row, "gemini", r.run_id, r.seats1_4_ask_index, is_pass(r.seats1_4_pass),
        r.private_msgs_peer + r.private_msgs_to_seat5, rel(DE_PIN / "pinned_dg_runs.csv"),
        "off" if r.arm == "Base-nocomms5" else "on")
metrics_runs("box/pinned90/*_pinned90_gpt56sol_*/collusion_metrics.json", "q_sol", "sol", messaging)
metrics_runs("box/pinned90/*_pinned90_gpt6luna_*/collusion_metrics.json", "q_luna", "luna", messaging)
metrics_runs("shard2/pinned90/*_pinned90_gemini38flash_agy_*/collusion_metrics.json", "q_gem2", "gemini", messaging)

# ---------------------------------------------------------------- data table
row_label = {k: lab for _, rows in BLOCKS for k, lab in rows if k}
row_block = {k: b for b, rows in BLOCKS for k, _ in rows if k}
df = pd.DataFrame(points)
assert set(df.row) == set(row_label), set(row_label) ^ set(df.row)
df.insert(0, "block", df.row.map(row_block))
df.insert(2, "row_label", df.row.map(row_label))
df.insert(3, "row_contents", df.row.map(MERGED).fillna(""))
df.to_csv(HERE / "outcome_map_data.csv", index=False)

# ---------------------------------------------------------------- figure
FS_TICK, FS_LAB, FS_TXT = 12, 14, 11
mpl.rcParams.update({"font.family": "DejaVu Sans", "text.parse_math": False, "axes.linewidth": 0.8})

W = 6.5
PITCH = 0.1805        # row pitch, inches
HEAD = 0.200          # header line, inches
SUBGAP = 0.06         # gap before the $90 rows of the 4+4 block, inches
LANE = 0.25           # lane offset as a share of the pitch (messaging on above, off below)
LEFT_TXT = 2.40       # label column, inches (row labels end here)
RIGHT_COL = 0.48      # message column, inches
TOP, BOTTOM = 0.27, 0.27
X0, X1 = -0.85, 1.0

ys, heads, spans = {}, [], []
y = 0.0
for title, rows in BLOCKS:
    heads.append((title, y + HEAD * 0.5))
    y += HEAD
    top = y
    for key, _ in rows:
        if key is None:
            spans.append((top, y))
            y += SUBGAP
            top = y
            continue
        ys[key] = y + PITCH / 2
        y += PITCH
    spans.append((top, y))
y_end = y + 0.02
H = TOP + y_end + BOTTOM

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([LEFT_TXT / W, BOTTOM / H, (W - LEFT_TXT - RIGHT_COL) / W, y_end / H])
ax.set_xlim(X0, X1)
ax.set_ylim(y_end, 0)
for s in ("left", "right"):
    ax.spines[s].set_visible(False)
for s in ("top", "bottom"):
    ax.spines[s].set_color("#888888")

# Reference lines per block, so they stop at the headers: $90 (index 0) dashed, $95 (0.5, the criterion) dotted.
for top, bot in spans:
    ax.plot([0, 0], [top, bot], color="#666666", lw=0.9, ls=(0, (5, 3)), zorder=1)
    ax.plot([0.5, 0.5], [top, bot], color="#666666", lw=1.2, ls=(0, (1, 2)), zorder=1)
# Alternate rows carry a pale band, so the two lanes of a row read as one row.
for i, key in enumerate(ys):
    if i % 2 == 0:
        ax.axhspan(ys[key] - PITCH / 2, ys[key] + PITCH / 2, color="#F0F0F0", lw=0, zorder=0)

for key, g in df.groupby("row"):
    lanes = set(g.lane)
    for r in g.itertuples():
        dy = 0.0 if len(lanes) == 1 else (-LANE if r.lane == "on" else LANE) * PITCH
        c = COLOR[r.family]
        ax.scatter(r.ask_index, ys[key] + dy, s=34, marker="o" if r.lane == "on" else "s",
                   facecolor=c if r.passed else "white", edgecolor=c, linewidth=1.2,
                   zorder=4 if r.passed else 3, clip_on=False)

# Row labels, block headers, message column.
ax.set_yticks(list(ys.values()))
ax.set_yticklabels([row_label[k] for k in ys], fontsize=FS_TICK)
ax.tick_params(axis="y", length=0, pad=4)
tr = blended_transform_factory(fig.transFigure, ax.transData)
for title, yh in heads:
    ax.text(0.004, yh, title, transform=tr, fontsize=FS_TXT, fontweight="bold", va="center", ha="left")
ax.text(0.99, heads[0][1], "Private msgs", transform=tr, fontsize=FS_TXT, fontweight="bold", va="center",
        ha="right")
for key, g in df.groupby("row"):
    on = g[g.lane == "on"].private_msgs
    v = on.mean() if len(on) else 0.0
    txt = "0" if v == 0 else (f"{v:.0f}" if v >= 9.95 else f"{v:.1f}")
    ax.text(0.99, ys[key], txt, transform=tr, fontsize=FS_TXT, va="center", ha="right")

# Axes: ask index below, mean ask in dollars above; their names sit in the label column, level with the ticks.
ax.set_xticks([-0.5, 0, 0.5, 1])
ax.set_xticklabels(["−0.5", "0", "0.5", "1"], fontsize=FS_TICK)
ax.tick_params(axis="x", pad=2)
top_ax = ax.secondary_xaxis("top", functions=(lambda i: 90 + 10 * i, lambda p: (p - 90) / 10))
top_ax.set_xticks([85, 90, 95, 100])
top_ax.set_xticklabels(["$85", "$90", "$95", "$100"], fontsize=FS_TICK)
top_ax.spines["top"].set_color("#888888")
top_ax.tick_params(axis="x", pad=2)
lab_x = (LEFT_TXT - 0.08) / W
fig.text(lab_x, (BOTTOM - 0.155) / H, "Ask index", fontsize=FS_LAB, ha="right", va="center")
fig.text(lab_x, (H - TOP + 0.155) / H, "Mean ask", fontsize=FS_LAB, ha="right", va="center")

# Key, in the empty left part of the first block.
k_top = spans[0][0]
key_items = [("o", True, "meets criterion"), ("o", False, "does not"), ("s", False, "messaging off")]
for i, (m, filled, text) in enumerate(key_items):
    yk = k_top + PITCH * (0.5 + i)
    ax.scatter(-0.80, yk, s=34, marker=m, facecolor="#555555" if filled else "white", edgecolor="#555555",
               linewidth=1.2, zorder=5)
    ax.text(-0.75, yk, text, fontsize=FS_TXT, va="center", ha="left", color="#333333")

fig.savefig(HERE / "outcome_map.png", dpi=300)
print(f"{W:.2f} x {H:.2f} in, {len(ys)} rows, {len(df)} markets")
