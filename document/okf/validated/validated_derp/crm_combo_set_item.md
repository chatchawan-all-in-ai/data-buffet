---
type: BigQuery Table
title: "crm_combo_set_item"
description: "One row = one product line within a combo set from source table `crm_combo_set_item`, unique on (combo_set_item_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_combo_set_item&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_combo_set_item
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_combo_set_item.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_combo_set_item.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T22:03:22+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_combo_set_item`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Items in each combo set with price and quantity.

# Grain and key

One row per `combo_set_item_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

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
| `created_at` | DATETIME | วันที่และเวลาที่สร้างรายการ |
| `updated_by` | STRING | ผู้แก้ไขรายการล่าสุด |
| `updated_at` | DATETIME | วันที่และเวลาที่แก้ไขล่าสุด |
| `mac5_code` | STRING | MAC5 item code associated with the combo-set line. |
| `d365_variant` | STRING | D365 product variant identifier. |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/crm_combo_set_item.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `COALESCE(updated_at, created_at) DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_combo_set_item`
GROUP BY asatdate
ORDER BY asatdate DESC
```
