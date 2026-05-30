---
marp: true
theme: default
paginate: true
size: 16:9
header: 'HW4-B — AI Harness · DRL Research Assistant'
footer: 'csm088220 · 2026'
style: |
  section { font-family: "Microsoft JhengHei", "PMingLiU", sans-serif; font-size: 22px; }
  h1 { color: #0ea5e9; }
  h2 { color: #0c4a6e; border-bottom: 2px solid #0ea5e9; padding-bottom: 4px; }
  table { font-size: 18px; }
  code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; }
  .small { font-size: 16px; color: #64748b; }
  .good { color: #15803d; font-weight: 700; }
---

# AI Harness Design — A DRL Research Assistant

## An LLM-driven system that writes literature surveys

HW4 Version B (AI Harness Systems Design and Analysis)
csm088220 · 2026

<small style="color:#94a3b8">10–15 min presentation · Marp-compatible Markdown</small>

---

## 投影片大綱（14 張，10–15 min）

1. Title
2. Problem：寫 DRL survey 為什麼痛？為何用 Harness 而非 ChatGPT
3. System architecture（LLM controller + tools + memory）
4. 4 個工具設計（strict schema + fail-safe）
5. Orchestration：4-phase pipeline
6. 關鍵設計 ①：cross-topic dedup
7. 關鍵設計 ②：Critic loop 真的會觸發
8. 關鍵設計 ③：Compiler 只信 note store（反幻覺）
9. Evaluation — 實測數字
10. Ablation — 隔離每個 phase 的貢獻
11. Failure-mode defense
12. Live demo + tests
13. Conclusion：thesis + 與 Version A 的鏡像關係
14. Q&A

---

## 2. Problem — 為什麼用 AI Harness，而不是直接問 ChatGPT？

**痛點**：研究生為新主題做 DRL 文獻綜述 —— arXiv 每天上百篇、引用格式手動轉、跨 paper synthesis 全靠自己。

**單一 LLM 對話的三個 fundamental 問題：**
1. **知識截止** — 不知道 2025–2026 新 paper
2. **幻覺引用** — 常編造看似真實但不存在的 arXiv ID
3. **無 stateful 規劃** — 無法把大查詢拆成多階段並彙整

> AI Harness = **LLM as controller + 外部工具 + 雙層 memory + 4-phase orchestration**，逐一解這三點。

---

## 3. System Architecture

```
User Query
   ▼
LLM CONTROLLER  (Claude Haiku 4.5 預設 / offline planner)
   Planner → Reasoner(ReAct) → Critic → Compiler
   │                    │
   ▼                    ▼
MEMORY (short+long)   TOOLS  T1..T4 ──► arXiv / offline cache
   │
   ▼
Structured Survey Report (Markdown + IEEE refs)
```

- **Controller**：四個 sub-role 共用同一 model，用不同 system prompt 切換。
- **Memory**：short-term = context window；long-term = JSON note store（per-topic）。

<span class="small">完整 6-panel 視覺化見 infographic/architecture.html</span>

---

## 4. 四個工具（≥3 ✓；strict schema + fail-safe）

| # | Tool | 簽章 | 副作用 / 失敗 mode |
|---|---|---|---|
| 1 | `arxiv_search` | (query, year_min, year_max, max_results) → list[paper] | 無；無結果→空 list |
| 2 | `paper_summarize` | (arxiv_id) → {contribution, methods, results, limitations} | 無；未知 ID → `{error}`（不 raise） |
| 3 | `citation_format` | (paper, style∈IEEE/ACM/APA/BibTeX) → str | 無（純函式）；缺欄位 → `<unknown>` |
| 4 | `note_save` | (topic, content, tags?, **meta?**) → ack | **寫** notes.json；disk error → `persisted:false` |

> 三原則：**單一職責 · 嚴格 JSON schema · 失敗回 actionable error 而非 stack trace。**

---

## 5. Orchestration — 4-Phase Pipeline

```
PLAN     user query → 2–4 sub-topics
  ▼
EXECUTE  (a) search 每個 sub-topic（relevance-scored）
         (b) cross-topic DEDUP：每篇 paper → 最相關的單一 sub-topic
         (c) summarize（memoized）→ note_save(meta)
  ▼
CRITIC   binary coverage check；某 sub-topic = 0 篇 → 放寬年份 re-search（≤1 round）
  ▼
COMPILE  從 note store 的 meta 重建 → Markdown + IEEE refs
```

> 不是單一 ReAct loop —— 是能處理 cross-paper synthesis 的多階段流程。

---

## 6. 關鍵設計 ① — Cross-topic Dedup

**問題**：同一篇 paper 會在多個 sub-topic 的搜尋結果中重複出現。

**做法**：summarize 之前，依 relevance score 把每篇 paper 指派給**唯一最相關**的 sub-topic（平手取較前者）。

**效果：**
- 報告正文 / 比較表 **0 重複 paper**
- 同一篇 **只 summarize 一次**（memoized）→ tool 效率 100%

```
search 3 topics → dedup → VLA: [Magma, OpenVLA] ·
                          Humanoid: [GR00T, Gemini, Pi-0.5] ·
                          Diffusion Policy: []  ← 被清空！
```

---

## 7. 關鍵設計 ② — Critic Loop 真的會觸發

dedup 把 `Diffusion Policy` 清成 **0 篇**（真正的 Diffusion Policy 是 2023、被 `year_min=2024` 濾掉）。

```
[CRITIC] Post-dedup coverage: VLA=2, Diffusion Policy=0, Humanoid=3
[CRITIC] Coverage GAP on ['Diffusion Policy'] → 放寬年份 re-search
[EXECUTE] arxiv_search('diffusion policy robot', year_min=2022)
          → recovers Diffusion Policy (arXiv:2303.04137, RSS 2023)
```

> orchestration 的價值具體可見：**dedup 暴露 coverage gap，Critic 用「放寬年份」這個非平凡決策補上。** 不是 dead code。

---

## 8. 關鍵設計 ③ — Compiler 只信 note store（反幻覺）

- 每次 `note_save` 都附**結構化 `meta`**（paper record）。
- Compiler **只**讀 note store 的 `meta` 重建報告 —— 不接受任何 LLM inline 編造的 paper ID 或 fact。

**可量測的保證**：
<span class="good">citation accuracy = 100%</span> —— 每一條被引用的 arXiv ID 都實際存在於 corpus（由測試 `test_pipeline_every_cited_id_exists_in_corpus` 守住）。

> 「System design 的核心是決定**哪一條 channel 才是 source of truth**。」

---

## 9. Evaluation — 實測數字（`python code/eval.py`）

| Query | Papers | **F1** | Citation acc. | Efficiency | Critic |
|---|---|---|---|---|---|
| Robotics VLA 2024-26 | 6 | **1.00** | 100% | 100% | 1 |
| LLM alignment & reasoning RL | 5 | 0.67 | 100% | 100% | 0 |
| Game AI agents | 7 | 0.55 | 100% | 100% | 0 |
| **Macro avg** | | **0.74** | **100%** | **100%** | |

- Coverage F1 macro **0.74**（過 0.70 門檻）；duplicate papers **0**。
- Q2/Q3 較低是**誠實結果** —— keyword planner 對廣度 query 的限制，換真 LLM planner 可改善。

---

## 10. Ablation — 隔離每個 phase 的貢獻

Flagship query: *"Survey robotics VLA models in 2024-2026"*

| 組別 | Papers | **F1** | Critic rounds |
|---|---|---|---|
| **Full**（plan+critic） | 6 | **1.00** | 1 |
| − Critic | 5 | 0.91 | 0 |
| − Planner（single ReAct） | 4 | 0.80 | 0 |

- 拿掉 **Critic** → 補不回 seminal Diffusion Policy（F1 1.00 → 0.91）。
- 拿掉 **Planner** → 3 sub-topics 塌成 1（F1 → 0.80）。

> 每個 phase 都掙到它的存在價值。

---

## 11. Failure-Mode Defense（已落實於程式）

| Failure | 防護 | 程式對應 |
|---|---|---|
| LLM 幻覺 arxiv_id | 未知 ID 回 `{error}`，不靜默填值 | `paper_summarize` |
| 假裝寫 note 沒呼叫工具 | Compiler 只讀 store 的 meta | `view_from_store` |
| 同篇 paper 重複 | summarize 前 cross-topic dedup | `assign_papers` |
| Critic perfectionist loop | binary check + `max_critic_rounds=1` | `critic_review` |
| 網路 / API failure | offline cached corpus fallback | `arxiv_search` |

---

## 12. Live Demo + Tests（offline，無需 API key）

```bash
python code/harness_demo.py     # 端到端
python code/eval.py             # evaluation + ablation
python -m pytest code/test_harness.py   # → 15 passed
```

**預設 query 一次跑完：**
<span class="small">3 sub-topics · <span class="good">6 papers · 0 重複</span> · 6 IEEE refs · 22 tool calls · <span class="good">效率 100%</span> · critic 觸發 1 輪 · 0.04 s</span>

- Transcript：`artifacts/demo_run.md`（含 critic loopback）
- 成品：`artifacts/compiled_report.md`
- 持久化 memory：`artifacts/notes.json`（含結構化 meta）

---

## 13. Conclusion — Thesis + 與 Version A 的鏡像

**核心 thesis**：AI Harness 的競爭力不在 LLM 多強，而在 **system design 多嚴謹**。

- 哪些事 LLM 負責（reasoning / planning）、哪些 tool 負責（事實 / state）、哪些 system 負責（schema / dedup / fallback）—— 邊界畫清楚後，**LLM 反而是最 commoditized 的部分**。

**A ↔ B 鏡像**：
- **Version A** 是 pipeline 的 *output*（一份 11,575 字 survey）。
- **Version B** 是能 *生成* 那種 survey 的 *system*。

> 這正是 Anthropic MCP / Claude Code / OpenAI Operator 的共同方法論。

---

## 14. Q&A

Thanks for listening!

**Infographic：** [`infographic/architecture.html`](../infographic/architecture.html)
**書面報告（≤5 頁）：** [`report/report.html`](../report/report.html) · [PDF](../report/report.pdf)
**Code：** [`code/harness_demo.py`](../code/harness_demo.py) · [`code/tools.py`](../code/tools.py) · [`code/eval.py`](../code/eval.py)
**設計過程：** [`log.md`](../log.md)（14 iterations）

<span class="small">offline 完全可重現 · 15 tests green · macro F1 0.74 · citation accuracy 100%</span>
