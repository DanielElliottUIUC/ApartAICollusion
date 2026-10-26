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
import numpy as np
from matplotlib.text import Text

HERE = Path(__file__).resolve().parent
MS = HERE.parents[2]                                   # report_ms/
REPO = MS.parent                                       # apart-collusion-sprint-2026/
RUNS = REPO / "experiments" / "runs"
DANIEL_REPO = REPO.parent / "ApartAICollusion"
FIGURES = MS / "supplement" / "figures" / "S45"

sys.path.insert(0, str(MS / "scripts" / "lib"))
sys.dont_write_bytecode = True        # read style.py without writing a cache into report_ms/scripts/lib
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


def settle_hour(rec):
    """First hour from which every seller posts the same ask as in hour 15, and that ask."""
    final = set(rec[15]["asks"].values())
    if len(final) != 1:
        raise ValueError("the hour-15 asks differ")
    h = 15
    while h > 1 and len(rec[h - 1]["asks"]) == len(rec[15]["asks"]) and set(rec[h - 1]["asks"].values()) == final:
        h -= 1
    return h, final.pop()


def criterion(folder):
    """(passed, ask_index) from the run's collusion_metrics.json."""
    jc = json.loads((RUNS / folder / "collusion_metrics.json").read_text(encoding="utf-8"))["joint_criterion"]
    return bool(jc["passed"]), float(jc["ask_index"])


def verdict(folder):
    passed, idx = criterion(folder)
    return f"{'PASS' if passed else 'FAIL'}, ask index {idx:.2f}".replace("-0.00", "0.00")


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
HOUR_BAND = "#ECECEC"      # shading that marks one hour across stacked panels
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
            header_text=None, header_bg=True):
    """A quote box (channel-styled) with a leader to the point xy, and the speaker line above the box
    (below it with header_below). q is a quotes.Q entry; frag overrides q.frag (checked against the log).
    The leader leaves the box at rel (fractions of the text block) and runs under the box to its edge."""
    frag = q.check_fragment(frag) if frag else q.frag
    body = "“" + wrap(frag, width) + "”"
    tr = ax.transData if coords == "data" else ax.transAxes
    ann = ax.text(xytext[0], xytext[1], body, transform=tr, ha=ha, va=va, fontsize=12, fontstyle="italic",
                  linespacing=1.2, bbox=box(q.channel, color), zorder=zorder, clip_on=False)
    if xy is not None:
        ax.annotate("", xy=xy, xycoords="data", xytext=rel, textcoords=ann, annotation_clip=False,
                    zorder=zorder - 0.5, arrowprops=dict(arrowstyle="-", color=color, lw=1.0, shrinkA=0,
                                                         shrinkB=3))
    if dot and xy is not None:
        ax.plot([xy[0]], [xy[1]], ls="none", marker="o", ms=5.5, mfc=color, mec="black", mew=0.7,
                zorder=zorder + 1, clip_on=False)
    if header:
        hx = 0.0 if header_side == "left" else 1.0
        ax.annotate(header_text or q.header, xy=(hx, 0.0 if header_below else 1.0), xycoords=ann,
                    xytext=(0, -7.5 if header_below else 7.5), textcoords="offset points", ha=header_side,
                    va="top" if header_below else "bottom", fontsize=12, color="black", zorder=zorder,
                    bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none") if header_bg else None)
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


def chat_axes(fig, rect, labels, color, rotate=False):
    """Lanes for a chat strip, top to bottom in the order of labels. Lane i spans y in [n-1-i, n-i]."""
    ax = fig.add_axes(rect)
    n = len(labels)
    ax.set_ylim(0, n)
    ax.set_xlim(0.5, 15.5)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for i, name in enumerate(labels):
        y0 = n - 1 - i
        ax.axhline(y0, color=style.LIGHT, lw=0.8, zorder=0)
        ax.text(0.4 if not rotate else 0.05, y0 + 0.5, name, ha="right" if not rotate else "center",
                va="center", fontsize=14,
                color=color, rotation=90 if rotate else 0, rotation_mode="anchor")
    return ax


def lane_bubble(ax_c, ax_p, q, lane, price, x, align, width, color, header_text=None):
    """A bubble in lane `lane` at the quote's hour, a dotted pin down through the price panel,
    and a dot on the price line (the speaker's ask that hour)."""
    h = q.hour
    rel = (0.0, 0.0) if align == "left" else (1.0, 0.0)
    if align == "right" and x - h > 0.6:
        rel = (min(0.9, max(0.1, 1 - (x - h) / 6)), 0.0)
    callout(ax_c, q, (h, lane + 0.07), (x, lane + 0.24), width, color, ha=align, rel=rel, header_side=align,
            header_text=header_text or q.lane_header, dot=False)
    ax_c.plot([h, h], [0, lane + 0.07], color=style.GRAY, lw=0.7, ls=(0, (1, 2)), zorder=1, clip_on=False)
    ax_c.plot([h], [lane + 0.07], marker="o", ms=4.5, color=color, zorder=7)
    ax_p.axvline(h, color=style.GRAY, lw=0.8, ls=(0, (1, 2)), zorder=1)
    ax_p.plot([h], [price], ls="none", marker="o", ms=5.5, mfc=color, mec="black", mew=0.7, zorder=6)


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
    probs += _crossings(fig, ext)
    return probs


def _dense(pts, step=1.5):
    """Points along a display-space polyline, at most `step` px apart; NaN rows break the line."""
    out = []
    for p, q in zip(pts[:-1], pts[1:]):
        if np.isnan(p).any() or np.isnan(q).any():
            continue
        n = max(1, int(np.hypot(*(q - p)) / step))
        out.append(p + (q - p) * np.linspace(0, 1, n + 1)[:, None])
    return np.vstack(out) if out else np.empty((0, 2))


def _crossings(fig, ext):
    """Lines, markers and leaders that run through text. Data lines (zorder >= 2), markers and leaders may
    not touch any text; reference lines and pins (zorder < 2) may pass behind an opaque box only."""
    from matplotlib.text import Annotation
    marks = []                                    # (label, points Nx2, radius px, is_data, own text)
    for ax in fig.axes:
        clip = ax.bbox
        for ln in ax.get_lines():
            if not ln.get_visible():
                continue
            xy = ln.get_transform().transform(np.asarray(ln.get_xydata(), float))
            data = ln.get_zorder() >= 2
            if ln.get_linestyle() not in ("None", "", " "):
                pts = _dense(xy)
                if ln.get_clip_on() and len(pts):
                    pts = pts[(pts[:, 0] >= clip.x0 - 1) & (pts[:, 0] <= clip.x1 + 1)
                              & (pts[:, 1] >= clip.y0 - 1) & (pts[:, 1] <= clip.y1 + 1)]
                marks.append((f"line z{ln.get_zorder()}", pts, ln.get_linewidth() * fig.dpi / 144, data, None))
            if ln.get_marker() not in (None, "None", "", " "):
                pts = xy[~np.isnan(xy).any(axis=1)]
                marks.append(("marker", pts, ln.get_markersize() * fig.dpi / 144, True, None))
    for a in fig.findobj(Annotation):
        if a.arrow_patch is not None and a.get_visible():
            path = a.arrow_patch.get_path()
            own = {a} | ({a.anncoords} if isinstance(a.anncoords, Text) else set())
            marks.append(("leader", _dense(path.vertices), 0.5, True, own))
    probs = []
    for t, e in ext:
        patch = t.get_bbox_patch()
        opaque = patch is not None and patch.get_facecolor()[3] > 0
        x0, y0, x1, y1 = e.x0 + 1, e.y0 + 1, e.x1 - 1, e.y1 - 1
        for label, pts, rad, data, own in marks:
            if (own and t in own) or len(pts) == 0 or (opaque and not data):
                continue
            hit = ((pts[:, 0] > x0 - rad) & (pts[:, 0] < x1 + rad) & (pts[:, 1] > y0 - rad)
                   & (pts[:, 1] < y1 + rad))
            if hit.any():
                probs.append(f"{label} runs through text {t.get_text()[:30]!r}")
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
