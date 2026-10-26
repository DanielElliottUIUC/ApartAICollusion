"""Build the S4.3 supplement: data, the nine figures and the Markdown fragment sections/S43.md.

Every number in a caption or explanation is computed by the figure script that draws the figure; this script
only runs them in order and writes their text into the fragment.

Run from anywhere:  python report_ms/supplement/scripts/S43/build_section.py
"""
import importlib
import re
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import s43lib as L  # noqa: E402

MODULES = [
    "make_s43_01_ask_paths",
    "make_s43_02_two_runs",
    "make_s43_03_matching_asks",
    "make_s43_04_haiku_buyers",
    "make_s43_05_sol_buyers",
    "make_s43_06_talk_within",
    "make_s43_07_grok_floors",
    "make_s43_08_judge",
    "make_s43_09_bertrand",
]
OUT = L.SUP / "sections" / "S43.md"


def full_paths(text):
    """Supplement-relative paths in Source lines become repository-relative."""
    return re.sub(r"(?<![\w/])(data/s43/|scripts/S43/)", r"report_ms/supplement/\1", text)


def main():
    runpy.run_path(str(HERE / "build_s43_data.py"), run_name="__main__")
    parts = []
    for i, name in enumerate(MODULES, start=1):
        mod = importlib.import_module(name)
        out = mod.make()
        if not out["file"].startswith(f"S43_{i:02d}_"):
            raise ValueError(f"{name}: file {out['file']} is out of order")
        for key in ("caption", "shows", "title"):
            if "—" in out[key] or "–" in out[key]:
                raise ValueError(f"{name}: dash in {key}")
        parts.append(
            f"### Figure S43.{i}. {out['title']}\n\n"
            f"![](figures/S43/{out['file']})\n\n"
            f"**Caption.** {out['caption']}\n\n"
            f"**What it shows.** {out['shows']}\n\n"
            f"Source: {full_paths(out['source'])}\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT} with {len(parts)} figures")


if __name__ == "__main__":
    main()
