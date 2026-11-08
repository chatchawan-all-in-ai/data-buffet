---
type: BigQuery Table
title: "crm_master_payment_condition"
description: "One row = one payment condition from source table `crm_master_payment_condition`, unique on (master_payment_condition_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_master_payment_condition&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_master_payment_condition
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_master_payment_condition.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_master_payment_condition.sqlx)"
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

Validated copy of DERP `crm_master_payment_condition`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Payment condition (mixed pattern): 30% deposit / 100% cash, etc.

# Grain and key

One row per `master_payment_condition_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `master_payment_condition_id` | STRING | รหัสอ้างอิงหลัก |
| `payment_condition_code` | STRING | รหัสเงื่อนไข \| เช่น CASH_30_BFR_70_ON / TRF_30_BFR_TRF_70_ON |
| `payment_condition_name` | STRING | ชื่อเงื่อนไข \| เช่น เก็บเงินสด (มัดจำ) 30% ก่อนส่ง \| ส่วนที่เหลือ 70% ณ วันส่ง |
| `description` | STRING | คำอธิบายย่อ \| เช่น มัดจำเงินสด 30% ก่อนส่ง, เหลือ 70% ณ วันส่ง |
| `order_sort` | INT64 | ลำดับการแสดงผล |
| `company_code` | STRING | รหัสบริษัท (NULL = ใช้ร่วมทุกบริษัท) |
| `organization_code` | STRING | รหัสหน่วยงาน (NULL = ใช้ร่วมทุกหน่วยงาน) |
| `status` | STRING | สถานะ: ACTIVE / INACTIVE |
| `created_at` | DATETIME | วันที่และเวลาที่สร้างข้อมูล |
| `updated_at` | DATETIME | วันที่และเวลาที่แก้ไขข้อมูลล่าสุด |
| `created_by_name` | STRING | ชื่อผู้สร้าง (denormalized) |
| `updated_by_name` | STRING | ชื่อผู้แก้ไข (denormalized) |
| `created_by` | STRING | ผู้สร้างข้อมูล |
| `updated_by` | STRING | ผู้แก้ไขข้อมูลล่าสุด |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/crm_master_payment_condition.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `COALESCE(updated_at, created_at) DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_master_payment_condition`
GROUP BY asatdate
ORDER BY asatdate DESC
```
