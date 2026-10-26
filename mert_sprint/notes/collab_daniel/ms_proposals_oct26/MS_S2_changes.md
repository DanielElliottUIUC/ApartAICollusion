# S2: proposed changes to Report v2 (1f951ac)

Proposed by M.S. for D.E. to accept or decline. The patch MS_S2.diff applies with git apply to report/REPORT.md at 1f951ac. Mert's ruling on each change is recorded on the desk page.

## C92 (line 14, paragraph)

The abstract set up only the offer, although half its results concern the warning. The purpose now names both countermeasures, so the warning result reads as the answer to the second. Semicolon chains are split into sentences.

Before:

> Autonomous LLM sellers can coordinate on prices; one proposed countermeasure is a trusted agent that invites collusion and reports whoever accepts. We test it in an LLM double auction with private messaging and a neutral report action, where a scripted seller privately offers every seller a $96 price floor, about the going price; other arms add human pleas, a warning that undercover agents may be present, or a precedent of punished sellers. Gemini 3.8 Flash sellers almost all reported the offer (19 of 20), yet 7 also wrote back agreeing, 6 stating an aim to keep the proposer anchored, and none of the 20 reported a peer's price talk. GPT-4.1 sellers backed the offer in words and, at $96, reported it only under a precedent describing the scenario; Claude Haiku 5.5 sellers, asking about $10 below the offer, refused it openly. Under the one-sentence warning, Gemini sellers in the undercover market never messaged each other privately, while prices stayed inside the baseline's range. Price evidence is weak by construction. The baseline met the joint high-price and trade criterion in 1 of 5 seeds, and prices held or fell from the opening ask. With three to five seeds per arm, results are directional. The undercover offer exposed double-dealing but rarely drew reports of the sellers' own price talk, and silence under a warning is not evidence of deterrence.

After:

> Autonomous LLM sellers can coordinate on prices. Proposed countermeasures are a trusted agent that invites collusion and reports whoever accepts, and a cheaper warning that such agents may be present. We test both in an LLM double auction with private messaging and a neutral report action, where a scripted seller privately offers every seller a price floor near the going price. Variants add human pleas, the warning or a precedent of punished sellers. Gemini 3.8 Flash sellers almost all reported the offer (19 of 20), yet 7 also wrote back agreeing, 6 stating an aim to keep the proposer anchored, and the sellers' price talk went unreported. GPT-4.1 sellers backed the offer in words and reported it only under a precedent describing the scenario. Claude Haiku 5.5 sellers refused it openly. Under the warning, Gemini sellers in the undercover market never messaged each other privately, while prices stayed inside the baseline's range. Price evidence is weak by construction, because the baseline met our joint criterion in one of five seeds and prices kept the opening ask. With three to five seeds per arm, results are directional. A honeypot exposed double-dealing but missed the sellers' own price talk, and silence under a warning is not evidence of deterrence.

## C93 (line 22, caption)

The first sentence now says what the figure shows, and the semicolon join becomes two sentences. The regulator clause goes because the figure's own box says "no effect in the run" and Section 3.2 says the report action has no consequence. The credit "(Figure: M.S.)" goes because Code and Data and Author Contributions already credit the design, and the body speaks as "we".

Before:

> Figure 1. The undercover market. Four LLM sellers, a scripted fifth seller (seat 5) and five LLM buyers trade for 15 hours; seat 5's hour-3 message and the prompt notice vary by arm (Figure 2), and reports go to a regulator with no effect in the run.

After:

> Figure 1. The undercover market, in which four LLM sellers, scripted seat 5 and five LLM buyers trade for 15 hours. Seat 5's hour-3 message and the prompt notice vary by arm (Figure 2).

## C94 (line 34, paragraph)

The criterion was given without its purpose, so the paragraph now says why it also requires trades ("fixed in advance" replaces "fixed before the undercover runs" for length, and README line 67 shows it was fixed before any run). The index caveat becomes a relative clause instead of a parenthesis with its own semicolon, and the positive control's counts move to Table D5.

Before:

> In the continuous double auction of Agrawal et al. [2025] (Appendix B), seller cost is $80 and buyer value $100, so every price from $80 to $100 clears; the ask index runs from 0 at the harness's $90 competitive price to 1 at the $100 cartel price. The $90 zero is a midpoint convention: a price-taking benchmark for the undercover market is $96 or above (Appendix D.9). Asks open near $97.50. Sellers post one public and up to two private messages an hour, seen the next hour, at temperature 0.7. Buyers are GPT-4.1-mini agents unless stated otherwise, because the harness's own rule-based buyer always bids about $80 (Appendix D.8). A market passes the joint criterion, fixed before the undercover runs, when over hours 11 to 15 the ask index exceeds 0.5, the trade-price index exceeds 0.25 and at least one trade clears per hour on average; in the 4+4 positive control (four sellers, four buyers) messaging met it in 3 of 3 seeds, no messaging in 0 of 3.

After:

> In the continuous double auction of Agrawal et al. [2025] (Appendix B), seller cost is $80 and buyer value $100, so every price from $80 to $100 clears. The ask index runs from 0 at the harness's $90 competitive price, a midpoint convention that is only the index's zero in the undercover market (Appendix D.9), to 1 at the $100 cartel price. Asks open near $97.50. Sellers (temperature 0.7) post one public and up to two private messages an hour, seen the next hour. Buyers are GPT-4.1-mini agents unless stated otherwise, because the harness's own rule-based buyer always bids about $80 (Appendix D.8). Because high asks alone need not mean collusion, a market passes the joint criterion, fixed in advance, when over hours 11 to 15 the ask index exceeds 0.5, the trade-price index 0.25 and at least one trade clears per hour on average. The 4+4 positive control (four sellers, four buyers) passed with messaging and failed without (Table D5).

## C95 (line 38, caption)

The list of bare items hung off a colon becomes a statement of the layout, so the reader knows what rows and columns hold. Buyers, hours, messaging, the report action and the absent prohibition notice are given in Sections 3.1 and 3.2. Dropping "prohibition notice" also removes the clash with the column header "No notice". "Base-hb was planned but not run" goes because the figure's dashed cell says "Base-hb not run".

Before:

> Figure 2. The ten arms of the undercover market. Every arm has four Gemini 3.8 Flash sellers and scripted seat 5, five GPT-4.1-mini buyers, 15 hours, messaging on, the report action, no prohibition notice, seeds 0 to 4 (10 arms × 5 seeds = 50 markets). The prompt notice is in every seller's prompt from hour 1; Base-hb was planned but not run.

After:

> Figure 2. The ten arms of the undercover market, by seat 5's hour-3 message (rows) and by the prompt notice from hour 1 and buyer 5's message (columns). Each arm used Gemini 3.8 Flash sellers and seeds 0 to 4 (50 markets).

## C96 (line 40, paragraph)

Seat 5's replayed path and its $96 hold were stated without their reasons. The paragraph now gives both, which is what makes the offer-plus-price caveat in the results readable, and the colon list of arms becomes a relative clause.

Before:

> In the undercover market (Figure 1), four LLM sellers trade with five buyers and a scripted fifth seller, seat 5, which replays a pilot seller's asks. At hour 3 it privately sends every seller a neutral note or the $96 offer, at about the going price (arm-mean hour-3 asks $95.35 to $96.63); in offer arms its ask then stays at $96, so offer arms differ from the placebo in message and visible price (Figure D1). Every arm has the report action, costless and without consequence, and no prohibition notice (a prompt statement that coordinating prices is prohibited; Appendix C), since pilot markets did not collude under it (Appendix D.8). Figure 2 lays out the ten arms. Base gets the placebo note and D the plain offer, and the texts are in Appendix C.

After:

> In the undercover market (Figure 1), four LLM sellers trade with five buyers and a scripted fifth seller, seat 5, which replays a pilot seller's asks to pass as a peer. At hour 3 it privately sends every seller a neutral note or the $96 offer, near the going price (Figure D1). In offer arms its ask holds at $96 to match its words, so these arms differ from the placebo in message and visible price. Every arm has the report action, costless and without consequence, and no prohibition notice, since collusion did not survive the notice in pilots (Appendix D.8). Figure 2 lays out the ten arms, where Base gets the placebo note and D the plain offer (texts in Appendix C).

## C97 (line 56, caption)

The verbless first sentence becomes the figure's result. The layout note "(columns: seeds; rows: seats)" goes because the figure labels every column "Seed n" and every row "Seat n". The reply counts (8 supportive, 1 refusing) go because the legend keys the dots and Appendix D.1 gives the counts. The semicolon join becomes "and".

Before:

> Figure 3. Every Gemini seller in arm D (columns: seeds; rows: seats) and in Base. Nine D sellers wrote back (7 agreeing to $96, 2 declining it); the 7 outlined ones also reported seat 5 and asked below $96.

After:

> Figure 3. Nineteen of 20 Gemini sellers in arm D reported seat 5, and none in Base did. All 19 first reported in hour 4, the first hour the offer was visible, and the 7 outlined ones also wrote back agreeing while asking below $96.

## C98 (line 80, paragraph)

The paragraph now says why the price null is uninformative and why the 4+4 market is the informative test, and it ends on what this means for reading deterrence from text.

Before:

> Warning-arm ask indices were 0.37 to 0.48 against 0.41 in Base, inside Base's seed range (Figure 5b; p = 0.90, 0.52 and 0.75 for E, G-warn and G-prec), an uninformative null, not evidence that collusion went tacit. In the 4+4 market, where messaging holds a high opening, the warning kept 2 of 3 passes (3 against 3 seeds; Appendix D.3).

After:

> Warning-arm mean ask indices stayed inside Base's seed range (Figure 5b; p = 0.90, 0.52 and 0.75 for E, G-warn and G-prec). Because Base is not a demonstrated price cartel, this is an uninformative null, not evidence that collusion went tacit. In the 4+4 positive control, where messaging holds a high opening, the warning kept 2 of 3 passes (Appendix D.3). Deterrence read from messages or judge labels would thus overstate what the warning did to prices.

## C99 (line 88, paragraph)

The paragraph held two ideas, the criterion and the lessons for AI control, so it becomes two. "Talk and price diverged" becomes "talk and the criterion diverged", the agreed framing in the STATUS note, because talk did set prices in the Grok and $90-opening markets (Figure D5). This wording correction is for the owner to rule on.

Before:

> Talk and the joint criterion diverged throughout (Figure D5). The criterion has no ground truth (a stable cartel below $90 fails it; a pass can be a seeded price that no one enforces), and only a paired deviation test from a saved state [Tran and Yu, 2026], which we did not run, could tell these apart. For AI control, the honeypot caught the stranger but rarely the sellers' own talk (7 sellers in 5 of 50 Gemini markets reported a peer), as Adlakha and Adlakha [2026] also saw, and a warning that empties the private channel looks like deterrence to a text monitor. Reports cost nothing and sanctions were only described, so nothing here validates undercover offers or warnings as deployed controls; tests should open markets at the competitive price and fix the undercover seller's price path (Appendix A).

After:

> Talk and the criterion diverged throughout. The criterion has no ground truth, because a stable cartel below $90 fails it and a pass can be patience at a seeded price. Only a deviation test from a saved market state [Tran and Yu, 2026], which we did not run, could separate the two.
> 
> For AI control, the honeypot caught the stranger but missed the sellers' own talk, as Adlakha and Adlakha [2026] also saw. A warning that empties the private channel looks like deterrence to a text monitor. Reports cost nothing and sanctions were only described, so nothing here validates undercover offers or warnings as deployed controls (Appendix A). Tests should open markets at the competitive price and fix the undercover seller's price path.

## C100 (line 92, paragraph)

The semicolon chain is split and the 7 are named as reporters (the STATUS correction). "Without moving prices" becomes the measured fact the body states, prices in Base's range, because the STATUS note calls the price null uninformative.

Before:

> Undercover offers drew reports from Gemini 3.8 Flash sellers, 7 of 20 of whom also wrote back agreeing, written agreement from GPT-4.1 sellers and open refusals from Claude Haiku 5.5 sellers. A one-sentence warning kept Gemini sellers in the undercover market from messaging each other privately, without a detectable price change in a market whose baseline rarely met our criterion. Next are a baseline that demonstrably colludes on price, a generic precedent, AI-persona pleas, an undercover agent that replies, and deviation tests.

After:

> Undercover offers drew reports from Gemini 3.8 Flash sellers, written agreement from GPT-4.1 sellers and open refusals from Claude Haiku 5.5 sellers. Seven Gemini reporters also wrote back agreeing, and no seller reported peers' price talk. A one-sentence warning kept Gemini sellers in the undercover market from messaging each other privately, with prices in Base's range. Next are a baseline that demonstrably colludes on price, a generic precedent, AI-persona pleas, an undercover agent that replies, and deviation tests.
