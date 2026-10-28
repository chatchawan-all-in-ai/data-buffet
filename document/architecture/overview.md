# สถาปัตยกรรม Data-Buffet

> จำนวนไฟล์ต่อชั้นไม่เขียนซ้ำในหน้านี้ — ดูตัวเลขล่าสุดที่ generate จากโค้ดใน
> [diagrams/pipeline_lineage.md](../diagrams/pipeline_lineage.md#1-layer-overview)
> · โครงสร้างในหน้านี้ตรวจกับ `definitions/` เมื่อ 2026-10-18

## ภาพรวม

```
GCS files  gs://file-raw-data  (AVRO, Hive partition: ASATDATE=YYYYMMDD · มี CSV 1 ตาราง)
      │
      ▼
┌────────────┐  definitions/initial/
│  INITIAL   │  external table + UDF 7 ตัว (function_dataset) + ไฟล์ drop
└────────────┘  ⚠️ tag `initial` ลบตาราง validated ของ source ที่ไม่ใช่ MAC5 ด้วย
      ▼
┌────────────┐  definitions/validated/ (ตาราง + schema bootstrap 1 ไฟล์ต่อ source)
│ VALIDATED  │  cast + TRIM + NULL + dedup (QUALIFY) — 1 ไฟล์ต่อ 1 ตารางต้นทาง
└────────────┘  mac5 · cis360 · mastersku · master_sku · saleout_mdt · derp
      ▼
┌────────────┐  definitions/curated/ (ตาราง + schema bootstrap 1 ไฟล์ต่อ source)
│  CURATED   │  business logic: status lookup, split-sale, JSON parsing, รวม sell-out
└────────────┘
      ├───────────────────────────────┐
      ▼                               ▼
┌────────────┐                 ┌────────────┐
│ DIMENSION  │ ◄──── SK ────── │    FACT    │
└────────────┘                 └────────────┘
 dimension_table                 fact_table
      └───────────────┬───────────────┘
                      ▼
              ┌────────────┐  definitions/view/
              │    VIEW    │  BI/reporting views (type: "view")
              └────────────┘  dimension_view · fact_view · bridge_dataset ·
               view schemas    onetime · process_dataset · pub_sub

ท่อเสริม:  CDC (cdc_dataset)  →  PROCESS (process_dataset —
           AI.GENERATE แกะที่อยู่ไทย + RLS + นำร่องส่ง Pub/Sub)
ต้นทางภายนอก:  mds_dataset (master data service — repo นี้ไม่ได้สร้าง)
```

## หน้าที่ของแต่ละชั้น

| ชั้น | Dataset | Materialization | หน้าที่ |
|---|---|---|---|
| Initial | `raw_*`, `function_dataset` | operations | external table ชี้ GCS, สร้าง schema/UDF, ไฟล์ drop สำหรับ (re-)initial |
| Validated | `validated_*` | incremental / table | cast type, ลบ string ว่าง, dedup ตาม PK |
| Curated | `curated_*` | incremental / table | join ข้าม validated, JSON parsing, split-sale (ag01), รวม sell-out ทุกห้าง |
| Dimension | `dimension_table` | table rebuild / operations MERGE | ออก surrogate key, SCD |
| Fact | `fact_table` | table / operations | join SK ทุก dimension, retention 4 ปี |
| View | `dimension_view`, `fact_view`, `bridge_dataset`, `onetime`, `process_dataset`, `pub_sub` | view | BI/reporting อ่านจาก dim/fact/curated (`type: "view"`, tag `view`) |
| CDC | `cdc_dataset` | operations | จับ NEW/CHANGED จาก config |
| Pub/Sub | `pub_sub` | operations | `pub_sub_schema` สร้าง dataset · ที่อยู่ของตารางเตรียมข้อมูลก่อนส่ง Pub/Sub ในอนาคต (view ส่งออกอยู่ที่ `definitions/view/pub_sub/`) |
| Process | `process_dataset` | incremental / table / operations | AI แกะที่อยู่ไทย (row ที่ CDC เปลี่ยน) + RLS (`rls_customer360`) + [นำร่องส่ง Pub/Sub](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) |

### แยกย่อย dimension

| กลุ่ม | ลักษณะ |
|---|---|
| mds full daily rebuild (ค่าเริ่มต้น) | `type: "table"` · SK ออกใหม่ทุกวัน |
| mds MERGE legacy (2) | `dim_company`, `dim_aging_rang` · SK เสถียร |
| lake MERGE (validated/curated) (10) | SK เสถียร ไม่มี tombstone |
| mds + invoice MERGE (1) | `dim_customer_report_info` (2026-10-28) · SK เสถียร ไม่มี delete |
| full rebuild อื่น | `_last` 7 ตัว, target 2 ตัว, `dim_store`, `dim_pump_information`, `dim_product_series` (hard-code) |
| operations อื่น (3) | `dim_calendar`, `dim_aging`, `update_sk_sale_rep_group` |

จำนวนต่อกลุ่มและรายชื่อทุกไฟล์: [project_wiki/dimension/inventory.md](../project_wiki/dimension/inventory.md)

> วิธีนับที่เชื่อถือได้: จับ `mds_data_\w+` **ทั้งไฟล์** ไม่ใช่แค่ `name: "..."` —
> dim ชุด MDT อ้าง mds ผ่าน const ใน `js {}` ถ้าจับแค่ `name:` จะนับขาด

### แยกย่อย fact

| กลุ่ม | ไฟล์ |
|---|---|
| MAC5 ขาย/วางบิล/รับชำระ | `fact_order`, `fact_invoice`, `fact_quotation`, `fact_transaction_delivery`, `fact_delivery`, `fact_transcation`, `fact_chq`, `fact_mir_vs`, `fact_mir_rs` |
| store (แยกตามคลัง) | `fact_order_store`, `fact_invoice_store`, `fact_backlog_store` |
| SALEOUT_MDT | `fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `fact_stock_mdt`, `fact_stock_mdt_monthly`, `fact_target_saleout_mdt`, `fact_target_series_mdt` |

## จุดสำคัญเชิงออกแบบ

### Surrogate key (SK) — 2 ระบบ (ตั้งแต่ 2026-07-20)

- **SK เสถียร** (MERGE dims: `dim_company`, `dim_aging_rang` + lake dims 10 ตัว + `dim_customer_report_info`):
  ออกด้วย `max_sk + ROW_NUMBER()` + dual self-join รักษา SK เดิมตลอดชีพ —
  ห้าม regenerate เด็ดขาด ดู
  [project_wiki/dimension/merge-sk-pattern.md](../project_wiki/dimension/merge-sk-pattern.md)
- **SK รายวัน** (mds dims แบบ full rebuild — ปั้น full ใหม่ทุกวัน): `ROW_NUMBER()` ออกเลขใหม่
  ทุกคืน — consumer ทุกตัว re-derive รายวัน (ตรวจครบแล้ว) **ห้าม persist SK
  พวกนี้ข้ามวัน** ดู
  [project_wiki/dimension/full-rebuild-pattern.md](../project_wiki/dimension/full-rebuild-pattern.md)

### mds_dataset และการจัดการ delete/overwrite

ตาราง `mds_data_*_master` ทุกตัวมี `id`, `is_active`, `updated_at`
และรองรับ **overwrite import** (ล้างแล้วลงใหม่ = id ใหม่หมด)

- **dims แบบ full rebuild**: อ่านเฉพาะ `is_active = TRUE` ทั้งตารางทุกคืน —
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

dim_zone_mdt → dim_zone_ta_mdt → dim_sales_branch_mdt → dim_pc
                                                     → dim_target_saleout_mdt
                                                     → dim_target_series_mdt (+ dim_product_series)
dim_region_last, dim_section_last → dim_sales_branch_mdt

fact_quotation → fact_order → fact_invoice          (SK ต่อเป็นทอด)
fact_transaction_delivery → fact_delivery
fact_chq → fact_mir_vs → fact_mir_rs                (dim_aging อ่าน fact_mir_vs)
fact_stock_mdt → fact_stock_mdt_monthly
curated_saleout_monthly_mdt → fact_saleout_monthly_mdt
fact_transcation (join ~20 dims + onetime.Transaction_Data_Mart)
   └─ dim_pump_information อ่านกลับจาก fact_transcation
```

แผนผังเต็มที่ generate จากโค้ดจริง: [diagrams/pipeline_lineage.md](../diagrams/pipeline_lineage.md)
(อย่าแก้มือ — รัน `python document/diagrams/generate_lineage.py`)

รายละเอียดเชิงลึกทุกชั้น: [project_wiki/](../project_wiki/README.md)
