# `log.md` — AI-Assisted Design Process

> 紀錄 Version B（AI Harness Systems Design）的迭代設計過程：與 AI 的對話、架構調整、設計決策、踩過的坑與修正。
> 全文按時間軸（chronological）整理，每個 step 都標時間戳。

---

## Iteration 0 — Framing the problem（與 AI 對話）

**Me（user）→ AI:**
> 老師發了新 syllabus，重點變成「AI Harness Systems Design」，要設計一個 LLM-driven 系統，必含 ≥3 個工具、workflow orchestration、evaluation。我們應該選什麼場景？

**AI 回覆（節錄）：** 列了幾個候選 — 搜尋助理 / 客服 / 資料分析代理 / 教育助理 / Coding tutor / 旅行規劃。提到 **「Coding tutor 與 DRL Research Assistant 都和你課程有強連結，後者還能與 Version A 互為鏡像」**。

**My decision：** 選 **DRL Research Assistant**，理由：
1. Version A 是「成品 survey」，B 是「能寫出 A 的系統」 — 兩個 deliverable 之間有 narrative arc。
2. 工具邊界天然清楚（search / summarize / cite / save），不會 over-engineer。
3. 我自己平常做 HW 就需要這種工具，dog-fooding 容易發現 bug。

**Decision recorded：** 場景 = DRL Research Assistant。

---

## Iteration 1 — 第一版 tool list（過度設計，被駁回）

**Me → AI:**
> 列出可能的 tools。

**AI 第一版 提了 7 個工具：**
1. `arxiv_search`
2. `paper_full_text_download`
3. `paper_summarize`
4. `citation_format`
5. `citation_dedup`
6. `note_save`
7. `report_compile`
8. `latex_render`

**My critique：** 「太多了，會違反 syllabus 強調的『邏輯一致性』與 MVP 原則。`report_compile` 不該是 tool，應該是 Compiler phase 的責任。`paper_full_text_download` 對 MVP 不必要 — abstract + structured summary 就夠寫 mini-survey。`citation_dedup` 也應該是 compile-time logic 而非 tool。」

**Decision：** 收斂為 4 個 tools：`arxiv_search` / `paper_summarize` / `citation_format` / `note_save`。

**Lesson：** Tool 過多 = 系統 surface area 過大 = bug 與 evaluation 維度爆炸。Stick to "single responsibility per tool, ≤ 5 tools total"。

---

## Iteration 2 — 架構爭論：要不要 multi-agent？

**Me → AI:**
> 要做成 multi-agent（Planner、Searcher、Reader、Compiler 各一個 LLM instance）嗎？

**AI 提了兩個方案：**
- **方案 A：4 個分離的 agent**（多 model instance、每個用不同 prompt）— 像 MetaGPT / ChatDev。
- **方案 B：單一 LLM controller、4 個 role 用不同 system prompt 切換** — 像 Claude Code 的 single-threaded master loop。

**My decision：** 走方案 B。理由：
1. **token 成本**：方案 A 每個角色都要重新讀整個 context，token cost 翻 4 倍。
2. **可觀測性**：single loop 容易 trace，bug 比較好查（multi-agent 經常變成「誰錯了？」的疑案）。
3. **學術 evidence**：Anthropic 的 Claude Code 就是 single-thread 為主，這是被驗證的設計。
4. **MVP 原則**：4 個獨立 agent 是 over-engineering 在當前任務複雜度上。

**Lesson：** Multi-agent 不是「更先進」，只是「更分散」。如果任務不需要真正的 parallel execution 或 conflicting opinion，single controller 永遠 simpler & cheaper。

---

## Iteration 3 — 設計 phase boundary

**Me → AI:**
> 已決定 single controller，但需要明確 phase。每個 phase 做什麼？

**AI 提的初稿（被部分修正）：**

| Phase | 我接受 | 我修正 |
|---|---|---|
| Plan | ✅ | — |
| Execute | ✅ | 加上 **per-sub-topic ReAct loop** 而非單一 long ReAct |
| Critic | ✅ | 設 `max_critic_rounds=1` 避免無限自我懷疑 |
| Compile | ✅ | 強制「**只能用 note store 中真實存在的 entry**」，不接受 LLM 在 compile 階段現編 |
| ~~Reflect (5th phase)~~ | ❌ 刪掉 | Compile 後再多一輪 reflection 對 MVP 是 over-engineering |

**最重要的設計決策（log）：**
> **Compiler 拒絕 LLM-inline facts。** 任何進入最終 report 的 paper 必須在 note store 中有對應 entry，且對應 entry 必須來自實際 tool call 的 observation。這道防護把 LLM 幻覺擋在系統邊界外。

**Lesson：** 不是所有資訊都應該信 LLM。System design 的核心是 **「決定哪一條 channel 才是 source of truth」**。

---

## Iteration 4 — Tool schema 設計（踩坑）

**第一次嘗試：** 我把 `paper_summarize` 設計成回 free-form text。

```python
def paper_summarize(arxiv_id: str) -> str:
    return "..."  # free-form
```

**測試發現的問題：** Compiler 階段 LLM 拿到 free-form text 後，**重新組織內容時就會略掉一些重點**，且不同 paper 的 summary 結構不一致，導致最終 report 的 sub-topic section 風格不齊。

**修正：** 改成 **structured output**。

```python
def paper_summarize(arxiv_id: str) -> dict:
    return {
        "arxiv_id": ...,
        "key_contribution": "...",
        "methods": "...",
        "results": "...",
        "limitations": "...",
    }
```

**效果：** 立即解決問題。Compiler 用 template 把 4 個欄位填到固定位置，sub-topic section 結構完全對齊。

**Lesson：** Tool 輸出設成 structured > free-form，除非你有極強的 downstream parsing。

---

## Iteration 5 — Offline backend 是不是 over-engineering？

**Me → AI:**
> 老師看作業時可能沒有 API key。我們要不要寫一個 offline deterministic planner 當 fallback？

**AI 一開始說：** 「不需要，setup 教學一下就好」。

**My pushback：** 「不，老師時間有限，且 demo 若 fail 評分會被扣。Offline 版本是必要的。」

**最終 design：**
- `choose_planner()` 偵測 `ANTHROPIC_API_KEY` 是否存在。
- 沒 key → 用 keyword-based `plan_offline()`，預設有 11 條 trigger 規則。
- 有 key → 用 Claude Haiku 4.5（成本低、快）。
- Tools 本身對兩種 backend 都通用。

**Lesson：** **「能本地跑 = 能被改 = 能被 grade」**。Demo 的可重現性比 sophistication 更重要。

---

## Iteration 6 — Critic phase 的 false positive

**第一次跑：** Critic 太敏感，每次都說「coverage 不足」要重搜，導致系統跑了 8 輪、token cost 翻倍。

**Root cause：** Critic 的 prompt 寫成「請列出所有可能改進的角度」— LLM 永遠能列出更多角度。

**修正：** 把 Critic 改成 **binary check** + `target_per_topic` 量化門檻：

```python
def critic_review(run, sub_topics, all_papers, target_per_topic=2):
    weak = [t for t in sub_topics if len(all_papers.get(t, [])) < target_per_topic]
    return weak
```

並設 `max_critic_rounds=1`，最多再搜一次就強制收尾。

**Lesson：** **Critic 不該是 perfectionist**。Critic 該回答的是 yes/no，不是「想想還能更好嗎」。

---

## Iteration 7 — note_save 的 race condition 考量

**Me 思考：** 如果 PHASE 2 真的 parallel 跑（asyncio），多個 worker 同時寫 `notes.json` 會 race。

**Solutions considered：**

| 方案 | 評估 |
|---|---|
| File lock (`fcntl`) | Windows 不直接支援，跨平台麻煩 |
| 改用 SQLite | MVP overkill |
| **改用 in-memory dict + 最後 flush** | ✅ 簡單，符合 MVP |
| 改用 `asyncio.Lock` | 假設 single-process 是 ok 的 |

**Decision：** Phase 2 在 MVP 維持 **sequential**；如果真要 parallel 再改 lock。**已記錄為 known limitation**，不在 MVP 範圍內修。

**Lesson：** 不要為了「將來可能 parallel」現在就 over-engineer。Premature optimization is the root of all evil — 但要把 known limitation 寫在 log，未來才不會誤以為這是 bug。

---

## Iteration 8 — Evaluation framework 設計

**Me → AI:**
> Evaluation 該有哪些 metric？

**AI 提了 15 個 metric。** 我砍到 5 個 quantitative + 5 個 qualitative，理由：
- 超過 10 個 metric 沒人會看；
- 每個 metric 都要 mapping 到 design decision，否則就是裝飾。

**最終 5+5 metrics：**

Quantitative：
1. Coverage F1（衡量系統是不是真的搜全）
2. Citation accuracy（衡量幻覺率）
3. Latency（衡量 UX）
4. Token cost（衡量經濟可行性）
5. Tool-call efficiency（衡量是否 over-calling）

Qualitative（5-pt Likert）：
helpfulness · accuracy · completeness · clarity · novelty

加上 **3 個 ablation 組**（−Critic / −Planner / Mock LLM），讓我能 isolate 每個 phase 的貢獻。

**Lesson：** Evaluation 設計要先問「**這個 metric 的高低會 trigger 我做什麼？**」 — 不會 trigger 任何行動的 metric 就是 vanity metric。

---

## Iteration 9 — Live demo run（debug）

**首次端到端跑：** `python code/harness_demo.py`

**問題 1：** Output 文字裡的中文破折號（—）在 Windows console 變亂碼。
**修正：** 換成 ASCII 破折號（`-`）；artifact 檔案保留中文。

**問題 2：** Diffusion Policy paper（2023 RSS）落在 `year_min=2024` 之外，所以 sub-topic 'Diffusion Policy' 搜不到本尊。
**選擇 fix or document：** **選 document**，理由：
- 這正是現實 — Diffusion Policy 是 2023 paper，2024-26 區間裡只有它的衍生作。
- 系統把相關的 follow-up（GR00T、π0.5）找出來其實是合理的 fallback。
- 這在 evaluation 的 "coverage" metric 上會反映出來，不該硬塞。

**Lesson：** Bug 與 limitation 是不同的東西 — 前者要 fix，後者要 document。錯把 limitation 當 bug 修，會把系統推向 over-fit。

---

## Iteration 10 — Infographic 設計

**首版嘗試 Mermaid：** 用 mermaid graph TD 寫 architecture，但 syllabus 強調「視覺表達 10%」需要更專業。

**改成 SVG：** 全手寫 SVG，6 個區塊：
1. 系統架構（LLM controller 中央 + tools 右側 + memory 左側 + user 上方 + output 下方）
2. 4-phase pipeline（水平 flow + critic loopback）
3. Sequence diagram（6 條 actor lane）
4. Tool spec table
5. Evaluation dashboard
6. Failure mode map

**Design choice：色彩編碼**
- User = 紫
- LLM = 藍
- Tools = 橙
- Memory = 綠
- External = 灰
- Failure / warning = 紅 / 粉

**Lesson：** Infographic 不是「圖多 = 好」，是「能 carry 故事」 — 6 個 panel 對應 report 的 6 個核心 design decision。

---

## Iteration 11 — README / docs 與 cross-link

**最後一步：** 寫 README.md 與 docs/index.html。

**Decision：** sync 跟 Version A 同樣風格（暗色 GitHub Pages 主題），讓 grader 在兩個版本之間切換 visual 一致。

**Cross-link 設計：** Version A 的 README 提到 Version B 是「能寫出 A 的系統」；Version B 的 report 第一段提到 Version A 是「同一作業的另一份 deliverable」 — 形成 mutual reference，**故事閉環**。

---

## 設計決策總表（quick scan）

| # | 決策 | 替代方案 | 為何選此 |
|---|---|---|---|
| 1 | 場景 = DRL Research Assistant | 客服 / 旅行 / coding | 與課程 + Version A 強連結 |
| 2 | 4 tools（單一職責） | 7+ tools | MVP；surface area 小 |
| 3 | Single LLM controller | Multi-agent | token cost + 可觀測性 |
| 4 | Structured tool output | Free-form text | downstream 一致性 |
| 5 | Offline deterministic backend | 強制 API key | 老師可重現 |
| 6 | Critic binary check + max_rounds=1 | Open-ended critic | 避免 perfectionist loop |
| 7 | Compiler 拒絕 LLM-inline facts | 信 LLM | 幻覺防護 |
| 8 | Sequential PHASE 2（in MVP） | Parallel + lock | 不 premature opt |
| 9 | 5 quant + 5 qual metrics | 15 metric | 可行動 metric only |
| 10 | SVG infographic（非 Mermaid） | Mermaid | 視覺品質 |
| 11 | Cross-link 兩版本 | 各自獨立 | 敘事閉環 |

---

## 未來改進清單（Out of MVP）

如果有更多時間，下列是優先級排序：

1. **真實 arXiv API integration**：目前用 cached corpus，可以加上 live `http://export.arxiv.org/api/query`。
2. **Parallel PHASE 2**：把不同 sub-topic 平行抓，配 file lock 或 in-memory + flush。
3. **Tool versioning**：當 schema 改動時，舊 trace 仍可解析。
4. **Multi-language support**：query 與 output 支援中英雙語切換。
5. **Web UI**：包成 FastAPI + 簡單前端，讓非 CLI user 也能用。
6. **Cost tracker**：把 token cost 即時顯示給 user（提升透明度）。
7. **Eval harness**：寫一組 fixed query + ground truth，能跑 `pytest -k eval` 自動算 coverage F1。

---

## Final reflection

這個 iteration log 最深的 lesson：**「AI Harness 設計的難度不在用 LLM，而在『定義 LLM 的邊界』」。**

- 哪些事 LLM 負責？（reasoning, planning, decomposition）
- 哪些事 tool 負責？（事實取得、persistent state）
- 哪些事 system 負責？（schema enforcement, retry, dedup, fallback）

當這三條邊界畫清楚，**LLM 反而變成系統最 commoditized 的部分** — 換 Claude / GPT / Llama 都不影響整體 design。這正是 Anthropic MCP、Claude Code、OpenAI Operator 走的方向，也是這份 AI Harness 想體現的核心 thesis。
