# Initial Layer — `definitions/initial/`

> **LLM context**: **17 files** that bootstrap everything: datasets, external tables over
> GCS AVRO, and UDFs. All `type: "operations"`. Tags: `initial` (create) and
> `re-initial` (drop for rebuild). Verified against the repo and
> `function_dataset.INFORMATION_SCHEMA.ROUTINES` on 2026-09-15.

## File map (17)

| File | Tag | หน้าที่ |
|---|---|---|
| `create_all_schema.sqlx` | — | `CREATE SCHEMA IF NOT EXISTS` ทุก dataset |
| `create_all_function.sqlx` | — | **7 UDFs** ใน `function_dataset` |
| `mac5/create_all_table_raw_mac5.sqlx` | initial | AG01 — **87 external tables** (13 hive-partitioned) |
| `mac5/create_all_table_raw_mac5_aa05.sqlx` | initial | AA05 — 14 tables (5 hive) |
| `mac5/create_all_table_raw_mac5_ab01.sqlx` | initial | AB01 — 14 tables (5 hive) |
| `mac5/create_all_table_raw_mac5_ac02.sqlx` | initial | AC02 — 14 tables (5 hive) |
| `mac5/create_all_table_raw_mac5_ak02.sqlx` | initial | AK02 — 14 tables (5 hive) |
| `mac5/drop_all_tables_validated_mac5.sqlx` | **re-initial** | DROP 86 validated_mac5 tables |
| `mac5/drop_all_tables_curated_mac5.sqlx` | **re-initial** | DROP 3 curated_mac5 tables |
| `cis360/create_all_table_raw_cis360.sqlx` | initial | 25 hive-partitioned external tables |
| `cis360/drop_all_tables_validated_cis360.sqlx` | initial | DROP 24 validated tables |
| `mastersku/create_all_table_raw_mastersku.sqlx` | initial | 11 hive-partitioned external tables |
| `mastersku/drop_all_tables_validated_mastersku.sqlx` | initial | DROP 11 validated tables |
| `saleout_mdt/create_all_table_raw_saleout_mdt.sqlx` | initial | 11 hive-partitioned external tables แยกตามร้าน (bt/gb/hp/tw) |
| `saleout_mdt/drop_all_tables_validated_saleout_mdt.sqlx` | initial | DROP 10 validated tables |
| `allkons_commission/create_all_table_raw_allkons_commission.sqlx` | initial | 7 hive-partitioned external tables |
| `allkons_commission/drop_all_tables_validated_allkons_commission.sqlx` | initial | DROP 7 validated tables |

> ⚠️ **ALLKONS_COMMISSION หยุดอยู่แค่ชั้นนี้** — ไฟล์ `definitions/validated/allkons_commission/`
> ถูกลบไปแล้วใน commit `74a10e0 "pause process data layer of commission"` · raw external
> table ยังสร้างอยู่และ dataset `validated_allkons_commission` ยังค้างใน BigQuery
> (ข้อมูลเก่า ไม่มีใครเติม) ถ้าจะรื้อฟื้นต้องเขียน validated ใหม่

## `create_all_schema.sqlx`

`CREATE SCHEMA IF NOT EXISTS` สำหรับ **ทุก** dataset: raw MAC5 ×5, raw/validated/curated
ต่อ source, `dimension_table`, `dimension_view`, `fact_table`, `fact_view`,
`bridge_dataset`, `process_dataset`, `cdc_dataset`, `function_dataset`, `onetime`
— ทั้งหมดใส่ `OPTIONS(location="us-central1")`

## `create_all_function.sqlx` — 7 UDFs

**BigQuery คือ source of truth ของไฟล์นี้** (ดูบันทึก drift ท้ายหัวข้อ) ตรวจตรงกัน
7/7 ตัวกับ `function_dataset.INFORMATION_SCHEMA.ROUTINES` เมื่อ 2026-09-15

| UDF | Signature | หน้าที่ |
|---|---|---|
| `fn_flag_exc` | `(mihcancel INT64, mihstatus INT64, FlagExc STRING)` | cancel/status → exclude flag |
| `fn_flag_sales_kpi` | `(mihcancel INT64, mihstatus INT64, rebate STRING)` | sales-KPI Yes/No |
| `fn_flag_scg` | `(mihvnos STRING, mihcus STRING)` | "ซื้อตรง"/"ซื้อผ่านร้าน" สำหรับ vnos ของ CRC |
| `fn_get_scg_customer_ids` | `()` — ไม่รับพารามิเตอร์ | คืนชุดรหัสลูกค้า SCG ที่ `fn_flag_scg` ใช้อ้างอิง |
| `fn_order_type` | `(mihref2 STRING)` | prefix `QOAG` → `Online-AllkonsM`, ที่เหลือ `Offline` (ใช้โดย `view_dim_order`) |
| `EXTRACT_CHQ_DATA` | `(memo_raw STRING, datec DATETIME, total FLOAT64)` → `STRUCT<chqmemo, extract_text, extract_value ARRAY<STRUCT<extract_date DATE, extract_amount FLOAT64>>>` | แกะ memo เช็ค/โอนภาษาไทย รองรับเดือนย่อไทย + แปลง พ.ศ. → ค.ศ. เริ่มแกะเฉพาะเมื่อ **trigger** ติด (ดูหัวข้อถัดไป) |
| `clean_company_prefix` | `(text_input STRING)` | ตัดคำนำหน้า (`บริษัท`, `บจก.`, `บมจ.`, `หจก.`, `ร้าน`, `ห้างหุ้นส่วนจำกัด`, `+` นำหน้า) และคำต่อท้าย (`จำกัด`, `(มหาชน)`) → เหลือชื่อบริษัทเปล่า ไว้จับคู่ |

> **UDF ไม่ใช่ Dataform action แยกตัว** — ทั้ง 7 ตัวถูกสร้างโดย `operations` action
> เดียวนี้ ผู้ใช้จึง `ref()` ไม่ได้ ให้ interpolate `${databuffet.FUNCTION_DATASET}`
> แทน และ **ห้ามใส่ชื่อ UDF ใน `dependencies[]`**

> **บันทึก drift (2026-07-24)**: ไฟล์นี้เคยมีแค่ 4 UDFs (`fn_order_type` หายทั้งตัว) และ
> `fn_flag_scg` ประกาศพารามิเตอร์เป็น `milvnos`/`milcus` ขณะที่ BigQuery ใช้
> `mihvnos`/`mihcus` · ยังมี **335 backslash ที่ไม่ได้ escape** รวมถึง `\1` ตัวหนึ่งที่ทำให้
> ทั้ง action compile ไม่ผ่าน ("octal escape") ซึ่งน่าจะเป็นสาเหตุที่ไฟล์หลุดจากความจริง
> ตั้งแต่แรก · regenerate ใหม่จาก `INFORMATION_SCHEMA.ROUTINES` · backslash ในโค้ด SQL
> ใช้ตัวเดียวตาม [coding-standard §3.3](../../coding-standards/sqlx-coding-standard.md)
> **ตรวจซ้ำ 2026-09-15: ตรงกับ BigQuery ครบ 7/7**

### `EXTRACT_CHQ_DATA` — รายการ trigger

`transfer_pos` คือ `COALESCE` ของ regex trigger บน `memo_raw` คืนตำแหน่งของ trigger
**ตัวแรก** ที่ติด · `0` = ไม่มี trigger แล้ว parser คืน NULL ทั้งก้อน · **ลำดับสำคัญ** —
ตัวก่อนหน้าชนะ การเติมท้ายรายการจึงไม่มีทางเปลี่ยนผลของ memo ที่ match อยู่แล้ว

| # | Trigger | หมายเหตุ |
|---|---|---|
| 1 | `โอน…` / `รับโอนแทน` / `**<ธนาคาร>` / `เปลี่ยนเช็ค` | ชื่อธนาคารภาษาไทยติดได้เฉพาะเมื่อมี `โอน` หรือ `**` นำหน้า |
| 2 | `เช็ค` | |
| 3 | `\b(?:kbank\|kbnak\|kasikorn\|kbiz\|bbl\|bualuang\|ktb\|krungthai\|krungsri\|scb\|scbt\|ttb\|tmb\|tbm\|thanachart\|gsb\|baac\|ghb\|uob\|tisco\|kkp\|cimb\|icbc\|hsbc\|citibank\|lhbank)\s*/\s*\d` | เพิ่ม 2026-08-10 · `/<ตัวเลข>` ท้ายเป็น **ข้อบังคับ** — memo จริงเขียน `kbank/908`, `scb/264` · ถ้าไม่มี `ค่า ON NET / KTB = 800611831` จะได้ยอดปลอม 800 ล้าน |
| 4 | `(?:รุด\|รูด\|รับ)\s*บัตร(?:เครดิต)?(?:คืน)?[^0-9\n]{0,10}(?:\d{1,2}/\d{1,2}\|(?:ยอด\|จำนวน\|เป็นเงิน\|=)\s*\d)` | เพิ่ม 2026-08-10 · วันที่-หรือ-ยอดท้ายเป็น **ข้อบังคับ** — 34 จาก 43 memo ที่มีคำว่า `รูดบัตร` คือ `ค่าเช่าเครื่องรูดบัตร` (ค่าเช่า EDC ไม่ใช่การชำระ) ต้องไม่ติด |

วัดบน `validated_mac5.chq` ทั้ง 76,573 แถวตอนเพิ่ม trigger 3–4:
**+60 แถวได้ยอดเพิ่ม, 0 แถวหาย, 1 แถวเปลี่ยน (`189` → `189,176` ซึ่งถูกขึ้น), 1 แถว noise**
(`to bbl/418` — trigger ติดแต่ไม่มียอดใน memo) · **รันการเทียบนี้ซ้ำทุกครั้งก่อนแก้รายการ trigger**

## รูปแบบ external table

**Incremental** (ตารางรายการเคลื่อนไหว) — ค้น Hive partition จากโฟลเดอร์ `ASATDATE=`:
```sql
CREATE OR REPLACE EXTERNAL TABLE `raw.<table>`
WITH PARTITION COLUMNS (ASATDATE STRING)
OPTIONS(format='AVRO',
        uris=['gs://file-raw-data/<gcs_prefix>/<table>/*'],
        hive_partition_uri_prefix='gs://file-raw-data/<gcs_prefix>/<table>/')
```

**Full** (ตารางอ้างอิง) — glob ตรง ไม่มี partition:
```sql
CREATE OR REPLACE EXTERNAL TABLE `raw.<table>`
OPTIONS(format='AVRO', uris=['gs://file-raw-data/<gcs_prefix>/<table>/*.avro'])
```

ทุกตารางมี `DROP TABLE IF EXISTS` นำหน้าเสมอ

### จุดที่ต้องรู้ต่อ source

- **MAC5 AG01** (`create_all_table_raw_mac5.sqlx`) เป็นไฟล์ใหญ่ที่สุด: 87 ตาราง โดย 13 ตัว
  เป็น hive-partitioned (`cql, rcv, cst, mih, cps, cps_dummy, mie, mie_dummy, mih2,
  mih_dummy, mil, mil_dummy, mir`) · `stg_report`/`stgacc` อ่านจากโฟลเดอร์ `mac5_report`
  ส่วน `tdelivery`/`ttrip*` อ่านจาก `mac5_gps`
- **MAC5 อีก 4 บริษัท** ไฟล์ละ 14 ตาราง: hive 5 ตัว (`cql, mih, mil, mir, mie`) + full
  (`ap_s, ar_s, chq, deb, dep, per, stg, stk, cfs`)
- **SALEOUT_MDT** มีการเปลี่ยนชื่อระหว่างโฟลเดอร์กับตาราง: โฟลเดอร์
  `reportsalesubscription` → ตาราง `report_sale_subscription`, `gb/*` → `saleout_gb`

## การผูก dependency

`create_all_table_raw_<source>` ขึ้นกับ `drop_all_tables_*` ของ source นั้น ส่วนไฟล์
`validated_schema_*` ขึ้นกับ create action อีกที · `dataform run --tags initial` จึง
สร้าง raw external table ใหม่ได้สะอาด

⚠️ tag `re-initial` **DROP ตาราง validated/curated ของ MAC5** — ใช้เฉพาะตอน rebuild
ทั้งก้อน ข้อมูลใน incremental table จะหายจนกว่าจะรันใหม่ (PreToolUse hook บล็อกคำสั่งนี้
ไว้ ต้องให้เจ้าของงานรันเอง)
