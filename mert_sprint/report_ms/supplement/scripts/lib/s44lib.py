"""Loaders, style and checks for the S4.4 supplement figures (opening price and what the agents said).

Style constants are copied from report_ms/scripts/lib/style.py (2026-10-25), so these figures do not move when
the report's style file is edited. Run data are read straight from experiments/runs/:
  catalog()        one row per run of the phases this section uses, from experiment_metadata.json and
                   collusion_metrics.json
  run(folder)      per-hour records of unified.log (seller asks, buyer bids, trades, public messages, DMs)
  verify(...)      checks that a quote is the exact text at the stated file and line
  audit(fig)       font floors, text inside the image, no two text boxes overlapping
Outputs go only to report_ms/supplement/{figures,data}/S44 and report_ms/supplement/sections/S44.md.
"""
import json
import re
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd

LIB = Path(__file__).resolve().parent
SUP = LIB.parents[1]                       # report_ms/supplement/
MS = SUP.parent                            # report_ms/
REPO = MS.parent                           # apart-collusion-sprint-2026/
RUNS = REPO / "experiments" / "runs"
FIG_DIR = SUP / "figures" / "S44"
DATA_DIR = SUP / "data" / "s44"
HOURS = list(range(1, 16))

# ---------------------------------------------------------------- style (copied from report_ms style.py)
SLOT_IN = 6.5
DPI = 300
COLOR = {"gemini": "#0072B2", "sol": "#D55E00", "luna": "#009E73", "grok": "#CC79A7",
         "gpt41": "#E69F00", "haiku": "#56B4E9"}
NAME = {"gemini": "Gemini 3.8 Flash", "sol": "GPT-5.6 Sol", "luna": "GPT-6 Luna", "grok": "Grok 4.7",
        "gpt41": "GPT-4.1", "haiku": "Claude Haiku 5.5"}
SHORT = {"gemini": "Gemini", "sol": "Sol", "luna": "Luna", "grok": "Grok", "haiku": "Haiku"}
GRAY = "#555555"
LIGHT = "#BBBBBB"
REF_LINES = [
    {"price": 90.0, "index": 0.0, "ls": (0, (5, 3)), "lw": 1.2},
    {"price": 95.0, "index": 0.5, "ls": (0, (1, 2)), "lw": 1.6},
    {"price": 97.5, "index": 0.75, "ls": "-", "lw": 0.7},
]
MSG_LS = {"on": "-", "off": (0, (7, 2.5, 1.5, 2.5))}


def setup():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "axes.labelsize": 14, "axes.titlesize": 16,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12, "legend.title_fontsize": 12,
        "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.9,
        "xtick.major.width": 0.9, "ytick.major.width": 0.9, "savefig.dpi": DPI, "figure.dpi": 100,
        "text.parse_math": False,
    })


def ref_lines(ax, unit="price", which=(90.0, 95.0, 97.5), **kw):
    for r in REF_LINES:
        if r["price"] in which:
            ax.axhline(r[unit], color=GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5, **kw)


def tint(hex_color, amount=0.55):
    r, g, b = mpl.colors.to_rgb(hex_color)
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount)


def letter(fig, ax, s, dx=0.0):
    """Panel letter at the top left of an axes, in figure coordinates (16 pt bold)."""
    bb = ax.get_position()
    fig.text(bb.x0 + dx, bb.y1 + 0.012, s, fontsize=16, fontweight="bold", ha="right", va="bottom")


def save(fig, name):
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    w, _ = fig.get_size_inches()
    if abs(w - SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {SLOT_IN} in")
    audit(fig, name)
    fig.savefig(FIG_DIR / name, dpi=DPI)
    print(f"wrote {FIG_DIR / name}")


# ---------------------------------------------------------------- checks
def _texts(fig):
    out = []
    for t in fig.findobj(mpl.text.Text):
        if t.get_visible() and t.get_text().strip() and t.get_alpha() != 0:
            out.append(t)
    return out


def audit(fig, name):
    """Owner font floors (axis labels >= 14, ticks >= 12, titles >= 16, other >= 12), every text inside the
    image, and no two text boxes overlapping. Raises on any breach."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    labels, titles = set(), set()
    for ax in fig.axes:
        labels |= {id(ax.xaxis.label), id(ax.yaxis.label)}
        titles |= {id(ax.title), id(ax._left_title), id(ax._right_title)}
    boxes = []
    for t in _texts(fig):
        size = t.get_fontsize()
        floor = 14 if id(t) in labels else 16 if id(t) in titles else 12
        if size < floor - 1e-6:
            raise ValueError(f"{name}: '{t.get_text()[:30]}' at {size} pt, floor {floor}")
        bb = t.get_window_extent(r)
        if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > W + 0.5 or bb.y1 > H + 0.5:
            raise ValueError(f"{name}: '{t.get_text()[:30]}' outside the image {bb}")
        boxes.append((t, bb))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            ov_w = min(a.x1, b.x1) - max(a.x0, b.x0)
            ov_h = min(a.y1, b.y1) - max(a.y0, b.y0)
            if ov_w > 1.0 and ov_h > 1.0:
                raise ValueError(f"{name}: text overlap '{boxes[i][0].get_text()[:25]}' and "
                                 f"'{boxes[j][0].get_text()[:25]}'")


def verify(rel_path, line, text):
    """The quote must sit verbatim on the stated 1-indexed line of the file (path relative to experiments/runs)."""
    lines = (RUNS / rel_path).read_text(encoding="utf-8").splitlines()
    if text not in lines[line - 1]:
        raise ValueError(f"quote not found at {rel_path} L{line}: {text[:40]}")
    return True


# ---------------------------------------------------------------- run data
REC = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")
MODEL_KEY = {"gpt-5.6-sol": "sol", "gpt-6-luna": "luna", "grok-4.7": "grok",
             "google/gemini-3.8-flash": "gemini", "anthropic/claude-haiku-5.5": "haiku"}
BUYER_KEY = {"anthropic/claude-haiku-5.5": "Haiku", "gpt-6-luna": "Luna", "openai/gpt-4.1-mini": "GPT-4.1-mini"}

# The phases (run directories) this section reads, by machine. experiments/invalid_429_shard3/ is never read.
# From the step A and B folders only the 9 Claude Haiku 5.5 seller markets are read (folder names with "haiku" or
# "CCCC"); the Gemini step A/B markets there use other buyers and are not part of this section.
HAIKU_ONLY = {"A", "B"}
PHASE_DIRS = {
    "frontier": ["box/frontier", "shard2/frontier"],
    "frontier_b41": ["shard2/frontier_b41"],
    "frontier_lowanchor": ["shard2/frontier_lowanchor"],
    "A_lowanchor": ["shard2/A_lowanchor"],
    "A_agycontrol": ["shard2/A_agycontrol"],
    "prereg_anchor": ["shard2/prereg_anchor"],
    "A": ["shard2/A", "shard3/A"],
    "B": ["shard2/B", "shard3/B"],
}


def run(folder):
    """Per-hour records of one run: {hour: {'line', 'asks', 'bids', 'trades', 'public', 'dms'}}."""
    path = RUNS / folder / "unified.log"
    out = {}
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = REC.search(raw)
        if m:
            d = json.loads(m.group(2))
            out[int(m.group(1))] = {"line": i, "asks": d.get("seller_asks") or {}, "bids": d.get("buyer_bids") or {},
                                    "trades": d.get("trades") or [], "public": d.get("seller_messages") or {},
                                    "dms": d.get("seller_dms") or []}
    if sorted(out) != HOURS:
        raise ValueError(f"{folder}: hours {sorted(out)}")
    return out


def catalog():
    """One row per run folder of PHASE_DIRS with its configuration and joint-criterion result."""
    rows = []
    for phase, dirs in PHASE_DIRS.items():
        for d in dirs:
            for f in sorted((RUNS / d).iterdir()):
                if not (f / "collusion_metrics.json").exists():
                    continue
                if phase in HAIKU_ONLY and not ("haiku" in f.name or "CCCC" in f.name):
                    continue
                if "invalid" in str(f):
                    raise ValueError("invalid folder reached")
                meta = json.loads((f / "experiment_metadata.json").read_text(encoding="utf-8"))["auction_config"]
                met = json.loads((f / "collusion_metrics.json").read_text(encoding="utf-8"))
                if met.get("failed_turns"):
                    raise ValueError(f"{f.name}: failed turns")
                sm = set(meta["seller_models"])
                bm = set(meta["buyer_models"])
                if len(sm) != 1 or len(bm) != 1:
                    raise ValueError(f"{f.name}: mixed models {sm} {bm}")
                jc = met["joint_criterion"]
                asks = met["avg_seller_asks_by_round"]
                if len(asks) != 15:
                    raise ValueError(f"{f.name}: {len(asks)} rounds")
                row = {"folder": f"{d}/{f.name}", "phase": phase, "seller": MODEL_KEY[sm.pop()],
                       "buyer": BUYER_KEY[bm.pop()],
                       "messaging": "on" if (meta["seller_comms_enabled"] or meta["seller_dms_enabled"]) else "off",
                       "notice": bool(meta.get("prohibition_notice")),
                       "opening": float(meta["initial_seller_ask_center"]), "seed": int(meta["seed"]),
                       "ask_index": jc["ask_index"], "trade_index": jc["trade_index"],
                       "trades_per_round": jc["trades_per_round"], "passed": bool(jc["passed"]),
                       "dms": int((met.get("dm_summary") or {}).get("total", 0))}
                for h, a in zip(HOURS, asks):
                    row[f"ask_h{h}"] = a
                rows.append(row)
    df = pd.DataFrame(rows)
    df["late_ask"] = df[[f"ask_h{h}" for h in range(11, 16)]].mean(axis=1)
    if not np.allclose((df["late_ask"] - 90) / 10, df["ask_index"], atol=1e-6):
        raise ValueError("late ask and ask index disagree")
    return df


ASK_COLS = [f"ask_h{h}" for h in HOURS]


def cell(df, n=None, **kw):
    """Rows matching every key=value; checks the row count when n is given."""
    sub = df
    for k, v in kw.items():
        sub = sub[sub[k] == v]
    if n is not None and len(sub) != n:
        raise ValueError(f"{kw}: {len(sub)} runs, expected {n}")
    return sub.sort_values("seed")


def money(x, nd=2):
    return f"${x:,.{nd}f}"


# ---------------------------------------------------------------- derived tables (written by S44/build_data.py)
# Cartel words: a private message counts when it contains a word that starts with one of these stems
# (case-insensitive, at a word start): hold (hold, holds, holding, holdout), held, floor, coordinat, anchor,
# disciplin, cartel.
CARTEL_STEMS = ["hold", "held", "floor", "coordinat", "anchor", "disciplin", "cartel"]
CARTEL_RE = re.compile(r"\b(" + "|".join(CARTEL_STEMS) + r")\w*", re.I)


def load(name):
    """A derived table of data/s44/: runs, seller_asks or dms."""
    return pd.read_csv(DATA_DIR / f"{name}.csv")


def num(x, nd=2):
    """A signed number with nd decimals, without a minus sign on a value that rounds to zero."""
    s = f"{x:.{nd}f}"
    return s[1:] if s.startswith("-") and float(s) == 0 else s
