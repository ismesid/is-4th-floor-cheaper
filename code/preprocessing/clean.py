# 依據 plan/preprocessing/PRE01_資料清理與變數定義/v2.md(tag: PRE01-v2-locked)
"""PRE01 資料清理與變數定義。

用法(在專案根目錄執行):
    python code/preprocessing/clean.py

輸入:data/raw/<季別>/a_lvr_land_a.csv(臺北市)、f_lvr_land_a.csv(新北市)
輸出:
    data/processed/clean.csv                      清理後資料(不上傳 GitHub)
    analysis/preprocessing/PRE01/篩選流程.csv      每步筆數
    analysis/preprocessing/PRE01/變數檢查.md       缺漏率、範圍、筆數表、x6 界線、SHA-256

本程式不做任何樓層之間的價格比較，只產生資料與筆數。
"""
from __future__ import annotations

import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT_DATA = ROOT / "data" / "processed" / "clean.csv"
OUT_DIR = ROOT / "analysis" / "preprocessing" / "PRE01"
PLAN = "plan/preprocessing/PRE01_資料清理與變數定義/v2.md(tag PRE01-v2-locked)"
SCRIPT = "code/preprocessing/clean.py"

SEASONS = ["112S4", "113S1", "113S2", "113S3", "113S4", "114S1",
           "114S2", "114S3", "114S4", "115S1", "115S2", "115S3"]
CITY_FILES = [("A", "a_lvr_land_a.csv"), ("F", "f_lvr_land_a.csv")]
SQM_PER_PING = 3.30579

# ---------------------------------------------------------------- 第 3 節規則
I5_WHITELIST = {"陽台", "陽臺", "平台", "騎樓", "電梯樓梯間", "走廊", "通道", "門廳", "見其他登記事項"}
X1_KEYWORDS = [
    "親友", "特殊關係", "親屬", "配偶", "二親等",
    "債", "急買急賣", "瑕疵", "凶宅",
    "政府機關", "合建", "權利變換", "都更", "重劃",
    "讓渡", "原價轉讓", "持分",
    "租約", "毛胚",
    "稅費", "仲介費", "地政士", "續建費用", "公共設施保留地",
]
ROOF_EXT = ["頂樓加蓋", "頂樓增建", "屋頂加蓋", "屋頂增建"]
OTHER_EXT = ["增建", "外推", "加蓋", "加窗", "未登記建物"]
FURNISH = ["傢俱", "家具", "裝潢", "家電"]

# ---------------------------------------------------------------- 第 4 節工具函數
_CN = {c: i + 1 for i, c in enumerate("一二三四五六七八九")}


def cn_to_int(s) -> int | None:
    """中文數字(一到九十九)轉整數。規則：一到九;十;十X;X十;X十Y。其他格式回傳 None。"""
    if not isinstance(s, str):
        return None
    s = s.strip().replace("層", "")
    if not s or any(ch not in "一二三四五六七八九十" for ch in s):
        return None
    if s == "十":
        return 10
    if len(s) == 1:
        return _CN[s]
    m = re.fullmatch(r"([一二三四五六七八九]?)十([一二三四五六七八九]?)", s)
    if not m:
        return None
    tens = _CN[m.group(1)] if m.group(1) else 1
    ones = _CN[m.group(2)] if m.group(2) else 0
    return tens * 10 + ones


def roc_to_date(s):
    """民國日期字串轉西元日期。7 位數 YYYMMDD(日 00 設為 1);5 位數 YYYMM(日設 1);其他為缺漏。"""
    if not isinstance(s, str):
        return pd.NaT
    s = s.strip()
    if not s.isdigit():
        return pd.NaT
    if len(s) == 7:
        y, m, d = int(s[:3]), int(s[3:5]), int(s[5:7])
        if d == 0:
            d = 1
    elif len(s) == 5:
        y, m, d = int(s[:3]), int(s[3:5]), 1
    else:
        return pd.NaT
    try:
        return pd.Timestamp(year=y + 1911, month=m, day=d)
    except ValueError:  # 無效日期(含月份 00)
        return pd.NaT


_FW = str.maketrans("０１２３４５６７８９", "0123456789")


def building_id(city: str, addr) -> tuple[str, bool]:
    """第 4 節 building_id 演算法。回傳 (building_id, 是否用到步驟 4 的備案)。"""
    a = addr if isinstance(addr, str) else ""
    a = a.translate(_FW)                                  # 1. 全形數字轉半形
    a = re.sub(r"[ 　]", "", a)                       #    刪除半形與全形空白
    a = re.split(r"[、，,]", a, maxsplit=1)[0]             # 2. 多門牌只取第一個
    m = re.match(r"^(.*?號)", a)                           # 3. 取到第一個「號」
    if m:
        return f"{city}|{m.group(1)}", False
    core = re.sub(r"(地下)?[0-9一二三四五六七八九十]+[樓層].*$", "", a, count=1)  # 4. 備案
    return f"{city}|{core}", True


def _self_test() -> None:
    """計畫第 4 節的 5 個範例 + 中文數字 + 日期。"""
    cases = [
        ("A", "臺北市大安區甲乙路二段１００號五樓之３", "A|臺北市大安區甲乙路二段100號"),
        ("F", "新北市板橋區丙丁路一段１０號之２三樓", "F|新北市板橋區丙丁路一段10號"),
        ("A", "臺北市中山區戊己街５號四樓、５號四樓之１", "A|臺北市中山區戊己街5號"),
        ("A", "臺北市文山區庚辛路３號", "A|臺北市文山區庚辛路3號"),
        ("F", "新北市中和區壬癸路１２號　　", "F|新北市中和區壬癸路12號"),
    ]
    for city, addr, want in cases:
        got, _ = building_id(city, addr)
        assert got == want, (addr, got, want)
    for s, want in [("一", 1), ("十", 10), ("十二", 12), ("二十", 20), ("二十三", 23), ("四層", 4), ("十X", None)]:
        assert cn_to_int(s) == want, (s, cn_to_int(s))
    assert roc_to_date("1130500") == pd.Timestamp(2024, 5, 1)
    assert roc_to_date("08005") == pd.Timestamp(1991, 5, 1)
    assert pd.isna(roc_to_date("1130013")) and pd.isna(roc_to_date("---")) and pd.isna(roc_to_date(""))


def md_table(t: pd.DataFrame, index: bool = True) -> str:
    """把 DataFrame 轉成 Markdown 表格(不依賴 tabulate)。"""
    t = t.reset_index() if index else t
    head = "| " + " | ".join(map(str, t.columns)) + " |"
    sep = "|" + "---|" * len(t.columns)
    rows = ["| " + " | ".join(map(str, r)) + " |" for r in t.itertuples(index=False)]
    return "\n".join([head, sep] + rows)


def contains_any(series: pd.Series, words: list[str]) -> pd.Series:
    return series.str.contains("|".join(map(re.escape, words)), regex=True)


def num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


# ---------------------------------------------------------------- 主流程
def load_raw() -> pd.DataFrame:
    frames = []
    for season in SEASONS:
        for city, fname in CITY_FILES:
            path = RAW / season / fname
            d = pd.read_csv(path, skiprows=[1], dtype=str, encoding="utf-8-sig", keep_default_na=False)
            d["city"] = city
            d["src_season"] = season
            frames.append(d)
    return pd.concat(frames, ignore_index=True)


def i5_floor(s: str):
    """I5:剛好一段樓層、其餘在白名單內 → 回傳樓層字串；否則 None。"""
    if not isinstance(s, str):
        return None
    parts = s.split("，")
    floors = [p for p in parts if re.fullmatch(r"[一二三四五六七八九十]+層", p)]
    if len(floors) != 1:
        return None
    if any(p not in I5_WHITELIST for p in parts if p != floors[0]):
        return None
    return floors[0]


def main() -> None:
    _self_test()
    run_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    raw = load_raw()
    n_raw = len(raw)
    # 去重：依季別由舊到新(同季內臺北市在前)，同一編號保留最後一次出現
    n_dup_ids = raw.loc[raw["編號"].duplicated(), "編號"].nunique()
    df = raw.drop_duplicates("編號", keep="last").copy()

    flow = []  # (步驟, 說明, 臺北市, 新北市, 合計)

    def record(step, desc, d):
        c = d["city"].value_counts()
        flow.append((step, desc, int(c.get("A", 0)), int(c.get("F", 0)), len(d)))

    record("raw", "合併 12 季原始資料(去重前)", raw)
    record("dedup", f"依編號去重(保留最後一次;重複編號 {n_dup_ids} 個)", df)

    df = df[df["交易標的"].str.startswith("房地")]
    record("I1", "交易標的以「房地」開頭", df)
    df = df[df["建物型態"].str.match(r"^(公寓|華廈|住宅大樓)")]
    record("I2", "建物型態為公寓/華廈/住宅大樓", df)
    df = df[df["主要用途"] == "住家用"]
    record("I3", "主要用途 == 住家用", df)
    tdate_int = num(df["交易年月日"])
    df = df[(tdate_int >= 1121001) & (tdate_int <= 1150930)]
    record("I4", "交易年月日介於 1121001–1150930", df)
    df = df.assign(_floor_str=df["移轉層次"].map(i5_floor))
    df = df[df["_floor_str"].notna()]
    record("I5", "只買一層樓，附屬空間在白名單內", df)
    nb = df["交易筆棟數"].str.extract(r"建物(\d+)")[0]
    df = df[nb == "1"]
    record("I6", "交易筆棟數的建物數為 1", df)
    df = df.assign(floor=df["_floor_str"].map(cn_to_int), total_floors=df["總樓層數"].map(cn_to_int))
    df = df[df["floor"].notna() & df["total_floors"].notna()]
    df = df[(df["floor"] >= 1) & (df["floor"] <= df["total_floors"])]
    record("I7", "樓層、總樓層可解析且 1 ≤ 樓層 ≤ 總樓層", df)
    df = df.copy()
    df["floor"] = df["floor"].astype(int)
    df["total_floors"] = df["total_floors"].astype(int)

    # ------------------------------------------------ 變數(第 4 節)
    rem = df["備註"].fillna("")
    target = df["交易標的"]
    total_price = num(df["總價元"])
    park_price = num(df["車位總價元"])
    bldg_area = num(df["建物移轉總面積平方公尺"])
    park_area = num(df["車位移轉總面積平方公尺"])

    df["has_park"] = target.str.contains("車位")
    df["area_ping"] = (bldg_area - park_area.fillna(0)) / SQM_PER_PING
    price = (total_price - park_price.fillna(0)) / 1e4 / df["area_ping"]
    price = price.where(np.isfinite(price) & (price > 0))
    df["price_ping"] = price
    df["log_price"] = np.log(price)
    ptot = total_price / 1e4 / (bldg_area / SQM_PER_PING)
    df["price_ping_total"] = ptot.where(np.isfinite(ptot) & (ptot > 0))
    main_area = num(df["主建物面積"]) + num(df["附屬建物面積"]) + num(df["陽台面積"])
    df["main_area_ping"] = main_area / SQM_PER_PING

    df["f4"] = df["floor"] == 4
    df["f1"] = df["floor"] == 1
    df["f2"] = df["floor"] == 2
    df["top"] = df["floor"] == df["total_floors"]
    df["relpos"] = df["floor"] / df["total_floors"]
    df["relpos_grp"] = np.where(3 * df["floor"] <= df["total_floors"], "低",
                                np.where(3 * df["floor"] <= 2 * df["total_floors"], "中", "高"))
    df["elevator"] = df["電梯"].map({"有": 1, "無": 0}).astype("Int64")
    df["btype"] = df["建物型態"].str.extract(r"^(公寓|華廈|住宅大樓)")[0]
    is_apt = df["btype"] == "公寓"
    bgroup = np.select(
        [is_apt & (df["total_floors"] == 4),
         is_apt & (df["total_floors"] == 5),
         (df["elevator"] == 1).fillna(False) & (df["total_floors"] >= 7)],
        ["W4", "W5", "E7"], default="other")
    df["bgroup"] = bgroup

    tdate = df["交易年月日"].map(roc_to_date)
    bdate = df["建築完成年月"].map(roc_to_date)
    df["trade_date"] = tdate
    df["age"] = (tdate - bdate).dt.days / 365.25
    df["age0"] = df["age"].clip(lower=0)            # age 缺漏時維持缺漏
    df["age_neg"] = (df["age"] < 0).astype("boolean").mask(df["age"].isna())
    df["rooms"] = num(df["建物現況格局-房"]).astype("Int64")
    df["has_mgmt"] = df["有無管理組織"] == "有"
    df["has_roof_ext"] = contains_any(rem, ROOF_EXT)
    df["has_mezz"] = rem.str.contains("夾層")
    rem_no_roof = rem.str.replace("|".join(ROOF_EXT), "", regex=True)
    df["has_other_ext"] = contains_any(rem_no_roof, OTHER_EXT)
    df["has_ext"] = df["has_roof_ext"] | df["has_mezz"] | df["has_other_ext"]
    df["has_furnish"] = contains_any(rem, FURNISH)
    df["district"] = df["city"] + "|" + df["鄉鎮市區"]
    q = (tdate.dt.year - 1911).astype("Int64").astype(str) + "Q" + tdate.dt.quarter.astype("Int64").astype(str)
    df["quarter"] = q.where(tdate.notna())

    bid = [building_id(c, a) for c, a in zip(df["city"], df["土地位置建物門牌"])]
    df["building_id"] = [b for b, _ in bid]
    n_bid_fallback = sum(f for _, f in bid)

    # ------------------------------------------------ 排除旗標(各自獨立)
    df["x1"] = contains_any(rem, X1_KEYWORDS)
    df["x2"] = rem.str.contains("預售屋")
    df["x3"] = ((df["has_park"] & (park_price.isna() | (park_price == 0)))
                | (df["has_park"] & (park_area.isna() | (park_area == 0)))
                | (~df["has_park"] & (park_price > 0))
                | rem.str.contains("車位面積無法概算"))
    df["x4"] = df["age"].isna() | (df["age"] < 0)
    df["x5"] = df["area_ping"].isna() | (df["area_ping"] < 5) | (df["area_ping"] > 200)

    cand = ~(df["x1"] | df["x2"] | df["x3"] | df["x4"] | df["x5"])
    bounds = {}
    df["x6"] = False
    for city in ["A", "F"]:
        v = df.loc[cand & (df["city"] == city), "log_price"].dropna().to_numpy()
        q1, q3 = np.percentile(v, [25, 75])
        iqr = q3 - q1
        lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
        bounds[city] = (q1, q3, lo, hi, len(v))
        m = (df["city"] == city) & df["log_price"].notna()
        df.loc[m, "x6"] = (df.loc[m, "log_price"] < lo) | (df.loc[m, "log_price"] > hi)
    df["x6"] = df["x6"].astype(bool)
    df["main"] = ~(df["x1"] | df["x2"] | df["x3"] | df["x4"] | df["x5"] | df["x6"])

    cov_cols = ["log_price", "floor", "total_floors", "age", "area_ping", "rooms",
                "has_mgmt", "elevator", "btype", "district", "quarter"]
    df["cov_complete"] = df[cov_cols].notna().all(axis=1)

    for k in ["x1", "x2", "x3", "x4", "x5", "x6"]:
        record(k, f"{k} 為 True 的筆數(各旗標獨立計算，非依序)", df[df[k]])
    record("main", "主要分析樣本(x1–x6 皆為 False)", df[df["main"]])

    # ------------------------------------------------ 輸出 clean.csv
    cols = ["編號", "src_season", "city", "district", "quarter", "trade_date", "building_id",
            "btype", "bgroup", "floor", "total_floors", "f1", "f2", "f4", "top", "relpos", "relpos_grp",
            "elevator", "price_ping", "log_price", "price_ping_total", "area_ping", "main_area_ping",
            "age", "age0", "age_neg", "rooms", "has_mgmt", "has_park", "has_roof_ext", "has_mezz",
            "has_other_ext", "has_ext", "has_furnish",
            "x1", "x2", "x3", "x4", "x5", "x6", "main", "cov_complete"]
    out = df[cols].sort_values("編號", kind="mergesort").copy()
    out["trade_date"] = out["trade_date"].dt.strftime("%Y-%m-%d")
    OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_DATA, index=False, encoding="utf-8", lineterminator="\n", float_format="%.10g", na_rep="")
    sha = hashlib.sha256(OUT_DATA.read_bytes()).hexdigest()

    # ------------------------------------------------ 輸出 analysis
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    n_main = int(df["main"].sum())
    header = [
        f"計畫:{PLAN}",
        f"程式:{SCRIPT}",
        f"執行時間:{run_time}",
        f"樣本：全部資料(PRE02 切分前);通過 I1–I7 共 {len(df)} 筆，主要分析樣本 {n_main} 筆",
    ]

    flow_df = pd.DataFrame(flow, columns=["步驟", "說明", "臺北市", "新北市", "合計"])
    with open(OUT_DIR / "篩選流程.csv", "w", encoding="utf-8", newline="\n") as f:
        for h in header:
            f.write(f"# {h}\n")
        flow_df.to_csv(f, index=False, lineterminator="\n")

    md = ["# PRE01 變數檢查", ""] + [f"- {h}" for h in header] + [""]
    md += ["## 篩選流程", "", md_table(flow_df, index=False), ""]
    md += ["## x6 界線(log_price,依縣市)", "",
           "| 縣市 | 計算用筆數 | Q1 | Q3 | 下界 | 上界 |", "|---|---|---|---|---|---|"]
    for c, (q1, q3, lo, hi, n) in bounds.items():
        md.append(f"| {c} | {n} | {q1:.6f} | {q3:.6f} | {lo:.6f} | {hi:.6f} |")
    md.append("")
    fl_all = pd.Series(np.where(df["floor"] >= 6, "6+", df["floor"].astype(str)), index=df.index, name="樓層")
    x6_tab = pd.crosstab(df.loc[df["x6"], "city"], fl_all[df["x6"]])
    md += ["## x6 排除筆數(縣市 × 樓層，只有筆數)", "", md_table(x6_tab), ""]

    md += ["## 變數缺漏率(通過 I1–I7 的全部列)", "", "| 變數 | 缺漏筆數 | 缺漏率 |", "|---|---|---|"]
    for c in ["price_ping", "area_ping", "main_area_ping", "age", "rooms", "elevator", "trade_date"]:
        n_na = int(df[c].isna().sum())
        md.append(f"| {c} | {n_na} | {n_na / len(df):.2%} |")
    md.append("")
    md += ["## 範圍檢查(只報告筆數，不另外排除)", "",
           f"- 屋齡 > 80 年:{int((df['age'] > 80).sum())} 筆",
           f"- 屋齡 < 0:{int((df['age'] < 0).sum())} 筆(由 x4 排除)",
           f"- 坪數 < 5 或 > 200:{int(((df['area_ping'] < 5) | (df['area_ping'] > 200)).sum())} 筆(由 x5 排除)",
           f"- 公寓但總樓層 > 5(歸入 bgroup other):{int((is_apt & (df['total_floors'] > 5)).sum())} 筆",
           f"- building_id 找不到「號」、使用步驟 4 備案:{n_bid_fallback} 筆",
           f"- 建物數(building_id 唯一值，全部列):{df['building_id'].nunique()};主要分析樣本:{df.loc[df['main'], 'building_id'].nunique()}",
           ""]
    m = df[df["main"]]
    fl = np.where(m["floor"] >= 6, "6+", m["floor"].astype(str))
    md += ["## 樓層 × 建物分組筆數(主要分析樣本)", "", md_table(pd.crosstab(pd.Series(fl, name="樓層", index=m.index), m["bgroup"])), ""]
    md += ["## elevator × btype 筆數(通過 I1–I7 的全部列)", "",
           md_table(pd.crosstab(df["btype"], df["elevator"].astype(str))), ""]
    md += ["## 增建與其他旗標筆數(通過 I1–I7 的全部列)", ""]
    for c in ["has_roof_ext", "has_mezz", "has_other_ext", "has_ext", "has_furnish", "has_park", "cov_complete"]:
        md.append(f"- {c}:{int(df[c].sum())}")
    md += ["", "## clean.csv", "",
           f"- 筆數:{len(out)}",
           f"- SHA-256:`{sha}`",
           "- 格式：依編號排序、UTF-8(無 BOM)、換行 `\\n`、浮點數 `%.10g`、缺漏為空字串", ""]
    (OUT_DIR / "變數檢查.md").write_text("\n".join(md), encoding="utf-8", newline="\n")

    print(f"完成：通過 I1–I7 {len(df)} 筆，主要分析樣本 {n_main} 筆")
    print(f"clean.csv SHA-256 {sha}")


if __name__ == "__main__":
    sys.exit(main())
