# Part 6 — Comparative Analysis

下面以五個代表性演算法做橫向比較。除了題目要求的 strength / weakness / sample efficiency / real-world usage 四維，再額外加入 **policy type、on/off policy、planning vs model-free、典型 wall-clock 與是否仍是 SOTA baseline** 等資訊以增加 analytical depth。

## 6.1 五法概覽表

\begin{longtable}{p{1.7cm}p{2.4cm}p{3.0cm}p{3.0cm}p{1.7cm}p{3.0cm}}
\toprule
\textbf{演算法} & \textbf{類型} & \textbf{Strength} & \textbf{Weakness} & \textbf{Sample Eff.} & \textbf{Real-world Usage} \\
\midrule
DQN & Value-based / off-policy / discrete & Atari benchmark 元祖、簡單、replay 與 target net 變所有 DQN 系列基石 & $\max$ 造成 overestimation；連續動作不可用；訓練不穩 & 中（off-policy、replay） & 推薦系統、廣告 bidding、教學示例；產業已大量被 Rainbow / PPO 取代 \\
\midrule
PPO & Policy-based / on-policy & 實作簡單、超參魯棒、離散 / 連續通用；**LLM RLHF 事實標準** & on-policy 因此 sample-inefficient；需大量並行 envs；對 advantage normalization 等實作細節敏感 & 低 & RLHF (GPT/Claude/Gemini)、Dota 2/OpenAI Five、自駕、Isaac Lab humanoid RL \\
\midrule
SAC & Actor-critic / off-policy / continuous & 連續控制 SOTA baseline；entropy 鼓勵探索；temperature 可自動調；穩 & 連續動作專屬；需要 twin critic ensemble；實作較 PPO 複雜 & 高 & 機械手、四足 / 人形 locomotion (Berkeley G1 15 min)、UAV、自駕；SERL 在真實機器上 25-50 分訓出 PCB 組裝 \\
\midrule
MuZero & Model-based / planning + RL & 同一套架構解 board games + Atari；不需已知環境模型；極高 sample efficiency & 工程複雜（MCTS + reps learning）；對 stochastic env 較弱；訓練成本高 & 高（learned model） & DeepMind 內部（video compression, search）、學術 model-based RL 標竿；產業少見 \\
\midrule
Decision Transformer & Sequence model（無 RL update） & 把 offline RL 變為純 supervised；天然支援 multi-task return-conditioning；Transformer scaling laws & Stitching 差於 DP-based offline RL；對 OOD return target 敏感；需大量資料 & 中（offline，與資料量呈正比） & VLA 系列（Gato / Octo / OpenVLA / GR00T）的概念祖先；offline RL benchmarks \\
\bottomrule
\end{longtable}

## 6.2 深度討論

### 6.2.1 為什麼 PPO 變成「萬用 baseline」？

PPO 並不是任一單一指標最好的演算法 — sample efficiency 不如 SAC、planning 不如 MuZero。但它在 **「實作 / 超參 / on-policy 規模化 / 離散+連續通用 / 對 reward scale 魯棒」** 五個維度同時及格。當你的任務是 (a) sim 可以大量並行、(b) 需要 RL 對齊預訓 model（如 RLHF），PPO 幾乎是 default choice。**它的最大競爭者是 GRPO**（DeepSeek 提出，取消 critic 改用 group 標準化 advantage）— 在 LLM 推理 RL 上 GRPO 已逐漸取代 PPO。

### 6.2.2 為什麼 SAC 在連續控制這麼穩？

三個原因：(1) off-policy → replay → sample efficient；(2) twin Q + clipped target → 抑制 overestimation；(3) maximum entropy → 自然探索 + 對多模態最優解友善。SAC 在學術 benchmark 通常打贏 PPO，但 sim2real 部署時 PPO 仍常被選 — 因 PPO 在大規模 distributed 訓練更可預測、不易 critic 過擬合。

### 6.2.3 MuZero 為什麼沒在產業界遍地開花？

工程上 MuZero 很重 — 同時學三個 head（policy / value / reward）+ MCTS + representation。當 simulator 便宜（如 Atari、棋類），model-free 的 R2D2 / Rainbow / Muesli 已夠強；當需要 model-based 帶來的 sample efficiency，DreamerV3 反而更輕量、且在 Minecraft / DMControl 上 SOTA。**MuZero 是漂亮的學術里程碑，但 DreamerV3 是更實用的工程繼承者**。

### 6.2.4 Decision Transformer 開啟了什麼？

DT 證明 **「offline RL 可以是純 supervised learning」**，把 RL 變成 sequence modelling，這個 framing 直接導致：
- **Gato**（DeepMind 2022）：一個 transformer 跨 600+ 任務
- **Octo / OpenVLA / GR00T**：robotics VLA 全部 transformer-based、全部 IL-as-sequence-modeling

不過 DT 也有底層缺陷：缺乏 dynamic programming 的 **stitching** 能力（從 sub-optimal 段落拼最優），所以在純 offline benchmark 上常輸 CQL / IQL。實務上 DT-like 架構通常配 RL fine-tuning 補足。

### 6.2.5 哪種演算法選哪種任務？

| 任務情境 | 推薦演算法 | 理由 |
|---|---|---|
| Atari / 離散決策 | Rainbow DQN / Muesli | 已是 model-free SOTA |
| 連續控制（學術 benchmark）| SAC / TD3 | sample efficient |
| 大規模分散式（Dota/StarCraft） | PPO + League | 簡單可預測 |
| LLM RLHF / RLAIF / RLVR | PPO / GRPO + DPO/KTO | 事實標準 |
| Board games / 棋類 | AlphaZero / MuZero | self-play + MCTS |
| 開放世界 (Minecraft / DM Control) | **DreamerV3** | 單一 hyperparam 跨任務 |
| Offline RL（醫療 / log）| IQL / CQL / DT | OOD-safe |
| Robot manipulation（demonstration 豐富） | Diffusion Policy / OpenVLA | multimodal continuous |
| Robot manipulation（real-world fast）| SERL (RLPD) | 25–50 分鐘從零 |

### 6.2.6 趨勢圖

```
DQN (2013)
  └─→ Double DQN (2016) ── Dueling (2016) ── PER (2016) ── Distributional C51 (2017) ── Rainbow (2017) ── Muesli (2021)
                                                                                          │
                                              ┌───────────────────────────────────────────┘
                                              ▼
A3C (2016) ─→ A2C (2016) ─→ PPO (2017) ─→ IMPALA (2018) ─→ V-trace ────────┐
                                                                            ▼
                                                                       RLHF / DPO / GRPO (2023–25)
DDPG (2015) ─→ TD3 (2018)                                                   │
            ─→ SAC (2018) ─→ SAC-X / DrQ-v2 / SERL ─→ DrEureka (2024)       │
                                                                            ▼
AlphaGo (2016) ─→ AlphaGo Zero (2017) ─→ AlphaZero (2018) ─→ MuZero (2020) ─→ DreamerV3 (2025)
                                                              │                  │
                                                              └─→ AlphaTensor / AlphaDev / AlphaProof
Decision Transformer (2021) ─→ Gato (2022) ─→ Octo / OpenVLA / π0 / GR00T N1 (2024–25)
```

這張圖揭示 2025–2026 三條演化主線：(1) policy 從 model-free 走向 model-based / world-model 路線；(2) sequence modelling 已成為 robotics policy 的主流架構；(3) 所有 SOTA 演算法的「外圍」都被 LLM / foundation model 包覆。
