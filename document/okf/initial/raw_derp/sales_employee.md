---
type: BigQuery Table
title: "sales_employee"
description: "One row = one employee, a record of source table `sales_employee` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=sales_employee&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: sales_employee
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/sales_employee/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sales_employee` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Sales-side employees of the DERP system (salespeople, managers, credit staff) with employee number, role group and status.

Read by: [validated_derp.sales_employee](/validated/validated_derp/sales_employee.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | UUID of the employee. |
| `employee_no` | STRING | Employee number. |
| `first_name` | STRING | Employee first name. |
| `last_name` | STRING | Employee last name. |
| `nickname` | STRING | Employee nickname. |
| `employee_group` | STRING | Employee role group (e.g. `sale`, `SALE_TA`, `SALE_MANAGER`, `manager`, `BUSINESS_UNIT_MANAGER`, `credit`). |
| `status` | STRING | Employee status (`ACTIVE` or `DELETED`). |
| `remarks` | STRING | Free-text remarks about the employee. |
| `company_code` | STRING | Code of the company the employee belongs to (e.g. `DHITETA`, `TM`). |
| `organization_code` | STRING | Code of the organization the employee belongs to (e.g. `TM`). |
| `user_id` | STRING | UUID of the system user account linked to the employee. |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `position` | STRING | Job position of the employee. |
| `phone_number` | STRING | Employee phone number. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/sales_employee/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.sales_employee`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.sales_employee`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
