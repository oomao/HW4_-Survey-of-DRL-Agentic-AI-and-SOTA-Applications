# AI_CHAT — AI 協作開發對話紀錄

本資料夾保留 HW4 開發過程中與 AI 助手的所有 session 對話紀錄，作為「人機協作開發過程」的可追溯佐證（與 `B_AI_Harness/log.md` 互補）。

## 檔案

| 檔名 | 內容 | 對應日期 |
|---|---|---|
| [`session_01_drl_survey_main.md`](session_01_drl_survey_main.md) | 第一場 session：從零搭建 A/B 兩版作業 — Survey 撰寫、PPO/LLM agent demo、AI Harness 系統設計與 MVP 編寫 | 2026-05-20 |
| [`session_02_delivery_verification.md`](session_02_delivery_verification.md) | 第二場 session：交付前 end-to-end 驗證（跑 demo、檢查 HTML、確認可交付狀態） | 2026-05-26 |
| [`session_03_harness_hardening.md`](session_03_harness_hardening.md) | 第三場 session：Version B 補強（Compiler 讀 store / cross-topic dedup / Critic 觸發）、實測 evaluation + 15 pytest、A 版一致性稽核、交付 PDF、B 版簡報 | 2026-05-30 |
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
- **session_03** 為 curated 摘要：該場 session 的原始 jsonl 約 57 MB（遠大於前兩場的 ~0.2–0.5 MB），不適合隨 repo 封存，故以可讀摘要保留關鍵指令、設計決策與 before→after，未附 `raw/` jsonl
