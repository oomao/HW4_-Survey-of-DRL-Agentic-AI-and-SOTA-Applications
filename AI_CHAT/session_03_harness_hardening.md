# Session 03 — AI Harness hardening, A-version audit, PDFs & slides

> 第三場 session（2026-05-30）：把 **Version B（AI Harness）做到「report 宣稱 = 程式事實」**，補上實測 evaluation 與測試，稽核 Version A 的一致性，產出交付 PDF，並補做 B 版簡報。
>
> *本場 session 的原始 jsonl 約 57 MB（遠大於 session 01/02 的 ~0.2–0.5 MB），不適合隨 repo 封存，故此檔為 **curated 摘要**（保留關鍵 user 指令、設計決策與 before→after），而非 `convert.py` 的逐字轉檔。*

---

## 🧑 User — 起手

> 感覺還是做得沒有很完美 你怎麼看 我們這次重點做 AI harness 把它做完美 拿到高分 好嗎

接著提供了完整 syllabus，並特別強調：**「資訊圖表（infographic）非常重要」**。

評分比例（與 README §8 一致）：AI 系統設計完整性 35% / Tool·Orchestration 25% / Workflow 與邏輯清晰度 20% / Infographic 10% / log.md 10%；注意事項明寫「**所有設計需具備邏輯一致性與可解釋性**」。

---

## 🤖 Assistant — 稽核：找到三個「report 比 code 漂亮」的破口

實跑 `harness_demo.py` 對照 report 宣稱，發現三個 bug 級不一致（剛好打在「邏輯一致性 20%」「orchestration 25%」）：

1. **Compiler 沒有從 note store 讀** — report/infographic 的核心賣點是「Compiler 只用 note store、擋幻覺」，但 `compile_report()` 其實讀記憶體 `all_papers`，`get_note_store` import 了沒用。**反幻覺防線只存在於文字裡。**
2. **同一篇 paper 重複三次** — dedup 只做在 references，正文/比較表沒有；且「Diffusion Policy」那節一篇 diffusion policy paper 都沒有（真正那篇是 2023、被 `year_min=2024` 濾掉）。
3. **Critic 從不啟動** — demo 每次印 "coverage OK"，loopback 是 dead code。

> 核心判斷：**最省力又最對的修法不是改文件遷就 code，而是把 code 補成符合文件的宣稱** —— 一改，report / infographic / docs 三邊同時變「真」。

---

## 🤖 Assistant — 修復（tools.py + harness_demo.py）

- `note_save` 增加結構化 `meta`；新增 `search_scored()` 吐 relevance score。
- 重寫 PHASE 2：**search 每個 sub-topic → 依 score 跨 topic 去重指派（`assign_papers`）→ 只對指派到的 paper summarize（memoized）+ note_save(meta)**。
- 新增 `view_from_store()`：Compiler **只**從 note store 的 `meta` 重建報告。
- Critic 改 binary coverage check：dedup 後「Diffusion Policy=0」→ 觸發 re-search、放寬年份到 2022 → **撈回 seminal Diffusion Policy（arXiv:2303.04137）**。

**Before → After（flagship demo）：**

| | 修前 | 修後 |
|---|---|---|
| papers | 9（含重複） | **6（0 重複）** |
| 重複 paper | GR00T ×3… | **0** |
| OpenVLA（2024 關鍵開源 VLA） | 被擠掉 | **有** |
| Diffusion Policy 段落 | 無本尊 | **有（critic 撈回）** |
| Critic | 從不啟動 | **觸發 1 輪** |
| Compiler 來源 | 記憶體 dict | **note store meta** |
| tool 效率 | — | **22/22 = 100%** |

---

## 🤖 Assistant — Evaluation 從「計畫」變「實測」+ 測試

- 新增 `code/eval.py`：3 個 fixed query × 專家 ground truth，算 P/R/F1、citation accuracy、效率、latency，並跑 full / −critic / −planner ablation，輸出 `artifacts/eval_results.md`。
  - **macro F1 0.74**（flagship 1.00）、**citation accuracy 100%**（可量測的反幻覺）、**效率 100%**、**0 重複**。
  - Ablation：Full **1.00** → −Critic **0.91**（補不回 Diffusion Policy）→ −Planner **0.80**。
  - Q2/Q3（0.67 / 0.55）刻意不灌水 —— keyword planner 對廣度 query 的真實限制。
- 新增 `code/test_harness.py`：15 個 pytest（工具單元 + pipeline 不變量：無重複、引用都真實、critic 確實觸發、−critic 撈不回、offline 決定性）→ **15 passed**。

---

## 🤖 Assistant — 同步 report / infographic / docs / log

- `report.md` §4/§5/§6 改寫（dedup + compiler-from-store + critic worked example + 實測數字 + ablation）；rebuild `report.html`。
- `infographic/architecture.html`：三處假宣稱（compile from store / critic / dedup）變真；Panel 5 加「實測 + ablation」；Panel 2/3 畫出 dedup 與 critic loopback；header 加 measured badge。（用 preview DOM 驗證 6 panel、sequence 文字無裁切。）
- `docs/index.html`、README、`overview.svg`、`log.md`（新增 Iteration 12–14 + 決策表擴到 15 列）全部對齊。

---

## 🧑 User — 「也可以」（稽核 Version A）

用同樣標準稽核 A 版：

- **PPO**：`ppo_cartpole_log.txt` 實測 500.00±0.00 / 80.99s / 50K / 4 envs，與 README、code 一致 ✓
- **ReAct agent**：offline 實跑、決定性，重現 README trace（2028.0 / DeepSeek-R1 / 2^10−24=1000）✓
- **字數**：`wc -w` = 11,575，與宣稱精確相符 ✓
- **引用**：清單剛好 100 篇 → 把「100+」精確化為「100」（不動 rl-zoo 那種無關的 100+）。

> 結論：**A 版沒有 B 版那種功能性不一致**，只有「100+」一個邊緣精確度問題，已修。

---

## 🧑 User — 「兩者都做」→ PDF + 解 syllabus 合規

用 headless Chrome `--print-to-pdf` 產出三份 PDF。過程中發現 **B 書面報告 render 出 9 頁，超出 syllabus「2–5 頁」**（且 README 自稱 2-5 頁 → 又一個 claim≠reality）。

依「瘦身」做法壓到 **5 頁**（實質全留）：
- §2 大型 ASCII 架構圖、§4.3 ASCII sequence diagram → 改「見 infographic 區塊 1 / 3」（infographic 畫得更好）。
- §3 四個工具 docstring → 收成單行簽章（**附帶修正**：`paper_summarize` 原寫會回 `related_work_anchor`，程式根本沒回 → 改成實際回傳值）。
- 列印專用 CSS 壓密（只影響列印）。

PDF：B report **5 頁** / B infographic 5 頁 / A report 47 頁，均為合法 PDF。

---

## 🧑 User — 「補」（B 版簡報）

新增 `slides/slides.md` —— 14 張 Marp-compatible，與 A 版同風格，內容用已驗證數字（problem → architecture → 4 tools → 4-phase → 三個關鍵設計 → 實測 eval → ablation → failure-mode → demo+tests → conclusion/A↔B 鏡像）。串進 B README、root README、B docs；並把殘留的「11 iteration/decision」修正為 14/15、log.md「11 條 trigger」修正為實際的 14 條。

---

## 設計決策總表（本場）

| # | 決策 | 為何 |
|---|---|---|
| 1 | 修 code 去符合文件宣稱（而非弱化宣稱） | 一次補齊 report/infographic/docs 的一致性 |
| 2 | summarize 前 cross-topic dedup（依 score） | 0 重複；同篇只 summarize 一次 |
| 3 | Compiler 只讀 note store meta | 反幻覺成為 code 事實（citation 100%） |
| 4 | Critic 用 coverage gap 觸發 broadened re-search | loopback 真的會跑、撈回 pre-2024 seminal |
| 5 | eval 實測 + ablation + 15 pytest | 數字可重現、不變量被守住 |
| 6 | Q2/Q3 F1 不灌水 | 誠實 > 漂亮 |
| 7 | report 瘦身到 ≤5 頁（刪與 infographic 重複的圖） | 合規且實質全留 |
| 8 | A 版「100+」→「100」 | 精確；rl-zoo 的 100+ 保留 |

## 成果

- **B 版**：report ↔ code ↔ infographic ↔ docs ↔ slides 全一致；15 tests 綠；macro F1 0.74 / citation 100% / 效率 100% / 0 重複；報告 5 頁合規；三份 PDF 就緒；log.md 14 iterations。
- **A 版**：稽核通過（PPO/agent 實測一致），字數精確、引用數已精確化。

> 最深的 lesson 與 log.md 呼應：**AI Harness 的難度不在用 LLM，而在「定義 LLM 的邊界」並讓每一條設計宣稱都在 code 裡為真。**
