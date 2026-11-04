"""Download a mirrored public CSV from Data.go.th's zoo-visitors2569 dataset.

To use the authoritative Data.go.th file directly, download its latest CSV
manually from https://data.go.th/dataset/zoo-visitors2569 and save it as
'data/zoo_visitors_2569.csv' (UTF-8 encoding).
"""

import csv
import io
from pathlib import Path

import requests

URL = "https://www.thaigovdata.com/dl/2992966"  # Sep 2569 CSV, third-party snapshot
TARGET = Path(__file__).resolve().parent / "data" / "zoo_visitors_2569.csv"
REQUIRED_COLUMNS = {"รายการ", "สวนสัตว์", "ปีงบประมาณ"}


def decode_and_verify(raw: bytes) -> tuple[str, int]:
    for encoding in ("utf-8-sig", "utf-8", "cp874", "tis-620"):
        try:
            text = raw.decode(encoding)
        except UnicodeError:
            continue
        reader = csv.DictReader(io.StringIO(text))
        names = {name.strip() for name in (reader.fieldnames or []) if name}
        if REQUIRED_COLUMNS.issubset(names):
            rows = [row for row in reader if row.get("สวนสัตว์")]
            if len(rows) >= 20:
                return text, len(rows)
    raise ValueError("ไฟล์ดาวน์โหลดไม่ใช่ CSV ชุดข้อมูลสวนสัตว์ปี 2569 ที่อ่านได้")


def main():
    print("Downloading public zoo visitor CSV from the archived mirror...")
    print("Original official dataset: https://data.go.th/dataset/zoo-visitors2569")
    try:
        response = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        decoded, row_count = decode_and_verify(response.content)
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(decoded, encoding="utf-8-sig", newline="")
        print(f"SUCCESS: Saved {row_count} rows to {TARGET}")
        print("Restart FastAPI and check GET /api/source to confirm is_sample=false")
    except (requests.RequestException, ValueError) as exc:
        print(f"FAILED: {exc}")
        print("Please manually download the latest CSV from Data.go.th,")
        print("save it as data/zoo_visitors_2569.csv (UTF-8), then restart the API.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
