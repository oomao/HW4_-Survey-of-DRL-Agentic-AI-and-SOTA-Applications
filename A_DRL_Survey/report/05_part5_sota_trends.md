# Part 5 — SOTA Research Trends (2025–2026)

把 Part 1–4 收斂起來看，可以找出 **十條** 2025–2026 真正在推進 DRL 與 agentic AI 邊界的研究 trend。本章對每條 trend 解釋 **為什麼重要 / 當前限制 / 未來方向**。

## 5.1 Embodied AI

**為什麼重要。** 從 ChatGPT 之後，業界普遍相信 AI 的下一個 frontier 在 **physical world**——能拿東西、能在你廚房做菜、能去 Mercedes 工廠搬箱子。2025 年的代表事件：
- Figure 03（Oct 2025）以 12k units/年產能設計；
- Apptronik Apollo 拿 $520M，$5B 估值；
- 1X NEO 開放消費市場（$499/月訂閱）；
- Tesla Optimus Gen 3 demo kung-fu / 烹飪。

**當前限制。** (1) **資料稀缺**：Open X-Embodiment 1M+ trajectory 在 LLM 資料尺度上只是「打底」；(2) **長時域 reliability**：示範影片漂亮，反覆 trial 的 pass^k 仍低；(3) **安全認證**：沒有 humanoid 取得 unstructured home deployment 的 formal safety cert。

**未來方向。** 大規模 teleop fleet（特斯拉、Figure）+ 人類影片監督（HumanPlus、V-JEPA 2）+ differentiable simulator + dual-system architecture，是接下來 3–5 年的工程主軸。

## 5.2 World Models

**為什麼重要。** World model 是讓 agent 「在腦中想像 → 規劃 → 行動」的核心。2024–2025 三個並行突破：
- **DreamerV3** (Nature April 2025)：第一個用單一 hyperparameter 跨 150+ 任務、且從零挖到 Minecraft diamond 的演算法。
- **Genie 2 → Genie 3** (2024 Dec / 2025 Aug)：DeepMind 從 2D playable 推到 720p 24 fps 多分鐘 consistent 的 interactive world，已釋出 "Project Genie"（2026 Jan）。
- **V-JEPA 2** (Meta Jun 2025)：1.2B params 在 1M 小時影片 + 62 小時 robot data 上訓練，zero-shot pick-and-place 65–80%；比 NVIDIA Cosmos 快約 30×。

**當前限制。** Sora-style video model 的 cause-and-effect 仍弱（會 hallucinate 不合物理）；Genie 3 有 10 秒級 short-term memory；V-JEPA 走 embedding-space prediction，對 fine control 不夠直接。

**未來方向。** World model + RL outer loop（用 world model 當 imaginary env，把 RL data efficiency 推上幾個量級）是 2026–2027 預期突破點；differentiable physics（Newton、MJX）會強化這條路。

## 5.3 Multi-agent RL（MARL 與 LLM agent 的融合）

**為什麼重要。** 真實場景幾乎沒有 single-agent — 自駕、生產線、市場、社交都是 multi-agent。經典 MARL（QMIX、MAPPO、CTDE 家族）解 cooperative 與 zero-sum 已有成果；但 **LLM 多 agent**（MetaGPT、CrewAI、AutoGen）給了新的可能性：以自然語言為通訊媒介、以 role 為分工。

**當前限制。** (1) MARL 對於異質 reward / state / action space 的 multi-task 擴展仍開放；(2) LLM agent 群組缺少 MARL 嚴格的 credit assignment；(3) 兩條路線**還沒有像 LLM + RL 那樣的成功融合典範**。

**未來方向。** Population-based training（AlphaStar 風格）套到 LLM agent；RLAIF 形式的 group reward；MARL 中嵌入 LLM 提案層。SIMA 2 的 group self-play 是早期 prototype。

## 5.4 Offline RL

**為什麼重要。** 機器人、醫療、金融、自駕的真實場景**不能 online try-and-error**，只能從歷史 dataset 學。Offline RL（BCQ / CQL / IQL / Decision Transformer）讓「從 log 學 policy」變成可行。

**當前限制。** (1) Distribution shift 仍是核心難題；(2) 上限受限於 behavior policy 覆蓋；(3) **缺少 well-known benchmark 之外的真實成功案例**——D4RL/Atari/RoboMimic 之外，產業界 deployment 仍少。

**未來方向。** Offline-to-online fine-tuning（先 offline、再小量 online 修正）、與 VLA fine-tuning 結合（用 RL 修 imitation policy 的 reliability tail）。

## 5.5 Diffusion Policy

**為什麼重要。** 機器人示範資料天生 multimodal（同個 sub-goal 可有多種完成方式），Gaussian policy 容易塌縮。Chi et al. (RSS 2023, IJRR 2025) 的 **Diffusion Policy** 用 conditional denoising 自然表達多峰，+46.9% over 先前 SOTA across 12 任務。

**當前限制。** (1) 推論 latency 高（多步 denoising）；(2) cross-embodiment transfer 不佳；(3) 對 reflective / transparent objects（DP3 依賴 depth）效果差。

**未來方向。** Distillation 把多步 diffusion 壓成 single-step（consistency models）；flow matching 路線（π0）；與 VLA 整合（OpenVLA 仍是 discrete token，DP-style continuous output 是改進空間）。

## 5.6 Foundation Agents

**為什麼重要。** 從 specialist policy 轉向 **「一個 model 跨多任務、多 embodiment、多 modality」**。代表：
- **Magma** (CVPR 2025)：同時做 UI 與 robot manipulation；
- **GR00T N1**：首個 open humanoid foundation model；
- **SIMA 2**：跨多款 3D game 的 generalist；
- **Voyager**：用 LLM 當 in-context RL 的 outer loop；
- **Octo / CrossFormer**：多 embodiment robot policy。

**當前限制。** (1) Per-task specialist 仍打贏 foundation agent（trade-off 仍在）；(2) 缺乏 well-defined evaluation 跨領域；(3) 訓練成本急速上升。

**未來方向。** 統一的 action space tokenization（OpenVLA 風格的 discrete token、或 π0 的 flow continuous）；more compute → emergence；foundation agent + 在 deployment 端做 RL personalization。

## 5.7 Robotics Foundation Models

**為什麼重要。** 與 5.6 重疊但聚焦 robotics — 2024–2025 是 robotics 自己的「BERT moment」：
- **OpenVLA** (2024)：第一個 open VLA。
- **π0 / π0.5** (2024–25)：高頻 continuous control 突破。
- **Helix** (Feb 2025)：dual-system 上 embedded GPU。
- **GR00T N1** (Mar 2025)：NVIDIA open humanoid FM。
- **Gemini Robotics 1.5** (Sep 2025)：加入 agentic tool use；部署 Apollo。

**當前限制。** (1) Latency vs capability tradeoff（VLA 越大越聰明，越大延遲越高）；(2) Data scarcity；(3) Per-embodiment generalization 仍弱；(4) LIBERO-PRO 揭示 benchmark memorization 問題。

**未來方向。** Dual-system 標準化、heterogeneous co-training（web + verbal + 多 robot）、與 world model 整合。

## 5.8 Sim2Real Transfer

**為什麼重要。** 真實機器人訓練昂貴、危險、慢；模擬器訓便宜、安全、快百萬倍。**Sim2Real gap 是這條 pipeline 的決勝點**。

**2025 重要事件**：
- **Newton physics engine** (NVIDIA + Google + Disney, GTC 2025)：open-source、GPU-accelerated、differentiable，**humanoid 70× 加速、in-hand manipulation 100×**。
- **MuJoCo MJX + Playground** (Feb 2025)：JAX-native，sim2real 到 6 個 robot 平台只花 < 8 週。
- **DrEureka** (RSS 2024)：LLM 同時自動生成 reward 與 domain randomization 參數。
- **ASAP** (2025)：sim-pretrain + delta-action residual model 補 sim2real gap，可達 agile parkour。

**當前限制。** Contact-rich / deformable / fluid 仍是 simulator 的短板；vision sim2real 仍需 photorealistic rendering（如 Cosmos、Omniverse）。

**未來方向。** Differentiable physics 直接讓 gradient 穿過 simulator；real-data residual learning（ASAP）；foundation video generator + RL（V-JEPA 2、Sora-style）。

## 5.9 Autonomous Scientific AI

**為什麼重要。** AI 不只是工具，而是 **科學家本身**——這是 AGI 最具體的試金石。代表：
- **Coscientist** (Nature 2023)：GPT-4 agent + 真實實驗室，做 Pd-catalyzed coupling。
- **A-Lab** (Nature 2023)：自主合成 GNoME 提案的 41 個材料 / 17 天。
- **AlphaProof + AlphaGeometry 2** (Nature 2025)：IMO 2024 銀牌（28/42）。
- **AI Scientist v2** (Sakana, Apr 2025)：**首篇 AI-authored paper 通過 ICLR 2025 workshop peer review**。

**當前限制。** (1) Literature synthesis 仍弱；(2) Novelty 多為 surface-level；(3) Reproducibility crisis（GNoME / AlphaChip 都受 2024 critique）；(4) 缺少 cross-discipline 通用 verifier。

**未來方向。** 封閉迴圈 hypothesis → experiment → analysis → next hypothesis 全自動；以 RL 在 verified scientific reward 上 self-improve；多 modality scientific agent（看 PDF + 跑 sim + 操 instrument）。

## 5.10 RL + Transformers

**為什麼重要。** 兩條融合線：

**A. Transformer 當 policy 架構**（policy as sequence model）
- **Decision Transformer / Trajectory Transformer**（NeurIPS 2021）
- **Gato**（DeepMind 2022）：一個 transformer 玩 Atari + 寫字 + 操作 Sawyer 機械手 + 對話
- **Octo / OpenVLA / π0 / GR00T**：robotics 領域全部 transformer-based

**B. RL 訓練 Transformer policy（用 RL 做後訓練）**
- RLHF / RLAIF / DPO / KTO 訓 LLM
- RLVR（DeepSeek-R1 / o1）訓 reasoning model
- GRPO（DeepSeek 提）取消 critic 降低訓練成本

**當前限制。** (1) Transformer 的計算成本對 high-frequency control 是負擔；(2) RL post-training 對 base model 的依賴強（pre-training 沒覆蓋的能力，RL 很難「無中生有」）；(3) 缺少 standardized RL+Transformer benchmark。

**未來方向。** Mamba/SSM 等線性序列 model + RL；長時域 token-by-token planning；test-time RL（在 inference 時繼續學）。

---

## 5.11 五條趨勢的交叉骨架

以上十條 trend 互相關聯，可以收斂成 **五條主軸**：

```
1. Foundation Models 與 RL 的融合
   - LLM/VLM 提供 prior, RL 提供 alignment + reasoning
   - 代表：RLHF, RLAIF, DPO, RLVR, GRPO; SIMA 2, AI Scientist v2

2. Embodied generalist agent
   - Single model 跨 task / embodiment / modality
   - 代表：OpenVLA, π0.5, GR00T N1, Magma, Gemini Robotics 1.5

3. Sim2Real + Differentiable Physics
   - GPU-accelerated photorealistic sim, 梯度可穿過 simulator
   - 代表：Newton, MJX, Isaac Lab 4.x, DrEureka

4. World Model + Imagined Planning
   - 在 agent 腦中模擬世界做 planning
   - 代表：DreamerV3 (Nature 2025), Genie 3, V-JEPA 2

5. Verifier-Driven RL
   - Formal proof / code execution / sim 作為可驗證 reward
   - 代表：DeepSeek-R1, AlphaProof, AlphaGeometry 2, AlphaDev
```

這五條主軸構成 2025–2026 DRL 與 agentic AI 的「全景」，下一階段的突破很可能來自**它們的交叉點**（如 world-model RL on humanoid、verifier-driven scientific agent）。
