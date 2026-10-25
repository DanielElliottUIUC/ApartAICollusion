#!/usr/bin/env python3
"""Score finished double-auction runs with Grok as the LLM judge, after the run.

Daniel's harness hardcodes the in-run judge as gpt-4.1-mini (evaluation/evaluate.py, DEFAULT_EVAL_MODEL). Runs started with
JUDGE=off skip it. This script reuses his judge prompt and parser unchanged and only swaps the model, in memory, so his
files stay untouched. It never overwrites an existing judge result: output goes to its own files in each run folder.

  llm_eval_<model>.json      every round's judge reply, per seller (same layout as his llm_eval_full.json)
  judge_<model>_summary.json judge model, temperature, mean coordination score per seller, rounds scored and failed

Run it with Daniel's environment (the sprint repo's ../ApartAICollusion checkout):
  cd ../ApartAICollusion/third_party/llm-agent-collusion
  uv run --no-sync python ../../../apart-collusion-sprint-2026/scripts/judge_with_grok.py <runs_root> [--model grok-4.7]
The subscription proxy must be up on :8787 (scripts/start_proxy.sh).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))  # Daniel's project root, so `src.` imports resolve
from src.continuous_double_auction.evaluation import evaluate  # noqa: E402


def score_run(run_dir: Path, model: str, workers: int) -> str:
    tag = model.replace("/", "_")
    out_full, out_sum = run_dir / f"llm_eval_{tag}.json", run_dir / f"judge_{tag}_summary.json"
    if out_sum.exists():
        return "skip (already scored)"
    metadata = json.loads((run_dir / "experiment_metadata.json").read_text())
    evaluate.DEFAULT_EVAL_MODEL = model
    evaluate.MAX_WORKERS = workers
    results = evaluate.run_llm_eval(metadata, run_dir / "unified.log")
    if not results:
        return "no results"
    out_full.write_text(json.dumps([{"seller_id": s, "rounds": r} for s, r in results.items()], indent=2, ensure_ascii=False))
    summary = {"judge_model": model, "temperature": evaluate.DEFAULT_EVAL_TEMPERATURE, "sellers": {}}
    for seller, rounds in results.items():
        scores = [r["data"]["score"] for r in rounds
                  if r.get("status") == "success" and isinstance(r.get("data"), dict) and "score" in r["data"]]
        summary["sellers"][seller] = {"rounds_scored": len(scores), "rounds_failed": len(rounds) - len(scores),
                                      "mean_coordination_score": sum(scores) / len(scores) if scores else None}
    out_sum.write_text(json.dumps(summary, indent=2))
    return "scored " + ", ".join(f"{s}={v['mean_coordination_score']}" for s, v in summary["sellers"].items())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, help="folder holding run folders (each has unified.log and experiment_metadata.json)")
    ap.add_argument("--model", default="grok-4.7")
    ap.add_argument("--workers", type=int, default=4, help="parallel judge calls per run")
    ap.add_argument("--only", default="", help="substring filter on the run folder name")
    a = ap.parse_args()
    runs = sorted({p.parent for p in a.root.rglob("unified.log") if (p.parent / "experiment_metadata.json").exists()})
    runs = [r for r in runs if a.only in str(r)]
    print(f"{len(runs)} run folders under {a.root}", flush=True)
    for r in runs:
        print(f"{r.name}: {score_run(r, a.model, a.workers)}", flush=True)


if __name__ == "__main__":
    main()
