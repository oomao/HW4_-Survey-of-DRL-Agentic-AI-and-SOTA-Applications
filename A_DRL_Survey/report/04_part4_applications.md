# Part 4 — DRL Applications in Different Research Domains

本章選擇三個 2024–2026 進展最快、最能反映 DRL 與 foundation models 整合的應用領域，逐一分析：(a) **問題定義**、(b) **為什麼 DRL 有用**、(c) **SOTA 系統**、(d) **代表論文與分析**、(e) **資料集 / simulator**、(f) **未來方向**。

## 4.1 Robotics 與 Embodied AI

### 4.1.1 問題定義

Robotics 涵蓋 humanoid locomotion、bimanual manipulation、mobile manipulation、HRI 等子任務。Embodied AI 進一步要求 agent 在具身（embodied）的感知 → 推理 → 行動迴圈中與環境互動，常見任務是 navigation、object rearrangement、language-instructed manipulation。這是一個 high-dim continuous control + partial observability + long horizon + sparse reward 同時存在的任務家族。

### 4.1.2 為什麼 DRL 有用

- **高維連續控制**：對 humanoid 而言一次決策要輸出 30–60 維 torque/joint position，超出傳統 MPC 即時可解的範圍；off-policy DRL（SAC、TD3）與 on-policy（PPO + 大量並行 envs）能直接 end-to-end 學。
- **泛化性**：用 randomization 訓出的 policy 可以橫跨數千個變體；imitation learning 雖然準，但對新場景的 fallback 不如 RL。
- **與 foundation model 互補**：VLM 提供高層 semantic（這是什麼物件、目標在哪），RL/IL 提供低層 reactive control（如何接觸、力道多大）。

### 4.1.3 SOTA 系統（2024–2026）

| 類別 | 代表系統 | 年份 | 機構 | 一句話 |
|---|---|---|---|---|
| **VLA Foundation Model** | **OpenVLA** [^kim2024openvla] | 2024 | Stanford+Berkeley+TRI+DeepMind+PI | 第一個 open-weights VLA；7B params；+20.4% over Diffusion Policy |
| | **π0 / π0-FAST / π0.5** [^pi2024pi0] | 2024–25 | Physical Intelligence | flow-matching 50 Hz；π0.5 能清掃「**完全沒見過的廚房**」 |
| | **Helix** [^figure2025helix] | 2025 | Figure AI | **dual-process** S2 (7-9 Hz VLM) + S1 (200 Hz visuomotor) |
| | **GR00T N1** [^nvidia2025groot] | 2025 | NVIDIA | 首個 open humanoid FM；63.9 ms latency on L40 |
| | **Gemini Robotics / 1.5** [^deepmind2025geminirobotics] | 2025 | Google DeepMind | 驅動 Apptronik Apollo；加入 agentic tool use |
| | **Magma** [^magma2025] | 2025 | Microsoft | 同時做 digital UI + physical manipulation |
| **Imitation / Diffusion Policy** | **Diffusion Policy** [^chi2023dp] | 2023 | Columbia | conditional denoising 處理 multimodal action；+46.9% over prior SOTA |
| | **DP3 (3D)** [^ze2024dp3] | 2024 | Stanford | point cloud + diffusion；40 demo 達 85% real success |
| | **Mobile ALOHA** | 2024 | Stanford | $32k 雙臂全身 teleop；做飯、清潔 |
| | **Octo / CrossFormer** [^team2024octo] | 2024 | Berkeley | 開源 800k OXE transformer；單一 model 多 embodiment |
| **RL on Real Robot** | **Eureka / DrEureka** [^ma2024eureka] | 2024 | NVIDIA+UPenn | LLM 寫 reward function；80%+ 任務超越人工 |
| | **SERL** [^luo2024serl] | 2024 | Berkeley | real-world RL 25–50 分鐘訓出 PCB / 線材組裝 |
| **Humanoid WBC** | **HumanPlus** | 2024 | Stanford | RGB 影片 shadowing |
| | **OmniH2O** [^he2024omniH2O] | 2024 | CMU LeCAR | VR + voice + RGB；GPT-4 autonomy |
| | **ASAP** [^he2025asap] | 2025 | CMU+NVIDIA | sim-pretrain + delta-action residual 補 sim2real |
| **快速 RL on G1** | arXiv:2512.01996 | 2025 | UC Berkeley | RTX 4090 上 15 min 訓出 Unitree G1 locomotion |

### 4.1.4 代表性論文分析

**OpenVLA (2024)** 重要性在於**打破 RT-2 的閉源壟斷**。Stanford 用 Llama 2 + SigLIP/DINOv2 在 970k Open X-Embodiment trajectory 上訓出 7B model，並把 action tokenize 成 7-DoF 離散 token。LoRA fine-tune 即可在新 embodiment 上適配，4-bit quantization 仍保留性能。**Critical view**：5 Hz inference latency 對高頻 dexterous control 仍是瓶頸（這也是後續 dual-system 出現的原因），且離散 action token 對精細力控限制大。

**π0.5 (Apr 2025)** 是首個能在「**完全未見過的真實住家**」做開放性任務（如清潔廚房 / 整理臥室）的 VLA — 不是 demo 而是反覆 trial 的成功率。技術上靠 hierarchical reasoning（用 VLM 規劃 sub-goal）+ heterogeneous co-training（web data + verbal instructions + 多機器人資料）。**Critical view**：成功率仍非可商業部署等級（特定任務 60–80%）；長時域失敗仍主流。

**Helix (Feb 2025)** 的工程意義很大：在 embedded GPU 上跑完整 dual-process 架構，**S2 跑 7–9 Hz 做語意 / 規劃、S1 跑 200 Hz 做 visuomotor**，控制 Figure 02 的 35 DoF — 證明 dual-system 不是學術點子，能放到出貨機上。

### 4.1.5 資料集與 Simulator

- **資料**：Open X-Embodiment（1M+ traj, 22 embodiments, 2024 Google + 21 機構聯盟）、DROID（76k demos, 564 scenes, RSS 2024）、Mobile ALOHA dataset、BridgeData-V2、RoboCasa 100 廚房任務。
- **Simulator**：Isaac Lab（GPU end-to-end，2025 推 4.x）、Isaac Sim、MuJoCo MJX（JAX-native, differentiable, 2025）、ManiSkill3（SAPIEN backend, 2024）、Habitat 3.0（室內 navigation）、RLBench、CALVIN、LIBERO、Newton（2025 NVIDIA + Google + Disney）。
- **數字**：Isaac Lab 在 8× RTX Pro 6000 跑 humanoid RL 達 **2M env step / sec**，manipulation 達 900k FPS。

### 4.1.6 未來方向

1. **Dual-system architecture 標準化**：S2 (VLM, 5–10 Hz) + S1 (visuomotor, 100–200 Hz) 已成 Helix / GR00T N1 / Gemini Robotics 1.5 共識。
2. **World-model + VLA 整合**：V-JEPA 2、1XWM 嘗試把 world model 變成 robot 的 imagination engine。
3. **Sim2Real with differentiable physics**：Newton + MJX 推動「梯度可穿過 simulator」。
4. **Verifier-driven robot RL**：類似 RLVR 在 LLM 推理上的成功，下一步是怎麼為 manipulation 設計 reliable verifier。
5. **資料 scaling**：1M trajectory 仍只是 LLM 訓練資料的 < 1%，需要更便宜的 teleop / 影片監督路線（HumanPlus、ASAP）。

---

## 4.2 Game AI

### 4.2.1 問題定義

Game AI 涵蓋 perfect-information board games（圍棋、西洋棋）、imperfect-information games（撲克、Diplomacy）、realtime competitive video games（StarCraft、Dota、GT 賽車）、open-world creative games（Minecraft）。共同挑戰：**長時域 credit assignment、多 agent 競合、龐大狀態空間、稀疏 reward**。

### 4.2.2 為什麼 DRL 有用

- Self-play 提供 **automatic curriculum** — 對手隨自己變強，永遠在學區邊緣。
- 棋類遊戲的 **可驗證 reward**（勝負）讓 RL 可以遠超 supervised learning（後者受限於人類 demonstration 的上限）。
- 多 agent setting 中 **Nash equilibrium / 子博弈完美 equilibrium** 提供漂亮的理論 grounding。

### 4.2.3 SOTA 系統 (Lineage Map)

```
2016  AlphaGo (Nature) — human-data + RL self-play + MCTS
2017  AlphaGo Zero (Nature) — tabula rasa
2018  AlphaZero (Science) — generalized to chess/shogi
2019  AlphaStar (Nature) — StarCraft II Grandmaster, League training
2019  OpenAI Five (Dota 2) — PPO + 128k CPU
2020  MuZero (Nature) — learned latent dynamics
2022  Cicero (Science) — Diplomacy + LLM dialogue
2022  DeepNash (Science) — Stratego, model-free Nash (R-NaD)
2022  Gran Turismo Sophy (Nature) — beat human champions, QR-SAC
2023  Voyager (NeurIPS) — Minecraft LLM agent, no gradient RL
2024  AlphaGeometry (Nature) — IMO geometry
2024  SIMA (DeepMind) — 9 commercial 3D games, generalist
2024  Tearing-instability avoidance (Nature) — DIII-D plasma control
2025  DreamerV3 (Nature) — first to mine diamonds **from scratch**
2025  SIMA 2 (Dec 2025) — Gemini-powered, self-improving in 3D
2025  AlphaProof + AlphaGeometry 2 (Nature, Nov) — IMO 2024 silver, 28/42
```

### 4.2.4 代表性論文分析

**AlphaStar (Nature 2019) [^vinyals2019alphastar]**. 第一次在 realtime imperfect-information game 中達 Grandmaster。架構結合 (a) 971k 人類 replay 的 supervised imitation、(b) transformer + pointer network、(c) **League training** — 主 agent 與 main-exploiter / league-exploiter 共同演化以避免 strategy cycling。**Critical view**：APM 與 camera 限制曾受爭議；對 OOD 的人類策略仍脆弱；訓練成本約 $10M。**啟示**：純 RL on Pong 行得通，但要打複雜遊戲，supervised init + population-based 是必要的。

**MuZero (Nature 2020) [^schrittwieser2020muzero]**. 真正把 model-based RL 帶到實用層級。核心是 learning a **value-equivalent** latent dynamics model — 不必預測完整 next-state pixels，只預測「對 policy / value 有用」的潛在表徵。同一套架構打敗 AlphaZero（棋類）+ R2D2（Atari）。**Critical view**：訓練成本高；對 stochastic env（如撲克）不擅長；模型本身非 interpretable。

**DreamerV3 (Nature April 2025) [^hafner2025dreamerv3]**. **第一個用單一 hyperparameter config 解 150+ 任務的演算法**，且首次「從零開始」（無 human data）在 Minecraft 挖到鑽石（~30M env steps）。技巧：Recurrent State-Space Model + categorical latents + symlog squashing — 處理不同 reward / observation scale 的關鍵。**Critical view**：訓練 wall-clock 仍以天計；無法像 VPT 那樣利用 YouTube 影片。

**AlphaProof + AlphaGeometry 2 (Nature Nov 2025) [^deepmind2025alphaproof]**. IMO 2024 拿銀牌（28/42 分），解了 6 題中的 3 題，包括 Q6（人類只有 5 位解出）。**AlphaProof**：用 Lean formalize，AlphaZero-style RL 在百萬 auto-formalized 題目上訓練。**AlphaGeometry 2**：神經符號 hybrid — LLM 提案輔助線，symbolic engine 驗證，比 v1 快 100×（IMO 2024 Q4 在 19 秒內解出）。**Critical view**：combinatorics 仍未解；formalization 仍是瓶頸；難 transfer 到研究級數學。

**SIMA 2 (Dec 2025) [^sima2025v2]**. 用 Gemini 驅動的 self-improving 3D 遊戲 generalist。最關鍵的創新是 **self-play loop 使用 Gemini-generated reward** — 在新 env 不靠人類設計 reward，靠 LLM judge。約是 v1 兩倍成功率，trained env 接近人類。**Critical view**：長時域規劃仍弱、精細運動仍弱、evaluation 限於 DeepMind 自選 game。

### 4.2.5 資料集 / Simulator

- **棋類**：AlphaZero 用自己的 self-play；無外部 dataset。
- **StarCraft / Dota**：人類 replay 資料集 + 自家 simulator。
- **Minecraft**：MineDojo（NeurIPS 2022）— simulator + 730k YouTube 影片 + 7k wiki page + 340k Reddit；VPT 用 contractor 標註 → IDM → 70k 小時 unlabeled video。
- **GT 賽車**：Sony PlayDriver simulator（內部）。
- **數學**：Lean 4 mathlib（百萬 formalized 定理）。

### 4.2.6 未來方向

1. **Foundation agent for games**：SIMA 2 的 self-improving loop 是雛形；目標是跨遊戲、跨遊戲類型的單一 model。
2. **Verifier-driven scientific game**：把 IMO 推理 transfer 到實際定理（millennium prize 級別）。
3. **Open-ended creative game AI**：Voyager 開頭、SIMA 2 接力，但「無限發明新任務」仍未真正解決。
4. **多模態 game agents**：把語音 / 視訊 / 鍵盤 / mouse 視為通用 action space，向 SIMA / Helix-style 收斂。

---

## 4.3 AI for Science

### 4.3.1 問題定義

科學發現的核心活動：(1) 大空間搜尋（化合物、材料、theorem、algorithm），(2) 多 step decision under uncertainty（實驗該做哪個 / 該量哪個量），(3) 高成本驗證（合成、實驗、formal proof）。這恰好對應 RL 的核心結構：long-horizon decision、稀疏但可驗證的 reward。

### 4.3.2 為什麼 DRL 有用

- **Verifiable reward**：許多科學問題有可驗證的成功訊號（化合物的 binding affinity、formal proof 的 Lean check、algorithm 的執行時間），這正是 RLVR 的理想場景。
- **跟人類昂貴的試錯比優勢**：模擬器內 trial 便宜（毫秒），把人類數年研究壓縮到數天。
- **Foundation model + RL outer loop 已成主流範式**：LLM 提案、verifier scoring、RL 更新 — 與 AlphaProof / FunSearch / AI-Scientist 一脈相承。

### 4.3.3 SOTA 系統（不限於純 DRL，但 RL 是核心驅動）

| 子領域 | 代表系統 | 期刊 | 年份 | RL 角色 |
|---|---|---|---|---|
| **蛋白質結構** | AlphaFold 2/3 | Nature 2021/2024 | 2021/24 | 非 RL（diffusion + attention），但下游設計用 RL |
| **De novo 蛋白質設計** | **RFDiffusion** [^watson2023rfdiffusion] | Nature 2023 | 2023 | 生成 diffusion + 下游 RL fine-tune ProteinMPNN |
| **化合物設計** | **REINVENT 4** [^loeffler2024reinvent] | J. Cheminf. 2024 | 2024 | **PPO 直接 optimize multi-property reward**（QED, SAS, docking） |
| **晶體 / 材料** | **GNoME** [^merchant2023gnome] | Nature 2023 | 2023 | Active learning（RL-adjacent） |
| **自主合成** | **A-Lab** [^szymanski2023alab] | Nature 2023 | 2023 | LLM 抽 recipe + 熱力學 active learning |
| **代數演算法** | **AlphaTensor** [^fawzi2022alphatensor] | Nature 2022 | 2022 | **純 AlphaZero MCTS** 找 tensor decomposition |
| **數學發現** | **FunSearch** [^romera2023funsearch] | Nature 2023 | 2023 | LLM 提 mutation + score-based selection |
| | **AlphaProof** | Nature 2025 | 2025 | AlphaZero-style RL on Lean proof tree |
| | **AlphaGeometry 2** | Nature 2025 | 2025 | LLM 提 aux 線 + symbolic verifier |
| **演算法** | **AlphaDev** [^mankowitz2023alphadev] | Nature 2023 | 2023 | AlphaZero 在 assembly instruction space；**merged into LLVM libc++** |
| **電漿控制** | **DIII-D Tearing avoidance** [^seo2024diii_d] | Nature 2024 | 2024 | RL 即時調磁場避開 tearing instability |
| **晶片設計** | **AlphaChip** [^mirhoseini2021chip] | Nature 2021 + addendum 2024 | 2021/24 | PPO + GNN 做 floorplan；**部署在 TPU** |
| **自主科學家** | Coscientist [^boiko2023coscientist] | Nature 2023 | 2023 | GPT-4 agent + 真實實驗室；做 Pd-catalyzed coupling |
| | **AI Scientist v2** [^yamada2025aisci] | arXiv 2025 | 2025 | **首次 AI-authored paper 通過 ICLR 2025 workshop peer review** |

### 4.3.4 代表性論文分析

**AlphaDev (Nature 2023) [^mankowitz2023alphadev]**. 真正影響日常 computing — DeepMind 把 AlphaZero 套用到 assembly instruction game，找到 short-sequence sort 比現有 libc++ 快 **70%** 的演算法，**merged into LLVM libc++**，每天執行數兆次。Latency reward per-instruction，correctness 用 test-equivalence。**Critical view**：只在 short branchless kernels 有效；不能 generalize 到任意演算法。**意義**：是少數能說「我的 RL 改變了基礎建設」的案例。

**DIII-D Tearing-instability avoidance (Nature Feb 2024) [^seo2024diii_d]**. 在真實 tokamak 上即時跑 RL 控制磁場，避免電漿 disruption（這是 fusion 商用的最大障礙之一）。能 compete 古典 PID/MPC 是因為 plasma dynamics 太高維。**Critical view**：sim2real 仍需 per-tokamak retraining；ITER 級別未證；reward 含 engineered terms 不確定通用性。

**AI Scientist v2 (Apr 2025) [^yamada2025aisci]**. Sakana AI 的 v2 用 agentic tree search + experiment manager。**首篇 AI 全自動撰寫的 paper 通過 ICLR 2025 workshop peer review**。雖然有 arXiv 2502.14297 對 v1 的尖銳批評（弱 literature synthesis、表面 novelty、shallow ablation），這仍代表一個門檻被跨過。**意義**：autonomous research agent 從概念變成可量化驗證的階段。

**GNoME + A-Lab (Nature 2023, 連續發表) [^merchant2023gnome] [^szymanski2023alab]**. GNoME 用 GNN + active learning 發現 2.2M 晶體 candidate，A-Lab 用自主機器人 17 天合成 41/58 個 GNoME 推薦。**Critical view**：2024 年 Cheetham & Seshadri 批評許多 GNoME "新材料" 其實是 rediscovery 或 composition duplicate；A-Lab 的 phase ID 也被質疑。但 **這仍是 RL + 自主實驗室「閉環」的最完整 demo**。

### 4.3.5 資料集 / Simulator

- **蛋白質**：PDB（19 萬+ 結構）、UniProt 序列、ESM-3 訓練用 2.78B proteins。
- **化合物**：ZINC, ChEMBL, GuacaMol, MOSES benchmark。
- **材料**：Materials Project, ICSD, OQMD；GNoME 的 release。
- **數學**：Lean 4 mathlib, IMO past papers, MathPile, ProofNet。
- **演算法**：CodeContests（AlphaCode）, LLVM IR, GEMM benchmark。
- **科學文獻**：S2ORC, OpenReview replicas。

### 4.3.6 未來方向

1. **Closed-loop autonomous lab**：A-Lab 是雛形，下一步是「LLM 提假設 → RL 規劃實驗 → robot 執行 → 解讀資料 → 更新假設」全自動。
2. **RL on formal verifier**：AlphaProof 證明這條路可行，把它擴到生物學（如 PathML proof）、物理（symbolic regression）。
3. **避免 reproducibility crisis**：AlphaChip / GNoME 的爭議警示，AI for Science 需要 open benchmark 與 independent replication，不只是 Nature 封面。
4. **多 modal scientific agent**：未來 agent 同時看 paper PDF、跑 simulation、操作真實 instrument，朝 Coscientist + AI Scientist v2 整合。

---

[^kim2024openvla]: Kim, M. J. et al. "OpenVLA: An open-source vision-language-action model." *arXiv:2406.09246* (2024).
[^pi2024pi0]: Physical Intelligence. "π0 / π0-FAST / π0.5: A vision-language-action flow model for general robot control." (2024–2025). arXiv:2504.16054.
[^figure2025helix]: Figure AI. "Introducing Helix: A vision-language-action model for humanoid control." (2025).
[^nvidia2025groot]: NVIDIA Research. "Isaac GR00T N1: A foundation model for humanoid robots." *arXiv:2503.14734* (2025).
[^deepmind2025geminirobotics]: Google DeepMind. "Gemini Robotics: Bringing AI into the physical world." *arXiv:2503.20020* (2025).
[^chi2023dp]: Chi, C. et al. "Diffusion policy: Visuomotor policy learning via action diffusion." *RSS* (2023); *IJRR* (2025). arXiv:2303.04137.
[^ze2024dp3]: Ze, Y. et al. "3D diffusion policy." *arXiv:2403.03954* (2024).
[^team2024octo]: Octo Model Team. "Octo: An open-source generalist robot policy." *RSS* (2024). arXiv:2405.12213.
[^ma2024eureka]: Ma, Y. J. et al. "Eureka: Human-level reward design via coding large language models." *ICLR* (2024).
[^luo2024serl]: Luo, J. et al. "SERL: A software suite for sample-efficient robotic reinforcement learning." *arXiv:2401.16013* (2024).
[^he2024omniH2O]: He, T. et al. "OmniH2O: Universal and dexterous human-to-humanoid whole-body teleoperation and learning." *CoRL* (2024). arXiv:2406.08858.
[^he2025asap]: He, T. et al. "ASAP: Aligning simulation and real-world physics for learning agile humanoid whole-body skills." (2025).
[^vinyals2019alphastar]: Vinyals, O. et al. "Grandmaster level in StarCraft II using multi-agent reinforcement learning." *Nature*, 575 (2019).
[^hafner2025dreamerv3]: Hafner, D. et al. "Mastering diverse control tasks through world models." *Nature*, 640 (2025). arXiv:2301.04104.
[^deepmind2025alphaproof]: AlphaProof and AlphaGeometry teams. "Solving olympiad-level math problems with AI." *Nature* (Nov 2025).
[^sima2025v2]: SIMA Team. "SIMA 2: An embodied agent that plays, reasons and learns with you in virtual 3D worlds." *arXiv:2512.04797* (2025).
[^watson2023rfdiffusion]: Watson, J. L. et al. "De novo design of protein structure and function with RFdiffusion." *Nature*, 620 (2023).
[^loeffler2024reinvent]: Loeffler, H. H. et al. "REINVENT 4: Modern AI-driven generative molecule design." *J. Cheminformatics* (2024).
[^merchant2023gnome]: Merchant, A. et al. "Scaling deep learning for materials discovery." *Nature*, 624 (2023).
[^szymanski2023alab]: Szymanski, N. J. et al. "An autonomous laboratory for the accelerated synthesis of novel materials." *Nature*, 624 (2023).
[^fawzi2022alphatensor]: Fawzi, A. et al. "Discovering faster matrix multiplication algorithms with reinforcement learning." *Nature*, 610 (2022).
[^romera2023funsearch]: Romera-Paredes, B. et al. "Mathematical discoveries from program search with large language models." *Nature*, 625 (2023).
[^mankowitz2023alphadev]: Mankowitz, D. J. et al. "Faster sorting algorithms discovered using deep reinforcement learning." *Nature*, 618 (2023).
[^seo2024diii_d]: Seo, J. et al. "Avoiding fusion plasma tearing instability with deep reinforcement learning." *Nature*, 626 (2024).
[^mirhoseini2021chip]: Mirhoseini, A. et al. "A graph placement methodology for fast chip design." *Nature*, 594 (2021); Addendum (2024).
[^boiko2023coscientist]: Boiko, D. A. et al. "Autonomous chemical research with large language models." *Nature*, 624 (2023).
[^yamada2025aisci]: Yamada, Y. et al. "The AI Scientist v2: Workshop-level automated scientific discovery via agentic tree search." *arXiv:2504.08066* (2025).
