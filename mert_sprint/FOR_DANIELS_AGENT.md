# For Daniel's coding agent: what is in mert_sprint/ and how to use it

Written Sun 2026-10-25, about 22:00 CT, for the agent that is writing Daniel's version of the report.
Everything in `mert_sprint/` is from Mert Senkardesler (M.S.). This is an interim state. Read the warnings below
before you use any number.

## Read in this order

1. `notes/status_for_daniel_oct25_2145.md`: the plain language status note. Start here.
2. `notes/strategy_oct25/message_to_daniel.md`: corrections to Daniel's report (against main b7cbccd) and
   paste-ready blocks A to F for his `report/REPORT.md`. Block G lists lines that go stale if the opening-price result goes in.
3. `report_ms/report/REPORT.md`: M.S.'s parallel version of the report, "Talk Is Not Price: Undercover Offers,
   Warnings and Opening Prices in an LLM Double Auction". It reuses Daniel's study and credits it.

## Map of mert_sprint/

| Path | What it is |
|---|---|
| `experiments/runs/` | M.S.'s run folders (unified.log, per-agent files). Tonight's: `shard2/frontier_lowanchor/`, `shard2/frontier_b41/`, `shard2/A_lowanchor/`, `shard2/A_agycontrol/`, `shard2/prereg_anchor/` |
| `notes/status_for_daniel_oct25_2145.md` | Status note for Daniel |
| `notes/handoff_report_ms_oct25.md` | Handoff note that describes this sync |
| `notes/strategy_oct25/` | Strategy notes; `message_to_daniel.md` holds the corrections and blocks A to F |
| `report_ms/report/REPORT.md` | M.S.'s report text; figures in `report_ms/report/figures/` |
| `report_ms/drafts/` | Interim PDF renders |
| `report_ms/supplement/` | Supplementary figure book, partial |
| `report_ms/provenance.md` | Where the opening order book comes from (harness and upstream code) |
| `report_ms/prereg_sol_anchor.md`, `report_ms/prereg_result.md` | Pre-specified test: protocol (committed before the runs, c5a14aa) and result |
| `report_ms/pro_checks.md` | Item by item check of the external review (GPT-6 Pro) |
| `report_ms/quotes_candidates.md` | Verification of the quoted agent messages |
| `report_ms/data/`, `report_ms/scripts/` | Copies of Daniel's report CSVs, `ms_runs.csv`, one script per figure |
| `dashboard_page/` | A visual explainer of Daniel's experiment (source and standalone HTML) |

## Key new results (copied from the status note; no new numbers)

- **Prices stay where the market opens.** The harness seeds the opening order book with seller asks near $97.50,
  as does the original Agrawal et al. code (`report_ms/provenance.md`). Opened at the $90 benchmark instead, with
  everything else unchanged, no market passes: Daniel's step A Gemini market 0 of 3 with messaging on and 0 of 3 with
  it off, GPT-5.6 Sol 0 of 6, GPT-6 Luna 0 of 3. From $97.50 the same Gemini market passes 2 of 3. Runs: Gemini
  from $90 in `experiments/runs/shard2/A_lowanchor/`, Gemini from $97.50 in `shard2/A_agycontrol/`, Sol and Luna
  from $90 in `shard2/frontier_lowanchor/`.
- **Pre-specified test.** Protocol in `report_ms/prereg_sol_anchor.md` (commit c5a14aa): 6 fresh seed blocks, Sol,
  $97.50 vs $90, endpoint mean ask hours 11 to 15. All 6 pairs higher from the $97.50 opening, mean +$6.79, exact
  paired sign-flip p = 2/64 = 0.031; 5 of 6 pass vs 0 of 6. See `report_ms/prereg_result.md`, runs in
  `experiments/runs/shard2/prereg_anchor/`.
- **Sol with Daniel's GPT-4.1-mini buyers passes 4 of 6**, so its frontier passes are not a soft-buyer effect.
  Runs: `experiments/runs/shard2/frontier_b41/`.
- **Four corrections still needed in Daniel's report** (paste-ready text in `notes/strategy_oct25/message_to_daniel.md`):
  1. §4.7 line 236: Grok 4.7 has all 12 runs, 0 of 12 pass (not "0 of 4 ... two runs missing").
  2. Line 236 and A.2 item 11: the frontier runs requested and received gpt-5.6-sol, gpt-6-luna and grok-4.7 (the
     alias sentence is reversed).
  3. Line 236: the 15 rate-limited shard-3 Gemini runs were rerun; the reruns are valid.
  4. D.4 Haiku row: messaging on 3 of 3, off 1 of 3, prohibition notice 1 of 3.

## What is interim and NOT fact-checked

- `report_ms/drafts/talk_is_not_price_DRAFT2_2026-10-25_2143.pdf` (interim draft 2) and the current
  `report_ms/report/REPORT.md` are not fact-checked yet.
- `report_ms/supplement/` is partial: some figures and sections are still missing.

## Coming tonight, as further commits to this same pull request

- The fact-checked final of `report_ms/`.
- The final PDF, replacing the draft PDFs.
- The finished supplement.

## Coordination rules

- Do not edit anything under `mert_sprint/`. Write Daniel's version in his own files.
- Treat M.S.'s numbers as unverified until the fact-checked final lands in this pull request.
- Use blocks A to F in `notes/strategy_oct25/message_to_daniel.md` as paste-ready text for Daniel's `report/REPORT.md`.
- Cite run folders by their path under `mert_sprint/experiments/runs/`.
- Credit M.S. for this work.
- If you disagree with a number or a claim, flag it back to Daniel. Do not change it silently.
- How the two versions get combined into the submission is for Mert and Daniel to decide together tonight.
