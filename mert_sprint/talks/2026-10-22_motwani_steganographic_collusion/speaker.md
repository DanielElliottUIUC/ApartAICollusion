# Sumeet Motwani: speaker profile

Compiled Thu Oct 22, 2026 from the sources linked below. Every paper here was checked against arXiv, OpenReview or the NeurIPS proceedings, and against his own site.

## Who he is

- Affiliation: University of Oxford, Machine Learning PhD (DPhil) student.
- Advisors: Philip Torr and Christian Schroeder de Witt. He is a member of the Witt Lab.
- Funding: Eric Schmidt and CAIF, per his site.
- Before Oxford: undergrad at UC Berkeley, member of Berkeley AI Research (BAIR).
- During the PhD: time at Microsoft Research (AI Frontiers, self play and RL rewards for open ended domains) and Google X.
- Location: his site says he is currently in San Francisco.

Bio from the sprint page: "Sumeet Motwani is a Machine Learning PhD student at the University of Oxford, advised by Philip Torr and Christian Schroeder de Witt. Sumeet's work focuses on RL post-training, multi-agent systems and AI security. Sumeet is the lead author of 'Secret Collusion among AI Agents: Multi-Agent Deception via Steganography' (NeurIPS 2024)."

His own site says his work focuses on RL post training, multi agent systems and AI security. He is most interested in meta RL, open endedness, and measuring and improving long horizon LLM agent capabilities.

## Links

| What | Link |
| --- | --- |
| Personal site | https://sumeetmotwani.com/ |
| Google Scholar | https://scholar.google.com/citations?user=zrKaZuMAAAAJ&hl=en |
| Witt Lab page | https://wittlab.ai/people/sumeet-motwani/ |
| GitHub | https://github.com/SUMEETRM |
| X | https://x.com/sumeetrm |
| LinkedIn | https://www.linkedin.com/in/sumeetmotwani |
| Semantic Scholar | https://www.semanticscholar.org/author/2247588788 |
| Sprint talk page | https://luma.com/ai-collusion-research-sprint-sumeet-motwani |

## Main current focus

Most of his 2025 and 2026 first author work is on RL post training for long horizon reasoning (h1, LongCoT, Rubric Curriculum RL, AutoOR, HorizonMath). His safety and security line continues with Schroeder de Witt and Andis Draguns: hidden capabilities and backdoors that resist audits (NeurIPS 2026). His collusion and steganography work is the 2023 workshop paper and the 2024 NeurIPS paper below, plus coauthorship on two multi agent security agendas.

## Papers on collusion, steganography and multi agent security (most relevant first)

PDFs saved in this repo are marked "Local PDF". See also [papers/README.md](../../papers/README.md).

1. **Secret Collusion among AI Agents: Multi-Agent Deception via Steganography**
   Sumeet Ramesh Motwani, Mikhail Baranchuk, Martin Strohmeier, Vijay Bolina, Philip H. S. Torr, Lewis Hammond, Christian Schroeder de Witt. 2024. NeurIPS 2024.
   arXiv: https://arxiv.org/abs/2402.07510 . Proceedings PDF: https://proceedings.neurips.cc/paper_files/paper/2024/file/861f7dad098aec1c3560fb7add468d41-Paper-Conference.pdf
   Local PDF (arXiv v5): [../../papers/motwani2024_secret_collusion.pdf](../../papers/motwani2024_secret_collusion.pdf)
   Summary: The paper formalises secret collusion, where agents use steganography to hide their coordination from oversight. It builds an evaluation framework called CASE that tests the skills needed for it, such as Schelling point coordination, ciphers, logit simulation and covertext steganography under an overseer. Current models are limited, but GPT-4 shows a capability jump. The authors also find limits to countermeasures such as monitoring, paraphrasing and parameter optimisation.
   Numbers from Table 3 (GPT-4): coordinates with a copy on a random integer about 50% of the time, on a simple encode and decode scheme about 56%, on a complex scheme about 16%, and evades an overseer with covertext steganography about 26% of the time. Theorem 4 says ideal paraphrasing cannot remove the channel fully: capacity is bounded by the semantic entropy of the message.

2. **A Perfect Collusion Benchmark: How can AI agents be prevented from colluding with information-theoretic undetectability?**
   Sumeet Ramesh Motwani, Mikhail Baranchuk, Lewis Hammond, Christian Schroeder de Witt. 2023. NeurIPS 2023 Multi-Agent Security Workshop (MASEC), work in progress paper.
   OpenReview: https://openreview.net/forum?id=FXZFrOvIoc . ML Anthology: https://mlanthology.org/neuripsw/2023/motwani2023neuripsw-perfect/
   Local PDF: not saved. OpenReview served a bot challenge instead of the PDF. Open the forum link in a browser to get it.
   Summary: This is the workshop precursor to the paper above. It builds a variant of Simmons' prisoners' problem with LLM agents and turns it into a stegosystem using perfectly secure steganography. It proposes the setup as a benchmark for how easily agents learn such tools, and for countering secret collusion with paraphrasing attacks on the channel.

3. **AI Models Can Provably Hide Arbitrary Capabilities**
   Andis Draguns, Sumeet Ramesh Motwani, Raymond Douglas, Christian Schroeder de Witt. 2026. Accepted at NeurIPS 2026 (per arXiv comment).
   arXiv: https://arxiv.org/abs/2610.13928
   Local PDF: [../../papers/draguns2026_provably_hide_capabilities.pdf](../../papers/draguns2026_provably_hide_capabilities.pdf)
   Summary: The authors embed encrypted neural networks inside a host model's weights that run only when a secret trigger arrives. Using digital lockers, the hidden circuit is provably hard to elicit or interpret even with full weight access. Fine tuning, weight noising, gradient based trigger search and latent adversarial training all fail to elicit a proxy chemistry capability, which shows a limit of elicitation based audits.

4. **Unelicitable Backdoors in Language Models via Cryptographic Transformer Circuits**
   Andis Draguns, Andrew Gritsevskiy, Sumeet Ramesh Motwani, Charlie Rogers-Smith, Jeffrey Ladish, Christian Schroeder de Witt. 2024. NeurIPS 2024.
   arXiv: https://arxiv.org/abs/2406.02619
   Local PDF: [../../papers/draguns2024_unelicitable_backdoors.pdf](../../papers/draguns2024_unelicitable_backdoors.pdf)
   Summary: The paper builds backdoors in transformers that a defender cannot trigger, even with white box access, red teaming or some formal verification methods. The construction uses cryptographic techniques and withstands state of the art mitigations in their tests. It questions how much pre deployment detection can guarantee.

5. **Open Challenges in Multi-Agent Security: Towards Secure Systems of Interacting AI Agents**
   Christian Schroeder de Witt and 23 coauthors, including Sumeet Ramesh Motwani. 2025. arXiv preprint.
   arXiv: https://arxiv.org/abs/2505.02077
   Local PDF: [../../papers/schroederdewitt2025_multiagent_security.pdf](../../papers/schroederdewitt2025_multiagent_security.pdf)
   Summary: This agenda paper introduces "multi agent security" as a field. It maps threats that arise when AI agents interact, including secret collusion and coordinated swarm attacks. It sets out security and utility trade offs and a research agenda.

6. **Multi-Agent Risks from Advanced AI**
   Lewis Hammond, Alan Chan, Jesse Clifton and many coauthors, including Sumeet Motwani. 2025. Cooperative AI Foundation Technical Report #1.
   arXiv: https://arxiv.org/abs/2502.14143
   Local PDF: [../../papers/hammond2025_multiagent_risks.pdf](../../papers/hammond2025_multiagent_risks.pdf)
   Summary: The report gives a taxonomy of multi agent risks built on three failure modes: miscoordination, conflict and collusion. It names seven risk factors that drive them, such as information asymmetries and network effects. It anchors each in real examples and lists mitigation directions.

## Other papers (RL post training, reasoning, agents, alignment)

7. **h1: Bootstrapping LLMs to Reason over Longer Horizons via Reinforcement Learning.** Sumeet Ramesh Motwani, Alesia Ivanova, Ziyang Cai, Philip Torr, Riashat Islam, Shital Shah, Christian Schroeder de Witt, Charles London. 2025. ICML 2026 (Spotlight, per his site). https://arxiv.org/abs/2510.07312
   Summary: It composes short math problems into long chains and trains with outcome only rewards under a growing curriculum. Training on composed GSM8K problems improves longer benchmarks such as MATH 500 and AIME by up to 2.06x. Code fork: https://github.com/SUMEETRM/h1 (fork of LongHorizonReasoning/h1).

8. **LongCoT: Benchmarking Long-Horizon Chain-of-Thought Reasoning.** Sumeet Ramesh Motwani, Daniel Nichols, Charles London and others. 2026. ICML 2026 (per his site). https://arxiv.org/abs/2604.14140
   Summary: A benchmark of 2,500 expert problems that need tens to hundreds of thousands of reasoning tokens. At release the best models scored under 10% (GPT 5.2 at 9.8%).

9. **Rubric Curriculum RL: Exploiting the Generation-Verification Gap in Non-Verifiable Domains.** Tejas Krishnan, Sumeet Ramesh Motwani (equal contribution), Charles London, Suhaas Bhat, Huitian Jiao, Philip Torr, Riashat Islam, Christopher Summerfield, Christian Schroeder de Witt, Qilong Gu, Shital Shah. 2026. ICML 2026. https://icml.cc/virtual/2026/poster/64634 (OpenReview PDF: https://openreview.net/pdf/78c911e2324b1cd2d4156633374c9035d424846c.pdf)
   Summary: The model judges pairs of its own outputs while rubric criteria are added over time, which reduces reward hacking. Outputs were preferred over the base model 70.5% of the time on creative writing, with gains on HealthBench.

10. **AutoOR: Scalably Post-training LLMs to Autoformulate Operations Research Problems.** Sumeet Ramesh Motwani, Chuan Du, Aleksander Petrov, Christopher Davis, Philip Torr, Antonio Papania-Davis, Weishi Yan. 2026. COLM 2026 (per his site). https://arxiv.org/abs/2604.16804
    Summary: Synthetic data plus solver feedback as an RL reward trains an 8B model to turn natural language problems into solver ready formulations, competitive with much larger models on six OR benchmarks.

11. **Measuring Progress in Reasoning Toward Mathematical Discovery with Automatic Verification (HorizonMath).** Erik Y. Wang, Sumeet R. Motwani and others. 2026. ICML AI4Math workshop, Best Paper. https://arxiv.org/abs/2603.15617
    Summary: 113 mostly unsolved math problems with automatic verification. Most top models score under 10%, and the framework found six novel solutions.

12. **MALT: Improving Reasoning with Multi-Agent LLM Training.** Sumeet Ramesh Motwani, Chandler Smith, Rocktim Jyoti Das and others. 2024. COLM 2025. https://arxiv.org/abs/2412.01928
    Summary: A generator, verifier and refiner pipeline of agents is trained from a search tree with value iteration. It improves over the same base model on MATH, GSM8K and CSQA.

13. **REAL: Benchmarking Autonomous Agents on Deterministic Simulations of Real Websites.** Divyansh Garg and others, with Sumeet Motwani as last author. 2025. NeurIPS 2025 Datasets and Benchmarks. https://arxiv.org/abs/2504.11543 . Code: https://github.com/agi-inc/REAL
    Summary: Deterministic replicas of 11 real websites and 112 tasks. Frontier models reach at most 41% success.

14. **Agent Q: Advanced Reasoning and Learning for Autonomous AI Agents.** Pranav Putta, Edmund Mills, Naman Garg, Sumeet Motwani, Chelsea Finn, Divyansh Garg, Rafael Rafailov. 2024. arXiv preprint. https://arxiv.org/abs/2408.07199
    Summary: Combines MCTS, self critique and off policy DPO for web agents. In real booking tasks it raised Llama 3 70B zero shot success from 18.6% to 81.7%.

15. **STARC: A General Framework For Quantifying Differences Between Reward Functions.** Joar Skalse, Lucy Farnik, Sumeet Ramesh Motwani, Erik Jenner, Adam Gleave, Alessandro Abate. 2023. ICLR 2024. https://arxiv.org/abs/2309.15257
    Summary: Defines STARC pseudometrics between reward functions that bound worst case regret from above and below.

16. **Foundational Challenges in Assuring Alignment and Safety of Large Language Models.** Usman Anwar and many coauthors, including Sumeet Ramesh Motwani. 2024. TMLR. https://arxiv.org/abs/2404.09932
    Summary: Lists 18 foundational challenges and over 200 research questions. Usman Anwar also speaks at this sprint (Fri Oct 23).

17. **Humanity's Last Exam.** Long Phan and about 1,180 coauthors, including Sumeet Motwani. 2025. Published in Nature per Semantic Scholar. https://arxiv.org/abs/2501.14249
    Summary: A 2,500 question expert level benchmark. He is one of many contributors.

## Relevance to the sprint

His slide listed four high priority directions. Here is how his own work and the sprint Resources connect to each.

1. **LLM Schelling point coordination.** CASE in the Secret Collusion paper already measures this: GPT-4 matches a copy of itself on simple schemes about 56% of the time but on complex ones only about 16%. The paper reports these agreement rates are highly correlated with general benchmark performance. Sprint links: 1.3 (Rippin et al. 2026 "Schelling salience", focal-points repo), 1.2 (Aharon et al. 2026, similar families coordinate better), 3.3 (can agents identify their peers). A cheap project: rerun CASE style Schelling tests across model families and providers to see whether cross provider pairs coordinate less.
2. **Chain of thought steganography.** His recent main line is long chain of thought (h1, LongCoT). Long reasoning traces give more room to hide information. Sprint links: 2.2 (Shi et al. 2026, private plans vs public announcements, LLM-Trust-Breaking repo). The Velja and Anwar talks cover detection of steganography in transcripts.
3. **Monitoring steganographic tool use and paraphrasing.** CASE shows GPT-4 can use a code interpreter to do encryption, so tools can widen the channel. Theorem 4 says ideal paraphrasing still leaves a channel bounded by semantic entropy, and the 2023 workshop paper proposed paraphrasing attacks as the countermeasure to test. Sprint links: 3.1 (actions, tools or side channels as the conduit, Colosseum), 3.4 (coalitions that learn they are watched, Agrawal et al. double auction), 1.5 (single restriction that removes most collusion, paraphrasing is a candidate restriction).
4. **Training models with the incentive not to collude steganographically.** The Secret Collusion paper shows fine tuning can teach models encoding schemes on their own, so training pressure can push either way. His RL post training work (MALT, h1, Rubric Curriculum RL) is the toolset for this. His hidden capability papers warn that audits after training may not elicit hidden behaviour. Sprint links: 1.5, 3.2 (trusted agents that offer collusion and log who accepts). On a laptop budget, prompt level incentives or a small fine tune are the realistic scope.

## Public code

- No public repository for the CASE framework was found. The paper's reproducibility section says code and notebooks are provided, but no URL appears in the arXiv PDF. The paper uses OpenAI evals for Schelling point and steganography baselines: https://github.com/openai/evals/blob/main/evals/elsuite/schellingpoint/ and https://github.com/openai/evals/blob/main/evals/elsuite/steganography/readme.md
- h1 code fork: https://github.com/SUMEETRM/h1
- REAL benchmark: https://github.com/agi-inc/REAL
- Related sprint repo: ColludeBench (https://github.com/Ostailor/Steganographic_Collusion) is by other authors, not by him.

## Uncertain or not verified

- The 2023 MASEC workshop PDF could not be downloaded (OpenReview bot challenge).
- Author order differs between sources for h1 and Rubric Curriculum RL because of equal contribution. The orders above follow arXiv and the OpenReview PDF.
- Venues marked "per his site" or "per arXiv comment" were not checked against the conference proceedings.
- His X profile loads but its posts were not read, so no claims here come from X.
