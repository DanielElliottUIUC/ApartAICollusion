"""Build the S4.2 supplement section: run every figure script and write supplement/sections/S42.md.

Each make_NN_*.py module draws its PNG and returns its title, caption, explanation and source, with every
number computed from the data in the same run. This script only orders and formats them.

    python report_ms/supplement/scripts/S42/build_S42.py
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))

import s42lib as L  # noqa: E402

MODULES = ["make_01_ask_by_hour", "make_02_trades_by_hour", "make_03_profit", "make_04_profit_vs_ask",
           "make_05_hour3", "make_06_dispersion", "make_07_channels", "make_08_labels_by_hour",
           "make_09_suspicion_by_text"]
OUT = L.SUPP / "sections" / "S42.md"


def main():
    blocks = []
    for i, name in enumerate(MODULES, start=1):
        e = importlib.import_module(name).entry()
        blocks.append(
            f"### Figure S42.{i}. {e['title']}\n\n"
            f"![](figures/S42/{e['file']})\n\n"
            f"**Caption.** {e['caption']}\n\n"
            f"**What it shows.** {e['shows']}\n\n"
            f"Source: {e['source']}\n")
    text = "\n".join(blocks)
    for bad in ("—", "–"):
        if bad in text:
            raise ValueError(f"dash character {bad!r} in the section text")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT} ({len(MODULES)} figures)")


if __name__ == "__main__":
    main()
