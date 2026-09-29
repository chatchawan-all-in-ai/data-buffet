# สถาปัตยกรรม Data-Buffet

> ตัวเลขทุกตัวในหน้านี้นับจาก `definitions/` จริงเมื่อ 2026-09-15

## ภาพรวม

```
GCS AVRO files  gs://file-raw-data  (Hive partition: ASATDATE=YYYYMMDD)
      │
      ▼
┌────────────┐  definitions/initial/ (17 ไฟล์)
│  INITIAL   │  external table + CREATE SCHEMA + UDF 7 ตัว (function_dataset)
└────────────┘
      ▼
┌────────────┐  definitions/validated/ (136 ไฟล์ = 132 ตาราง + 4 schema bootstrap)
│ VALIDATED  │  cast + TRIM + NULL + dedup (QUALIFY) — 1 ไฟล์ต่อ 1 ตารางต้นทาง
└────────────┘  mac5 87 · cis360 25 · mastersku 12 · saleout_mdt 12
      ▼
┌────────────┐  definitions/curated/ (11 ไฟล์ = 7 ตาราง + 4 schema bootstrap)
│  CURATED   │  business logic: status lookup, split-sale, JSON parsing, รวม sell-out
└────────────┘
      ├───────────────────────────────┐
      ▼                               ▼
┌────────────┐                 ┌────────────┐
│ DIMENSION  │ ◄──── SK ────── │    FACT    │
│ (67 ไฟล์)  │                 │ (15 ไฟล์)  │
└────────────┘                 └────────────┘
 dimension_table                 fact_table
      └───────────────┬───────────────┘
                      ▼
              ┌────────────┐  definitions/view/ (33 ไฟล์)
              │    VIEW    │  BI/reporting views (type: "view")
              └────────────┘  dimension_view · fact_view · bridge_dataset ·
               view schemas    onetime · process_dataset

ท่อเสริม:  CDC (cdc_dataset, 2 ไฟล์)  →  PROCESS (process_dataset, 2 ไฟล์ —
           AI.GENERATE แกะที่อยู่ไทย + RLS)
ต้นทางภายนอก:  mds_dataset (master data service — repo นี้ไม่ได้สร้าง)
```

## หน้าที่ของแต่ละชั้น

| ชั้น | ไฟล์ | Dataset | Materialization | หน้าที่ |
|---|---:|---|---|---|
| Initial | 17 | `raw_*`, `function_dataset` | operations | external table ชี้ GCS, สร้าง schema/UDF |
| Validated | 136 | `validated_*` | incremental / table | cast type, ลบ string ว่าง, dedup ตาม PK |
| Curated | 11 | `curated_*` | incremental / table | join ข้าม validated, JSON parsing, split-sale (ag01), รวม sell-out ทุกห้าง |
| Dimension | 67 | `dimension_table` | table rebuild / operations MERGE | ออก surrogate key, SCD |
| Fact | 15 | `fact_table` | table / operations | join SK ทุก dimension, retention 4 ปี |
| View | 34 | `dimension_view`, `fact_view`, `bridge_dataset`, `onetime`, `process_dataset` | view | BI/reporting อ่านจาก dim/fact/curated (`type: "view"`, tag `view`) |
| CDC | 2 | `cdc_dataset` | operations | จับ NEW/CHANGED จาก config |
| Process | 2 | `process_dataset` | table / operations | AI แกะที่อยู่ไทย (row ที่ CDC เปลี่ยน) + RLS (`rls_customer360`) |

### แยกย่อย dimension 67 ไฟล์

| กลุ่ม | จำนวน | ลักษณะ |
|---|---:|---|
| mds full daily rebuild | **41** | `type: "table"` · SK ออกใหม่ทุกวัน |
| mds MERGE legacy | 2 | `dim_company`, `dim_aging_rang` · SK เสถียร |
| lake MERGE (validated/curated) | 10 | SK เสถียร ไม่มี tombstone |
| full rebuild อื่น | 11 | `_last` 7 ตัว, target 2 ตัว, `dim_store`, `dim_pump_information` |
| operations อื่น | 3 | `dim_calendar`, `dim_aging`, `update_sk_sale_rep_group` |

> วิธีนับที่เชื่อถือได้: จับ `mds_data_\w+` **ทั้งไฟล์** ไม่ใช่แค่ `name: "..."` —
> dim ชุด MDT อ้าง mds ผ่าน const ใน `js {}` ถ้าจับแค่ `name:` จะนับขาด 6 ตัว

### แยกย่อย fact 15 ไฟล์

| กลุ่ม | จำนวน | ไฟล์ |
|---|---:|---|
| MAC5 ขาย/วางบิล/รับชำระ | 9 | `fact_order`, `fact_invoice`, `fact_quotation`, `fact_transaction_delivery`, `fact_delivery`, `fact_transcation`, `fact_chq`, `fact_mir_vs`, `fact_mir_rs` |
| store (แยกตามคลัง) | 3 | `fact_order_store`, `fact_invoice_store`, `fact_backlog_store` |
| SALEOUT_MDT | 3 | `fact_saleout_mdt`, `fact_stock_mdt`, `fact_stock_mdt_monthly` |

## จุดสำคัญเชิงออกแบบ

### Surrogate key (SK) — 2 ระบบ (ตั้งแต่ 2026-07-20)

- **SK เสถียร** (MERGE dims: `dim_company`, `dim_aging_rang` + lake dims 10 ตัว):
  ออกด้วย `max_sk + ROW_NUMBER()` + dual self-join รักษา SK เดิมตลอดชีพ —
  ห้าม regenerate เด็ดขาด ดู
  [project_wiki/dimension/merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md)
- **SK รายวัน** (mds dims **41 ตัว** — ปั้น full ใหม่ทุกวัน): `ROW_NUMBER()` ออกเลขใหม่
  ทุกคืน — consumer ทุกตัว re-derive รายวัน (ตรวจครบแล้ว) **ห้าม persist SK
  พวกนี้ข้ามวัน** ดู
  [project_wiki/dimension/full-rebuild-pattern.md](../project_wiki/dimension/full-rebuild-pattern.md)

### mds_dataset และการจัดการ delete/overwrite

ตาราง `mds_data_*_master` ทุกตัวมี `id`, `is_active`, `updated_at`
และรองรับ **overwrite import** (ล้างแล้วลงใหม่ = id ใหม่หมด)

- **dims 41 ตัว (full rebuild)**: อ่านเฉพาะ `is_active = TRUE` ทั้งตารางทุกคืน —
  soft delete และ overwrite import หายเองอัตโนมัติ (ตัดสินใจ 2026-07-20)
- **dims 2 ตัว (MERGE)**: window `MDS_BACKFILL_DAYS` (1 วัน) + tombstone DELETE
  ลบ row ที่ต้นทาง `is_active = FALSE` (hard delete, ตัดสินใจ 2026-07-10)

### MAC5 multi-company

5 บริษัท (ag01/aa05/ab01/ac02/ak02) → raw dataset แยกกัน → validated รวมด้วย
UNION ALL + คอลัมน์ `company_id` (14 ตาราง) — logic พิเศษบางอย่างเฉพาะ ag01
(split-sale, sign flip)

### Document-grain purge (2026-09-10)

`mih` / `mil` / `mir` ฝั่ง validated และ `curated_mil` ใช้ `pre_operations` ลบ
**ทั้งเอกสาร** ก่อน insert เพราะ MERGE บน PK ระดับบรรทัดลบบรรทัดที่ต้นทางลบไปไม่ได้
วัดได้ 476 แถว / 9.2 ล้านบาทบน `mil` และ 506 / 10.4 ล้านบาทบน `mir`
ดู [project_wiki/validated/validated-layer.md](../project_wiki/validated/validated-layer.md)

### Retention

- Fact: rolling 4 ปี (ตัดที่ต้นปี) — ยกเว้น `fact_backlog_store` ที่ผูกกับ snapshot
  ล่าสุดของ `cps`
- CDC change log: 7 วัน (partition expiration)

## แผนผัง dependency หลัก

```
dim_company (root)
  ├─ mds dims เกือบทุกตัว
  ├─ dim_customer ─ dim_customer_grade / dim_group_customer*
  ├─ dim_order ─ dim_invoice
  └─ dim_*_last (7 ตัว) ─ update_sk_sale_rep_group
        └─ dim_target_product_group_by_sale ─ ..._dayofwork (join dim_calendar)

dim_zone_mdt → dim_zone_manager_mdt → dim_sales_branch_mdt → dim_pc
                                                           → dim_target_saleout_mdt

fact_quotation → fact_order → fact_invoice          (SK ต่อเป็นทอด)
fact_transaction_delivery → fact_delivery
fact_chq → fact_mir_vs → fact_mir_rs                (dim_aging อ่าน fact_mir_vs)
fact_stock_mdt → fact_stock_mdt_monthly
fact_transcation (join ~20 dims + onetime.Transaction_Data_Mart)
   └─ dim_pump_information อ่านกลับจาก fact_transcation
```

แผนผังเต็มที่ generate จากโค้ดจริง: [diagrams/pipeline_lineage.md](../diagrams/pipeline_lineage.md)
(อย่าแก้มือ — รัน `python document/diagrams/generate_lineage.py`)

รายละเอียดเชิงลึกทุกชั้น: [project_wiki/](../project_wiki/README.md)
