"""下載內政部實價登錄的季資料，只保留臺北市(a)與新北市(f)的不動產買賣檔。

用法:
    python code/download_data.py                  # 預設 112S4 到 115S3,共 12 季
    python code/download_data.py 114S1 114S2      # 只抓指定季別

輸出:專案根目錄的 data/raw/<季別>/{a,f}_lvr_land_a*.csv
已經下載過的季別會跳過；要重抓就先刪掉該季的資料夾。
"""
import io
import sys
import time
import zipfile
from pathlib import Path

import requests

URL = "https://plvr.land.moi.gov.tw/DownloadSeason?season={season}&type=zip&fileName=lvr_landcsv.zip"
CITIES = {"a": "臺北市", "f": "新北市"}
# _a 是不動產買賣主檔,_build 建物、_land 土地、_park 車位明細
SUFFIXES = ["lvr_land_a.csv", "lvr_land_a_build.csv", "lvr_land_a_land.csv", "lvr_land_a_park.csv"]
DEFAULT_SEASONS = ["112S4",
                   "113S1", "113S2", "113S3", "113S4",
                   "114S1", "114S2", "114S3", "114S4",
                   "115S1", "115S2", "115S3"]

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"  # 專案根目錄/data/raw


def download_season(season: str) -> None:
    out = RAW_DIR / season
    if out.exists() and any(out.glob("*.csv")):
        print(f"{season}: 已存在，跳過")
        return

    print(f"{season}: 下載中…", flush=True)
    r = requests.get(URL.format(season=season), timeout=300,
                     headers={"User-Agent": "Mozilla/5.0 (statistics course project)"})
    r.raise_for_status()
    if not r.content.startswith(b"PK"):
        print(f"{season}: 回傳的不是 zip(可能還沒公布)，跳過")
        return

    wanted = {f"{c}_{s}" for c in CITIES for s in SUFFIXES}
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for name in z.namelist():
            base = Path(name).name.lower()
            if base in wanted:
                (out / base).write_bytes(z.read(name))
    got = sorted(p.name for p in out.glob("*.csv"))
    print(f"{season}: 完成，{len(got)} 個檔案")


def main() -> None:
    seasons = sys.argv[1:] or DEFAULT_SEASONS
    for i, s in enumerate(seasons):
        try:
            download_season(s)
        except requests.RequestException as e:
            print(f"{s}: 下載失敗 ({e})")
        if i < len(seasons) - 1:
            time.sleep(3)  # 對政府網站客氣一點


if __name__ == "__main__":
    main()
