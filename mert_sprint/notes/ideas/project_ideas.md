# Project ideas from Sumeet Motwani's talk and papers

Source: his talk on Oct 22, 2026 (slide in talks/2026-10-22_motwani_steganographic_collusion/slides/), his NeurIPS 2024 paper "Secret Collusion among AI Agents" (https://arxiv.org/abs/2402.07510, papers/motwani2024_secret_collusion.pdf), and the X thread archived in archive/x/2026-10-21_cnm13ryan_fable_image_steganography/.

Open item: Mert heard him name a "lowest hanging fruit" in the talk. Add it here once confirmed from the slides or recording.

Ordered from cheapest to riskiest.

## 1. Cross provider Schelling test
- Paper result: GPT-4 matches a copy of itself on a secret scheme about 56% of the time for simple schemes and about 16% for complex ones.
- Test: can models from different providers still agree on a code with no communication? Pairs such as Claude with Claude and Claude with GPT.
- Cost: prompts only, a few tens of dollars.
- Start from: OpenAI evals schellingpoint (https://github.com/openai/evals/blob/main/evals/elsuite/schellingpoint/).
- Sprint directions: 1.2, 1.3, 3.3.

## 2. Paraphrasing as a defense
- Paper result: Theorem 4 says ideal paraphrasing still leaves a channel bounded by semantic entropy.
- Test: agent A hides a message, a cheap model paraphrases it, agent B decodes it. Measure how much hidden information gets through.
- Compare light and heavy paraphrasing, and how much benign meaning each one destroys.
- Start from: OpenAI evals steganography (https://github.com/openai/evals/blob/main/evals/elsuite/steganography/readme.md).
- Sprint directions: 1.5, 3.1.

## 3. Image version: visual paraphrase defense
- Base: the Fable 5.1 image steganography thread (see notes/replications/cnm13ryan_fable_image_steganography.md).
- Test: whether noise, a small warp, or redrawing the image breaks the hidden channel.
- This is the same question as idea 2, in images. It gives the most visual figures for the report.
- Sprint direction: 3.1.

## 4. Tools widen the channel
- Paper result: GPT-4 can do real encryption once it has a code interpreter.
- Test: compare how often the hidden message gets through with and without a Python tool. Check whether a monitor that reads only the tool calls catches it.
- Sprint directions: 3.1, 3.4.

## 5. Hidden messages in chain of thought
- Test: can a reasoning model hide a message in its visible reasoning that a second model decodes?
- This is the most open question and the riskiest for one weekend.
- Sprint direction: 2.2.

## Current recommendation
For a solo weekend, idea 2 or idea 3. Both are cheap, have a clear measurement, and test his Theorem 4 directly.
