# HW4 Version B — AI Harness Systems Design

> **DRL Research Assistant** — an LLM-driven harness that automates DRL literature surveys.
> Submitted under the *AI Harness Systems Design and Analysis* syllabus.

**Live infographic：** [`infographic/architecture.html`](infographic/architecture.html)
**完整書面報告（HTML）：** [`report/report.html`](report/report.html) · [Markdown 原稿](report/report.md)
**設計過程紀錄：** [`log.md`](log.md)
**Live demo 入口：** [`docs/index.html`](docs/index.html)

---

## 一、選定場景

**問題**：研究生（含我自己）為新主題做 DRL 文獻綜述時，arXiv 每天上百篇、引用格式手動轉換、跨 paper 的 synthesis 全靠自己 — 既慢又容易漏 SOTA。

**目標 user**：DRL 研究生 / 研究員 / 寫 paper 的人。

**為什麼用 AI Harness 而不是 ChatGPT 直接問？**
1. LLM 不知道 2025–2026 新 paper（知識截止）。
2. LLM 常**幻覺**看似真實但不存在的 arXiv ID。
3. LLM 無 stateful 規劃，無法把大型查詢拆成多階段並彙整。

AI Harness 用 **LLM-as-controller + 外部工具 + 雙層 memory + 4-phase orchestration** 解這三點。

---

## 二、系統架構

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       ▼
╔═══════════════════════════════════════╗
║       LLM CONTROLLER                  ║
║  ① Planner → ② Reasoner → ③ Critic →  ║
║              ④ Compiler               ║
╚════════╤═════════════════╤════════════╝
         │                 │
   ┌─────▼─────┐     ┌─────▼─────┐
   │  MEMORY   │     │   TOOLS   │
   │ short+long│     │  T1..T4   │
   └───────────┘     └─────┬─────┘
                           ▼
                  ┌─────────────────┐
                  │ arXiv / cache   │
                  └─────────────────┘
                           │
                ┌──────────▼──────────┐
                │  Structured Report   │
                └──────────────────────┘
```

詳見視覺化：[`infographic/architecture.html`](infographic/architecture.html)

---

## 三、四個工具（≥3 ✓）

| # | Tool | 簽章 | 副作用 |
|---|---|---|---|
| 1 | `arxiv_search` | `(query, year_min, year_max, max_results) → list[paper]` | None |
| 2 | `paper_summarize` | `(arxiv_id) → {contribution, methods, results, limitations}` | None |
| 3 | `citation_format` | `(paper, style ∈ {IEEE,ACM,APA,BibTeX}) → str` | None |
| 4 | `note_save` | `(topic, content, tags?) → {persisted, note_count, ...}` | **Write** to `artifacts/notes.json` |

每個工具的 **strict JSON schema** 在 `code/tools.py` 中 `TOOL_SCHEMAS` 變數。

---

## 四、Workflow（4 Phases）

```
PLAN  ──▶  EXECUTE (per sub-topic ReAct)  ──▶  CRITIC  ──▶  COMPILE
                              ↑                    │
                              └────────────────────┘
                              re-search if gap (max 1 round)
```

詳細的 per-phase 邏輯、sequence diagram、failure mode 請見 [`report/report.md`](report/report.md) §4 與 [`infographic/architecture.html`](infographic/architecture.html) 區塊 2-3。

---

## 五、Evaluation

| 類型 | 指標 | 目標 |
|---|---|---|
| 量化 | Coverage F1, citation accuracy, latency, token cost, tool-call efficiency | F1 ≥ 0.7 / accuracy ≥ 95% / ≤ 120s / ≤ $0.50 / efficiency ≥ 80% |
| 質性 | 5-pt Likert × 5 維度（helpfulness, accuracy, completeness, clarity, novelty） | 平均 ≥ 4/5 |
| Ablation | full / −critic / −planner / mock LLM | 隔離每個 phase 的貢獻 |

---

## 六、實際 demo（已跑過）

```powershell
pip install -r code/requirements.txt   # anthropic 為可選，offline 也能跑
python code/harness_demo.py            # 跑預設 query
python code/harness_demo.py "Survey foundation agents in 2024-2026"   # 自訂
```

**實際輸出：**
- 預設 query "Survey robotics VLA models in 2024-2026" → **3 sub-topics、9 papers、4 unique IEEE citations**、25 tool calls，wallclock **0.04 s**（offline backend）。
- Transcript: [`artifacts/demo_run.md`](artifacts/demo_run.md)
- 純報告: [`artifacts/compiled_report.md`](artifacts/compiled_report.md)
- 持久化 notes: [`artifacts/notes.json`](artifacts/notes.json)

---

## 七、目錄結構

```
B_AI_Harness/
├── README.md                       ← 你在這
├── report/
│   ├── report.md                   ← 2-5 頁書面報告（Markdown）
│   ├── report.html                 ← HTML（瀏覽器 Print → PDF）
│   └── build_html.py
├── infographic/
│   └── architecture.html           ← 自含 SVG 視覺化（含 6 區塊）
├── log.md                          ← AI-assisted design process（11 次 iteration）
├── code/
│   ├── tools.py                    ← 4 個工具實作 + 15 篇 mini paper corpus
│   ├── harness_demo.py             ← 4-phase orchestrator
│   └── requirements.txt
├── artifacts/                      ← demo 輸出（會被覆蓋）
│   ├── demo_run.md
│   ├── compiled_report.md
│   └── notes.json
└── docs/
    └── index.html                  ← Live demo 入口
```

---

## 八、評分對應（按 syllabus 比例）

| 評分項 | 權重 | 對應證據 |
|---|---|---|
| **AI 系統設計完整性** | 35% | `report/report.md` §2 系統架構 + `infographic/architecture.html` 區塊 1 |
| **Tool / Orchestration 設計** | 25% | `report/report.md` §3-4 + `code/tools.py` + `code/harness_demo.py` |
| **Workflow 與邏輯清晰度** | 20% | `report/report.md` §4 + `infographic/architecture.html` 區塊 2-3 |
| **Infographic 視覺表達** | 10% | `infographic/architecture.html`（6 panel SVG） |
| **log.md 設計過程紀錄** | 10% | `log.md`（11 次 iteration + 11 條 decision table） |

**Bonus**：完整實作 MVP + 端到端 demo + cross-link 到 Version A，形成 narrative arc。

---

## 九、與 Version A 的關係

**Version A** 是 DRL Survey 的 *output*（一份 11,575 字的綜述）。
**Version B** 是能 *生成* Version A 那種 survey 的系統。

兩者形成「**成品 ↔ 工具**」的鏡像。Version B 的 `code/llm_agent_demo.py` 設計也與 Version A 的 Bonus C（簡易 ReAct agent）一脈相承，是它的**生產級延伸版**（從 2 工具 + 單 ReAct loop → 4 工具 + 4-phase orchestration）。
