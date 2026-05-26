# Part 8 — Bonus MVP: Two Hands-On Demos

為了讓這份 survey **不只是文獻整理，而是 grounded in actual code**，本節提供兩個刻意輕量、但 **endpoint-runnable** 的 MVP。前者代表 Part 1–2 的「傳統 DRL 路線」（PPO + Gym），後者代表 Part 3 的「Agentic AI 路線」（tool-using ReAct agent）。

## 8.1 Bonus B — PPO on CartPole-v1（Stable-Baselines3）

### 目標與設計
- 用 Stable-Baselines3（v2.8.0）的 PPO 訓練 `CartPole-v1`。
- 跑 4 個並行 env、共 50,000 env steps、PPO 預設 hyperparameter（`lr=3e-4`、`n_steps=128`、`batch=64`、`gae_lambda=0.95`、`clip_range=0.2`）。
- 訓練完成後做 20 episode deterministic evaluation。

### 程式碼路徑
```
code/ppo_demo.py
```

### 實際結果（Windows 11 + Python 3.11 + RTX 4090，CPU PPO）
```
total_timesteps  = 50000
n_envs           = 4
seed             = 42
wallclock_sec    = 81.0
episodes         = ~400+
final_mean_eval  = 500.0 ± 0.0     # ← 完美收斂到 CartPole-v1 最高分
max_episode_ret  = 500.0
```

訓練曲線：

![PPO CartPole reward curve](../artifacts/ppo_cartpole_reward.png)

### 觀察與對應到報告本體
1. **PPO 的 sample efficiency 與穩定性**：CartPole 僅 50K env steps（< 90 秒）即收斂到 500.0；展示了 **Part 1.2.3** 提到「PPO 是最魯棒的 baseline」並非空談。
2. **on-policy 設定的計算特性**：4 envs × 128 steps = 每 update 收 512 samples，與我們在 **Part 6.2.1** 的論述一致 — PPO 在 reward scale / hyperparameter 上的魯棒性正是它成為 LLM RLHF 預設選擇的原因。
3. **可重現性**：固定 `seed=42`，整個 pipeline 從零跑到生成 reward curve 只需要一條命令。

## 8.2 Bonus C — Tool-Using ReAct Agent（Mini LLM Agent）

### 目標與設計
做一個最小可運行的 **ReAct-style agent loop**（呼應 Part 3.3 的 ReAct / Toolformer / Gorilla 系列），具備：
- 兩個工具：`calculator(expression)`、`wiki_search(query)`。
  - calculator 用 `ast`-based safe evaluator（**不用 `eval()` 避免 RCE**）。
  - wiki_search 查一個內建的迷你 DRL/AI 語料（無網路相依，部署簡單）。
- 兩個 LLM backend：
  - **Anthropic Claude**（`claude-haiku-4-5-20251001`）— 設 `ANTHROPIC_API_KEY` 即用。
  - **Offline 確定性 planner** — 無 API key 也能跑，跑出 ReAct trajectory，可作為 unit-test fixture。

### 程式碼路徑
```
code/llm_agent_demo.py
```

### 互動範例（Offline backend，跑 3 個內建問題）

**Q1: "What is sqrt(144) plus the year AlphaGo played Lee Sedol?"**
```
[USER] What is sqrt(144) plus the year AlphaGo played Lee Sedol?
[AGENT] Thought: I need AlphaGo's debut year. I'll check the wiki.
        Action: wiki_search(AlphaGo)
[TOOL]  wiki_search('AlphaGo') -> AlphaGo ... match versus Lee Sedol took place in March 2016 ...
[AGENT] Thought: Good — AlphaGo's Lee-Sedol match was in 2016. Now compute sqrt(144) + 2016.
        Action: calculator(sqrt(144) + 2016)
[TOOL]  calculator('sqrt(144) + 2016') -> 2028.0
[AGENT] FinalAnswer: sqrt(144) = 12 and AlphaGo's Lee-Sedol match was in 2016, so the answer is 2028.0.
```
這是一個**典型 multi-hop**的問題：必須先查 fact（AlphaGo），再做算術。Agent 正確 chain 兩個工具呼叫。

**Q2: "Tell me about DeepSeek-R1."**
```
[AGENT] Thought: Let me look up DeepSeek-R1.
        Action: wiki_search(DeepSeek-R1)
[TOOL]  wiki_search('DeepSeek-R1') -> DeepSeek-R1 ... pure reinforcement learning from verifiable rewards using GRPO ...
[AGENT] FinalAnswer: DeepSeek-R1 is an open-weights reasoning model trained with pure RL from verifiable rewards using GRPO. It is the first peer-reviewed LLM in Nature (2025).
```

**Q3: "Compute 2 ** 10 - 24"**
```
[AGENT] Thought: Pure arithmetic — use calculator.
        Action: calculator(2 ** 10 - 24)
[TOOL]  calculator('2 ** 10 - 24') -> 1000
[AGENT] FinalAnswer: 1000
```

### 觀察與對應到報告本體
1. **ReAct loop 的本質**：`Thought → Action → Observation` 循環是 Part 3.3 的核心 — 即使是 100 行程式碼的迷你 agent 也能展示完整的決策迴圈。
2. **Tool selection**：與 Gorilla / ToolACE 對照 — 我們手動寫了 routing rule；產業界的 SOTA 用大模型 + 微調做工具選擇，但抽象上是同一件事。
3. **Safety**：calculator 用 AST whitelist 而非 `eval()`，是 production agent 的最小安全規範 — 對應 Part 3.7.4 我們提到的「reward hacking」與「supply chain」隱憂的子集。
4. **可演進性**：把 `llm_offline` 換成 `llm_anthropic` 就升級成真實 Claude agent；可以再加 web search、bash execution 等工具 — 這正是 Claude Code、OpenAI Operator 走的路線（Part 3.1.1-3.1.2）。

## 8.3 Bonus 的 Critical Reflection

兩個 demo 故意保持小：

- **PPO demo** 不挑戰 humanoid 或 MuJoCo MJX — 因為 MVP 的目的是「在合理時間內 reproducible」。CartPole 反而最能凸顯 RL 的核心 dynamic：reward → policy update → 行為改善。要把它升級成 Atari、LunarLander 只需要改 `env_id` 與 `total_timesteps`。
- **LLM agent demo** 不寫複雜的 LangGraph workflow — 因為要展示的是「**ReAct 範式本身的簡潔性**」。一旦這個 100 行 loop 跑通，加 LangGraph、加 memory store、加 multi-agent 都是工程量的線性疊加，而非另一個 paradigm。

兩個 MVP 共同想說的話：**「DRL 不再是孤立的 algorithm，而是被 foundation models 與 agent loop 包覆的元件。」** PPO 訓的是低層 reactive policy；ReAct agent 是高層 planning loop。**真正的 SOTA（如 Helix、GR00T、Voyager）就是把這兩端整合起來。**
