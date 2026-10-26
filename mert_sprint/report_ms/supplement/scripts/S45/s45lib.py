"""Shared loaders, quote registry and drawing helpers for the S4.5 figures
(what the seller agents said, pinned on what prices did).

Inputs, all read only:
  experiments/runs/<run>/unified.log          one JSON record per hour: seller asks, buyer bids, trades,
                                              public seller messages, private seller-to-seller messages
  experiments/runs/<run>/Seller <name>.md     each seller's private notes (reflection, plans, scratchpad)
  experiments/runs/<run>/collusion_metrics.json   joint_criterion (passed, ask_index)
  ApartAICollusion origin/main:report/data/dg/market_by_hour.csv   Daniel's per-hour market table (git show)
Style (colors, reference lines, font floors) comes from report_ms/scripts/lib/style.py.

Every quote a figure shows is an entry of quotes.py. Each entry is checked against its source file and line
when that module is imported, and each call-out fragment is checked to be a verbatim part of the entry.
save() refuses a figure whose text breaks the font floors, overlaps other text or leaves the canvas.
"""
import json
import re
import subprocess
import sys
from io import StringIO
from pathlib import Path

import matplotlib as mpl
from matplotlib.text import Text

HERE = Path(__file__).resolve().parent
MS = HERE.parents[2]                                   # report_ms/
REPO = MS.parent                                       # apart-collusion-sprint-2026/
RUNS = REPO / "experiments" / "runs"
DANIEL_REPO = REPO.parent / "ApartAICollusion"
FIGURES = MS / "supplement" / "figures" / "S45"

sys.path.insert(0, str(MS / "scripts" / "lib"))
import style  # noqa: E402  (report_ms/scripts/lib/style.py)

HOURS = list(range(1, 16))
XTICKS = [1, 3, 5, 7, 9, 11, 13, 15]
REC = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")


# ----------------------------------------------------------------------------------------------- run data
def run(folder):
    """Per-hour records of one run: {hour: {'line', 'asks', 'bids', 'trades', 'public', 'dms'}}."""
    path = RUNS / folder / "unified.log"
    out = {}
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        m = REC.search(raw)
        if not m:
            continue
        d = json.loads(m.group(2))
        out[int(m.group(1))] = {"line": i, "asks": d.get("seller_asks") or {}, "bids": d.get("buyer_bids") or {},
                                "trades": d.get("trades") or [], "public": d.get("seller_messages") or {},
                                "dms": d.get("seller_dms") or []}
    if sorted(out) != HOURS:
        raise ValueError(f"{folder}: hours {sorted(out)}")
    return out


def sellers(rec):
    names = set()
    for h in HOURS:
        names |= set(rec[h]["asks"])
    return sorted(names)


def ask_path(rec, seller):
    """A seller's posted ask by hour; None where the seller posted none."""
    return [rec[h]["asks"].get(seller) for h in HOURS]


def mean_ask_path(rec):
    out = []
    for h in HOURS:
        a = [v for v in rec[h]["asks"].values() if v is not None]
        out.append(sum(a) / len(a) if a else None)
    return out


def best_bid_path(rec):
    return [max((v for v in rec[h]["bids"].values() if v is not None), default=None) for h in HOURS]


def trades(rec):
    """[(hour, seller, price)] for every trade in the run."""
    return [(h, t.get("seller_id"), t.get("price")) for h in HOURS for t in rec[h]["trades"]]


def criterion(folder):
    """(passed, ask_index) from the run's collusion_metrics.json."""
    jc = json.loads((RUNS / folder / "collusion_metrics.json").read_text(encoding="utf-8"))["joint_criterion"]
    return bool(jc["passed"]), float(jc["ask_index"])


def verdict(folder):
    passed, idx = criterion(folder)
    return f"{'PASS' if passed else 'FAIL'}, ask index {idx:+.2f}".replace("+-0.00", "0.00").replace("-0.00", "0.00")


NOTE_FIELD = re.compile(r'^\s*"(reflection|plan_for_this_hour|plan_for_message|scratch_pad_update|new_memory)"'
                        r'\s*:\s*"(.*)",?\s*$')


def private_sentences(folder, seller_file):
    """Sentences of a seller's private notes: [(hour, field, line, sentence)]. Hour is the Response block's round."""
    out, hour = [], None
    for i, line in enumerate((RUNS / folder / seller_file).read_text(encoding="utf-8").splitlines(), start=1):
        m = re.match(r"## Response: Round (\d+)", line)
        if m:
            hour = int(m.group(1))
            continue
        if line.startswith("## Prompt"):
            hour = None
        fm = NOTE_FIELD.match(line) if hour else None
        if not fm:
            continue
        for s in re.split(r"(?<=[.!?])\s+|\\n+", fm.group(2)):
            s = s.strip().lstrip("-# ").strip()
            if s:
                out.append((hour, fm.group(1), i, s))
    return out


def daniel_market(run_id):
    """Daniel's market_by_hour rows for one run, read with git show from his repository's origin/main."""
    import pandas as pd
    csv = subprocess.run(["git", "-C", str(DANIEL_REPO), "show", "origin/main:report/data/dg/market_by_hour.csv"],
                         capture_output=True, check=True).stdout.decode("utf-8")
    df = pd.read_csv(StringIO(csv))
    sub = df[df["run_id"] == run_id].sort_values("hour")
    if list(sub["hour"]) != HOURS:
        raise ValueError(f"run {run_id}: hours {list(sub['hour'])} in Daniel's market_by_hour.csv")
    return sub


# ----------------------------------------------------------------------------------------------- drawing
CHANNEL_KEY = {"public": "public message", "dm": "private message", "note": "private note"}


def box(channel, color):
    """Call-out box by channel: public solid border, private message dashed border, private note tinted fill."""
    if channel == "public":
        return dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.3)
    if channel == "dm":
        return dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.3, ls=(0, (3.5, 2.2)))
    if channel == "note":
        return dict(boxstyle="round,pad=0.35", fc=style.tint(color, 0.82), ec="none")
    raise ValueError(channel)


def wrap(text, width):
    """Greedy word wrap to at most `width` characters per line."""
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def callout(ax, q, xy, xytext, width, color, ha="left", va="bottom", header=True, rel=(0.5, 0.0),
            frag=None, header_side="left", dot=True, coords="data", zorder=6, header_below=False,
            header_text=None):
    """A quote box (channel-styled) with a leader to the point xy, and the speaker line above the box
    (below it with header_below). q is a quotes.Q entry; frag overrides q.frag (checked against the log)."""
    frag = q.check_fragment(frag) if frag else q.frag
    body = "“" + wrap(frag, width) + "”"
    ann = ax.annotate(body, xy=xy, xytext=xytext, textcoords=coords, ha=ha, va=va, fontsize=12,
                      fontstyle="italic", linespacing=1.2, bbox=box(q.channel, color), zorder=zorder,
                      annotation_clip=False,
                      arrowprops=None if xy is None else dict(arrowstyle="-", color=color, lw=1.0, shrinkA=0,
                                                              shrinkB=3, relpos=rel))
    if dot and xy is not None:
        ax.plot([xy[0]], [xy[1]], ls="none", marker="o", ms=5.5, mfc=color, mec="black", mew=0.7,
                zorder=zorder + 1, clip_on=False)
    if header:
        hx = 0.0 if header_side == "left" else 1.0
        ax.annotate(header_text or q.header, xy=(hx, 0.0 if header_below else 1.0), xycoords=ann,
                    xytext=(0, -7.5 if header_below else 7.5), textcoords="offset points", ha=header_side,
                    va="top" if header_below else "bottom", fontsize=12, color="black", zorder=zorder,
                    bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))
    return ann


def channel_key(fig, y, channels=("public", "dm", "note"), color="#444444", x0=0.5):
    """One row of sample boxes that explains the call-out styles, centered at figure x0."""
    labels = [CHANNEL_KEY[c] for c in channels]
    texts = []
    for c, lab in zip(channels, labels):
        texts.append(fig.text(0, y, lab, fontsize=12, ha="left", va="center", bbox=box(c, color)))
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W = fig.get_size_inches()[0] * fig.dpi
    widths = [t.get_window_extent(r).width / W for t in texts]
    gap = 0.045
    x = x0 - (sum(widths) + gap * (len(widths) - 1)) / 2
    for t, w in zip(texts, widths):
        t.set_x(x)
        x += w + gap
    return texts


def hour_axis(ax, label=True):
    ax.set_xlim(0.5, 15.5)
    ax.set_xticks(XTICKS)
    if label:
        ax.set_xlabel("Hour")


def panel_letter(fig, ax, letter, dx=-0.0, dy=0.008, x=None):
    bb = ax.get_position()
    fig.text(bb.x0 + dx if x is None else x, bb.y1 + dy, letter, fontsize=16, fontweight="bold",
             ha="left", va="bottom")


# ----------------------------------------------------------------------------------------------- saving
def _text_extent(t, r):
    p = t.get_bbox_patch()
    return (p if p is not None else t).get_window_extent(r)


def check_layout(fig):
    """Font floors (text >= 12 pt, axis labels >= 14 pt, titles >= 16 pt), no text outside the canvas,
    no two texts overlapping. Returns a list of problems."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.get_size_inches() * fig.dpi
    ticks, shown = set(), []
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            for tk in axis.get_major_ticks() + axis.get_minor_ticks():
                ticks.update([tk.label1, tk.label2])
            shown += [t for t in axis.get_ticklabels() if t.get_visible() and t.get_text()]
    texts = [t for t in fig.findobj(Text) if t not in ticks and t.get_visible() and t.get_text().strip()
             and t.get_alpha() != 0]
    texts += shown
    probs = []
    for ax in fig.axes:
        for lab in (ax.xaxis.label, ax.yaxis.label):
            if lab.get_text() and lab.get_fontsize() < 14:
                probs.append(f"axis label {lab.get_text()!r} {lab.get_fontsize()} pt")
        if ax.title.get_text() and ax.title.get_fontsize() < 16:
            probs.append(f"title {ax.title.get_text()!r} {ax.title.get_fontsize()} pt")
    ext = []
    for t in texts:
        if t.get_fontsize() < 12:
            probs.append(f"text {t.get_text()[:30]!r} {t.get_fontsize()} pt")
        e = _text_extent(t, r)
        if e.x0 < -0.5 or e.y0 < -0.5 or e.x1 > W + 0.5 or e.y1 > H + 0.5:
            probs.append(f"outside canvas: {t.get_text()[:40]!r}")
        ext.append((t, e))
    for i in range(len(ext)):
        for j in range(i + 1, len(ext)):
            a, b = ext[i][1], ext[j][1]
            if min(a.x1, b.x1) - max(a.x0, b.x0) > 1 and min(a.y1, b.y1) - max(a.y0, b.y0) > 1:
                probs.append(f"overlap: {ext[i][0].get_text()[:30]!r} / {ext[j][0].get_text()[:30]!r}")
    return probs


def save(fig, name):
    w, h = fig.get_size_inches()
    if abs(w - style.SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {style.SLOT_IN} in")
    probs = check_layout(fig)
    if probs:
        import tempfile
        draft = Path(tempfile.gettempdir()) / f"s45_draft_{name}"
        fig.savefig(draft, dpi=style.DPI)
        raise ValueError(f"{name}: layout problems (draft at {draft}):\n  " + "\n  ".join(probs))
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, dpi=style.DPI)
    print(f"wrote {path} ({w:.2f} x {h:.2f} in)")


def setup():
    style.setup()
    mpl.rcParams["figure.dpi"] = 100
