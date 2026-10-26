# Supplement check, 2026-10-25

This file records the check of `SUPPLEMENT.md` and `build/supplement.pdf` (43 figures, sections 3 and 4.1 to 4.4). It lists every issue found and the fix made.

## 1. Method

1. Every figure script was rerun under an audit wrapper. The wrapper recorded every text element of the saved figure and checked the owner's font floors (axis labels 14 pt, ticks 12 pt, titles 16 pt, other text 12 pt), text outside the canvas and text overlapping text. All 43 PNGs came out pixel-identical to the committed PNGs before any fix, so every figure reproduces from its script.
2. Every PNG was opened and read against its caption and explanation.
3. For every figure, at least two numbers in the text were recomputed by independent code. That code read the raw `unified.log`, `collusion_metrics.json`, `auction_results.md`, judge and Bertrand files, and D.E.'s CSVs, and did not use the supplement libraries. The D.E. CSV copies in `data/daniel/` were confirmed byte-identical to ApartAICollusion `origin/main` (e8c48ed), and `replay_base_pilot_norule.json` to its `configs/replay/base_pilot_norule.json`.
4. Every quote was matched verbatim at its stated file and line, with speaker, hour and channel. These were the eight quotes of S44.8, the four of S43.2 and the P0 prompt sentence of S43.9.
5. The PDF was re-rendered with `scripts/render_supplement.py` (46 pages). The pages were rasterised and inspected, and the corrected sentences were found in the PDF text.

## 2. Results per figure

All 43 figures pass the font audit, with no text below its floor and no text-on-text overlap. The audit flagged one item outside the canvas, the tick label "140" in S43.6(a). That label lies beyond the axis limit and is not drawn, so it is a false alarm. Every figure is 6.5 in wide at 300 dpi.

| Figure | Numbers recomputed independently (examples) | Result |
|---|---|---|
| S3.1 | 93 runs, passes, 21 runs at $90 with 0 passes | fixed (issue 1, issue 2) |
| S3.2 | hour-1 asks: Luna 25 of 48, Grok 34 of 48, Haiku 21 of 36 at $91 or below; Sol minimum $95.99 | correct |
| S3.3 | r = 0.984, 119 failing, 112 on ask, 19 and 16 near 0.5 | updated by issue 1 |
| S3.4 | 626 of 750, 495 of 600, gap $2.06, arm means $95.35 to $96.63, 30 of 50 | correct; source line clarified (issue 9) |
| S3.5 | Grok 7.92 per hour (from raw seller_dms), Sol 5 of 12 runs | updated by issue 1 |
| S3.6 | Sol 4 of 6 per buyer model, means 0.546, 0.505, 0.529 | fixed (issue 3) |
| S3.7 | handcheck table (10/7, 9/10, 7/10, 8/10, 0/10), Grok run means 1.00 to 1.28 and 3.47 to 3.93 | updated by issue 1 |
| S3.8 | Fisher p 0.10, 0.015, 0.061, 0.40, 0.0013; 4 ask-index permutation p 0.52 to 0.90 | clarified (issue 10) |
| S41.1 | per-seed counts, 22 of 25, 24 of 25 | correct |
| S41.2 | 120 reporters, 112 in hour 4, D 5 of 19, 23.0 and 5.8 reports per market | correct |
| S41.3 | 91 to 114 peer messages, 58 of 80, the 4 peer reports | correct |
| S41.4 | agreement 18 to 20, D 17 of 20, plea mentions 7, 3, 0 | correct |
| S41.5 | Gemini $93.85 to $97.05 (mean $95.76), GPT-4.1 9 of 12, Haiku mean $85.87 | correct |
| S41.6 | 0, 12, 11, 12 counts, ask index 0.28 to 0.72, p = 0.40 | correct |
| S41.7 | stratified p 192/63504, replies p 0.66 | correct |
| S41.8 | seat-1 5 of 5, 12/1024 | correct |
| S41.9 | −$0.91, −$0.22, p = 0.04, hourly steps and their p | fixed (issue 6) |
| S42.1 | $1.13 to $1.51, $0.33 to $0.55, $93.74 to $94.78 | correct |
| S42.2 | 0.6 and 3.2, 11 of 50 markets, p 0.87, 0.53, 0.48 | correct |
| S42.3 | 3 to 53 trades, CV 0.48 and 0.10, $519 against $435, p values | correct |
| S42.4 | r = 0.01 and 0.98, the 3 ringed markets | correct |
| S42.5 | $1.28 spread, r = 0.66 and 0.49 | fixed (issue 4) |
| S42.6 | median spreads $0.04, $0.07, $0.03, 42 of 50 | correct |
| S42.7 | 0 messages in 25 warning markets, F against F-sham p = 0.048 | correct |
| S42.8 | 9 to 14 in hour 4, 116 of 119 | fixed (issue 5) |
| S42.9 | 20 against 0, 14 and 16 against 1, all p = 0.008 | correct |
| S43.1 | 8 of 12 (2, 1, 2, 3), hour-1 means $96.71, $89.79, $89.96 | correct |
| S43.2 | index −0.35, 110 DMs, "Please keep new asks at or above 86.47" by all four sellers in hours 10 to 14, 12 identical Sol hours | correct; quotes verbatim |
| S43.3 | 48 Sol asks $95.99 to $97.60, 23 and 25 below $90, at least 6, 10, 11 runs matching | correct |
| S43.4 | Haiku $85.98 in hour 4, run band $85.43 to $86.63, Fisher p 0.011 and 0.0090 | clarified (issue 7) |
| S43.5 | ask and trade indices per buyer model, 0.4998 | correct |
| S43.6 | rho −0.01, 0.93, 0.70 | correct |
| S43.7 | 269 floor requests, 138 private, 174 of 207, 245 below $90 | correct |
| S43.8 | 1379 seller-hours with 3 unscored, score ranges | correct |
| S43.9 | Grok gain 0.972 and 26 of 30, Sol −0.016 and 22 of 30, Haiku and Gemini replicates | correct; P0 sentence verbatim |
| S44.1 | 11 of 18 and 0 of 21, maximum index at $90 0.006 | correct |
| S44.2 | hour-15 ranges by cell | fixed (issue 8) |
| S44.3 | paired differences +5.28 to +7.38, hour-1 gaps 7.50 to 7.64, all 15 hours above | correct |
| S44.4 | mean +6.79, p = 2/64 | correct |
| S44.5 | 80 of 81, Luna seed 2 hour 9 +$0.09, median fall $1.40 | correct |
| S44.6 | 34, 18 and 25 of 42 market-hours, $1.49, $0.06, $9.01 | correct |
| S44.7 | 243 of 339, 226 of 340, per-market shares, word list, 8 to 24 DMs per hour | correct |
| S44.8 | 8 quotes at file and line; mean ask $88.66 to $88.10; hour-14 asks | fixed (issue 8) |

## 3. Issues found and fixes

1. **One run was treated in two ways, and S3 called its criterion uncomputable.** The run is `shard3/B/20261024_224207_danielB_GGGG-seed0`. Its `unified.log` and metrics series stop after hour 1, but its `auction_results.md` holds all 15 hourly records, which agree with `unified.log` in hour 1. S4.3 recomputed the run from that file and found a pass (ask index 0.736, trade index 0.743, 3.0 trades per hour), as `notes/strategy_oct25/01_our_results.md` section 5.1 also does. S3 instead drew the run as "not computable" and left it out of S3.3, S3.5 and S3.6. As a result, S3.1 and S43.4 gave different pass counts for the same runs (Gemini with Haiku buyers, messaging on and off: 5 of 9 in S3.1 against 6 of 9 in S43.4). Fix: `scripts/S3/build_s3_data.py` now reads the run's hours from `auction_results.md` and recomputes its criterion with D.E.'s rule (helpers `rounds_from_results`, `mean_ask` and `criterion` added to `scripts/lib/s3lib.py`). The build checks hour 1 against `unified.log` and the message count against `dm_summary.total`. Only that row and its 15 hour rows changed in `data/S3/`. The hatched marker and the "not computable" legend entry were removed from the S3.1 and S3.7 scripts, the S3.5 group count was raised from 5 to 6 runs, and S3.1, S3.3, S3.5, S3.6 and S3.7 were regenerated. Text updated: M.S.'s runs pass 26 times, not 25. S3.3 now has 179 markets with correlation 0.985 and median difference 0.0048. S3.5 now has 45 runs and Gemini at 7.79 to 8.00 messages per hour. The S3.1, S3.3, S3.5 and S3.7 captions no longer say the criterion cannot be computed.
2. **S3.1 said the passes "sit in three places", and one of them was "Gemini with messaging from $97.50".** Gemini also passes without messaging. This covers 6 of D.E.'s warning-arm markets, 1 of 3 of our runs without messaging and 1 of 3 rule-notice runs. Fixed to: "The passes come from three seller models", with counts printed by the script. These are Gemini 3.8 Flash in 24 of D.E.'s 68 markets and 9 of M.S.'s 15 runs from $97.50, and GPT-4.1 in 10 of 15 markets.
3. **The S3.6 caption did not list every excluded run.** The figure leaves out the 6 pre-specified Sol runs at $97.50 with Haiku buyers, and the caption did not say so. Fixed in the caption and the script docstring.
4. **S42.5 gave the market range in a sentence about the five identical arms.** The range "$93.56 to $97.14" covers all ten arms, and $93.56 is an F-sham market. The same market (Base seed 0, $97.145) also read $97.14 here and $97.15 in S3.4. Fixed to "single markets in all ten arms span $93.56 to $97.15". The script now rounds half up for this value.
5. **The S42.8 caption referred to "The table".** No table is shown. Fixed to "D.E.'s outcomes table counts labels from hour 4".
6. **The S41.9(a) caption did not give the shown time range.** The panel shows hours 1 to 8 only. "over hours 1 to 8" was added to the caption and the script.
7. **S43.4 described a "band" without saying what it measures.** The band is the range of the 9 Haiku runs' mean asks over hours 11 to 15. The sentence now says so, in the text and the script.
8. **Two values ending in half a cent were rounded down.** These were S44.2, where the Luna hour-15 mean of $82.595 read $82.59 while the report says $82.60, and S44.8, where the buyer bid of $82.425 read $82.42. `money()` in `scripts/lib/s44lib.py` now rounds half up. The text reads $82.60 and $82.43. No other S44 number changed, and no S44 figure changed.
9. **The S3.4 source line did not name the original replay file.** The line now says the file is a copy of ApartAICollusion `configs/replay/base_pilot_norule.json`.
10. **S3.8 gave p = 0.031 without naming its test.** The figure marker for the same test shows the Fisher p of 0.015. The text now says that 0.031 belongs to the paired primary endpoint.
11. **Two section introductions were inaccurate.** S4.3 omitted the Sol runs with GPT-4.1-mini buyers that S43.5 uses. S4.4 said that S44.6 to S44.8 show "the sellers' own words", but S44.6 shows asks with and without messaging, and it now reads "set the sellers' talk next to their asks". The S44 builder `scripts/S44/build_section.py` was updated to match.

Every wording fix was made in `SUPPLEMENT.md` and in the matching fragment in `sections/` where that fragment carries the sentence. The fragments are earlier lane versions and differ from the edited book in other places. After the fixes, all S41 to S44 PNGs are still pixel-identical to the committed ones. Only S3.1, S3.3, S3.5, S3.6 and S3.7 changed, and the audit was rerun on them with no flags.

## 4. Open items, not fixed here

1. **S5 is cited by the report but absent from the book.** The report cites "Supplement S5" twice (section 5 and the Table 3 caption), for the keyword list and the quote checks. `sections/S5.md` (6 figures) and `sections/S45.md` (12 figures, numbered S4.5.x, although the report has no section 4.5) exist but are not in `SUPPLEMENT.md`, and they were not checked here. Whether to add them, and how to number S45, is a decision for the orchestrator.
2. **The truncated run is still left out in S5 and the report.** `sections/S5.md` leaves out the same GGGG seed 0 run "because its hourly log stops after hour 1", and the report's Figure 5 and Table 3 follow it. After issue 1 the book treats the run as recoverable. The report itself was not touched.
3. **Font sizes on the page.** The PNGs meet the font rule at their native 6.5 in width. The renderer scales 21 of the 43 figures to between 71 % (S43.9) and 98 % of the text width, so that each figure shares a page with its text. In the PDF their 12 pt text therefore prints at 8.5 to 11.8 pt. Printing every figure at full width (`MIN_SCALE = 1.0` in `render_supplement.py`) would move the text of those figures to the following page. That choice is left to the owner.
4. **Scaffolding left in place.** The `hours_logged == 15` filters in the S3.3, S3.5 and S3.6 scripts are now always true, because the build guarantees 15 hours for every run. They are harmless and can be removed in a cleanup pass.

## 5. Sections 4.5 and 5 added, and every figure at full width (2026-10-25, second pass)

This pass closes open items 1 to 3 of section 4. The book now holds 61 figures in 100 pages.

### 5.1 What was added

1. Section 4.5, "What the agents said, on the price path", holds the 12 figures of `sections/S45.md` (S4.5.1 to S4.5.12). Section 5, "Behavioural profiles of the seller models", holds the 6 pages of `sections/S5.md` (S5.1 to S5.6). Both sit after section 4.4 and before "Data and code".
2. Captions, explanations and sources were kept. The edits are format only. Source lines now follow the book (run folders prefixed with experiments/runs/, scripts relative to supplement/, no backticks). Negative numbers use the minus sign of the other sections. The S5 image paths lost their `../`. "Daniel" became "D.E." in S4.5.11, in the heading, the caption, and the figure's own title and note. The report's Figure 5 is now its Figure 8, so the S5 text says "Figure 8 of the report".
3. Each section has a new two-sentence introduction. Section 4.5 links to the report's Table 2, and section 5 links to the report's section 5 and Figure 8. The section 5 introduction has a third sentence. It says that section 5 follows the report and leaves out `shard3/B/20261024_224207_danielB_GGGG-seed0`, because the run's stored metrics cover only hour 1, while sections 3 and 4.3 include it, rebuilt from its round log (auction_results.md). This closes open item 2.
4. Section 5 keeps the method note of the fragment after its introduction. The note gives the three designs, the five-pattern keyword list, the read of 36 matches and the quote check. The report cites "Supplement S5" for the keyword list and the quote checks (section 5 and the Table 3 caption), so the note cannot be cut.
5. The book introduction now names sections 4.5 and 5. "Data and code" has rows for 4.5 and 5, says how the S45 and S5 scripts get their data, and records that D.E.'s report/data/ and REPORT.md are identical at commits b7cbccd (read by S5) and e8c48ed (copied to data/daniel/). The fragments in `sections/` received the two factual fixes ("Figure 8", "D.E.").

### 5.2 Full text width

1. **The previous PDF printed no figure at full width.** pandoc's reference document.xml holds an empty `<w:sectPr />`. The page-size patch in `render_supplement.py` replaced only `<w:pgSz>` and `<w:pgMar>` elements, which do not exist there, so it never took effect. pandoc then fell back to a print width of 420 pt and capped every image at 5.83 in, 90% of the 6.5 in the scripts draw. In that PDF the images measured 4.6 to 5.83 in, so 12 pt figure text printed at 8.5 to 10.8 pt. The main report's renderer has the same fix already (`report_ms/scripts/render_report.py`, line 121).
2. **Fix.** The renderer now writes the section properties (Letter, 1-inch margins) into the reference document. Every image measures 6.50 in wide in the new PDF (checked with PyMuPDF on all 61), so figure text prints at the size it was drawn at.
3. **Scaling removed.** `fit_width()` and `MIN_SCALE` are gone, because no figure is scaled any more. A figure taller than a page under its heading now stops the render with its name, instead of being shrunk. Each figure starts a new page. The first figure of a section follows the section introduction only when its whole block fits there. Otherwise the text of a block continues on the next page, and the renderer lists those blocks.
4. **Five figures were too tall for a page at full width.** The limit is 8.59 in under a one-line heading and 8.39 in under a two-line heading. The figures were S44.8 (9.40 in), S4.5.12 (8.60 in), S5.1 (8.74 in), S5.3 (8.69 in) and S5.6 (8.69 in). They were redrawn shorter with the same font sizes. S44.8 and S4.5.12 are now 8.40 in tall (figure height in their scripts). The S5 pages use a panel row of 2.30 in instead of 2.45 in and drop the blank band after the last quote, so S5.1 is 8.26 in and S5.3 and S5.6 are 8.21 in. Each script's own check passed (font floors, overlaps and canvas). A separate audit of the six S5 pages found axis labels of 14 pt or more, ticks of 12 pt or more and no text below 12 pt. All five were viewed.
5. **Placement.** All pages of sections 4.5 and 5, and the random older pages 5, 52 and 57, were viewed as page images. Every heading sits on the page of its image, and no image is clipped (lowest image bottom 9.78 in, on S5.1). 33 of the 61 figure blocks continue their text on the next page. For 7 of them only the source line goes over (S43.1, S43.2, S43.6, S44.1, S44.6, S4.5.4 and S4.5.9). The introductions of sections 4.2 to 4.5 now stand alone on their page, because the first figure block of each no longer fits below them. The section 5 numbered list renders with its numbers.

### 5.3 Reproduction and spot checks

1. The 12 S45 scripts and the S5 script were rerun before any change. All 18 PNGs were byte-identical to the committed ones, and every quote passed its file-and-line check (`scripts/S45/quotes.py` on import, `profiles_lib.verify_quote` in S5). After the changes, S4.5.11, S4.5.12, S44.8 and the six S5 pages were drawn again and passed the same checks. The other 11 S45 PNGs are unchanged.
2. Two or more numbers per new figure were recomputed by independent code. It read `unified.log`, `collusion_metrics.json` and D.E.'s CSVs directly and grouped runs by folder name, without the S45 or profiles libraries.

| Figure | Numbers recomputed independently | Result |
|---|---|---|
| S4.5.1 | asks $89.99 or $90.00 from hour 4; 4 trades per hour at $90.00 to $90.02 from hour 4; ask index 0.00 | correct |
| S4.5.2 | the four asks within $0.01 of each other in every hour from 4; all at $89.99 or $90.00 | correct |
| S4.5.3 | asks $97.32 to $97.60 and no trade in hours 1 to 13; hour 14 Max $88.30 against $97.31, one trade at $88.90; ask index 0.51, trade index −0.11, 0.8 trades per hour | correct |
| S4.5.4 | Max $88.30 in hour 14; Kai, and every seller, $88.50 in hour 15 | correct |
| S4.5.5 | all four asks $86.47 in hours 10 to 15; ask index −0.35 | correct |
| S4.5.6 | hour-1 asks $88.00, $97.50, $94.50 and $83.48; asks $87.96 to $88.00 from hour 2 and all $87.99 from hour 9; ask index −0.20 | correct |
| S4.5.7 | identical asks in 12 and 7 of 15 hours; no DM, and 46 of 56 public messages with "independently"; hour-15 means $97.50 and $95.40; indices 0.75 and 0.54 | correct |
| S4.5.8 | pre-specified test passes 5 of 6 at $97.50 and 0 of 6 at $90; seed-0 indices 0.75 and 0.01 | correct |
| S4.5.9 | hour-15 means $95.30 and $90.00; indices 0.53 (pass) and 0.00 | correct |
| S4.5.10 | seed 1: mean ask $96.09 to $96.18 in hours 1 to 6, first trade in hour 8, $93.03 to $93.17 from hour 10, index 0.31; seed 2: hour-1 asks $97.33 and $82.79 to $82.81, $85.70 to $85.80 from hour 5, index −0.42 | correct |
| S4.5.11 | D.E.'s market_by_hour.csv: mean ask $96.63 at hour 3, $95.39 at hour 6, $95.33 to $95.37 from hour 7 | correct |
| S4.5.12 | verdicts and indices of the six runs (0.00, 0.53, −0.20, −0.35, 0.75, −0.42) | correct |
| S5.1 | 17 runs; 1,888 messages in the 11 runs with messaging; 103 to 119 private messages per run; 7 of 11 pass from $97.50 and 0 of 6 from $90 | correct |
| S5.2 | 991 messages; late asks $82.12 to $89.44 and 0 of 12 pass; late ask $1.82 higher with messaging | correct |
| S5.3 | 927 messages; 7 of 12 runs with messaging send no DM; 17 of 24 pass from $97.50 (12 without messaging) and 0 of 12 from $90 | correct |
| S5.4 | 341 public and 0 private messages; late asks $82.12 to $93.09 and $82.59 to $88.69; no pass | correct |
| S5.5 | agreed 12, 12, 11 and 9 of 12 in Base, D, E and G-warn, 0 in F; F reported 12 of 12; asks $92.84 to $97.63; 10 of 15 pass | correct |
| S5.6 | 321 public and 3 private messages in 6 runs; 0 of 9 pass; arm D rejected 12 of 12 and reported 3 of 12 | correct |

Not recounted here are the explicit-wording shares, which depend on the keyword list itself, and the floor counts of S4.5.5 and the reasoning counts of S4.5.8, which the scripts compute and print. The Bertrand gains of Grok, Sol, Haiku and Gemini were recomputed for S43.9 above. The Grok and Luna minimum late asks are both $82.12, and they come from different runs.

### 5.4 Open items

1. The book uses two styles of figure number, S41.3 for section 4.1 and S4.5.3 for section 4.5, because the S4.5 numbers were set by request. The book introduction states both.
2. The 7 pages that hold only a source line could be avoided only by shrinking figures or text, which the font rule forbids.
