# Consolidated Research Notes — HW4 (2024–2026 SOTA)

This file consolidates research material from three parallel research streams for the HW4 survey report. Material is used in Parts 3–5.

## A. Agentic AI / LLM Agents / RLHF / RLAIF (used in Part 3, 5)

### Key papers / systems
- OpenAI: CUA/Operator (Jan 2025), Deep Research (Feb 2025), GPT-5/5.2/5.5 (Aug–Dec 2025); SWE-bench Verified 74.9%–82.7%.
- Anthropic: Claude Computer Use (Oct 2024), MCP (Nov 2024, 97M monthly downloads by Dec 2025, donated to Linux Foundation Agentic AI Foundation), Claude Code, Claude Skills.
- Google: Project Astra, Project Mariner (10 parallel tasks), Gemini 2.5 Pro Deep Think (planning via "world model").
- DPO (NeurIPS 2023), IPO (AISTATS 2024), KTO (ICML 2024 spotlight).
- Constitutional AI (Bai 2022), RLAIF vs RLHF (Lee, ICML 2024).
- PRM800K (Lightman, ICLR 2024), DeepSeek-R1 (Nature 2025) — GRPO + RLVR, ~147K H800 GPU-hr.
- OpenAI o1/o3 — inference-time scaling law.
- ReAct (ICLR 2023), Toolformer (NeurIPS 2023), Gorilla (NeurIPS 2024).
- Benchmarks: SWE-bench Verified, GAIA, AgentBench, WebArena (61.7% by IBM CUGA), OSWorld, τ-bench.
- Generative Agents (Park 2023), CAMEL, MetaGPT (ICLR 2024 oral), ChatDev, AutoGen → Microsoft Agent Framework.
- SIMA (Mar 2024), SIMA 2 (Nov 2025), Magma (CVPR 2025).
- Self-Rewarding LMs (Yuan, ICML 2024), Meta-Rewarding LMs, STaR.
- MemGPT/Letta, Generative-agent memory.

### Key open problems
1. Reliability gap (τ-bench shows weak pass^k consistency)
2. Reward hacking (UC Berkeley CRDI cracked all 8 agent benchmarks Apr 2026)
3. RLVR plateau in non-verifiable domains
4. Memory: no consensus (long-context vs RAG vs OS-style)
5. MARL + LLM agent integration is an open frontier

## B. Robotics / Embodied AI / VLA / Diffusion Policy / Sim2Real (used in Parts 4, 5)

### Key systems
**VLA models:**
- RT-1 (Dec 2022), RT-2 (Jul 2023, PaLI-X based, CoT reasoning)
- **OpenVLA** (2024) — 7B, open-weights, Llama-2+SigLIP, Open X-Embodiment 970k traj; +20.4% over Diffusion Policy, LoRA-tuneable, 5 Hz inference.
- **π0** (Oct 2024) — flow-matching at 50 Hz; **π0-FAST** (Jan 2025, DCT tokenizer, 5× train); **π0.5** (Apr 2025) — hierarchical reasoning, novel-kitchen cleanup.
- **Figure Helix** (Feb 2025) dual-process (S2 7-9Hz VLM + S1 200Hz visuomotor); **Figure 03** (Oct 2025) hardware redesign; 12k/yr production target.
- **GR00T N1** (NVIDIA, Mar 2025) — first open humanoid FM, 2B params, 16 actions in 63.9ms.
- **Gemini Robotics / 1.5 / -ER** (Mar/Sep 2025) — powers Apptronik Apollo.
- **Magma** (CVPR 2025) — digital + physical action FM, SoM/ToM.

**Diffusion Policy:**
- Diffusion Policy (RSS 2023, IJRR 2025), +46.9% across 12 tasks.
- 3D Diffusion Policy (DP3, 2024) — point clouds, 85% success on 4 real tasks with 40 demos.
- DexCap, Mobile ALOHA, Octo, CrossFormer.

**World models:**
- **DreamerV3** (Nature April 2025) — single hyperparam config, 150+ tasks, first to mine diamonds in Minecraft from scratch (~30M env steps).
- **Genie 1/2/3** — Genie 2 (Dec 2024) 3D worlds 10s memory; **Genie 3** (Aug 2025) 720p 24fps multi-minute consistency.
- **V-JEPA 2** (Meta, Jun 2025) — 1.2B, 1M hr video + 62 hr robot, 65-80% zero-shot pick-place, 30× faster than Cosmos.
- 1X World Model (1XWM), Sora as world simulator.

**Sim2Real:**
- DrEureka (RSS 2024) — LLM jointly synthesizes reward + DR params.
- Isaac Lab + Isaac Sim 4.x (2025): 2M env step/s on 8× RTX Pro 6000.
- MuJoCo MJX + MuJoCo Playground (Feb 2025) — JAX-native differentiable; sim2real to 6 platforms in <8 weeks.
- **Newton physics engine** (NVIDIA + Google + Disney, GTC 2025) — GPU + differentiable, 70× humanoid speedup, 100× in-hand manipulation.

**Humanoids:**
- Tesla Optimus Gen 3 (Oct 2025), Figure 02/03, Unitree H1/G1, 1X NEO ($499/mo), Apptronik Apollo ($520M raise, $5B val, Mercedes/GXO/Jabil deployed), Sanctuary AI.
- Berkeley fast RL on G1 (15 min on RTX 4090, arXiv:2512.01996); LeVERB (zero-shot WBC from language).
- HumanPlus, OmniH2O, ASAP (sim-pretrain + delta-action residual for real).

**Benchmarks/Datasets:**
- LIBERO (NeurIPS 2024) — dominant VLA bench; LIBERO-PRO (arXiv:2510.03827) flags memorization.
- RoboCasa (RSS 2024) — 100 kitchen tasks, gen-AI assets.
- ManiSkill3 (2024), DROID (RSS 2024, 76k demos), Open X-Embodiment (1M+ traj from 22 embodiments).

**RL-trained manipulation:**
- Eureka (ICLR 2024) — LLM reward design beats humans 80%+ of 29 tasks; Shadow Hand pen-spin.
- DrEureka (RSS 2024); SERL (Berkeley 2024) — 25-50 min real-world peg/PCB/cable.

### Open problems
1. Data scarcity (1M traj is <1% of LLM data)
2. Latency vs capability — dual-system consensus (Helix/GR00T/Gemini Robotics)
3. Generalization — π0.5 first credible novel-env demo
4. Sim2real for contact-rich/deformable still hard
5. Benchmark memorization (LIBERO-PRO)
6. Safety certification for unstructured deployment

## C. Game AI / AI for Science (used in Parts 4, 5)

### Game AI key
- AlphaGo (Nature 2016), AlphaGo Zero (Nature 2017), AlphaZero (Science 2018), MuZero (Nature 2020).
- AlphaStar (Nature 2019) — Grandmaster in StarCraft II; league training prevents Nash cycling.
- OpenAI Five (2019) — PPO on 128k CPU, beat OG world champions.
- Cicero (Science 2022) — Diplomacy human-level, piKL planning + LLM dialogue.
- DeepNash (Science 2022) — Stratego, R-NaD, model-free Nash convergence.
- SIMA / SIMA 2 (Mar 2024, Dec 2025) — Gemini-powered, self-improving in 3D games.
- MineDojo (NeurIPS 2022), Voyager (NeurIPS 2023) — in-context RL via GPT-4 + skill library.
- VPT (NeurIPS 2022) — BC pretrain + RL fine-tune on Minecraft, first diamond pickaxe.
- DreamerV3 (Nature 2025) — first to mine diamonds *from scratch*.
- POET / Enhanced POET (Uber, GECCO 2019, ICML 2020); XLand (DeepMind 2021).
- Gran Turismo Sophy (Nature 2022) — QR-SAC, beat world champion drivers; vision-only version 2024 (arXiv:2406.12563); GT7 champion 2025 (arXiv:2504.09021).
- **AlphaProof + AlphaGeometry 2** (Nature Nov 2025) — IMO 2024 silver (28/42), solved 3 problems incl. Q6.

### AI for Science key
- AlphaFold 2 (Nature 2021), AlphaFold 3 (Nature May 2024) — diffusion unifies proteins/NA/ligands.
- RoseTTAFold All-Atom (Science 2024); RFDiffusion (Nature 2023) — de novo protein design with picomolar binders.
- ESM-3 (EvolutionaryScale, Jun 2024) — 98B params, generated "500M years of evolution" GFP.
- REINVENT 4 (J. Cheminformatics 2024) — RL + transformer for molecular design.
- **GNoME** (DeepMind, Nature 2023) — 2.2M crystals, 380k stable (subject to 2024 critique).
- **A-Lab** (Berkeley + DeepMind, Nature 2023) — autonomous synthesis of 41/58 in 17 days.
- AlphaTensor (Nature 2022) — Strassen for 4×4 in F_2: 47 muls.
- FunSearch (Nature 2023) — LLM-driven new math (cap-set, bin-packing).
- AlphaCode 2 (Tech report 2023) — 85th percentile Codeforces; 10000× more sample-efficient than AC1.
- AlphaDev (Nature 2023) — sorts up to 70% faster, merged into LLVM libc++.
- TCV plasma control (Nature 2022); **Tearing-instability avoidance** (Nature Feb 2024) — DIII-D real-time control.
- AlphaChip (Nature 2021, addendum 2024) — controversial; Markov CACM 2024 critique.
- Coscientist (Nature 2023) — GPT-4 agent did Pd-catalyzed couplings.
- **AI Scientist v1/v2** (Sakana, 2024/Apr 2025) — first AI-authored paper passed ICLR 2025 workshop peer review.

### Cross-cutting Themes (2024-2026)
1. **RL + foundation models is the dominant paradigm** (SIMA 2, Voyager, AI-Scientist, AlphaProof).
2. **Verifier-driven RL** (formal proof, code exec, sims) winning vs pure preference-based RLHF/DPO.
3. **World-model RL** (DreamerV3, MuZero) crossed real-world thresholds.
4. **Reproducibility crises** (AlphaChip, GNoME) — field needs benchmarks not Nature covers.
