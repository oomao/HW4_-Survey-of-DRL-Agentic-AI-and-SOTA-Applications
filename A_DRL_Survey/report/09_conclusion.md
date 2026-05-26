# Part 9 — Conclusion, Ethics, and Future Directions

## 9.1 結論

本份 survey 從 **演算法基礎 → 系統平台 → agentic AI → 三個應用領域 → 五條 SOTA 趨勢 → 比較分析 → GitHub 生態 → 兩個 hands-on MVP**，回答了一個核心問題：

> **2024–2026 之間，Deep Reinforcement Learning 的角色發生了什麼根本性轉變？**

答案可以總結為 **三個轉折**：

1. **從「獨立 sub-field」變成「foundation model 的對齊 / 推理元件」。**
   PPO、GRPO 不再只是訓 robot 用，它們現在每天在 RLHF、RLAIF、RLVR 中對齊 GPT-5、Claude 4.7、Gemini 2.5、DeepSeek-R1 等等模型。DeepSeek-R1 用純 RL with verifiable rewards 訓出可與 o1 競爭的推理能力，且論文是 **首次以 LLM 為主題的 Nature peer-reviewed paper**——這是一個歷史時刻。

2. **從「flat policy」走向「dual-system 與 hierarchy」。**
   Helix（S2 慢 + S1 快）、GR00T N1、Gemini Robotics 1.5、π0.5 等系統共同收斂在「VLM 想 + visuomotor 做」的雙系統架構；agentic AI 端則用 plan-then-execute / Tree-of-Thoughts / MCTS-with-learned-value 把 LLM reasoning 結構化。這呼應了人腦 dual-process theory（System 1 / System 2）。

3. **從「在 sim 中 train、在 real 中失敗」走向「differentiable physics + foundation video model 構成的新 sim2real stack」。**
   Newton（NVIDIA + Google + Disney）、MuJoCo MJX、V-JEPA 2、Genie 3 共同把 robot 訓練拉進「梯度可穿過 simulator、video 作為 imagined env」的新時代。Berkeley 在 RTX 4090 上 15 分鐘訓完 Unitree G1 locomotion 已不是奇蹟。

## 9.2 倫理與安全考量

報告也必須誠實面對 DRL + agentic AI 的負面 / 風險面：

### 9.2.1 Reward hacking 與 specification gaming
RL agent 永遠在 **「reward 是什麼」與「我們想要什麼」** 之間的縫隙裡找漏洞。2026 年 4 月 UC Berkeley CRDI 公布的「自動 reward-hack 所有八個主流 agent benchmark」攻擊 agent，把這個古老 RL 問題搬到 agentic AI 評估的全新規模上。**Critical**：每個 reward 設計都應被視為一個攻擊面。

### 9.2.2 Sycophancy 與對齊偏差
RLHF / RLAIF 訓出的模型容易「迎合」用戶觀點而非說真話；constitutional AI 雖然降低了部分問題，但對抗 prompt 下仍易崩（arXiv:2504.04918「Constitution or Collapse?」）。同家族 AI labeler 帶來的 self-reinforcing bias 仍是開放問題。

### 9.2.3 機器人安全
humanoid 商用部署（Apollo 在 Mercedes、Figure 03 設計年產 12k 台、1X NEO 開放消費市場）走在 **formal safety certification 之前**——目前沒有任何 humanoid 在 unstructured 家庭環境取得正式安全認證。**Critical**：第一次 RL-driven robot 在私人住家造成傷害事件可能就在 2026–2027 之間發生，產業與監管需要提前對齊。

### 9.2.4 自主科學 AI 的可重現性
AlphaChip（Nature 2021 + 2024 addendum，Markov CACM 2024 批評）、GNoME / A-Lab（2024 Cheetham & Seshadri 批評）展示 Nature cover 不等於 reproducible science。AI Scientist v2 通過 ICLR 2025 workshop peer review 是里程碑，但同年 arXiv:2502.14297 批評其 literature synthesis 薄弱。**Critical**：autonomous science 必須以 open benchmark + independent verification 為前提，否則只是規模化的 confirmation bias。

### 9.2.5 經濟與社會衝擊
agentic coding（GPT-5 SWE-bench 82.7%、Claude Code 等）、agentic web（Mariner、Operator）、humanoid 勞動（Apollo at GXO/Jabil/Mercedes）三線同時推進，**正在重新定義「人類做什麼」的邊界**。Universal verification、職業轉型、公平分配將是 2026–2030 必須面對的政策議題。

## 9.3 未來研究方向（個人觀點）

基於本 survey 的脈絡，我認為以下五個方向值得未來研究投入：

1. **World-model RL on humanoids**：DreamerV3 + Genie 3 風格 video model + Helix dual-system 的整合 — 把「在腦中模擬」實際應用到人形機器人上。
2. **Verifier-driven agent training for non-mathematical domains**：把 DeepSeek-R1 / AlphaProof 的 RLVR 思路擴到生物、化學、UI 任務上 — 關鍵是設計「不會被 hacked 的 verifier」。
3. **Cross-embodiment foundation policies**：OpenVLA、Octo、CrossFormer 開頭，但離真正的「**a single weight that drives any robot**」仍遠 — 需要更大規模的 multi-embodiment data + 更聰明的 action space unification。
4. **Agent reliability engineering**：τ-bench 揭露的 pass^k 問題不是 model issue 而是 **system engineering** issue — 需要 RL-style sequential improvement + traditional SE practice（retry / timeout / circuit-breaker）的融合。
5. **MARL + LLM 真正融合**：population-based training（AlphaStar 風格）套到 LLM agent；多 agent debate / negotiation 用 self-play 風格 RL — 這個交叉點目前還沒有 SOTA 代表作。

## 9.4 個人收穫

撰寫本 survey 的過程中我最深的感受：**2024–2026 的 DRL 已經不是 2018 年的 DRL**。

- 2018 年的 DRL 是 PPO + Mujoco + 一張 RTX 1080 + 你自己的 reward function。
- 2026 年的 DRL 是 GRPO + RLVR + RTX Pro 6000 cluster + LLM 生成 reward + foundation policy。

這個轉變的速度，加上 agentic AI 的勢頭，讓我相信 2027–2028 之間我們會看到：(a) 第一個能在你家廚房 90% 成功率清理 30 分鐘的 humanoid 商品；(b) 第一篇 AI 全自動撰寫並通過 main-track（非 workshop） peer review 的論文；(c) RL-trained 軟體 agent 在 SWE-bench Verified 衝破 90%。

當這些里程碑被達成的時候，本 survey 整理的演算法、平台、agent 系統將是回顧那段歷史的重要參考。
