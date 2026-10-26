> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# ARCHITECTURE card: M.S.'s version of the final report (v3)

Written 2026-10-26, about 00:35 CT, by the architect lane. Binds the prose-writer, who writes every sentence to it and may not reorder, add or drop sections. Sources: STATUS = notes/STATUS_oct25_late_for_agents.md; MSI = notes/collab_daniel/MS_input_for_final_report_oct25_late.md; DIG = notes/daniel_digest_oct25_late.md; OLD = report_ms/report/REPORT.md (frozen, 3a2fab3); V2 = Daniel's REPORT_v2.md (content source only); FIG = report_ms/figures_README.md; HS = report_ms/review/HOUSE_STYLE.md (every sentence follows it).

## 0. Title (choice for Mert)

- Proposed, ours, under the agreed framing: "Reports, Silence and the Opening Price: An Undercover Offer and a Warning in an LLM Double Auction".
- Alternative, Daniel's v2 working title: "Report and Pretend: How LLM Sellers Answer an Undercover Collusion Offer, and What Warnings Change".
- Dropped: "Talk Is Not Price" (STATUS, framing bullet 1). Daniel sends the final string; it must match the form.

Authors: Daniel Elliott and Mert Senkardesler, both University of Illinois Urbana-Champaign, equal contribution, "With Apart Research", footnote on the sprint. No email, hostname, machine or account name anywhere.

## 1. Reader

Sprint judges scoring impact and novelty, execution (sound method, interpretable results, stated limitations) and clarity. They know the Agrawal harness from many other entries. They attack first: any novelty claim about the opening price; any price-effect claim from a 5-seed arm; any count that cannot be traced to a file. Daniel is the second reader. He takes sections whole, so each section must stand alone.

## 2. Claims hierarchy

Thesis: in one LLM double auction, what sellers wrote and whether their prices met the joint high-price and trade criterion came apart, and the seller model and the opening price, not messaging, set the criterion's verdict.

F1 (spine, D.E., strongest at 5 seeds). The offer elicited reports from 19 of 20 Gemini sellers (0 of 20 in Base, p = 0.008), all first in hour 4; 7 reported and agreed (9 replied, 8 agreed), rebuilt from the logs, 6 of 7 with a stated aim to keep seat 5 anchored; the sellers' own 104 private messages per market went unreported. Three families answered one offer: GPT-4.1 reported 0 of 12 and 11 of 12 wrote back, 10 in support, support that cost little ($96 at or below the hour-3 asks of 9 of 12) and vanished at $99 (0 of 12 raised asks by $1 or more, 10 of 10 replies declined, 1 of 12 reported, credibility confounded); Haiku refused (11 of 12 by D.E.'s reading, 12 of 12 by the judge) and 3 of 12 reported. Evidence: report_ms/data/daniel/*; V2 §4.1, §4.2, Tables D1, D2, D7; DIG B.2, B.4; MSI §3 items 4 and 5; the log-built 7 of 20 from `daniel/pr43_figures_oct25/report/data/dg/fig_report_and_feign_cells.csv` (DIG B.4).

F2 (D.E., directional). With the warning in the prompt from hour 1, private messaging between Gemini sellers never started in any of the 25 warning-arm markets (103.6 per market in Base), a between-arm difference present from hour 1; the 26 private messages that remained went to seat 5, all in hour 4; public messages continued in E, G-warn and F-sham (45.8 to 55.6 vs 58.4) and stopped in F, G-prec and one F-sham market; the precedent's content, not its length, made sellers suspect a test (16 vs 1 of 20). Prices did not separate (arm means 0.37 to 0.48 vs Base 0.41, seed range 0.12 to 0.61), and the null is uninformative. In the 4+4 market where messaging raises prices, the warning kept 2 of 3 passes (0.70, 0.55, 0.35; 0, 63, 0 private messages) and about 80% of the premium against about half under the prohibition notice, 3 vs 3 seeds. GPT-4.1 kept messaging under the warning alone (64.0 in E, 55.7 in G-warn between sellers per market) and not under warning plus precedent. Evidence: FIG Figure 2 tables; MSI §2; STATUS "New verified results" PR #41; V2 Table D3; DIG B.2.

F3 (M.S., with D.E.'s PR #40, directional). Seller models split talk from the criterion: Sol passed 8 of 12 (3 of 6 with messaging, 5 of 6 without), Luna 0 of 12, Grok 0 of 12 with 104 to 112 private messages per messaging run and private floor agreements below $90 (Fisher p = 0.0013 for Sol against each); Haiku 0 of 9; Sol under GPT-4.1-mini buyers 4 of 6. D.E.'s judge tracks talk (Spearman 0.78 with private messages) and predicts the criterion at AUC 0.60 (p = 0.18; 0.50 within Gemini); 10 markets pass with a mean score under 2. M.S.'s Grok judge scored Sol's 5 silent passes 1.00 to 1.28. Evidence: report_ms/data/ms_runs.csv; OLD §4.3; DIG B.1; quotes_candidates.md for a Grok private floor agreement with file and line.

F4 (M.S. replication plus pre-specified test; D.E. and M.S. pinned market). Prices stay where the market opens: hour 1 held the highest mean ask in 44 of 45 of M.S.'s default-opening markets and D.E. counts 8 raises above $1 in 2,519 seller-hour moves; 0 of 21 runs from $90 passed and no last-third index exceeded 0.01; Gemini at $90 coordinated openly ("completely rock solid") at $88 to $90 while the same market from $97.50 passed 2 of 3. The pre-specified test found Sol's late asks higher from $97.50 in 6 of 6 blocks (+$6.79, range +$5.28 to +$7.38, p = 2/64 = 0.031; 5 of 6 vs 0 of 6 passes). This replicates Douglas (a $4.66 lower price for a $5 lower opening) and Patil and Hoze (GPT-4.1 holds its opening ask, r = 0.995). In no tested market did messaging raise prices above the opening; it sustained a high opening clearly only for Gemini in the ordinary 4+4 market (hour-15 $96.12 vs $90.55). In the pinned market ($90 the unique competitive price, $97.50 opening), Gemini, GPT-4.1 and Sol held $3 to $7 above $90 with and without messaging (Gemini 2 of 3 and 1 of 3, hour-15 $94.87 vs $94.08; GPT-4.1 2 of 3 and 3 of 3, $95.59 vs $95.64; Sol 3 of 3 and 1 of 3, $96.28 vs $93.64, no private message in any run); Luna 0 of 3 and 1 of 3 ($87.08 vs $92.77); the pin only partly bound (the value-$90 buyer bought above its value). Evidence: OLD §4.4, Tables B2, B3; prereg_result.md; MSI §1 table; DIG C.1 to C.3; STATUS pinned90 table, 12 of 12.

## 3. Section order and word budget

Text only, captions and tables excluded: 2,700 words, about 6.75 text pages at 400 words per page. Figures with captions about 3.5 pages, tables about 0.95, title block 0.2. Total about 11.3 pages. The render decides; if it exceeds 11.5, apply cut 1 of §10 first.

| § | Section | Words | Must establish |
|---|---|---|---|
| | Abstract | 220 | the thesis and F1 to F4 at strength, directional, one recommendation |
| 1 | Introduction | 340 | two kinds of evidence, two countermeasures, the sprint questions, scope, four contributions |
| 2 | Related work | 200 | only what the argument uses later |
| 3 | Setup | 560 | market and criterion, undercover market, M.S.'s runs and the pinned market, judges and statistics |
| 4 | Results | 1,020 | F1 in 4.1, F2 in 4.2, F3 in 4.3, F4 in 4.4 |
| 5 | Discussion | 270 | what counts as evidence, per family, breaking it up, four recommendations |
| 6 | Conclusion | 90 | the four findings in one sentence each, then the next tests |

Back matter, uncounted: Code and Data; Author Contributions; LLM Usage Statement; References; Appendices A to E.

## 4. Paragraph plan

Abstract, one paragraph, 220 words: the question (two kinds of evidence); the design (double auction, private messaging, report action, scripted seller, warning, three families, frontier sellers, opening price, pinned market); F1 with the 19 of 20, 0 of 20, 7 reported and agreed, unreported talk; the three families in one sentence; F2 with "never started", public talk continued, prices did not separate, null uninformative, 4+4 premium kept; F3 Sol vs Grok; F4 0 of 21 from $90, +$6.79 in 6 of 6 blocks p = 0.031, "no tested seller model raised prices", messaging sustained a high opening only for Gemini, pinned prices $3 to $7 above $90 with and without messaging; results directional; evaluators should read text and criterion together and add a competitive-opening control. Source: OLD abstract corrected by MSI §3 and STATUS.

1 Introduction. P1 (opening move, 90): the two kinds of evidence; the two countermeasures, a trusted agent that invites collusion and reports who takes it [Greenblatt; Hammond; Wehner and Kraprayoon] and a sentence announcing such agents; that this report reads messages, private reasoning and the criterion side by side in one market and finds they come apart. No novelty wording. Source: OLD §1 P1, V2 §1 P1. P2 (110): the sprint's three questions, each a one-line bullet with its track questions (Q1.1, Q1.5, Q3.2, Q3.3, Q3.4) and section pointers: when (seller model and opening price, §4.3, §4.4, "no tested seller model"); evidence (talk against the criterion, §4.1, §4.3); breaking it up (offer, warning, §4.1, §4.2). Source: OLD §1 bullets corrected by STATUS. P3 (60): threat model in one sentence; scope (one market, 3 to 6 seeds per cell, directional). P4 (80): four contributions with D.E. and M.S. attribution: the offer with placebo seat and report action across three families (D.E.); the warning with and without an offer and the precedent against a sham (D.E.); frontier sellers in the same market (M.S.); the replication of the opening-price effect with a pre-specified paired test and the pinned market (M.S. and D.E.). No "we add" and no "first".

2 Related work. P1 (80): the harness and its findings [Agrawal 2025]; LLM pricing collusion [Fish]; honeypots and warnings [Greenblatt; Hammond; Wehner and Kraprayoon 20% to 3%; Radev]. P2 (70): text and action evidence diverge [Nakamura; Xu; Azevedo]; opening anchoring [Struski; Hantel]; in this harness Douglas and Patil and Hoze report that the opening book sets the price, with their numbers; §4.4 replicates them. P3 (50): concurrent undercover offers [Adlakha and Adlakha; Qin HEYI; Chen], one clause each on what each found. End there (HS R2, R5). Source: OLD §2, V2 §2 for Douglas and Patil and Hoze.

3 Setup. 3.1 Market and criterion (140). P1: harness, costs and values, $90 midpoint as the index zero and $100 cartel price, ask index, opening near $97.50, messaging rules, prohibition notice off except three runs. P2: the joint high-price and trade criterion, fixed before the undercover runs; a threshold, not ground truth. Source: OLD §3.1 with "index zero" wording (MSI §3 item 3). 3.2 The undercover market (190). P1: five sellers, four Gemini, scripted seat 5, placebo or offer at hour 3 visible from hour 4, offer at the going price ($95.35 to $96.63), free report action, warning from hour 1, precedent; Table 1; 5 seeds per Gemini arm; GPT-4.1 and Haiku replications at 3 seeds; extensions ($99 offer; warning in the 4+4 market). P2 (50): seat 5 made 67 of 1,503 trades, so a price-taking benchmark puts this market's competitive price at $96 or above; $90 is kept as the index zero; LLM buyers are not price-takers, so this is a benchmark, not a prediction. Source: OLD §3.2; MSI §3 item 3; DIG B.1. 3.3 M.S.'s runs and the pinned market (150). P1: frontier runs (Sol, Luna, Grok; Haiku and Luna buyers; 36 runs), Sol under GPT-4.1-mini (6), Haiku sellers (9); proxy at low effort, no temperature or seed; the $90 opening runs and the route control (Table C2); the pre-specified test, "protocol written before the runs and committed in M.S.'s repository". P2: the pinned market, costs 80 80 80 90 and values 100 100 100 90, $90 the unique competitive price, opening unchanged at $97.50; D.E.'s Gemini and GPT-4.1 runs, M.S.'s Sol and Luna runs with GPT-4.1-mini buyers, messaging on and off, 3 seeds each. Source: OLD §3.3; DIG C.1; STATUS pinned90. 3.4 Judges and statistics (80), one paragraph: D.E.'s Haiku judge and its κ check; M.S.'s Grok judge; not pooled; permutation and Fisher tests, 2/252, 15 contrasts, Holm, directional; sign-flip 2/64. Source: OLD §3.4.

4 Results. Lead (40): Table 2 sets what sellers wrote beside what the criterion returned, in the order of the subsections. 4.1 The offer elicited reports, and some reporters feigned agreement (320). P1: 19 of 20, 0 of 20 in Base (p = 0.008), all first reports in hour 4, a response elicited by the probe, not a detection rate; 7 reported and agreed (9 replied, 8 agreed), rebuilt from the logs, 6 of 7 with the stated aim of keeping seat 5 anchored (two quotes, marked as quoted from D.E.'s run logs, his Table D7); 104 private messages per market between sellers in Base and D, none reported; the explicitness caveat. P2: D against Base is an offer-plus-price package; the pre-trend in D.E.'s numbers only (D −$0.48 per hour vs Base −$0.12 over hours 1 to 3; difference in slope change +$0.08 per hour, p = 0.70); the cleaner comparisons share seat 5's path. P3: three families (Figure 2b): GPT-4.1 as in F1 with "cost little" and the $99 result and its confound; Haiku as in F1 with the offer $10 above its market. P4 (60): pleas, 12 of 20 and 7 of 20 (p = 0.016); the pooled test under both definitions, first report 38 of 40 vs 19 of 40 (p = 0.003) and any report 39 of 40 vs 19 of 40 (p = 0.002); exploratory; a wording package. Source: OLD §4.1; MSI §3 items 4, 5; DIG B.1, B.2; STATUS fixes.

4.2 Under the warning, private messaging between Gemini sellers never started, and prices did not separate (240). P1: F2's talk result with the hour-1 timing, the 26 messages to seat 5, public messages by arm, the precedent's content against its length (suspects a test 16 vs 1; public 0 vs 45.8, p = 0.048). P2: prices did not separate, with the three p values; why the null is uninformative (Base 1 of 5, no messaging-off control, $1.28 hour-3 spread, the $96 benchmark), once (HS R9). P3: the 4+4 Gemini market, where messaging raises prices (3 of 3 vs 0 of 3): the warning's 0.70, 0.55, 0.35, 2 of 3, 0, 63, 0 private messages, about 80% of the premium against about half under the notice, 3 vs 3 seeds, directional; seed 1's neutral wording with four asks at $95.48; GPT-4.1 kept messaging under the warning alone and not with the precedent. Source: MSI §2; FIG Figure 2; DIG B.2; V2 Table D3.

4.3 Seller models split talk from the criterion (180). P1: F3's pass counts and Fisher p; Grok's private floor agreements below $90 (a verified private message from quotes_candidates.md, not the $86.47 public line); Sol's silent passes with the "focal clearing price" plan; Sol under GPT-4.1-mini. P2: D.E.'s judge against the criterion (Spearman 0.78, AUC 0.60, p = 0.18, 0.50 within Gemini, 10 passes under 2); M.S.'s Grok judge on Sol's silent passes; Spearman −0.01 across 18 messaging markets and 0.93 within Grok, post hoc. Figure 4. Source: OLD §4.3; DIG B.1.

4.4 Prices stay where the market opens: a replication and a pre-specified test (280). P1: hour 1 highest in 44 of 45; 8 raises in 2,519 moves; 0 of 21 from $90; Gemini at $90 with 113 to 114 private messages and "completely rock solid" at $88 to $90, the same market from $97.50 passing 2 of 3; Douglas and Patil and Hoze report the same effect, so this is an independent replication. P2: the pre-specified test as in F4, protocol wording as fixed; what it shows, bounded once: the high opening is needed for Sol's passes in these markets. P3: messaging and the opening (MSI §1 table, updated for Sol pinned): in no tested market did messaging raise prices above the opening; it sustained a high opening clearly only for Gemini in the ordinary 4+4 market; elsewhere silent sellers held it about as well (GPT-4.1, pinned Gemini, Sol at $97.50 under Haiku and Luna buyers) or neither arm did (Luna, Grok, the $90 openings); Sol in the pinned market is the one messaging-on advantage (3 of 3 vs 1 of 3, +$2.64, no private messages, n = 3). P4: the pinned market (Table 3) as in F4, with the partial bind and 3 seeds; the Gemini agy row only if any run has `collusion_metrics.json`, with the count stated. Source: OLD §4.4; MSI §1; DIG C; STATUS pinned90 table.

5 Discussion. P1 What counts as evidence (100): text flagged Grok and Gemini at $90 and neither passed; the criterion flagged Sol's silent passes; the judge tracks talk, not the criterion; the criterion is a threshold with no ground truth, a cartel at $88 fails it, a Sol pass can be patience at a seeded price; telling them apart needs a deviation test [Tran and Yu], not run; talk is informative within Grok and as a screen [Azevedo]. P2 Per family (70): a text-only monitor flags Grok, Haiku's bands and Gemini at $90 and misses Sol; a price-only monitor flags Sol and misses the below-benchmark cartels; the verdict changes with the opening; profiles in Appendix D. P3 Breaking it up (100): the offer elicited reports and feigned agreement and missed the sellers' own talk; offers recruit [Qin HEYI; Chen]; under the warning Gemini private messaging never started and prices did not separate, null uninformative; in the 4+4 market most of the premium survived; GPT-4.1 kept talking; reports cost nothing and sanctions were described, so nothing validates offers or warnings in deployment; Q3.4 answered within that bound. P4 Recommendations, four one-line items: competitive-opening control; text and criterion together; opening price, benchmark and buyer model with every pass rate; the undercover seller's price path held fixed [Adlakha and Adlakha]. Source: OLD §5 "Implications" and §6, corrected.

6 Conclusion (90), one paragraph: F1 to F4 in one sentence each at strength; directional; next tests: a longer horizon from the competitive opening, a base market that passes with a messaging-off control, an undercover agent that replies with a fixed price path, a pinned market whose pin binds, deviation tests from saved states. Not "an offer above the going price".

## 5. Figures and tables

Body figures, all 6.5 in wide, labels 14 pt, ticks 12 pt, titles 16 pt at print size, no claim title on any figure, captions at most 70 words, the caption carries the claim (HS R18, R19).

- Figure 1, `diag1_market.png`, §3.2, the market and what each agent sees. Carries the design. No change.
- Figure 2, `fig1_offer.png`, §4.1, reports and judge labels by arm (a) and the three families (b). Carries F1. Image unchanged. Caption: the 7 of 20 are now rebuilt from D.E.'s logs and are not plotted; drop "cannot be rebuilt".
- Figure 3, `fig2_warning.png`, §4.2, talk (a) and the criterion (b) by arm. Carries F2. Image unchanged. Caption opens with what it shows, not "ends private talk, not prices"; "$90 (dashed, the index zero)"; "never started" wording.
- Figure 4, `fig3_talk_vs_price.png`, §4.3, 110 markets. Carries F3. Image unchanged. Caption: "$90 (dashed, the index zero)".
- Figure 5, `fig4_opening_price.png`, §4.4. Carries F4. Change: drop old panel (a); new (a) = old (b), the $90 opening lines with the two pinned quotes; new (b) = old (c), the pre-specified slope chart; total height at most 5.5 in; fonts at the minimums at print size; "$90 (dashed, the index zero)". Old panel (a) retires to the supplement; Table C1 carries its numbers.
- Daniel's figures: none needed in the body. Our Figures 1 to 3 cover his `fig_design_timeline` and `fig_reporting_by_arm`; his `fig_report_and_feign` count is stated in text with its CSV source.

Tables. Table 1 (arms, §3.2, OLD Table 1, unchanged). Table 2 (§4 lead, four rows of OLD Table 2: Gemini Leo feign, Grok private floor agreement, Sol silent pass, Gemini at $90 "rock solid"; the full table goes to Appendix E). Table 3 (§4.4, new): the pinned market, one row per seller family and source (Gemini D.E., GPT-4.1 D.E., Sol M.S., Luna M.S., Gemini agy M.S. conditional), columns passes on and off, hour-15 mean ask on and off, ask index per seed, private messages per run; sources `daniel/pr44_pinned_price_oct26/report/data/pinned/` and `experiments/runs/box/pinned90/`.

Appendix figures: B1 `diag2_design.png`, B2 `diag3_our_tests.png` (caption rewritten to the agreed framing), D1 `fig5_model_profiles.png` with OLD Table 3.

## 6. Cuts

- OLD §5 Behavioural profiles (630 words, Figure 8, Table 3): to Appendix D; one paragraph survives in Discussion P2.
- OLD §4.4 P4 (Struski, Hantel, the positive control sentence): the citations move to §2 P2; the rest goes.
- OLD §4.2 P2 (prohibition notice in the 4+4 market): absorbed into 4.2 P3 as the "about half" comparator.
- OLD §4.3 "split appears in the first hour" paragraph with old Figure 7a: to Appendix C.
- OLD §1 last paragraph ("We add ...") and OLD §2 last sentence: cut (novelty, STATUS framing bullet 2).
- OLD §4.1 hour-by-hour ask steps ($0.37, $0.57, p = 0.56): replaced by D.E.'s pre-trend numbers, one set only.
- References not cited by the plan (Keppo; Lee; Zeng and Rudzicz; Agrawal 2026; Kale; Riemer; and V2's other new entries): out. Motwani stays in A.2, Liu in A.1.
- V2's gallery counts ("at least twenty entries", "nineteen use this harness", "eight or more entries find"): not repeated; unverified on our side.

## 7. Appendices

- A. Limitations and Dual-Use / Ethical Considerations. A.1 limitations, OLD A.1 items 1 to 12 corrected: item 9 loses "cannot be rebuilt"; add the 4+4 warning test (3 vs 3, smallest p 0.10, day-drift check at seed 0 only), the $99 confound, the partial bind of the pinned market, GPT-4.1 messaging under the warning. A.2 dual use and deception (OLD A.2). A.3 the plain offer and the warning texts (OLD A.3).
- B. Design diagrams: B1, B2.
- C. Run tables: C1 frontier (OLD B1), C2 $90 opening and controls (OLD B2), C3 pre-specified test (OLD B3), C4 pinned market per run, C5 warning in the 4+4 market (V2 D3 numbers, D.E.'s), C6 GPT-4.1 arms with the $99 extension (V2 D2, D.E.'s); the old 4.3 first-hour paragraph.
- D. Behavioural profiles: OLD §5 text, D1, OLD Table 3.
- E. Quotes with file and line (OLD Table 2 in full, OLD Appendix C quote sources), data and code availability, harness provenance.

Back matter before References: Code and Data (public repository and `mert_sprint/`; no dashboard link); Author Contributions (DIG A.1 item 8 plus the pre-registered test and the pinned Sol and Luna runs); LLM Usage Statement (Claude Code, mostly Opus 5.5, and Codex; a GPT-6 Pro external review of the joint package verified item by item; no token counts).

## 8. Opening and closing moves

Opening: the first paragraph gives the reader the two kinds of evidence and the two countermeasures, and says in one sentence that in this market they came apart. No history, no novelty claim.

Closing: the conclusion ends on the next tests, after one sentence per finding. The reader leaves with what an evaluator should run next, not a recap.

## 9. Framing traps the writer must avoid (quoted from the binding sources)

1. STATUS: 'The title "Talk Is Not Price" is dropped.' and 'The divergence is between talk and the criterion, not between talk and price.'
2. STATUS: 'Novelty claims in sections 1, 2 and 4.4 are dropped.' and 'Section 4.4 becomes an independent replication plus the pre specified paired test.'
3. STATUS: 'Use the GPT 6 Pro wording: "the offer elicited reports" and "the joint high-price and trade criterion".'
4. STATUS: 'The price null is uninformative. Do not write "warnings stop the talk, not the prices".'
5. STATUS: 'In the warning arms messaging never started, so nothing was "cut". Describe it as a between arm difference present from hour 1.' Never "ended", "cut private messages from 108 to 0 to 3", or "silenced".
6. STATUS: 'Write "no tested seller model raised prices". Grok and Haiku were never run from $90.'
7. MSI §1: 'The half "messaging sustains a high opening price" holds clearly only in row 1, weakly in row 1x and possibly in row 6'; never "messaging drives prices up" or "messaging maintained a high opening price" unqualified.
8. STATUS: '"7 of 20 agreed" should be "7 reported and agreed (9 replied, 8 agreed)".'
9. STATUS: plea test, 'First report: 38/40 vs 19/40, p = 0.003. Any report: 39/40 vs 19/40, p = 0.002.' Give both; pick neither.
10. STATUS: 'write "written before the runs, committed in M.S.'s repository"'; never "37 s before".
11. STATUS: 'Grok: the $86.47 line was a public message. Cite the private floor agreements instead (all below $90).'
12. MSI §3 item 1: '"Warnings drive talk to silence." ... holds only for Gemini in the 5+5 market'; 'GPT-4.1 sellers kept messaging under the warning alone.'
13. MSI §3 item 3: 'Caption "$90 (dashed, the index zero)"' and 'a price-taking benchmark here is $96 or above. We keep $90 as the index zero.'
14. MSI §3 item 4: '"That support cost nothing" ... "That support cost little"'; 'Section 6, drop "an offer above the going price".'
15. DIG F.1 item 10: 'GPT-4.1 never reports' is too broad; 'one seller reported seat 5 (8 reports)' at $99.
16. STATUS: track 'Q1.1, Q1.5, Q3.2, Q3.3, Q3.4 (not Q1.3)'.
17. STATUS: 'No aliasing applied to the reported frontier runs'; never "Sol served as gpt-5.4".
18. STATUS: 'Luna: 0/12 at $97.50 and 0/3 at $90.' In the pinned market Luna passed 1 of 6; keep the markets apart.
19. STATUS: D-hsb '7/20 reported seat 5'; '8/20 is "reported anyone"'.
20. MSI §3 item 5: Haiku refused '11 of 12 by D.E.'s reading' 'and 12 of 12 by the judge'.
21. Brief: no email, hostname, machine or account name; no dashboard link; no made-up number or reference.

## 10. CUT PLAN to 8 pages (ranked; each move needs one pointer sentence and no rewriting)

| Rank | Move | Saves | Cumulative |
|---|---|---|---|
| 1 | Figure 1 (`diag1_market`) to Appendix B | 0.55 | 0.55 |
| 2 | Table 2 (quotes) to Appendix E; §4 lead becomes one sentence | 0.35 | 0.90 |
| 3 | §2 P3 (concurrent offers) to Appendix A.1 context; Qin, Chen, Adlakha stay cited in §5 | 0.15 | 1.05 |
| 4 | Table 3 (pinned) to Appendix C4; 4.4 P4 keeps its first sentence | 0.30 | 1.35 |
| 5 | 4.2 P3 (4+4 warning, GPT-4.1 under warning) to Appendix C5 with its numbers; one pointer sentence stays | 0.30 | 1.65 |
| 6 | Figure 4 (`fig3_talk_vs_price`) to Appendix D | 0.67 | 2.32 |
| 7 | 4.3 P2 (judge against criterion, correlations) to Appendix C | 0.25 | 2.57 |
| 8 | §5 P2 (per family) cut to one sentence pointing to Appendix D | 0.15 | 2.72 |
| 9 | §1 P2 bullets cut to one sentence naming the track questions | 0.15 | 2.87 |
| 10 | 4.4 P3 (messaging and the opening) to Appendix C2 caption; one sentence stays | 0.20 | 3.07 |
| 11 | Figure 5 reduced to the slope chart alone (old panel c); the $90 lines to Appendix C | 0.30 | 3.37 |
| 12 | 4.1 P4 (pleas) to Appendix C6; one sentence with both p values stays | 0.15 | 3.52 |

From 11.3, ranks 1 to 10 reach about 8.2 and ranks 1 to 12 about 7.8. Stop at the first rank that brings the render to 8.0.

## NOTES

- Pinned Gemini via agy: 0 of 6 runs had `collusion_metrics.json` at 00:30 CT. Table 3 carries that row only if runs finish before the writer's pass, with the count stated.
- Wall in MSI §1: its proposed sentence put Sol in the pinned market among "silent sellers held it about as well" on 8 of 12 runs (2 of 2 vs 1 of 2). The full 12 give Sol 3 of 3 with messaging and 1 of 3 without, hour-15 $96.28 vs $93.64, with no private message in any run. The card plans the sentence from the complete data (4.4 P3). Daniel should be told, since his note cites the partial version.
- Douglas and Patil and Hoze: their reference entries come from V2's list and are not in pro_checks.md. Verify both project URLs before the writer cites them. Their numbers are quoted from STATUS and V2 only.
- The two feigned-agreement quotes (Leo, Amir) are from D.E.'s local logs; keep the "quoted from D.E.'s run logs" attribution, as OLD did.
- Pre-trend: one set of numbers, D.E.'s PR #40, recomputed on our side (DIG B.1). OLD's hour-step numbers are retired.
- Page arithmetic is an estimate from word counts and image heights; the render decides.
