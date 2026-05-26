# Part 1 — Introduction to Deep Reinforcement Learning

## 1.1 Fundamental Concepts

### 1.1.1 Reinforcement Learning (RL)

Reinforcement Learning（強化學習）研究的是一個 **agent** 如何在與 **environment** 反覆互動的過程中，學會選擇能最大化長期累積回饋（cumulative reward）的行動。RL 與監督式 / 非監督式學習的本質差異在於：**訓練訊號不是事先標好的標籤，而是由 agent 自己用行動「探索」出來的回饋。** 這個 closed-loop 的結構讓 RL 同時面對三個傳統 ML 不必處理的難題——延遲回饋（credit assignment）、非穩態資料分布（policy 改變則資料分布跟著改變）、以及 **探索 vs 利用** 的權衡。

### 1.1.2 Markov Decision Process (MDP)

絕大多數 DRL 演算法都假設環境可以被建模成一個 **Markov Decision Process** $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)$：

- $\mathcal{S}$：狀態空間。
- $\mathcal{A}$：動作空間（離散或連續）。
- $P(s' \mid s, a)$：轉移機率，滿足 **Markov property**——下一狀態只依賴當前 $(s, a)$，不依賴歷史。
- $R(s, a)$ 或 $R(s, a, s')$：reward function。
- $\gamma \in [0, 1)$：discount factor，把無窮時域問題折成有限期望值。

當部份可觀測時退化成 **POMDP**（Partially Observable MDP），agent 只看得到 observation $o_t$ 而非 $s_t$，這是真實機器人和大多數 video games 的設定。

### 1.1.3 Reward Function

Reward function 是 RL 中最重要、也最容易被低估的設計選擇。它決定「目標是什麼」，因此一切學到的行為都是 reward 的副產物——reward hacking、specification gaming 都源自此處。SOTA 趨勢之一是 **不再人工手刻 reward**，而是用 LLM 生成（如 NVIDIA Eureka）、用人類偏好學（RLHF）、或從可驗證的成功訊號取得（RLVR，如 DeepSeek-R1）。

### 1.1.4 Policy 與 Value Functions

- **Policy** $\pi(a \mid s)$：在每個狀態下選擇動作的分布。Deterministic 時寫成 $\pi(s) \to a$。
- **State-value** $V^\pi(s) = \mathbb{E}_\pi[\sum_{t=0}^\infty \gamma^t r_t \mid s_0 = s]$：從 $s$ 起遵循 $\pi$ 的期望累積折扣回饋。
- **Action-value** $Q^\pi(s, a)$：在 $s$ 先執行 $a$ 再遵循 $\pi$ 的期望回饋。
- **Advantage** $A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$：執行 $a$ 比平均策略好多少，是 policy gradient 方法的核心訊號。

兩條基礎理論：**Bellman 方程**將 $V$、$Q$ 寫成遞迴形式，為所有 value-based 演算法提供更新公式；**Policy Gradient Theorem** 給出 $\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}[\nabla_\theta \log \pi_\theta(a \mid s) Q^{\pi_\theta}(s,a)]$，是 PPO/SAC 等 policy-based 方法的根。

### 1.1.5 Exploration vs Exploitation

短期想最大化 reward 就應該選目前看起來最好的動作（exploit），但長期想找到真正的最優策略就必須嘗試陌生動作（explore）。常見策略：

| 策略 | 機制 | 典型用法 |
|---|---|---|
| $\epsilon$-greedy | 以機率 $\epsilon$ 隨機、否則 greedy | DQN 系列 |
| Boltzmann/softmax | 依 $Q$ 值加溫度做機率取樣 | tabular RL |
| Entropy bonus | 在 loss 加入策略熵 $\mathcal{H}(\pi)$ | A2C / PPO / SAC |
| Intrinsic motivation | 額外的 curiosity / prediction-error reward | RND, ICM |
| Posterior sampling | 從後驗分布取樣 $Q$ | Bootstrapped DQN |
| Noise on parameters | NoisyNet | Rainbow DQN |

---

## 1.2 Deep RL Algorithms — Survey and Comparison

下面對 10 個代表性演算法做系統性整理，每個都包含 **core idea / advantages / weaknesses / typical applications**。

### 1.2.1 DQN (Deep Q-Network)

**Core idea.** Mnih et al., Nature 2015 [^mnih2015]。用神經網路 $Q_\theta(s,a)$ 近似 action-value，搭配兩個關鍵 trick 解決深度 RL 的不穩定：
1. **Experience Replay Buffer**：把 $(s,a,r,s')$ 存進 buffer，訓練時均勻取樣，打破時序相關性。
2. **Target Network**：另外維護一個延遲更新的 $Q_{\theta^-}$，提供穩定的 target $y = r + \gamma \max_{a'} Q_{\theta^-}(s', a')$。

**Advantages.** 第一個在 high-dimensional 像素輸入上成功的 DRL 演算法；架構簡單；off-policy 因此可重複利用資料。

**Weaknesses.** $\max$ 運算造成系統性 Q 值高估（overestimation bias）；只能處理 **離散動作**；對 reward scaling 敏感；訓練不穩。

**Typical applications.** Atari 2600 benchmark、桌面遊戲、離散決策（推薦、廣告 bidding）。

### 1.2.2 Double DQN

**Core idea.** van Hasselt et al., AAAI 2016 [^vanhasselt2016]。把目標的 $\max$ 拆成「選動作」與「估值」兩步：
$$ y = r + \gamma \, Q_{\theta^-}\!\left(s', \arg\max_{a'} Q_\theta(s', a')\right). $$
online network 負責挑動作、target network 負責估該動作的 Q，緩解高估偏差。

**Advantages.** 改動極小（一行 code），效果卻顯著穩定；後續所有 DQN 變體幾乎都內建。

**Weaknesses.** 仍是離散動作；overestimation 沒有完全消除（只是降低）；在動作空間很大時偏差可能轉為低估。

**Typical applications.** 所有原本 DQN 的場景；現代 Atari 訓練的預設 baseline。

### 1.2.3 PPO (Proximal Policy Optimization)

**Core idea.** Schulman et al., OpenAI 2017 [^schulman2017ppo]。沿用 TRPO 的 trust-region 哲學（避免每次更新走太遠導致 policy 崩壞），但用一個簡單的 **clipped surrogate objective** 取代二階近似：
$$ L^{CLIP}(\theta) = \mathbb{E}_t\!\left[\min\left(r_t(\theta) \hat A_t,\ \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\, \hat A_t\right)\right], $$
其中 $r_t(\theta) = \pi_\theta(a_t \mid s_t) / \pi_{\theta_{\text{old}}}(a_t \mid s_t)$。

**Advantages.** **目前最常用的 on-policy 演算法**；實作簡單、超參數魯棒、適用離散與連續動作；是 RLHF / RLAIF / RLVR 的事實標準（GPT、Claude、Gemini 全部用 PPO 變體做對齊）。

**Weaknesses.** on-policy 因此 sample-inefficient；對 advantage normalization、learning-rate schedule 等實作細節敏感（被 Andrychowicz et al., ICLR 2021 [^andrychowicz2021] 證實是「37 implementation details」）。

**Typical applications.** 機器人控制、自駕、Dota 2/StarCraft 等大規模分散式訓練、**LLM 對齊（RLHF）**。

### 1.2.4 A2C / A3C (Asynchronous Advantage Actor-Critic)

**Core idea.** Mnih et al., ICML 2016 [^mnih2016a3c]。同時學一個 actor $\pi_\theta$ 和一個 critic $V_\phi$，用 advantage $\hat A = R - V_\phi$ 替代 Q 來降低 policy gradient 的 variance。**A3C** 用多個 worker 在 CPU 上**非同步**地各自抓資料、各自做梯度、push 回 master；**A2C** 是同步版本（等所有 worker 收完一筆 batch 再一起更新），在 GPU 時代往往效果更好。

**Advantages.** 不必 replay buffer；天然支援連續動作；多 worker 也是一種探索的隱性 randomization。

**Weaknesses.** 比 PPO 不穩；缺乏 trust-region 控制；on-policy 因此 sample-inefficient。**已被 PPO 取代成 baseline。**

**Typical applications.** 學術 baseline；多核 CPU cluster 上的大規模訓練（PPO 出現前的 Dota 等）。

### 1.2.5 SAC (Soft Actor-Critic)

**Core idea.** Haarnoja et al., ICML 2018 [^haarnoja2018sac]。把標準 RL 目標改成 **maximum entropy** 形式：
$$ J(\pi) = \sum_t \mathbb{E}\!\left[r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot \mid s_t))\right]. $$
鼓勵 policy 在所有「等好」的動作上保持熵，自然兼顧探索。架構是 off-policy actor-critic + 兩個 Q network（取 min 避免高估）。

**Advantages.** **連續控制的 SOTA baseline**（與 TD3 並列）；sample-efficient（off-policy）；temperature $\alpha$ 可自動調整；穩健。

**Weaknesses.** 實作比 PPO 複雜；連續動作專用（離散版本後出但較少用）；對 critic 過擬合敏感（需要 target 與 ensemble）。

**Typical applications.** 機械手臂、足式機器人、UAV、自駕。

### 1.2.6 TD3 (Twin Delayed DDPG)

**Core idea.** Fujimoto et al., ICML 2018 [^fujimoto2018td3]。針對 DDPG 的 Q 值高估與不穩，提出三個技巧：
1. **Clipped Double Q-learning**：兩個 critic 取 min。
2. **Delayed policy updates**：critic 多更新幾步 actor 才更新一次。
3. **Target policy smoothing**：在 target action 加 Gaussian noise 後 clip，避免 critic 對窄峰 over-fit。

**Advantages.** Deterministic policy 在精確控制（如手臂末端定位）上略優於 SAC；演算法純粹、無 entropy term。

**Weaknesses.** 缺乏 SAC 的自動探索能力，對 exploration noise schedule 敏感；當任務需要多模態行為時，deterministic policy 表現不如 SAC。

**Typical applications.** 連續控制；機器人精準定位；常與 SAC 並列為 baseline。

### 1.2.7 MuZero

**Core idea.** Schrittwieser et al., Nature 2020 [^schrittwieser2020muzero]。AlphaZero 的繼承者，**但不再需要環境模型作為已知輸入**——MuZero 學一個 **抽象的 latent dynamics model**（不直接預測 pixels，只預測對 policy/value 有用的 latent 表徵），然後在這個學到的模型裡做 MCTS。可以同時打敗 AlphaZero（圍棋/西洋棋/將棋）與 R2D2（Atari），不需要任何遊戲規則。

**Advantages.** model-based 帶來高 sample efficiency；不需手刻環境模型；同一架構征服 board games + Atari。

**Weaknesses.** 工程複雜（MCTS + 表徵學習 + reward/value prediction）；對隨機環境（如撲克）不擅長；訓練成本高。

**Typical applications.** 棋類遊戲、Atari、video compression（DeepMind 後續 paper）、推薦系統（少數產業應用）。

### 1.2.8 Decision Transformer (DT)

**Core idea.** Chen et al., NeurIPS 2021 [^chen2021dt]。**把 RL 重新當成序列建模問題**——給定一個 trajectory $(R_1, s_1, a_1, R_2, s_2, a_2, \dots)$，用 Transformer 自迴歸地預測下一個動作。$R_t$ 是 **return-to-go**（從 $t$ 起的剩餘 reward 總和）；inference 時把目標 return 餵進去，agent 就「假裝自己能拿到那麼多 reward」並輸出動作。

**Advantages.** 完全不用 RL（沒有 TD、沒有 policy gradient）；天然支援 offline RL；可以受惠於 Transformer scaling laws；用 return-conditioning 做 multi-task 很自然。

**Weaknesses.** 在 **stitching**（從不連續的次優 trajectory 拼出最優策略）上不如 dynamic programming-based offline RL（如 CQL）；對 OOD return target 敏感；需要大量資料才打得贏 TD-based 方法。

**Typical applications.** Offline RL benchmarks、robotic learning from demonstrations、後續 Trajectory Transformer / Gato / VLA 系列的祖先。

### 1.2.9 Offline RL

**Core idea.** 給定一個 **靜態的 dataset** $\mathcal{D} = \{(s, a, r, s')\}$（由未知 behavior policy 收集），不能再與環境互動，學一個 policy 使其表現超過 behavior。核心難題是 **distribution shift**：學到的 policy 在 OOD 動作上的 Q 估計沒有資料約束，會「幻想」出很高的值。

**代表方法。**
- **BCQ** (Fujimoto et al., ICML 2019 [^fujimoto2019bcq])：強制 policy 只選與 behavior 相近的動作。
- **CQL** (Kumar et al., NeurIPS 2020 [^kumar2020cql])：在 critic loss 加 conservative penalty，明確壓低 OOD action 的 Q。
- **IQL** (Kostrikov et al., ICLR 2022 [^kostrikov2022iql])：用 expectile regression 學 $V$，再做 advantage-weighted regression 取 policy，完全避開對 OOD 動作的 query。
- **Decision Transformer / Trajectory Transformer**：序列建模路線。

**Advantages.** 不需要環境互動，適合 **昂貴/不安全/不可逆** 的場景（醫療、金融、自駕真實道路）。

**Weaknesses.** 上限受限於 behavior policy 覆蓋範圍；對 OOD 的處理仍是 open problem；缺少 well-established benchmark 之外的真實成功案例。

**Typical applications.** Medical AI（ICU 治療策略）、推薦系統、自駕（從 fleet 紀錄學）、機器人從 demonstration 學。

### 1.2.10 Hierarchical RL (HRL)

**Core idea.** 把長時域決策拆成兩層：**high-level policy** 選擇 sub-goal 或 option（持續多個 timestep 的動作）；**low-level policy** 在 option 內執行 primitive actions。經典框架是 **Options framework** (Sutton, Precup, Singh, 1999 [^sutton1999options])；現代代表如 **FuN** (FeUdal Networks, Vezhnevets et al., ICML 2017 [^vezhnevets2017fun]) 和 **HIRO** (Nachum et al., NeurIPS 2018 [^nachum2018hiro])。

**Advantages.** 緩解 sparse reward 與 long-horizon credit assignment；sub-policy 可重用；天然有可解釋性（可以看到 sub-goal）。

**Weaknesses.** 怎麼自動發現 option 仍是 open problem；high-level 與 low-level 的訓練常彼此干擾；在純 end-to-end 大模型時代（如 OpenVLA、π0）反而被 flat policy 打過。

**Typical applications.** Long-horizon robotics、multi-room navigation、Minecraft 類的開放世界任務。

---

[^mnih2015]: Mnih, V. et al. "Human-level control through deep reinforcement learning." *Nature*, 518, 529–533 (2015).
[^vanhasselt2016]: van Hasselt, H., Guez, A., & Silver, D. "Deep reinforcement learning with double Q-learning." *AAAI* (2016).
[^schulman2017ppo]: Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. "Proximal policy optimization algorithms." *arXiv:1707.06347* (2017).
[^andrychowicz2021]: Andrychowicz, M. et al. "What matters in on-policy reinforcement learning? A large-scale empirical study." *ICLR* (2021).
[^mnih2016a3c]: Mnih, V. et al. "Asynchronous methods for deep reinforcement learning." *ICML* (2016).
[^haarnoja2018sac]: Haarnoja, T., Zhou, A., Abbeel, P., & Levine, S. "Soft actor-critic." *ICML* (2018).
[^fujimoto2018td3]: Fujimoto, S., Hoof, H., & Meger, D. "Addressing function approximation error in actor-critic methods." *ICML* (2018).
[^schrittwieser2020muzero]: Schrittwieser, J. et al. "Mastering Atari, Go, chess and shogi by planning with a learned model." *Nature*, 588, 604–609 (2020).
[^chen2021dt]: Chen, L. et al. "Decision Transformer: Reinforcement learning via sequence modeling." *NeurIPS* (2021).
[^fujimoto2019bcq]: Fujimoto, S., Meger, D., & Precup, D. "Off-policy deep reinforcement learning without exploration." *ICML* (2019).
[^kumar2020cql]: Kumar, A., Zhou, A., Tucker, G., & Levine, S. "Conservative Q-learning for offline reinforcement learning." *NeurIPS* (2020).
[^kostrikov2022iql]: Kostrikov, I., Nair, A., & Levine, S. "Offline reinforcement learning with implicit Q-learning." *ICLR* (2022).
[^sutton1999options]: Sutton, R. S., Precup, D., & Singh, S. "Between MDPs and semi-MDPs: A framework for temporal abstraction in reinforcement learning." *Artificial Intelligence*, 112(1-2), 181–211 (1999).
[^vezhnevets2017fun]: Vezhnevets, A. S. et al. "FeUdal networks for hierarchical reinforcement learning." *ICML* (2017).
[^nachum2018hiro]: Nachum, O., Gu, S. S., Lee, H., & Levine, S. "Data-efficient hierarchical reinforcement learning." *NeurIPS* (2018).
