---
type: BigQuery Table
title: "crm_combo_set_sale_territory"
description: "One row = one sales-territory assignment to a combo set, a record of source table `crm_combo_set_sale_territory` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_combo_set_sale_territory&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_combo_set_sale_territory
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_combo_set_sale_territory/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_combo_set_sale_territory` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Sales territories where the combo set is usable (usage_type = sale).

Read by: [validated_derp.crm_combo_set_sale_territory](/validated/validated_derp/crm_combo_set_sale_territory.md).

# Grain and key

One row per source record per `ASATDATE` partition. There is no key at this layer; see the [validated table card](../../validated/validated_derp/crm_combo_set_sale_territory.md) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `combo_set_sale_territory_id` | STRING | รหัสรายการเขตการขายที่ผูกกับชุดคอมโบ |
| `combo_set_id` | STRING | รหัสชุดคอมโบที่อ้างอิง |
| `combo_set_code` | STRING | รหัสชุดคอมโบ (Snapshot, denormalized) |
| `sale_territories_id` | STRING | รหัสเขตการขายที่ชุดคอมโบนี้ใช้งานได้ |
| `path_id` | STRING | Path ของเขตการขายแบบลำดับชั้น อ้างอิงด้วย id (รูปแบบ parent_id/child_id/...) (Snapshot) |
| `path_code` | STRING | Path ของเขตการขายแบบลำดับชั้น อ้างอิงด้วย code เช่น SA/SA_13 (Snapshot) |
| `path_name` | STRING | Path ของเขตการขายแบบลำดับชั้น อ้างอิงด้วยชื่อ (Snapshot) |
| `created_at` | STRING | วันที่และเวลาที่สร้างรายการ (ค่าเริ่มต้น now()) |
| `created_by` | STRING | ผู้สร้างรายการ |
| `updated_at` | STRING | วันที่และเวลาที่แก้ไขล่าสุด (ค่าเริ่มต้น now()) |
| `updated_by` | STRING | ผู้แก้ไขรายการล่าสุด |
| `created_by_name` | STRING | ชื่อผู้สร้างรายการ (Snapshot) |
| `updated_by_name` | STRING | ชื่อผู้แก้ไขรายการล่าสุด (Snapshot) |
| `ASATDATE` | STRING | Hive partition column (`YYYYMMDD`) identifying the extract date. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` preceded by `DROP TABLE IF EXISTS`.
- The external table stores metadata in BigQuery; queries read the GCS AVRO files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_combo_set_sale_territory/*`.
- The extract job writes files to the bucket; the external table sees them without a daily Dataform refresh.

# Examples

Rows from the latest extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_combo_set_sale_territory`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-level row counts by extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_combo_set_sale_territory`
GROUP BY ASATDATE
ORDER BY ASATDATE
```
