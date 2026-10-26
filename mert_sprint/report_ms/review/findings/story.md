> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Story and signposting lens: findings on REPORT.md

Lens: story and signposting. 15 findings, most important first. Severity count: high 3, medium 7, low 5 (2 of the low ones are marked dismissible).

ESCALATE-STRUCTURE: The headline (prices stay where the market opens) is the fourth of four parallel "ways" in the abstract, the introduction, the contributions, §4 and the conclusion. In fact it is the mechanism that explains the other three. Gate 2 should decide whether §4.4 moves to lead §4, or whether §4.1 to §4.3 are reframed as consequences of it. The findings below repair the hierarchy inside the existing order.

---

## F-STORY-01
- LOCATION: Abstract, "Fourth, from a $90 competitive opening instead of the default $97.50, no seller model raised prices (0 of 21 passed)"
- SEVERITY: high
- ISSUE: The headline is the fourth of four parallel findings, and its unifying sentence ("Messaging maintained a high opening price and did not create one") comes third from the end. A judge who reads only the abstract keeps "they came apart in four ways" and a string of counts, not the claim that sells the paper. The closing "Results are directional." also undercuts the pre-specified p = 0.031 that the abstract has just given.
- FIX: Replace the abstract with the text below (247 words by whitespace split, all numbers taken from the report). It drops the GPT-4.1 clause and the "7 of whom" clause; restore them only if the word budget allows.
  "Evidence of LLM seller collusion comes from what sellers write and what prices do. In an LLM double auction with private seller messaging, prices stayed near or below where the market opened, whatever sellers wrote. The harness we use (Agrawal et al., 2025) opens seller asks around $97.50, near the $100 cartel price. Opened instead at the $90 competitive price, no seller model raised prices within 15 hours (0 of 21 runs passed our joint high-price and trade criterion), and Gemini 3.8 Flash sellers who called their coordination "completely rock solid" held $88 to $90. In a pre-specified test, GPT-5.6 Sol sellers' late asks were higher from $97.50 in all six seed blocks (mean +$6.79, p = 0.031). Messaging maintained a high opening price and did not create one. Text and price evidence came apart in three further ways. Sol sellers passed in 8 of 12 runs, 5 of 6 without messaging, while Grok 4.7 sellers passed in 0 of 12 despite over 100 private messages per messaging run. A scripted undercover seller's offer to hold asks at $96, about the going price, drew reports from 19 of 20 Gemini sellers (0 of 20 without it), while their own price talk went unreported. A one-sentence warning about undercover agents ended private messaging between sellers, and prices did not separate from a baseline that passed in 1 of 5 seeds. Evaluators should add a competitive-opening control and report text and price evidence together. The undercover results are directional."
- AUTHORITY: AP-STORY-02 (main finding stated early; major and minor findings must not get equal emphasis); R1 (the owner's sentences "Messaging maintained..." and "Evaluators should add..." are kept verbatim); R7.

## F-STORY-02
- LOCATION: §1 Introduction, "An evaluator has two kinds of evidence, what sellers wrote and what prices did. This report studies what happens when the two disagree."
- SEVERITY: high
- ISSUE: The opening paragraph states a topic, not a finding, and it cites "seller messaging raises prices [Agrawal et al., 2025]" as settled. Yet §4.4 shows that the same harness opens asks near $97.50. That provenance fact gives the paper its stakes (the field's positive control may measure maintenance, not formation), and it never reaches the introduction.
- FIX: Replace the sentence "This report studies what happens when the two disagree." with: "The harness behind the second result opens seller asks around $97.50, near the $100 cartel price, so its positive control may measure whether sellers keep a high price rather than whether they create one. We find that prices stay near or below where the market opens. From a $90 competitive opening no seller model raised prices, with or without messaging, and a pre-specified test confirmed that GPT-5.6 Sol's passes need the high opening (§4.4). Text and price evidence can therefore disagree, and §4 measures four ways in which they did."
- AUTHORITY: AP-STORY-02 (main finding in the opening of the introduction); AP-STORY-03 (stakes and gap); evidence: provenance.md and §4.4 ("their reported collusion also descends from a high opening price").

## F-STORY-03
- LOCATION: §1 Introduction, "on Q3.2 (a scripted agent offers each agent a pact) and Q3.4 (what a coalition does when it learns it is watched)"
- SEVERITY: high
- ISSUE: The gloss of Q3.2 describes the design, not the track question ("Can we disrupt collusion through introducing trusted agents?"). Neither track question is then answered by name in the introduction. Q3.4 is answered only in the last sentence of §5 "How to break it up", in negative form, and Q3.2 is never answered by name. Judges score the entry against these two questions.
- FIX: Replace the quoted clause with: "on Q3.2 ("Can we disrupt collusion through introducing trusted agents?"), which we test with a scripted undercover seller that offers each seller a pact, and Q3.4 ("What does a coalition do when it learns it is being watched?"), which we test with a one-sentence warning". Then replace the third bullet ("How can it be broken up?") with two bullets: "- **Q3.2, trusted agents.** An undercover offer drew reports from the sellers who received it, including sellers who also signaled agreement, and did not reach the sellers' own price talk (§4.1)." and "- **Q3.4, a coalition that learns it is watched.** Sellers warned of undercover agents stopped messaging each other, and their prices did not separate from a baseline that rarely passed (§4.2)."
- AUTHORITY: CONTEXT.md (track questions, verbatim); AP-STORY-01 (stated focus); R10 (the reader's thread runs from the question to its answer).

## F-STORY-04
- LOCATION: §5 Discussion, "A low-anchor control separates the formation of collusion from its maintenance. In our runs only maintenance occurred."
- SEVERITY: medium
- ISSUE: The headline has no paragraph of its own in the Discussion. It is filed as two sentences under "How to break it up", although it answers the first sprint question ("When do agents start colluding?"), and §1's first bullet promises that answer. The first recommendation then has no discussion paragraph behind it.
- FIX: Cut the two quoted sentences from "How to break it up" and open §5 with a new paragraph: "**When collusion starts.** In these markets no seller model formed high prices from a competitive opening within 15 hours, and messaging kept a high opening price without creating one. The harness of Agrawal et al. [2025] opens asks around $97.50, so a pass in it, ours included, can reflect a kept opening price. This is the reason for the first recommendation below."
- AUTHORITY: narrative.md (the discussion interprets the main finding first); AP-STORY-02 (major and minor findings at unequal emphasis); R5 (the result is stated once, in its place).

## F-STORY-05
- LOCATION: §6 Conclusion, "In one LLM double auction, the evidence of collusion in logs and in prices came apart in four ways."
- SEVERITY: medium
- ISSUE: The conclusion restates the abstract's four findings in the same order and in the past tense. It never says how they connect, and it omits the recommendation, so the paper ends on a list of next tests instead of on its claim.
- FIX: Replace everything before "The next tests are" with: "In one LLM double auction, prices stayed near or below where the market opened, whatever the sellers wrote. Opened at the competitive price, no seller model raised prices in 21 runs, Gemini sellers held an openly coordinated price at the benchmark, and a pre-specified test found Sol's late asks $6.79 higher from the default opening in all six seed blocks. Messaging kept a high opening price and did not create one. Text and price evidence therefore came apart. GPT-5.6 Sol sellers passed most often without messaging, Grok 4.7 sellers never passed despite open floor proposals, an undercover offer drew reports for its own proposal and none for the sellers' talk, and a warning silenced talk without a detectable price change. Evaluators should add a competitive-opening control and report text and price evidence for every market." Keep the final "The next tests are ..." sentence unchanged.
- AUTHORITY: academic-communication narrative.md (a conclusion synthesizes and does not repeat the abstract); R5 (the conclusion states the main results for its own purpose); R1.

## F-STORY-06
- LOCATION: §4.4, "The positive control of §3.2 therefore measures the maintenance of a high opening price. It does not show collusion forming from a competitive start."
- SEVERITY: medium
- ISSUE: The headline section ends on a related-work paragraph and then a negative sentence. The paragraph before it also closes on two "does not" clauses ("It does not show what Sol would do ... and it does not decide whether the passes at $97.50 are collusion"), although A.1 items 4 and 6 already state these limits. The section that should land the headline ends on what it is not.
- FIX: Move the paragraph "Other LLM double auctions are also sensitive to their opening ..." up so that it directly follows the first paragraph of §4.4, which already discusses the harness opening. Cut the sentence "It does not show what Sol would do over a longer horizon or from another opening, and it does not decide whether the passes at $97.50 are collusion." End §4.4 with: "Across all 21 runs opened at $90, none passed. The positive control of §3.2 therefore measures whether sellers keep a high opening price." Cut "It does not show collusion forming from a competitive start."
- AUTHORITY: R3 (end a result on the result); R8 (cut sentences that only say what a result does not establish); R9 (a limitation is stated once).

## F-STORY-07
- LOCATION: §3.2, "under which Gemini sellers in a 4+4 market passed in 3 of 3 seeds with messaging and 0 of 3 without"
- SEVERITY: medium
- ISSUE: The term "positive control" is used only in §4.4 ("The positive control of §3.2") and is never defined. The control appears in §3.2 as a subordinate clause about buyer choice. §3.1 also gives "The harness seeds seller asks near $97.50" as a flat detail, so nothing prepares the reader for the fact that §4.4 turns on it.
- FIX: In §3.2, replace "and five GPT-4.1-mini buyers, under which Gemini sellers in a 4+4 market passed in 3 of 3 seeds with messaging and 0 of 3 without." with "and five GPT-4.1-mini buyers. The buyers were chosen with a 4+4 positive control, a market built to show that the criterion detects coordination when sellers can message, in which Gemini sellers passed in 3 of 3 seeds with messaging and 0 of 3 without." In §3.1, after "The harness seeds seller asks near $97.50 and buyer bids near $82.50." add "The seeded ask is close to the $100 cartel price, and §4.4 tests this choice."
- AUTHORITY: R12 (say what a control is for before its result); R17 (name exactly what a statement refers to).

## F-STORY-08
- LOCATION: §4.3, "Four Gemini markets that passed with open messaging scored 3.47 to 3.83, although seller model and messaging both differ between the two groups."
- SEVERITY: medium
- ISSUE: §4.3 ends on a confounded judge-score comparison. The sentence that leads into §4.4 ("Sol's mean hour-1 ask was $96.7, close to the seeded $97.50, while Luna and Grok asked about $90") is buried at the start of the last paragraph. The reader reaches §4.4 without being told why the opening is the next question.
- FIX: Move the two sentences "The split appears in the first hour (Figure 4a). Sol's mean hour-1 ask was $96.7, close to the seeded $97.50, while Luna and Grok asked about $90." to the end of §4.3 and follow them with: "Sol's sellers stayed near the price at which the market opened, and §4.4 moves that opening."
- AUTHORITY: narrative.md (each section ends pointing at the next); R11 (connect a result to the related result elsewhere).

## F-STORY-09
- LOCATION: §1 contributions, "A low-anchor control and a pre-specified paired test, in which no seller model formed high prices from a competitive start"
- SEVERITY: medium
- ISSUE: The introduction lists the results three times in three orders: the bullets (§4.4, §4.3, §4.1 and §4.2), the "We add ..." paragraph and the contributions (§4.1 to §4.4). The "We add" sentence is repeated again at the end of §2. In the contributions the headline comes last, and items 1, 2 and 4 are phrased as designs rather than as findings.
- FIX: Cut the sentence "We add warning-only and sham-precedent controls and a competitive-opening control, and we measure reports, messages and prices separately in the same markets." from §1, because §2 closes on the same point. Rewrite the contributions as findings, headline first: "1. A low-anchor control and a pre-specified paired test, which show that no seller model formed high prices from a competitive start and that Sol's passes need the high opening (M.S.). 2. Frontier sellers in one market, where talk and price point in opposite directions for GPT-5.6 Sol and Grok 4.7 (M.S.). 3. An undercover seller with a report action and a matched placebo seat, which drew reports from Gemini sellers and support from GPT-4.1 sellers and did not reach the sellers' own talk (D.E.). 4. Warning, precedent and sham-precedent arms, which separate deterrence by belief from deterrence by presence and a precedent's content from its length (D.E.)." If the authors want D.E.'s items first, keep the order and keep only the rephrasing as findings.
- AUTHORITY: R5 (each result once; orientation text in its place); AP-STORY-01 (ranked, not unranked, questions and contributions).

## F-STORY-10
- LOCATION: §4 Results, "Table 2 sets what sellers wrote next to what their prices did, in the order of the subsections below."
- SEVERITY: medium
- ISSUE: The results section opens straight into a table. It does not recall the questions of §1 or say which data each subsection uses. The reader cannot see that §4.1 and §4.2 use D.E.'s 5+5 market and that §4.3 and §4.4 use M.S.'s 4+4 market.
- FIX: Insert before the quoted sentence: "Section 1 asked when sellers start colluding, what counts as evidence in their logs and how coordination can be broken up. Sections 4.1 and 4.2 answer with D.E.'s 5+5 undercover markets, and §4.3 and §4.4 answer with M.S.'s 4+4 frontier and low-anchor markets."
- AUTHORITY: R10 (open a results section by recalling the question and naming the data, without previewing the answers).

## F-STORY-11
- LOCATION: §3 Setup, "We use the continuous double auction of Agrawal et al. [2025] as vendored for the sprint."
- SEVERITY: low
- ISSUE: §3 opens without saying that the study has two markets run by two authors and how they map to the results. The reader learns this only from the "(D.E.)" and "(M.S.)" tags in the subsection headings.
- FIX: Insert at the start of §3, before §3.1: "The study uses two versions of one market. D.E.'s 5+5 undercover market (§3.2) gives the results of §4.1 and §4.2, and M.S.'s 4+4 frontier and low-anchor market (§3.3) gives those of §4.3 and §4.4. Both use the market and criterion of §3.1."
- AUTHORITY: narrative.md (why before what; triangle opening per section); R10.

## F-STORY-12
- LOCATION: §4.2, "The warning did not silence GPT-4.1 sellers, whose E markets kept 57 to 68 private messages between sellers per run."
- SEVERITY: low
- ISSUE: §4.2 ends on a GPT-4.1 aside that belongs with the warning's effect on talk in the first paragraph. The section therefore closes without a bridge to §4.3, whose question is the reverse case: price without talk.
- FIX: Move the quoted sentence to directly follow "(3 private messages per market in G-warn, 1 in E)." End §4.2 with: "Under the warning, Gemini talk stopped and prices did not separate from Base. Section 4.3 turns to the reverse case, sellers whose prices stayed high with no talk."
- AUTHORITY: R13 (keep a sentence with the paragraph whose idea it continues); narrative.md (each section ends pointing at the next).

## F-STORY-13
- LOCATION: Table 2, "Gemini 3.8 Flash, Seller Max, `agy_gemini_comms_gpt41miniB-seed0` (opened at $97.50), hour 14, private plan and public message"
- SEVERITY: low
- ISSUE: The caption says the rows follow "the order of §4.1 to §4.4". Row 2, however, comes from the default-opening Gemini control of §4.4. The text never cites rows 2 and 4, so two of the seven quotes are not signposted from the argument.
- FIX: Move the Seller Max row to sit directly above the `L90_gemini_comms_gpt41miniB-seed0` Kai row. In §4.4, after "passed 2 of 3 from the default $97.50 opening (ask index 0.50 and 0.53) with 110 to 118 private messages", add "(the failing seed is Table 2, row 5)". In §4.3, after "proposed floors in public", add "(Table 2, row 3)". Renumber the existing citations: the prohibition notice becomes row 2 and Sol becomes row 4. Rows 6 and 7 are unchanged.
- AUTHORITY: R17 (exact reference); R11 (link each quoted result to its place in the argument).

## F-STORY-14 (dismissible)
- LOCATION: Title, "Talk Is Not Price: Undercover Offers, Warnings and Opening Prices in an LLM Double Auction"
- SEVERITY: low
- ISSUE: The subtitle lists opening prices last, in the same flat order as the abstract. "Talk Is Not Price" carries the headline well, because talk did not set the price. Dismissible if F-STORY-01 and F-STORY-02 are adopted, since the abstract and introduction would then carry the hierarchy.
- FIX: Optional: "Talk Is Not Price: Opening Prices, Undercover Offers and Warnings in an LLM Double Auction".
- AUTHORITY: OPINION (AP-STORY-02 applied to the title).

## F-STORY-15 (dismissible)
- LOCATION: §5 Discussion, "In these markets, text evidence flagged Grok 4.7 sellers and the Gemini markets opened at $90"
- SEVERITY: low
- ISSUE: The run-in labels "What counts as evidence." and "How to break it up." name topics, not takeaways. They do mirror the sprint questions, which helps signposting, so this is dismissible.
- FIX: Optional: "**Text and price flag different markets.**" and "**Offers draw reports, and warnings draw silence.**"
- AUTHORITY: OPINION (narrative.md takeaway-bearing headings).
