---
marp: true
theme: default
paginate: true
size: 16:9
header: 'HW4 — DRL & Agentic AI Survey (2024–2026)'
footer: 'csm088220 · 2026'
style: |
  section { font-family: "Microsoft JhengHei", "PMingLiU", sans-serif; font-size: 22px; }
  h1 { color: #0ea5e9; }
  h2 { color: #0c4a6e; border-bottom: 2px solid #0ea5e9; padding-bottom: 4px; }
  table { font-size: 18px; }
  code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; }
  .small { font-size: 16px; color: #64748b; }
---

# A Survey of Deep RL, Agentic AI, and SOTA Applications
## 2024 – 2026

DRL Course HW4
csm088220 · 2026

<small style="color:#94a3b8">10–15 min presentation · Marp-compatible Markdown</small>

---

## 投影片大綱（15 張，10–15 min）

1. Title
2. Motivation：DRL 在 2024–2026 變成了什麼？
3. Part 1：DRL 演算法地圖（一張圖）
4. Part 2：Systems & Platforms 概覽
5. Part 3：Agentic AI — 三大堆疊 + RLHF→RLVR
6. Part 4-A：Robotics & Embodied AI 的 dual-system 共識
7. Part 4-B：Game AI — AlphaGo 到 AlphaProof 12 年演化
8. Part 4-C：AI for Science — RL 改變了什麼
9. Part 5：5 條 SOTA 主軸收斂
10. Part 6：5 個演算法比較表
11. Part 7：開源生態關鍵 repo
12. Bonus Demo B：PPO on CartPole — 81 秒到 perfect
13. Bonus Demo C：ReAct LLM agent — 100 行的 multi-hop
14. Conclusion：3 個轉折 + 5 個未來方向 + 倫理風險
15. Q&A

---

## 2. Motivation — 為什麼 DRL 在 2024–2026 重新「重要」？

- **DeepSeek-R1**（Nature 2025）— 首篇 peer-reviewed LLM Nature 論文，純 RL on verifiable rewards
- **DreamerV3**（Nature 2025）— 首個從零挖到 Minecraft diamond 的演算法
- **AlphaProof**（Nature 2025）— IMO 2024 銀牌（28/42）
- **Figure 03**（Oct 2025）— 12k units/yr 量產設計，跑 Helix dual-system VLA
- **Apptronik Apollo**（Feb 2026, $5B 估值）— 部署 Mercedes / GXO / Jabil

> DRL 從「sub-field」變成「foundation models 的對齊 + 推理 + 規劃元件」

---

## 3. Part 1 — DRL 演算法地圖

```
Value-based:   DQN ── Double DQN ── Dueling ── PER ── C51 ── Rainbow ── Muesli
Policy-based:  REINFORCE ── A3C/A2C ── TRPO ── PPO ── GRPO (DeepSeek 2025)
Actor-Critic:  DDPG ── TD3 ── SAC ── SAC-X ── SERL / DrEureka
Model-based:   AlphaGo ── AlphaZero ── MuZero ── DreamerV3 (Nature 2025)
Sequence Model: Decision Transformer ── Gato ── Octo ── OpenVLA ── π0 ── GR00T N1
Offline RL:    BCQ ── CQL ── IQL ── DT
```

**Critical observation.** 全部演算法的「外圍」都被 LLM / VLM / foundation model 包覆。

---

## 4. Part 2 — Systems & Platforms 概覽

| 平台 | 為何重要 |
|---|---|
| **Isaac Lab** (NVIDIA) | GPU end-to-end, 2M env/s on 8× RTX Pro 6000 |
| **Habitat 3.0** (Meta) | 室內具身導航事實標準；HM3D 1000+ 棟掃描 |
| **CARLA** | 唯一被廣泛採用的開源自駕 simulator |
| **RLlib** vs **SB3** | 產業大規模 vs 學術 baseline 的 yin-yang |
| **FinRL** | 金融 DRL 主流框架；2024 推 FinRL-DeepSeek |
| **MineDojo** | 唯一規模化的 open-ended embodied benchmark |
| **OpenVLA** | 首個 open-weights VLA，打破 RT-2 閉源壟斷 |

---

## 5. Part 3 — Agentic AI：三大堆疊 + RLHF→RLVR 演化

**三大產品堆疊（2024–2026）**
- OpenAI：CUA / Deep Research / GPT-5（SWE-bench Verified 82.7%）
- Anthropic：Claude Code + Computer Use + **MCP**（97M 月下載；捐 Linux Foundation）
- Google：Project Astra + Mariner（10 parallel tasks）+ Gemini 2.5 Deep Think

**對齊演算法演化（成本下降 + 訊號客觀化）**
```
PPO + RLHF (2022)
   → DPO (NeurIPS 2023) ─ no reward model
   → KTO (ICML 2024)  ─ 二元標籤即可
   → RLAIF (ICML 2024) ─ AI 標籤
   → RLVR (DeepSeek-R1 / o1, 2024-25) ─ 可驗證 reward
   → GRPO ─ 取消 critic
```

---

## 6. Part 4-A — Robotics & Embodied AI：Dual-System 共識

**Helix / GR00T N1 / Gemini Robotics 1.5 / π0.5 共同收斂在：**

```
S2 (slow, 5–10 Hz) — 內部 VLM，做 semantic / planning
   │
   ▼ language goal / sub-task
S1 (fast, 100–200 Hz) — visuomotor policy，做 reactive control
```

**Key 2024–25 systems：**
- **OpenVLA** (7B, open weights, +20.4% over DP)
- **π0 / π0.5** — flow matching @ 50 Hz；π0.5 清掃 *unseen* kitchen
- **Helix** — 35 DoF Figure 02/03，embedded GPU
- **GR00T N1** — 16 actions in 63.9 ms on L40
- **Newton** physics engine — humanoid 70× sim 加速

---

## 7. Part 4-B — Game AI：12 年演化（2016 → 2026）

```
2016 AlphaGo (Lee Sedol)         ── supervised + RL + MCTS
2017 AlphaGo Zero                ── tabula rasa
2018 AlphaZero                   ── 跨棋類
2019 AlphaStar / OpenAI Five     ── realtime imperfect-info, league training
2020 MuZero                      ── learned latent dynamics
2022 Cicero / DeepNash           ── Diplomacy / Stratego, LLM+plan / R-NaD
2022 Gran Turismo Sophy          ── 打敗人類冠軍車手
2023 Voyager                     ── LLM + skill library + 無 gradient RL
2024 SIMA                        ── 9 款商業 3D 遊戲 generalist
2025 DreamerV3 (Nature)          ── 首次從零 mine diamond
2025 SIMA 2 (Dec) + AlphaProof   ── Gemini-driven self-improve + IMO 銀牌
```

---

## 8. Part 4-C — AI for Science：RL 改變了什麼？

| 系統 | 期刊 | RL 角色 | 影響 |
|---|---|---|---|
| **AlphaDev** | Nature 2023 | AlphaZero on assembly | sort 算法 70% 加速 → **merged into LLVM libc++** |
| **AlphaTensor** | Nature 2022 | MCTS on tensor decomp | Strassen 4×4 in F₂: 47 muls |
| **AlphaProof + AGeo2** | Nature 2025 | RL on Lean proof tree | IMO 2024 銀牌（28/42） |
| **DIII-D plasma** | Nature 2024 | real-time RL on tokamak | 避開 tearing instability |
| **GNoME + A-Lab** | Nature 2023 | active learning + 機器人 | 41/58 新材料 17 天 |
| **AI Scientist v2** | arXiv 2025 | agentic tree search | **首篇 AI-paper 通過 ICLR workshop peer review** |

---

## 9. Part 5 — 5 條 SOTA 主軸（2025–2026）

```
1. Foundation Models × RL
     RLHF / RLAIF / RLVR / GRPO; SIMA 2, AI Scientist v2

2. Embodied Generalist Agent
     OpenVLA, π0.5, GR00T N1, Magma, Gemini Robotics 1.5

3. Sim2Real × Differentiable Physics
     Newton, MJX, Isaac Lab 4.x, DrEureka

4. World Model × Imagined Planning
     DreamerV3 (Nature 2025), Genie 3, V-JEPA 2

5. Verifier-Driven RL
     DeepSeek-R1, AlphaProof, AlphaGeometry 2, AlphaDev
```

> 下一波 breakthrough 預測在這 5 條的**交叉點**。

---

## 10. Part 6 — 5 個演算法橫向比較

| 演算法 | Strength | Weakness | Sample Eff. | Real-world Use |
|---|---|---|---|---|
| **DQN** | Atari 元祖；replay+target 是基石 | overestimation；離散 only | 中 | 推薦、廣告 bidding |
| **PPO** | 簡單魯棒；離散+連續通用 | on-policy 不省 sample | 低 | **LLM RLHF 事實標準** |
| **SAC** | 連續控制 SOTA；entropy 探索 | continuous only；複雜 | 高 | 機器人、UAV、自駕 |
| **MuZero** | 不需已知 env model；高 sample eff. | 工程複雜；stochastic 弱 | 高 | 棋類、Atari、產業少見 |
| **DT** | 純 sequence model；天然 offline | stitching 差於 DP-based | 中 | VLA 系列祖先 |

---

## 11. Part 7 — 開源生態關鍵 repo

**研究 / 教學**
- SB3 · CleanRL · OpenAI Spinning Up · RLlib

**機器人 / 模擬器**
- Isaac Lab · MuJoCo MJX + Playground · Habitat-Lab · CARLA · Newton

**新世代 (2024–25)**
- OpenVLA · openpi (Physical Intelligence) · Octo · DROID
- Eureka / DrEureka / SERL · LIBERO · RoboCasa

**Agentic AI**
- DeepSeek-R1 · LangGraph · MCP specification · AutoGen→Microsoft Agent Framework

---

## 12. Bonus B — PPO on CartPole-v1（81 秒到滿分）

```bash
python code/ppo_demo.py
```

| | |
|---|---|
| Env | CartPole-v1, 4 parallel envs |
| Algo | PPO (SB3 2.8.0), MlpPolicy |
| Steps | 50,000 |
| Wallclock | **81.0 s** (CPU) |
| Eval (det.) | **500.0 ± 0.0** ← 滿分 |

![w:600](../artifacts/ppo_cartpole_reward.png)

---

## 13. Bonus C — ReAct LLM Agent (~100 行)

兩個工具：`calculator()` 與 `wiki_search()`；無 API key 也跑得起來。

```text
[USER]  What is sqrt(144) plus the year AlphaGo played Lee Sedol?
[AGENT] Thought: 需要 AlphaGo 年份。
        Action: wiki_search(AlphaGo)
[TOOL]  -> AlphaGo ... match versus Lee Sedol took place in March 2016 ...
[AGENT] Thought: 計算 sqrt(144) + 2016。
        Action: calculator(sqrt(144) + 2016)
[TOOL]  -> 2028.0
[AGENT] FinalAnswer: sqrt(144)=12 + 2016 = 2028.0
```

> 這個 100 行 loop = Part 3 ReAct → Toolformer → Gorilla → Claude Code 的最小版本。

---

## 14. Conclusion — 3 個轉折 + 5 個未來方向 + 倫理風險

**3 個轉折**
1. DRL 從 sub-field → foundation models 的對齊 / 推理元件（DeepSeek-R1）
2. flat policy → dual-system / hierarchy（Helix, GR00T N1, AlphaProof）
3. 「sim train, real fail」→ differentiable physics + foundation video model（Newton, V-JEPA 2）

**5 個未來方向**
World-Model RL on humanoids · RLVR for non-math domains ·
Cross-embodiment foundation policy · Agent reliability engineering · MARL+LLM 融合

**倫理風險**
- Reward hacking (UC Berkeley CRDI 2026 破解全部 8 個 agent benchmark)
- Humanoid 商用走在 formal safety cert 之前（Apollo / Figure 03 / NEO）
- Reproducibility crisis（AlphaChip / GNoME 2024 critique）

---

## 15. Q&A

Thanks for listening!

**Live demo:** [`docs/index.html`](docs/index.html)
**Full HTML report:** [`report/HW4_DRL_Survey.html`](report/HW4_DRL_Survey.html)
**Code:** [`code/ppo_demo.py`](code/ppo_demo.py)、[`code/llm_agent_demo.py`](code/llm_agent_demo.py)
**Artifacts:** [`artifacts/`](artifacts/)

References：100+ 篇（Nature, Science, NeurIPS/ICML/ICLR/CoRL/RSS/CVPR, arXiv 2024–2026）
