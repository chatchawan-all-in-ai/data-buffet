---
type: BigQuery Table
title: "inventory_formula_line"
description: "One row = one line of a production formula from source table `inventory_formula_line`, unique on (formula_line_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=inventory_formula_line&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: inventory_formula_line
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/inventory_formula_line.sqlx"
    title: "Dataform definition (definitions/validated/derp/inventory_formula_line.sqlx)"
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

Validated copy of DERP `inventory_formula_line`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: BOM component line items — shared across all bom_type.

# Grain and key

One row per `formula_line_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `formula_line_id` | STRING | Source formula line id value. |
| `id` | STRING | Source row identifier. |
| `formula_id` | STRING | D365: formula_id ⚠ พบ 1 formula_id ('15420601_V1') ใน formula_line ที่ไม่มีอยู่ใน formula_versions ในข้อมูลปัจจุบัน (orphan child) — ต้องมี data quality check ก่อน load |
| `line_creation_sequence_number` | FLOAT64 | ลำดับการสร้าง line (ต่างจาก line_number ที่เป็นลำดับแสดงผล) \| D365: line_creation_sequence_number |
| `product_configuration_id` | STRING | Variant dimension ของ component — configuration \| D365: product_configuration_id (3/4,733) |
| `substitution_priority` | FLOAT64 | ลำดับความสำคัญของวัตถุดิบทดแทนภายในกลุ่ม \| D365: substitution_priority |
| `position_number` | STRING | รหัส operation/position ในสายผลิตที่ใช้ component นี้ \| D365: position_number (1,791/4,733, 37.8%) |
| `consumption_calculation_method` | STRING | วิธีคำนวณการเบิกใช้ \| D365: consumption_calculation_method (พบค่า 'Formula0' ทุกแถวในข้อมูลปัจจุบัน) |
| `is_consumed_at_operation_complete` | BOOL | เบิกเมื่อ operation เสร็จหรือไม่ \| D365: is_consumed_at_operation_complete |
| `line_number` | FLOAT64 | ลำดับ line ใน BOM (มีค่าทศนิยมได้ เช่น 3.5 สำหรับ insert line) \| D365: line_number |
| `consumption_calculation_constant` | FLOAT64 | ค่าคงที่ในการคำนวณเบิกใช้ \| D365: consumption_calculation_constant |
| `product_size_id` | STRING | Variant dimension — ขนาด \| D365: product_size_id (141/4,733) |
| `item_number` | STRING | D365: item_number |
| `product_version_id` | STRING | Variant dimension — version \| D365: product_version_id (0/4,733 ปัจจุบันไม่มีค่า) |
| `consumption_warehouse_id` | STRING | คลังที่เบิกวัตถุดิบ \| D365: consumption_warehouse_id (4,140/4,733, 87.4%) |
| `valid_from_date` | DATETIME | Source valid from date value. |
| `consumption_site_id` | STRING | Site ที่เบิกวัตถุดิบ \| D365: consumption_site_id |
| `will_cost_calculation_include_line` | BOOL | รวม line นี้ในการคำนวณต้นทุนหรือไม่ \| D365: will_cost_calculation_include_line |
| `sub_bom_id` | STRING | รหัส sub-BOM (ใช้กับ line_type='Phantom') \| D365: sub_bom_id |
| `is_resource_consumption_used` | BOOL | ใช้ resource consumption หรือไม่ \| D365: is_resource_consumption_used |
| `will_manufactured_item_inherit_batch_attributes` | BOOL | สินค้าที่ผลิตรับ batch attribute จาก component นี้หรือไม่ \| D365: will_manufactured_item_inherit_batch_attributes |
| `product_unit_symbol` | STRING | Source product unit symbol value. |
| `substitution_group_id` | STRING | กลุ่มวัตถุดิบที่ใช้แทนกันได้ \| D365: substitution_group_id (256/4,733, 5.4%) |
| `line_type` | STRING | 'Item' = วัตถุดิบ/สินค้าปกติ 'Phantom' = sub-assembly (ไม่มี stock เอง ใช้แทนชุดประกอบ) 'Bundle' = สินค้าชุด (เฉพาะ bom_type=Bundle) D365: line_type (Item 4,543 / Phantom 190 ในข้อมูลปัจจุบัน) |
| `quantity_rounding_up_multiples` | FLOAT64 | ปัดเบิกขึ้นเป็นจำนวนเท่าของค่านี้ \| D365: quantity_rounding_up_multiples |
| `physical_product_depth` | FLOAT64 | ความลึก override เฉพาะ line \| D365: physical_product_depth (0 ทุกแถวในข้อมูลปัจจุบัน) |
| `physical_product_height` | FLOAT64 | ความสูง override เฉพาะ line \| D365: physical_product_height (0 ทุกแถว) |
| `variable_scrap_percentage` | FLOAT64 | % ของเสียแบบผันแปรตามปริมาณ \| D365: variable_scrap_percentage |
| `physical_product_density` | FLOAT64 | ความหนาแน่น override เฉพาะ line \| D365: physical_product_density (0 ทุกแถว) |
| `valid_to_date` | DATETIME | Source valid to date value. |
| `rounding_up_method` | STRING | วิธีปัดเศษ \| D365: rounding_up_method |
| `consumption_type` | STRING | 'Variable'=ตามสูตร \| 'Fixed'=คงที่ \| D365: consumption_type |
| `will_manufactured_item_inherit_shelf_life_dates` | BOOL | สินค้าที่ผลิตรับวันที่ shelf life จาก component นี้หรือไม่ \| D365: will_manufactured_item_inherit_shelf_life_dates |
| `formula_quantity_percentage` | FLOAT64 | % ของสูตรที่ component นี้คิดเป็น (ใช้เมื่อ is_percentage_controlled=true) \| D365: formula_quantity_percentage |
| `warehouse_bom_release_reservation_requirement_rule` | STRING | กฎการจอง stock เมื่อ release BOM \| D365: warehouse_bom_release_reservation_requirement_rule |
| `material_overpick_percentage` | FLOAT64 | % เบิกเกินที่อนุญาต \| D365: material_overpick_percentage |
| `flushing_principle` | STRING | เวลาเบิกวัตถุดิบ: 'Start' = เบิกตอนเริ่มผลิต 'Finish' = เบิกตอนผลิตเสร็จ 'Manual' = เบิกเอง D365: flushing_principle (Start 3,867 / Finish 581 / Manual 256 / Blank 29) |
| `quantity_denominator` | FLOAT64 | ตัวหารปริมาณ (คู่กับ quantity เพื่อคำนวณอัตราส่วนจริง) \| D365: quantity_denominator |
| `vendor_account_number` | STRING | รหัส vendor สำหรับ vendor-specific substitution \| D365: vendor_account_number (0/4,733 ปัจจุบันไม่มีค่า) |
| `is_percentage_controlled` | BOOL | คุมปริมาณด้วย % ของสูตรหรือ qty ตรง ๆ \| D365: is_percentage_controlled |
| `product_color_id` | STRING | Variant dimension — สี \| D365: product_color_id (3/4,733) |
| `catch_weight_quantity` | FLOAT64 | จำนวน catch weight ระดับ line \| D365: catch_weight_quantity (0 ทุกแถวในข้อมูลปัจจุบัน) |
| `physical_product_width` | FLOAT64 | ความกว้าง override เฉพาะ line \| D365: physical_product_width (0 ทุกแถว) |
| `is_scalable` | BOOL | ปริมาณ scale ตาม batch size หรือไม่ \| D365: is_scalable |
| `route_operation_number` | FLOAT64 | เลข operation บน route ที่เชื่อมกับ line นี้ \| D365: route_operation_number |
| `constant_scrap_quantity` | FLOAT64 | ของเสียคงที่ต่อ batch (ไม่ผันแปรตามปริมาณ) \| D365: constant_scrap_quantity |
| `product_style_id` | STRING | Variant dimension — สไตล์ \| D365: product_style_id (3/4,733) |
| `quantity` | FLOAT64 | จำนวนที่ใช้ต่อ batch \| D365: quantity |
| `sub_route_id` | STRING | Route ย่อยที่เชื่อมกับ line นี้ \| D365: sub_route_id |
| `ivzs_bom_accessories` | BOOL | Source ivzs bom accessories value. |
| `qms_allow_over_dispensing` | BOOL | อนุญาตเบิกเกินใน QMS หรือไม่ \| D365: qms_allow_over_dispensing |
| `qms_under_dispense_percentage` | FLOAT64 | % เบิกขาดที่ยอมรับได้ \| D365: qms_under_dispense_percentage |
| `qms_over_dispense_percentage` | FLOAT64 | % เบิกเกินที่ยอมรับได้ \| D365: qms_over_dispense_percentage |
| `is_active` | BOOL | D365: is_active ('Y'/'N' — Mac5 ส่ง 'Yes'/'No' ต้อง normalize ก่อน merge) |
| `remarks` | STRING | หมายเหตุ \| D365: remarks (0/4,733 ปัจจุบันไม่มีค่า) |
| `created_datetime` | DATETIME | Source created datetime value. |
| `created_by` | STRING | D365: created_by — ⚠ เป็นชื่อ service account เช่น 'Service' ไม่ใช่ uuid (แก้ type จาก V1) |
| `updated_datetime` | DATETIME | Source updated datetime value. |
| `updated_by` | STRING | D365: updated_by (0/4,733 ปัจจุบันไม่มีค่า) |
| `product_id` | STRING | D365: product_id ⚠ D365 ส่งค่ามาจริงเพียง 24/4,733 แถว (0.5%) ต้อง resolve ผ่าน item_number join กับ products แทน |
| `formula_versions_id` | STRING | FK → formula_versions.formula_versions_id ⚠ ไม่มีอยู่ใน formula_line_d365.xlsx (raw export) — มีเฉพาะใน .sql (target DB) ต้อง resolve ผ่าน join formula_id → formula_versions |
| `site_id` | STRING | FK → sites.id ⚠ ไม่มีอยู่ใน formula_line_d365.xlsx (raw export) — มีเฉพาะใน .sql (target DB) ต้อง derive จาก consumption_site_id ผ่าน lookup |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/inventory_formula_line.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `updated_datetime DESC, created_datetime DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.inventory_formula_line`
GROUP BY asatdate
ORDER BY asatdate DESC
```
