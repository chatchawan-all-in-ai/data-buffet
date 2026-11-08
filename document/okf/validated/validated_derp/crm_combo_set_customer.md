---
type: BigQuery Table
title: "crm_combo_set_customer"
description: "One row = one customer entitlement for a combo set from source table `crm_combo_set_customer`, unique on (combo_set_customer_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_combo_set_customer&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_combo_set_customer
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_combo_set_customer.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_combo_set_customer.sqlx)"
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

Validated copy of DERP `crm_combo_set_customer`: every source field is cleaned or cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Customers entitled to use the combo set (usage_type = customer).

# Grain and key

One row per `combo_set_customer_id`. The key is declared in `uniqueKey` and `pk_key` and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `combo_set_customer_id` | STRING | รหัสรายการลูกค้าที่ผูกกับชุดคอมโบ |
| `combo_set_id` | STRING | รหัสชุดคอมโบที่อ้างอิง |
| `customer_id` | STRING | รหัสลูกค้าที่ได้รับสิทธิ์ใช้ชุดคอมโบนี้ |
| `customer_code` | STRING | รหัสลูกค้า (Snapshot) |
| `customer_name` | STRING | ชื่อลูกค้า (Snapshot) |
| `created_by` | STRING | ผู้สร้างรายการ |
| `created_at` | DATETIME | วันที่และเวลาที่สร้างรายการ |
| `updated_by` | STRING | ผู้แก้ไขรายการล่าสุด |
| `updated_at` | DATETIME | วันที่และเวลาที่แก้ไขล่าสุด |
| `asatdate` | DATE | Extract date (`YYYY-MM-DD`), parsed from raw `ASATDATE` (`YYYYMMDD`); used for table partitioning. |

# How it is built

- Built by `definitions/validated/derp/crm_combo_set_customer.sqlx` as an incremental table partitioned on `asatdate` and clustered by the primary key.
- Reads the matching raw table, cleans or casts every source field, filters incremental runs to the configured backfill window, and keeps one row per key ordered by `COALESCE(updated_at, created_at) DESC, asatdate DESC`.
- The primary key is added as `NOT ENFORCED` after full builds.

# Examples

Latest extract dates:

```sql
SELECT asatdate, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_combo_set_customer`
GROUP BY asatdate
ORDER BY asatdate DESC
```
