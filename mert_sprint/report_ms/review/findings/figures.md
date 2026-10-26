> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Figures and tables lens: findings

Basis: all eight PNGs in `snapshot/figures/` viewed (fig1 to fig4, fig5, diag1 to diag3), and `full.pdf` rendered with pdftoppm (pages 4 to 9, 11, 13, 19 to 21 inspected at 100 dpi). Placement sizes come from `pdfimages -list` and `pdftotext`. `fig5_model_profiles.png` and `diag1` to `diag3` are not called out in `REPORT.md` or placed in `full.pdf` (see F-FIG-15). Nothing in the report or any other file was edited.

---

## F-FIG-01
- **LOCATION:** §4, all four data figures; Figure 4 caption: "Figure 4. Prices stay where the market opens (M.S.'s runs)."
- **SEVERITY:** high
- **ISSUE:** `pdfimages -list` shows every figure embedded at 1166 px and 200 ppi, that is 5.83 in wide, while the scripts design them at 6.5 in and the text block is about 6.45 in. The scale of 0.897 puts ticks at 10.8 pt, axis labels at 12.6 pt, titles at 14.4 pt and in-figure notes at 10.8 pt, all below the owner minimums (ticks 12, labels 14, titles 16, other text 12) at print size.
- **FIX:** In the PDF build, remove the 90% width setting on figures. In `scripts/lib/style.py` set the figure width to the text width (6.45 in) and keep the 14/12/16 pt sizes, so the images insert at 100% with no scaling. Regenerate Figures 1 to 4 and re-run the font audit on the placed size, not the design size. Figure 4 then needs the shorter layout of F-FIG-06.
- **AUTHORITY:** Owner rule "Matplotlib Figures" (labels >= 14 pt, ticks >= 12 pt, titles >= 16 pt); `figures_README.md` "Text sizes" audits the design size only.

## F-FIG-02
- **LOCATION:** Figure 1 caption: "Arms with the warning in the prompt are shaded."
- **SEVERITY:** high
- **ISSUE:** The caption lists what is plotted and carries counting provenance (first reports give 19 and 18, n labels already on the axis), but it does not say what to conclude. The arm codes D-hs, D-hb, E, F, G-warn and G-prec are defined only in Table 1 on page 4, four pages before the figure. The five zeros in the "Agreed with a peer" column of panel (a) read as a result, yet they only reflect that warned sellers sent no private messages.
- **FIX:** Replace the caption by: "Figure 1. Gemini sellers reported the plain offer in 19 of 20 cases (arm D) and in 20 of 20 cases under a warning (E, F, F-sham), GPT-4.1 sellers never reported it, and Haiku sellers rejected it (D.E.'s runs). (a) Gemini 3.8 Flash sellers, out of 20 per arm (arms as in Table 1), who reported seat 5 and who were judge-coded as agreeing with any peer's price proposal. Arms with the warning in the prompt are shaded. Agreement is 0 in those arms because their sellers sent no private messages (Figure 2a). Base, G-warn and G-prec received no offer. (b) The plain offer (arm D) made to three seller families. The offer sat at the going price for Gemini and GPT-4.1 sellers and about $10 above it for Haiku sellers. Only the Gemini labels were checked by a second model." Move "counting only first reports gives 19 for D-hb and 18 for E" and the 7-of-20 reading to the §4.1 text or Appendix A.
- **AUTHORITY:** House style R18 (first sentence says what the figure shows, then each subfigure) and R19 (leave out provenance a caption does not need); figures_README.md "Notes for the caption".

## F-FIG-03
- **LOCATION:** Figure 3 caption: "Talk against price for every market with a per-market message count, from both halves of the study"
- **SEVERITY:** medium
- **ISSUE:** The figure shows 110 markets. It omits the 9 Haiku-seller runs (Table B1 gives them a message count, 0.5 per market), the 12 pre-specified Sol runs (0 messages) and the 3 prohibition-notice Gemini runs (0 messages), which all have per-market counts, so "every market" is false (`figures_README.md`, "What is not drawn").
- **FIX:** Replace the first sentence by: "Talk against price for the 110 markets plotted, D.E.'s 50 Gemini markets and M.S.'s 60 Gemini, GPT-5.6 Sol, GPT-6 Luna and Grok 4.7 runs." Add at the end: "Not plotted are the 9 Haiku 5.5 seller runs (none passed), the 12 pre-specified Sol runs of Figure 4c, the 3 prohibition-notice Gemini runs and D.E.'s GPT-4.1 and Haiku markets, which have no per-market message counts."
- **AUTHORITY:** Caption-must-match-data principle; `figures_README.md` "What is not drawn, for the caption".

## F-FIG-04
- **LOCATION:** Figure 3 caption: "Markets with zero messages are spread in columns left of the axis break, one column per seller model, and their horizontal position carries no value."
- **SEVERITY:** medium
- **ISSUE:** Figure 3 is the paper's headline picture and does not carry its result at a glance. (a) The zero strip has four unnamed columns and one tick "0" that sits between the Gemini and Sol columns, so the reader cannot tell which column is which except by color. (b) The takeaways appear only in the last caption sentence. (c) About 25 of D.E.'s markers pile up at 91 to 114 messages, filled and hollow overlapping, so the pass counts cannot be read. (d) The legend says "Gemini, Daniel's 5+5 market" and "Gemini, our 4+4 market", while the report names owners as D.E. and M.S.
- **FIX:** (a) Replace the lone "0" tick by four 12 pt column labels under the strip, "Gemini 4+4", "Sol", "Luna", "Grok", with one bracket labeled "0 messages". (b) Add four 12 pt in-plot labels: "Warning arms: no talk, Base-range prices" on the yellow strip, "Sol, no talk: above $95", "Grok: 104 to 112 messages, below $90", "Gemini from $90: 113 to 114 messages, index 0"; then cut the last caption sentence. (c) Draw hollow markers first, filled on top, markers 20% smaller. (d) Legend entries "Gemini, undercover market (D.E., 5+5)" and "Gemini, 4+4 market (M.S.)".
- **AUTHORITY:** House style R19 (caption carries only what the figure cannot), R17 (name exactly what a label refers to); `figures_README.md` Figure 3 conventions (column order Gemini Daniel, Gemini ours, Sol, Luna, Grok).

## F-FIG-05
- **LOCATION:** Table 2 caption: "Table 2. What the agents said, in the order of §4.1 to §4.4."
- **SEVERITY:** medium
- **ISSUE:** Table 2 starts at the bottom of page 5, row 2 splits across the page 5 and 6 break, and the caption sits at the top of page 7, a full page after the last row. Column 1 holds long monospace run IDs (`agy_gemini_comms_gpt41miniB-seed0`) that break mid-word, and no column states what each row shows, so the table does not give its result at a glance.
- **FIX:** Put the caption above the table, forbid row splits (`tr { break-inside: avoid }` in the CSS, or `\nopagebreak` in LaTeX), and keep the table and caption together. Replace each run ID in column 1 by a label "Run 1" to "Run 6" and list label and folder in Appendix C, which already holds the folders. Add a fourth column "Reading" of at most five words per row, for example row 4 "Talk, low price", row 5 "No talk, high price", rows 6 and 7 "Talk, price at $90".
- **AUTHORITY:** Float-integrity principle (a caption stays with its float and rows stay whole); house style R18 (say exactly what each part shows).

## F-FIG-06
- **LOCATION:** Figure 4 caption: "Each line joins one seed block (3 to 8) from its run opened at $97.50 to its run opened at $90."
- **SEVERITY:** medium
- **ISSUE:** Figure 4 fills a page (5.83 by 7.85 in as placed). Its 230-word caption starts on page 13 and ends on page 14 after "pinned at the hours they were sent", so half the caption is separated from the figure. The caption restates results already in §4.4 and Table B3 (mean difference, p = 0.031, 5 of 6 and 0 of 6 passes, which are also on the panel (c) x labels).
- **FIX:** Reduce the figure height so figure and caption fit on one page (panels (a) and (b) 2.2 in, (c) 2.0 in at 6.45 in width). Replace the caption by: "Figure 4. Prices stay where the market opens (M.S.'s runs). (a) Mean seller ask by hour at the default $97.50 opening for GPT-5.6 Sol, GPT-6 Luna and Grok 4.7 sellers, messaging on (solid) and off (dash-dot), 6 runs per line. (b) Runs opened at $90, 3 per line, against Gemini 3.8 Flash from $97.50. The two quotes are private messages from one Gemini run, pinned at the hour sent. (c) The pre-specified test: each line joins one seed block (3 to 8) of Sol sellers from its $97.50 run to its $90 run, and filled markers meet the joint criterion. In all panels, horizontal lines mark $90 (dashed), $95 (dotted) and $97.50 (solid)."
- **AUTHORITY:** House style R5 (state each result once), R19 (leave out what the reader does not need), R18; page-break evidence in `full.pdf` pages 13 to 14.

## F-FIG-07
- **LOCATION:** §4.1: "A human seller's plea gave 12 of 20 reports (p = 0.29 against D)"
- **SEVERITY:** medium
- **ISSUE:** Four floats are never called out in the body. Figure 1a is not cited (only "Figure 1b" is). Table B1 is not cited anywhere in the body. Table 2 row 2 (Gemini Max, `agy_gemini_comms_gpt41miniB-seed0`) and row 4 (Grok Kai and Leo) are not cited, although the text cites rows 1, 3, 5, 6 and 7.
- **FIX:** (1) "A human seller's plea gave 12 of 20 reports (p = 0.29 against D; Figure 1a)". (2) In §4.3 after "Sol met the joint criterion in 8 of 12 runs, 3 of 6 with messaging and 5 of 6 without" add "(Table B1)". (3) In §4.3 after "and proposed floors in public" add "(Table 2, row 4)". (4) In §5 after "so we cannot say which source is right in a given market" add "(in Table 2, row 2, a Gemini seller wrote 'continue holding our firm line together' while asking about $9 below the others)". If row 2 or row 4 is not worth a citation, delete the row.
- **AUTHORITY:** Rule that every float is called out in the body and interpreted there; house style R11 (connect a result to the related result and say what it shows).

## F-FIG-08
- **LOCATION:** §4.3: "so within Grok more talk did go with higher late asks (Figure 3)."
- **SEVERITY:** medium
- **ISSUE:** Figure 3 is called out once, for one subgroup correlation that the plot barely shows, and without interpretation. It carries the evidence for three other claims (the warning arms at zero talk inside Base's range in §4.2, silent Sol above the line in §4.3, and the Gemini cartel at $90 in §4.4) that never cite it.
- **FIX:** In §4.3 write: "so within Grok more talk did go with higher late asks. Figure 3 shows the whole pattern: silent Sol markets sit above the $95 line, Grok markets with 104 to 112 messages sit below $90, and Luna sends no messages." In §4.2 after "inside Base's seed range of 0.12 to 0.61" add "(Figure 3 shows the same in all 110 markets)". In §4.4 after "Across all 21 runs opened at $90, none passed and no last-third ask index exceeded 0.01." add "Figure 3 rings 15 of them, and the other 6 are in Figure 4c."
- **AUTHORITY:** House style R11 (name the figure and say what it shows); callout-with-interpretation principle.

## F-FIG-09
- **LOCATION:** Figure 4 caption: "In all panels, horizontal lines mark $90 (dashed, the competitive price), $95 (dotted, an ask index of 0.5)"
- **SEVERITY:** medium
- **ISSUE:** Figure 3 labels its reference lines in the plot ("0, $90", "0.5, $95", "0.75, $97.50 opening") and Figure 2b labels them on the axis, but Figure 4 labels none, so the reader must read the caption to decode three gray lines in each panel. Figures 2 and 3 plot the ask index and Figure 4 plots dollars, with no mapping in the plot. Panels (a) and (b) have different y ranges (about 83 to 98 and 85.5 to 98), and only (b) has the axis title "Hour".
- **FIX:** In panel (a) add 12 pt gray labels at the left end of the three lines: "$97.50 opening", "$95, index 0.5", "$90, index 0". Say in the caption that the lines are the same in (b) and (c). Set (a) and (b) to the same y range (82 to 98) and add "Hour" under panel (a).
- **AUTHORITY:** Style-sheet consistency across sibling figures (figures_README.md "Shared conventions": reference lines); house style R19 (a line that marks a reference value stays in the caption, and in-figure labels spare the reader the caption).

## F-FIG-10
- **LOCATION:** Table B3 caption: "Table B3. The pre-specified paired test (M.S., Oct 25), with GPT-5.6 Sol sellers, Claude Haiku 5.5 buyers and messaging off."
- **SEVERITY:** medium
- **ISSUE:** In the render, Table B1 is at the bottom of page 19 and its caption at the top of page 20. Table B3 splits across pages 20 and 21 with a repeated header. Model names wrap inside cells ("GPT-5.6 / Sol", "Claude / Haiku / 5.5", "Gemini / 3.8 / Flash", "GPT- / 4.1-mini"), and numeric cells wrap inside parentheses ("0.43 (0.25 to / 0.60)"). In Table B2 the column "Hour-15 mean ask" mixes a list ("$88.50, $95.00, $95.30") with ranges, and "Private msgs per run" mixes "0, 42, 0" with "113 to 114".
- **FIX:** Caption above each table and tables kept whole (as in F-FIG-05). Use non-breaking spaces in model names and drop the Opening column from Table B2 by splitting it into two sub-blocks "Opened at $90" and "Opened at $97.50". Give every range cell the form "low to high" on one line, and give "Private msgs per run" the form "mean (range)" in Tables B1 and B2.
- **AUTHORITY:** Table format consistency across sibling tables (B1 uses "mean (range)", B2 uses lists); float-integrity principle.

## F-FIG-11
- **LOCATION:** Table 1 row: "offer as a human seller's plea (D-hs), plain offer with a human buyer's plea (D-hb), or both (D-hsb)"
- **SEVERITY:** low
- **ISSUE:** One row stands for three arms, and in the render the arm names break at the hyphens ("D-hs, D- / hb, D-hsb"), so the arm code is unreadable. The same design also appears as `diag2_design.png` (panel b).
- **FIX:** Split into three rows: "D-hs | offer as a human seller's plea | nothing", "D-hb | plain offer with a human buyer's plea | nothing", "D-hsb | offer as a human seller's plea, with a human buyer's plea | nothing". If `diag2_design.png` panel (b) enters §3.2, delete Table 1 so the arm design is stated once.
- **AUTHORITY:** House style R5 (state each definition once); table formatting.

## F-FIG-12
- **LOCATION:** §4.2: "against 108 private messages in Base and D (p = 0.008 for D against E and for Base against G-warn)"
- **SEVERITY:** low
- **ISSUE:** The text gives 108 for Base and D while the bars of Figure 2a, cited in the sentence before, read 103.6 for both. The difference is the messages to seat 5, which Figure 2a excludes (`figures_README.md`, Figure 2 table), and the sentence does not say so.
- **FIX:** "against 108 private messages per market in Base and D when messages to seat 5 are counted (Figure 2a plots only the 103.6 between sellers; p = 0.008 for D against E and for Base against G-warn)".
- **AUTHORITY:** House style R17 (name exactly what a count refers to); `figures_README.md`, Figure 2 "Messages to seat 5 per market".

## F-FIG-13
- **LOCATION:** Figure 2 caption: "The grey band is Base's seed range (0.12 to 0.61)."
- **SEVERITY:** low
- **ISSUE:** "grey" occurs in the captions of Figures 2 and 3 ("the grey band is Base's seed range"). Both captions also repeat the in-figure legend ("circles, filled when the market meets the joint criterion"; "Filled markers meet the joint criterion, hollow markers do not, and black rings mark runs opened at $90").
- **FIX:** Use "gray" in both captions. Cut the legend repeats: in Figure 2 write "(b) Last-third ask index of each market (circles) and the mean of the 5 markets (black tick)."; in Figure 3 cut "Filled markers meet the joint criterion, hollow markers do not, and black rings mark runs opened at $90."
- **AUTHORITY:** House style R21 (American spelling) and R19 (display conventions left out of the caption).

## F-FIG-14
- **LOCATION:** Figure 4 caption: "Two private messages from one Gemini run opened at $90 are pinned at the hours they were sent"
- **SEVERITY:** low
- **ISSUE:** The two black pins sit on the 3-run mean line of "Gemini on, $90" ($89.12 at hour 1, $88.91 at hour 12), while the quoted run's own mean ask was $90.09 and $89.995 (`figures_README.md`, call-outs in (b)). Separately, the line-end labels use the series colors as text (Grok #CC79A7 about 3.1:1, Luna #009E73 about 3.4:1, Sol #D55E00 about 3.9:1 against white) at 10.8 pt as placed.
- **FIX:** Move each pin to the seed-0 run's own ask (draw that run as a thin line) or add "on the 3-run mean line" to the caption. Set label text in a darker shade of the series hue with at least 4.5:1 contrast (for example #8E3F72 Grok, #00785A Luna, #B04B00 Sol) and keep the series color on the line.
- **AUTHORITY:** WCAG 1.4.3 contrast minimum (4.5:1 for small text); house style R19 (a caption names what the figure plots exactly).

## F-FIG-15
- **LOCATION:** §3.1: "We use the continuous double auction of Agrawal et al. [2025] as vendored for the sprint."
- **SEVERITY:** low
- **ISSUE:** Section 3 has no diagram, and `diag1_market.png`, `diag2_design.png`, `diag3_our_tests.png` and `fig5_model_profiles.png` are not called out in `REPORT.md` (CONTEXT.md says they are being added in parallel). Dismissible until they are placed, but each has a defect to fix first: `diag3` says "Step A market", which the report defines nowhere (only the Table B1 caption says "step-A"). `fig5` has the header "Bertrand" touching the right image edge, uses "Prompt P0" and "Collusion gain" with no definition in the report, and does not say that the dollar bars run from the value to zero.
- **FIX:** Place `diag1` after the first paragraph of §3.1, `diag2` (panel b only, replacing Table 1) in §3.2 and `diag3` in §3.3, each with a caption in the R18 form, then renumber and re-check every callout with a script. In `diag3` replace "Step A market, every run:" by "4+4 market, every run:". In `fig5` add an 8 px right margin, define "Prompt P0" and "Collusion gain" in the caption, and state the bar encoding.
- **AUTHORITY:** House style R18 and R5; floats-never-called-out principle.

---

Dismissible concerns, listed and not counted above:
- Figures 2 and 3 draw the pale warning band over the gray Base band, which makes a brown overlap on which blue markers have slightly less contrast. The overlap is intended (`figures_README.md`) and the markers stay legible. Dismissible.
- Figure 4a: the Luna-on and Grok-on lines coincide from hour 5, so one hides the other. The leader-line labels resolve it. Dismissible.
- The Figure 1b palette uses sky blue (Haiku) next to blue (Gemini) and orange (GPT-4.1) next to vermillion (Sol) in other figures. Rows are labeled in Figure 1b and GPT-4.1 does not appear in Figures 3 and 4, so no reader is misled. Dismissible.
