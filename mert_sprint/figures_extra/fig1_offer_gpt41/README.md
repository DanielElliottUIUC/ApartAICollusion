# fig1_offer with two GPT-4.1 rows (variant)

`fig1_offer_gpt41.png` is `report_ms` Figure fig1_offer with two rows added to panel b:

- **GPT-4.1, precedent** (arm F, warning and precedent): reported seat 5 12 of 12, echo label 0 of 12, rejection label 8 of 12. Source: Daniel's `report/data/dg_gpt41/outcomes_by_arm.csv`, row F.
- **GPT-4.1, offer $99** (arm D99): reported seat 5 1 of 12. The judge was not run on D99, so the two judge columns show the hand read instead, in italics: 0 of 12 sellers raised their ask by $1 or more in hours 4 to 6, and 10 of 10 messages to seat 5 declined. Source: Daniel's `report/data/dg_gpt41_99/outcomes.csv` (PR #41, identical on report-v2), copied here as `data/dg_gpt41_99_outcomes.csv`.

All other numbers are as in fig1_offer. Panel a uses the any report count (D-hb 20 of 20).

Suggested caption addition: "GPT-4.1 under the precedent reported 12 of 12; at $99, 0 of 12 raised asks toward the offer and all 10 replies declined (hand read; no judge run)."

Rebuild: `python make_fig1_offer_gpt41.py`. It imports the fig1_offer script and its helpers from `report_ms/scripts/` next to this folder (in Daniel's repo, `mert_sprint/report_ms/`, on PR #39), plus matplotlib and pandas. Made by M.S.
