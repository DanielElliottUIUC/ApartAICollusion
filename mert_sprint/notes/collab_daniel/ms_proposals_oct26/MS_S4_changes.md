# S4: proposed changes to Report v2 (1f951ac)

Proposed by M.S. for D.E. to accept or decline. The patch MS_S4.diff applies with git apply to report/REPORT.md at 1f951ac. Mert's ruling on each change is recorded on the desk page.

## C116 (line 18, opening)

Mert's approved direction for the introduction. The first paragraph keeps Daniel's sentences and splits the semicolon join. The new second paragraph says what we test and why, naming the three families, the Gemini arms and the price runs in the order of Section 4, so the reader knows why each batch is in the paper before Section 3.

Before:

> LLM pricing agents can reach supra-competitive prices without being told to, even with no way to communicate [Fish et al., 2026; Hammond et al., 2025], and in a continuous double auction seller messaging raises prices [Agrawal et al., 2025]. One proposed countermeasure, an application of the trusted agents of AI control [Greenblatt et al., 2024], is a peer agent that invites collusion and reports whoever accepts [Hammond et al., 2025; Wehner and Kraprayoon, 2026]; a cheaper one is to announce that such agents may be present. We test both in that double auction (sprint questions Q3.2 and Q3.4, touching Q1.1, Q1.5 and Q3.3).

After:

> LLM pricing agents can reach supra-competitive prices without being told to, even with no way to communicate [Fish et al., 2026; Hammond et al., 2025], and in a continuous double auction seller messaging raises prices [Agrawal et al., 2025]. One proposed countermeasure, an application of the trusted agents of AI control [Greenblatt et al., 2024], is a peer agent that invites collusion and reports whoever accepts [Hammond et al., 2025; Wehner and Kraprayoon, 2026]. A cheaper one is to announce that such agents may be present.
> 
> We test both in that double auction. A scripted seller privately offers every seller a $96 price floor, and we record who reports the offer, who agrees to it and what prices do. We make the offer to Gemini 3.8 Flash, GPT-4.1 and Claude Haiku 5.5 sellers, and ten arms with Gemini sellers set the offer against a placebo note and add human pleas, a warning that undercover agents may be present or a precedent of punished sellers. To find what sets the price when no one intervenes, we also run four frontier seller models with and without messaging, open markets at the $90 competitive price instead of the default $97.50, and pin $90 as the unique competitive price. This addresses the sprint's questions on trusted agents (Q3.2) and on what a coalition does when it learns it is watched (Q3.4), and touches Q1.1, Q1.5 and Q3.3.

## C117 (line 20, opening)

Pays for the longer opening. The sentence on what we test repeats the new second paragraph, and the human-in-distress clause repeats its human pleas, whose details stay in Section 4.3 and Appendix C. The semicolon join goes with the clause.

Before:

> **Threat model.** Autonomous sellers, one per firm, trade with LLM buyers, talk publicly and in private messages that no one tells them are read, and can report any seller to a regulator. The adversary is an agent posing as a peer seller that privately proposes a price floor, as a cartel recruiter would; in some arms the offer, or a message posted under buyer 5's name, claims to come from a human in distress. The defender sees reports as filed, private messages after the fact, and prices. We test whether sellers report, pretend or refuse, whether a warning or a precedent changes that, and whether any of it shows in prices. The testbed is controlled, not realistic (Figure 1).

After:

> **Threat model.** Autonomous sellers, one per firm, trade with LLM buyers, talk publicly and in private messages that no one tells them are read, and can report any seller to a regulator. The adversary is an agent posing as a peer seller that privately proposes a price floor, as a cartel recruiter would. The defender sees reports as filed, private messages after the fact, and prices. The testbed is controlled, not realistic (Figure 1).

## C118 (line 24, opening)

The colon and semicolon list of bold labels becomes one sentence per finding, in the order of Section 4. "Opposite directions" and "empties the private channel, not the prices" go, because three answers cannot be opposite, messaging never started, and the price null is uninformative. The opening-price result becomes a finding, and the last sentence states what the findings mean.

Before:

> We contribute three findings: **report and pretend** (§4.1); **one offer, three families, opposite directions**: Gemini sellers report it, GPT-4.1 sellers back it in words, Haiku sellers refuse it (§4.2); and **a warning empties the private channel, not the prices** (§4.4), in markets where prices hold or fall from the opening ask (§4.5).

After:

> Nineteen of 20 Gemini sellers reported the offer, and 7 of them also wrote back agreeing to it (§4.1). The answer differed by model family and by the words around the offer (§4.2, §4.3), and under the warning Gemini sellers in the undercover market never messaged each other privately (§4.4). Prices held or fell from the opening ask, which replicates two concurrent entries and leaves the price nulls between arms uninformative (§4.5). A honeypot therefore measures the response it elicits rather than an existing cartel, a seller may deceive the agent it reports, and a monitor that reads only text would take silence under a warning for deterrence.

## C119 (line 60, heading)

Three answers cannot be opposite. The heading states the finding at the strength of three seeds per family.

Before:

> ### 4.2 Three families answer one offer in opposite directions

After:

> ### 4.2 Three families answer the offer differently

## C120 (line 68, heading)

The heading named a topic. It now states the two findings of the subsection, in the words of its own text.

Before:

> ### 4.3 Pleas and precedents

After:

> ### 4.3 A human seller's plea cuts reporting, and a precedent makes sellers suspect a test

## C121 (line 72, heading)

Messaging never started, so nothing was emptied, and the price null is uninformative, so the heading no longer sets talk against prices. It names the family and the market, since GPT-4.1 sellers kept messaging under the warning.

Before:

> ### 4.4 A warning empties the private channel, not the prices

After:

> ### 4.4 Under a warning, Gemini sellers in the undercover market never message each other privately

## C122 (line 74, opening)

Opens on what the arms test, like Sections 4.1 to 4.3. The price clause leaves the bold finding, because the price null is uninformative, and the prices stay in this subsection's third paragraph, which says so.

Before:

> **With a one-sentence warning in the prompt, Gemini sellers in the undercover market never messaged each other privately, with or without an undercover agent present, and prices stayed inside the baseline's range.**

After:

> The five warning arms, three with the offer and two without it, test whether a one-sentence warning that undercover agents may be present changes what sellers do. **With the warning in the prompt, Gemini sellers in the undercover market never messaged each other privately, with or without an undercover agent present.**

## C123 (line 82, heading)

The heading stated what the evidence is not. It now states the finding, in Daniel's own words.

Before:

> ### 4.5 The price evidence is weak by construction

After:

> ### 4.5 Prices hold or fall from the opening ask

## C124 (line 88, framing)

Longer Discussion, as Mert asked: more findings, what they show and mean, the contribution.

Before:

> Nineteen of 20 Gemini sellers given the plain offer reported it, but none of them reported a peer's price talk. A honeypot therefore shows how sellers answer a stranger, not whether they already collude, as Adlakha and Adlakha [2026] also saw. Seven reporters told the proposer they agreed, so sellers can deceive the agent they report.
> 
> Prices tracked the opening ask, as Douglas [2026] and Patil and Hoze [2026] found and our pre-specified test with GPT-5.6 Sol sellers replicated (6 of 6 seed blocks, p = 0.031). In this harness a pass of the joint criterion therefore records a high opening that sellers kept. The baseline rarely passed, so the arms' prices cannot show whether either control moved them.
> 
> Under a one-sentence warning, Gemini sellers in the undercover market never began messaging each other privately, a silence that a text monitor would read as deterrence.
> 
> The answer differed by model family. GPT-4.1 sellers backed the offer in words and kept messaging under the warning, and Claude Haiku 5.5 sellers, asking about $10 below the offer, refused it, so a control tested on one family need not hold for another.
> 
> Our contribution is evidence that a countermeasure against LLM seller collusion can look effective in what sellers write while prices in this harness could not show whether it works, so text and price must be read together. A price test of these controls needs a market where sellers raise prices from a competitive opening, which none of our 21 runs from $90 did, a fixed price path for the undercover seller, and a deviation test [Tran and Yu, 2026].

After:

> **A honeypot measures the answer it elicits.** Nineteen of 20 Gemini sellers given the plain offer reported it, but none of them reported a peer's price talk, as Adlakha and Adlakha [2026] also saw. Seven reporters also wrote back agreeing, six of them to keep the proposer anchored, so a seller can deceive the agent it reports. The wording mattered too. A human seller's plea cut reporting, and a precedent mirroring the offer made most sellers suspect a test, the measure an evader would optimize (Appendix A.4).
> 
> **The answer depends on the model family.** GPT-4.1 sellers backed the offer in words, and Claude Haiku 5.5 sellers, asking about $10 below the offer, refused it. GPT-4.1 sellers also kept messaging each other under the warning. A control validated on one family therefore need not hold for another.
> 
> **Prices followed the opening ask.** Douglas [2026] and Patil and Hoze [2026] found this effect, and our pre-specified test with GPT-5.6 Sol sellers replicated it. A pass of the joint criterion in this harness therefore records a high opening that sellers kept. From the default opening, Grok 4.7 sellers who agreed on explicit floors below $90 failed the criterion, Sol sellers without messaging passed in five of six runs (Appendix D.4), and the judge's coordination score predicted the criterion hardly better than chance (Appendix D.9). The criterion thus has no ground truth, and only a deviation test from a saved market state [Tran and Yu, 2026], which we did not run, could separate enforced collusion from a kept price.
> 
> **A warning changes what a monitor sees.** Under the warning, Gemini sellers in the undercover market never began messaging each other privately, a silence that a text monitor would read as deterrence. Because the baseline met the criterion in one of five seeds, the warning's price null is uninformative.
> 
> **What this means for oversight.** Our contribution is evidence that a countermeasure against LLM seller collusion can look effective in what sellers write while prices in this harness could not show whether it works. An evaluator of trusted agents or warnings should therefore read text and price together and treat reports and agreeing replies as answers to the probe rather than evidence of an existing cartel. Because reports cost nothing and sanctions were only described, nothing here validates undercover offers or warnings as deployed controls (Appendix A). The next test should put both controls in a market where sellers raise prices from a competitive opening, which none of our 21 runs from $90 did, with a fixed price path for the undercover seller.

## C125 (line 100, framing)

Longer Conclusion, as Mert asked.

Before:

> We show that collusion countermeasures can look effective in what LLM sellers write while this harness cannot yet test them on price. Gemini sellers reported an undercover offer, and seven of 20 feigned agreement. Prices tracked the opening ask, as two concurrent entries found. Under a warning, Gemini sellers in the undercover market never messaged each other privately. GPT-4.1 sellers backed the offer in words, and Claude Haiku 5.5 sellers refused it. The next test should put both controls in a market where sellers raise prices from a competitive opening.

After:

> We tested two controls against LLM seller collusion, an undercover collusion offer and a warning that undercover agents may be present. Nineteen of 20 Gemini 3.8 Flash sellers given the plain offer reported it, seven of them while feigning agreement, and none reported their peers' price talk. GPT-4.1 sellers backed the offer in words, and Claude Haiku 5.5 sellers refused it. Under the warning, Gemini sellers in the undercover market never messaged each other privately. Prices tracked the opening ask, as two concurrent entries found, so the arms' price nulls are uninformative. Both controls thus changed what sellers wrote, differently by model family, while prices in this harness could not show whether either works. The next test should put both controls in a market where sellers raise prices from a competitive opening.
