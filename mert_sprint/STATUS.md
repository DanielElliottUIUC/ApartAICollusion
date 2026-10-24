# Status

Last updated: Sat Oct 24, 2026, 1:00 PM CT.

## Deadline

Submissions close Sun Oct 25, 11:59 PM AoE. That is Mon Oct 26, 6:59 AM CT.

## Submission rules

1. Submit through the official submission form on the sprint page.
2. The submit button appears Friday. This comes from the setup brief. The sprint page text does not state it.
3. To fix or replace a submission, submit again before the deadline with the exact same title and details. The new files replace the old ones.
4. Report: a PDF on the official Apart template. Most strong projects are 4 to 8 pages. The cap is 8 pages, not counting references and appendices.
5. Abstract: 150 to 250 words. Include author names and affiliations.
6. A "Limitations and Dual-Use / Ethical Considerations" appendix is required.
7. Max two projects per person. Each needs its own submission with a unique title.
8. Mark any preexisting code in the README and the report.
9. Optional: public GitHub repo, and a 3 to 5 minute video demo.

## Open tasks

- [ ] Pick a track and research question (see notes/resources.md).
- [ ] Join the sprint Discord: https://discord.gg/XswWBvugYs
- [ ] Make a copy of the report template (see report/TEMPLATE.md).
- [ ] Clone the starter code for the chosen question into src/ and run the positive control.
- [ ] Decide whether to stay solo or join a team.
- [ ] Attend the talks (talks/SCHEDULE.md).
- [ ] Write the report, including the Limitations and Dual-Use / Ethical Considerations appendix.
- [ ] Run the pre-submission checklist in report/TEMPLATE.md.
- [ ] Submit before Mon Oct 26, 6:59 AM CT.
- [x] Set up Fable 5.1 image steganography replication harness in src/fable_image_stego/ and pass end to end smoke tests (author example 01 decoded 100%, fresh msg_01 'meet at dawn' encoded and decoded 100%).
- [ ] Run full pilot batch for cnm13ryan replication (`cd /workspace/apart-collusion-sprint-2026/src/fable_image_stego && python3.13 run_pilot.py --mode pilot`).

## Update 2026-10-23: Poseidon starter code archived

All 10 Poseidon starter codebases plus `util/` and `setup.sh` are archived in `archive/poseidon_collusion_hackathon_code/` (weights, venvs, caches, and files of 50 MB or more excluded). The runnable clone with all 11 environments installed is at `/workspace/collusion_hackathon`.

## Run plan (Sat Oct 24)

Every remaining run, its machine and status: [notes/RUN_PLAN.md](notes/RUN_PLAN.md). Behavior write up: [docs/AGENT_BEHAVIOR.md](docs/AGENT_BEHAVIOR.md).

- [x] Inventory what has run vs what is planned.
- [x] Proxy strict routing and OpenRouter passthrough (S-2).
- [x] `scripts/run_all.sh`: one entry point, N shards (`--shard k/N`, pinned in `notes/shard_assignment.json`), resumable, per shard outputs, merge step.
- [x] `experiments/make_behavior_report.py` writes `docs/AGENT_BEHAVIOR.md` from every run in `experiments/snapshot/` and `experiments/runs/` (now 40 finished auction and 49 Bertrand sprint runs).
- [x] Keep `unified.log` files in git.
- [ ] Shard 1 (box): 33 of 57 done; 12 ready (Grok sweeps, Fable parts) and 12 that need `OPENROUTER_API_KEY`. All 6 Fable parts failed once (encoder reply without `<svg>`).
- [ ] Shard 2: 11 of 39 done, 1 failed (Haiku 4.5 refused the PC prompt twice). Shard 3: 11 of 39 done, 1 failed (same refusal). The 22 Gemini runs per shard wait for the agy quota (resets about Oct 30).
- [ ] Rerun the 9 het55 CCO/OOC/OOO auctions on a machine whose codex CLI answers GPT-6 Luna: on the Windows machine every Luna seat returned empty replies, so they were moved out of the repo (`quarantine_luna_empty_2026-10-24/`, not pushed).
- [ ] `scripts/run_all.sh merge` after both finish, then read `docs/AGENT_BEHAVIOR.md` again.
- [ ] Steps C and D to G: 81 runs waiting on Daniel's code.

## Collaboration with Daniel (ApartAICollusion)

Daniel's plan and runs, merged as tasks: [notes/collab_daniel/PLAN_AND_TASKS.md](notes/collab_daniel/PLAN_AND_TASKS.md).
Read from his `main` at `788092c` on Fri Oct 23, 2026, evening CT. Our workspace copy is his PR #9 (merged).

Daniel's steps (his status in brackets):

- [ ] D-A positive control, Gemini Flash first (built, not yet passed)
- [ ] D-B heterogeneous sweep: GGGG, GGCC, GGDD, GCCD, CCCC, 3 seeds each (runnable after A)
- [ ] D-C shared identity labels, 6 labels × 2 mixes × 3 seeds (needs label + check code)
- [ ] D-pilot Base pilot run to record the seat 5 replay path
- [ ] D-D undercover offer to every seller (needs undercover seat + report tool)
- [ ] D-human arms D-hs, D-hb, D-hsb (needs persona text + buyer→seller messages)
- [ ] D-E warning (needs warning text)
- [ ] D-F warning + precedent (needs precedent text)
- [ ] D-G G-warn and G-prec, no undercover agent (reuses E/F text)
- [ ] D-Fsham (should) and D-Basehb (if time)
- [ ] D-ID identity probe fixes and run
- [ ] D-judge freeze judge prompts; D-outcomes per seller episode table

Our suggestions (not yet agreed with Daniel):

- [ ] S-1 Agree which B composition D to G uses.
- [x] S-2 Proxy: unknown ids now fail with HTTP 400; DeepSeek, Kimi, GPT-4.x go to OpenRouter when `OPENROUTER_API_KEY` is set (Oct 24).
- [ ] S-3 Offer to run his step A Gemini gate through the proxy.
- [ ] S-4 Port `experiments/heterogeneous/run_matrix.sh` to his v2 harness and B mixes.
- [ ] S-5 Haiku 4.5 Bertrand refusal: written up in `docs/AGENT_BEHAVIOR.md` section 6 (Oct 24). Rerun with log kept, and Haiku 5.5 PC: `refusal` and `sweep` phases of `scripts/run_all.sh`.
- [ ] S-6 Pick one viewer and one case format for the shared repo.
- [ ] S-7 Offer to build one D to G piece (outcome table, judge prompts, or buyer→seller block).
