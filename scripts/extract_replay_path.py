"""Extract one seller's ask path from a finished harness run, as the replay file for the D–G scripted seat.

The Base pilot is a 5-seller + 5-buyer market in which seat 5 is an ordinary Gemini LLM seller. That seat's
ask path, hour by hour, becomes the replay file reused by the scripted seat (`--scripted_seat_path`) in every
D–G arm and seed, so the scripted seat looks like a real seller.

    python scripts/extract_replay_path.py results/<pilot_run_dir> --seller "Seller Max" --out configs/replay/base_pilot.json
    python scripts/extract_replay_path.py results/<pilot_run_dir> --out configs/replay/base_pilot.json   # last seller

Reads auction_results.md (or unified.log if that is missing). Writes
{"asks": [one float per hour], "source_run": ..., "source_seller": ..., "filled_rounds": [...]}.
An hour in which the seller placed no ask (failed turn or withdrawn ask) repeats the previous hour's ask and is
listed in "filled_rounds". Stdlib only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

LOG_RE = re.compile(r"Auction round \d+ completed with result: (\{.*\})\s*$")


def load_rounds(run_dir: Path) -> list[dict]:
    md = run_dir / "auction_results.md"
    if md.is_file():
        blocks = re.findall(r"````json\n(.*?)\n````", md.read_text(encoding="utf-8"), flags=re.S)
        rounds = [json.loads(b) for b in blocks]
    else:
        log = run_dir / "unified.log"
        if not log.is_file():
            sys.exit(f"no auction_results.md or unified.log in {run_dir}")
        rounds = [json.loads(m.group(1)) for line in log.read_text(encoding="utf-8").splitlines()
                  if (m := LOG_RE.search(line))]
    by_round = {r["round_number"]: r for r in rounds}  # last record per round wins
    return [by_round[k] for k in sorted(by_round)]


def extract(run_dir: Path, seller: str | None) -> dict:
    meta_path = run_dir / "experiment_metadata.json"
    seller_ids = json.loads(meta_path.read_text(encoding="utf-8")).get("seller_ids", []) if meta_path.is_file() else []
    if seller is None:
        if not seller_ids:
            sys.exit("no experiment_metadata.json to pick the last seller from; pass --seller")
        seller = seller_ids[-1]
    elif seller_ids and seller not in seller_ids:
        sys.exit(f"{seller!r} is not a seller in this run: {seller_ids}")

    rounds = load_rounds(run_dir)
    if not rounds:
        sys.exit(f"no round records found in {run_dir}")
    asks, filled, last = [], [], None
    for rnd in rounds:
        ask = rnd.get("seller_asks", {}).get(seller)
        if ask is None:
            if last is None:
                sys.exit(f"{seller} has no ask in hour {rnd['round_number']} and no earlier ask to repeat")
            ask = last
            filled.append(rnd["round_number"])
        asks.append(float(ask))
        last = ask
    return {"asks": asks, "source_run": run_dir.name, "source_seller": seller, "filled_rounds": filled}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run_dir", type=Path)
    p.add_argument("--seller", default=None, help='e.g. "Seller Max" (default: the last seller seat)')
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    path = extract(args.run_dir, args.seller)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(path, indent=2) + "\n", encoding="utf-8")
    print(f"{path['source_seller']}: {len(path['asks'])} hours, filled {path['filled_rounds'] or 'none'} -> {args.out}")


if __name__ == "__main__":
    main()
