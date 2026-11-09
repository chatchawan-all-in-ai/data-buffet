---
type: BigQuery Table
title: "inventory_formula_versions"
description: "One row = one product formula version, a record of source table `inventory_formula_versions` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=inventory_formula_versions&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: inventory_formula_versions
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (definitions/initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:codex", at: "2026-11-09T02:05:00+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/inventory_formula_versions/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `inventory_formula_versions` table from DERP; nothing is cleaned or deduplicated here. Table meaning: BOM header — bom_type: Production | Bundle | Accessory.

Read by: [validated_derp.inventory_formula_versions](/validated/validated_derp/inventory_formula_versions.md).

# Grain and key

One row per source record per `ASATDATE` partition. There is no key at this layer; see the [validated table card](../../validated/validated_derp/inventory_formula_versions.md) for its key and deduplication rules.

# Schema

| Column | Type | Description |
|---|---|---|
| `formula_versions_id` | STRING |  Source formula versions id value. |
| `id` | STRING | Source row identifier. |
| `manufactured_item_number` | STRING | รหัสสินค้าที่ผลิต (FG) \| D365: manufactured_item_number (เดิม V1 ใช้ชื่อ item_number) |
| `formula_id` | STRING | รหัส BOM/สูตร เช่น 12610048_V1 \| D365: formula_id |
| `production_site_id` | STRING | รหัส Site ที่ผลิต เช่น KTB \| D365: production_site_id |
| `product_configuration_id` | STRING | Variant dimension ของสินค้าที่ผลิต — configuration \| D365: product_configuration_id (4/998 มีค่า) |
| `product_color_id` | STRING | Variant dimension — สี \| D365: product_color_id (793/998, 79%) |
| `product_size_id` | STRING | Variant dimension — ขนาด \| D365: product_size_id (795/998, 80%) |
| `product_style_id` | STRING | Variant dimension — สไตล์ \| D365: product_style_id (792/998, 79%) |
| `product_version_id` | STRING | Variant dimension — version สินค้า \| D365: product_version_id (0/998 ปัจจุบันไม่มีค่า) |
| `is_active` | STRING | สูตรที่ใช้งานอยู่ \| D365: is_active ('Y'/'N' — Mac5 ส่ง 'Yes'/'No' ต้อง normalize ก่อน merge) |
| `valid_from_date` | DATETIME | Source valid from date value. |
| `from_quantity` | FLOAT64 | ขนาด batch ต่ำสุดที่สูตรนี้มีผล (คู่กับ formula_batch_size กำหนดช่วง qty ที่ valid) \| D365: from_quantity |
| `bulk_item_number` | STRING | รหัสสินค้า bulk (ใช้กับสินค้าที่ผลิตแบบ bulk/ถัง) \| D365: bulk_item_number (0/998 ปัจจุบันไม่มีค่า) |
| `catch_weight_size` | FLOAT64 | ขนาด catch weight \| D365: catch_weight_size (0 ทุกแถวในข้อมูลปัจจุบัน) |
| `is_selected_for_designer` | STRING | เลือกใช้แสดงใน Designer tool หรือไม่ \| D365: is_selected_for_designer |
| `version_name` | STRING | ชื่อ version/สูตร \| D365: version_name |
| `changed_date` | DATETIME | วันที่แก้ไขเนื้อหาสูตรล่าสุด (ต่างจาก updated_at ที่เป็น audit ของระบบ) \| D365: changed_date |
| `formula_batch_size_multiples` | FLOAT64 | batch ต้องเป็นจำนวนเท่าของค่านี้ \| D365: formula_batch_size_multiples |
| `is_co_product_quantity_variation_allowed` | STRING | อนุญาตให้ co-product แปรผันปริมาณได้หรือไม่ \| D365: is_co_product_quantity_variation_allowed |
| `from_catch_weight_quantity` | FLOAT64 | จำนวน catch weight ต่ำสุด \| D365: from_catch_weight_quantity |
| `yield_percentage` | FLOAT64 | % yield ของการผลิต (ปกติ 100) \| D365: yield_percentage |
| `approver_personnel_number` | STRING | รหัสพนักงานผู้ approve \| D365: approver_personnel_number (684/998, 68.5%) |
| `formula_batch_size` | FLOAT64 | ขนาด batch สูงสุดที่สูตรนี้มีผล \| D365: formula_batch_size |
| `is_approved` | STRING | ผ่านการ approve แล้ว \| D365: is_approved ('Yes'/'No') |
| `will_cost_calculation_include_version` | STRING | รวม version นี้ในการคำนวณต้นทุนหรือไม่ \| D365: will_cost_calculation_include_version |
| `valid_to_date` | DATETIME | Source valid to date value. |
| `is_total_cost_allocation_used` | STRING | ใช้การกระจายต้นทุนรวมหรือไม่ \| D365: is_total_cost_allocation_used |
| `ivzs_bom_accessories` | STRING | Source ivzs bom accessories value. |
| `remarks` | STRING | หมายเหตุ \| D365: remarks (0/998 ปัจจุบันไม่มีค่า) |
| `created_datetime` | STRING | Source created datetime value. |
| `created_by` | STRING | D365: created_by |
| `updated_datetime` | STRING | Source updated datetime value. |
| `updated_by` | STRING | D365: updated_by (0/998 ปัจจุบันไม่มีค่า) |
| `product_id` | STRING | D365: product_id |
| `site_id` | STRING | FK → sites.id |
| `ASATDATE` | STRING | Hive partition column (`YYYYMMDD`) identifying the extract date. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` preceded by `DROP TABLE IF EXISTS`.
- The external table stores metadata in BigQuery; queries read the GCS AVRO files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/inventory_formula_versions/*`.
- The extract job writes files to the bucket; the external table sees them without a daily Dataform refresh.

# Examples

Rows from the latest extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.inventory_formula_versions`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-level row counts by extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.inventory_formula_versions`
GROUP BY ASATDATE
ORDER BY ASATDATE
```
