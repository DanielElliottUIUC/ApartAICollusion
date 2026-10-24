#!/usr/bin/env python3
"""Copy experiment run outputs from the harness clone into experiments/snapshot/ so this repo alone feeds the dashboard.

    python3 experiments/sync_runs.py            # source: $COLLUSION_HACKATHON, ./collusion_hackathon, or /workspace/collusion_hackathon

Copies, keeping the harness layout:
  llm-agent-collusion/results/<run>/            every sprint run, whole folder (chat, plans, metrics)
  llm-agent-collusion/data/<run>/*.json         the authors' 2025 runs, metrics and metadata only
  llm-cartel/results/jsonl/                     every Bertrand run and its config
Also writes the harness's uncommitted changes (the subscription-proxy wiring) to experiments/patches/,
then regenerates the readable case files in experiments/cases/.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Same lookup as dashboard/serve.py: $COLLUSION_HACKATHON, else the clone that scripts/setup_other_machine.sh
# makes inside this repo, else the sprint box's clone.
SRC = Path(os.environ.get("COLLUSION_HACKATHON") or next(
    (p for p in (REPO / "collusion_hackathon", Path("/workspace/collusion_hackathon")) if p.is_dir()),
    REPO / "collusion_hackathon"))
DST = Path(__file__).resolve().parent / "snapshot"
PATCH = Path(__file__).resolve().parent / "patches" / "collusion_hackathon_local_changes.patch"


def mirror(src: Path, dst: Path, only=None) -> int:
    if dst.exists():
        shutil.rmtree(dst)
    n = 0
    for f in src.rglob("*"):
        if f.is_file() and (only is None or f.name in only):
            out = dst / f.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, out)
            n += 1
    return n


def main() -> None:
    cda, cartel = SRC / "llm-agent-collusion", SRC / "llm-cartel"
    counts = {
        "auction sprint runs": mirror(cda / "results", DST / "llm-agent-collusion" / "results"),
        "auction author runs": mirror(cda / "data", DST / "llm-agent-collusion" / "data",
                                      only={"collusion_metrics.json", "experiment_metadata.json"}),
        "bertrand runs": mirror(cartel / "results" / "jsonl", DST / "llm-cartel" / "results" / "jsonl"),
    }
    PATCH.parent.mkdir(parents=True, exist_ok=True)
    PATCH.write_text(subprocess.run(["git", "-C", str(SRC), "diff"], capture_output=True, text=True).stdout)
    for k, v in counts.items():
        print(f"[sync] {k}: {v} files")
    print(f"[sync] harness patch: {PATCH} ({PATCH.stat().st_size} bytes)")
    # Rebuild the readable case files from the fresh snapshot.
    env = {k: v for k, v in os.environ.items() if k != "COLLUSION_HACKATHON"}
    subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "make_cases.py")], env=env, check=True)


if __name__ == "__main__":
    main()
