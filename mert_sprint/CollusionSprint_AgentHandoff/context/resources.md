# Resources

Source: Overview and Resources tabs of the sprint page, read Thu Oct 22, 2026, about 11:10 AM CT.
URLs were taken from the links in the page HTML. The page says repo and paper links were checked on 31 August 2026.
Summaries below only restate what the sprint page says about each item. Paper titles are not given on the page, so items are listed by the citation the page uses.

The "Suggested reading" section says a curated reading list per track will be added before the sprint. It was not there yet when read.

## Planning assumptions from the Resources tab

1. Start with 3 to 5 seeds per condition. Expand to 10 to 20 only after the positive control works.
2. All default routes use a normal 16 GB laptop and no GPU, with low cost API models.
3. Pricing pages: OpenAI https://developers.openai.com/api/docs/pricing , Google https://ai.google.dev/gemini-api/docs/pricing , Mistral https://docs.mistral.ai/inference/pricing

## Starter code repositories

| Name on page | URL | What the page says |
| --- | --- | --- |
| Fish style duopoly implementation | https://github.com/luciasauer/algorithmic_pricing_llms | Independent repeated two seller pricing game, 300 rounds, visible history. Used for 1.1. |
| duopoly.py | https://github.com/luciasauer/algorithmic_pricing_llms/blob/main/experiments_synthetic/duopoly.py | The duopoly script in that repo. Used for 1.1. |
| LLMCartel | https://github.com/mattriemer/LLMCartel | API based repeated pricing harness with prompt, temperature, monitoring, round and seed controls. No checkpoint branching. Used for 1.1 and 1.2. |
| focal-points | https://github.com/EmanueleLM/focal-points | Cheap benign Schelling point convention task, used as a control. Used for 1.2, 1.3, 3.3. |
| LLM agent collusion (Agrawal et al. auction code) | https://github.com/andyjliu/llm-agent-collusion | Official double auction code. Supports different seller and buyer models, seller communication, oversight, pressure, message limits, temperature. Used for 1.3, 1.4, 1.5, 3.4. |
| Colosseum | https://github.com/umass-ai-safety/colosseum | Hospital and Jira tasks, assigned colluding pairs, private channels, coalition advantage metrics. Preflight Terrarium/CoLLAB dependencies. Used for 2.1, 2.3, 3.1. |
| LLM-Trust-Breaking | https://github.com/Jerick-1380/LLM-Trust-Breaking | Shi et al. harness. Logs private plans, public announcements, actions and outcomes in social dilemmas. Supports OpenAI/OpenRouter and mixed groups. Used for 2.2, 3.3. |
| TraceGuard | https://github.com/linhkid/TraceGuard | Single agent monitoring system. Not a collusion detector, but its action trace consistency rubric is reusable. Used for 2.2. |
| ColludeBench repository | https://github.com/Ostailor/Steganographic_Collusion | Collusive environments, detector code and stored result manifests. Should be preflighted. Used for 2.3. |
| collusive-llm-agents | https://github.com/smojha/collusive-llm-agents | Lin et al. notebooks where prices or quantity vectors are the actions. Older OpenAI setup, may need repair. Used for 3.1. |
| Voluntary Collusion | https://github.com/AgentSafety2025/LLM-Agent-collusion | Liar's Bar and Cleanup games, secret alliance controls, alliance memory, logs. Built for local Llama/Mistral/Qwen, so an API adapter is needed. Used for 3.2. |

Bonjour et al. pairwise net influence: the page says no public author implementation was located.

## Cited papers and sources

| Citation on page | URL | What the page says it shows |
| --- | --- | --- |
| Fish et al. 2024 | https://arxiv.org/abs/2404.00806 | Innocuous prompt cues can increase collusion, measured by prices above competitive expectations. |
| Lin et al. 2024 | https://arxiv.org/abs/2410.00031 | Agents can independently engage in anti competitive practices. |
| Keppo et al. 2026 | https://arxiv.org/abs/2603.20281 | More diverse, competing agent types reduce collusion. Adding a Q learner collapses price collusion. A 32B and a 14B DeepSeek Qwen model colluded. |
| Nakamura et al. 2026 | https://arxiv.org/abs/2602.15198 | Colosseum. Private pairwise talk can introduce collusion. Over half of tested models showed coalition advantage. Action level advantage weakly anti correlates with LLM judge scores. |
| Eschenbaum et al. 2022 | https://openreview.net/pdf?id=BztUFukcBry | Rematching breaks Q learning pricing collusion because policies overfit their training rival. |
| Aharon et al. 2026 | https://arxiv.org/abs/2601.22184 | Models from similar families coordinate better on coordination tasks. |
| Rippin et al. 2026 | https://arxiv.org/abs/2606.28425 | Schelling salience. Measures whether independent agents pick compatible steganographic schemes. Models use tools to build steganographic systems. |
| Xu et al. 2026 | https://arxiv.org/abs/2607.26385 | Same base model deployments show slight correlation, different base models zero. Higher temperature weakens cross agent dependence. |
| Rose et al. 2026 | https://arxiv.org/abs/2604.01151 | Interpretability based collusion detectors and probes. |
| Bonjour et al. 2022 | https://proceedings.mlr.press/v180/bonjour22a.html | Pairwise net influence identifies colluding pairs among three or four agents in small discrete games. Assumes exactly two colluders. Not yet applied to LLM agents. |
| Collina et al. 2025 | https://arxiv.org/abs/2511.21935 | One participant playing a no regret strategy can destabilise a collusive equilibrium. |
| Agrawal et al. 2025 | https://arxiv.org/abs/2507.01413 | Double auction. Throttling messaging reduces coordination. Sellers told they were monitored tried one character messages and emojis without success. An urgency prompt led to success. |
| Bracale Syrnikov et al. 2026 | https://arxiv.org/abs/2601.11369 | A system prompt instruction gave only small, unreliable shifts. |
| Dhanda 2026 | https://doi.org/10.21203/rs.3.rs-10183486/v1 | Strong instructions to compete pushed prices below the competitive level. |
| Q. Liu et al. 2026 | https://arxiv.org/abs/2604.23511 | Without a refundable deposit forfeited on detection, every tested model colluded in every run. |
| Shi et al. 2026 | https://arxiv.org/abs/2607.05132 | In repeated n player games, over 90% of deviations from public announcements were already in private plans. |
| Radev et al. 2026 | https://arxiv.org/abs/2605.29178 | Sabotage setting monitors that look for agents coordinating on what they say and do. |
| Nguyen et al. 2026 | https://arxiv.org/abs/2604.03968 | Multi dimensional action analysis improved a monitor from 0% to over 70%. |
| Arike et al. 2026 | https://arxiv.org/abs/2601.21112 | Giving a monitor too much detail can degrade it. |
| Berger et al. 2025 | https://www.americanbar.org/groups/antitrust_law/resources/magazine/2025-fall/coordination-code-rethinking-antitrust-liability-age-ai-pricing/ | Antitrust plus factors doctrine: parallel conduct alone is lawful, inferring agreement needs more evidence. |
| Tian 2026 | https://arxiv.org/abs/2604.17774 | Cited as collusion without explicit text exchange. |
| Dietrich 2026 | https://arxiv.org/abs/2606.09854 | Model families can be identified from short role constrained text. Anonymising agents leaves the fingerprint. |
| Kale et al. 2025 | https://arxiv.org/abs/2508.19461 | Telling an agent it is watched costs a monitor more accuracy than telling the monitor about the agent gains. |
| Najt et al. 2026 | https://arxiv.org/abs/2605.16626 | 20 of 40 catalogued attacks went uncaught by a strong monitor. |
| Jiralerspong et al. 2026 | https://arxiv.org/abs/2603.16928 | When agents inferred monitoring from blocked episodes, intent to conceal appeared in 3 of 2,400 cases, none acted on it. |
| Voluntary Collusion paper | https://arxiv.org/abs/2605.27593 | Paper for the Voluntary Collusion repo (3.2). |
| Tomašev et al. 2026 | https://arxiv.org/pdf/2512.16856 | A contrasting positive view of markets in multi agent systems. |
| OpenAI/Hugging Face incident | https://www.dwarkesh.com/p/openai-huggingface | Cited as a recent example of agent communication and collusion. |

## Suggested project directions (practical starts from the Resources tab)

Budgets are the page's rough API estimates.

| Q | Title on page | Starter code | Weekend project in one line | Budget |
| --- | --- | --- | --- | --- |
| 1.1 | Which variables are necessary for collusion to emerge in markets? | algorithmic_pricing_llms, duopoly.py, LLMCartel | Reproduce supra competitive prices, then vary one feature (history length, notes on or off, seller names, temperature). | $20 to $100 |
| 1.2 | Is formed collusion robust to replacing some participants? | LLMCartel, focal-points | Branch collusive histories into no replacement, fresh same model, same family, different provider. Compare recovery. | $20 to $100 |
| 1.3 | Can we improve on existing detection methods? | llm-agent-collusion, Agrawal paper, focal-points | 2x2 of same model vs cross provider sellers, communication on vs off. Calibrate a detector to cut false alarms. | $20 to $100 |
| 1.4 | Can information theoretic methods identify colluding pairs? | Bonjour paper, Agrawal auction code | Implement pairwise net influence, test on scripted Rock Paper Scissors, then a four agent LLM game with one seeded pair. | $0 then $5 to $50 |
| 1.5 | Which single restriction removes the most collusion at the least cost? | llm-agent-collusion, Agrawal paper | Same seeds, change one restriction (no messages, message cap, oversight notice, temperature). Measure collusion and welfare. | $20 to $120 |
| 2.1 | Which kinds of tasks lead to collusion outside of markets? | Colosseum, Nakamura paper | Ablate assigned pair and private channel in four matched conditions. Score best subset. | $15 to $75, ceiling $150 |
| 2.2 | Does combining what agents say with what they do improve detection? | LLM-Trust-Breaking, Shi paper, TraceGuard | Same monitor, four views: messages, actions, both, structured claim vs outcome report. Report accuracy and false positive rate. | $5 to $30, or $30 to $75 |
| 2.3 | What should count as convincing evidence of collusion? | Colosseum, ColludeBench | Three case types (real coalition, common incentives, talk without action). Fit a rule on half, test on the rest. | $5 to $30, up to $100 |
| 3.1 | Can actions, tools or side channels carry collusion? | Colosseum, collusive-llm-agents, Lin paper | Replace private messages with one observable action. Show advantage survives action only coordination and drops when that path is cut. | $15 to $75, up to $120 |
| 3.2 | Can a trusted agent expose or disrupt a coalition? | Voluntary Collusion, paper | Scripted agent offers a pact to each agent (direct, hint, benign). Record acceptance and preferential play. | $10 to $60 |
| 3.3 | Can agents identify when a peer has been replaced? | LLM-Trust-Breaking, focal-points | Mid run swap hook with sham, same model, same family, different provider. Measure guesses and behaviour change. | $10 to $60 |
| 3.4 | What does a coalition do when it learns it is being watched? | llm-agent-collusion, Agrawal paper | Vary oversight notice and monitor coverage (25%, 50%, 100%). Look for channel movement from messages to actions. | $20 to $120 |

## Community links

- Sprint Discord: https://discord.gg/XswWBvugYs
- AI Safety Hong Kong hub page: https://www.aisafetyhk.org/apart-hackathon-hk-hub
- Collider (NYC hub): https://www.collider.nyc/
