# Glossary — คำศัพท์และแนวคิดหลักของ Data-Buffet

คำศัพท์ที่ developer ใหม่ต้องรู้ก่อนอ่านโค้ดในโปรเจกต์นี้

## แนวคิดสถาปัตยกรรม

| คำ | ความหมาย |
|---|---|
| **Medallion architecture** | การแบ่งชั้นข้อมูล raw → validated → curated → (dimension/fact) แต่ละชั้นสะอาดและพร้อมใช้ขึ้นเรื่อย ๆ |
| **Star schema** | โมเดลข้อมูลชั้นบนสุด: fact table ตรงกลาง join กับ dimension รอบ ๆ ด้วย surrogate key |
| **Layer / ชั้น** | initial → validated → curated → dimension + fact (มี cdc/process เป็นท่อเสริม) |
| **Dataform** | Framework ที่ใช้ orchestrate SQL ใน BigQuery — ไฟล์ `.sqlx` = SQL + JavaScript template |
| **SQLX** | ไฟล์ Dataform: `config {}` (metadata) + `js {}` (ตัวแปร) + ตัว SQL ที่มี `${...}` template |

## Key และ ID

| คำ | ความหมาย |
|---|---|
| **SK (Surrogate Key)** | คีย์ตัวเลขที่ระบบสร้างเอง (`CompanySK`, `SaleRepSK`, `WeightSK`, ...) ใช้ join ระหว่าง fact ↔ dimension ห้ามเอาไปมีความหมายทางธุรกิจ |
| **Natural key / Business key** | คีย์จากระบบต้นทาง เช่น `CompanyID + StkCode` ใช้จับคู่ว่า row ต้นทางตรงกับ dimension row ไหน |
| **MdsID** | คอลัมน์ในตาราง dimension เก็บค่า `id` ของ row ต้นทางจาก `mds_dataset` ใช้ทั้ง dedup (join `t3`) และลบ row ที่ต้นทาง `is_active = FALSE` |
| **max_sk + ROW_NUMBER()** | วิธีออก SK ใหม่: หา `MAX(SK)` เดิม แล้วบวก `ROW_NUMBER()` ให้ row ใหม่ที่ยังไม่มี SK |
| **Dangling FK / orphan** | ค่า SK ใน fact ที่ไม่มีอยู่ใน dimension แล้ว (เช่นหลังลบ row) — โปรเจกต์นี้สแกนแล้ว ณ 2026-07 ไม่มีค้าง |

## ข้อมูลและแหล่งข้อมูล

| คำ | ความหมาย |
|---|---|
| **MAC5** | ระบบ POS/บัญชี มี 5 บริษัท (ag01, aa05, ab01, ac02, ak02) แต่ละบริษัทมี raw dataset แยก รวมเป็น `validated_mac5` ด้วยคอลัมน์ `company_id` |
| **MASTERSKU** | Product master (สี ขนาด มิติสินค้า — มี JSON ซ้อน) |
| **CIS360** | ข้อมูลอ้างอิงลูกค้า |
| **SALEOUT_MDT** | ข้อมูล sell-out จากห้าง modern trade — ขอบเขตและสายข้อมูลปัจจุบันดู [Source Systems — SALEOUT_MDT](../project_wiki/overview/source-systems.md#saleout_mdt--sell-out-modern-trade) |
| **mds_dataset** | ตาราง master-data-service ที่โหลดเข้ามาจากภายนอก (ไม่ได้สร้างโดย repo นี้) — เป็นต้นทางของ dimension ส่วนใหญ่ ทุกตารางมี `id`, `is_active`, `updated_at` |
| **ASATDATE / asatdate** | วันที่ของ snapshot ข้อมูล (string `YYYYMMDD` ใน raw → `DATE` ใน validated) เป็น partition column หลักของตาราง incremental |
| **AVRO / external table** | ไฟล์ raw บน GCS (`gs://file-raw-data`) อ่านผ่าน BigQuery external table — ข้อมูลจริงอยู่บน GCS |

## Pattern ที่เจอบ่อย

| คำ | ความหมาย |
|---|---|
| **Full load** | สร้างตารางใหม่ทั้งก้อนทุกรอบ — ใช้กับ reference data ขนาดเล็ก (tag `validated_full`) |
| **Incremental** | โหลดเฉพาะ partition ช่วงหลัง (`asatdate >= CURRENT_DATE('Asia/Bangkok') - N`) (tag `validated_incremental`) |
| **QUALIFY dedup** | `QUALIFY ROW_NUMBER() OVER(PARTITION BY <pk> ORDER BY file_load_datetime DESC) = 1` — เก็บ row ล่าสุดต่อคีย์ |
| **MERGE upsert** | `MERGE ... WHEN MATCHED UPDATE / WHEN NOT MATCHED INSERT` — ใช้ใน dimension ที่ต้องรักษา SK เดิม (dim_company, dim_aging_rang, lake dims) |
| **Full rebuild dim** | pattern หลักของ mds dims (ตั้งแต่ 2026-07-20): `type: "table"` ปั้นใหม่ทุกวันจาก `is_active = TRUE` — SK ออกเลขใหม่ทุกวัน ห้ามเก็บข้ามวัน |
| **mds inactive DELETE (tombstone)** | ท้าย dimension MERGE (เหลือ 2 ตัว): `DELETE FROM dim WHERE MdsID IN (SELECT id FROM mds WHERE is_active = FALSE)` — ลบ row ที่ต้นทาง soft-delete |
| **Overwrite import** | โหมด import ของ mds ที่ล้างตารางแล้วลงใหม่ (id เปลี่ยนหมด) — full rebuild รองรับเองอัตโนมัติ |
| **MDS_BACKFILL_DAYS** | ตัวแปรโปรเจกต์ (ปัจจุบัน `1`) จำกัดหน้าต่าง `updated_at` ของ dim แบบ MERGE (full rebuild ไม่ใช้) |
| **BACKFILL_DAYS** | ตัวแปรโปรเจกต์ (ปัจจุบัน `1`) หน้าต่างย้อนหลังของ incremental window ใน validated/curated — ตั้งชั่วคราวเป็นเลขมากขึ้นเพื่อเก็บข้อมูลย้อนหลังหลายวัน แล้วตั้งกลับเป็น `1` |
| **operations type** | ไฟล์ Dataform ที่รัน raw BigQuery script (`BEGIN...END`) — Dataform ไม่จัดการ schema/lineage ให้ ตารางต้องมีอยู่ก่อน |
| **cleanString** | helper แปลง `''` → `NULL` + TRIM — มาตรฐานการจัดการ string ทั้งโปรเจกต์ |
| **Bangkok timezone** | ทุกการคำนวณวันที่ใช้ `CURRENT_DATE('Asia/Bangkok')` เสมอ |
| **Waiting Master** | placeholder row ใน `dim_stk_mkt` (MdsID = NULL) สำหรับ stkcode ที่ยังไม่มี master |

## เครื่องมือ

| คำ | ความหมาย |
|---|---|
| **Dataform compile** | สร้าง execution graph — วิธีตรวจและข้อจำกัดดู [run/debug guide](../how-to/run-and-debug.md#compile-กับ-sql-dry-run) |
| **Dataform execution** | รัน action/tag ที่เลือก — วิธีรันดู [run/debug guide](../how-to/run-and-debug.md#รันด้วย-tag) |
| **`bq` CLI** | Query BigQuery ตรง ๆ — ต้องระบุ `--project_id=databuffet-nonprd` เสมอ |

## คำที่เพิ่มมาใหม่ (2026-09)

| คำ | ความหมาย |
|---|---|
| **sell-out / sell-in** | sell-**out** = ห้างขายออกจากสาขาให้ผู้บริโภค (ชุด MDT) · sell-**in** = เราขายเข้าห้าง (`view_fact_salein_mdt`) |
| **MDT** | Modern Trade — ห้างค้าปลีกรายใหญ่ · dim/fact ชุดนี้ลงท้ายด้วย `_mdt` |
| **degenerate dimension** | รหัสจากต้นทางที่เก็บไว้ใน fact ตรง ๆ เพื่อสืบกลับ (เช่น `store_code`, `product_code` ใน fact MDT) คู่กับ SK ที่ใช้ join จริง |
| **`date_is_estimated`** | ธงใน `curated_saleout_mdt` — `TRUE` แปลว่าห้างส่งยอดมาเป็นช่วงวัน เราเฉลี่ยลงรายวันเอง (บุญถาวร) |
| **`FlagFree`** | ธงของแถมใน `fact_order_store` / `fact_invoice_store` / `fact_backlog_store` · ⚠️ **นิยามไม่ตรงกัน 2 แบบ** — สองตัวแรกใช้ `milSum = 0`, backlog ใช้ `cpssumreq = 0` ดู known-issues.md |
| **`StoreSK` / `ReportStore`** | `dim_store` — คลัง/สาขาจาก `validated_mac5.sto` · `ReportStore` ยุบ `stogroup` ที่ไม่อยู่ใน kk/pk/lp/ub/hy เป็น `'KTB'` — **เป็นถังรวม ไม่ใช่คลังของกรุงไทย** |
| **doc-grain purge** | `pre_operations` ลบ**ทั้งเอกสาร**ก่อน insert — จำเป็นเพราะ MERGE บน PK ระดับบรรทัดลบบรรทัดที่ต้นทางลบไปไม่ได้ (`mih`/`mil`/`mir`/`curated_mil`) |
| **drift (view)** | repo กับ BigQuery ไม่ตรงกัน — เกิดจากคนแก้ view บน console หรือ repo แก้แล้วยังไม่ได้รัน tag `view` · ตรวจด้วย skill `bq-drift-scan` |
