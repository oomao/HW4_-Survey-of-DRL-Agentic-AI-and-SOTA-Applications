# Session 06 — Report deepening, design-log consolidation, infographics & git hygiene

> 第六場 session（2026-06-10）：rubric 衝高後的打磨 —— 修報告渲染、把內容從「列決策」加深成「論證決策」、把 `log.md` 併進 `AI_CHAT/`、清掉 commit 的 Claude 署名、為兩個專案各加一張一頁式資訊圖表。
>
> *同 session 03–05，以 curated 摘要保留關鍵指令、發現與 before→after，未附 raw jsonl。*

---

## 🧑 User — 「這次報告做得好爛」

看了一次 B report 覺得很糟。

## 🤖 Assistant — 不防衛，逐頁重看抓到真 bug

不嘴硬說數字都對。逐頁檢視，抓到兩個**真實渲染問題**（不是錯覺）：

- **3 個清單渲染壞掉**：§1.1 痛點 / §2.1 Memory / §6 code 的項目符號因「清單前缺空行」（加上 `sane_lists` 更嚴格）被吸進上一段，變成「- … - … -」擠成一坨。
- **justify 兩端對齊**讓中英混排出現尷尬空隙。

修法：補空行 + `build_html.py` 的 `text-align` justify→靠左。重渲染後乾淨，仍 5 頁。

## 🧑 User — 釐清：真正的問題是「內容太淺」

修完版面後確認——「好爛」主因不是版面，是**內容深度不夠 / 不夠有料**。

## 🤖 Assistant — 把設計推理從 log.md 搬進報告本體

診斷：報告**「列了決策、卻沒論證決策」**，真正的料埋在 log.md。六處加深：

| 節 | 加的料 |
|---|---|
| §2 開頭 | 三條貫穿全系統的設計原則 |
| §2.2 | 單一 controller vs multi-agent 的 trade-off（token ×4 / 可觀測性 / 單線程先例） |
| §3 | 為什麼正好 4 個工具（砍 3 個「假工具」+ 工具數 = eval surface） |
| §4.4 | Critic 踩坑故事（初版 8 輪 perfectionist loop → binary check） |
| §5.3 | ablation 量化綜述（Planner +0.20 / Critic +0.09 F1） |
| §7 | 結論從泛論改成 MCP / ReAct / 單線程 agent loop 各自印證 thesis |

為塞下又不破 5 頁，砍**冗餘**（非料）：§3.5 比較表（與 infographic 區塊 4 重複）、§6 實作（與 §5 重複）壓成 3 行、§4.2 pseudo-code 18→4 行。**仍 5 頁合規。**

## 🧑 User — 「log.md 就是 AI_CHAT」→ 併進去

判斷：兩者都是「AI 協作設計過程」。決定**以 AI_CHAT 為主**，把 `log.md` 實體移進 `AI_CHAT/`（`git mv`，rename 歷史保留）。守住「log.md 設計過程紀錄 10%」的做法：B README §7/§8、root README、slides、docs 全部改指 `../AI_CHAT/log.md`，`AI_CHAT/README` 把 log.md 標為 ⭐ 評分對應 deliverable。

## 🧑 User — 「記得不要帶有 claude」→ 清 commit 署名

- 當前 commit `amend` 拿掉 `Co-Authored-By: Claude` 行。
- 發現更早、**已 push** 的 commit 也帶署名 → `filter-branch` 清掉全歷史的 Claude 署名行 + `--force-with-lease` 重推（經 user 明確授權）。**GitHub 全歷史 0 個 Claude 署名。**
- **保留**：報告 / 程式裡的「Claude Haiku 4.5」是 LLM 後端的設計選型，非署名。
- 記憶：以後 commit 訊息一開始就不寫 Claude（連技術引用也用中性說法），避免回頭 force-push。

## 🧑 User — 兩張資訊圖表放進兩個專案

從 Downloads 用 md5 比對找出兩張不重複的圖、視覺辨識 A/B，複製進 `A_DRL_Survey/infographic/survey_infographic.png`、`B_AI_Harness/infographic/architecture.png`（與既有 html/pdf 並排）；README 嵌入、B §8 評分證據改指新 PNG。核對圖中數字（F1 0.74 / 100% / ablation 1.00·0.91·0.80）與實測一致。

## 設計決策總表（本場）

| # | 決策 | 為何 |
|---|---|---|
| 1 | 報告壞清單先修、再確認真正問題是深度 | 不防衛、先分辨「版面 vs 內容」再對症下藥 |
| 2 | 加深 = 把 log.md 的 trade-off 論證搬進報告，砍冗餘換空間 | 維持 ≤5 頁合規又「有料」 |
| 3 | log.md 併入 AI_CHAT（以 AI_CHAT 為主），但保留實體 `log.md` | 守住「log.md 設計過程 10%」、又消除重複 |
| 4 | commit 全歷史去 Claude 署名（force-push 經授權） | git log 乾淨、無 AI 痕跡；技術引用照留 |
| 5 | 兩張一頁式 infographic 入庫並嵌 README | 視覺 deliverable 升級、GitHub 直接可見 |

## 成果

- **B 報告**從「骨架」變「論證」：6 處加深、3 個壞清單修好、justify 改靠左，仍 5 頁合規。
- **設計過程紀錄整合**：`log.md` 進 `AI_CHAT/`，全 repo 指路標一致。
- **git**：GitHub 全歷史無 Claude 署名；偏好已記入記憶。
- **兩專案各一張精緻一頁式資訊圖表**（數字與實測一致）。

> 一以貫之的 lesson：先確認「**真正的問題是什麼**」再動手（壞清單 ≠ 內容淺），且每個宣稱都對得起 code 與實測。
