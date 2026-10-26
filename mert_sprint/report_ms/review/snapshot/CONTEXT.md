> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Context for the reviewer: the task, the data, the paper

## The task
Apart Research's AI Collusion Research Sprint (October 23 to 25, 2026), a three-day hackathon. It asks when AI agents
start colluding, what counts as real evidence of collusion in their logs, and how to break it up. This entry is in
Track 3, questions Q3.2 ("Can we disrupt collusion through introducing trusted agents?") and Q3.4 ("What does a
coalition do when it learns it is being watched?").

Judges score every project from 1 to 5 on (1) impact and novelty, (2) execution: sound method, interpretable results,
stated limitations, (3) clarity. Made-up results or references disqualify a project. Deliverable: one PDF, body at most
8 pages (references and appendices excluded), abstract 150 to 250 words, authors and affiliations, an appendix on
Limitations and Dual Use. Due Mon 2026-10-26 06:59 CT. The owners currently allow a longer draft (about 11 pages) and
will cut to 8 at the end by moving material to appendices.

## What exists (the data behind the paper)
- Daniel Elliott's undercover-offer study: 50 Gemini 3.8 Flash markets (10 arms x 5 seeds), 15 GPT-4.1 markets, 3 Claude
  Haiku 5.5 markets, 18 identity-label runs. Per-run CSVs (market, hourly, seller-level outcomes, permutation tests).
- Mert Senkardesler's runs: 36 frontier-seller runs (GPT-5.6 Sol, GPT-6 Luna, Grok 4.7; messaging on and off; two buyer
  models; 3 seeds), 9 Claude Haiku 5.5 seller runs, 6 Sol runs under GPT-4.1-mini buyers, 21 runs with the order book
  opened at $90 instead of the default $97.50 (Sol, Luna, Gemini), 3 Gemini runs at the default opening as a serving-route
  control, and a pre-specified test (12 runs) whose protocol was committed before the runs. All runs exited cleanly with
  no failed model calls. Summary table: ms_runs.csv. Pre-specified result: prereg_result.md.
- The original Agrawal et al. (2025) harness seeds the same high opening: provenance.md.
- An external review (GPT-6 Pro) and its independent verification: pro_checks.md (every reference opened, every number
  recomputed).
- Verified agent quotes with file and line: quotes_candidates.md.
- Figures: figures/ (fig1 to fig4 data figures, diag1 to diag3 diagrams); figures_README.md gives every plotted number.

## The paper
REPORT.md (Markdown source) and full.pdf (its current render, about 11 to 16 pages). Two sections are still being added
in parallel and are not in this snapshot: the setup diagrams in section 3 and a section on each seller model's
behavioural profile.
