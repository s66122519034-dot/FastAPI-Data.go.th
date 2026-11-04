# ข้อ 5 — FastAPI จากชุดข้อมูลภาครัฐ Data.go.th

**ชุดข้อมูล:** ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ ปีงบประมาณ 2569  
**Dataset ID:** `zoo-visitors2569`  
**Resource ID ตามใบงาน:** `0ecc96cf-d914-42a1-b184-dbbd013c3c9c` (เป็นรหัสที่โจทย์อ้างอิง; เว็บอาจมี Resource ID ใหม่เมื่ออัปเดตไฟล์รายเดือน)  
**หน่วยงานต้นทาง:** องค์การสวนสัตว์แห่งประเทศไทย ในพระบรมราชูปถัมภ์  
**แหล่งข้อมูล:** https://data.go.th/dataset/zoo-visitors2569  
**FastAPI Documentation:** https://fastapi.tiangolo.com/tutorial/first-steps/

## 1) เตรียมเครื่อง

ติดตั้ง Python 3.10 ขึ้นไป, Visual Studio Code และ Postman (ถ้าต้องทดสอบแยกจาก Swagger)

แตก ZIP แล้วเปิดโฟลเดอร์ `Zoo_Visitors_FastAPI_2569` ใน VS Code เปิด **Terminal > New Terminal**

บน **Windows PowerShell** รันทีละคำสั่ง:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe download_data.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

**หมายเหตุ:** คำสั่ง `download_data.py` ดาวน์โหลดสำเนา CSV ที่จัดเก็บโดย ThaiGovData (ไฟล์กันยายน 2569) ซึ่งระบุว่าเป็นสำเนาของชุดข้อมูลจาก Data.go.th; ไม่ใช่บริการ API โดยตรงจาก Data.go.th หากดาวน์โหลดไม่ได้ ให้ดูข้อ 2

ถ้า PowerShell ขึ้นว่า `py` ไม่พบ ให้ใช้ `python` แทน `py` สำหรับการสร้าง virtual environment

## 2) ใช้ไฟล์ CSV จาก Data.go.th โดยตรง (วิธีที่แนะนำสำหรับส่งงาน)

1. เข้า https://data.go.th/dataset/zoo-visitors2569
2. เลือกไฟล์ **ข้อมูลรายงานสถิติจำนวนผู้เข้าชมสวนสัตว์ อสส กันยายน 2569** หรือเดือนล่าสุดที่ต้องการ โดยเลือกรูปแบบ **CSV**
3. ดาวน์โหลด CSV จริง แล้วเปิดด้วย VS Code หากไม่ใช่ UTF-8 ให้เลือก **Save with Encoding > UTF-8**
4. ตั้งชื่อ `zoo_visitors_2569.csv` และวางในโฟลเดอร์ `data/`
5. เปิด API ใหม่หรือเรียกอีกครั้ง แล้วเข้า `http://127.0.0.1:8000/api/source` ตรวจสอบ `is_sample: false`

**สำคัญ:** โปรเจกต์มีไฟล์ `data/sample_2569.csv` จำนวน **13 แถวตัวอย่าง** ที่คัดข้อมูลจากหน้าชุดข้อมูลของรัฐ เพื่อให้เปิด API ได้แม้ไม่ต่ออินเทอร์เน็ต **แต่ไม่ใช่ข้อมูลเต็มทั้งปี** หากต้องส่งงานโดยใช้ข้อมูลครบ ให้ทำข้อ 1 (ดาวน์โหลด) หรือข้อ 2 (ไฟล์ต้นทาง) ก่อน และดูว่า `is_sample` เป็น `false`

## 3) เปิดหน้า API และ Swagger

ขณะที่ Terminal แสดงว่า Uvicorn ทำงานอยู่ ให้เปิด:

- API: http://127.0.0.1:8000/
- ข้อมูลทั้งหมด: http://127.0.0.1:8000/api/zoo-visitors
- Swagger UI: http://127.0.0.1:8000/docs
- สถานะและที่มาของข้อมูล: http://127.0.0.1:8000/api/source
- ดูรูปแบบ OpenAPI JSON: http://127.0.0.1:8000/openapi.json

ใน `/docs` ให้กด **GET /api/zoo-visitors → Try it out → Execute** จะเห็น JSON Response กับ HTTP 200

## 4) Endpoint ที่สร้าง

| Method | Endpoint | ความหมาย |
|---|---|---|
| GET | `/` | หน้าแรก |
| GET | `/api/health` | ตรวจสอบว่า API ทำงาน |
| GET | `/api/source` | ตรวจสอบว่าโหลด CSV จริงหรือข้อมูลตัวอย่าง |
| GET | `/api/zoo-visitors` | ข้อมูลสถิติผู้เข้าชมสวนสัตว์ทั้งหมด |
| GET | `/api/zoo-visitors?zoo=เชียงใหม่` | ค้นหาตามชื่อสวนสัตว์ |
| GET | `/api/zoo-visitors?category=เด็ก&limit=5` | ค้นหาประเภทผู้เข้าชม จำกัด 5 รายการ |
| GET | `/api/zoo-visitors/summary` | สรุปยอดรายเดือนจากแถวที่โหลดมา |
| GET | `/api/zoo-visitors/1` | ข้อมูลลำดับที่ 1 |
| GET | `/api/zoo-visitors/999999` | ตัวอย่าง 404 Not Found |

**ข้อมูลแต่ละแถว:** `id`, `zoo`, `category`, `fiscal_year`, `monthly_visitors`  
**ข้อมูลที่เป็น `-`:** ส่งกลับ JSON `null` ไม่เดาเป็นศูนย์  
**หมายเหตุสรุปยอด:** ตัวเลขรวมตามรายการที่ปรากฏในไฟล์ ไม่ได้ยืนยันว่าไฟล์มีการแยกรายการไม่ซ้ำกันทุกกรณี การใช้งานจริงควรตรวจสอบนิยามข้อมูลกับหน่วยงานเจ้าของข้อมูล

## 5) ทดสอบ Postman

1. เปิด Postman แล้วกด **Import**
2. เลือกไฟล์ `Zoo_Visitors_FastAPI.postman_collection.json`
3. กด **GET All Zoo Visitors** (หรือคำขออื่น)
4. กด **Send** ดูสถานะ `200 OK` และ JSON ใน Response
5. ต้องเปิด FastAPI ค้างไว้ระหว่างทดสอบ

ไฟล์ Collection มีตัวแปร `base_url = http://127.0.0.1:8000` อยู่แล้ว

## 6) ทดสอบระบบด้วย Python

เปิด Terminal อีกแท็บในโฟลเดอร์โปรเจกต์:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

ชุดทดสอบตรวจ GET สำเร็จ, กรองข้อมูล, Swagger, สรุป, 404 และ 422

## 7) ภาพหน้าจอที่ควรแคปส่งอาจารย์

1. **VS Code + Terminal:** มีไฟล์ `main.py`, `requirements.txt` และข้อความ Uvicorn ทำงาน (จะเห็น `http://127.0.0.1:8000`)
2. **Swagger UI:** เบราว์เซอร์ที่ `http://127.0.0.1:8000/docs` เห็นชื่อ `Zoo Visitors API - FY 2569` และ GET endpoints
3. **Swagger Response:** เปิด `GET /api/zoo-visitors`, กด Execute เห็น `200` และ JSON Response
4. **Postman:** Method `GET`, URL `http://127.0.0.1:8000/api/zoo-visitors`, Response Status `200 OK`, และข้อมูล JSON
5. **แหล่งข้อมูล:** หน้า Data.go.th ที่แสดงชื่อ dataset / ไฟล์ CSV และหน้า `/api/source` ที่แสดง `is_sample: false`
6. **ทดสอบ Python (เพิ่มเติม):** Terminal ที่แสดง `pytest` ผ่าน

**ข้อควรระวัง:** ขณะส่งควรแคปภาพจากการรันจริง ไม่ใช้ภาพจำลอง หาก `is_sample` ยังเป็น `true` ให้ดาวน์โหลดไฟล์จริงก่อนส่ง

## 8) หมายเหตุการส่งงาน

- URL `localhost` เข้าได้เฉพาะเครื่องตัวเอง: ผู้ตรวจต้องรันโปรเจกต์บนเครื่องหรือดูหลักฐานภาพ/วิดีโอ
- ถ้าอาจารย์ต้องการ URL ที่บุคคลอื่นเข้าได้ ต้องนำขึ้น Hosting และตรวจสอบ URL/Port ที่เปิดใช้งานจริง
- โค้ดนี้ใช้ CSV จริงของชุดข้อมูล ไม่ได้เชื่อม MySQL เพราะโจทย์ให้ MySQL เป็นงานเพิ่มเติม *ถ้ามีสิทธิ์เชื่อมต่อ*
- Data.go.th อาจมี Resource ID เปลี่ยนตามรอบเดือน ให้ใช้ Dataset ID/หน้า dataset เป็นหลักสำหรับเลือก CSV ล่าสุด
