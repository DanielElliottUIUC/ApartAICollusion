"""Print-size checks shared by the report's body figures (new sprint code).

Every body figure is drawn with matplotlib figsize equal to its printed size (6.5 in wide: Letter with 1 in
margins) and saved at 300 dpi, so a font size in points is the printed size in points. `save` refuses to write a
figure that breaks the print spec:

  - width exactly 6.5 in and height at most the figure's limit;
  - every visible text at least 8 pt;
  - no visible text outside the figure, and no two visible texts overlapping (bounding boxes, 0.01 in slack).

It prints the file's pixel size, print size and smallest font, which the report's figure list records.
"""

from itertools import combinations
from pathlib import Path

from matplotlib.text import Text

TEXT_WIDTH_IN = 6.5
DPI = 300
MIN_PT = 8.0
SLACK_IN = 0.01


def _texts(fig):
    out = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        if t.axes is not None and not t.axes.get_visible():
            continue
        out.append(t)
    return out


def check(fig, max_h_in: float, min_pt: float = MIN_PT, allow_overlap=()) -> dict:
    """Raise on any breach of the print spec; return the measured sizes."""
    w, h = fig.get_size_inches()
    if abs(w - TEXT_WIDTH_IN) > 1e-6:
        raise ValueError(f"width {w} in, the text width is {TEXT_WIDTH_IN} in")
    if h > max_h_in + 1e-6:
        raise ValueError(f"height {h} in, the limit is {max_h_in} in")
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    dpi = fig.dpi
    texts = _texts(fig)
    sizes = [t.get_fontsize() for t in texts]
    small = [(t.get_text()[:40], t.get_fontsize()) for t in texts if t.get_fontsize() < min_pt - 1e-9]
    if small:
        raise ValueError(f"text below {min_pt} pt: {small}")
    boxes = [(t, t.get_window_extent(r)) for t in texts]
    fb = fig.bbox
    slack = SLACK_IN * dpi
    outside = [t.get_text()[:40] for t, b in boxes
               if b.x0 < fb.x0 - slack or b.x1 > fb.x1 + slack or b.y0 < fb.y0 - slack or b.y1 > fb.y1 + slack]
    if outside:
        raise ValueError(f"text outside the figure: {outside}")
    allowed = {frozenset(p) for p in allow_overlap}
    clashes = []
    for (t1, b1), (t2, b2) in combinations(boxes, 2):
        ix = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
        iy = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
        if ix > slack and iy > slack:
            if frozenset((t1.get_text(), t2.get_text())) in allowed:
                continue
            clashes.append((t1.get_text()[:30], t2.get_text()[:30]))
    if clashes:
        raise ValueError(f"overlapping text: {clashes}")
    return {"width_in": round(w, 3), "height_in": round(h, 3), "min_font_pt": min(sizes), "n_texts": len(texts)}


def save(fig, path: Path, max_h_in: float, **kw) -> dict:
    """Check the figure, then write it as a 300 dpi PNG (no tight cropping, so the print size is kept)."""
    m = check(fig, max_h_in, **kw)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, metadata={"Software": None})
    from PIL import Image  # matplotlib depends on Pillow

    with Image.open(path) as im:
        m["px"] = im.size
    m["file"] = str(path)
    print(f"wrote {path}: {m['px'][0]} x {m['px'][1]} px, {m['width_in']} x {m['height_in']} in at {DPI} dpi, "
          f"smallest font {m['min_font_pt']} pt ({m['n_texts']} texts)")
    return m
