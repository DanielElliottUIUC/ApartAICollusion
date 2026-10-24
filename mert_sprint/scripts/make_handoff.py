#!/usr/bin/env python3
"""Assemble CollusionSprint_AgentHandoff/: the stand-alone folder a collaborator's agent starts from.

    python3 scripts/make_handoff.py     # rerunnable: sync sources -> localise -> clean -> manifest

The folder holds what an agent must read (start-here, runbook, every run's case record, notes, the usage log).
The runnable code stays in this repo; 00_START_HERE.md gives the sparse-clone recipe for it.
"""

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "CollusionSprint_AgentHandoff"
URL = "https://github.com/BARDAK1995/apart-collusion-sprint-2026.git"
BRANCH = "main"
WALLS = """> WALLS DOCTRINE (binding): the spec you received is an approximate pointer to the
> simplest, cleanest design; that goal outranks its literal words. If you hit a wall,
> a case that doesn't fit, a spec clause that breaks, an assumption that fails, STOP.
> Re-derive the design from first principles; if the honest answer diverges from the
> spec, report the divergence as your primary result. NEVER patch around a wall to
> satisfy the letter of the spec: no flags, special cases, conversion shims, second
> channels, parallel paths, or tests rewritten to dodge a rule. A patch-around is a
> failed deliverable regardless of green gates and will be rejected; an honestly
> reported blocker with a design-level diagnosis is a good outcome."""

# source (repo-relative) -> destination (folder-relative); directories copy recursively
COPIES = {
    "experiments/README.md": "CAMPAIGN_RUNBOOK.md",
    "experiments/cases": "context/cases",
    "experiments/heterogeneous/run_matrix.sh": "context/run_matrix_example.sh",
    "notes/sprint_overview.md": "context/sprint_overview.md",
    "notes/resources.md": "context/resources.md",
    "notes/research_questions": "context/research_questions",
    "papers/README.md": "context/papers_index.md",
    "token-usage/USAGE_LOG.md": "context/USAGE_LOG.md",
    "token-usage/usage_snapshot.json": "context/usage_snapshot.json",
    "README.md": "context/repo_README.md",
}


def start_here(head: str) -> str:
    return f"""# Start here: AI collusion sprint, agent handoff

## Mission
Study whether LLM agents collude when they set prices, and whether it depends on who is on the team. Two markets from
Poseidon: a continuous double auction (sellers get a message board, CEO pressure, an overseer) and a repeated Bertrand
price game (no talking). Vary the model, the prompt and the team mix; add cases; keep every run documented.

## Rules for working
{WALLS}

Report measured results as measured. Runs here are single seeds (leads, not findings): repeat before claiming anything.

## Get the code (sparse clone, about 30 MB without the archive)
```bash
git clone --filter=blob:none --no-checkout {URL} sprint && cd sprint
git sparse-checkout init --cone
git sparse-checkout set dashboard experiments scripts src/subscription_proxy src/fable_image_stego token-usage notes talks report
git checkout {BRANCH}
./scripts/setup_other_machine.sh      # clones the Poseidon harness at d585a7b, applies our patch, installs envs
```
Do not check out `archive/` (573 MB of reference copies of the Poseidon starter code; the setup script clones it fresh).
Do not initialise submodules (there are none to initialise).

Report back by committing under `experiments/` on a branch named `results/<your-name>` and opening a pull request;
never push to `{BRANCH}` directly. Run `python3 experiments/sync_runs.py` first so `cases/` is regenerated.

## Environment assumptions
Linux or macOS, git, python3.9+, uv, and at least one signed-in CLI among `claude`, `codex`, `agy`, `grok`
(no API keys needed). `scripts/start_proxy.sh` serves them on `http://127.0.0.1:8787/v1`.
Harness input discipline: copy an existing run's command and change values only; never edit `collusion_hackathon/` source
beyond `experiments/patches/collusion_hackathon_local_changes.patch`.

## Reading order
1. `CAMPAIGN_RUNBOOK.md`: the two games, the conditions, how to run agents and batches.
2. `context/cases/README.md`: index of every run with setup and headline numbers.
3. A few case files in `context/cases/double_auction/` and `context/cases/bertrand/`: each round's moves, the seller
   message board, private plans and thoughts. Start with the `het_*` runs (mixed teams).
4. `context/repo_README.md`: observations so far and the repo map.
5. `context/research_questions/`: literature checks and why these markets were chosen.
6. `context/sprint_overview.md`, `context/resources.md`, `context/papers_index.md`: the sprint rules and sources.
7. `context/USAGE_LOG.md`: tokens and cost to date.

## Execution contract
- Gate order for any new batch: one smoke run (2 to 3 rounds) -> check its case file reads sensibly -> the batch.
- Compare against a baseline run in the same session; cite run names, rounds and file paths for every claim.
- Misses are reported, not tuned away. Failed or incomplete runs stay in `snapshot/` and are marked in `cases/`.

## Known gaps (HOLD list)
- **Scripted ZIP buyers are frozen near $80** (their learning loop is commented out, `market/agents.py` lines 90 to 122):
  with them, a seller price wall means zero trades. HOLD any claim about market efficiency until runs use LLM buyers.
  Fallback: use `--buyer_models <llm>` for the comparison.
- **Single seeds.** HOLD any ranking of models or teams until each setting has at least 3 seeds. Fallback: describe as leads.
- **Model names.** Runs record requested ids; the proxy serves `gpt-5.4-mini` as GPT-6 Luna and Claude Haiku ids as 4.5
  before the evening of 2026-10-23 and 5.5 after. See the runbook.
- **Usage totals** cover machines up to their last ledger sync (see `context/USAGE_LOG.md`).

## Provenance
Built from `{URL}` at commit `{head}`. `MANIFEST.md` lists every file with its SHA-256.
"""


def localise(text: str) -> str:
    text = text.replace("/home/box/", "~/").replace("/workspace/apart-collusion-sprint-2026/", "").replace("/workspace/collusion_hackathon", "./collusion_hackathon")
    return text


def main() -> None:
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    # 1. sync sources
    if OUT.exists():
        shutil.rmtree(OUT)
    for src, dst in COPIES.items():
        s, d = REPO / src, OUT / dst
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(s, d) if s.is_dir() else shutil.copy2(s, d)
    (OUT / "00_START_HERE.md").write_text(start_here(head), encoding="utf-8")
    # 2. localise absolute paths in text files
    for f in OUT.rglob("*"):
        if f.is_file() and f.suffix in {".md", ".sh", ".json", ".txt"} and f.name != "00_START_HERE.md":
            t = f.read_text(encoding="utf-8")
            if localise(t) != t:
                f.write_text(localise(t), encoding="utf-8")
    # 3. delete byproducts
    for junk in list(OUT.rglob("__pycache__")) + list(OUT.rglob(".DS_Store")):
        shutil.rmtree(junk, ignore_errors=True) if junk.is_dir() else junk.unlink()
    # 4. manifest
    rows = []
    for f in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name != "MANIFEST.md"):
        rows.append(f"| `{f.relative_to(OUT)}` | {f.stat().st_size} | `{hashlib.sha256(f.read_bytes()).hexdigest()}` |")
    (OUT / "MANIFEST.md").write_text(
        f"# Manifest\n\nSource: {URL} at commit `{head}`. Assembled by `scripts/make_handoff.py` (rerunnable).\n\n"
        "Deliberate exclusions: `archive/` (573 MB reference copies of the Poseidon starter code), `papers/*.pdf` (20 MB; "
        "listed in `context/papers_index.md`, fetch from the repo), `experiments/snapshot/` (raw run files; the case files "
        "carry the same text), all code (clone it with the recipe in `00_START_HERE.md`).\n\n"
        f"{len(rows)} files.\n\n| File | Bytes | SHA-256 |\n|---|---|---|\n" + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"[handoff] {len(rows)} files, {sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()) / 1e6:.1f} MB -> {OUT}")


if __name__ == "__main__":
    main()
