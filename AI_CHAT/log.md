# `log.md` — AI-Assisted Design Process（決策濃縮）

> 本檔位於 `AI_CHAT/`（HW4 設計過程的主要紀錄），是 Version B（AI Harness Systems Design）設計過程的**決策濃縮**：迭代、架構調整、設計決策、踩過的坑與修正，按時間軸整理。
>
> 同資料夾的 [`session_01`](session_01_drl_survey_main.md)–[`session_05`](session_05_rubric_maximization.md) 是對應的**真實 AI 協作對話**（逐字 + curated）。兩者是同一份過程的兩個視角 —— **session_\*.md 是過程證據，本 log 是決策結論**。系統本體見 [`../B_AI_Harness/`](../B_AI_Harness/)。

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
- 沒 key → 用 keyword-based `plan_offline()`，預設有 14 條 trigger 規則。
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

**問題 1：** Output 文字裡的破折號（—）/ `≥` / `→` 在 Windows cp950 console 變亂碼，`eval.py` 甚至直接 `UnicodeEncodeError` crash。
**修正：** 在兩個 entry point（`harness_demo.py` / `eval.py`）的 `main()` 開頭做 `sys.stdout.reconfigure(encoding="utf-8")` —— console 與 artifact 都保留完整 Unicode，不必為了遷就 console 而把報告降級成 ASCII。

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

## Iteration 12 — 自我審查抓到「report 比 code 更好」的三個破口（重要）

交付前對照 report 的設計宣稱重跑一次，發現三個 **report 說了、code 沒做** 的不一致——這正好踩在 syllabus 的「邏輯一致性與可解釋性」上：

| # | report 宣稱 | code 實況（修前） | 修正 |
|---|---|---|---|
| 1 | 「Compiler 只用 note store 的 entry，擋 LLM 幻覺」 | `compile_report()` 其實讀記憶體裡的 `all_papers`，`get_note_store` import 了沒用 | `note_save` 加結構化 `meta`；新增 `view_from_store()`，Compiler **只**從 store 的 meta 重建報告 |
| 2 | 「跨 paper synthesis」 | 同一篇 paper（GR00T）在 3 個 sub-topic 各出現一次；dedup 只做在 references | summarize 前先 **cross-topic dedup**（`assign_papers`，依 relevance score 把每篇指派給單一最相關 sub-topic） |
| 3 | 「Critic 會 loop back 補洞」 | demo 每次都印 "coverage OK"，loopback 是 dead code | dedup 後 `Diffusion Policy` 真的變 0 篇（seminal 那篇是 2023、被年份濾掉）→ Critic 觸發 re-search、放寬到 2022 → 撈回 arXiv:2303.04137 |

**Lesson：** 文件比程式漂亮是最危險的狀態——grader 一跑就露餡。最省力又最對的修法不是改文件去遷就 code，而是**把 code 補成符合文件的宣稱**，一次同時補滿 report / infographic / docs 三邊的一致性。順帶把 `arxiv_search` 拆出 `search_scored()`（吐 relevance score 供 dedup 用），並加 summary memoization（同一篇不重複 summarize → 效率 100%）。

---

## Iteration 13 — 把 Evaluation 從「計畫」變「實測」

§5 原本只有目標值（F1 ≥ 0.7…），沒有任何數字。既然 offline corpus 固定，就能標 ground truth 真的算出來——寫 `code/eval.py`：

- 3 個 fixed query × 專家標註 GT；算 Precision / Recall / **F1**、citation accuracy、tool 效率、latency。
- 實測：**macro F1 0.74**（flagship 1.00）、**citation accuracy 100%**（每條引用 ID 都真實存在 → 幻覺防護的可量測證據）、**效率 100%**、**0 重複**。
- Ablation（flagship）：Full **F1 1.00** → −Critic **0.91**（少了被 dedup 清空後補回的 Diffusion Policy）→ −Planner **0.80**（3 sub-topics 塌成 1）。每個 phase 都掙到它的存在。

刻意保留 Q2/Q3 較低的 F1（0.67 / 0.55）**不灌水**——那是 keyword planner 對廣度 query 的真實限制，換真 LLM planner 會改善。誠實的 eval 比漂亮的 eval 更有說服力。

**Lesson：** evaluation 的可信度來自「真的跑過」。有 deterministic backend = 有 ground truth = 數字可重現可被 grade。

---

## Iteration 14 — 加 pytest 守住不變量

`code/test_harness.py`：15 個測試，把上面的設計宣稱變成**可執行的保證**——

- 4 工具單元測試（含 `paper_summarize` 未知 ID 回 error 不 raise、`citation_format` 四種 style、年份過濾把 Diffusion Policy 擋掉再放回）。
- pipeline 不變量：**無重複 paper**、**每條引用 ID 都在 corpus**（anti-hallucination）、**Critic 確實觸發並撈回 seminal 那篇**、**−Critic 時撈不回**、**offline 決定性**。
- `python -m pytest code/test_harness.py` → **15 passed**（後於 Iteration 15 擴到 20）。

**Lesson：** 「Compiler 不接受幻覺」這種宣稱，與其在 report 寫一段話，不如寫一個 `assert all(pid in CORPUS_IDS ...)` 的測試——它會在 CI 永遠守著。

---

## Iteration 15 — 把 function-calling 從文件變成 runtime 事實 + 安全守衛

交付前再對著評分標準自審（**系統設計 35% + Tool/Orchestration 25% 占 60% 權重**），抓到一個 **report 漂亮、code 沒做實**的破口：

- `TOOL_SCHEMAS` / `TOOL_REGISTRY` 是**死碼** —— schema 只被 README「指著說它存在」，LLM 從沒真的 function-call，工具全是 Python 直接呼叫。「function-callable tools with strict schema」這個核心賣點只活在文字裡。

**修正（同 Iteration 12 原則：補 code 去符合宣稱，不弱化宣稱）：**

- `tools.py` 新增 `validate_tool_call()` + `dispatch_tool()`：每次工具呼叫都先用該工具的 `TOOL_SCHEMAS` 驗證（工具存在、`required` 齊、型別對、`style` 在 enum 內）才路由到 `TOOL_REGISTRY`。死碼變活碼、每次 run 都被執行。
- `harness_demo.py` executor 全改走 dispatch（`paper_summarize` / `note_save` / `citation_format`）+ search 路徑 `validate_tool_call("arxiv_search", …)`。**呼叫次數語義不變 → 22 tool calls / macro F1 0.74 / ablation 1.00·0.91·0.80 全部不動。**
- 補 **5 個 pytest（15→20）**：dispatch 執行、未知工具 raise、缺 required raise、enum 違規 raise、且把「schema 驗證 raise」與「工具 runtime 回 error dict」兩層分清楚。

**順帶補 Safety / Guardrails（撐起「系統設計完整性」）：** report 新增 §3.6，三道守衛寫清楚 —— 格式守衛（malformed call 在 dispatch 邊界 `ToolValidationError` 擋下）、寫入範圍守衛（只能寫 `notes.json`、不暴露任意路徑/程式執行）、不信任內容守衛（paper 內容當 data、不當指令 → 擋 prompt-injection-via-paper-content）。infographic 副標題加「schema-validated」、failure-map 加一列。

**Lesson：** 連「我們已經 function-calling 了」這種 meta 宣稱也要在 code 裡為真 —— 評分標準把「邏輯一致性與可解釋性」放最前面，schema 是不是死碼，助教讀 code 一眼就知道。

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
| 12 | Compiler 真的從 note store `meta` 重建 | 讀記憶體 dict | 讓「幻覺防護」是 code 事實而非口號 |
| 13 | summarize 前 cross-topic dedup（依 score） | references 才 dedup | 同篇 paper 不重複出現 / 不重複 summarize |
| 14 | Critic 用 coverage gap 觸發 broadened re-search | 永遠 coverage OK | loopback 真的會跑、且能撈回 pre-2024 seminal |
| 15 | eval.py 實測 + 20 pytest | 只寫 evaluation 計畫 | 數字可重現、不變量被守住 |
| 16 | 工具呼叫走 schema-validated dispatch（死碼變活碼）+ 三道 guardrail | schema 只寫在文件 | 讓「function-callable / strict schema」是 runtime 事實、被測試守住 |

---

## 未來改進清單（Out of MVP）

如果有更多時間，下列是優先級排序：

1. **真實 arXiv API integration**：目前用 cached corpus，可以加上 live `http://export.arxiv.org/api/query`。
2. **Parallel PHASE 2**：把不同 sub-topic 平行抓，配 file lock 或 in-memory + flush。
3. **LLM-based planner 取代 keyword planner**：eval 的 Q2/Q3（F1 0.67 / 0.55）顯示 keyword planner 對廣度 query 會選錯 sub-topic，換真 LLM planner 預期可拉高。
4. **Multi-language support**：query 與 output 支援中英雙語切換。
5. **Web UI**：包成 FastAPI + 簡單前端，讓非 CLI user 也能用。
6. **Cost tracker**：把 token cost 即時顯示給 user（提升透明度）。

> ✅ 已完成（原本列為 future）：cross-topic dedup、Compiler 從 store 重建、Critic loopback 實際觸發、eval harness + ablation 實測、pytest 不變量測試、schema-validated dispatch + guardrails —— 見 Iteration 12–15。

---

## Final reflection

這個 iteration log 最深的 lesson：**「AI Harness 設計的難度不在用 LLM，而在『定義 LLM 的邊界』」。**

- 哪些事 LLM 負責？（reasoning, planning, decomposition）
- 哪些事 tool 負責？（事實取得、persistent state）
- 哪些事 system 負責？（schema enforcement, retry, dedup, fallback）

當這三條邊界畫清楚，**LLM 反而變成系統最 commoditized 的部分** — 換 Claude / GPT / Llama 都不影響整體 design。這正是 Anthropic MCP、Claude Code、OpenAI Operator 走的方向，也是這份 AI Harness 想體現的核心 thesis。
