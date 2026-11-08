---
type: BigQuery Table
title: "crm_master_payment_term"
description: "One row = one payment term, a record of source table `crm_master_payment_term` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_master_payment_term&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_master_payment_term
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (definitions/initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:codex", at: "2026-11-08T22:03:22+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_master_payment_term/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_master_payment_term` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Payment term / credit days: N003, N014, N030, etc.

Read by: [validated_derp.crm_master_payment_term](/validated/validated_derp/crm_master_payment_term.md).

# Grain and key

One row per source record per `ASATDATE` partition. There is no key at this layer; see the [validated table card](../../validated/validated_derp/crm_master_payment_term.md) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `master_payment_term_id` | STRING | รหัสอ้างอิงหลัก |
| `payment_term_code` | STRING | รหัสเงื่อนไข \| เช่น N003 / N014 / N030 / N060 / N180 |
| `payment_term_name` | STRING | ชื่อเงื่อนไข \| เช่น ชำระเงิน 30 วัน นับจากวันที่ส่งสินค้า |
| `description` | STRING | คำอธิบายเพิ่มเติม |
| `credit_days` | INT64 | จำนวนวันเครดิต \| เช่น 3 / 14 / 30 / 60 / 180 |
| `order_sort` | INT64 | ลำดับการแสดงผล |
| `company_code` | STRING | รหัสบริษัท (NULL = ใช้ร่วมทุกบริษัท) |
| `organization_code` | STRING | รหัสหน่วยงาน (NULL = ใช้ร่วมทุกหน่วยงาน) |
| `status` | STRING | สถานะ: ACTIVE / INACTIVE |
| `created_at` | STRING | วันที่และเวลาที่สร้างข้อมูล |
| `updated_at` | STRING | วันที่และเวลาที่แก้ไขข้อมูลล่าสุด |
| `created_by_name` | STRING | ชื่อผู้สร้าง (denormalized) |
| `updated_by_name` | STRING | ชื่อผู้แก้ไข (denormalized) |
| `created_by` | STRING | ผู้สร้างข้อมูล |
| `updated_by` | STRING | ผู้แก้ไขข้อมูลล่าสุด |
| `term_kind` | STRING | Payment term category supplied by the source. |
| `ASATDATE` | STRING | Hive partition column (`YYYYMMDD`) identifying the extract date. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` preceded by `DROP TABLE IF EXISTS`.
- The external table stores metadata in BigQuery; queries read the GCS AVRO files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_master_payment_term/*`.
- The extract job writes files to the bucket; the external table sees them without a daily Dataform refresh.

# Examples

Rows from the latest extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_master_payment_term`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-level row counts by extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_master_payment_term`
GROUP BY ASATDATE
ORDER BY ASATDATE
```
