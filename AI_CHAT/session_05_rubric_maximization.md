# Session 05 — Maximizing the 5 grading dimensions (make function-calling real + guardrails)

> 第五場 session（2026-06-08，接續 session_04）：使用者貼出**正式評量標準**(五項加總 100%)，要求把五項都拚到最高。以「最嚴格助教」視角自審後，在占 **60% 權重**的前兩項各補一個破口，並把所有交付物同步——全程保住已驗證數字。
>
> *同 session_03/04，以 **curated 摘要**保留關鍵指令、發現與 before→after，未附 `raw/` jsonl。*

---

## 🧑 User — 起手（貼出評分標準）

> 我們要把這五個部分拚到最高

評量標準（截圖）：

| 評分項目 | 比例 |
|---|---|
| AI 系統設計完整性 | **35%** |
| Tool / Orchestration 設計 | **25%** |
| Workflow 與邏輯清晰度 | 20% |
| Infographic 視覺表達 | 10% |
| log.md 設計過程紀錄 | 10% |

---

## 🤖 Assistant — 嚴格助教自審：兩個破口都落在占 60% 的前兩項

不因為剛驗證過就放水。grep + 讀 code 後抓到：

1. **`TOOL_SCHEMAS` / `TOOL_REGISTRY` 是死碼（D2, 25%）** —— `TOOL_SCHEMAS` 除了被 README「指著說它存在」外，從沒被任何程式用到；`TOOL_REGISTRY` 在 `harness_demo.py` 只被 import、body 從沒呼叫。連 Claude 路徑也只是要一個 JSON 陣列。**「function-callable tools with strict schema」這個核心賣點只活在文字裡。**
2. **報告 0 行談 security / guardrails / injection（D1, 35%）** —— 缺現代 AI 系統設計該有的安全邊界。

> 後三項（workflow 20% / infographic 10% / log 10%）已接近滿，動它們邊際遞減；提升空間集中在前兩項。

**User 選擇：全做（schema 驗證 dispatch + guardrails + 同步，保留所有已驗證數字）。**

---

## 🤖 Assistant — 把 function-calling 從文件變成 runtime 事實（D2）

- `tools.py` 新增 `validate_tool_call()` + `dispatch_tool()`：每次工具呼叫先用該工具的 `TOOL_SCHEMAS` 驗證（工具存在 / `required` 齊 / 型別 / `style` enum）才路由到 `TOOL_REGISTRY`。
- `harness_demo.py` executor 全改走 dispatch（`paper_summarize` / `note_save` / `citation_format`）+ search 路徑 `validate_tool_call("arxiv_search", …)`。
- 關鍵約束：**呼叫次數語義不動** → 死碼變活碼，但 22 tool calls / macro F1 0.74 / ablation 1.00·0.91·0.80 / 6 papers 全部不變。
- 補 **5 個 pytest（15 → 20）**：dispatch 執行、未知工具 raise、缺 required raise、enum 違規 raise、且「schema 驗證 raise」與「工具 runtime 回 error dict」兩層分清楚。

**Before → After：**

| | 修前 | 修後 |
|---|---|---|
| `TOOL_SCHEMAS` / `TOOL_REGISTRY` | 死碼（只被文件引用） | **每次 run 都執行、被 5 個 pytest 守住** |
| LLM 工具呼叫 | Python 直接呼叫 | **schema-validated dispatch** |
| pytest | 15 | **20** |
| 22 calls / F1 0.74 / ablation | — | **完全不變** |

---

## 🤖 Assistant — Safety & Guardrails + memory（D1）

- report 新增 **§3.6**：三道守衛 —— 格式守衛（malformed call 在 dispatch 邊界 `ToolValidationError` 擋下）、寫入範圍守衛（只能寫 `notes.json`、不暴露任意路徑/程式執行）、不信任內容守衛（paper 內容當 data、不當指令 → 擋 prompt-injection-via-paper-content）。
- §2.1 memory 模型講清楚：short-term = context window + within-run summary memoization；long-term = JSON note store（每則附 `meta`、Compiler 唯一 source of truth）。

---

## 🤖 Assistant — 同步所有交付物 + 重生成 PDF

- **infographic**：副標題加「(schema-validated)」、測試 badge 15→20、failure-map 加「Malformed / unknown tool call → dispatch boundary」一列；重生成 `architecture.pdf`（仍 5 頁，視覺驗證 6 panel 完整無破版）。
- **report**：rebuild `report.html` + 重生成 `report.pdf`（**仍 5 頁、合規**）；「~450 行」誠實化為「~560 orchestrator + ~650 tools」。
- **log.md**：新增 **Iteration 15** + 決策表第 **16** 列；iteration 14→15。
- **slides / B README / root README / docs/index.html / overview.svg**：測試 15→20、iteration 14→15、decision 15→16 全部同步；slides + report + infographic 都補了 guardrail。

---

## 設計決策總表（本場）

| # | 決策 | 為何 |
|---|---|---|
| 1 | 補 code 讓 schema/registry 變活碼（而非弱化文件宣稱） | 同 Iteration 12 原則：讓「function-callable」是 runtime 事實 |
| 2 | dispatch 保持呼叫次數語義不變 | 死碼變活碼但 22 calls / F1 0.74 / ablation 一個不動 |
| 3 | schema 驗證 raise vs 工具 runtime 回 error dict 分兩層 | 邊界違約與執行失敗是不同的事，各有測試 |
| 4 | 安全只加在報告 §3.6 + 既有 failure-map（不另開大段） | report 維持 ≤5 頁合規 |
| 5 | 後三項（workflow/infographic/log）不大改 | 已接近滿，邊際遞減 |

## 成果

- **D2（25%）**：`function-callable tools + strict schema` 從文件變 **runtime 事實**，每次 run 執行、20 pytest 守住。
- **D1（35%）**：補齊 Safety & Guardrails（三道守衛）+ 清楚的雙層 memory。
- **D3/D4/D5**：infographic / log / slides / docs 全數同步，數字一致。
- **零回歸**：20 tests green、demo 22 calls、eval macro F1 0.74 / ablation 1.00·0.91·0.80、兩份 PDF 均 5 頁。

> 一以貫之的 thesis：**每一條設計宣稱都要在 code 裡為真** —— 包括「我們已經 function-calling 了」這種 meta 宣稱。評分標準把「邏輯一致性與可解釋性」放最前面，schema 是不是死碼，助教讀 code 一眼就知道。
