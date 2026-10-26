"""Build every S41 figure and write the section fragment supplement/sections/S41.md.

Run: python build_s41.py   (from any directory). Every number in the fragment comes from the figure scripts.
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import s41_lib as L  # noqa: E402

MODULES = ["make_s41_01_reports_by_market", "make_s41_02_report_timing", "make_s41_03_peer_talk",
           "make_s41_04_seller_labels", "make_s41_05_offer_position", "make_s41_06_gpt41_arms",
           "make_s41_07_plea_2x2", "make_s41_08_seat_position", "make_s41_09_ask_change"]
BANNED = ["—", "–"]          # em and en dashes


def main():
    parts = []
    for name in MODULES:
        d = importlib.import_module(name).make()
        text = "\n".join([
            f"### Figure {d['id']}. {d['title']}",
            "",
            f"![](figures/S41/{d['file']})",
            "",
            f"Caption. {d['caption']}",
            "",
            f"What it shows. {d['shows']}",
            "",
            f"Source: {d['source']} Script: `supplement/scripts/S41/{name}.py`.",
            "",
        ])
        for ch in BANNED:
            if ch in text:
                raise ValueError(f"{name}: dash character {ch!r} in the text")
        parts.append(text)
    out = L.SUPP / "sections" / "S41.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
