---
type: BigQuery Table
title: "crm_combo_set_item"
description: "One row = one product line within a combo set, a record of source table `crm_combo_set_item` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=crm_combo_set_item&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: crm_combo_set_item
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

External table over AVRO files in `gs://file-raw-data/derp_temp/crm_combo_set_item/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `crm_combo_set_item` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Items in each combo set with price and quantity.

Read by: [validated_derp.crm_combo_set_item](/validated/validated_derp/crm_combo_set_item.md).

# Grain and key

One row per source record per `ASATDATE` partition. There is no key at this layer; see the [validated table card](../../validated/validated_derp/crm_combo_set_item.md) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `combo_set_item_id` | STRING | รหัสรายการสินค้าในชุดคอมโบ |
| `combo_set_id` | STRING | รหัสชุดคอมโบที่อ้างอิง |
| `product_id` | STRING | รหัสสินค้าที่อยู่ในชุดคอมโบ |
| `product_code` | STRING | รหัสสินค้า (Snapshot) |
| `product_name` | STRING | ชื่อสินค้า (Snapshot) |
| `barcode` | STRING | บาร์โค้ดสินค้า (Snapshot) |
| `quantity` | FLOAT64 | จำนวนสินค้าต่อชุดคอมโบ (ค่าเริ่มต้น 1) |
| `is_freebie` | BOOL | ระบุว่ารายการสินค้านี้เป็นของแถมหรือไม่ (ค่าเริ่มต้น false) |
| `normal_price` | FLOAT64 | ราคาปกติของสินค้า (ก่อนโปรโมชัน) |
| `special_price` | FLOAT64 | ราคาพิเศษของสินค้า |
| `promotion_price` | FLOAT64 | ราคาขายของสินค้าภายใต้ชุดคอมโบนี้ (ค่าเริ่มต้น 0) |
| `sort_order` | INT64 | ลำดับการแสดงผลรายการสินค้าในชุด (ค่าเริ่มต้น 0) |
| `created_by` | STRING | ผู้สร้างรายการ |
| `created_at` | STRING | วันที่และเวลาที่สร้างรายการ |
| `updated_by` | STRING | ผู้แก้ไขรายการล่าสุด |
| `updated_at` | STRING | วันที่และเวลาที่แก้ไขล่าสุด |
| `mac5_code` | STRING | MAC5 item code associated with the combo-set line. |
| `d365_variant` | STRING | D365 product variant identifier. |
| `ASATDATE` | STRING | Hive partition column (`YYYYMMDD`) identifying the extract date. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` preceded by `DROP TABLE IF EXISTS`.
- The external table stores metadata in BigQuery; queries read the GCS AVRO files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/crm_combo_set_item/*`.
- The extract job writes files to the bucket; the external table sees them without a daily Dataform refresh.

# Examples

Rows from the latest extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.crm_combo_set_item`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-level row counts by extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.crm_combo_set_item`
GROUP BY ASATDATE
ORDER BY ASATDATE
```
