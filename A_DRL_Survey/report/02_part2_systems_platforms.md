# Part 2 — Survey of DRL Systems and Platforms

DRL 的進步從來不是只有演算法。一個能在 **單一 GPU 上每秒模擬數萬個機器人** 的 simulator、一個能在 **百萬時間步** 內收斂的 distributed trainer，往往才是論文背後真正的決勝點。本章節整理十個現代 DRL 系統，沿四個維度做比較：**系統架構 / 模擬環境 / 支援演算法 / 目標應用**，並指出每個系統的優勢與限制。

## 2.1 NVIDIA Isaac Gym / Isaac Sim / Isaac Lab

**架構。** Isaac Gym（2021 釋出）是 **GPU-end-to-end** 的機器人模擬器——physics simulation、observation rendering 與 RL training 全部在 GPU 上，不必走 CPU↔GPU 來回。一張 RTX 4090 可同時模擬數千到上萬個並行環境（envs），把 PPO 從「兩週」壓到「數小時」收斂。2023 年起 NVIDIA 推出 **Isaac Sim**（基於 Omniverse 的 photorealistic simulator）與 **Isaac Lab**（取代舊版 Isaac Gym 的學術用 RL 框架）；2024 年又跟 Google DeepMind、Disney 聯手發布 **Newton**——一個專為 robotics 設計的下一代 differentiable physics engine（建立在 NVIDIA Warp 上）。

**支援演算法。** PPO、SAC、TRPO（透過 rl_games / skrl / Stable-Baselines3 整合）；2024–2025 起 NVIDIA 大力推 **Eureka / DrEureka**（用 LLM 自動生成 reward function）與 **GR00T**（humanoid foundation model）。

**應用。** 四足機器人（ANYmal / Spot）、人形機器人（GR00T training, 1X NEO）、機械手（Allegro / Shadow Hand）、Sim2Real 的所有環節。

**優勢。** 速度無人能敵；photorealistic rendering；NVIDIA 的 GPU/CUDA 生態。**限制。** 對非 NVIDIA GPU 不友善；deformable / fluid 支援仍弱；學習曲線陡（Omniverse 的 USD 格式並不友善）。

## 2.2 Habitat Lab (Meta AI)

**架構。** Meta AI 開發的 **embodied AI** 模擬平台。Habitat-Sim 用 C++ + Bullet/Magnum 做 high-throughput rendering（10000+ FPS in headless mode），Habitat-Lab 是 Python 端的 RL/IL framework。2023 年釋出 **Habitat 3.0** 支援 humanoid avatar 和 human-robot interaction；2024 年 **Habitat-Matterport 3D Semantics (HM3D)** 提供 1000+ 棟真實住宅的 photorealistic 3D 掃描。

**支援演算法。** PPO、DD-PPO（distributed PPO）、imitation learning。

**應用。** Visual navigation（PointNav, ObjectNav, ImageNav）、language-guided navigation、mobile manipulation、social navigation。

**優勢。** **室內具身導航的事實標準**；rendering 與物理速度極快；資料集生態完整（MP3D、HM3D、Gibson、ReplicaCAD）。**限制。** 物理模擬不像 Isaac 那麼精準（足以做 navigation 但 manipulation 較弱）；以 Linux 為主。

## 2.3 CARLA

**架構。** 開源的都市自駕模擬器（Intel + CVC + Toyota Research），基於 Unreal Engine 4/5。提供完整的城市環境（CARLA Towns）、感測器（RGB、Depth、Lidar、Radar、IMU、GNSS）、可調節天氣、行人/車輛 NPC，以及 Python/C++ API。CARLA Leaderboard 是業界公認的端到端自駕 benchmark。

**支援演算法。** 任意 DRL 演算法（環境用 Gym/Gymnasium 包好即可）；近年大量出現基於 model-based RL（如 Latent World Models）與 imitation learning + RL hybrid 的工作。

**應用。** 自駕策略 / planning / control；多 agent driving；強化學習與規則式 planner 的對比。

**優勢。** **唯一被產業界廣泛採用的開源自駕模擬器**；社群活躍；CARLA Challenge 比賽提供共同 leaderboard。**限制。** Unreal 端 rendering 很重，難以同時跑大量 envs；sim2real gap 仍然大；CARLA scenarios 的 distribution 與真實道路不完全重疊。

## 2.4 Unity ML-Agents

**架構。** Unity 推出的開源 toolkit，讓任何 Unity 場景變成 Gym-compatible RL environment。架構分三層：**Unity scene + ML-Agents C# Behavior** → **Python low-level API (gRPC)** → **mlagents-learn trainer**（內建 PPO、SAC、POCA for multi-agent）。

**應用。** **遊戲 AI 訓練**（NPC 行為、難度調節）、教育示範、small-scale robotics（藉由 Unity Robotics Hub 整合 ROS）。

**優勢。** 對遊戲開發者最友善；3D 物件 / 動畫資產庫巨大；跨平台部署。**限制。** 物理模擬不及 Isaac/MuJoCo；trainer 不及 RLlib 強大；不適合大規模 distributed training。

## 2.5 Ray RLlib

**架構。** UC Berkeley RISELab → Anyscale 商業化。建構在 **Ray** distributed computing 上，提供 **rollout workers / learner workers / replay buffer** 抽象，能輕鬆從單機擴到上千 CPU/GPU。內建超過 30 種演算法的官方實作（PPO, IMPALA, APPO, SAC, DQN, DDPG, MARL 等）。

**應用。** 產業界的大規模 DRL 訓練；推薦系統、game AI、廣告 bidding；Anyscale 是目前最完整的 commercial DRL platform。

**優勢。** **scalability 一流**；演算法選擇齊全；產業級維護。**限制。** 抽象多、API 學習曲線陡；2.x → 3.x 大改動讓社群一度抱怨穩定性；單機快速實驗反而不如 SB3 / CleanRL 順手。

## 2.6 Stable-Baselines3 (SB3)

**架構。** PyTorch 重寫的 Stable-Baselines（OpenAI Baselines 的 fork）。設計哲學是 **single-machine、可讀性優先、reproducibility 優先**。提供 PPO、A2C、DQN、SAC、TD3、DDPG 等核心演算法，所有 baseline benchmark 與 hyperparameter 公開在 **rl-baselines3-zoo**。

**應用。** 研究 baseline、教學、小型產業 prototyping。

**優勢。** **學術界最被引用的 PyTorch DRL 庫**；文件完整；rl-zoo 提供了 100+ 個調好的 hyperparameter set。**限制。** 不支援 distributed training（單 GPU + 多 env 上限）；演算法保守（不追新 SOTA 如 DreamerV3）。

## 2.7 FinRL (AI4Finance Foundation)

**架構。** 哥倫比亞大學 Xiao-Yang Liu 團隊主導的開源金融 DRL 框架。三層架構：**FinRL-Meta**（金融資料 + 環境）→ **FinRL** （演算法層，基於 SB3 / ElegantRL / RLlib）→ **FinRL-Tutorials**（範例）。2024 年釋出 **FinRL-DeepSeek** 結合 LLM signal 與 DRL trader。

**應用。** 股票 / 加密貨幣 / 期貨的演算法交易、portfolio optimization、market making、order execution。

**優勢。** **唯一被廣泛採用的金融專用 DRL 框架**；提供 trading environments、tutorials、leaderboard；活躍維護。**限制。** 真實金融市場的 non-stationarity 讓 sim-trained policy 難以泛化；論文中的 outperformance 在實盤常打折扣。

## 2.8 MineDojo (NVIDIA + 學術界)

**架構。** Fan et al., NeurIPS 2022 [^fan2022minedojo]。在 Minecraft 之上建造的 open-ended embodied agent benchmark。三大資產：
1. **Simulator**（基於 MineRL，提供 thousands of 任務）；
2. **資料集**：730k YouTube 影片 + 7000+ Wiki 頁 + 340k Reddit posts；
3. **基礎模型 MineCLIP**：對齊 Minecraft 影片與文字描述。

**應用。** Voyager (Wang et al., NeurIPS 2023 [^wang2023voyager]) 在此上面驗證 LLM-driven lifelong learning；後續 GITM、JARVIS-1 等基於 MineDojo 做評估。

**優勢。** **目前唯一規模化的開放世界 embodied benchmark**；任務多樣性 + 海量 unlabeled video；極適合驗證 foundation agents。**限制。** Minecraft 本身的視覺/物理與真實世界差距大；setup 複雜（需要 Java + Mod 環境）。

## 2.9 OpenVLA (Stanford + Google DeepMind + Toyota Research, 2024)

**架構。** Kim et al., 2024 [^kim2024openvla]。**開源 Vision-Language-Action foundation model**，7B 參數，在 Open X-Embodiment 970k+ robot trajectory 上微調 Llama 2 + DINOv2/SigLIP visual encoder。輸出是 tokenized 7-DoF action sequence。

**支援演算法。** Primarily imitation learning + behavior cloning；可用 RL fine-tune（後續工作如 RLDP、PARL）。

**應用。** Multi-embodiment manipulation; benchmark 在 BridgeData-V2、LIBERO 等。

**優勢。** **首個 open-weights VLA**，打破 RT-2 的閉源壟斷；參數量適中（消費級 GPU 可微調）。**限制。** 在新 embodiment 上仍需 demonstration fine-tuning；推論 latency 對 high-frequency control 是挑戰；缺乏線上 RL 機制。

## 2.10 Microsoft AirSim / Project AirSim

**架構。** Microsoft Research 的開源無人機/車輛模擬器，建構在 Unreal Engine 上。提供 photorealistic environments、physics-based flight dynamics 與 multiple sensor modalities。**注意**：原 AirSim repo 已 archived（2022 年底），Microsoft 把後續開發轉到商業化的 **Project AirSim**（基於 Azure cloud）。社群 fork **Cosys-AirSim** 繼續維護開源版。

**應用。** UAV 自主飛行訓練、深度視覺 + RL 控制、CV pipeline 測試。

**優勢。** **學術界 UAV RL 的主要實驗平台**；豐富感測器；Multi-vehicle 支援。**限制。** 已停止官方開源維護是隱患；對沒用過 Unreal 的人 setup 不容易；rendering throughput 限制大規模並行訓練。

---

## 2.11 比較表

\begin{longtable}{p{2.8cm}p{3.6cm}p{3.2cm}p{3.6cm}}
\toprule
\textbf{平台} & \textbf{主要 simulator / 環境} & \textbf{支援演算法} & \textbf{目標應用} \\
\midrule
Isaac Lab / Sim & GPU end-to-end physics + photorealistic & PPO/SAC + Eureka, GR00T & Humanoid / 機械手 / quadruped \\
Habitat 3.0 & Photoreal 室內 3D 掃描 (HM3D) & PPO / DD-PPO / IL & 室內具身導航 + HRI \\
CARLA & Unreal-based 城市駕駛 & 任意 DRL (Gym API) + IL & 自駕、planning \\
Unity ML-Agents & 任意 Unity 場景 & PPO / SAC / POCA & 遊戲 AI、教學 \\
RLlib & 任意 Gym 環境 (Ray cluster) & 30+ 演算法 (含 MARL) & 大規模產業 DRL \\
Stable-Baselines3 & 任意 Gym 環境 (單機) & PPO / SAC / TD3 / DQN ... & 研究 baseline、教學 \\
FinRL & 金融資料 (股票/加密) & 透過 SB3/RLlib/ElegantRL & 演算法交易、portfolio \\
MineDojo & Minecraft + 多模態資料 & 任意 + LLM agent & 開放世界 / 終身學習 \\
OpenVLA & Open X-Embodiment 資料集 & IL（可 RL fine-tune） & 多 embodiment manipulation \\
AirSim & Unreal 無人機 / 車輛 & 任意 DRL (Gym API) & UAV、autonomous driving \\
\bottomrule
\end{longtable}

---

[^fan2022minedojo]: Fan, L. et al. "MineDojo: Building open-ended embodied agents with internet-scale knowledge." *NeurIPS Datasets and Benchmarks Track* (2022).
[^wang2023voyager]: Wang, G. et al. "Voyager: An open-ended embodied agent with large language models." *arXiv:2305.16291* (2023).
[^kim2024openvla]: Kim, M. J. et al. "OpenVLA: An open-source vision-language-action model." *arXiv:2406.09246* (2024).
