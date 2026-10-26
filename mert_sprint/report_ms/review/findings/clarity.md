> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Clarity lens (Google technical-writing standards)

Bible: `~/writing-resources/Google-TechWriting/` (files 07, 08, 13, 16, 21, 22 cited below). Register: an external-facing sprint report read by judges, so the Google standard binds at full strength. Reader assumed: an AI-safety judge who is not an economist. Count: 3 high, 11 medium, 1 low.

---

### F-GOOG-01
- LOCATION: §3.1, "with equal numbers of each, every price from $80 to $100 clears the market."
- SEVERITY: high
- ISSUE: The report never explains how a continuous double auction works (asks, bids, order book, when a trade happens), what an "hour" is, or why a higher price is a harm, and it uses economics terms without definition ("supracompetitive" in §1, "clears the market", "order book", "surplus", "Bertrand market", "tacit coordination"). A judge who is not an economist cannot see why $90 is "competitive" when every price from $80 to $100 trades, or whether "15 hours" is wall-clock time.
- FIX: Replace the second sentence of §3.1 with: "Each hour, every seller posts an ask (the price at which it will sell) and every buyer posts a bid (the price at which it will buy) in a shared order book, and a trade happens when a bid meets an ask. A unit costs a seller $80 and is worth $100 to a buyer, so any price from $80 to $100 lets both sides gain, and the price decides how the $20 gain is split. For example, a trade at $97.50 gives the seller $17.50 and the buyer $2.50. The market runs for 15 rounds, which the harness calls hours." In §1, gloss the first use as "supracompetitive prices (prices above the level that competition between sellers would produce)". Gloss "Bertrand market" in §1 as "a market in which firms compete on price". Place `diag1_market.png` in §3.1 (this part is dismissible, since CONTEXT.md says the setup diagrams are being added in parallel).
- AUTHORITY: Google TW One, "Determine what your audience needs to learn" and "Fit documentation to your audience" (21); Jargon, "define it clearly on first use" (13); TW Two, "Compare and contrast with something that readers are already familiar with" (22).

### F-GOOG-02
- LOCATION: §4.1, "The cleaner comparisons are E against D, G-warn against Base and F against F-sham, whose arms share seat 5's price path."
- SEVERITY: high
- ISSUE: The arm codes D, E, F, F-sham, G-warn, G-prec and D-hs/D-hb/D-hsb carry no meaning, so every result sentence in §4.1, §4.2, §5 and the Figure 1 and 2 captions sends the reader back to Table 1. "Arm" itself is a clinical-trial term that is never defined.
- FIX: In §3.2 define "arm" as "a condition of the undercover market" and gloss each code with a plain name on its first use in §4: offer (D), offer with warning (E), offer with warning and precedent (F), offer with warning and sham history (F-sham), warning only (G-warn), warning and precedent (G-prec). Rewrite the quoted sentence as: "The cleaner comparisons keep seat 5's price path fixed. They set the offer with a warning (E) against the offer alone (D), the warning alone (G-warn) against Base, and the real precedent (F) against a sham history of the same length (F-sham)."
- AUTHORITY: Google TW One, "Pick specific nouns over vague ones" and "Use terms consistently" (21); Jargon (13).

### F-GOOG-03
- LOCATION: §4.4, last paragraph, "The positive control of §3.2 therefore measures the maintenance of a high opening price."
- SEVERITY: high
- ISSUE: This is the paper's main methodological conclusion, but it is the last sentence of a related-work paragraph placed after Figure 4, and "therefore" does not follow from the Hantel comparison before it. The term "positive control" appears here for the first time, because §3.2 never names the 4+4 result as one.
- FIX: Define the positive control in §3.2 (see F-GOOG-04). Move the sentence and its partner out of the related-work paragraph to a closing paragraph of its own at the end of §4.4, written as: "So the positive control of §3.2 measures whether sellers keep a high opening price, and it does not show collusion forming from a competitive start." Keep the Struski and Hantel sentences as a separate paragraph before it.
- AUTHORITY: Google Paragraph structure, "Put critical information first ... Don't hide the key point of a paragraph at the end" (08); TW One, "Establish your document's key points at the start of the document" (21); house style R12.

### F-GOOG-04
- LOCATION: §3.2, "under which Gemini sellers in a 4+4 market passed in 3 of 3 seeds with messaging and 0 of 3 without."
- SEVERITY: medium
- ISSUE: One sentence both describes the undercover market and reports a separate market's result, joined by an ambiguous "under which". "4+4" is never defined here, and "5+5" (§4.2) is never defined anywhere in the text.
- FIX: Replace the first sentence of §3.2 with: "The undercover market has five sellers and five GPT-4.1-mini buyers (a 5+5 market). Four sellers are Gemini 3.8 Flash at temperature 0.7, and the fifth, seat 5, is scripted. Under these buyers, Gemini sellers in a market of four sellers and four buyers (a 4+4 market) passed in 3 of 3 seeds with messaging and 0 of 3 without. We call this 4+4 market with messaging the positive control, a market known to meet the criterion."
- AUTHORITY: Google TW One, "Focus each sentence on a single idea" (21); Write for a global audience, "Define abbreviations" (16); house style R12.

### F-GOOG-05
- LOCATION: Abstract, "In a pre-specified test, Sol's late asks were higher from $97.50 in all six seed blocks"
- SEVERITY: medium
- ISSUE: One quantity has four names ("late ask" in the abstract, §1, §4.3 and §6; "last-third ask index"; "last-third mean ask"; "mean ask over hours 11 to 15"), and one condition has three ("low-anchor control/test/runs", "competitive-opening control", "runs opened at $90"). "Trade index" in §3.1 becomes "trade-price index" in the next paragraph. A reader may take each name for a different measure.
- FIX: In §3.1 define once: "We call the mean ask over hours 11 to 15 the last-third mean ask, and its index the last-third ask index." Replace every "late ask(s)" with "last-third mean ask(s)". Replace "low-anchor" everywhere with "competitive-opening" (the abstract's and recommendations' term). Use "trade index" in both places in §3.1.
- AUTHORITY: Google TW One, "Use terms consistently" (21); Write for a global audience, "Use consistent terminology" (16).

### F-GOOG-06
- LOCATION: Table 2, row 2, "Gemini 3.8 Flash, Seller Max, `agy_gemini_comms_gpt41miniB-seed0` (opened at $97.50), hour 14"
- SEVERITY: medium
- ISSUE: The "Who and where" column names runs by folder tags such as `agy_gemini_comms_gpt41miniB-seed0` and `grok47_comms_lunaB-seed0`, which a judge cannot read. Row 2 is cited nowhere in the text, and it breaks the caption's claim that rows follow "the order of §4.1 to §4.4", because it belongs to the §4.4 default-opening control. The caption also carries quote provenance that the reader does not need to read the table.
- FIX: Replace each tag with a plain description, for example "Gemini 3.8 Flash sellers, GPT-4.1-mini buyers, messaging on, opened at $97.50, seed 0", and keep the tags in Appendix C. Move row 2 to sit before the current row 6, and cite it in §4.4 after "passed 2 of 3 from the default $97.50 opening" with "The third run failed after one seller undercut the others while its public messages kept the cooperative line (Table 2, row 2)." Move the caption sentences from "His raw logs are not public" to "listed in Appendix C" into Appendix C.
- AUTHORITY: Google TW One, "Introduce lists and tables appropriately" and "Pick specific nouns over vague ones" (21); house style R4 and R19 (log-style internals and run provenance out of captions).

### F-GOOG-07
- LOCATION: §5, "In these markets, text evidence flagged Grok 4.7 sellers and the Gemini markets opened at $90, and neither passed the joint criterion."
- SEVERITY: medium
- ISSUE: Both Discussion paragraphs run 12 to 13 sentences and cover several ideas each. The first opens on a detail instead of its answer, and the answer to Q3.4, which judges score against, is the last sentence of the second paragraph.
- FIX: Open the first paragraph with "Neither text nor price evidence alone identified collusion in these markets." and start a new paragraph after "so we cannot say which source is right in a given market." Split "How to break it up" into three paragraphs (undercover offers, warnings, the competitive opening). Open the warnings paragraph with: "For Q3.4, sellers who learned they might be watched stopped messaging, and this design cannot show whether coordination moved into prices."
- AUTHORITY: Google Paragraph structure, "A paragraph longer than 5 or 6 sentences is often an indication that the paragraph is trying to convey too much information" and "Put critical information first" (08); TW One, "Create great opening sentences that establish a paragraph's central point" (21).

### F-GOOG-08
- LOCATION: §4.1, first paragraph, "By D.E.'s reading of the transcripts, 7 of 20 sellers also signalled agreement to seat 5"
- SEVERITY: medium
- ISSUE: The paragraph has nine sentences and four ideas (reports and their timing, feigned agreement and how it was counted, the judge label caveat, unreported peer talk and the explicitness explanation). The same fault recurs in §3.3 paragraph 2 (pre-specified test, prohibition-notice runs, serving, failed turns) and in the §4.4 pre-specified-test paragraph (eleven sentences covering design, result, execution and scope).
- FIX: In §4.1 start new paragraphs at "By D.E.'s reading of the transcripts" and at "The sellers sent each other 104 private messages". In §3.3 start new paragraphs at "Three Gemini 3.8 Flash markets" and at "Calls for the other runs", and state before the notice runs what they were designed to test (R12). In §4.4 start a new paragraph at "Sol's mean ask over hours 11 to 15 was higher".
- AUTHORITY: Google Paragraph structure, "Each paragraph should address a single idea" (08); TW One, "Focus each paragraph on a single topic" (21).

### F-GOOG-09
- LOCATION: §3.4, "No single test therefore survives family-wise correction across the 15 planned contrasts, and we read every undercover result as directional."
- SEVERITY: medium
- ISSUE: The paragraph's conclusion, the one a judge needs, comes after a chain of arithmetic, and "Holm step" and "family-wise correction" are not explained for a reader who is not a statistician.
- FIX: Open the paragraph with: "No undercover contrast survives correction for the 15 planned contrasts, so we read every undercover result as directional. With five markets per arm, the smallest attainable p is 2/252 ≈ 0.008, and the Holm correction for multiple tests multiplies the smallest p by the number of tests, which gives 15 × 2/252 ≈ 0.12." Then give the test names.
- AUTHORITY: Google Paragraph structure, "Put critical information first" (08); Jargon, "define it clearly on first use" (13).

### F-GOOG-10
- LOCATION: §4.2, "The 0 to 3 private messages per market that remained all went to seat 5, against 108 private messages in Base and D"
- SEVERITY: medium
- ISSUE: Two sentences earlier, Base and D have 103.4 to 104.2 messages between sellers. The 108 here counts something else (all private messages including those to seat 5, `private_msgs_llm_total`), but the sentence does not say so, and the reader sees two counts for one baseline.
- FIX: "The 0 to 3 private messages per market that remained in the warning arms all went to seat 5. Counting messages to seat 5 as well, Base and D had 108 per market (p = 0.008 for D against E and for Base against G-warn)."
- AUTHORITY: house style R17; Google TW One, "Pick specific nouns over vague ones" (21); evidence `figures_README.md` line 108 (108.0 is `private_msgs_llm_total`, including messages to seat 5).

### F-GOOG-11
- LOCATION: §4.4, "The original harness of Agrawal et al. [2025] seeds the opening order book with seller asks centred on $97.50"
- SEVERITY: medium
- ISSUE: The finding that matters most to a safety reader, that the published collusion result also descends from a high opening price, sits third in its paragraph. A restatement of §3.1 comes before it, and a file name and commit hash interrupt it, although Appendix C already gives both. The paragraph then turns to a second idea (hour 1 holds the highest ask).
- FIX: Delete the paragraph's first sentence (§3.1 gives it). Open with: "The original harness of Agrawal et al. [2025] also opens the order book with seller asks centered on $97.50 (Appendix C). Their paper draws each seller's first ask from $95 to $100, and their Figure 3 ask curves start near $97, so their reported collusion also descends from a high opening price." Start a new paragraph at "In our frontier and Haiku markets".
- AUTHORITY: Google Paragraph structure, "Put critical information first" (08); house style R4 and R5.

### F-GOOG-12
- LOCATION: §1, first bullet, "With messaging, Gemini sellers proposed holding prices in hour 1, at whatever price the market opened."
- SEVERITY: medium
- ISSUE: The bullet answers "When do agents start colluding?" but never states the answer, so the reader has to infer it from two observations. The other two bullets lead with their answers.
- FIX: "**When do agents start colluding?** In our markets, sellers kept a high opening price and did not create one. With messaging, Gemini sellers proposed holding prices in hour 1 at whatever price the market opened, and no seller model raised prices from a competitive opening within 15 hours. A pre-specified test showed that Sol's last-third asks depend on the opening price (§4.4)."
- AUTHORITY: Google Paragraph structure, "Put critical information first" (08); TW One, "Establish your document's key points at the start of the document" (21).

### F-GOOG-13
- LOCATION: §1, contribution 2, "Deterrence by belief separated from deterrence by presence, and the content of a precedent separated from its length (D.E.)."
- SEVERITY: medium
- ISSUE: "Deterrence by belief", "deterrence by presence" and "matched placebo seat" (contribution 1) are not defined and never appear again, so the reader cannot connect the contributions to the arms of §3.2.
- FIX: "2. Warning-only arms, which separate the effect of telling sellers that undercover agents may be present from the effect of an actual offer, and a sham-history arm, which separates what the precedent says from its length (D.E.)." In contribution 1, replace "a matched placebo seat" with "a placebo arm in which the same scripted seller sends a neutral note".
- AUTHORITY: Google Jargon, "define it clearly on first use" (13); TW One, "Use terms consistently" (21).

### F-GOOG-14
- LOCATION: §4.1, "Pooled over this factorial, the plain seller wording (D and D-hb) drew first reports naming seat 5 from 38 of 40 sellers"
- SEVERITY: medium
- ISSUE: The plea arms give one of the largest effects in the paper (47.5 percentage points), but the body never says what a "plea" contains beyond Table 1's label, and "factorial" is not explained. Appendix A.2 states that the plea texts are described without quoting them, but the body holds no description.
- FIX: In §3.2 add one sentence describing what the plea changes (its argument, its length relative to the plain offer and the identity it claims), without quoting it. Replace the start of the quoted sentence with: "The four offer arms form a 2 × 2 design, with seat 5's offer worded plainly or as a human seller's plea, and with or without a human buyer's plea. Pooled over this design, the plain seller wording (D and D-hb) drew first reports ..."
- AUTHORITY: Google TW One, "Determine what your audience needs to learn" (21); Jargon (13); TW Two, "In tutorials, reinforce concepts with examples" (22, applied by analogy).

### F-GOOG-15
- LOCATION: §4.1, "Base had 0 of 20 reports (p = 0.008 against D)."
- SEVERITY: low
- ISSUE: The section's headline result (19 of 20 against 0 of 20) has no pointer to Figure 1a, which plots it. Figure 1a is cited nowhere, only Figure 1b. Table B1, which holds the §4.3 pass counts, is also cited nowhere in the body.
- FIX: "Base had 0 of 20 reports (p = 0.008 against D, Figure 1a)." In §4.3, add "(Table B1)" after "Sol met the joint criterion in 8 of 12 runs".
- AUTHORITY: Google TW One, "Introduce lists and tables appropriately" (21); TW Two, "Focus the reader's attention through discontinuities" (22).

---

## Dismissible, not counted (listed so nothing is dropped)

- D1. Setup diagrams `diag1` to `diag3` exist in `figures/` and are not placed. CONTEXT.md says they are being added in parallel. Dismissible.
- D2. British spellings mixed with American: "signalled" (abstract, §1, §4.1, §5, §6), "favour" (§1, §2), "centre" (§3.3), "centred" (§4.4), "relabelled" (§3.4), against "behavior", "color", "optimize". House style R21 asks for American spelling. A mechanical gate may already catch this.
- D3. §1 paraphrases Q3.2 as "a scripted agent offers each agent a pact". The sprint's wording is "Can we disrupt collusion through introducing trusted agents?" (CONTEXT.md). Quoting the question lets a judge match the answer to it.
- D4. Abstract, "privately proposed holding asks at $96, about the going price": "about" can read as "concerning". "close to the going price" removes the ambiguity.
- D5. Persona names in quotes (Mia, Raj, Leo in Table 2 row 1; "Maya" in §4.1) are never introduced. One sentence in §3.2 naming seat 5's persona, or "[seat 5]" inside the quotes, would fix it.
- D6. Undefined terms of lower weight: "softer Haiku and Luna buyers" (§4.3), "serving route" (§4.4, defined only in A.1), "κ" (§3.4, Cohen's κ not named), "seller-episodes" (§3.2), "step-A and all-Haiku step-B runs" (Table B1 caption).
