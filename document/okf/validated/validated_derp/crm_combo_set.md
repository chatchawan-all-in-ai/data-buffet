---
type: BigQuery Table
title: "crm_combo_set"
description: "One row = one combo-set header from source table `crm_combo_set`, unique on (combo_set_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_combo_set&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_combo_set
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_combo_set.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_combo_set.sqlx)"
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

Validated copy of DERP `crm_combo_set`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Combo set (sales BOM / bundle) header document.

# Grain and key

One row per `combo_set_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `combo_set_id` | STRING | รหัสชุดคอมโบ (UUID v7, สร้างอัตโนมัติ) |
| `code` | STRING | รหัสชุดคอมโบแบบ Business-facing เช่น COMBOSET00001 (unique เมื่อไม่เป็น NULL) |
| `name` | STRING | ชื่อชุดคอมโบ |
| `usage_type` | STRING | ประเภทการใช้งานชุดคอมโบ: 'sale'=ใช้ได้กับการขายทั่วไปตามเขตการขาย, 'customer'=จำกัดเฉพาะลูกค้าที่กำหนด, 'private'=ใช้ภายในองค์กร |
| `start_date` | DATE | วันที่เริ่มมีผลของชุดคอมโบ |
| `end_date` | DATE | วันที่สิ้นสุดผลของชุดคอมโบ (ต้อง >= start_date) |
| `status` | STRING | สถานะชุดคอมโบ: 'active' \| 'inactive' \| 'deleted' (ค่าเริ่มต้น active) |
| `created_by` | STRING | ผู้สร้างรายการ |
| `created_by_name` | STRING | ชื่อผู้สร้างรายการ (Snapshot) |
| `created_at` | DATETIME | วันที่และเวลาที่สร้างรายการ |
| `updated_by` | STRING | ผู้แก้ไขรายการล่าสุด |
| `updated_by_name` | STRING | ชื่อผู้แก้ไขรายการล่าสุด (Snapshot) |
| `updated_at` | DATETIME | วันที่และเวลาที่แก้ไขล่าสุด |
| `deleted_at` | DATETIME | วันที่ลบรายการ (soft delete) |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/crm_combo_set.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `COALESCE(updated_at, created_at) DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_combo_set`
GROUP BY asatdate
ORDER BY asatdate DESC
```
