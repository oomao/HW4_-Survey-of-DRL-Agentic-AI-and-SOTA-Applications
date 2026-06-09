# AI_CHAT — AI 協作開發對話紀錄（設計過程主要紀錄）

本資料夾是 HW4「人機協作設計過程」的 **主要、完整紀錄**：所有 session 的真實 AI 對話（session 01/02 為逐字 jsonl 轉檔，03–05 為 curated 摘要）。

> 同資料夾的 [`log.md`](log.md) 是從這些對話**萃取出的設計決策濃縮**（評分表上「log.md 設計過程紀錄」對應的 deliverable）。兩者是同一份過程的兩個視角：**session_\*.md 是過程證據（主），log.md 是決策結論（衍生索引）**。先看 session 看「怎麼走到這」，再看 log.md 看「最後決定了什麼」。

## 檔案

| 檔名 | 內容 | 對應日期 |
|---|---|---|
| [`log.md`](log.md) | ⭐ **設計決策濃縮 — 評分對應的 deliverable**（「log.md 設計過程紀錄」10%）：15 iteration + 16 決策表，從下列對話萃取 | — |
| [`session_01_drl_survey_main.md`](session_01_drl_survey_main.md) | 第一場 session：從零搭建 A/B 兩版作業 — Survey 撰寫、PPO/LLM agent demo、AI Harness 系統設計與 MVP 編寫 | 2026-05-20 |
| [`session_02_delivery_verification.md`](session_02_delivery_verification.md) | 第二場 session：交付前 end-to-end 驗證（跑 demo、檢查 HTML、確認可交付狀態） | 2026-05-26 |
| [`session_03_harness_hardening.md`](session_03_harness_hardening.md) | 第三場 session：Version B 補強（Compiler 讀 store / cross-topic dedup / Critic 觸發）、實測 evaluation + 15 pytest、A 版一致性稽核、交付 PDF、B 版簡報 | 2026-05-30 |
| [`session_04_final_verification.md`](session_04_final_verification.md) | 第四場 session：交付前最終驗證（15 tests / demo / eval 全部實跑核對、infographic 視覺檢查），抓到並修復 `eval.py` 在 cp950 console 的 `UnicodeEncodeError` crash（且與 log.md Iteration 9 宣稱矛盾），console 改 UTF-8 | 2026-06-08 |
| [`session_05_rubric_maximization.md`](session_05_rubric_maximization.md) | 第五場 session：對著正式評量標準衝高五項。在占 60% 權重的前兩項補破口——把死碼 `TOOL_SCHEMAS`/`REGISTRY` 做成 schema-validated dispatch（D2，15→20 tests）、補 Safety & Guardrails（D1）；同步 infographic/log/slides/docs，保留所有已驗證數字 | 2026-06-08 |
| [`session_06_report_depth_and_polish.md`](session_06_report_depth_and_polish.md) | 第六場 session：rubric 後的打磨——修報告 3 個壞清單渲染、把內容從「列決策」加深成「論證決策」（6 處 trade-off 論證、仍 5 頁）、把 `log.md` 併進 `AI_CHAT/`、清掉 commit 全歷史的 Claude 署名、為 A/B 各加一張一頁式資訊圖表 | 2026-06-10 |
| [`raw/`](raw/) | 原始 session jsonl（含 thinking / tool calls / tool results 完整紀錄） | — |
| [`convert.py`](convert.py) | jsonl → markdown 轉換腳本 | — |

## 重新產生 markdown

```bash
cd AI_CHAT
python convert.py
```

腳本會讀取 `raw/*.jsonl` 並重寫對應的 `session_*.md`。

## 註

- `thinking` 區塊與 `tool_result` 區塊以 `<details>` 摺疊，在 GitHub 上預設收合
- 超過 800 字元的 tool 輸出會被截斷以保持可讀性 — 完整內容仍可在 `raw/*.jsonl` 中找到
- **session_03 / 04 / 05 / 06** 為 curated 摘要：session_03 的原始 jsonl 約 57 MB（遠大於前兩場的 ~0.2–0.5 MB），不適合隨 repo 封存；這四場皆以可讀摘要保留關鍵指令、發現、設計決策與 before→after，未附 `raw/` jsonl
