# 給 GitHub Copilot 的說明

本專案的 AI 規則寫在根目錄的 `AGENTS.md`。開始任何工作前，請完整讀完 `AGENTS.md` 並遵守，特別是:

- 用繁體中文回答。
- **計畫閘門**:任何以價格為對象的計算、資料清理、檢定、模型，都必須先確認對應計畫在 `plan/README.md` 中狀態為「鎖定」,且有 git tag `<編號>-<版本>-locked`。沒有就不要寫程式。
- 不可寫入任何人的真實姓名，組員用 GitHub 帳號稱呼。
- 改 `plan/`、`code/`、`analysis/` 要開分支並走 Pull Request,不可 force push。
