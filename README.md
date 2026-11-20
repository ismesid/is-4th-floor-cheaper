# 4 樓真的比較便宜嗎?

統計課期末專題。用內政部實價登錄資料(臺北市、新北市，112 年第 4 季到 115 年第 3 季),檢驗 4 樓的每坪單價是否比較低，以及原因是忌諱、電梯(爬樓梯)、屋齡還是地段。

## 第一次來?

**從沒用過 GitHub 或 VS Code 的組員，請先看 [新手教學](docs/新手教學.md)**,裡面有:
- Windows / Mac 安裝 Git、VS Code、Python
- VS Code 介面怎麼操作
- 安裝自己用的 AI 擴充套件(Claude、Copilot、Gemini、ChatGPT)
- 怎麼把專案下載(clone)到自己的電腦
- 每天的工作流程：同步 → 開分支 → 修改 → 上傳 → Pull Request
- 出問題怎麼辦

## 和 AI 一起工作

大家都會用 AI 協作，所以**讓你的 AI 知道規則**最重要。規則寫在 [AGENTS.md](AGENTS.md)。

- **Claude Code**:會自動讀 `CLAUDE.md`(裡面匯入 `AGENTS.md`)。
- **Copilot**:會自動讀 `.github/copilot-instructions.md`(指向 `AGENTS.md`)。
- **Gemini CLI**:會自動讀 `GEMINI.md`(指向 `AGENTS.md`)。
- **Codex**:會自動讀 `AGENTS.md`。
- **ChatGPT、Gemini 等網頁版**:讀不到 repo。每次開新對話，先上傳 `AGENTS.md` 和相關的計畫檔，並貼上這段開場白:

```
請先完整閱讀我上傳的 AGENTS.md,這是我們小組專題的規則，整段對話都要遵守。
我的 GitHub 帳號是 ______。我今天要做的是 ______(例如:IN02 的程式)。
```

**最重要的一條規則**:任何跟價格有關的分析，都要等對應的計畫「鎖定」後才能寫程式。計畫狀態看 [plan/README.md](plan/README.md)。

## 資料夾結構

```
├── README.md              本檔
├── AGENTS.md              給所有 AI 的專案規則
├── CLAUDE.md、GEMINI.md、.github/copilot-instructions.md   各家 AI 的入口，都指向 AGENTS.md
├── docs/新手教學.md        安裝與 Git 操作教學
├── requirements.txt       Python 套件清單
├── plan/                  分析計畫與審查紀錄，總覽與進度見 plan/README.md
├── code/                  程式，依類別分 preprocessing / inclass_analysis / extra_analysis
├── data/                  資料(不在 GitHub 上，從雲端下載，見 data/README.md)
├── analysis/              程式產生的結果(表、圖、模型)，不手動修改
└── report/
    ├── proposal/          題目提案
    ├── mid_report/        期中報告(研究方法、Q&A、簡報)
    └── final_report/      期末報告
```

## 協作規則(摘要)

| 要改的東西 | 做法 |
|---|---|
| `plan/`、`code/`、`analysis/`、規則檔 | 開分支 → Pull Request → 另一位組員 Approve 後合併 |
| `report/` 的 md、`docs/`、錯字 | 可以直接推到 `main` |

- 開工前先同步(Pull),收工前一定要上傳(Push)。
- Commit 訊息用中文，開頭標計畫編號，例如 `IN02:加入交互作用圖`。
- 不要 force push;不要上傳 `data/`、密碼;已鎖定的計畫檔不能改。
- Word、PowerPoint 同一時間只有一個人改，改之前在群組說一聲。
- 這是公開 repo,**不要寫任何人的真實姓名、學號、email**,組員用 GitHub 帳號稱呼。

完整規則見 [AGENTS.md](AGENTS.md) 第四節。

## 目前進度

見 [plan/README.md](plan/README.md)。
