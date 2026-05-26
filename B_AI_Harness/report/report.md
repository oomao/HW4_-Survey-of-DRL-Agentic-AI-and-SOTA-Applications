---
title: "AI Harness Design: A DRL Research Assistant"
subtitle: "Homework 4 (AI Harness Systems Design and Analysis)"
author: "csm088220"
date: "May 2026"
papersize: a4
geometry: "a4paper, margin=2.2cm"
fontsize: 11pt
numbersections: true
toc: false
---

# AI Harness Design: A DRL Research Assistant

> *"The best demo of an AI Harness for literature survey is one that could have written this course's other deliverable."*
> — Project tagline; cross-references `../A_DRL_Survey/` (this HW4's other version).

## 1. Problem Definition & Use Case

### 1.1 痛點

對於修 DRL 課程的研究生，**為一個新主題做文獻綜述**是反覆出現、耗時且容易遺漏 SOTA 的工作：
- arXiv 每天上百篇新 paper；
- 不同主題涵蓋面廣（VLA / Diffusion Policy / RLHF / Sim2Real ...）；
- 引用格式（IEEE / ACM / BibTeX）轉換手動費時；
- 主題之間的 cross-cutting insight（如「五條 SOTA 主軸的交叉點」）需要 across-paper synthesis。

### 1.2 目標使用者

| Persona | 用途 | 典型 query |
|---|---|---|
| 研究生 | HW 文獻綜述 | "幫我整理 2024–2026 robotics VLA 模型的 SOTA" |
| 研究員 | 進入新領域 | "AlphaGo lineage 12 年的演化重點？" |
| 寫論文者 | 蒐集 Related Work | "PPO 與 GRPO 的關鍵差異？" |

### 1.3 為什麼用 AI Harness（而不是單一 LLM 對話）

單純把問題丟給 ChatGPT 有三個 fundamental 問題：(1) **知識截止** — LLM 不知道 2025–2026 新 paper；(2) **幻覺引用** — LLM 常編造看似真實但不存在的 arXiv ID；(3) **無 stateful 規劃** — 無法把大型查詢拆解成多階段執行並彙整。

AI Harness 用 **LLM as controller + 外部工具 + 記憶體** 解這三點：工具給 LLM「即時 + 可驗證」的事實，memory 維持跨輪 state，orchestration 確保複雜任務不會丟步驟。

---

## 2. AI Harness System Architecture

```
                    ┌─────────────────────┐
                    │     User Query       │
                    └──────────┬──────────┘
                               ▼
        ╔══════════════════════════════════════════════╗
        ║              LLM CONTROLLER                  ║
        ║         (Claude Haiku 4.5 by default)        ║
        ║                                              ║
        ║   ┌─────────┐  ┌─────────┐  ┌─────────┐    ║
        ║   │ Planner │→│ Reasoner│→│ Critic  │      ║
        ║   └─────────┘  └─────────┘  └─────────┘    ║
        ║                    │                         ║
        ║                    ▼                         ║
        ║              ┌─────────┐                     ║
        ║              │Compiler │                     ║
        ║              └─────────┘                     ║
        ╚════════╤═════════════════════════╤═══════════╝
                 │                         │
        ┌────────▼────────┐       ┌────────▼─────────┐
        │     MEMORY      │       │      TOOLS       │
        │                 │       │                  │
        │ Short-term:     │       │ T1 arxiv_search  │
        │   conversation  │       │ T2 paper_summarize│
        │                 │       │ T3 citation_format│
        │ Long-term:      │       │ T4 note_save     │
        │   note store    │       │                  │
        │   citation DB   │       │                  │
        └─────────────────┘       └────────┬─────────┘
                                           ▼
                                  ┌──────────────────┐
                                  │  External Services│
                                  │  arXiv API / cache│
                                  └──────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │    Structured Survey Report (Markdown)       │
                    │      with IEEE-formatted citations           │
                    └──────────────────────────────────────────────┘
```

### 2.1 三個核心元件

1. **LLM Controller** — 四個 sub-role 共用同一個 model（Claude Haiku 4.5），透過不同 system prompt 切換角色，無需多個 model instance。
2. **Memory** — 雙層：
   - *Short-term*：當輪對話 history，用 LLM 原生 context window。
   - *Long-term*：JSON-backed note store（per-topic）+ citation DB（per-paper），跨輪持久化。
3. **Tools** — 4 個 function-callable APIs，每個都有 strict JSON schema。

---

## 3. Tool Design（≥3，本系統 4 個）

每個工具設計遵循 **三原則**：(a) 單一職責；(b) 嚴格 JSON schema（input/output）；(c) 失敗時回 actionable error 而非 stack trace。

### 3.1 Tool 1 — `arxiv_search`

```python
def arxiv_search(
    query: str,
    year_min: int = 2024,
    year_max: int = 2026,
    max_results: int = 10,
) -> list[dict]:
    """
    Search arXiv for papers matching query within year range.

    Returns:
        list of {arxiv_id, title, authors, abstract, year, primary_category}
    """
```
**設計考量**：預設 `year_min=2024` 反映「SOTA 文獻優先」；`max_results=10` 平衡 coverage 與 token cost。實作支援兩個 backend：(a) 真實 arXiv API（`http://export.arxiv.org/api/query`）；(b) offline cached corpus（用於 demo + reproducibility）。

### 3.2 Tool 2 — `paper_summarize`

```python
def paper_summarize(arxiv_id: str) -> dict:
    """
    Fetch a paper's abstract and extract structured summary.

    Returns:
        {arxiv_id, title, key_contribution, methods, results,
         limitations, related_work_anchor}
    """
```
**設計考量**：輸出是 **structured** 而非 free-form summary — 強迫 LLM 抽取「contribution / method / results / limitations」四個維度，下游 Compiler 可以直接 template 化使用。

### 3.3 Tool 3 — `citation_format`

```python
def citation_format(
    paper: dict,
    style: Literal["IEEE", "ACM", "APA", "BibTeX"] = "IEEE",
) -> str:
    """Format a paper dict into a citation string in the requested style."""
```
**設計考量**：純函式（pure function），無 side effect，可單元測試。支援 4 個主流 style，預設 IEEE（DRL/AI 領域最常見）。

### 3.4 Tool 4 — `note_save`

```python
def note_save(topic: str, content: str, tags: list[str] | None = None) -> dict:
    """
    Persist a note under a topic key (acts as long-term memory).

    Returns:
        {topic, note_count, total_chars, recently_added_tags}
    """
```
**設計考量**：這是 **memory 與 tools 的橋樑** — 透過工具呼叫操作 memory，LLM 不需要直接看到底層 storage 細節。`topic` 為主鍵讓後續 Compiler 能按主題分組取出 notes。

### 3.5 Tools 比較表

| 工具 | 副作用 | 對外連線 | 失敗 mode |
|---|---|---|---|
| `arxiv_search` | 無（讀取） | 可選 arXiv API | network error → fallback to offline cache |
| `paper_summarize` | 無 | 可選 arXiv | unknown ID → 回 `{"error": "..."}` 而非 raise |
| `citation_format` | 無 | 無 | missing field → 用 `<unknown>` 占位 |
| `note_save` | **有**（寫入 JSON store） | 無 | disk full → log + return ack with `persisted: false` |

---

## 4. Workflow / Agent Orchestration

### 4.1 四階段 pipeline

```
PHASE 1  PLAN         User query → N sub-topics + dependency DAG
   │
   ▼
PHASE 2  EXECUTE      For each sub-topic (parallel-eligible):
                        ReAct loop:
                          search → top-K → summarize_each → note_save
   │
   ▼
PHASE 3  CRITIC       LLM reviews notes across sub-topics; flags gaps
                      → optionally loops back to PHASE 2 with refined query
   │
   ▼
PHASE 4  COMPILE      Notes + citations → templated Markdown report
                      → return to user
```

### 4.2 Per-sub-topic ReAct loop（PHASE 2 細節）

```
LOOP for sub_topic in plan.sub_topics:
    Thought : "What's the key recent paper for {sub_topic}?"
    Action  : arxiv_search(sub_topic, year_min=2024)
    Obs     : [paper1, paper2, ..., paperK]

    for paper in top-K:
        Thought : "Summarize paper {paper.id}."
        Action  : paper_summarize(paper.id)
        Obs     : {key_contribution, methods, ...}

        Action  : note_save(sub_topic, formatted_summary, tags=[...])
        Obs     : {topic, note_count, ...}

    Thought : "Coverage check — am I missing a major angle?"
    if yes:
        Action  : arxiv_search(refined_query)
        ... (back to top of inner loop)
```

### 4.3 Sequence Diagram（簡化版）

```
User    Controller    arxiv_search  paper_summarize  note_save  citation_format
 │           │             │              │              │             │
 │──query──▶│             │              │              │             │
 │           │─plan(N)────▶│             │              │             │
 │           │◀── plan ────│             │              │             │
 │           │                                                         │
 │           │ for each sub-topic ──────────────────────────────────── │
 │           │──search(q)─▶│             │              │             │
 │           │◀─[papers]───│             │              │             │
 │           │                                                         │
 │           │ for each top paper ────────────────────────────────────│
 │           │──summarize─────────────▶│              │             │
 │           │◀──── {contrib, methods, limits} ───│              │   │
 │           │──note_save──────────────────────────▶│             │   │
 │           │◀── ack ─────────────────────────────│             │   │
 │           │                                                         │
 │           │──critic-loop (self-prompt, may trigger more searches) ─│
 │           │                                                         │
 │           │──cite_each────────────────────────────────────────────▶│
 │           │◀── [IEEE strings] ─────────────────────────────────────│
 │           │                                                         │
 │           │──compile(template)──────────────────────────────────── │
 │◀── report─│                                                         │
```

### 4.4 Decision-making 機制

LLM Controller 用三類 prompt 切換角色：

1. **Planner prompt**："分解 user query 為 sub-topics、估計每個的 paper 數量、產生 DAG"。輸出格式 enforced via JSON schema。
2. **Reasoner prompt**：ReAct 形式（`Thought / Action / Observation`），每輪只允許單一 action。
3. **Critic prompt**："給定當前 notes，是否有 missing aspect？若有列出 refined queries"。
4. **Compiler prompt**："給定 notes + citations，按 IEEE 結構（abstract, sections, refs）產生 Markdown"。

每個 prompt 都明確 enforce 輸出格式，避免 free-form 漂移。Tool call schema 用 Anthropic / OpenAI 的 function calling spec 表達。

---

## 5. Evaluation Framework

### 5.1 量化指標

| 指標 | 定義 | 量法 | 目標 |
|---|---|---|---|
| **Coverage** | F1 of retrieved vs expert-curated paper list | 5 個 fixed query × 專家標註 ground truth | ≥ 0.7 |
| **Citation accuracy** | % of citations whose arxiv_id 真實存在 | 隨機抽 10 條 → arxiv.org 查 | ≥ 95% |
| **Latency** | End-to-end wallclock for full report | 5 個 fixed query 平均 | ≤ 120 s |
| **Token cost** | Sum of input+output tokens × price | 用 Anthropic API usage | ≤ $0.50 / query |
| **Tool call efficiency** | (useful calls) / (total calls) | manual annotation | ≥ 80% |

### 5.2 質性指標（rubric）

5 點 Likert（1=很差，5=很好），3 位 evaluator 平均：

| 維度 | 觀察點 |
|---|---|
| Helpfulness | 報告是否回答 user 的真實意圖 |
| Accuracy | 引用 / 事實是否正確 |
| Completeness | 是否漏掉重要 SOTA |
| Clarity | 結構是否易讀、insight 是否清楚 |
| Novelty | 是否提出 cross-paper synthesis |

**目標**：≥ 4/5 平均。

### 5.3 Ablation 計畫

| 組別 | 描述 | 預期觀察 |
|---|---|---|
| Full | 完整 4-phase pipeline | Baseline |
| − Critic | 跳過 PHASE 3 | Coverage 降，但 latency 減半 |
| − Planner | 不做 sub-topic 分解，single ReAct loop | Coverage / clarity 降 |
| Mock LLM | offline deterministic planner | 用於 CI 測試 reliability |

### 5.4 失敗 mode 與防護

| Failure | 防護 |
|---|---|
| LLM 幻覺 arxiv_id | `paper_summarize` 對未知 ID 回 error，不靜默填預設值 |
| 工具迴圈呼叫 | 每個 phase 設 `max_steps`；超過 → fall back to compile with existing notes |
| Reward hacking style 行為（LLM 假裝寫了 note 但沒呼叫工具） | Compiler 只用 note store 中**實際存在**的 entries；不接受 LLM inline 編造的 fact |
| 網路 / API failure | offline cache fallback；標記 `[OFFLINE_DEMO_MODE]` |

---

## 6. Implementation & Demo（accompanying MVP）

詳見 `code/`：
- `code/tools.py` — 4 個工具的實作（offline corpus + 可選真實 arXiv API）
- `code/harness_demo.py` — Plan / Reason / Critic / Compile 四段 controller
- `code/requirements.txt`
- `artifacts/demo_run.md` — 一次完整的 demo trace（query：「Survey robotics VLA models 2024-2026」）

**MVP scope**（刻意保持小）：

- 用 ~400 行 Python 完整實作 4-phase pipeline；
- 兩個 LLM backend：Claude（API key 可選）/ offline deterministic planner（CI-safe）；
- 跑一個 query 產出 ~600 字 mini-survey + 5 條 IEEE 引用，可端對端 reproduce。

---

## 7. Conclusion

本 AI Harness 設計用 **「LLM as controller + 4 個專責工具 + 雙層 memory + 4-phase orchestration」** 的架構解決「研究生做 DRL 文獻綜述」的具體問題。三個設計重點：

1. **Tool 設計重 strict schema 與 fail-safe**——LLM 永遠在 tool spec 邊界內工作。
2. **Orchestration 用 plan→execute→critic→compile 四段** 而非單一 ReAct loop，讓系統能處理需要 cross-paper synthesis 的複雜任務。
3. **Evaluation 同時量化（coverage / accuracy / cost）與質化（rubric）**，並設計 ablation 區隔每個元件的貢獻。

更廣的 lesson：**「AI Harness 的競爭力不在 LLM 多強，而在 system design 多嚴謹」**——這也是 Anthropic MCP、OpenAI Operator、Claude Code 等業界系統共同的方法論。

---

\textit{See `log.md` for the AI-assisted iterative design process; see `infographic/architecture.html` for the full visual system diagram.}
