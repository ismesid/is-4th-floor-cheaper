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
└── processed/           清理後資料，由 code/preprocessing 的程式產生，不用下載
```

## 前處理後的資料不要上傳

- 負責前處理(PRE01、PRE02)的組員跑完程式後，**不要把 `data/processed/` 的資料 push 到 GitHub**,也不用上傳到雲端。
- 上傳的是**程式**(`code/preprocessing/`)和**篩選流程表**(`analysis/preprocessing/`)。其他組員拿到程式後，在自己電腦執行一次，就會產生一模一樣的資料。
- `.gitignore` 已排除整個 `data/`,正常操作不會被加入。如果原始檔控制頁出現 `data/` 底下的檔案，代表設定被改掉了，不要 commit,先在群組說。

雲端失效時，也可以直接從政府網站重新下載：在專案根目錄執行 `python code/download_data.py`(約 1 分鐘)。

## 資料來源

- 內政部不動產交易實價查詢服務網，開放資料「非本期下載」:https://plvr.land.moi.gov.tw/DownloadOpenData
- 範圍:112S4 到 115S3,共 12 季，只保留臺北市(a)和新北市(f)的不動產買賣。
- 下載日期:2026-11-20。

## 資料量(下載時統計)

- 買賣主檔共 237,238 筆，其中建物型態是公寓、華廈、住宅大樓的有 196,951 筆。
- 還沒排除特殊交易，也還沒限制交易日期。

## 讀檔與清理時要注意

1. **第二列是英文欄名**:讀檔用 `pd.read_csv(path, skiprows=[1])`。
2. **季別是「登記」的季別，不是「交易」的季別**:
   - 檔案裡有不少交易日期早於 112 年的資料(108–111 年約 4 萬筆)。推測多半是預售屋交屋後才登記的買賣，成交價反映的是簽約當時的行情。
   - 分析前要依「交易年月日」限制期間。
   - 少數交易日期大於 115 年 9 月，應該是登錄錯誤。
3. **編號有 3 筆重複**:合併各季時用「編號」去重。
4. **交易年月日是民國年**,例如 `1130315` 是 113 年 3 月 15 日。
5. 實際的清理規則以已鎖定的 `plan/preprocessing/PRE01_資料清理與變數定義/` 為準。
