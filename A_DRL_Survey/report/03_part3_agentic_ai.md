# Part 3 — Agentic AI and Autonomous Agents

DRL 在 2024–2026 最大的「身分轉換」是：**它從一個獨立的 sub-field，變成了大型模型（LLM/VLM）系統裡的一個 alignment + reasoning 元件**。本章梳理 LLM agents、RLHF / RLAIF、tool-using、multi-agent、self-improving、memory 等六個面向，最後討論 DRL 如何被融入 agentic AI、以及對 AGI 的影響。

## 3.1 LLM Agents — 三大產品堆疊

### 3.1.1 OpenAI Agent Stack
- **Computer-Using Agent (CUA) / Operator**（2025 Jan）：GPT-4o vision 模型 + RL 訓練的 CUA，能在瀏覽器中點擊、輸入、滾動；2025 升級到 o3-based 版本，加入 self-correction loop 與遇到不確定時主動 hand-back 給用戶。
- **Deep Research**（2025 Feb）：以 o3 為核心的多步研究 agent，能瀏覽網頁、彙整資訊、撰寫長報告；以 RL on research-task verifiers 訓練。
- **GPT-5 / 5.2 / 5.5**（2025 Aug–Dec）：「Steerable, collaborative」agentic mode；SWE-bench Verified 74.9%、Aider Polyglot 88%；GPT-5.5 在 agentic coding bench 達 82.7%。
- **Open problem**：UC Berkeley CRDI 在 2026 Apr 公開能自動 reward-hack 全部八個主流 agent benchmark 的攻擊 agent — 整個評估體系正在被質疑。

### 3.1.2 Anthropic Agent Stack
- **Claude Computer Use**（2024 Oct）：以 screenshot 為輸入、tool API 為輸出的 GUI 控制。
- **Model Context Protocol (MCP)**（2024 Nov）：開放的 JSON-RPC 2.0 標準（設計受 LSP 啟發），讓 LLM 以統一 schema 連結工具與資料源。**到 2025 Dec 月下載量達 9700 萬**；Anthropic 已將其捐贈給新成立的 Linux Foundation Agentic AI Foundation（與 Block、OpenAI 共同創立）[^anthropic2025mcp]。
- **Claude Code**（2024–2026）：terminal-resident 的 agentic coding 工具，採 single-threaded master loop + 細粒度 permission system + 工具層（Read / Glob / Grep / Edit / Bash）；新版引入 multi-agent 分解（planner / executor / debugger / validator）。
- **Claude Skills**（2025）：以「Skill 包」（檔案集合）為單位的能力註冊與調用。

### 3.1.3 Google Agent Stack
- **Project Astra**（2024 Dec → I/O 2025）：跨裝置（手機 + 原型眼鏡）的 multimodal 助理，session memory 約 10 分鐘。
- **Project Mariner**（2024 Dec → I/O 2025）：Gemini 2.5 Pro 驅動的 web agent，可同時跑 **10 個 parallel task**，整合進 AI Mode 做預訂、查詢。
- **Gemini 2.5 Pro / Deep Think**：擴充為「world model」做 planning 與 imagined-experience simulation。

### 3.1.4 Orchestration Frameworks
| 框架 | 模型 | 特色 | 適用 |
|---|---|---|---|
| **LangGraph** v1.0（2025） | 任意 | Stateful graph + conditional edges；LangChain 預設 runtime | 產業 audit 與穩定性 |
| **CrewAI** | 任意 | Role-based crews；2025 取得 $18M A 輪，宣稱 60% 財富 500 大使用 | 中型企業 workflow |
| **Microsoft Agent Framework**（2025 Oct 由 AutoGen 與 Semantic Kernel 合併，2026 Q1 GA） | 任意 | GroupChat conversational pattern | Azure 生態 |
| **AutoGPT / BabyAGI** lineage | GPT-4 系列 | 概念先驅，已大致被 graph-based 框架取代 | 教學示範 |

## 3.2 RLHF / RLAIF — 對齊的演算法

### 3.2.1 直接偏好最佳化（DPO 系列）
- **DPO**（Rafailov et al., NeurIPS 2023 [^rafailov2023dpo]）：用一個閉式映射把 reward 模型「吸收」進 policy，pairwise preference loss 可直接訓 policy — 不需要 RM、不需要 online sampling，匹配甚至超越 PPO-RLHF。
- **IPO**（Azar et al., AISTATS 2024）：用 bounded objective 取代 Bradley-Terry，修正 DPO 在 deterministic preference 上的 unbounded margin 發散，OOD 泛化更好。
- **KTO**（Ethayarajh et al., ICML 2024 spotlight [^ethayarajh2024kto]）：用 prospect theory 的 utility maximization，**只需要「好 / 壞」二元標籤**，標註成本遠低於 pairwise；在大模型上匹配 DPO。

### 3.2.2 Constitutional AI / RLAIF
- **Constitutional AI**（Bai et al., Anthropic 2022 [^bai2022constitutional]）：兩階段 — (1) SL：以「constitution」為原則做 self-critique + revise；(2) RL：以 AI 生成的偏好標籤訓練偏好模型再做 RLHF。**「RLAIF」一詞由此而來**。
- **RLAIF vs RLHF**（Lee et al., Google, ICML 2024 [^lee2024rlaif]）：在 summarization、helpful + harmless dialogue 上 RLAIF ≈ RLHF；AI labeler 大小不必超過 policy；**d-RLAIF**（off-the-shelf LLM 直接給 reward，跳過 RM）反而打敗 canonical RLAIF。
- **Open problem**：相同家族 labeler 帶來的 sycophancy；對抗 prompt 下 constitutional principles 仍易崩（「Constitution or Collapse?」arXiv:2504.04918）。

### 3.2.3 推理 RL — PRM / ORM / RLVR
- **Process Reward Models (PRM)**（Lightman et al., OpenAI ICLR 2024 [^lightman2024verify]）：每一步給 reward 比只給最終結果（ORM）更有效；釋出 PRM800K（800k step-level 標籤），在 MATH 子集達 78% 解題率。
- **DeepSeek-R1**（Guo et al., **Nature 2025**，首篇 peer-reviewed LLM Nature [^deepseek2025r1]）：純 RL with **verifiable rewards** — 數學以符號驗證、程式碼以單元測試。提出 **GRPO**（Group Relative Policy Optimization）取消 critic、以 group 內 K 個樣本的 advantage 標準化取代之；以 ~147K H800 GPU-hr（比 o1 級便宜約 10 倍）達到 o1 等級推理能力。
- **OpenAI o1 / o3**（2024 Sep / 2025）：RL 訓練 long-CoT；提出 **inference-time scaling law** — 表現同時隨 train-time RL 計算與 test-time thinking budget 增長。
- **RLVR 理論**（arXiv:2506.14245）：RLVR 不只是提高「能 sample 出正確 CoT 的機率」，而是**擴展推理邊界**；提出 CoT-Pass@K 指標。
- **Open problem**：reward over-optimization；narrow verifier；數學/程式碼 RL 難以 transfer 到開放性推理（「Crossing the Reward Bridge」arXiv:2503.23829）。

## 3.3 Tool-using / Function-calling Agents

- **ReAct**（Yao et al., ICLR 2023 [^yao2023react]）：把 reasoning 與 acting 交錯生成（`Thought → Action → Observation` loop），是後續所有 agent loop 的 baseline。
- **Toolformer**（Schick et al., NeurIPS 2023）：自監督地在 pretraining 中插入 API call token，學「何時該叫 tool」。
- **Gorilla**（Patil et al., NeurIPS 2024 [^patil2024gorilla]）：微調 LLaMA 在 1600+ API 中做 API 選擇；衍生 Berkeley Function Calling Leaderboard (BFCL v4，含 agentic / multi-hop / error recovery 多項)。
- **ToolACE**（ICLR 2025）：自動合成 tool-use 資料的 pipeline，BFCL SOTA。

### 3.3.1 Agent Benchmarks
| Benchmark | 任務數 / 範圍 | 當前 SOTA | 特性 |
|---|---|---|---|
| **SWE-bench / Verified**（ICLR 2024）| 2,294 真實 GitHub issue | ~75–82%（GPT-5/5.5）| Execution-based |
| **GAIA**（Meta, ICLR 2024）| 多工具複合題 | -- | 單一 ground truth |
| **AgentBench**（ICLR 2024）| 8 環境（OS/DB/KG/...）| -- | 廣 coverage |
| **WebArena**（ICLR 2024）| 812 長時域 web task | 14.4% → 61.7%（IBM CUGA, 2025）| 真實 web 環境 |
| **OSWorld**（NeurIPS 2024）| 369 跨 app real-OS task | ~60pt 人類落差 | 真實 OS |
| **τ-bench**（Sierra/Yao, 2024）| Reliability：pass^k | -- | 揭露一致性問題 |

**Open problem**：UC Berkeley CRDI 2026 Apr 公布能自動破解全部八個主流 benchmark 的 reward-hacking agent — 整個評估典範面臨重建。

## 3.4 Multi-Agent Collaboration

- **Generative Agents**（Park et al., Stanford, UIST 2023 [^park2023generative]）：25 個 simulacra 在沙盒小鎮中以「observe + reflect + plan + 記憶流」互動，產生 emergent 社會行為（自發辦派對、傳八卦）。
- **CAMEL**（Li et al., NeurIPS 2023）：「inception prompting」讓兩個 LLM 扮演 user / assistant 對話自我引導；生成 AI Society + Code datasets。
- **MetaGPT**（Hong et al., ICLR 2024 oral [^hong2024metagpt]）：把軟體開發 SOP 指派給 agent role（PM / Architect / Engineer / QA），釋出時程式碼 Pass@1 達 85.9 / 87.7。
- **ChatDev**（Qian et al., ACL 2024）：CEO / CTO / Programmer / Tester 的「waterfall 軟體公司」。
- **AutoGen**（Wu et al., ICLR 2024 workshop / COLM 2024）：比 MetaGPT/ChatDev 更靈活的 GroupChat。

### 3.4.1 MARL（classical multi-agent RL）
- 2024 surveys（Sci. Direct S2949855424000042、arXiv:2412.21088）：合作型 MARL 仍由 CTDE 家族（QMIX / MAPPO）主導；open problem 是 curse of dimensionality、non-stationarity、跨異質 reward/state/action 空間的 multi-task 規模化。
- **LLM agent + MARL 的融合是個 open frontier** — LLM agent 缺乏 MARL 的 credit assignment 形式化；MARL 缺乏 LLM agent 的泛化能力。

## 3.5 Foundation Agents / Self-improving Agents

- **SIMA**（DeepMind, 2024 Mar [^deepmind2024sima]）：跨多款商業 3D 遊戲用 keyboard/mouse 通用介面操作的 generalist agent；以 language instruction 觸發；首次達 31% 人類相對成功率。**SIMA 2**（2025 Nov）：用 Gemini 驅動，成功率約 v1 的兩倍，在訓練過環境近人類，能 transfer 到未見過遊戲。
- **Magma**（Microsoft, CVPR 2025 [^magma2025]）：foundation model 同時處理 digital UI 與 physical robot；提出 Set-of-Mark (SoM) 做 action grounding、Trace-of-Mark (ToM) 做 action planning，在 UI navigation 與 robot manipulation 上 SOTA。
- **STaR**（Zelikman et al., NeurIPS 2022）：Bootstrap rationales — 生成 → 以正確答案濾 → fine-tune；所有後續 rationale RL 的祖先。
- **Self-Rewarding LMs**（Yuan et al., Meta/NYU, ICML 2024 [^yuan2024selfrewarding]）：模型同時當 generator 與 LLM-as-judge，做迭代 DPO；instruction following 與 reward giving 一起進步。
- **Meta-Rewarding LMs**（Wu et al., arXiv:2407.19594）：再加一層 meta-judge 降低 judge bias。
- **Open problem**：多輪 self-iteration 後的 reward model collapse；缺外部 verifier 時的 grounding。

## 3.6 Memory Systems

| 路線 | 代表 | 優勢 | 限制 |
|---|---|---|---|
| **Long context (1M+ tokens)** | Gemini 1.5/2.5、Claude 200K–1M | 簡單、不需新架構 | 推論貴；needle-in-haystack 深度效能下滑 |
| **RAG** | Llama-Index、LangChain RAG | 標準外部知識 baseline | multi-hop / temporal update 表現差 |
| **MemGPT / Letta**（Packer et al., 2023 [^packer2023memgpt]） | OS-style 階層記憶（core / recall / archival），LLM 用 page-in/out 函式 | 長文件 QA、多 session chat | 需手刻 paging 邏輯 |
| **Generative-agent memory**（Park 2023） | Memory stream + recency/importance/relevance retrieval + reflection | 模擬 episodic memory | 規模化困難 |

**Open problem**：缺乏 episodic vs semantic 的標準 benchmark；long-context scaling law vs 結構化檢索的 trade-off 未解；遺忘 / consolidation 政策無共識。

## 3.7 DRL 與 Agentic AI 的整合

### 3.7.1 DRL 在 LLM agent 中的角色
1. **對齊（alignment）**：PPO/GRPO + RLHF/RLAIF/RLVR 是把 base model 變成 helpful + harmless + honest 助理的核心。
2. **推理（reasoning）**：o1 / DeepSeek-R1 證明 RL 能放大 LLM 內隱的推理路徑分布，**inference-time compute 與 train-time RL 是新 scaling axis**。
3. **規劃（planning）**：MuZero-style 的 model-based planning 開始與 LLM 結合（如 Tree-of-Thoughts、AlphaProof）。
4. **工具使用（tool use）**：偏好 / 結果 reward 訓 agent 選對工具（Gorilla, ToolACE）。
5. **多 agent 競合**：marketplace / debate / negotiation 用 self-play 風格 RL 訓練。

### 3.7.2 規劃與決策機制
- **靜態 chain-of-thought**：最簡單，但無法回頭。
- **Tree-of-Thoughts / Graph-of-Thoughts**：明確 search，可重訪 node。
- **ReAct loop**：感知 + 行動交錯，每一步看到 env feedback。
- **MCTS-style with learned value**（如 AlphaProof）：LLM 提案、value model 評分、search expansion。
- **Plan-then-execute**：先全局規劃再分配給 sub-agent（CrewAI、MetaGPT）。

### 3.7.3 人類回饋與對齊
從 InstructGPT 開始，**RLHF → DPO → KTO → RLAIF → RLVR** 這條演化路徑反映兩個趨勢：(a) **降低人類標註成本**（pairwise → binary → AI labels → verifier）；(b) **轉向可驗證信號**（從主觀偏好到客觀 ground truth）。下一步是 **process-aware reward** 與 **verifier 之外的泛化**（如何把數學 RL 學到的推理 transfer 到開放性問題）。

### 3.7.4 通往 AGI 的方向
2025–2026 各家路線收斂在三條軸線上：
- **通用性（generality）**：foundation agent 跨任務、跨 embodiment、跨 modality（GR00T、Magma、SIMA 2、Gemini Robotics）。
- **自主性（autonomy）**：long-horizon agent 能維持多小時/多天目標，不需要人類每步監督（Deep Research、Project Mariner）。
- **可驗證學習（verifiable learning）**：以 RL on verifiable rewards 持續 self-improve（DeepSeek-R1、Self-Rewarding LMs）。

**Critical view.** 雖然進展驚人，但 (1) **reliability gap** 仍大（τ-bench 顯示重複跑同一任務的一致性低）、(2) **benchmark gaming** 威脅整個 evaluation 典範、(3) memory 沒有共識解、(4) 真正的 long-term autonomous self-improvement 仍未被 demo。AGI 不是「規模再大一點」就會到，當前 agentic AI 距離真正的 autonomous artificial general intelligence 仍有顯著 gap。

---

[^anthropic2025mcp]: Anthropic. "Donating the Model Context Protocol and establishing the Agentic AI Foundation." (2025).
[^rafailov2023dpo]: Rafailov, R. et al. "Direct preference optimization: Your language model is secretly a reward model." *NeurIPS* (2023). arXiv:2305.18290.
[^ethayarajh2024kto]: Ethayarajh, K. et al. "KTO: Model alignment as prospect theoretic optimization." *ICML* (2024). arXiv:2402.01306.
[^bai2022constitutional]: Bai, Y. et al. "Constitutional AI: Harmlessness from AI feedback." *arXiv:2212.08073* (2022).
[^lee2024rlaif]: Lee, H. et al. "RLAIF vs. RLHF: Scaling reinforcement learning from human feedback with AI feedback." *ICML* (2024). arXiv:2309.00267.
[^lightman2024verify]: Lightman, H. et al. "Let's verify step by step." *ICLR* (2024). arXiv:2305.20050.
[^deepseek2025r1]: Guo, D. et al. "DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning." *Nature* (2025).
[^yao2023react]: Yao, S. et al. "ReAct: Synergizing reasoning and acting in language models." *ICLR* (2023).
[^patil2024gorilla]: Patil, S. G. et al. "Gorilla: Large language model connected with massive APIs." *NeurIPS* (2024).
[^park2023generative]: Park, J. S. et al. "Generative agents: Interactive simulacra of human behavior." *UIST* (2023). arXiv:2304.03442.
[^hong2024metagpt]: Hong, S. et al. "MetaGPT: Meta programming for a multi-agent collaborative framework." *ICLR* (2024).
[^deepmind2024sima]: SIMA Team. "Scaling instructable agents across many simulated worlds." *DeepMind* (2024). arXiv:2404.10179.
[^magma2025]: Yang, J. et al. "Magma: A foundation model for multimodal AI agents." *CVPR* (2025). arXiv:2502.13130.
[^yuan2024selfrewarding]: Yuan, W. et al. "Self-Rewarding Language Models." *ICML* (2024). arXiv:2401.10020.
[^packer2023memgpt]: Packer, C. et al. "MemGPT: Towards LLMs as operating systems." *arXiv:2310.08560* (2023).
