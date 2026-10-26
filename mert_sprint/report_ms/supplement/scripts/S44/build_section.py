"""Builds every S4.4 supplement figure and writes report_ms/supplement/sections/S44.md.

Run from anywhere:
  python report_ms/supplement/scripts/S44/build_data.py      (derived tables from experiments/runs/)
  python report_ms/supplement/scripts/S44/build_section.py   (figures and the Markdown fragment)
Every number in the fragment is computed by the figure scripts at build time.
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import s44lib as L  # noqa: E402

MODULES = ["make_S44_01_verdicts", "make_S44_02_paths", "make_S44_03_prereg_pairs", "make_S44_04_signflip",
           "make_S44_05_hour1_max", "make_S44_06_gemini_lockstep", "make_S44_07_cartel_words",
           "make_S44_08_quote_wall"]
INTRO = (
    "## S4.4 Opening price and what the agents said\n\n"
    "Alternate figures for report section 4.4 (prices stay where the market opens) and Table 2 (what the agents "
    "said). All come from our runs. Figures S44.1 to S44.5 follow the price, from the verdict of each market to "
    "the pre-specified test and the hour of the highest ask; Figures S44.6 to S44.8 set the sellers' talk next to "
    "their asks.\n"
)


def main():
    blocks = [INTRO]
    for name in MODULES:
        out = importlib.import_module(name).build()
        for key in ("caption", "shows", "title"):
            for bad in ("\u2014", "\u2013"):
                if bad in out[key]:
                    raise ValueError(f"{name}: dash in {key}")
        blocks.append(
            f"### Figure {out['id']}. {out['title']}\n\n"
            f"![](figures/S44/{out['file']})\n\n"
            f"**Caption.** {out['caption']}\n\n"
            f"**What it shows.** {out['shows']}\n\n"
            f"Source: {out['source']}\n")
    path = L.SUP / "sections" / "S44.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(blocks), encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
