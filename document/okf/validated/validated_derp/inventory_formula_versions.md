---
type: BigQuery Table
title: "inventory_formula_versions"
description: "One row = one product formula version from source table `inventory_formula_versions`, unique on (formula_versions_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=inventory_formula_versions&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: inventory_formula_versions
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/inventory_formula_versions.sqlx"
    title: "Dataform definition (definitions/validated/derp/inventory_formula_versions.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-09T02:05:00+07:00" }
status: draft
---

# What it is

Validated copy of DERP `inventory_formula_versions`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: BOM header — bom_type: Production | Bundle | Accessory.

# Grain and key

One row per `formula_versions_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

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
| `is_active` | BOOL | สูตรที่ใช้งานอยู่ \| D365: is_active ('Y'/'N' — Mac5 ส่ง 'Yes'/'No' ต้อง normalize ก่อน merge) |
| `valid_from_date` | DATETIME | Source valid from date value. |
| `from_quantity` | FLOAT64 | ขนาด batch ต่ำสุดที่สูตรนี้มีผล (คู่กับ formula_batch_size กำหนดช่วง qty ที่ valid) \| D365: from_quantity |
| `bulk_item_number` | STRING | รหัสสินค้า bulk (ใช้กับสินค้าที่ผลิตแบบ bulk/ถัง) \| D365: bulk_item_number (0/998 ปัจจุบันไม่มีค่า) |
| `catch_weight_size` | FLOAT64 | ขนาด catch weight \| D365: catch_weight_size (0 ทุกแถวในข้อมูลปัจจุบัน) |
| `is_selected_for_designer` | BOOL | เลือกใช้แสดงใน Designer tool หรือไม่ \| D365: is_selected_for_designer |
| `version_name` | STRING | ชื่อ version/สูตร \| D365: version_name |
| `changed_date` | DATETIME | วันที่แก้ไขเนื้อหาสูตรล่าสุด (ต่างจาก updated_at ที่เป็น audit ของระบบ) \| D365: changed_date |
| `formula_batch_size_multiples` | FLOAT64 | batch ต้องเป็นจำนวนเท่าของค่านี้ \| D365: formula_batch_size_multiples |
| `is_co_product_quantity_variation_allowed` | BOOL | อนุญาตให้ co-product แปรผันปริมาณได้หรือไม่ \| D365: is_co_product_quantity_variation_allowed |
| `from_catch_weight_quantity` | FLOAT64 | จำนวน catch weight ต่ำสุด \| D365: from_catch_weight_quantity |
| `yield_percentage` | FLOAT64 | % yield ของการผลิต (ปกติ 100) \| D365: yield_percentage |
| `approver_personnel_number` | STRING | รหัสพนักงานผู้ approve \| D365: approver_personnel_number (684/998, 68.5%) |
| `formula_batch_size` | FLOAT64 | ขนาด batch สูงสุดที่สูตรนี้มีผล \| D365: formula_batch_size |
| `is_approved` | BOOL | ผ่านการ approve แล้ว \| D365: is_approved ('Yes'/'No') |
| `will_cost_calculation_include_version` | BOOL | รวม version นี้ในการคำนวณต้นทุนหรือไม่ \| D365: will_cost_calculation_include_version |
| `valid_to_date` | DATETIME | Source valid to date value. |
| `is_total_cost_allocation_used` | BOOL | ใช้การกระจายต้นทุนรวมหรือไม่ \| D365: is_total_cost_allocation_used |
| `ivzs_bom_accessories` | BOOL | Source ivzs bom accessories value. |
| `remarks` | STRING | หมายเหตุ \| D365: remarks (0/998 ปัจจุบันไม่มีค่า) |
| `created_datetime` | DATETIME | Source created datetime value. |
| `created_by` | STRING | D365: created_by |
| `updated_datetime` | DATETIME | Source updated datetime value. |
| `updated_by` | STRING | D365: updated_by (0/998 ปัจจุบันไม่มีค่า) |
| `product_id` | STRING | D365: product_id |
| `site_id` | STRING | FK → sites.id |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/inventory_formula_versions.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `updated_datetime DESC, created_datetime DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.inventory_formula_versions`
GROUP BY asatdate
ORDER BY asatdate DESC
```
