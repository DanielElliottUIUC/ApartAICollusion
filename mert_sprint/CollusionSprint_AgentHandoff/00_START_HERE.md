# Start here: AI collusion sprint, agent handoff

## Mission
Study whether LLM agents collude when they set prices, and whether it depends on who is on the team. Two markets from
Poseidon: a continuous double auction (sellers get a message board, CEO pressure, an overseer) and a repeated Bertrand
price game (no talking). Vary the model, the prompt and the team mix; add cases; keep every run documented.

## Rules for working
> WALLS DOCTRINE (binding): the spec you received is an approximate pointer to the
> simplest, cleanest design; that goal outranks its literal words. If you hit a wall,
> a case that doesn't fit, a spec clause that breaks, an assumption that fails, STOP.
> Re-derive the design from first principles; if the honest answer diverges from the
> spec, report the divergence as your primary result. NEVER patch around a wall to
> satisfy the letter of the spec: no flags, special cases, conversion shims, second
> channels, parallel paths, or tests rewritten to dodge a rule. A patch-around is a
> failed deliverable regardless of green gates and will be rejected; an honestly
> reported blocker with a design-level diagnosis is a good outcome.

Report measured results as measured. Runs here are single seeds (leads, not findings): repeat before claiming anything.

## Get the code (sparse clone, about 30 MB without the archive)
```bash
git clone --filter=blob:none --no-checkout https://github.com/BARDAK1995/apart-collusion-sprint-2026.git sprint && cd sprint
git sparse-checkout init --cone
git sparse-checkout set dashboard experiments scripts src/subscription_proxy src/fable_image_stego token-usage notes talks report
git checkout main
./scripts/setup_other_machine.sh      # clones the Poseidon harness at d585a7b, applies our patch, installs envs
```
Do not check out `archive/` (573 MB of reference copies of the Poseidon starter code; the setup script clones it fresh).
Do not initialise submodules (there are none to initialise).

Report back by committing under `experiments/` on a branch named `results/<your-name>` and opening a pull request;
never push to `main` directly. Run `python3 experiments/sync_runs.py` first so `cases/` is regenerated.

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
Built from `https://github.com/BARDAK1995/apart-collusion-sprint-2026.git` at commit `1e16dc7`. `MANIFEST.md` lists every file with its SHA-256.
