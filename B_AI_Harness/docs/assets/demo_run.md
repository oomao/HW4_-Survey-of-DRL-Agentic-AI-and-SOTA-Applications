# AI Harness Demo Run

- **Query**: Survey robotics VLA models in 2024-2026
- **Backend**: offline
- **Sub-topics**: ['VLA foundation models', 'Diffusion Policy', 'Humanoid VLA']
- **Total tool calls**: 25
- **Wallclock**: 0.04s

## Phase Transcript

`[PLAN][agent]` User query: 'Survey robotics VLA models in 2024-2026'
`[PLAN][agent]` Plan: 3 sub-topics → ['VLA foundation models', 'Diffusion Policy', 'Humanoid VLA']
`[EXECUTE][agent]` --- Sub-topic: VLA foundation models ---
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'VLA foundation models'.
`[EXECUTE][action]` arxiv_search(query='vla foundation', year_min=2024, year_max=2026, max_results=3)
`[EXECUTE][observation]` Returned 3 papers: 2503.14734, 2503.20020, 2502.13130
`[EXECUTE][agent]` Thought: Summarise paper 2503.14734 (GR00T N1: An Open Foundation Model for Generalist …).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.14734')
`[EXECUTE][observation]` contribution: First open humanoid foundation model with embedded-GPU latency budget.
`[EXECUTE][action]` note_save(topic='VLA foundation models', content=<446 chars>)
`[EXECUTE][observation]` note_count=1 total_chars=446
`[EXECUTE][agent]` Thought: Summarise paper 2503.20020 (Gemini Robotics: Bringing AI into the Physical Wor…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.20020')
`[EXECUTE][observation]` contribution: Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids.
`[EXECUTE][action]` note_save(topic='VLA foundation models', content=<475 chars>)
`[EXECUTE][observation]` note_count=2 total_chars=921
`[EXECUTE][agent]` Thought: Summarise paper 2502.13130 (Magma: A Foundation Model for Multimodal AI Agents…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2502.13130')
`[EXECUTE][observation]` contribution: Single foundation model for both digital + physical action.
`[EXECUTE][action]` note_save(topic='VLA foundation models', content=<391 chars>)
`[EXECUTE][observation]` note_count=3 total_chars=1312
`[EXECUTE][agent]` --- Sub-topic: Diffusion Policy ---
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'Diffusion Policy'.
`[EXECUTE][action]` arxiv_search(query='diffusion policy robot', year_min=2024, year_max=2026, max_results=3)
`[EXECUTE][observation]` Returned 3 papers: 2503.14734, 2504.16054, 2503.20020
`[EXECUTE][agent]` Thought: Summarise paper 2503.14734 (GR00T N1: An Open Foundation Model for Generalist …).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.14734')
`[EXECUTE][observation]` contribution: First open humanoid foundation model with embedded-GPU latency budget.
`[EXECUTE][action]` note_save(topic='Diffusion Policy', content=<446 chars>)
`[EXECUTE][observation]` note_count=1 total_chars=446
`[EXECUTE][agent]` Thought: Summarise paper 2504.16054 (Pi-0.5: A Vision-Language-Action Model with Open-W…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2504.16054')
`[EXECUTE][observation]` contribution: First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials.
`[EXECUTE][action]` note_save(topic='Diffusion Policy', content=<528 chars>)
`[EXECUTE][observation]` note_count=2 total_chars=974
`[EXECUTE][agent]` Thought: Summarise paper 2503.20020 (Gemini Robotics: Bringing AI into the Physical Wor…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.20020')
`[EXECUTE][observation]` contribution: Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids.
`[EXECUTE][action]` note_save(topic='Diffusion Policy', content=<475 chars>)
`[EXECUTE][observation]` note_count=3 total_chars=1449
`[EXECUTE][agent]` --- Sub-topic: Humanoid VLA ---
`[EXECUTE][agent]` Thought: I need to gather recent papers on 'Humanoid VLA'.
`[EXECUTE][action]` arxiv_search(query='humanoid robot vla', year_min=2024, year_max=2026, max_results=3)
`[EXECUTE][observation]` Returned 3 papers: 2504.16054, 2503.14734, 2503.20020
`[EXECUTE][agent]` Thought: Summarise paper 2504.16054 (Pi-0.5: A Vision-Language-Action Model with Open-W…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2504.16054')
`[EXECUTE][observation]` contribution: First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials.
`[EXECUTE][action]` note_save(topic='Humanoid VLA', content=<528 chars>)
`[EXECUTE][observation]` note_count=1 total_chars=528
`[EXECUTE][agent]` Thought: Summarise paper 2503.14734 (GR00T N1: An Open Foundation Model for Generalist …).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.14734')
`[EXECUTE][observation]` contribution: First open humanoid foundation model with embedded-GPU latency budget.
`[EXECUTE][action]` note_save(topic='Humanoid VLA', content=<446 chars>)
`[EXECUTE][observation]` note_count=2 total_chars=974
`[EXECUTE][agent]` Thought: Summarise paper 2503.20020 (Gemini Robotics: Bringing AI into the Physical Wor…).
`[EXECUTE][action]` paper_summarize(arxiv_id='2503.20020')
`[EXECUTE][observation]` contribution: Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids.
`[EXECUTE][action]` note_save(topic='Humanoid VLA', content=<475 chars>)
`[EXECUTE][observation]` note_count=3 total_chars=1449
`[CRITIC][agent]` Coverage check passed for all 3 sub-topics.
`[COMPILE][agent]` Report compiled (5291 chars, 25 total tool calls).

---

## Compiled Report

# A Mini-Survey on Survey Robotics Vla Models In 2024-2026

> *AI Harness compiled survey — generated by DRL Research Assistant (offline backend).*
> Query: **"Survey robotics VLA models in 2024-2026"**

## 1. Overview

This mini-survey was compiled by an AI Harness from 9 papers across 3 sub-topic(s): VLA foundation models, Diffusion Policy, Humanoid VLA. All citations come from a tool-verified arXiv lookup; no LLM-generated paper IDs are accepted by the Compiler stage.

## 2. Findings by Sub-topic

### 2.1 VLA foundation models

- **GR00T N1: An Open Foundation Model for Generalist Humanoid Robots** (arXiv 2025; arxiv:2503.14734). _First open humanoid foundation model with embedded-GPU latency budget._ Limitation: Narrow real-world dexterity benchmarks; sim2real still needs domain-randomization tuning.
- **Gemini Robotics: Bringing AI into the Physical World** (arXiv 2025; arxiv:2503.20020). _Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids._ Limitation: Closed weights; cloud dependency; multimodal reasoning latency vs reactive control trade-off.
- **Magma: A Foundation Model for Multimodal AI Agents** (CVPR 2025; arxiv:2502.13130). _Single foundation model for both digital + physical action._ Limitation: Zero-shot real-robot dexterous performance lags specialist VLAs.

### 2.2 Diffusion Policy

- **GR00T N1: An Open Foundation Model for Generalist Humanoid Robots** (arXiv 2025; arxiv:2503.14734). _First open humanoid foundation model with embedded-GPU latency budget._ Limitation: Narrow real-world dexterity benchmarks; sim2real still needs domain-randomization tuning.
- **Pi-0.5: A Vision-Language-Action Model with Open-World Generalization** (arXiv 2025; arxiv:2504.16054). _First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials._ Limitation: Long-horizon failures remain dominant; teleop data still expensive; not yet a deployable household product.
- **Gemini Robotics: Bringing AI into the Physical World** (arXiv 2025; arxiv:2503.20020). _Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids._ Limitation: Closed weights; cloud dependency; multimodal reasoning latency vs reactive control trade-off.

### 2.3 Humanoid VLA

- **Pi-0.5: A Vision-Language-Action Model with Open-World Generalization** (arXiv 2025; arxiv:2504.16054). _First VLA shown to clean entirely unseen real-world kitchens and bedrooms across repeated trials._ Limitation: Long-horizon failures remain dominant; teleop data still expensive; not yet a deployable household product.
- **GR00T N1: An Open Foundation Model for Generalist Humanoid Robots** (arXiv 2025; arxiv:2503.14734). _First open humanoid foundation model with embedded-GPU latency budget._ Limitation: Narrow real-world dexterity benchmarks; sim2real still needs domain-randomization tuning.
- **Gemini Robotics: Bringing AI into the Physical World** (arXiv 2025; arxiv:2503.20020). _Closed-source generalist VLA powering Apptronik Apollo and other commercial humanoids._ Limitation: Closed weights; cloud dependency; multimodal reasoning latency vs reactive control trade-off.

## 3. Comparison Snapshot

| Paper | Sub-topic | Year | Venue | One-line contribution |
|---|---|---|---|---|
| GR00T N1: An Open Foundation Model for Generalis | VLA foundation models | 2025 | arXiv | First open humanoid foundation model with embedded-GPU latency budget. |
| Gemini Robotics: Bringing AI into the Physical W | VLA foundation models | 2025 | arXiv | Closed-source generalist VLA powering Apptronik Apollo and other comme |
| Magma: A Foundation Model for Multimodal AI Agen | VLA foundation models | 2025 | CVPR | Single foundation model for both digital + physical action. |
| GR00T N1: An Open Foundation Model for Generalis | Diffusion Policy | 2025 | arXiv | First open humanoid foundation model with embedded-GPU latency budget. |
| Pi-0.5: A Vision-Language-Action Model with Open | Diffusion Policy | 2025 | arXiv | First VLA shown to clean entirely unseen real-world kitchens and bedro |
| Gemini Robotics: Bringing AI into the Physical W | Diffusion Policy | 2025 | arXiv | Closed-source generalist VLA powering Apptronik Apollo and other comme |
| Pi-0.5: A Vision-Language-Action Model with Open | Humanoid VLA | 2025 | arXiv | First VLA shown to clean entirely unseen real-world kitchens and bedro |
| GR00T N1: An Open Foundation Model for Generalis | Humanoid VLA | 2025 | arXiv | First open humanoid foundation model with embedded-GPU latency budget. |
| Gemini Robotics: Bringing AI into the Physical W | Humanoid VLA | 2025 | arXiv | Closed-source generalist VLA powering Apptronik Apollo and other comme |

## 4. References

[1] NVIDIA Research, "GR00T N1: An Open Foundation Model for Generalist Humanoid Robots," arXiv, 2025. arXiv:2503.14734.

[2] Google DeepMind, "Gemini Robotics: Bringing AI into the Physical World," arXiv, 2025. arXiv:2503.20020.

[3] Yang, J. et al. (Microsoft), "Magma: A Foundation Model for Multimodal AI Agents," CVPR, 2025. arXiv:2502.13130.

[4] Physical Intelligence Team, "Pi-0.5: A Vision-Language-Action Model with Open-World Generalization," arXiv, 2025. arXiv:2504.16054.

---
\textit{Compiled in 0.04s · 25 tool calls · 9 papers across 3 sub-topics.}
