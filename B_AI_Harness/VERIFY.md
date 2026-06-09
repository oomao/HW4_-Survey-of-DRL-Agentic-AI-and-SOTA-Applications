# VERIFY — 快速驗證說明書（B AI Harness）

> 目的：讓你（或助教）**3 條指令**就能確認「report / infographic / slides 宣稱的數字 = 程式實跑結果」。
> 全程 **offline、無需 API key**，繁體中文 Windows（cp950 主控台）也不會 crash。
> 環境：Python 3.11+。先切到本資料夾：

```powershell
cd C:\Users\Mao\Desktop\DRL\HW4\B_AI_Harness
```

---

## ① 測試：pipeline 不變量 + schema 守衛

```powershell
python -m pytest code/test_harness.py -v
```

**你應該看到：** `20 passed`。其中這 5 條證明「工具是真的 schema 驗證、不是死碼」：

- `test_dispatch_tool_executes_valid_call`
- `test_validate_rejects_unknown_tool`
- `test_validate_rejects_missing_required_field`
- `test_validate_rejects_out_of_enum_style`
- `test_dispatch_preserves_tool_failsafe`

→ 對應評分維度 **Tool / Orchestration (25%)** + **系統設計完整性 (35%, guardrails)**

---

## ② Demo：一個 query 端到端跑完

```powershell
python code/harness_demo.py
```

**你應該看到（關鍵 4 行，數字必須完全一致）：**

```
[harness] tool calls         : 22
[harness] tool efficiency    : 22/22
[harness] critic rounds      : 1
[harness] wallclock          : 0.0Xs
```

底下會印出 6 篇、無重複、含 IEEE 引用的 mini-survey（3 個 sub-topic）。
→ 對應 **Workflow 與邏輯清晰度 (20%)** + working MVP（bonus）

---

## ③ Evaluation + Ablation：把「計畫」變「實測」

```powershell
python code/eval.py
```

**你應該看到（不會再 crash；數字必須一致）：**

| 項目 | 預期值 |
|---|---|
| Macro-average Coverage F1 | **0.74**（過 0.70 門檻） |
| Citation accuracy | **100%** |
| Tool-call efficiency | **100%** |
| Duplicate papers | **0** |
| Ablation：Full / −Critic / −Planner | **1.00 / 0.91 / 0.80** |

→ 對應 **系統設計完整性 (35%, evaluation)** + **Tool / Orchestration (25%)**

> 三條指令也會把實測結果寫進 `artifacts/`（`demo_run.md` / `compiled_report.md` / `eval_results.md` / `notes.json`），可直接開來對。

---

## ④ 視覺交付物（用瀏覽器 / 看圖開）

| 檔案 | 該看到 | 維度 |
|---|---|---|
| `infographic/architecture.html`（或 `.pdf`） | **6 panel**；header 顯示 `20/20 tests pass`、`schema-validated` | **Infographic (10%)** |
| `report/report.pdf` | **5 頁**，含 §3.6 安全守衛 | 系統設計 (35%) |
| `slides/slides.md` | 14 張簡報 | bonus |
| [`../AI_CHAT/log.md`](../AI_CHAT/log.md)（在 AI_CHAT/） | **15 次 iteration + 16 條決策表** | **log.md (10%)** |

---

## ✅ 全綠判準（一眼確認）

1. `pytest` → **20 passed**
2. `harness_demo.py` → **22 tool calls / 22/22 / critic 1**
3. `eval.py` → **macro F1 0.74 / citation 100% / ablation 1.00·0.91·0.80**，且**沒有 traceback**
4. infographic 6 panel、report 5 頁

四項都符合 = 文件宣稱與程式事實一致。
