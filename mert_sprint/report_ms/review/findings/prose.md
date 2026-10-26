> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Prose mechanics lens: findings

Lens: sentence-level voice, pruning, parallelism, numbers and units, register, term consistency, house-style violations.
Source: `report_ms/review/snapshot/REPORT.md`. House-style rules cited as R1 to R22 (HOUSE_STYLE.md). The "Prose" rule of the owner's global instructions (2026-09-08) is cited as PROSE-2026-09-08.
Mechanical scans run first: no em dashes or en dashes anywhere in REPORT.md; colons and semicolons in running prose all introduce a list, a definition or join two full clauses (R22 holds); "printed" does not occur (R20 holds). The findings below are what the scans do not catch.
Line numbers refer to REPORT.md in the snapshot folder. Quotes are verbatim.

---

## F-PROSE-01
- LOCATION: §3.2, “under which Gemini sellers in a 4+4 market passed in 3 of 3 seeds with messaging and 0 of 3 without”
- SEVERITY: high
- ISSUE: "under which" has no noun it can attach to (buyers? the market?), so the sentence must be parsed twice. "4+4" is used here for the first time without a definition, in a paragraph that describes a 5-seller market, and "positive control" (used in §4.4 and A.1 item 11) is never introduced. A.1 item 11 says the buyers were chosen on a "two-seed probe", while this sentence says 3 of 3 seeds, so the reader cannot tell which test the sentence reports.
- FIX: Replace the clause after "five GPT-4.1-mini buyers" with a new sentence: "With these buyers, Gemini sellers in a market with four sellers and four buyers (a 4+4 market) passed in 3 of 3 seeds with messaging and in 0 of 3 without. We call this run set the positive control." Then state in A.1 item 11 which of the two seed sets chose the buyers (two-seed probe) and which is the positive control (three seeds), and drop "overlaps" if the sets are nested.
- AUTHORITY: R17 (name exactly what a statement refers to); the dangling relative clause is a parse-twice fault (brief item 1).

## F-PROSE-02
- LOCATION: Abstract, “Messaging maintained a high opening price and did not create one.”
- SEVERITY: high
- ISSUE: The verb credits messaging with a maintaining effect that the report itself does not show. §4.3 says "We detect no messaging effect for Sol" (3 of 6 with messaging against 5 of 6 without), and no Gemini run without messaging exists at the $97.50 opening (Table B2). The same claim recurs in §4.4, “Messaging preserved the opening price; it did not raise it.”, and in the Discussion, “In our runs only maintenance occurred.” The last also clashes with §4.4, which says the test "does not decide whether the passes at $97.50 are collusion".
- FIX: Abstract (same word budget, the abstract is at the 250-word limit): "Messaging slowed the fall from the opening but raised no price." §4.4: "For Gemini at the $90 opening, messaging slowed the fall by about $1.60 (hour-15 means $88.82 against $87.23) and did not raise any price." Discussion: replace "A low-anchor control separates the formation of collusion from its maintenance. In our runs only maintenance occurred." with "A competitive-opening control separates the formation of high prices from the persistence of a high opening price. In our runs only persistence occurred."
- AUTHORITY: R7 (state a result at the strength the evidence gives); internal contradiction with §4.3 and Table B2.

## F-PROSE-03
- LOCATION: §1 contribution bullet, “A low-anchor control separates forming a cartel from keeping a high opening price”
- SEVERITY: high
- ISSUE: One manipulation has three names and its counterpart has four. The $90 manipulation is "low-anchor" (§1, §3.3, Figure 4, Tables B2, A.1), "competitive-opening control" (abstract, §1, §2, Recommendations) and "$90 opening" or "competitive opening" (abstract, §4.4). The default is "$97.50", "default opening", "high opening" and "seeded price". "Anchor" also names Hantel's prompt sentence in §4.4, which the text says is a different intervention. The reader must decide whether these are one control.
- FIX: Use "competitive-opening control" for the manipulation and "default opening" for $97.50 throughout. In §3.3 define once: "The competitive-opening control sets the opening ask center to $90 and changes nothing else." Replace "low-anchor test/runs/cell/contrasts" with "competitive-opening test/runs/cell/contrasts", retitle §3.3 "Frontier and competitive-opening runs", retitle Table B2 "Competitive-opening runs and their default-opening controls", and in §1 write "A competitive-opening control separates forming a cartel from keeping a high opening price."
- AUTHORITY: one name per concept (term consistency, brief item 3); R17.

## F-PROSE-04
- LOCATION: §4.3, “Sol met the joint criterion in 8 of 12 runs, 3 of 6 with messaging and 5 of 6 without”
- SEVERITY: medium
- ISSUE: §3.1 defines "the joint high-price and trade criterion" and never abbreviates it, yet §4 onward writes "the joint criterion", "the criterion", "passes" and "met". The abstract and §1 use the long form. "Late ask(s)" (abstract, §1, §4.3, Conclusion) is never defined; §3.1 and §4 use "last-third ask index", "last-third mean ask", "mean ask over hours 11 to 15", and §4.2 writes "mean ask indices". A reader meets four names for one window.
- FIX: In §3.1 write: "A market passes when it meets the joint high-price and trade criterion (the joint criterion below), which was fixed before the undercover runs. Over hours 11 to 15, the last third of the 15 hours, it requires ..." and add: "The last-third ask is the mean ask over these hours." Then replace "late ask(s)" with "last-third ask(s)" everywhere (abstract: "Sol's last-third asks", same word count) and "mean ask index" with "last-third ask index".
- AUTHORITY: term consistency (brief item 3); R17.

## F-PROSE-05
- LOCATION: Abstract, “7 of whom also signalled agreement by our reading”
- SEVERITY: medium
- ISSUE: The report switches between "we/our" and third-person initials for the same authors. The abstract says "by our reading", while §4.1, §5 and §6 say "by D.E.'s reading". §4.1 says "This count is his reading", Table 2's note says "His raw logs", Appendix C says "His raw run logs". The initials D.E. and M.S. are never glossed in the body, and the pronoun "his" is the only marker of who is meant.
- FIX: Abstract: "7 of whom also signalled agreement by D.E.'s reading" (same word count). §3 opening: "D.E. is Daniel Elliott and M.S. is Mert Senkardesler. 'We' means both authors, and the initials mark whose runs or readings a statement describes." Replace each "his" that refers to D.E. with "D.E.'s" ("This count is D.E.'s reading", "D.E.'s raw logs").
- AUTHORITY: R17 for the unglossed initials. The we/third-person mix has no card rule (OPINION).

## F-PROSE-06
- LOCATION: whole report, e.g. Abstract “7 of whom also signalled agreement by our reading”; §4.1 “reported and signalled agreement”
- SEVERITY: medium
- ISSUE: British spellings against R21 (American). Instances by line: signalled, L27, L39, L117, L171, L182; signalling, L54, L115, L171; favour/favours, L43, L58; centre, L87; centred, L155; relabelled, L93; grey, L131, L149.
- FIX: signalled -> signaled; signalling -> signaling; favour -> favor ("a favor game", "favor swap"); centre -> center ("ask center"); centred -> centered; relabelled -> relabeled; grey -> gray. Leave the reference-list title (L208, "Favour Game") in the cited paper's own spelling.
- AUTHORITY: R21.

## F-PROSE-07
- LOCATION: §3.2, “Every arm has a free `report_to_regulator` action, and the one-sentence warning (Appendix A.3) is in the prompt from hour 1.”
- SEVERITY: medium
- ISSUE: The coordinated "and" makes the warning look like a property of every arm, but Table 1 gives it to five arms only (E, F, F-sham, G-warn, G-prec). The same paragraph then counts "20 seller-episodes" per arm while §4 and the abstract count "20 sellers", so a count of sellers is a count of seller-episodes without saying so.
- FIX: "Every arm has a free `report_to_regulator` action. In the five warning arms (E, F, F-sham, G-warn, G-prec), the one-sentence warning (Appendix A.3) is in the seller prompt from hour 1." Then add after "20 seller-episodes": "(each seller in each market counts once, so counts 'of 20 sellers' are counts of seller-episodes)."
- AUTHORITY: R17.

## F-PROSE-08
- LOCATION: §3.1, “The harness seeds seller asks near $97.50 and buyer bids near $82.50.”
- SEVERITY: medium
- ISSUE: "Seed" carries two meanings within a few lines. It is the random seed ("3 seeds per cell", "six seed blocks", "seed label") and the initial order book ("seeds seller asks", "the seeded ask centre", "the seeded $97.50", "a seeded price", "the seeded book"). §4.4 puts both in adjacent sentences ("the harness seeds ... 3 seeds per cell").
- FIX: Keep "seed" for the random seed only. §3.1: "Each market starts with seller asks near $97.50 and buyer bids near $82.50 (the opening order book)." §3.3: "set the opening ask center to $90". §4.3: "close to the opening ask of $97.50". §4.4: "seeds the opening order book" -> "opens the order book"; Discussion: "patience at a seeded price" -> "holding the opening price" (see F-PROSE-15).
- AUTHORITY: one word, one meaning (term consistency, brief item 3); R17.

## F-PROSE-09
- LOCATION: §4.2, “against 108 private messages in Base and D”
- SEVERITY: medium
- ISSUE: One quantity appears under three numbers with no bridge. §4.1 gives "104 private messages per market in both Base and D", the same §4.2 paragraph opens with "103.4 to 104.2 per market", and then "108 private messages in Base and D" follows. The 108 counts messages to seat 5, the 104 does not (figures_README.md lines 108 and 112). The p = 0.008 does not say which count it tests.
- FIX: "The 0 to 3 private messages per market that remained all went to seat 5. Counting messages to seat 5, Base and D averaged 108 per market (about 104 between sellers), against 0 to 3 in the warning arms (p = 0.008 for D against E and for Base against G-warn)."
- AUTHORITY: figures_README.md lines 108 and 112; R17.

## F-PROSE-10
- LOCATION: §4.3, “so within Grok more talk did go with higher late asks (Figure 3)”
- SEVERITY: medium
- ISSUE: The sentence states a finding ("did go") that the parenthetical in the sentence before it undercuts: n = 6 markets, one subgroup "among several inspected after the fact". All six Grok markets have ask indices from −0.79 to −0.06 (figures_README.md line 145), so the correlation sits entirely below the benchmark. The parenthetical also interrupts the sentence that carries the number.
- FIX: "Within Grok's six messaging markets it was 0.93 (exact p = 0.033). We inspected several subgroups after the fact, so we read this as exploratory: among Grok's markets, those with more private messages had higher last-third asks, all of them below $90 (Figure 3)."
- AUTHORITY: R7 (an interpretation stays "consistent with" or "may"); R17.

## F-PROSE-11
- LOCATION: Figure 1 caption, “The 7 of 20 feigned agreements of §4.1 are D.E.'s reading of the transcripts and are not plotted.”
- SEVERITY: medium
- ISSUE: The same count of 7 has two names. The abstract, §4.1, Discussion and Conclusion say "signalled agreement". Figure 1 and A.1 item 9 say "feigned agreements", which asserts intent for all 7 although §4.1 says only "in several cases" was agreement used to keep seat 5 high and undercut it. §4.1 also has two unclear "it": "in several cases to keep it priced high and undercut it".
- FIX: Caption and A.1 item 9: "The 7 of 20 sellers who signaled agreement (§4.1) are D.E.'s reading of the transcripts and are not plotted." §4.1: "... 7 of 20 sellers also signaled agreement to seat 5, in several cases pretending to agree while undercutting the price they agreed to (Table 2, first row)."
- AUTHORITY: R7; R17.

## F-PROSE-12
- LOCATION: §5, “Undercover offers elicited reports from the sellers who received them, including sellers who, by D.E.'s reading, reported and signalled agreement in the same run.”
- SEVERITY: medium
- ISSUE: The "How to break it up" paragraph re-narrates §4.1 and §4.2: offers elicit reports, reports are "a response to the probe" and do not measure detection (said in §4.1 and again here), the warning stopped talk, GPT-4.1 kept talking (said in §4.2). "What counts as evidence" repeats the criterion-is-a-convention point of §3.1 and A.1 item 4, repeats Azevedo et al. from §2, and ends with "We did not run one." and "so talk is not uninformative either" (a double negative that restates Grok's post-hoc correlation as a general claim). Both paragraphs are single blocks of 12 or more sentences.
- FIX: Replace the "How to break it up" text from "Undercover offers elicited" through "GPT-4.1 sellers kept talking under the same warning." with: "Undercover offers elicited reports from the sellers who received them and did not reach the sellers' own talk (§4.1). The reports respond to the probe and do not show how well an offer finds an existing cartel. Concurrent work finds that such offers can also recruit colluders [Qin HEYI, 2026] and raise later recruiting [Chen, 2026]. Warnings ended the talk, and prices did not move detectably (§4.2), so in this design the price null cannot tell deterrence from a move to tacit coordination. Agrawal et al. [2025] likewise saw an overseer lower prices while sellers kept signaling." In "What counts as evidence" delete "We did not run one.", "Message volume did not predict price across models but did within Grok, so talk is not uninformative either." and the Azevedo sentence, and start a new paragraph at "Telling these cases apart".
- AUTHORITY: R5 (state each result once); R8 (cut sentences that only say what was not done); PROSE-2026-09-08 (break paragraphs at each new idea).

## F-PROSE-13
- LOCATION: Figure 3 caption, “Grok 4.7 markets carry heavy talk below the line, silent GPT-5.6 Sol markets sit above it”
- SEVERITY: medium
- ISSUE: Four captions (Table 2, 115 words; Figures 1, 3 and 4, 185, 194 and 242 words) carry what the body already says or what Appendix C holds. (a) Figure 3: "the line" has no antecedent (three horizontal lines are defined), and the closing sentence restates §4.3. (b) Figure 4: "All six blocks are higher from $97.50 (mean difference +$6.79, exact two-sided sign-flip p = 2/64 = 0.031)" and "(5 of 6 from $97.50, 0 of 6 from $90)" restate §4.4 and Table B3. (c) Figure 1 (185 words) adds checks, counting rules and an unplotted count. (d) Table 2 cells and caption carry run-folder names such as `agy_gemini_comms_gpt41miniB-seed0` and `unified.log`, which Appendix C lists.
- FIX: Figure 3 last sentence: "Grok 4.7 markets with heavy talk lie below the $90 line, and silent GPT-5.6 Sol markets lie above the $95 line." Figure 4: delete the two quoted restatements from the caption. Figure 1: move "counting only first reports gives 19 for D-hb and 18 for E" and the second-model sentence to the text or A.1. Table 2: replace each run folder name in column 1 with "run 1" to "run 5" and list "run n = folder" in Appendix C; shorten the caption to the dagger note and the row 3 note.
- AUTHORITY: R18 and R19 (captions: layout once, plain quantities, no provenance or display conventions); R4 (log-style internals); R5.

## F-PROSE-14
- LOCATION: §2, “Heterogeneity and more competitors make LLM collusion fragile [Keppo et al., 2026].”
- SEVERITY: medium
- ISSUE: Eleven works are cited only in §2 and never used again: Keppo, Lee, Zeng and Rudzicz, Agrawal et al. 2026, Greenblatt, Hammond, Wehner and Kraprayoon, Radev, Kale, Xu, Riemer. Each gets a one-clause "X found Y" sentence, so the register is flat across both paragraphs. One of them (Riemer) runs 43 words and hides two claims. The Nakamura sentence appears word for word in §1 and §2, and §1 and §2 each end with an "We add ..." sentence that lists the same additions.
- FIX: Keep Agrawal et al. [2025], Nakamura, Azevedo, Struski, Hantel and Tran and Yu (the studies the argument uses). Keep the two warning results as comparisons: "Wehner and Kraprayoon [2026] report that warnings about honeypots cut successful attacks from 20% to 3%, and Radev et al. [2026] report that telling agents a monitor is present halved Gemini's sabotage success. Our warning ended private messaging between sellers and left prices unchanged (§4.2)." Cut the other nine sentences, or collapse them into one sentence in §1. Delete the Nakamura sentence from §2 and the closing "We add ..." sentence from §1 (or §2). Bibliography entries for cut works go with them, per the no-ghost-entries rule.
- AUTHORITY: R2 (cite where the argument uses it, omit studies listed for completeness); R5; T-PROSE-01 for the uniform "X found Y" register.

## F-PROSE-15
- LOCATION: §4.4, “so a Sol pass can be patience at a seeded price”
- SEVERITY: low
- ISSUE: Mannered or metaphorical phrases where a literal one is available. Candidates by quote: "the offer sat about $10 above their market" (also "The offer sat at the going price", L123, L230); "patience at a seeded price" (L169) and "patience at a high opening price" (L226); "their reported collusion also descends from a high opening price" (L155) and "how fast asks descend" (L228); "so the softer Haiku and Luna buyers do not explain its passes" ("softer" is undefined); "as vendored for the sprint" (L64, L293); "Grok 4.7 sellers talked like a cartel and never passed" (L141); "Warnings drive talk to silence." (L171); "so that a pass measures formation and not a kept opening price" (L175).
- FIX: "the offer price was about $10 above their market price"; "The offer was at the going price"; "a Sol pass can be a seller holding the opening price"; "their reported collusion also starts from a high opening price"; "how fast asks fall from $97.50"; "so the Haiku and Luna buyers alone do not explain its passes"; "as copied into the sprint harness"; "Grok 4.7 sellers wrote cartel-style floor proposals and never passed"; "Warnings ended the talk."; "so that a pass shows that high prices formed, not that a high opening price persisted".
- AUTHORITY: PROSE-2026-09-08 (say what you mean; use the literal phrase); R17 for "softer".

---

## Dismissible notes (not counted among the 15 findings)

Each is labeled dismissible. They are mechanics the judge may adopt or drop.

- D1 (dismissible), §3.4, “verbal rejection, suspects collusion and suspects a test”. The list mixes noun phrases and verb phrases after "labels". Fix: "labels verbal agreement (...), verbal rejection, suspicion of collusion and suspicion of a test", and use "suspicion-of-a-test label" in A.1 item 9 and A.2 for "suspects-a-test label". Authority: parallelism, brief item 3.
- D2 (dismissible), A.1 lead-ins, “**The judges are models.**” against “**Buyers.**”. Bold lead-ins mix full clauses (items 4, 7, 9, 10) with noun labels (items 1, 3, 5, 6, 8, 11, 12). Fix: noun labels throughout ("Criterion as convention", "Base without a no-messaging control", "Model judges", "Free report action, simulated sanctions"). Authority: parallelism in lists.
- D3 (dismissible), numbers. §3.2 mixes "five sellers" with "5 seeds" in one paragraph; §3.1 "up to 2 private messages"; Figure 4 "Two private messages"; §4.3 “Sol's mean hour-1 ask was $96.7” should read "$96.70" (figures_README.md line 173); Table B2 and B3 captions “(M.S., Oct 25)” should read "(M.S., 2026-10-25)" or "October 25, 2026"; “2/252 ≈ 0.008” uses "≈" while “2/64 = 0.031” in §4.4 and the Figure 4 caption uses "=" for a rounded value (2/64 = 0.03125). Fix: numerals for all counts in a context; "≈" for rounded values. Authority: Chicago ch. 9 (consistency of numerals within a context).
- D4 (dismissible), §4.4, “Across all 21 runs opened at $90, none passed and no last-third ask index exceeded 0.01.” This repeats, nearly word for word, “No run passed (0 of 15), and no last-third ask index exceeded 0.01.” two paragraphs earlier. Same paragraph: “All 12 markets were launched at once, as the protocol states, finished before its cut-off and needed no retry.” is run history. Fix: delete the earlier sentence's second half or the later sentence; delete the run-history sentence. Authority: R5, R4.
- D5 (dismissible), §4.4 first paragraph, “(`cda_types.py` defaults, upstream commit 2bb2a7e)” and the first sentence “The harness seeds sellers' asks near $97.50, and a pass needs a last-third mean ask above $95.” The first repeats Appendix C; the second repeats §3.1. Fix: delete both. Authority: R4, R5.
- D6 (dismissible), §4.4 last paragraph, “The positive control of §3.2 therefore measures the maintenance of a high opening price.” "Therefore" follows Hantel's anchoring result, but the conclusion rests on the $90 control. Also “supports the opening as an explanation but does not explain ours causally” is hard to parse. Fix: "Hantel's intervention is a prompt sentence and ours changes the opening order book, so his result makes an opening-price explanation plausible without establishing it for our markets. In the positive control of §3.2, a high opening price persisted. The competitive-opening control does not show collusion forming from a competitive start." Authority: R7, R17.
- D7 (dismissible), Table B1 caption, “The Haiku-seller rows combine M.S.'s step-A and all-Haiku step-B runs”. "Step-A" and "step-B" appear nowhere else in the report. Fix: describe the two sets by what they are or write "all with Haiku buyers" only. Also table headers use "msgs" while the text writes "messages". Authority: R4, R19.
- D8 (dismissible), §1 contribution 2, “Deterrence by belief separated from deterrence by presence”. The two terms occur nowhere else. Inference: belief = the warning, presence = a placed undercover seller. Fix: "A warning that undercover agents may be present, separated from an undercover offer, and the content of a precedent separated from its length (D.E.)." Authority: R17.
- D9 (dismissible), §3.3 second paragraph mixes the pre-specified test, the prohibition-notice Gemini runs, the proxy and failed turns in one block, and §3.3 uses “A control ran that Gemini market with messaging from $97.50.” Fix: new paragraph at "Three Gemini 3.8 Flash markets"; "As a control, we ran that Gemini market with messaging from the default $97.50 opening." Authority: PROSE-2026-09-08 (one idea per paragraph).
- D10 (dismissible), §4.1 repeats “quoted from D.E.'s draft report” three times (also Table 2 dagger and Appendix C). Fix: one sentence at the paragraph start: "Quotes in this paragraph are from D.E.'s draft report." Authority: R5.
- D11 (dismissible), §2 mixes tenses within single summaries (the Adlakha and Adlakha sentence runs from present "give" and "vary" to past "moved", "worked" and "was reported"). Fix: present tense for what each study reports. Authority: OPINION.
- D12 (dismissible), model naming: “gpt-4.1-mini” in §2 against “GPT-4.1-mini” elsewhere. Fix: "GPT-4.1-mini". Authority: term consistency.
- D13 (dismissible), §4.1 plea paragraph, “A human seller's plea gave 12 of 20 reports (p = 0.29 against D)”. Arm labels D-hs and D-hsb are missing where D-hb is given, and "factorial" is undefined. Fix: "In D-hs (a human seller's plea) 12 of 20 sellers reported (p = 0.29 against D), and in D-hsb (adding a human buyer's plea) 7 of 20 did (p = 0.016). In D-hb (a buyer's plea alone) reports stayed at 20 of 20." Authority: R17.
- D14 (dismissible), source hygiene: the HTML comment “ORCHESTRATOR FLAG” in the Code and Data section and the word-count comment at the top are work comments inside the deliverable. They do not render, but R14-style completion applies before the clean copy. Authority: OPINION.
