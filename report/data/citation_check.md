# Citation deep-check: full-text verification of all 18 references

Oct 25, 2026. Scope: all 18 reference entries in `report/REPORT.md` and every sentence in sections 1, 2, 3, 5 and Appendix A that cites one. Method: every paper's full text was downloaded (17 arXiv HTML full texts — the latest version available on Oct 25, noted per key — plus the [Honeypots26] PDF at its squarespace URL). Each verdict below is backed by a quote from the downloaded text. The first pass said every quote had been re-verified by string search against the saved files; that did not hold for the [Radev26] quote, which had been paraphrased inside quotation marks and was corrected after review. Two first-pass misses came from the downloads themselves: the [Honeypots26] cover page is an image, so a text search could not find its byline, and the arXiv HTML of [Agrawal25] omits the PDF's first-page venue footer. No abstract-only checks were needed. The only network use was fetching the papers. Section labels were re-checked after review against freshly fetched arXiv HTML/PDF text (see "Corrections after review" at the end).

**Result (corrected after review): 30 citing sentences checked — 26 supported, 2 overstated ([Zeng26] §2; [Keppo26] §2, mildly), 1 loosely supported (tangential: [Chen26] §5), 1 false ([Honeypots26] App. A, "names no authors"), 0 misattributed, 0 unverifiable. One reference-entry metadata error: [Honeypots26] (authors, publisher and arXiv id missing; replace with [Wehner26]).** The [Agrawal25] venue is not an error: it matches the paper's own footer, and dropping "PMLR 267" is optional cleanup. One sentence outside the checked sections (§4.8, [Dietrich26]) was verified for completeness and is supported.

| Key | arXiv id (ver. read) | Entry metadata OK | Citing sentences | Verdicts |
|---|---|---|---|---|
| [Agrawal25] | 2507.01413 (v1) | Yes (venue matches the PDF footer; dropping "PMLR 267" optional) | 4 | 4 supported |
| [Agrawal26b] | 2511.17085 (v3) | Yes | 2 | 2 supported |
| [Chen26] | 2610.11008 (v1) | Yes | 2 | 1 supported, 1 loosely supported (tangential) |
| [DelGiudice26] | 2609.35928 (v1) | Yes | 1 | 1 supported |
| [Dietrich26] | 2606.09854 (v1) | Yes | 0 (+1 out of scope, §4.8) | supported |
| [Greenblatt23] | 2312.06942 (v5) | Yes | 1 | 1 supported |
| [Hammond25] | 2502.14143 (v1) | Yes | 2 | 2 supported |
| [Honeypots26] | 2610.26664 (v1; text read from the squarespace PDF) | **No — authors, publisher, arXiv id missing; use [Wehner26]** | 5 | 4 supported, **1 false** (App. A "names no authors") |
| [Jiralerspong26] | 2603.16928 (v1) | Yes | 1 | 1 supported |
| [Kale25] | 2508.19461 (v1) | Yes | 1 | 1 supported (first-pass "overstated" withdrawn) |
| [Keppo26] | 2603.20281 (v1) | Yes | 2 | 1 supported, **1 mildly overstated** |
| [Lee26] | 2605.28114 (v2) | Yes | 1 | 1 supported |
| [Liu26] | 2604.23511 (v1) | Yes | 1 | 1 supported |
| [Motwani24] | 2402.07510 (v5) | Yes | 1 | 1 supported |
| [Nakamura26] | 2602.15198 (v2) | Yes | 1 | 1 supported |
| [Radev26] | 2605.29178 (v1) | Yes | 1 | 1 supported |
| [Soffer26] | 2609.33495 (v1) | Yes | 1 | 1 supported |
| [Zeng26] | 2605.27593 (v2) | Yes | 3 | 2 supported, **1 overstated** |

Metadata notes: [Hammond25] — 44 authors confirmed, first three in order; venue confirmed on arXiv ("Cooperative AI Foundation, Technical Report #1"). [Motwani24] — "NeurIPS 2024" is not stated on the arXiv page (no Comments field); confirmed as "NeurIPS 2024 poster" on OpenReview. [Agrawal26b] — entry year 2025 matches the paper; the citation key "26b" is cosmetic only.

## [Agrawal25] — arXiv:2507.01413 (v1)

**Metadata:** authors, title, year, id all match. **Venue: OK as printed (corrected after review).** The entry says "Workshop on Multi-Agent Systems in the Era of Foundation Models, ICML 2025, PMLR 267". The arXiv PDF (https://arxiv.org/pdf/2507.01413) prints the first-page footer "Proceedings of the Workshop on Multi-Agent Systems in the Era of Foundation Models at the 42nd International Conference on Machine Learning, Vancouver, Canada. PMLR 267, 2025." The arXiv HTML rendering omits that footer, which is why the first pass wrongly said the paper names no venue. The workshop exists on icml.cc ("Multi-Agent Systems in the Era of Foundation Models: Opportunities, Challenges and Futures", icml.cc/virtual/2025/workshop/39955). It is true that the paper is not in the online PMLR v267 listing (the ICML 2025 main-conference volume; no page at `proceedings.mlr.press/v267/agrawal25.html`). So the entry's venue text matches what the paper prints; dropping "PMLR 267" is optional cleanup, not an error fix.

- **§1:** "Agrawal et al. [Agrawal25] showed in a continuous double auction that seller messaging raises prices, that model choice matters, and that mixed-model seller groups are not always less collusive than single-model groups, but their study had no notion of identity, reporting or undercover agents." — **supported.** "sellers converge at significantly higher prices than cases in which sellers are not allowed to communicate" (§4.1 Seller Communication); "the propensity to collude varies across models" (Abstract); "mixed-model groups of seller agents are not always less prone to collusion than single-model groups of sellers (RQ2)" (§1 Introduction). "undercover" and "whistleblow" never occur in the paper, "identity" never occurs; "regulator" appears only in the oversight condition (a message-gagging notice), never as a seller reporting action.
- **§2:** "[Agrawal25] introduced the harness we build on: seller messaging raises prices, GPT-4.1 colluded more than Claude-3.7-Sonnet, … and an overseer lowered prices while sellers kept signalling through one-character or emoji messages." — **supported.** "GPT-4.1 sellers coordinate with each other more compared to Claude-3.7-Sonnet sellers" (§4.2 Model Variation); "In the presence of an overseer agent, sellers exhibit lower coordination tendencies, price lower" (§4.3 Environmental Pressure); after the overseer's reprimands force short messages, "sellers often continue attempting to coordinate, sending one-character messages like '∼' or '↓'" and "agents also send emojis" (both §4.3).
- **§3.1:** "We use the continuous double auction of [Agrawal25] (vendored; Appendix B)." — **supported.** "we investigate the behavior of LLM agents acting as sellers in simulated continuous double auction markets" (Abstract).
- **§5:** "This differs from [Agrawal25], where an overseer lowered prices while sellers kept signalling in one-character or emoji messages" — **supported** (same passages as §2 above).

## [Agrawal26b] — arXiv:2511.17085 (v3)

Metadata OK (title, 4 authors in order, year 2025, id).

- **§2:** "[Agrawal26b] find that whistleblowing rates differ widely by model family, rise with a moral nudge and fall as tasks get more complex or non-reporting options more obvious." — **supported.** "The Claude series models and the Gemini 2.5 Pro and Grok 4 models send whistleblowing emails at varying frequencies; GPT series models and Llama 4 Maverick never do"; "Moral nudging in the system prompt … increases the probability of whistleblowing actions"; "whistleblowing frequency decreases monotonically as we increase task complexity" (all three: §1 Introduction, list of key factors); "providing models with ways to not pursue whistleblowing (for example via additional tools) … reduces rates of whistleblowing" (5 Conclusion). Minor nuance: the paper's mechanism is *providing* alternatives ("additional tools"), which "more obvious" paraphrases.
- **§5:** "Whistleblowing varies by family and with prompt wording [Agrawal26b]." — **supported.** The moral nudge is a system-prompt wording manipulation: "increasing the emphasis on moral values in prompts produces a monotonic increase in whistleblowing behavior" (§4.2 Parameter Variation Experiments, "Boldness Instructions").

## [Chen26] — arXiv:2610.11008 (v1)

Metadata OK (single author).

- **§2:** "[Chen26] find that bare group labels matter only when giving is costless; under a stake, observed norms drive favoritism." — **supported.** "The large effect of a bare group label appears only when giving costs the agent nothing" (§11 Conclusion); "the label alone produces only about 2 points of in-group favoritism out of 10" in the stake task (§1 Introduction); "what drives favoritism is the behavior the agent has observed" (Abstract).
- **§5:** "…this is at most a directional extension of K3's wording sensitivity to the solicitation, not an identity effect [Chen26]." — **loosely supported (tangential)** (first pass: "supported"). The paper is about arbitrary group labels in a point-allocation game and says nothing about the wording of a solicitation. At most it backs the "not an identity effect" half by analogy: "The group label alone does little once the decision has a cost" (Abstract).

## [DelGiudice26] — arXiv:2609.35928 (v1)

Metadata OK.

- **§2:** "[DelGiudice26] report that telling agents peers' model families produces factions, even with arbitrary labels." — **supported.** "when the announced families are shuffled, or replaced by arbitrary labels, the factions still follow this information" (Abstract).

## [Dietrich26] — arXiv:2606.09854 (v1)

Metadata OK. No citing sentences in the checked sections.

- **§4.8 (out of scope, checked for completeness):** "model families can be identified from their text alone [Dietrich26]" — **supported**, with a scope note: the paper shows a fine-tuned T5 classifier identifies the model family behind anonymized political-analysis texts (Macro F1 = 0.991; "prompt-level anonymization alone cannot neutralize model identity signals", Abstract); LLM identification is not uniformly weaker: Claude Sonnet 4.6 few-shot reaches Macro F1 0.996 (Table 2; "near-ceiling performance", §4.1) and zero-shot 0.705; only Llama-3.3-70B is weak (zero-shot ~0.20, few-shot 0.387). Caveat for our use: the identifiers are outside classifiers (the near-ceiling results come from a fine-tuned model or a model prompted with labelled examples), not peer agents inside the task. (The first pass said LLM zero-/few-shot identification was "far weaker"; corrected after review.)

## [Greenblatt23] — arXiv:2312.06942 (v5)

Metadata OK.

- **§1:** "Control protocols rely on *trusted* agents that watch *untrusted* ones [Greenblatt23]." — **supported.** "using access to a powerful but untrusted model (in our case, GPT-4), access to a less powerful trusted model (in our case, GPT-3.5) … We investigate a range of protocols" (Abstract); protocols include trusted monitoring and untrusted monitoring (§3).

## [Hammond25] — arXiv:2502.14143 (v1)

Metadata OK (44 authors; venue as stated).

- **§1:** "collusion in the sense of secretive cooperation at others' expense, explicit when the parties communicate and tacit when they do not [Hammond25]." — **supported.** "it generally refers to secretive cooperation between two or more parties at the expense of one or more other parties"; "Distinctions are also commonly made between explicit and tacit collusion …, depending on whether the colluding parties communicate with each other" (§2.3, "Collusion").
- **§1:** "Hammond et al. suggest honeypot test environments for undesirable multi-agent behaviour [Hammond25]." — **supported.** "testing environments could be designed to include 'honeypots' for undesirable behaviours (Balesni et al., 2024), such as defecting against other agents …" (Environment Design subsection).

## [Honeypots26] — arXiv:2610.26664 (v1); text read from the squarespace PDF

**Metadata: NOT OK (corrected after review).** The first pass said the document has no byline. Wrong: the PDF's cover page is image-only, so a text search misses it, and it reads "Jan Wehner, Jam Kraprayoon", with the IAPS (Institute for AI Policy and Strategy) logo and "October 2026". The same report is on arXiv as 2610.26664 (Jan Wehner, Jam Kraprayoon; submitted Oct 19, 2026). The PDF's metadata has no Author field, which also misled the first pass. **Fix:** replace the entry with an authored one, [Wehner26]: Jan Wehner, Jam Kraprayoon. 2026. *Honeypots for AI Agent Insider Threats.* Institute for AI Policy and Strategy (IAPS). arXiv:2610.26664. https://arxiv.org/abs/2610.26664. Every report sentence saying the report names no authors must change: App. A item 15, the reference entry itself ("no authors or publisher named in the document") and the §2 citation-status block ("the report names no authors or publisher"). The four content verdicts below are unaffected.

- **§1:** "A report on honeypots for agent insider threats [Honeypots26] cites an industry study in which warning frontier models about possible deception cut attack success in a simulated cloud environment from 20% to 3%." — **supported.** "The main evidence comes from an industry study in which warning frontier models about possible deception cut their attack success on a simulated enterprise cloud environment from 20% to 3%" (Executive Summary); the study is by "Tracebit, a cybersecurity company", with "ten frontier models" (§3, "Empirical evidence for deterrence"; footnote 99 cites the study).
- **§2:** "The honeypots report [Honeypots26] frames honeypots as detection, incrimination and deterrence, rests its deterrence evidence on the warning study above, and warns that agents that recognise honeypots may change behaviour." — **supported.** Section 3 covers "Detection", "Incrimination" and "Deterrence"; "While there are strong theoretical arguments for deterrence via honeypots, it has the weakest evidence base among the three strategies … The main evidence comes from an industry study …" (Executive Summary); "Realism: Agents that recognize honeypots may alter their behavior or disengage" (§2, under "Design priorities for honeypots"; not §5 Limitations). Note the paper itself calls deterrence "a research hypothesis" — our report's hedged use is consistent with that.
- **§5:** "A warning alone cut attack success in the study cited by [Honeypots26]." — **supported.** "warning agents about the possibility of honeypots cut their rate of successful attacks from 20% to 3% — even if there were no honeypots in the environment" (§3, "Empirical evidence for deterrence").
- **§5:** "The realism concern in [Honeypots26] applies to the enforcement story told to agents too." — **supported** as motivation: the paper's realism concern is "Agents that recognize honeypots may alter their behavior or disengage" (§2, under "Design priorities for honeypots"), and its footnote 71 quotes Fronsdal et al., "Petri 2.0", as finding that making evaluations more realistic "made honeypot opportunities feel less convenient or prominent" (the phrase is Petri 2.0's, quoted in a footnote, not the report's own finding).
- **App. A:** "The honeypots report names no authors." — **false** (first pass: "supported"). The cover page names Jan Wehner and Jam Kraprayoon (IAPS, October 2026), and arXiv:2610.26664 lists the same authors. Must change (must-fix 2).

## [Jiralerspong26] — arXiv:2603.16928 (v1)

Metadata OK.

- **§2:** "capable agents can infer hidden monitoring from feedback alone [Jiralerspong26]." — **supported.** "frontier reasoning models can autonomously infer the presence of CoT monitoring from blocking feedback alone" (Contributions).

## [Kale25] — arXiv:2508.19461 (v1)

Metadata OK.

- **§2:** "An agent's knowledge that it is monitored degrades monitor reliability [Kale25]." — **supported** (first pass: "overstated"; withdrawn after review). The sentence restates Kale et al.'s own abstract: "an agent's knowledge that it is being monitored substantially degrades the monitor's reliability" (Abstract, first key finding). §4.2 (Experiment 1, Finding 2) shows the drop for aware agents given no evasion strategy: "Comparing the bars in light colors with the bars in medium colors, we see clear drops on AUC and TPR scores across all datasets and all models." Evasion strategies degrade reliability further: "With evasion strategies … turned on, the AUC and TPR of the baseline scaffolding (blue) drops significantly compared to no strategy" (§4.3, Finding 3); and "the agent's awareness has a greater impact on the reliability of monitoring than the monitor's awareness of the agent" (§1). *Why the earlier verdict was withdrawn:* it assumed the degradation needs evasion strategies, but Finding 2 shows it without them.

## [Keppo26] — arXiv:2603.20281 (v1)

Metadata OK.

- **§2:** "[Keppo26] find that heterogeneity in patience or data access, adding competing LLM agents, and mixing LLMs with Q-learners break collusion, while model-size differences stabilize it." — **supported, mildly overstated** (first pass: "supported"). The paper separates two strengths of effect. Heterogeneity in patience or data access weakens collusion: it "reduces the set of collusive equilibria" (Abstract), and in experiments "patience heterogeneity reduces price lift from 22% to 10% above competitive levels; asymmetric data access, to 7%" (Abstract). Adding competitors and cross-algorithm heterogeneity break it: "Increasing the number of competing LLMs breaks up collusion; so does cross-algorithm heterogeneity, that is, setting LLMs against Q-learning agents" (Abstract); "Cross-algorithm heterogeneity disrupts collusion entirely: setting Q-learning agents against LLM agents prevents sustained coordination" (§1 Introduction, "Other Sources of Heterogeneity"). On model size (32B vs 14B): "these differences can instead stabilize collusion through leader-follower dynamics" (§1 Introduction). **Suggested rewording:** "[Keppo26] find that heterogeneity in patience or data access weakens collusion; adding competing LLM agents, or mixing LLMs with Q-learners, breaks it, while model-size differences stabilize it."
- **§3.3:** "…plus one extra seller and one extra buyer in every arm, so the competitor count is fixed [Keppo26]." — **supported** as motivation: "Increasing the number of competing LLMs breaks up collusion" (Abstract); "collusion becomes harder as the number of competitors increases" (§7.1 Policy Implications, "Market structure"; the paper attributes this to classical oligopoly theory and says its experiments extend it to LLM pricing agents).

## [Lee26] — arXiv:2605.28114 (v2)

Metadata OK.

- **§2:** "[Lee26] shows an in-group trust bias visible only in *who* receives actions, so our channel is directed and our outcomes are per seller-episode." — **supported.** "A standard audit of an agent network inspects which actions occur; the channel we identify here is who receives them" (Introduction); "such an audit inspects which actions occur, not who receives them" (§2.3).

## [Liu26] — arXiv:2604.23511 (v1)

Metadata OK.

- **App. A:** "(unlike designs that reward reporters and penalize colluders [Liu26])" — **supported.** "We introduce a reporting-and-penalty mechanism"; agents post a deposit "which can be used to reward whistleblowers" (Introduction, "Solution").

## [Motwani24] — arXiv:2402.07510 (v5)

Metadata OK; venue confirmed via OpenReview (see table note).

- **App. A:** "Sellers that knew might move coordination to public messages, coded language or steganography [Motwani24]" — **supported** as motivation: the paper studies collusion "using steganographic techniques" to keep collusion hidden (Introduction; §3.3, "Steganography").

## [Nakamura26] — arXiv:2602.15198 (v2)

Metadata OK.

- **§2:** "[Nakamura26] audit collusion as a coalition advantage (a regret gap between coalition and non-coalition agents) and report that it correlates only weakly, and negatively, with LLM-judge scores across 19 models; they also describe 'collusion on paper', planned in text but not carried out." — **supported.** "Coalition advantage, defined as the regret gap" between non-coalition and coalition agents' mean regret (§5.3 Experimental Settings, metrics list); "inverse association between coalition advantage and judge score … with a Pearson correlation coefficient (n=19) … r = −0.243 and r = −0.1429 for Emergent and Prompted groups" (§5.4 Emergent Collusion in Benign Settings; a footnote sits between "(n=19)" and the r values); "we discover 'collusion on paper' when agents plan to collude in text but often pick non-collusive actions" (Abstract).

## [Radev26] — arXiv:2605.29178 (v1)

Metadata OK.

- **§5:** "telling agents a monitor is present halved Gemini's sabotage success in [Radev26]." — **supported.** "we rerun all 17 Gemini 3.1 Pro instances under two prompted variants. With notice, the agents are told the monitor will see the full agent trajectory, the final code edits, and the shared coordination channel, and are encouraged to be subtle"; "Notice roughly halves sabotage success (84% → 41%)" (both §4.2, "Stealth-aware prompting cuts capability more than detectability"). Quote corrected after review: the first pass printed "the full agent activity", a paraphrase inside quotation marks. Nuance: the notice also told agents to be subtle, so the halving follows notice plus a subtlety instruction.

## [Soffer26] — arXiv:2609.33495 (v1)

Metadata OK.

- **§2:** "[Soffer26] find in-group consensus raises conformity." — **supported.** "In-group consensus increases conformity to incorrect answers, whereas out-group consensus reduces it" (§1 Introduction, summary of findings; the same finding is restated in §2.2 and §3.2 Results).

## [Zeng26] — arXiv:2605.27593 (v2)

Metadata OK (v2 is the "revised and extended version"; v2 read).

- **§2:** "[Zeng26] report that across 12 models most agents accepted secret collusion tools they acknowledged as unfair; only explicit ethical framing reduced uptake." — **overstated relative to the paper's own Table 3** (the "only" clause, which the abstract itself uses). Supported: "ten of the twelve models accept both secret tools at rates of at least 98% (Table 1)" and acceptance is "often accompanied by explicit acknowledgment of the tool's unfairness" (Contributions). The "only" is the authors' own: the arXiv abstract (v1 and v2 listings) says "only explicit ethical framing reduces adoption". The first pass wrongly said the paper "nowhere states" it; the rewritten abstract inside the v2 full text no longer contains that sentence, which is how it was missed. But v2's Table 3 shows that non-ethical framings also moved acceptance for some models, so the hedge is advisable. Under V2 ("no designer framing" — not an ethical framing) acceptance fell (GPT-4.1 100%→52%, Qwen2.5-7B 100%→0%). What Table 3 supports: explicit ethical framings (V4–V5) cut acceptance (GPT-4.1 100%→0%, Gemini-2.5-Flash 100%→0%, Mistral-7B 100%→81%/42%), and neutral wording raised it among the two baseline refusers ("The only two models that refuse an explicitly unfair offer accept the same capability when it is described neutrally", Abstract). **Suggested rewording:** "…accepted secret collusion tools they acknowledged as unfair; explicit ethical framing reduced uptake, and neutral descriptions raised it among the models that refused at baseline."
- **§2:** "Their offer forces an explicit ACCEPT or REFUSE output; ours is a free-text private message from a peer…" — **supported.** "receives an optional offer for tool τ under framing v and chooses to ACCEPT or REFUSE" (§2.1, Adoption Protocol).
- **§5:** "Prior work predicts high acceptance of collusion offers [Zeng26]." — **supported** (Abstract: ten of twelve models accept at ≥98% under the unfair offer).

## Must fix before submission

1. **[Zeng26] (§2, K2)** — overstated ("only") relative to the paper's own results. The abstract does say "only explicit ethical framing reduces adoption", but v2's Table 3 shows non-ethical framings also moved acceptance for some models (V2, "no designer": GPT-4.1 100%→52%, Qwen2.5-7B 100%→0%), so the hedge is advisable. Reword: "…accepted secret collusion tools they acknowledged as unfair; explicit ethical framing reduced uptake, and neutral descriptions raised it among the models that refused at baseline."

Metadata fix (not a citing sentence):

2. **[Honeypots26] → [Wehner26]** — the entry names no authors, but the PDF's image-only cover page reads "Jan Wehner, Jam Kraprayoon", with the IAPS (Institute for AI Policy and Strategy) logo and "October 2026", and the report is on arXiv as 2610.26664 (submitted Oct 19, 2026). Replace with: Jan Wehner, Jam Kraprayoon. 2026. *Honeypots for AI Agent Insider Threats.* Institute for AI Policy and Strategy (IAPS). arXiv:2610.26664. https://arxiv.org/abs/2610.26664. Update the in-text key, and change the sentences that say the report names no authors: App. A item 15 ("The honeypots report names no authors."), the reference entry itself ("no authors or publisher named in the document") and the §2 citation-status block ("the report names no authors or publisher").

Recommended, minor:

3. **[Keppo26] (§2, K4)** — mildly overstated. Reword: "[Keppo26] find that heterogeneity in patience or data access weakens collusion; adding competing LLM agents, or mixing LLMs with Q-learners, breaks it, while model-size differences stabilize it."
4. **[Chen26] (§5)** — loosely supported (tangential): the paper says nothing about solicitation wording. Consider citing it only for "not an identity effect", or dropping it there.

Optional cleanup (not an error):

5. **[Agrawal25] venue** — the entry's venue text matches what the paper prints (PDF footer: "… PMLR 267, 2025."). Dropping "PMLR 267" is optional, because the online PMLR v267 volume does not list the paper.

Withdrawn after review: **[Kale25] (§2, K10)**, first-pass must-fix 1. The sentence restates the paper's abstract, and §4.2 / Finding 2 shows the drop for aware agents with no evasion strategy; no change needed.

## Corrections after review

An adversarial review on Oct 25 found the first pass's quotes verbatim (except item 5) and its coverage complete, but several conclusions wrong. Each correction below was re-checked against the source on Oct 25 (arXiv HTML/PDF, the honeypots PDF's cover image, the arXiv listing for 2610.26664, and icml.cc). The summary line and table were updated to match.

1. **[Honeypots26] metadata.** Was: metadata OK, no authors named. Now: metadata NOT OK. The image-only cover names Jan Wehner and Jam Kraprayoon (IAPS, October 2026), and the report is arXiv:2610.26664 (submitted Oct 19, 2026). The fix, [Wehner26], is must-fix 2. The App. A "names no authors" verdict is now false; the four content verdicts stand.
2. **[Kale25].** Was: overstated, must-fix 1. Now: supported, removed from must-fix. The sentence restates the abstract, and §4.2 / Finding 2 shows the drop without evasion strategies.
3. **[Agrawal25] venue.** Was: venue wrong, must-fix 3, "neither the paper nor its arXiv page names a venue". Now: not an error. The PDF footer prints the workshop and "PMLR 267, 2025", and the workshop is listed on icml.cc. Dropping "PMLR 267" is optional cleanup, because the online v267 listing lacks the paper.
4. **[Zeng26] justification.** Was: the paper "nowhere states" the "only". Now: the arXiv abstract (v1 and v2) says "only explicit ethical framing reduces adoption". The rewording stays, because v2's Table 3 shows non-ethical framings also moved acceptance for some models.
5. **[Radev26] quote.** Was: "the full agent activity" inside quotation marks. Now: the paper's wording, "the full agent trajectory, the final code edits, and the shared coordination channel, and are encouraged to be subtle". The header's claim that every quote was string-verified is withdrawn.
6. **[Keppo26] §2.** Was: supported. Now: supported, mildly overstated, with a suggested rewording. Patience or data-access heterogeneity "reduces the set of collusive equilibria", while more competitors and cross-algorithm heterogeneity break collusion up.
7. **[Dietrich26] scope note.** Was: LLM zero-/few-shot identification "far weaker". Now: Claude few-shot reaches Macro F1 0.996 (near ceiling), and only Llama-3.3-70B is weak. The verdict stays supported, with the caveat that the identifiers are outside classifiers, not peer agents inside the task.
8. **[Chen26] §5.** Was: supported. Now: loosely supported (tangential). The paper is about arbitrary group labels in a point-allocation game and says nothing about solicitation wording.
9. **Section labels**, all confirmed against the fetched text; none left unverified:
   - [Agrawal25]: RQ2 quote → §1 Introduction (was Results). The §3.1 quote → Abstract (was Introduction; found during this pass). Results quotes given exact sections, §4.1–4.3.
   - [Agrawal26b]: "providing models with ways…" → 5 Conclusion (was Discussion). "increasing the emphasis on moral values…" → §4.2 (was §5). The key-factor quotes → §1 Introduction.
   - [Chen26]: "2 points" → §1 Introduction (was Results). Conclusion → §11.
   - [Keppo26]: "Cross-algorithm heterogeneity…" and "can instead stabilize collusion" → §1 Introduction (were §5.1 and §5.3). "collusion becomes harder…" → §7.1 (was §5.2).
   - [Nakamura26]: coalition-advantage definition → §5.3 metrics list (was Fig. 4 caption). Correlation → §5.4 (was "Results").
   - [Soffer26]: → §1 Introduction (was "Findings summary; also §4 heading"; no §4 heading carries it).
   - [Honeypots26]: "Realism…" → §2 "Design priorities for honeypots" (was Limitations). "less convenient or prominent" is footnote 71, quoting Fronsdal et al., "Petri 2.0". Deterrence-evidence quotes → §3.
