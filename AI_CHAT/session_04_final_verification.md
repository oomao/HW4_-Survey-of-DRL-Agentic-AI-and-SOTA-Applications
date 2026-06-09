# Session 04 — Final pre-delivery verification + cp950 portability fix

> 第四場 session（2026-06-08）：交付前**最終驗證** —— 把 report / README / infographic / slides 宣稱的每個數字用 `pytest` / `harness_demo.py` / `eval.py` 實跑核對，並視覺檢查 infographic。過程中抓到並修復一個會被助教一跑就露餡的 **cp950 console crash**。
>
> *本場 session 同 session_03，以 **curated 摘要**保留關鍵 user 指令、發現與 before→after，未附 `raw/` jsonl。*

---

## 🧑 User — 起手

> 再驗證一次 我想要拿高分 確定該有的東西都有嗎 以及資訊圖表 我們主要做 ai harness 的作業

重點：(1) 再驗證一次拿高分；(2) 確認該有的東西都在；(3) 特別點名**資訊圖表**；(4) 主軸是 Version B（AI Harness）。

---

## 🤖 Assistant — 盤點交付物 + 實跑核對每個數字

把 B 版所有檔案讀過，並**實際執行**而非只看文字：

| 交付物 | 在不在 | 實測 |
|---|---|---|
| 系統設計報告（≤5 頁） | ✅ report.md / html / **pdf 實際 5 頁** | — |
| 資訊圖表（6 panel） | ✅ architecture.html / pdf | 見下一節 |
| 簡報 14 張 | ✅ slides.md | 內容數字與實測一致 |
| log.md 設計過程 | ✅ Iteration 0–14 + 15 列決策總表 | — |
| 4 工具（≥3 ✓） | ✅ tools.py，strict JSON schema | — |
| 4-phase orchestration | ✅ harness_demo.py | demo 跑通 |
| 15 pytest | ✅ | **15 passed** ✓ |
| Demo | ✅ | **22 tool calls / 100% 效率 / critic 1 輪 / 6 papers** ✓ |
| Evaluation + ablation | ✅ | **macro F1 0.74 / citation 100% / 0 重複**；ablation **1.00→0.91→0.80** ✓ |

> 結論：report / README / infographic / slides 寫的每一個數字，都用實跑結果核對過，**完全吻合、沒有灌水**。

---

## 🤖 Assistant — 資訊圖表（user 特別在意）視覺檢查

直接讀渲染後的 `architecture.pdf`，確認 **6 個 panel 都完整**：① 系統架構（色彩編碼 User/Controller/Memory/Tools/External/Output 連線）② 4-phase pipeline ③ sequence diagram（6 條 actor lane）④ 工具規格表 ⑤ evaluation dashboard ⑥ failure-mode map。

關鍵：**dashboard 裡的數字（F1 0.74、citation 100%、效率 100%、15/15 tests、ablation 1.00/0.91/0.80）和實測 eval 完全一致** —— 圖表是有憑據的，不是裝飾。

---

## 🤖 Assistant — 抓到 cp950 crash（本場最有價值的發現）

`python code/eval.py` 在**繁體中文 Windows（cp950 主控台）會直接 crash**：

```
UnicodeEncodeError: 'cp950' codec can't encode character '≥' (≥) ...
```

兩個原因讓它特別致命：

1. **README 第 95 行明明叫助教「實測數字由 `python code/eval.py` 產生」** —— 助教一跑就看到 traceback。
2. **`log.md` Iteration 9 還寫著「Windows console 破折號亂碼問題已修正」** —— 但 code 根本沒修好，連 `eval.py` 都還在崩潰。**文件說修好了、程式沒修好**，正好踩在 syllabus 的「邏輯一致性」上。

`harness_demo.py` 印 compiled report 時的 em-dash 也是 mojibake（`—` → `�X`），只是沒 crash。

---

## 🤖 Assistant — 修復（3 檔，最小改動）+ 重跑

- **eval.py / harness_demo.py**：`main()` 開頭 `sys.stdout.reconfigure(encoding="utf-8")` —— console 與 artifact 都保留完整 Unicode，不必為了遷就 console 把報告降級成 ASCII（比 Iteration 9 原本設想的 ASCII 化更好）。
- **log.md Iteration 9**：改成如實描述 UTF-8 reconfigure 修法，讓 log ↔ code 一致。
- 順手修正 eval.py 一個 stale 註解（「16-paper corpus」→ 實際 **15** 篇）。

**Before → After：**

| | 修前 | 修後 |
|---|---|---|
| `python code/eval.py`（cp950） | **UnicodeEncodeError crash** | **exit 0**，`≥ → —` 正常顯示 |
| `harness_demo.py` console 破折號 | mojibake `�X` | 乾淨的 `—` |
| log.md Iteration 9 宣稱 | 說已修、實際沒修 | 與 code 一致 |
| eval.py 註解 | 「16-paper」 | 「15-paper」 |
| pytest | 15 passed | **仍 15 passed** |

重跑後 artifact 內容不變（只有 latency 時間戳漂移），故還原以保持 diff 聚焦。

---

## 設計決策總表（本場）

| # | 決策 | 為何 |
|---|---|---|
| 1 | 驗證以「實跑」為準，不信文字 | report 的每個數字都要能被重現才算數 |
| 2 | cp950 crash 用 `stdout.reconfigure(utf-8)` 修，而非把報告 ASCII 化 | console 與 artifact 同時保留完整 Unicode |
| 3 | 同步修 log.md Iteration 9 的宣稱 | 「文件說修好、程式沒修好」本身就是要消滅的不一致 |
| 4 | artifact 還原（只有時間戳變動） | 讓 commit 聚焦在 3 個有意義的原始碼改動 |

## 成果

- **驗證通過**：B 版 report / README / infographic / slides / log.md 的所有宣稱數字，皆由 `pytest`（15 green）/ `harness_demo.py`（22 calls·100%·critic 1·6 papers）/ `eval.py`（macro F1 0.74·citation 100%·效率 100%·0 重複·ablation 1.00→0.91→0.80）實跑核對一致。
- **修掉 1 個可移植性 bug**：`eval.py` 在 cp950 console 的 crash；連帶讓 log.md Iteration 9 的宣稱在 code 裡為真。
- 改動範圍：`code/eval.py`、`code/harness_demo.py`、`log.md` 三檔。

> 與前三場一脈相承的 lesson：**每一條設計宣稱都要在 code 裡為真，連「我們已經修好 X」這種 meta 宣稱也要 —— 助教（或 cp950 的主控台）一跑就知道。**
