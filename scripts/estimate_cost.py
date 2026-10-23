"""Rough OpenRouter cost estimate for a double-auction sweep.

Uses prices and per-call token assumptions from configs/models.toml.

    python scripts/estimate_cost.py --sellers gpt41 gpt41 gpt41 gpt41 --buyers 4 --runs 6
    python scripts/estimate_cost.py --sellers gpt41 gpt41 gpt41 --runs 3 --rounds 15 --no-judge

Buyers default to 3 Haiku LLM buyers (--buyer haiku --buyers 3). Use --buyers 0 for no buyer calls.
Private-message threads make seller prompts grow over a run; the token assumptions do not model that.
"""

import argparse
import tomllib
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "configs" / "models.toml"


def main() -> None:
    cfg = tomllib.loads(CONFIG.read_text())
    models, usage = cfg["models"], cfg["usage"]

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sellers", nargs="+", required=True, help=f"one model key per seller: {', '.join(models)}")
    p.add_argument("--rounds", type=int, default=15)
    p.add_argument("--runs", type=int, default=1, help="number of runs (seeds x conditions)")
    p.add_argument("--no-judge", action="store_true", help="skip the LLM-judge pass (--llm_eval)")
    p.add_argument("--buyer", default="haiku", help="model key for LLM buyers")
    p.add_argument("--buyers", type=int, default=3, help="number of LLM buyers (0 = none)")
    args = p.parse_args()

    def call_cost(key: str, tin: int, tout: int) -> float:
        m = models[key]
        return (tin * m["price_in"] + tout * m["price_out"]) / 1e6

    per_run = 0.0
    for key in args.sellers:
        per_run += args.rounds * call_cost(key, usage["seller_in_tokens"], usage["seller_out_tokens"])
    per_run += args.buyers * args.rounds * call_cost(
        args.buyer, usage["seller_in_tokens"], usage["seller_out_tokens"]
    )
    if not args.no_judge:
        per_run += len(args.sellers) * args.rounds * call_cost(
            "judge", usage["judge_in_tokens"], usage["judge_out_tokens"]
        )

    calls = (len(args.sellers) * (1 if args.no_judge else 2) + args.buyers) * args.rounds
    print(f"sellers: {' '.join(args.sellers)} | buyers: {args.buyers}x{args.buyer} | rounds: {args.rounds} "
          f"| judge: {not args.no_judge}")
    print(f"~{calls} calls/run, ~${per_run:.3f}/run, ~${per_run * args.runs:.2f} for {args.runs} run(s)")
    print("(token counts are assumptions; replace them in configs/models.toml after measuring real runs)")


if __name__ == "__main__":
    main()
