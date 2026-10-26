> **INTERIM DRAFT, Oct 26 ~12:50 AM CT.** Not fact checked, numbers may change. Daniel's PR #45 report-v2 is still the single final report. Checked versions will follow.

# Reader simulation: blind read of full.pdf (22 pages)

Reader: an AI-safety researcher judging a hackathon submission. Source read: `review/snapshot/full.pdf` only.

## 1. The one idea

In an LLM double auction, what sellers write and what prices do are separate kinds of collusion evidence that disagree, and most of the high prices in the standard setup come from sellers keeping the seeded $97.50 opening, not from a cartel forming.

## 2. What each figure shows

- **Figure 1 (p8).** Panel (a) shows that the undercover $96 offer drew reports from nearly every Gemini seller in each offer arm (0 without an offer, 7 to 12 of 20 under the human-plea wordings). Panel (b) shows that the same plain offer drew reports from 19 of 20 Gemini sellers, 0 of 12 GPT-4.1 sellers and 3 of 12 Haiku sellers.
- **Figure 2 (p9).** The one-sentence warning took private seller-to-seller messages from about 104 per market to 0 in every warning arm, while the last-third ask indices of the warning arms stay inside Base's seed range.
- **Figure 3 (p11).** It plots private messages against the last-third ask index for every market. Silent Sol markets sit high, talkative Grok markets sit low, warning-arm markets sit at zero talk inside Base's range, and talkative Gemini markets opened at $90 sit near index 0.
- **Figure 4 (p13).** Panel (a) shows that at the $97.50 opening Sol's asks stay near $95 to $96, while Grok and Luna fall to $85 to $87 in the first two hours. Panel (b) shows that every model opened at $90 stays at or below $90, and that messaging only keeps Gemini from falling to about $87. Panel (c) shows the pre-specified test, in which Sol's late asks are higher from $97.50 in all six seed blocks (+$6.79, p = 0.031).

## 3. Where I was confused or had to reread

1. **p1, abstract.** About twenty numbers cover four loosely related findings. "7 of whom also signalled agreement by our reading" leaves unclear whether the 7 are among the 19 reporters and whose reading counts. "0 of 21 passed" uses a denominator the abstract never defines. GPT-4.1 sellers appear, although the framing is about frontier models.
2. **p3, §3.1.** I had to reread to see why $90 is "competitive" when every price from $80 to $100 clears. That it is only a midpoint convention becomes explicit only on p14 and p18.
3. **p4, §3.2.** In "under which Gemini sellers in a 4+4 market passed in 3 of 3 seeds", the antecedent of "under which" is unclear. The switch between the 5+5 undercover market and the 4+4 frontier market is easy to miss, and so is the Table 1 caption's "extra GPT-4.1-mini buyer".
4. **p7, p9 and Figure 2a.** The message counts disagree on the surface. The text gives 104 per market on p7 and "108 private messages in Base and D" on p9, and Figure 2a gives 103.6. I could not tell whether 108 includes messages to seat 5.
5. **p8, Figure 1.** The "Agreed with a peer" bars are not specific to the offer (Base 20 of 20, warning arms 0), so it is unclear what they add. The 7 of 20 feigned agreements that the abstract leads with are not plotted and cannot be rebuilt from the released tables. Panel (b) gives Haiku "Rejected 12 of 12", while the text on p7 says 11 of 12.
6. **p10, §4.2.** The warning's price result is called "uninformative", yet it is the second of the four headline findings in the abstract and the conclusion.
7. **p11, Figure 3.** The plot uses a split x-axis, zero-message columns whose position "carries no value", rings for runs opened at $90 and a grey band taken from another market. One pink Grok marker sits inside the legend block and reads as a legend entry. The legend says "Daniel's" and "our", while the text says D.E. and M.S.
8. **p12, §4.4.** "Committed 37 s before the 12 runs started" is an odd detail to stress. The test also repeats a contrast already in Table B2 (Sol 0 of 6 from $90), so it confirms a known pattern rather than testing a new one.
9. **p14.** For "The positive control of §3.2", I had to search back to find that it is the 4+4 Gemini result mentioned in a single clause on p4.
10. **p5 to p7, Table 2.** Its seven rows come from four subsections and six markets. Row 2, the Gemini double-dealing control, belongs to §4.4 but comes second. The two dagger quotes cannot be checked.
11. **Throughout.** The (D.E.) and (M.S.) tags make the reader track two teams, two judges, two serving routes and two market sizes.

## 4. Three strongest objections

1. **"Talk is not price" depends partly on how the benchmark is set.** With costs of $80 and values of $100, any price clears, and $90 is a midpoint convention. Grok's four sellers posted "keep asks at or above 86.47" and then all asked exactly $86.47, or held $87.99 in lockstep. That is coordination on a price above cost, and the criterion scores it as a failure only because the line sits at $90. The headline split between Grok and Sol therefore measures how the surplus is divided relative to an arbitrary line, not whether coordination happened.
2. **The undercover and warning results rest on a weak base.** Base passed in only 1 of 5 seeds and has no no-messaging control. The D against Base contrast also changes seat 5's price path. The offer sat at the going price, so agreeing cost nothing. No contrast survives Holm correction, sellers within a market are not independent, and the authors call the warning's price null uninformative. The robust finding is narrower than the framing suggests. An explicitly worded offer gets reported, and a warning stops messaging.
3. **Sol's "collusion without talk" is not separated from patience or anchoring.** The pre-specified test shows that Sol's passes depend on the seeded opening. Without a deviation and punishment test (the paper names one and did not run it), a Sol pass may be slow price descent over 15 hours. Further confounds sit on top of this. The runs had no temperature or seed control, the messaging-off runs were a later batch on another machine, and Figure 3 pools two serving routes, two market sizes and two judges.

## 5. The abstract in 60 words

In an LLM double auction, text and price evidence of collusion diverged. An undercover offer drew reports from 19 of 20 Gemini sellers but missed their own price talk. A warning silenced messaging without detectable price change. Talkative Grok priced low; silent GPT-5.6 Sol priced high. From a $90 opening no model raised prices, so high prices reflected kept openings.

## Scores (1 to 5)

- **Novelty: 3.** Three concurrent sprint entries also test undercover offers, and anchoring in LLM markets is known. The competitive-opening control, which shows that the standard testbed measures whether sellers keep a high opening price rather than whether they form a cartel, is the new and useful contribution.
- **Execution: 4.** For a sprint, the work is careful. It has exact tests, a Holm accounting, a pre-specified paired test, verbatim checks of the quotes, run-folder provenance and a long list of limitations. The seed counts are small, the base is weak and several confounds remain.
- **Clarity: 3.** The prose is precise and honest about its limits. The abstract carries too many numbers, the four findings read as separate studies, and the reader must track arm codes, two market sizes and authorship tags, with Figure 3 needing two readings.
