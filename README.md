# HW4 — Two-Version Submission

DRL 作業 4。老師發布了兩版 syllabus，本資料夾**同時繳交兩個版本**，讓老師按實際採用版本評分。

| 版本 | 適用 syllabus | 主題 | 入口 |
|---|---|---|---|
| **A** | 原 syllabus（DRL Survey + Agentic AI） | 2024–2026 DRL / Foundation Models / Agentic AI 全景式文獻綜述 + 兩個 hands-on MVP | [`A_DRL_Survey/README.md`](A_DRL_Survey/README.md) |
| **B** | 新 syllabus（AI Harness Systems Design） | 設計一個「DRL Research Assistant」AI Harness — LLM controller + 4 個工具 + workflow orchestration | [`B_AI_Harness/README.md`](B_AI_Harness/README.md) |

---

## 各版本一句話

### A — DRL Survey & Agentic AI（11,575 字 / 100+ 引用 / 兩個 working demo）
從 DRL 演算法基礎（DQN→Decision Transformer）→ 系統平台 → Agentic AI → 三個應用領域（Robotics、Game、Science）→ 2025-2026 五條 SOTA 主軸 → 比較分析 → GitHub 生態 → Bonus MVP（PPO + ReAct LLM agent）→ 結論。完整 IEEE/ACM 格式報告 + 15 張簡報 + GitHub Pages live demo。

### B — AI Harness Systems Design（≤5 頁報告 + Infographic + log.md + working MVP）
選定場景：**DRL Research Assistant**——一個能幫研究生自動做文獻綜述的 LLM-driven 系統。設計：
- **LLM controller** + **4 工具**（`arxiv_search` / `paper_summarize` / `citation_format` / `note_save`）+ **短期 + 長期 memory**
- **Plan → Search → Read → Critic → Compile** 五段 orchestration
- **完整 evaluation 指標**（coverage / citation accuracy / latency / cost / user rubric）
- **可執行 MVP**（無 API key 也能跑 offline 版本）

> Version B 是「能寫出 Version A 的系統設計」，兩版互為鏡像。

---

## 為什麼兩版都做？

1. **覆蓋老師可能採用的任一版本** — 避免猜錯。
2. **內容互補**：Version A 是「end-product survey」、Version B 是「meta-system 設計」——可以同時展示理論深度與系統設計能力。
3. **共享資產**：Version B 的 LLM agent demo 是 Version A 中 Bonus C 的延伸版本，code reuse 顯而易見。

---

## 評分對應快速表

### 若採用原 syllabus → 看 `A_DRL_Survey/`
| 評分 | 對應 |
|---|---|
| Literature Survey Depth 25% | Part 1–7 + 100+ refs |
| Technical Understanding 25% | Part 1 critical view + Part 6 deep dive |
| SOTA Analysis 20% | Part 3 + 4 + 5（重點 2024-26） |
| Comparative Discussion 15% | Part 6 比較表 + 演化譜系 |
| Report Quality 10% | HTML 排版 + IEEE 格式 |
| Presentation 5% | `slides/slides.md`（15 張） |

### 若採用新 syllabus → 看 `B_AI_Harness/`
| 評分 | 對應 |
|---|---|
| AI 系統設計完整性 35% | `report/report.md` §2 + Infographic |
| Tool / Orchestration 設計 25% | `report/report.md` §3-4 + `code/tools.py` |
| Workflow 與邏輯清晰度 20% | `report/report.md` §4 + 序列圖 |
| Infographic 視覺表達 10% | `infographic/architecture.html` |
| log.md 設計過程紀錄 10% | `log.md` |
