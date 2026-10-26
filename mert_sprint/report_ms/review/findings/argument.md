> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Argument and rigour lens: findings on REPORT.md

Lens: does every claim follow from its evidence and n. Checked against ms_runs.csv (recomputed per condition), prereg_result.md, pro_checks.md, figures_README.md, quotes_candidates.md and provenance.md. Severity counts: high 4, medium 9, low 2.

---

## F-ARG-01

- LOCATION: Abstract, "In a double auction with private messaging and a report action, they came apart in four ways."
- SEVERITY: high
- ISSUE: Only the Sol case (high prices with no talk) is a clean divergence between talk and price. §4.1 compares reports with peer talk, which are both text. The report itself calls the §4.2 price null "uninformative". In §4.4 the Gemini sellers named $90 as their target ("bring them to our $90 target") and held $89.97 to $90.00, so talk and price agree there, and only the criterion disagrees with them. The thesis is carried by three verdict disagreements and one null, not by four divergences.
- FIX: Abstract: "In a double auction with private messaging and a report action, a verdict from text alone and a verdict from prices alone disagreed in three settings, and in a fourth a warning removed the text evidence while the price test could not detect a change." Conclusion: replace "the evidence of collusion in logs and in prices came apart in four ways" with "verdicts from the logs and from prices disagreed in three settings, and a warning removed the log evidence in a fourth".
- AUTHORITY: R7. §4.2 ("This null is uninformative."). Table 2 rows 6 and 7. AP-ARG-04 (reasoning gap between the findings and the thesis).

## F-ARG-02

- LOCATION: §5 Recommendations, item 3, "Report the opening price, the benchmark convention and the buyer model with every pass rate, since each of them changed verdicts here."
- SEVERITY: high
- ISSUE: The data contradict this sentence for the buyer model. Sol passed 4 of 6 under each of its three buyer models: Haiku 2+2, Luna 1+3 and GPT-4.1-mini 2+2. Luna and Grok passed 0 under every buyer. §4.3 itself concludes that the buyers "do not explain its passes". The benchmark convention was never varied, so no verdict changed with it. Only the opening price changed verdicts. "Softer" buyers in §4.3 is also unsupported.
- FIX: "3. Report the opening price with every pass rate, since it changed verdicts here, and state the benchmark convention, since a stable cartel below it fails the criterion." In §4.3, replace "so the softer Haiku and Luna buyers do not explain its passes" with "so the buyer model does not explain its passes (4 of 6 under each of the three buyer models)". If the buyer claim rests on D.E.'s two-seed buyer probe, report that probe's numbers instead.
- AUTHORITY: ms_runs.csv (frontier and frontier_b41 rows). Table B1. R7.

## F-ARG-03

- LOCATION: Abstract, "Messaging maintained a high opening price and did not create one."
- SEVERITY: high
- ISSUE: At the $97.50 opening, Sol held prices better without messaging (5 of 6 passes, mean index 0.62, hour-15 mean $96.14) than with it (3 of 6, 0.43, $94.30). The only evidence that messaging maintains a high price is D.E.'s 3 of 3 against 0 of 3 Gemini pilot in §3.2 (Fisher p = 0.10), which ran on another serving route. The "+$1.60" at $90 is Gemini only. Sol's hour-15 means at $90 were $89.09 with messaging and $89.08 without. The same overreach appears in the §4.4 headline ("messaging held the opening price") and in "Messaging preserved the opening price; it did not raise it."
- FIX: Abstract: "For Gemini sellers opened at $90, messaging held prices near the opening (hour-15 mean $88.82 against $87.23 without it, 3 runs each) and did not raise them." §4.4 headline: replace "and messaging held the opening price" with "and Gemini messaging held prices near the $90 opening". §4.4: "At the $90 opening, Gemini talk added about $1.60 (hour-15 means $88.82 against $87.23), while Sol's hour-15 means were $89.09 with messaging and $89.08 without."
- AUTHORITY: ms_runs.csv. figures_README.md, Figure 4a and 4b tables. R7. R17.

## F-ARG-04

- LOCATION: §4.3 headline, "Grok 4.7 sellers talked like a cartel and never passed, while GPT-5.6 Sol sellers passed most often with no channel at all"
- SEVERITY: high
- ISSUE: Grok's talk named floors below $90 ("I will stay at or above 88", "at or above 86.47"), and asks settled at those floors ($87.99 and $86.47). Within Grok, more talk went with higher late asks (rho 0.93), and messaging-on runs sat above messaging-off runs (−0.27 against −0.45). In C8, talk and price agree on the level. They disagree only with a criterion built on the $90 midpoint convention. The evidence file says the run "fails only because the floor sits $2 under the $90 benchmark". Contribution 3 ("talk and price point in opposite directions for two models") has the same problem.
- FIX: §4.3 headline: "In the same market, Grok 4.7 sellers proposed price floors below $90 and either held or broke them, and never passed, while GPT-5.6 Sol sellers passed most often with no channel at all." Contribution 3: "Frontier sellers in the same market, where the verdict from talk and the verdict from the price criterion disagree for two models (M.S.)."
- AUTHORITY: quotes_candidates.md C8 and C9. pro_checks.md item 4. Table B1. R7.

## F-ARG-05

- LOCATION: §4.2 headline, "One warning sentence ended private messaging between sellers, with or without an undercover offer, and prices did not separate from Base."
- SEVERITY: medium
- ISSUE: The result holds for Gemini only. The same section reports that GPT-4.1 E markets "kept 57 to 68 private messages between sellers per run". The headline, the abstract ("ended private messaging between sellers") and the Discussion ("Warnings drive talk to silence") all state the effect without naming the model.
- FIX: §4.2 headline: "One warning sentence ended private messaging between Gemini sellers, with or without an undercover offer, and prices did not separate from Base. GPT-4.1 sellers kept talking." Abstract: "ended private messaging between Gemini sellers". Discussion: "Warnings drove Gemini talk to silence."
- AUTHORITY: R17. R7. §4.2, last sentence.

## F-ARG-06

- LOCATION: Abstract, "from a $90 competitive opening instead of the default $97.50, no seller model raised prices (0 of 21 passed)"
- SEVERITY: medium
- ISSUE: Only Sol, Luna and Gemini ran at $90 (Table B2 and the prereg runs). Grok, Haiku and GPT-4.1 did not. "No seller model" extends the result to three untested models. The same wording is in §1 ("No seller model raised prices from a competitive opening"), the §4.4 headline, contribution 4 and the Conclusion.
- FIX: "from a $90 opening instead of the default $97.50, none of the three seller models tested there (Sol, Luna and Gemini) raised prices (0 of 21 passed)". Make the same change in §1, the §4.4 headline, contribution 4 and the Conclusion ("none of the three seller models opened at $90 raised prices in 21 runs").
- AUTHORITY: R17. ms_runs.csv (opening_price 90.0 rows). prereg_result.md.

## F-ARG-07

- LOCATION: §5, "A low-anchor control separates the formation of collusion from its maintenance. In our runs only maintenance occurred."
- SEVERITY: medium
- ISSUE: Gemini sellers opened at $90 formed explicit coordination from hour 1 ("let's keep our asks closely aligned around $90"), and their talk was associated with prices $1.60 above the no-messaging arm. What did not form was a price above the criterion. The sentence equates collusion with a high price, although the paper treats $90 as a convention (§3.1, A.1 item 4).
- FIX: "A low-anchor control separates the formation of a high price from the maintenance of one. In our runs no high price formed, and Gemini sellers coordinated at the $90 opening."
- AUTHORITY: R7. figures_README.md, Figure 4b call-outs. A.1 item 4.

## F-ARG-08

- LOCATION: §4.3, "so the messaging comparison is partly a batch comparison."
- SEVERITY: medium
- ISSUE: The paper's own data give the size of this confound, and the text does not use them. Luna sent zero private messages in all 12 runs, yet its messaging-on runs sit 0.22 index above its messaging-off runs (−0.30 against −0.53). That gap is as large as Grok's on-off gap (0.18) and Sol's off-on gap (0.18). No frontier messaging difference exceeds the shift that appears in a model that never talked.
- FIX: Add after the sentence: "Luna's runs give the size of this confound. Luna sent no private messages in either condition, yet its messaging-on runs sit 0.22 index above its messaging-off runs (−0.30 against −0.53), as far apart as Grok's and Sol's two conditions (0.18 each)."
- AUTHORITY: Table B1. ms_runs.csv. Skeptic preemption (named principle).

## F-ARG-09

- LOCATION: §4.2, "The precedent's content mattered, and its length did not."
- SEVERITY: medium
- ISSUE: No arm varies length with content held fixed. F against F-sham holds length constant, so it can show that content matters at equal length. It cannot show that length does not matter. The two contrasts are also p = 0.008 and 0.048 before Holm correction (0.12 and 0.33 after).
- FIX: "At equal length, the precedent's content mattered."
- AUTHORITY: R7. pro_checks.md item 2 (Holm table rows 7 and 13).

## F-ARG-10

- LOCATION: §4.1, "and adding a human buyer's plea gave 7 of 20 (p = 0.016)"
- SEVERITY: medium
- ISSUE: The verification file shows that 5 of the 7 D-hsb reports came from the seat-1 seller (5 of 5 seat-1 sellers against 2 of 15 in other seats). In 4 of the 5 markets, the seat-1 seller was the only reporter (within-market permutation p = 0.012, found after the fact). The pooled plea result therefore rests partly on one seat position. The text does not mention this, and it leaves seat placement or prompt order untested as an alternative to the wording package.
- FIX: Add after the sentence: "In D-hsb, 5 of the 7 reports came from the seller in seat 1, which was the only reporter in 4 of the 5 markets, so seat position or prompt order may contribute (a pattern found after the fact)."
- AUTHORITY: pro_checks.md item 6. Skeptic preemption.

## F-ARG-11

- LOCATION: §4.1, "so the asymmetry may reflect explicitness more than who proposed."
- SEVERITY: medium
- ISSUE: Inference. A second alternative is missing. A seller who reported the peers' price talk would also report its own part in that talk (Base reaches 20 of 20 on the agreement label), while a report on seat 5 implicated only seat 5. The asymmetry may reflect self-implication rather than detection. A referee will raise this.
- FIX: "so the asymmetry may reflect explicitness more than who proposed. A report on the peers' talk would also have reported the seller's own part in it, while a report on seat 5 implicated only seat 5."
- AUTHORITY: Skeptic preemption (named principle). This is an inference, not an evidence file.

## F-ARG-12

- LOCATION: §4.4, "The positive control of §3.2 therefore measures the maintenance of a high opening price."
- SEVERITY: medium
- ISSUE: The "therefore" follows the Hantel and Struski citations, but the previous sentence says Hantel "does not explain ours causally". The real basis is M.S.'s low-anchor Gemini runs. Those ran on the Antigravity route (2 of 3 passes at $97.50), while D.E.'s pilot ran on OpenRouter (3 of 3). Extending the result to D.E.'s positive control is an inference across serving routes, and the text should say so.
- FIX: "Our low-anchor Gemini runs, served by a different route than D.E.'s pilot, suggest that the positive control of §3.2 measures the maintenance of a high opening price."
- AUTHORITY: AP-ARG-04. A.1 item 3. R7.

## F-ARG-13

- LOCATION: §4.4 headline, "A pre-specified test confirmed that Sol's passes need the high opening."
- SEVERITY: medium
- ISSUE: The test covers messaging off, Haiku buyers, one low opening and 15 hours (the prereg_result.md scope), but the headline states the result for all of Sol's passes. Seeds do not control sampling on the proxy (A.1 item 2), so a "block" pairs two runs only by label and launch time, and the pairing is nominal.
- FIX: Headline: "A pre-specified test, with messaging off and Haiku buyers, found Sol's late asks higher from $97.50 than from $90 in all six seed blocks, and Sol passed only from $97.50." In §3.3, add after "for 12 runs (Table B3).": "Seed labels do not control sampling, so a block pairs two runs by label and launch time only."
- AUTHORITY: prereg_result.md ("Scope"). A.1 item 2. R7.

## F-ARG-14

- LOCATION: §4.2, "The 0 to 3 private messages per market that remained all went to seat 5, against 108 private messages in Base and D"
- SEVERITY: low
- ISSUE: The per-market range is 0 to 4 (G-warn has 2 to 4). The values 0 to 3.0 are arm means. The 108 is a per-market mean that counts messages to seat 5, while the previous sentence's 103.4 to 104.2 excludes them. The sentence mixes the two definitions without saying so.
- FIX: "The 0 to 4 private messages per market that remained (arm means 0 to 3) all went to seat 5. Counting messages to seat 5, Base and D averaged 108 private messages per market."
- AUTHORITY: figures_README.md, Figure 2 table and the note below it.

## F-ARG-15

- LOCATION: §5, "Message volume did not predict price across models but did within Grok, so talk is not uninformative either."
- SEVERITY: low
- ISSUE: The within-Grok rho (0.93, p = 0.033) comes from one of several subgroups inspected after the fact, with n = 6 and message counts from 104 to 112 with ties. The cross-model rho is driven by which models talk at all, since all Luna markets and three of the six Sol markets sent zero messages. The Discussion drops the caveat that §4.3 gives.
- FIX: "Message volume did not predict price across models. Within Grok's six messaging markets, more talk went with higher late asks (a subgroup found after the fact), so talk may still carry information about price."
- AUTHORITY: pro_checks.md item 4. R7.
