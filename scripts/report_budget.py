"""Instant page-budget estimate for report/REPORT.md, per section, without pandoc or Word.

scripts/render_report.py (pandoc + Word COM) gives the real page count but takes a minute or two; this gives an
estimate in under a second, to plan cuts section by section before re-rendering. Standard library only.

    python scripts/report_budget.py [path] [--target 8] [--drop "Figure 2,Table 1"] [--json]

Like render_report.py, it strips HTML comments, `<sup>1</sup>` and the "### TODO(verify): ..." block (up to the
next `---` line), and the body is everything before the "## Code and Data" heading (title block through the
Conclusion). Sections after that cut (References, appendices, ...) are totalled separately: they cost no body pages.

Model (Letter, 1-inch margins, Arial 11 pt, pandoc's default docx styles):
    pages = prose_words / 420 + 0.45 * figures + sum over tables of (0.05 * data_rows + 0.08)
Prose: headings, paragraphs, list items and table captions (a `*Table N. ...*` caption wraps like prose, so it
counts at the prose rate and belongs to its table). Not prose: table rows, and figure lines (the alt-text caption is
in the 0.45). Data rows exclude the header and |---| rows; the 0.08 covers the header row and spacing. --target N
gives the prose words to cut to reach N pages, as is and after dropping the --drop items (with their captions).

Calibration: on the Oct 25 20:36 render (report/build/body.md = the body of REPORT.md at e8c48ed) Word counted
20 pages and 8,331 words; this tokenizer counts 8,326 there. The planned constants above, unchanged, estimate
21.6 pages (21.8 counting the 111-word TODO(verify) block that render still contained): 1.6-1.8 pages, about 8%,
high, which is within the 2-page tolerance and on the safe side for a cap. Re-render to confirm.
"""

import argparse
import itertools
import json
import math
import pathlib
import re
import sys

WORDS_PER_PAGE, FIGURE_PAGES, TABLE_ROW_PAGES, TABLE_FIXED_PAGES = 420, 0.45, 0.05, 0.08
CUT = "## Code and Data"
ABSTRACT_RANGE = (150, 250)


def count_words(line: str) -> int:
    line = re.sub(r"^\s*(#+|[-*+]|\d+\.)\s+", "", line)  # heading and list markers
    return len(re.sub(r"[*`]", "", line).split())


def strip(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"### TODO\(verify\):.*?(?=\n---\n)", "", text, flags=re.S)
    return text.replace("<sup>1</sup>", "")


def table_pages(t: dict) -> float:
    return TABLE_ROW_PAGES * t["rows"] + TABLE_FIXED_PAGES


def parse(text: str) -> list[dict]:
    """Split at H2/H3 headings; per section count prose words, tables (data rows, caption) and figures."""
    def new(title: str, level: int) -> dict:
        return {"title": title, "level": level, "words": 0, "tables": [], "figures": []}
    secs, in_table = [new("(title block)", 1)], False
    for line in text.splitlines():
        s = line.strip()
        if m := re.match(r"(#{2,3}) (.+)", s):
            secs.append(new(m.group(2), len(m.group(1))))
        sec = secs[-1]
        if s.startswith("|"):
            if not in_table:
                sec["tables"].append({"label": f"table in {sec['title']}", "rows": -1, "caption_words": 0})
            in_table = True
            if not re.fullmatch(r"\|[\s:|-]+\|?", s):
                sec["tables"][-1]["rows"] += 1  # starts at -1, so the header row is not counted
            continue
        in_table = False
        if s.startswith("!["):
            m = re.match(r"!\[(Figure \w+)", s)
            sec["figures"].append(m.group(1) if m else f"figure in {sec['title']}")
        elif s and s != "---":
            sec["words"] += (n := count_words(s))
            m = re.match(r"\*(Table \w+)\.", s)
            if m and sec["tables"] and not sec["tables"][-1]["caption_words"]:
                sec["tables"][-1].update(label=m.group(1), caption_words=n)
    for sec in secs:
        sec["pages"] = round(sec["words"] / WORDS_PER_PAGE + FIGURE_PAGES * len(sec["figures"])
                             + sum(table_pages(t) for t in sec["tables"]), 2)
    return [s for s in secs if s["words"] or s["tables"] or s["figures"]]


def roll_up_h2(secs: list[dict]) -> list[dict]:
    out = []
    for s in secs:
        if s["level"] <= 2 or not out:
            out.append({"title": s["title"], "words": 0, "rows": 0, "figures": 0, "pages": 0.0})
        o = out[-1]
        o.update(words=o["words"] + s["words"], rows=o["rows"] + sum(t["rows"] for t in s["tables"]),
                 figures=o["figures"] + len(s["figures"]), pages=round(o["pages"] + s["pages"], 2))
    return out


def todo_markers(raw: str) -> list[dict]:
    """TODO( markers and HTML comments in the body of the raw file, by line number."""
    lines = raw.splitlines()
    end = next((i for i, line in enumerate(lines) if line.startswith(CUT)), len(lines))
    return [{"line": i, "kind": "+".join(k for k, pat in (("comment", "<!--"), ("TODO", "TODO(")) if pat in line),
             "text": line.strip()[:100]}
            for i, line in enumerate(lines[:end], 1) if "<!--" in line or "TODO(" in line]


def budget(path: pathlib.Path, target: float | None, drop: list[str]) -> dict:
    raw = path.read_text(encoding="utf-8")
    text = strip(raw)
    cut = text.find(CUT)
    body, after = (text[:cut], text[cut:]) if cut > 0 else (text, "")
    secs = parse(body)
    for s, cum in zip(secs, itertools.accumulate(s["pages"] for s in secs)):
        s["cum_pages"] = round(cum, 2)
    words = sum(s["words"] for s in secs)
    tables = [t for s in secs for t in s["tables"]]
    figures = [f for s in secs for f in s["figures"]]
    parts = {"prose": words / WORDS_PER_PAGE, "figures": FIGURE_PAGES * len(figures),
             "tables": sum(table_pages(t) for t in tables)}
    pages = sum(parts.values())
    abstract = next((s["words"] - count_words(s["title"]) for s in secs if s["title"].lower() == "abstract"), 0)
    dropped, drop_cost = [], 0.0
    for label in drop:
        t = next((t for t in tables if t["label"].lower() == label.lower()), None)
        if t or label.lower() in (f.lower() for f in figures):
            drop_cost += table_pages(t) + t["caption_words"] / WORDS_PER_PAGE if t else FIGURE_PAGES
            dropped.append(label)
    out = {
        "file": str(path), "sections": secs, "after_cut": roll_up_h2(parse(after)),
        "body": {"prose_words": words, "table_rows": sum(t["rows"] for t in tables), "tables": len(tables),
                 "figures": len(figures), "pages": round(pages, 2),
                 "pages_by_part": {k: round(v, 2) for k, v in parts.items()}},
        "abstract": {"words": abstract, "range": ABSTRACT_RANGE,
                     "pass": ABSTRACT_RANGE[0] <= abstract <= ABSTRACT_RANGE[1]},
        "constants": {"words_per_page": WORDS_PER_PAGE, "figure_pages": FIGURE_PAGES,
                      "table_row_pages": TABLE_ROW_PAGES, "table_fixed_pages": TABLE_FIXED_PAGES},
        "todos": todo_markers(raw),
    }
    if target is not None:
        def cut_words(p: float) -> int:
            return max(0, math.ceil((p - target) * WORDS_PER_PAGE))
        out["target"] = {
            "pages": target,
            "keep_all": {"cut_prose_words": cut_words(pages), "max_prose_words": words - cut_words(pages)},
            "drop": {"dropped": dropped, "not_found": [d for d in drop if d not in dropped],
                     "pages_saved": round(drop_cost, 2), "cut_prose_words": cut_words(pages - drop_cost)},
        }
    return out


def print_report(r: dict) -> None:
    b, c = r["body"], r["constants"]
    print(f"{r['file']}: body = start .. '{CUT}' (HTML comments and TODO(verify) block stripped)\n")
    print(f"{'Section':<52}{'Words':>7}{'Rows':>6}{'Figs':>6}{'Pages':>7}{'Cum':>7}")
    for s in r["sections"]:
        name = ("  " if s["level"] == 3 else "") + s["title"]
        print(f"{name[:51]:<52}{s['words']:>7,}{sum(t['rows'] for t in s['tables']):>6}"
              f"{len(s['figures']):>6}{s['pages']:>7.2f}{s['cum_pages']:>7.2f}")
    print(f"{'BODY TOTAL':<52}{b['prose_words']:>7,}{b['table_rows']:>6}{b['figures']:>6}{b['pages']:>7.2f}")
    print("\nAfter the cut (not counted against the cap):")
    for s in r["after_cut"]:
        print(f"{s['title'][:51]:<52}{s['words']:>7,}{s['rows']:>6}{s['figures']:>6}{s['pages']:>7.2f}")
    a = r["abstract"]
    print(f"\nAbstract: {a['words']} words, {'PASS' if a['pass'] else 'FAIL'} ({a['range'][0]}-{a['range'][1]})")
    p = b["pages_by_part"]
    print(f"Estimated body pages (Letter, 1in margins, Arial 11pt): {b['pages']:.1f}"
          f" = prose {p['prose']:.1f} ({b['prose_words']:,} words / {c['words_per_page']})"
          f" + figures {p['figures']:.2f} ({b['figures']} x {c['figure_pages']})"
          f" + tables {p['tables']:.2f} ({b['tables']} tables: {b['table_rows']} rows x {c['table_row_pages']}"
          f" + {c['table_fixed_pages']} each)\nCalibration: Oct 25 render = 20 Word pages, estimated 21.6 (~8% high).")
    if "target" in r:
        t, d = r["target"], r["target"]["drop"]
        print(f"\nTarget {t['pages']:g} pages:")
        print(f"  keep all tables and figures: cut {t['keep_all']['cut_prose_words']:,} prose words"
              f" (keep at most {t['keep_all']['max_prose_words']:,})")
        print(f"  drop {', '.join(d['dropped']) or 'nothing'} (saves {d['pages_saved']:.2f} pages incl. captions):"
              f" cut {d['cut_prose_words']:,} prose words")
        if d["not_found"]:
            print(f"  not found, ignored: {', '.join(d['not_found'])}")
    print(f"\nTODO( markers and HTML comments left in the body ({len(r['todos'])}; delete before rendering):")
    for t in r["todos"]:
        print(f"  line {t['line']:>4} [{t['kind']}] {t['text']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=str(pathlib.Path(__file__).resolve().parents[1] / "report/REPORT.md"))
    ap.add_argument("--target", type=float, help="page cap to budget for, e.g. 8")
    ap.add_argument("--drop", default="Figure 2,Table 1", help="figures/tables for the 2nd --target scenario")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # section titles contain non-ASCII (e.g. 2×2)
    r = budget(pathlib.Path(args.path), args.target, [d.strip() for d in args.drop.split(",") if d.strip()])
    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print_report(r)


if __name__ == "__main__":
    sys.exit(main())
