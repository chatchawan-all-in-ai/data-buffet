---
type: BigQuery Table
title: "crm_combo_set"
description: "One row = one combo-set header, a record of source table `crm_combo_set` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_combo_set&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_combo_set
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_combo_set/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_combo_set` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Combo set (sales BOM / bundle) header document.

Read by: [validated_derp.crm_combo_set](/validated/validated_derp/crm_combo_set.md).

# Grain and key

One row per source record per `ASATDATE` partition. There is no key at this layer; see the [validated table card](../../validated/validated_derp/crm_combo_set.md) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `combo_set_id` | STRING | รหัสชุดคอมโบ (UUID v7, สร้างอัตโนมัติ) |
| `code` | STRING | รหัสชุดคอมโบแบบ Business-facing เช่น COMBOSET00001 (unique เมื่อไม่เป็น NULL) |
| `name` | STRING | ชื่อชุดคอมโบ |
| `usage_type` | STRING | ประเภทการใช้งานชุดคอมโบ: 'sale'=ใช้ได้กับการขายทั่วไปตามเขตการขาย, 'customer'=จำกัดเฉพาะลูกค้าที่กำหนด, 'private'=ใช้ภายในองค์กร |
| `start_date` | STRING | วันที่เริ่มมีผลของชุดคอมโบ |
| `end_date` | STRING | วันที่สิ้นสุดผลของชุดคอมโบ (ต้อง >= start_date) |
| `status` | STRING | สถานะชุดคอมโบ: 'active' \| 'inactive' \| 'deleted' (ค่าเริ่มต้น active) |
| `created_by` | STRING | ผู้สร้างรายการ |
| `created_by_name` | STRING | ชื่อผู้สร้างรายการ (Snapshot) |
| `created_at` | STRING | วันที่และเวลาที่สร้างรายการ |
| `updated_by` | STRING | ผู้แก้ไขรายการล่าสุด |
| `updated_by_name` | STRING | ชื่อผู้แก้ไขรายการล่าสุด (Snapshot) |
| `updated_at` | STRING | วันที่และเวลาที่แก้ไขล่าสุด |
| `deleted_at` | STRING | วันที่ลบรายการ (soft delete) |
| `ASATDATE` | STRING | Hive partition column (`YYYYMMDD`) identifying the extract date. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` preceded by `DROP TABLE IF EXISTS`.
- The external table stores metadata in BigQuery; queries read the GCS AVRO files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_combo_set/*`.
- The extract job writes files to the bucket; the external table sees them without a daily Dataform refresh.

# Examples

Rows from the latest extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_combo_set`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-level row counts by extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_combo_set`
GROUP BY ASATDATE
ORDER BY ASATDATE
```
