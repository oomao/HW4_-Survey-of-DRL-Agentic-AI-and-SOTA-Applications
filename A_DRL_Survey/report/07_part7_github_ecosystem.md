# Part 7 — GitHub / Open Source Ecosystem Survey

DRL 的迭代速度很大程度由開源 community 決定。本章梳理十個對 2024–2026 研究最有影響力的 GitHub 專案，每個都從 **主要用途 / 支援演算法 / 優勢 / 弱點 / 研究 vs 產業適用** 五個維度評估。

## 7.1 Stable-Baselines3 (SB3)
**Repo.** [DLR-RM/stable-baselines3](https://github.com/DLR-RM/stable-baselines3) — 12k+ stars。
**用途.** PyTorch 重寫的 OpenAI Baselines；學術界最被引用的 DRL library。
**演算法.** PPO, A2C, DQN, SAC, TD3, DDPG, HER。
**優勢.** 文件完整；**rl-baselines3-zoo** 提供 100+ 個 tuned hyperparameter；reproducibility 一流。
**弱點.** 不支援 distributed training；演算法保守，不追新 SOTA（無 DreamerV3 / MuZero）。
**適用.** **研究 baseline、教學、prototyping** 是首選；產業大規模 deployment 換 RLlib。

## 7.2 Ray RLlib
**Repo.** [ray-project/ray](https://github.com/ray-project/ray) — 33k+ stars（整個 Ray ecosystem）。
**用途.** 建構在 Ray 上的 distributed RL framework；UC Berkeley RISELab → Anyscale 商業化。
**演算法.** 30+ algorithm（PPO, APPO, IMPALA, SAC, DQN, R2D2, DDPG, MARL 如 QMIX / MADDPG / PPO-Centralized 等）。
**優勢.** Scalability 一流，能從單機擴到上千 CPU/GPU；產業級維護；MARL 支援好。
**弱點.** 抽象多、API 學習曲線陡；2.x → 3.x 大改動讓社群一度抱怨穩定性；單機快速實驗反而不順手。
**適用.** **產業大規模 DRL** 主流選擇；學術界與 SB3 互補。

## 7.3 CleanRL
**Repo.** [vwxyzjn/cleanrl](https://github.com/vwxyzjn/cleanrl) — 7k+ stars。
**用途.** **「每個演算法一個 single-file Python」** — 教學最高優先級的設計哲學。
**演算法.** PPO, DQN, C51, SAC, TD3, DDPG, RPO, Rainbow（單一檔案，無 OOP 包裝）。
**優勢.** 可讀性 SOTA；Weights & Biases 整合所有 benchmark；對 reproduce paper 結果極友善。
**弱點.** 沒有 high-level API 抽象；改架構需要修每個檔案；不支援 distributed。
**適用.** **學 DRL 內部機制**、複刻 paper、做教學的首選。

## 7.4 OpenAI Spinning Up
**Repo.** [openai/spinningup](https://github.com/openai/spinningup) — 11k+ stars。
**用途.** OpenAI 的「自學 DRL」教材包；提供 6 個演算法的 reference implementation + 教材。
**演算法.** VPG, TRPO, PPO, DDPG, TD3, SAC。
**優勢.** **教材品質歷史最佳**；公式推導 + code + 直覺三位一體。
**弱點.** 自 2020 後幾乎停止維護；Python 環境依賴老舊（TF1 + PyTorch 並存）；不會更新到新 SOTA。
**適用.** **入門教學 only**。產業界已轉用 CleanRL + SB3。

## 7.5 NVIDIA Isaac Gym → Isaac Lab
**Repo.** [isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab) — 5k+ stars（前身 Isaac Gym preview 已 EOL）。
**用途.** GPU-end-to-end 機器人 RL 框架；建構在 Isaac Sim (Omniverse) 上。
**演算法.** 透過 rl_games / skrl / SB3 整合（PPO 為主，加上 SAC, TRPO）；2024–25 推 Eureka / DrEureka。
**優勢.** **速度無人能敵**（2M env step/s on 8× RTX Pro 6000）；photorealistic rendering；NVIDIA GPU 生態。
**弱點.** 非 NVIDIA GPU 不支援；deformable / fluid 仍弱；Omniverse USD 學習曲線陡。
**適用.** Humanoid / quadruped / 機械手的學術與產業 SOTA。

## 7.6 CARLA
**Repo.** [carla-simulator/carla](https://github.com/carla-simulator/carla) — 13k+ stars。
**用途.** 開源都市自駕 simulator；建構在 Unreal Engine 上。
**演算法.** 任意 DRL（Gym/Gymnasium API），近年主流是 model-based RL + IL hybrid。
**優勢.** **唯一被廣泛採用的開源自駕 simulator**；社群活躍；CARLA Challenge 是業界共同 leaderboard。
**弱點.** Unreal 重，難以同時跑大量 env；sim2real gap 仍大；CARLA scenarios 與真實道路分布不完全重疊。
**適用.** 學術自駕 RL；產業界 PoC、regression testing。

## 7.7 Habitat Lab
**Repo.** [facebookresearch/habitat-lab](https://github.com/facebookresearch/habitat-lab) — 2k+ stars（加上 habitat-sim 約 5k+ stars）。
**用途.** Meta AI 的 embodied AI simulator；專做 navigation + manipulation。
**演算法.** PPO, DD-PPO（distributed PPO）, IL。
**優勢.** **室內具身導航的事實標準**；rendering 與物理速度極快（10000+ FPS headless）；HM3D 1000+ 棟真實住宅資料集。
**弱點.** 物理較弱（manipulation 不如 Isaac）；Linux only。
**適用.** Visual navigation、object/image/PointNav、social/HRI navigation。

## 7.8 FinRL
**Repo.** [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) — 11k+ stars。
**用途.** 哥大 Xiao-Yang Liu 團隊維護的金融 DRL 框架。
**演算法.** 透過 SB3 / ElegantRL / RLlib（PPO, SAC, A2C, DDPG, TD3）。
**優勢.** **唯一被廣泛採用的金融專用 DRL 框架**；提供 trading env + 教材 + leaderboard；2024 釋 FinRL-DeepSeek 結合 LLM signal。
**弱點.** 真實金融 non-stationarity 讓 sim-trained policy 在實盤打折；paper outperformance 須謹慎解讀。
**適用.** 學術交易策略研究、教學；產業仍以自家專屬 stack 為主。

## 7.9 MineDojo
**Repo.** [MineDojo/MineDojo](https://github.com/MineDojo/MineDojo) — 2k+ stars。
**用途.** NVIDIA + 學術界的 Minecraft open-ended benchmark；含 simulator + 730k YouTube + 7k wiki + 340k Reddit + MineCLIP。
**演算法.** 任意 DRL；常與 LLM agent 結合（Voyager、GITM、JARVIS-1）。
**優勢.** **目前唯一規模化的開放世界 embodied benchmark**；海量 unlabeled video 適合 foundation agent 驗證。
**弱點.** Java + Mod 環境複雜；Minecraft 與真實世界差距大；活躍維護減少。
**適用.** Open-ended agent 研究、終身學習、verifier-driven RL on creative tasks。

## 7.10 Unity ML-Agents
**Repo.** [Unity-Technologies/ml-agents](https://github.com/Unity-Technologies/ml-agents) — 18k+ stars。
**用途.** Unity 推出的 toolkit，把任何 Unity 場景變成 Gym-compatible env。
**演算法.** PPO, SAC, POCA（multi-agent）, BC, GAIL。
**優勢.** **對遊戲開發者最友善**；3D 資產 / 動畫 library 巨大；跨平台部署。
**弱點.** 物理不及 Isaac/MuJoCo；trainer 不及 RLlib；不適合大規模 distributed。
**適用.** 遊戲 NPC、教育示範、小規模 robotics（透過 Unity Robotics Hub 接 ROS）。

---

## 7.11 比較表

\begin{longtable}{p{2.3cm}p{4.0cm}p{3.7cm}p{3.5cm}}
\toprule
\textbf{Repo} & \textbf{核心定位} & \textbf{Strength} & \textbf{Weakness} \\
\midrule
SB3 & 學術 baseline & 文件完整、rl-zoo 100+ tuned & 單機；不追新 SOTA \\
RLlib & 產業 distributed RL & 30+ algorithms; scalable 上千 GPU & API 陡；版本不穩 \\
CleanRL & 教學單檔 & 可讀性 SOTA；W&B 整合 & 無 high-level API \\
Spinning Up & DRL 入門教材 & 教材歷史最佳 & 已停止維護 \\
Isaac Lab & GPU 機器人 RL & 2M env/s；photorealistic & NVIDIA only；學習曲線陡 \\
CARLA & 都市自駕 sim & 業界 leaderboard；社群活躍 & 重；sim2real gap \\
Habitat Lab & 室內具身導航 & 10000 FPS；HM3D dataset & 物理弱；Linux only \\
FinRL & 金融 DRL & 唯一金融專用主流框架 & 真實市場非穩態 \\
MineDojo & Minecraft 開放世界 & 海量 video；唯一 open-ended bench & Java + Mod 複雜 \\
Unity ML-Agents & Unity 遊戲 RL & 3D 資產豐富；跨平台 & 物理弱；不適合 distributed \\
\bottomrule
\end{longtable}

---

## 7.12 2025–2026 新興 Repo（值得追蹤）

| Repo | 出處 | 為什麼重要 |
|---|---|---|
| [openvla/openvla](https://github.com/openvla/openvla) | Stanford 2024 | 第一個 open-weights VLA |
| [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | Physical Intelligence | π0 系列開源 |
| [NVIDIA/Newton](https://github.com/NVIDIA/Newton) | NVIDIA + Google + Disney 2025 | Differentiable GPU physics |
| [google-deepmind/mujoco_playground](https://github.com/google-deepmind/mujoco_playground) | DeepMind 2025 | sim2real 6 平台 < 8 週 |
| [octo-models/octo](https://github.com/octo-models/octo) | Berkeley 2024 | Open transformer-based generalist robot |
| [eureka-research/Eureka](https://github.com/eureka-research/Eureka) | NVIDIA + UPenn 2024 | LLM-as-reward-designer |
| [rail-berkeley/serl](https://github.com/rail-berkeley/serl) | Berkeley 2024 | Real-world RL 25–50 min |
| [deepseek-ai/DeepSeek-R1](https://github.com/deepseek-ai/DeepSeek-R1) | DeepSeek 2025 | GRPO + RLVR 開源權重 |
| [modelcontextprotocol/specification](https://github.com/modelcontextprotocol/specification) | Anthropic + Linux Foundation 2024–25 | MCP — agent 工具標準 |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | LangChain 2024–25 | Stateful agent graph runtime |
