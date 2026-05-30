# AI Harness Demo Run

- **Query**: Survey robotics VLA models in 2024-2026
- **Backend**: offline
- **Sub-topics**: ['VLA foundation models', 'Diffusion Policy', 'Humanoid VLA']
- **Total tool calls**: 22
- **Tool-call efficiency**: 22/22 = 100%
- **Critic rounds fired**: 1
- **Wallclock**: 0.02s

## Phase Transcript

`[PLAN][agent]` User query: 'Survey robotics VLA models in 2024-2026'
`[PLAN][agent]` Plan: 3 sub-topics → ['VLA foundation models', 'Diffusion Policy', 'Humanoid VLA']
`[EXECUTE][agent]` --- Sub-topic: VLA foundation models ---
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'VLA foundation models'.
`[EXECUTE][action]` arxiv_search(query='vla foundation', year_min=2024, year_max=2026, max_results=4)
`[EXECUTE][observation]` Returned 2503.14734(score 2), 2503.20020(score 2), 2502.13130(score 2), 2406.09246(score 2)
`[EXECUTE][agent]` --- Sub-topic: Diffusion Policy ---
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'Diffusion Policy'.
`[EXECUTE][action]` arxiv_search(query='diffusion policy robot', year_min=2024, year_max=2026, max_results=4)
`[EXECUTE][observation]` Returned 2503.14734(score 2), 2504.16054(score 1), 2503.20020(score 1), 2502.13130(score 1)
`[EXECUTE][agent]` --- Sub-topic: Humanoid VLA ---
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'Humanoid VLA'.
`[EXECUTE][action]` arxiv_search(query='humanoid robot vla', year_min=2024, year_max=2026, max_results=4)
`[EXECUTE][observation]` Returned 2504.16054(score 3), 2503.14734(score 3), 2503.20020(score 3), 2502.13130(score 2)
`[EXECUTE][agent]` Cross-topic dedup → VLA foundation models: [2502.13130, 2406.09246], Diffusion Policy: [], Humanoid VLA: [2503.14734, 2503.20020, 2504.16054]
`[EXECUTE][agent]` Thought: Summarise paper 2502.13130 (Magma: A Foundation Model for Multimodal AI Agents…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2502.13130')
`[EXECUTE][observation]` contribution: Single foundation model for both digital + physical action.
`[EXECUTE][action]` note_save(topic='VLA foundation models', content=<391 chars>, meta=<paper record>)
`[EXECUTE][observation]` note_count=1 total_chars=391 persisted=True
`[EXECUTE][agent]` Thought: Summarise paper 2406.09246 (OpenVLA: An Open-Source Vision-Language-Action Mod…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2406.09246')
`[EXECUTE][observation]` contribution: First open-weights VLA matching or beating proprietary RT-2 baselines.
`[EXECUTE][action]` note_save(topic='VLA foundation models', content=<540 chars>, meta=<paper record>)
`[EXECUTE][observation]` note_count=2 total_chars=931 persisted=True
`[EXECUTE][agent]` Thought: Summarise paper 2503.14734 (GR00T N1: An Open Foundation Model for Generalist …).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.14734')
`[EXECUTE][observation]` contribution: First open humanoid foundation model with embedded-GPU latency budget.
`[EXECUTE][action]` note_save(topic='Humanoid VLA', content=<446 chars>, meta=<paper record>)
`[EXECUTE][observation]` note_count=1 total_chars=446 persisted=True
`[EXECUTE][agent]` Thought: Summarise paper 2503.20020 (Gemini Robotics: Bringing AI into the Physical Wor…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.20020')
`[EXECUTE][observation]` contribution: Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids.
`[EXECUTE][action]` note_save(topic='Humanoid VLA', content=<475 chars>, meta=<paper record>)
`[EXECUTE][observation]` note_count=2 total_chars=921 persisted=True
`[EXECUTE][agent]` Thought: Summarise paper 2504.16054 (Pi-0.5: A Vision-Language-Action Model with Open-W…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2504.16054')
`[EXECUTE][observation]` contribution: First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials.
`[EXECUTE][action]` note_save(topic='Humanoid VLA', content=<528 chars>, meta=<paper record>)
`[EXECUTE][observation]` note_count=3 total_chars=1449 persisted=True
`[CRITIC][agent]` Post-dedup coverage: VLA foundation models=2, Diffusion Policy=0, Humanoid VLA=3
`[CRITIC][agent]` Coverage GAP on ['Diffusion Policy'] → broadening year range and re-searching (1 round).
`[EXECUTE][agent]` Critic-triggered re-search for 'Diffusion Policy' (year_min=2022).
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'Diffusion Policy'.
`[EXECUTE][action]` arxiv_search(query='diffusion policy robot', year_min=2022, year_max=2026, max_results=4)
`[EXECUTE][observation]` Returned 2303.04137(score 3), 2503.14734(score 2), 2504.16054(score 1), 2503.20020(score 1)
`[EXECUTE][agent]` Re-search dedup → Diffusion Policy: [2303.04137]
`[EXECUTE][agent]` Thought: Summarise paper 2303.04137 (Diffusion Policy: Visuomotor Policy Learning via A…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2303.04137')
`[EXECUTE][observation]` contribution: +46.9% over prior SOTA across 12 tasks / 4 benchmarks.
`[EXECUTE][action]` note_save(topic='Diffusion Policy', content=<470 chars>, meta=<paper record>)
`[EXECUTE][observation]` note_count=1 total_chars=470 persisted=True
`[COMPILE][agent]` Report compiled from note store (4183 chars, 22 total tool calls, 1 critic round(s) fired).

---

## Compiled Report

# A Mini-Survey on robotics VLA models in 2024-2026

> *AI Harness compiled survey — generated by DRL Research Assistant (offline backend).*
> Query: **"Survey robotics VLA models in 2024-2026"**

## 1. Overview

This mini-survey was compiled by an AI Harness from 6 papers across 3 sub-topic(s): VLA foundation models, Diffusion Policy, Humanoid VLA. Every entry below is reconstructed from the persistent note store (each note's structured `meta`); no LLM-inline paper IDs or facts are accepted by the Compiler stage.

## 2. Findings by Sub-topic

### 2.1 VLA foundation models

- **Magma: A Foundation Model for Multimodal AI Agents** (CVPR 2025; arxiv:2502.13130). _Single foundation model for both digital + physical action._ Limitation: Zero-shot real-robot dexterous performance lags specialist VLAs.
- **OpenVLA: An Open-Source Vision-Language-Action Model** (arXiv 2024; arxiv:2406.09246). _First open-weights VLA matching or beating proprietary RT-2 baselines._ Limitation: 5 Hz inference is too slow for dexterous control; discrete action tokens limit precision; single-image observation hurts depth tasks.

### 2.2 Diffusion Policy

- **Diffusion Policy: Visuomotor Policy Learning via Action Diffusion** (RSS 2023; arxiv:2303.04137). _+46.9% over prior SOTA across 12 tasks / 4 benchmarks._ Limitation: Multi-step denoising slows inference; cross-embodiment transfer weak; needs depth for many tasks.

### 2.3 Humanoid VLA

- **GR00T N1: An Open Foundation Model for Generalist Humanoid Robots** (arXiv 2025; arxiv:2503.14734). _First open humanoid foundation model with embedded-GPU latency budget._ Limitation: Narrow real-world dexterity benchmarks; sim2real still needs domain-randomization tuning.
- **Gemini Robotics: Bringing AI into the Physical World** (arXiv 2025; arxiv:2503.20020). _Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids._ Limitation: Closed weights; cloud dependency; multimodal reasoning latency vs reactive control trade-off.
- **Pi-0.5: A Vision-Language-Action Model with Open-World Generalization** (arXiv 2025; arxiv:2504.16054). _First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials._ Limitation: Long-horizon failures remain dominant; teleop data still expensive; not yet a deployable household product.

## 3. Comparison Snapshot

| Paper | Sub-topic | Year | Venue | One-line contribution |
|---|---|---|---|---|
| Magma: A Foundation Model for Multimodal AI Agen | VLA foundation models | 2025 | CVPR | Single foundation model for both digital + physical action. |
| OpenVLA: An Open-Source Vision-Language-Action M | VLA foundation models | 2024 | arXiv | First open-weights VLA matching or beating proprietary RT-2 baselines. |
| Diffusion Policy: Visuomotor Policy Learning via | Diffusion Policy | 2023 | RSS | +46.9% over prior SOTA across 12 tasks / 4 benchmarks. |
| GR00T N1: An Open Foundation Model for Generalis | Humanoid VLA | 2025 | arXiv | First open humanoid foundation model with embedded-GPU latency budget. |
| Gemini Robotics: Bringing AI into the Physical W | Humanoid VLA | 2025 | arXiv | Closed-source generalist VLA powering Apptronik Apollo and other comme |
| Pi-0.5: A Vision-Language-Action Model with Open | Humanoid VLA | 2025 | arXiv | First VLA shown to clean entirely unseen real-world kitchens and bedro |

## 4. References

[1] Yang, J. et al. (Microsoft), "Magma: A Foundation Model for Multimodal AI Agents," CVPR, 2025. arXiv:2502.13130.

[2] Kim, M. J. et al., "OpenVLA: An Open-Source Vision-Language-Action Model," arXiv, 2024. arXiv:2406.09246.

[3] Chi, C. et al., "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion," RSS, 2023. arXiv:2303.04137.

[4] NVIDIA Research, "GR00T N1: An Open Foundation Model for Generalist Humanoid Robots," arXiv, 2025. arXiv:2503.14734.

[5] Google DeepMind, "Gemini Robotics: Bringing AI into the Physical World," arXiv, 2025. arXiv:2503.20020.

[6] Physical Intelligence Team, "Pi-0.5: A Vision-Language-Action Model with Open-World Generalization," arXiv, 2025. arXiv:2504.16054.

---
\textit{Compiled in 0.02s · 22 tool calls · 6 papers across 3 sub-topics.}
