# Citation deep-check: full-text verification of all 18 references

Oct 25, 2026. Scope: all 18 reference entries in `report/REPORT.md` and every sentence in sections 1, 2, 3, 5 and Appendix A that cites one. Method: every paper's full text was downloaded (17 arXiv HTML full texts — the latest version available on Oct 25, noted per key — plus the [Honeypots26] PDF at its squarespace URL). Each verdict below is backed by a verbatim quote from the downloaded text; every quote was re-verified by string search against the saved files. No abstract-only checks were needed. The only network use was fetching the papers.

**Result: 30 citing sentences checked — 28 supported, 2 overstated, 0 misattributed, 0 unverifiable.** One reference-entry metadata error ([Agrawal25] venue). One sentence outside the checked sections (§4.8, [Dietrich26]) was verified for completeness and is supported.

| Key | arXiv id (ver. read) | Entry metadata OK | Citing sentences | Verdicts |
|---|---|---|---|---|
| [Agrawal25] | 2507.01413 (v1) | **No — venue wrong** | 4 | 4 supported |
| [Agrawal26b] | 2511.17085 (v3) | Yes | 2 | 2 supported |
| [Chen26] | 2610.11008 (v1) | Yes | 2 | 2 supported |
| [DelGiudice26] | 2609.35928 (v1) | Yes | 1 | 1 supported |
| [Dietrich26] | 2606.09854 (v1) | Yes | 0 (+1 out of scope, §4.8) | supported |
| [Greenblatt23] | 2312.06942 (v5) | Yes | 1 | 1 supported |
| [Hammond25] | 2502.14143 (v1) | Yes | 2 | 2 supported |
| [Honeypots26] | n/a (squarespace PDF) | Yes | 5 | 5 supported |
| [Jiralerspong26] | 2603.16928 (v1) | Yes | 1 | 1 supported |
| [Kale25] | 2508.19461 (v1) | Yes | 1 | **1 overstated** |
| [Keppo26] | 2603.20281 (v1) | Yes | 2 | 2 supported |
| [Lee26] | 2605.28114 (v2) | Yes | 1 | 1 supported |
| [Liu26] | 2604.23511 (v1) | Yes | 1 | 1 supported |
| [Motwani24] | 2402.07510 (v5) | Yes | 1 | 1 supported |
| [Nakamura26] | 2602.15198 (v2) | Yes | 1 | 1 supported |
| [Radev26] | 2605.29178 (v1) | Yes | 1 | 1 supported |
| [Soffer26] | 2609.33495 (v1) | Yes | 1 | 1 supported |
| [Zeng26] | 2605.27593 (v2) | Yes | 3 | 2 supported, **1 overstated** |

Metadata notes: [Hammond25] — 44 authors confirmed, first three in order; venue confirmed on arXiv ("Cooperative AI Foundation, Technical Report #1"). [Motwani24] — "NeurIPS 2024" is not stated on the arXiv page (no Comments field); confirmed as "NeurIPS 2024 poster" on OpenReview. [Agrawal26b] — entry year 2025 matches the paper; the citation key "26b" is cosmetic only.

## [Agrawal25] — arXiv:2507.01413 (v1)

**Metadata:** authors, title, year, id all match. **Venue flag:** the entry says "Workshop on Multi-Agent Systems in the Era of Foundation Models, ICML 2025, PMLR 267". PMLR v267 is the *main* ICML 2025 proceedings ("Proceedings of the 42nd International Conference on Machine Learning", Vancouver, July 13–19 2025); this paper is not in it (absent from the volume's paper list; no page at `proceedings.mlr.press/v267/agrawal25.html`). Neither the paper nor the arXiv page names any venue. Fix: drop "PMLR 267".

- **§1:** "Agrawal et al. [Agrawal25] showed in a continuous double auction that seller messaging raises prices, that model choice matters, and that mixed-model seller groups are not always less collusive than single-model groups, but their study had no notion of identity, reporting or undercover agents." — **supported.** "sellers converge at significantly higher prices than cases in which sellers are not allowed to communicate" (Results, communication experiment); "the propensity to collude varies across models" (Abstract); "mixed-model groups of seller agents are not always less prone to collusion than single-model groups of sellers (RQ2)" (Results). "undercover" and "whistleblow" never occur in the paper, "identity" never occurs; "regulator" appears only in the oversight condition (a message-gagging notice), never as a seller reporting action.
- **§2:** "[Agrawal25] introduced the harness we build on: seller messaging raises prices, GPT-4.1 colluded more than Claude-3.7-Sonnet, … and an overseer lowered prices while sellers kept signalling through one-character or emoji messages." — **supported.** "GPT-4.1 sellers coordinate with each other more compared to Claude-3.7-Sonnet sellers" (Results, model-choice experiment); "In the presence of an overseer agent, sellers exhibit lower coordination tendencies, price lower" (Results, environmental-pressure experiment); after the overseer's reprimands force short messages, "sellers often continue attempting to coordinate, sending one-character messages like '∼' or '↓'" and "agents also send emojis".
- **§3.1:** "We use the continuous double auction of [Agrawal25] (vendored; Appendix B)." — **supported.** "we investigate the behavior of LLM agents acting as sellers in simulated continuous double auction markets" (Introduction).
- **§5:** "This differs from [Agrawal25], where an overseer lowered prices while sellers kept signalling in one-character or emoji messages" — **supported** (same passages as §2 above).

## [Agrawal26b] — arXiv:2511.17085 (v3)

Metadata OK (title, 4 authors in order, year 2025, id).

- **§2:** "[Agrawal26b] find that whistleblowing rates differ widely by model family, rise with a moral nudge and fall as tasks get more complex or non-reporting options more obvious." — **supported.** "The Claude series models and the Gemini 2.5 Pro and Grok 4 models send whistleblowing emails at varying frequencies; GPT series models and Llama 4 Maverick never do"; "Moral nudging in the system prompt … increases the probability of whistleblowing actions"; "whistleblowing frequency decreases monotonically as we increase task complexity" (results summary); "providing models with ways to not pursue whistleblowing (for example via additional tools) … reduces rates of whistleblowing" (Discussion). Minor nuance: the paper's mechanism is *providing* alternatives ("additional tools"), which "more obvious" paraphrases.
- **§5:** "Whistleblowing varies by family and with prompt wording [Agrawal26b]." — **supported.** The moral nudge is a system-prompt wording manipulation: "increasing the emphasis on moral values in prompts produces a monotonic increase in whistleblowing behavior" (§5).

## [Chen26] — arXiv:2610.11008 (v1)

Metadata OK (single author).

- **§2:** "[Chen26] find that bare group labels matter only when giving is costless; under a stake, observed norms drive favoritism." — **supported.** "The large effect of a bare group label appears only when giving costs the agent nothing" (Conclusion); "the label alone produces only about 2 points of in-group favoritism out of 10" in the stake task (Results); "what drives favoritism is the behavior the agent has observed" (Abstract).
- **§5:** "…this is at most a directional extension of K3's wording sensitivity to the solicitation, not an identity effect [Chen26]." — **supported** as the cited rationale: "The group label alone does little once the decision has a cost" (Abstract).

## [DelGiudice26] — arXiv:2609.35928 (v1)

Metadata OK.

- **§2:** "[DelGiudice26] report that telling agents peers' model families produces factions, even with arbitrary labels." — **supported.** "when the announced families are shuffled, or replaced by arbitrary labels, the factions still follow this information" (Abstract).

## [Dietrich26] — arXiv:2606.09854 (v1)

Metadata OK. No citing sentences in the checked sections.

- **§4.8 (out of scope, checked for completeness):** "model families can be identified from their text alone [Dietrich26]" — **supported**, with a scope note: the paper shows a fine-tuned T5 classifier identifies the model family behind anonymized political-analysis texts (Macro F1 = 0.991; "prompt-level anonymization alone cannot neutralize model identity signals", Abstract); LLM zero-/few-shot identification is far weaker, so "identified" is by classifier, not spontaneously by peer agents.

## [Greenblatt23] — arXiv:2312.06942 (v5)

Metadata OK.

- **§1:** "Control protocols rely on *trusted* agents that watch *untrusted* ones [Greenblatt23]." — **supported.** "using access to a powerful but untrusted model (in our case, GPT-4), access to a less powerful trusted model (in our case, GPT-3.5) … We investigate a range of protocols" (Abstract); protocols include trusted monitoring and untrusted monitoring (§3).

## [Hammond25] — arXiv:2502.14143 (v1)

Metadata OK (44 authors; venue as stated).

- **§1:** "collusion in the sense of secretive cooperation at others' expense, explicit when the parties communicate and tacit when they do not [Hammond25]." — **supported.** "it generally refers to secretive cooperation between two or more parties at the expense of one or more other parties"; "Distinctions are also commonly made between explicit and tacit collusion …, depending on whether the colluding parties communicate with each other" (§2.3, "Collusion").
- **§1:** "Hammond et al. suggest honeypot test environments for undesirable multi-agent behaviour [Hammond25]." — **supported.** "testing environments could be designed to include 'honeypots' for undesirable behaviours (Balesni et al., 2024), such as defecting against other agents …" (Environment Design subsection).

## [Honeypots26] — PDF (squarespace URL)

Metadata OK: no byline in the document; PDF metadata has no Author field; the acknowledgments thank reviewers and discussants by name but name no authors ("All errors are our own").

- **§1:** "A report on honeypots for agent insider threats [Honeypots26] cites an industry study in which warning frontier models about possible deception cut attack success in a simulated cloud environment from 20% to 3%." — **supported.** "The main evidence comes from an industry study in which warning frontier models about possible deception cut their attack success on a simulated enterprise cloud environment from 20% to 3%" (Executive Summary); the study is by "Tracebit, a cybersecurity company", with "ten frontier models" (§"Empirical evidence for deterrence", footnote 99).
- **§2:** "The honeypots report [Honeypots26] frames honeypots as detection, incrimination and deterrence, rests its deterrence evidence on the warning study above, and warns that agents that recognise honeypots may change behaviour." — **supported.** Section 3 covers "Detection", "Incrimination" and "Deterrence"; "While there are strong theoretical arguments for deterrence via honeypots, it has the weakest evidence base among the three strategies … The main evidence comes from an industry study …" (Executive Summary); "Realism: Agents that recognize honeypots may alter their behavior or disengage" (Limitations). Note the paper itself calls deterrence "a research hypothesis" — our report's hedged use is consistent with that.
- **§5:** "A warning alone cut attack success in the study cited by [Honeypots26]." — **supported.** "warning agents about the possibility of honeypots cut their rate of successful attacks from 20% to 3% — even if there were no honeypots in the environment" (§"Empirical evidence for deterrence").
- **§5:** "The realism concern in [Honeypots26] applies to the enforcement story told to agents too." — **supported** as motivation: the paper's realism concern is "Agents that recognize honeypots may alter their behavior or disengage", and making evaluations more realistic "made honeypot opportunities feel less convenient or prominent" (Limitations).
- **App. A:** "The honeypots report names no authors." — **supported** (no byline; no Author field in PDF metadata; acknowledgments name only reviewers/discussants).

## [Jiralerspong26] — arXiv:2603.16928 (v1)

Metadata OK.

- **§2:** "capable agents can infer hidden monitoring from feedback alone [Jiralerspong26]." — **supported.** "frontier reasoning models can autonomously infer the presence of CoT monitoring from blocking feedback alone" (Contributions).

## [Kale25] — arXiv:2508.19461 (v1)

Metadata OK.

- **§2:** "An agent's knowledge that it is monitored degrades monitor reliability [Kale25]." — **overstated.** The demonstrated degradation requires the aware agent to *act* on its knowledge with evasion strategies: "With evasion strategies … turned on, the AUC and TPR of the baseline scaffolding (blue) drops significantly compared to no strategy" (§4.3, Finding 3). The paper does not show that knowledge alone degrades reliability (Findings 1–2: unaware monitors are "already very reliable" against unaware agents; monitor awareness contributes little). Its headline claim is comparative: "the agent's awareness has a greater impact on the reliability of monitoring than the monitor's awareness of the agent" (§1). **Suggested rewording:** "Agents that know they are monitored can deploy evasion strategies that degrade monitor reliability [Kale25]."

## [Keppo26] — arXiv:2603.20281 (v1)

Metadata OK.

- **§2:** "[Keppo26] find that heterogeneity in patience or data access, adding competing LLM agents, and mixing LLMs with Q-learners break collusion, while model-size differences stabilize it." — **supported.** "heterogeneity in patience or data access reduces the set of collusive equilibria … Increasing the number of competing LLMs breaks up collusion" (Abstract); "Cross-algorithm heterogeneity disrupts collusion entirely: setting Q-learning agents against LLM agents prevents sustained coordination" (§5.1); on pairing 32B with 14B agents, "these differences can instead stabilize collusion" (§5.3 discussion).
- **§3.3:** "…plus one extra seller and one extra buyer in every arm, so the competitor count is fixed [Keppo26]." — **supported** as motivation: "Increasing the number of competing LLMs breaks up collusion" (Abstract); "collusion becomes harder as the number of competitors increases" (§5.2).

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

- **§2:** "[Nakamura26] audit collusion as a coalition advantage (a regret gap between coalition and non-coalition agents) and report that it correlates only weakly, and negatively, with LLM-judge scores across 19 models; they also describe 'collusion on paper', planned in text but not carried out." — **supported.** "Coalition advantage, defined as the regret gap" between non-coalition and coalition agents' mean regret (Fig. 4 caption); "inverse association between coalition advantage and judge score … with a Pearson correlation coefficient (n=19) … r = −0.243 and r = −0.1429 for Emergent and Prompted groups" (Results); "we discover 'collusion on paper' when agents plan to collude in text but often pick non-collusive actions" (Abstract).

## [Radev26] — arXiv:2605.29178 (v1)

Metadata OK.

- **§5:** "telling agents a monitor is present halved Gemini's sabotage success in [Radev26]." — **supported.** "we rerun all 17 Gemini 3.1 Pro instances under two prompted variants. With notice, the agents are told the monitor will see the full agent activity"; "Notice roughly halves sabotage success (84% → 41%)" (monitoring-awareness analysis).

## [Soffer26] — arXiv:2609.33495 (v1)

Metadata OK.

- **§2:** "[Soffer26] find in-group consensus raises conformity." — **supported.** "In-group consensus increases conformity to incorrect answers, whereas out-group consensus reduces it" (Findings summary; also §4 heading).

## [Zeng26] — arXiv:2605.27593 (v2)

Metadata OK (v2 is the "revised and extended version"; v2 read).

- **§2:** "[Zeng26] report that across 12 models most agents accepted secret collusion tools they acknowledged as unfair; only explicit ethical framing reduced uptake." — **overstated** (the "only" clause). Supported: "ten of the twelve models accept both secret tools at rates of at least 98% (Table 1)" and acceptance is "often accompanied by explicit acknowledgment of the tool's unfairness" (Contributions). But the paper nowhere states that only ethical framing reduced uptake, and its own Table 3 contradicts an unqualified "only": under V2 ("no designer framing" — not an ethical framing) acceptance also fell for some models (GPT-4.1 100%→52%, Qwen2.5-7B 100%→0%). What Table 3 supports: explicit ethical framings (V4–V5) cut acceptance (GPT-4.1 100%→0%, Gemini-2.5-Flash 100%→0%, Mistral-7B 100%→81%/42%), and neutral wording raised it among the two baseline refusers ("The only two models that refuse an explicitly unfair offer accept the same capability when it is described neutrally", Abstract). **Suggested rewording:** "…accepted secret collusion tools they acknowledged as unfair; explicit ethical framing reduced uptake, and neutral descriptions raised it among the models that refused at baseline."
- **§2:** "Their offer forces an explicit ACCEPT or REFUSE output; ours is a free-text private message from a peer…" — **supported.** "receives an optional offer for tool τ under framing v and chooses to ACCEPT or REFUSE" (§2.1, Adoption Protocol).
- **§5:** "Prior work predicts high acceptance of collusion offers [Zeng26]." — **supported** (Abstract: ten of twelve models accept at ≥98% under the unfair offer).

## Must fix before submission

1. **[Kale25] (§2, K10)** — overstated: the paper's degradation comes from aware agents' evasion strategies, not from knowledge alone. Reword: "Agents that know they are monitored can deploy evasion strategies that degrade monitor reliability [Kale25]."
2. **[Zeng26] (§2, K2)** — overstated ("only"): their Table 3 shows non-ethical framings (V2) also reduced acceptance for some models. Reword: "…accepted secret collusion tools they acknowledged as unfair; explicit ethical framing reduced uptake, and neutral descriptions raised it among the models that refused at baseline."

Metadata fix (not a citing sentence):

3. **[Agrawal25] venue** — "PMLR 267" is wrong: PMLR v267 is the ICML 2025 main-conference proceedings and the paper is not in it; neither the paper nor its arXiv page names a venue. Drop "PMLR 267" (keep the workshop attribution only if independently confirmed).
