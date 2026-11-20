# 資料說明

`data/` 裡的資料**不放 GitHub**(已在 `.gitignore` 排除)，請從雲端下載。

## 怎麼取得資料

1. 從 Google Drive 下載壓縮檔:https://drive.google.com/file/d/1wxe0AJ0WzD7yyA3TIsjO7azjYhr4cfri/view?usp=sharing
2. 解壓縮後放到這個資料夾，確認結構像下面這樣(`data/raw/112S4/…` 等 12 個季別資料夾):

```
data/
├── README.md            本檔(唯一放在 GitHub 上的檔案)
├── raw/<季別>/          原始資料，不要手動修改
│   ├── a_lvr_land_a.csv         臺北市 不動產買賣
│   ├── a_lvr_land_a_build.csv   臺北市 建物明細
│   ├── a_lvr_land_a_land.csv    臺北市 土地明細
│   ├── a_lvr_land_a_park.csv    臺北市 車位明細
│   └── f_...                    新北市，同上
└── processed/           清理後資料，由負責前處理的組員上傳到雲端分享(見下方)
```

## 前處理後的資料：用雲端分享

- 負責前處理(PRE01、PRE02)的組員跑完程式後，把 `data/processed/` 壓縮，**上傳到自己的雲端硬碟，分享連結給大家**。**不要 push 到 GitHub。**
- GitHub 上放的是**程式**(`code/preprocessing/`)和**篩選流程表**(`analysis/preprocessing/`)。
- 把連結填到下表，並寫明是哪一版程式產生的，讓大家確認資料和程式對得上。每次重新產生資料都要新增一列。
- 其他組員下載後解壓縮到 `data/processed/`。想確認資料沒問題，也可以自己執行程式重建，結果必須完全相同。
- `.gitignore` 已排除整個 `data/`。如果原始檔控制頁出現 `data/` 底下的檔案，代表設定被改掉了，不要 commit,先在群組說。

| 日期 | 上傳者(GitHub 帳號) | 對應計畫版本 | 對應 commit | 雲端連結 |
|---|---|---|---|---|
| | | | | |
