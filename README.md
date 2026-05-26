# HW4 — DRL Survey & AI Harness

本 repo 同時提供兩個版本的作業內容，可依需要分別瀏覽：

| 版本 | 主題 | 入口 |
|---|---|---|
| **A** | 2024–2026 DRL / Foundation Models / Agentic AI 全景式文獻綜述 + 兩個 hands-on MVP | [`A_DRL_Survey/README.md`](A_DRL_Survey/README.md) |
| **B** | 「DRL Research Assistant」AI Harness 系統設計 — LLM controller + 4 個工具 + workflow orchestration | [`B_AI_Harness/README.md`](B_AI_Harness/README.md) |

---

## Version A — DRL Survey & Agentic AI

11,575 字 / 100+ 引用 / 兩個 working demo。

從 DRL 演算法基礎（DQN → Decision Transformer）→ 系統平台 → Agentic AI → 三個應用領域（Robotics、Game、Science）→ 2025–2026 五條 SOTA 主軸 → 比較分析 → GitHub 生態 → Bonus MVP（PPO + ReAct LLM agent）→ 結論。完整 IEEE/ACM 格式報告 + 15 張簡報 + GitHub Pages live demo。

## Version B — AI Harness Systems Design

≤5 頁報告 + Infographic + log.md + working MVP。

選定場景：**DRL Research Assistant** — 一個能幫研究生自動做文獻綜述的 LLM-driven 系統。

- **LLM controller** + **4 工具**（`arxiv_search` / `paper_summarize` / `citation_format` / `note_save`）+ **短期 + 長期 memory**
- **Plan → Search → Read → Critic → Compile** 五段 orchestration
- **完整 evaluation 指標**（coverage / citation accuracy / latency / cost / user rubric）
- **可執行 MVP**（無 API key 也能跑 offline 版本）

> Version B 是「能寫出 Version A 的系統設計」，兩版互為鏡像。

---

## 補充

- [`AI_CHAT/`](AI_CHAT/) — 開發過程中的 AI 協作對話紀錄（可追溯佐證）
