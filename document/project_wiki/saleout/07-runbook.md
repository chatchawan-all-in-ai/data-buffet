# 07 · Runbook — เจออาการนี้ ทำอะไร

> **LLM context**: ขั้นตอนรับมือเหตุการณ์ของสาย Sales Out MDT แบบ "อาการ → ตรวจ → แก้"
> · ยึดโค้ดบน dev ของ Dataform (บท 05) · query อ้างบท 06 · ข้อมูล Airflow/raw อ้างบท 02
> · เขียน 2026-10-06 · ❓ = ยังไม่ได้ยืนยัน

## 0. กฎเหล็ก (อ่านก่อนกดอะไร)

| ห้าม | เพราะ |
|---|---|
| รัน tag `initial` | ไฟล์ drop ของ validated saleout ใช้ tag นี้ด้วย → validated หายทั้ง 10 ตาราง (บท 02) |
| ติ๊ก **Include dependencies** ตอนรัน validated/curated ของ saleout | ลากไฟล์ drop มาด้วย |
| ติ๊ก **Run with full refresh** กับ `curated_saleout_mdt` โดยไม่จำเป็น | rebuild ทั้งก้อน ถ้า validated ขาดช่วงไหน ยอดช่วงนั้นหายจาก curated ด้วย |
| แก้ mapping สาขา/สินค้าใน SQL | แก้ที่ mds (บท 04) |
| mv / rm / restart บน VM `airflow-prd` โดยไม่ถาม | เป็น prod |
| deploy view จากรีโปโดยไม่เทียบกับ BigQuery ก่อน | view บน BQ อาจมีคอลัมน์ที่รีโปไม่มี (บท 05 ข้อ 12) |

## 1. รอบการรันปกติ

| เวลา (Asia/Bangkok) | อะไร |
|---|---|
| 05:45 | Dataform compile (release config) |
| 06:00 | Dataform workflow `daily_process` รันทุก tag |
| 08:00 | Airflow `pipline_saleout_mdt` วางไฟล์ HP/MH/BT/TW/GB ลง GCS |
| 08:30 | Airflow `pipline_saleout_dohome` ดึงไฟล์ DH จาก SharePoint |

❓ Dataform รัน 06:00 แต่ไฟล์ลง 08:00 → ไฟล์วันนี้เข้า curated **รอบเช้าพรุ่งนี้** (ช้า 1 วันโดยโครงสร้าง)
ยืนยันกับเวลา schedule จริงของ nonprd/prd ก่อนบอก BI ว่ารายงานพร้อมกี่โมง
· วัด 2026-10-06 ตอนค่ำ: curated มี `asatdate = 2026-10-06` แล้ว → nonprd อาจมีรอบหลัง 08:00 (บท 08 E-1)

**ทุกเช้าดู:** บท 06 Q1 (ความสด) — ใช้เวลา 1 นาที

## 2. ฟีดของห้างไม่มา / ยอดวันล่าสุดหาย

**อาการ:** Q1 `days_behind` ของห้างหนึ่งโตขึ้น หรือ Q2 มีวันหาย

1. **GCS มีโฟลเดอร์วันนั้นไหม**
   ```bash
   gsutil ls gs://file-raw-data/saleout_mdt/<ห้าง>/ | tail -5
   ```
2. **ไม่มีใน GCS** → ดูที่ VM ว่าไฟล์ค้างหรือไม่เคยมา (อ่านอย่างเดียว)
   ```bash
   gcloud compute ssh airflow-prd --zone=asia-southeast1-a --project=databuffet-prd --quiet --command='sudo ls -lt /opt/airflow/dags/SaleOut_MDT/<ห้าง>/ | head' -- -o BatchMode=yes
   ```
   - ไฟล์ค้างในโฟลเดอร์ห้าง (ไม่ได้ย้ายเข้า `archive/`) → DAG พัง ดูข้อ 3
   - ไม่มีไฟล์เลย → **ห้างไม่ส่ง** แจ้งคนที่ประสานกับห้าง ❓ ใครเป็นคนรับไฟล์จากห้าง
   - Airflow **ไม่ alert** ตอนไฟล์ไม่มา (task สำเร็จเงียบ ๆ) จึงต้องดูเอง
3. **มีใน GCS แต่ไม่มีใน curated** → Dataform ยังไม่รันรอบถัดไป (ข้อ 1) หรือ run ล้ม ดู execution log
   - ถ้า ASATDATE เก่ากว่า `BACKFILL_DAYS` (1 วัน) incremental จะไม่หยิบ → ข้อ 5

**GB:** เคยค้าง 6 ก.ค. – ก.ย. กลับมาแล้ว (2026-10-06) · ถ้าค้างอีก ดูไฟล์ซ้ำ `Sale_Date` เดิม (backlog 8)
**DH:** มาเดือนละครั้ง ช้าเป็นเรื่องปกติ

## 3. DAG Airflow พัง

| สาเหตุที่เคยเกิด | ดูยังไง | แก้ |
|---|---|---|
| ห้างเพิ่ม/ย้ายคอลัมน์ → ไม่ตรง `SCHEMA_MAP` ในไฟล์ DAG (2026-09-21) | log ของ task `process_all_folders` | แก้ `SCHEMA_MAP` ใน DAG + แก้ external table ใน `create_all_table_raw_saleout_mdt` ให้ตรง |
| HP ย้ายเครื่องหมาย `="..."` ไปคอลัมน์อื่น | ไม่พัง แต่ยอดหายเงียบ (บท 02) | validated แกะทุกคอลัมน์อยู่แล้ว ตรวจ Q2 |
| ไฟล์เปล่า (มีแต่ header) | ถูกข้ามเงียบ ๆ | ขอไฟล์ใหม่จากห้าง |

แก้ DAG = งานบน prod → **ถามก่อนทุกครั้ง** · โค้ดสำเนาอยู่ `~/Downloads/airflow` (ไม่ใช่ git)

## 4. DoHome อัปไฟล์ใหม่ / อัปทับ

- validated `saleout_dh` เป็น **full load** ทุกคืน → เดือนใหม่เข้าเองรอบถัดไป ไม่ต้องทำอะไร
- อัปทับเดือนเดิม → เก็บไฟล์ล่าสุดต่อ (`SOURCE_FOLDER`, เดือน) ด้วย `FILE_MODIFIED` อัตโนมัติ
- ตรวจหลังเข้า: Q7 (fact = curated) และยอดเดือนนั้นของ DH ไม่ควรเป็น 2 เท่า
- DAG DH ใช้ Microsoft Graph — ถ้า 403 ดูเรื่องสิทธิ์ `Sites.Selected` (ต้องผ่าน admin)

## 5. ต้องเติมข้อมูลย้อนหลัง (backfill)

**เมื่อไหร่:** ไฟล์ของห้างมาช้ากว่า 1 วัน หรือ run ล้มหลายวัน

1. แก้ `workflow_settings.yaml` → `BACKFILL_DAYS: "<จำนวนวันที่ต้องย้อน>"`
2. รัน tag `validated` แล้ว `curated` (**ไม่ติ๊ก** dependencies / full refresh) — dim/fact rebuild ทุกคืนอยู่แล้ว
3. **คืนค่าเป็น `"1"`** ทันทีที่เสร็จ
4. ตรวจ Q2 (วันหายหายไปไหม) + Q6 (ไม่มีแถวซ้ำ)

ข้อยกเว้น: TW / DH / BT stock เป็น full load ไม่ต้อง backfill · BT ขาย diff ด้วย LAG ที่ไม่กรอง asatdate จึงคำนวณย้อนเองได้
รายละเอียดทั่วไป: `document/project_wiki/operations/running-and-troubleshooting.md` §Backfilling

## 6. ยอดเป็น -1 เพิ่มขึ้น (สาขา/สินค้าใหม่)

1. Q4 → ห้างไหน · Q4b → รหัสไหน · Q5 → อะไรที่ "รอข้อมูล Master"
2. ส่งรายการรหัสให้ BI/MDS เติมใน mds (คอลัมน์ ห้าง/Store/Branch/Zone สำหรับสาขา · `product_mdt_code` → `product_mac5_code` สำหรับสินค้า)
3. รอบถัดไป dim rebuild เอง → ตรวจ Q4 อีกครั้ง
- ห้ามแก้ใน SQL · ข้อยกเว้นที่มีอยู่แล้วคือ GH→GB (บท 04 ข้อ 5)

## 7. ยอดไม่ตรงกับ BI

1. เทียบ**รายเดือน**เท่านั้น (Q3) ไม่ใช่รายวัน
2. ไล่ตามลำดับนี้ ก่อนสรุปว่าโค้ดผิด:
   | ตรวจ | ใช้ |
   |---|---|
   | วันหาย (ฟีดไม่ครบ) | Q2 |
   | ยอดที่ตั้งใจตัด: ปั๊ม Hitachi (GB), Segment `00221/00222` (GB, fact เท่านั้น), วัน TW ที่ < 30 สาขา | บท 05 ข้อ 11 |
   | ยอด -1 / กลุ่ม 999 ที่ BI อาจกรองทิ้ง | Q4, Q5 |
   | BT ยอดไปกองวันถัดไป (`date_is_estimated`) | กระทบรายวัน ไม่กระทบรายเดือน |
   | ฝั่ง BI ลงวันไม่ตรงวันขาย | เทียบรายเดือนแล้วหาย |
3. ถ้ายังต่างและอธิบายไม่ได้ → เจาะสาขา (Q3b) แล้วเปิด raw ของสาขานั้นดู

## 8. เพิ่มห้างใหม่

1. Airflow: โฟลเดอร์ห้างบน VM + `SCHEMA_MAP` + โฟลเดอร์ GCS (`GCS_SALEOUT_MDT/<ห้าง>/`)
2. Initial: external table ใน `create_all_table_raw_saleout_mdt`
3. Validated: ไฟล์ใหม่ใต้ `validated/saleout_mdt/<ห้าง>/` (ใช้ skill `add-validated-table`)
4. Curated: CTE ห้างใหม่ + UNION + **`feed_start` 1 แถว + กรองวันเดียวกันใน CTE** (แก้คู่ ไม่งั้นยอดนับซ้ำกับไฟล์ BI)
5. mds: สาขา/สินค้า · `dim_report` บรรทัดของห้าง · region ของ `store_code`
6. ตรวจ: Q6 → Q7 → Q4 → Q3

## 9. งานที่รอวันเปลี่ยน (ตั้งเตือนไว้)

| เมื่อ | ต้องทำ |
|---|---|
| MDS เปลี่ยน GH เป็น GB ครบ | ลบ GH_→GB_ **2 ที่** (`dim_target_saleout_mdt` :96 · `dim_target_series_mdt` :77) แล้วตรวจ Q8 = 0 |
| BI ยืนยันการตัด Segment GB | ย้ายจาก literal ใน fact :169 ไปเป็น master รายการตัดออก |
| หาสาเหตุช่องว่าง 19% เม.ย.–ก.ค. ได้ | ค่อยพิจารณาเปิด `lastyear_topup` |

## 10. ใครถามใคร
| เรื่อง | ถาม |
|---|---|
| ไฟล์ห้างไม่มา | ❓ ผู้ประสานงานห้าง |
| mds (สาขา/สินค้า/เป้า/PC) | Wisut (MDS) |
| นิยามยอด / เกณฑ์เทียบ / ตัดอะไรออก | BI (โอ๊ต) / คุณกุ้ง |
| Airflow VM, สิทธิ์ SharePoint | ❓ admin |
