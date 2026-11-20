@AGENTS.md

## Claude Code 專用補充

- 所有規則以上面匯入的 `AGENTS.md` 為準，這裡只補充 Claude Code 的操作方式。
- **獨立審查**:用 Agent 工具開一個**全新的** general-purpose agent(不能用 fork,不能沿用之前的 agent),prompt 為 `plan/_templates/審查指示.md` 的內容，加上要審查的檔案路徑和輸出路徑。第二次審查再開另一個新的 agent。
