"""REST API for the FY 2569 zoo visitor dataset (data.go.th)."""

import csv
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DATA_FULL = BASE_DIR / "data" / "zoo_visitors_2569.csv"
DATA_SAMPLE = BASE_DIR / "data" / "sample_2569.csv"
DATASET_URL = "https://data.go.th/dataset/zoo-visitors2569"

app = FastAPI(
    title="Zoo Visitors API - FY 2569",
    description=(
        "REST API สถิติผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569 "
        "จากชุดข้อมูลขององค์การสวนสัตว์แห่งประเทศไทยบน Data.go.th "
        "หากยังไม่ดาวน์โหลดไฟล์เต็ม API จะใช้ข้อมูลตัวอย่างที่ระบุสถานะไว้อย่างชัดเจน"
    ),
    version="1.0.0",
    contact={"name": "Original data: Data.go.th", "url": DATASET_URL},
)


class VisitorRecord(BaseModel):
    id: int = Field(description="ลำดับแถวในไฟล์ข้อมูล")
    zoo: str = Field(description="ชื่อสวนสัตว์")
    category: str = Field(description="ประเภทผู้เข้าชม เช่น ผู้ใหญ่ หรือ เด็ก")
    fiscal_year: int = Field(description="ปีงบประมาณ พ.ศ.")
    monthly_visitors: dict[str, Optional[int]] = Field(
        description="จำนวนผู้เข้าชมรายเดือน; null หมายถึงไฟล์ต้นฉบับระบุ - หรือไม่รายงาน"
    )


class VisitorsResponse(BaseModel):
    dataset: str
    source: str
    is_sample: bool
    total: int
    offset: int
    limit: int
    records: list[VisitorRecord]


class SummaryResponse(BaseModel):
    dataset: str
    source: str
    is_sample: bool
    matched_records: int
    monthly_totals: dict[str, int]
    grand_total: int
    note: str


def get_data_path() -> tuple[Path, bool]:
    if DATA_FULL.exists():
        return DATA_FULL, False
    return DATA_SAMPLE, True


def parse_count(value: str | None) -> Optional[int]:
    if value is None:
        return None
    cleaned = value.strip().replace(",", "")
    if cleaned in ("", "-", "–", "—"):
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def is_month_column(name: str) -> bool:
    month_names = (
        "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
        "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.",
    )
    return any(month in name for month in month_names)


def read_records() -> tuple[list[VisitorRecord], bool, str]:
    path, is_sample = get_data_path()
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("ไฟล์ CSV ไม่มีหัวตาราง")
        columns = [column.strip() if column else "" for column in reader.fieldnames]
        required = {"รายการ", "สวนสัตว์", "ปีงบประมาณ"}
        if not required.issubset(columns):
            raise ValueError(f"ไฟล์ CSV ต้องมีคอลัมน์ {', '.join(sorted(required))}")
        month_cols = [column for column in columns if is_month_column(column)]
        records = []
        for index, row in enumerate(reader, start=1):
            clean_row = {str(key).strip(): value for key, value in row.items() if key}
            zoo = (clean_row.get("สวนสัตว์") or "").strip()
            category = (clean_row.get("รายการ") or "").strip()
            year_text = (clean_row.get("ปีงบประมาณ") or "").strip()
            if not zoo or not category or not year_text:
                continue
            try:
                fiscal_year = int(year_text)
            except ValueError:
                continue
            records.append(
                VisitorRecord(
                    id=index,
                    zoo=zoo,
                    category=category,
                    fiscal_year=fiscal_year,
                    monthly_visitors={
                        month: parse_count(clean_row.get(month)) for month in month_cols
                    },
                )
            )
    return records, is_sample, path.name


def filter_records(
    records: list[VisitorRecord], zoo: Optional[str], category: Optional[str], fiscal_year: int
) -> list[VisitorRecord]:
    return [
        record for record in records
        if record.fiscal_year == fiscal_year
        and (zoo is None or zoo.casefold() in record.zoo.casefold())
        and (category is None or category.casefold() in record.category.casefold())
    ]


@app.get("/", tags=["System"], summary="หน้าแรก")
def home():
    return {
        "message": "Zoo Visitors API ปีงบประมาณ 2569",
        "docs": "/docs",
        "endpoint": "/api/zoo-visitors",
        "original_dataset": DATASET_URL,
    }


@app.get("/api/health", tags=["System"], summary="ตรวจสอบสถานะ API")
def health():
    records, is_sample, source = read_records()
    return {"status": "ok", "rows": len(records), "is_sample": is_sample, "source": source}


@app.get("/api/source", tags=["System"], summary="ข้อมูลแหล่งที่มา")
def source_info():
    records, is_sample, source = read_records()
    return {
        "dataset": "zoo-visitors2569",
        "fiscal_year": 2569,
        "organization": "องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์",
        "original_url": DATASET_URL,
        "source_file": source,
        "rows": len(records),
        "is_sample": is_sample,
        "message": (
            "กำลังใช้ข้อมูลตัวอย่างบางแถว; รัน python download_data.py หรือวาง CSV ฉบับเต็ม"
            if is_sample else "กำลังใช้ไฟล์ CSV ฉบับเต็มที่ดาวน์โหลดมา"
        ),
    }


@app.get("/api/zoo-visitors", response_model=VisitorsResponse, tags=["Zoo Visitors"], summary="ดูรายการผู้เข้าชม")
def get_visitors(
    zoo: Optional[str] = Query(None, description="ค้นหาชื่อสวนสัตว์ เช่น เชียงใหม่"),
    category: Optional[str] = Query(None, description="ค้นหาประเภท เช่น ผู้ใหญ่"),
    fiscal_year: int = Query(2569, ge=2500, le=3000, description="ปีงบประมาณ พ.ศ."),
    limit: int = Query(100, ge=1, le=500, description="จำนวนรายการต่อหน้า"),
    offset: int = Query(0, ge=0, description="จำนวนรายการที่ข้ามไป"),
):
    records, is_sample, source = read_records()
    filtered = filter_records(records, zoo, category, fiscal_year)
    return VisitorsResponse(
        dataset="zoo-visitors2569", source=source, is_sample=is_sample,
        total=len(filtered), offset=offset, limit=limit,
        records=filtered[offset : offset + limit],
    )


@app.get("/api/zoo-visitors/summary", response_model=SummaryResponse, tags=["Zoo Visitors"], summary="สรุปจำนวนผู้เข้าชมรายเดือน")
def visitor_summary(
    zoo: Optional[str] = Query(None, description="กรองตามสวนสัตว์"),
    category: Optional[str] = Query(None, description="กรองตามประเภทผู้เข้าชม"),
    fiscal_year: int = Query(2569, ge=2500, le=3000),
):
    records, is_sample, source = read_records()
    filtered = filter_records(records, zoo, category, fiscal_year)
    totals: dict[str, int] = {}
    for record in filtered:
        for month, value in record.monthly_visitors.items():
            totals.setdefault(month, 0)
            if value is not None:
                totals[month] += value
    return SummaryResponse(
        dataset="zoo-visitors2569", source=source, is_sample=is_sample,
        matched_records=len(filtered), monthly_totals=totals,
        grand_total=sum(totals.values()),
        note="รวมเฉพาะตัวเลขที่มีในไฟล์ต้นฉบับ; เครื่องหมาย - ไม่ถูกนับเป็น 0 ที่ยืนยันแล้ว",
    )


@app.get("/api/zoo-visitors/{record_id}", response_model=VisitorRecord, tags=["Zoo Visitors"], summary="ดูข้อมูลตามลำดับแถว")
def get_visitor_by_id(record_id: int):
    records, _, _ = read_records()
    for record in records:
        if record.id == record_id:
            return record
    raise HTTPException(status_code=404, detail="ไม่พบรายการที่ต้องการ")
