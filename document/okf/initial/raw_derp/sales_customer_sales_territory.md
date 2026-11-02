---
type: BigQuery Table
title: "sales_customer_sales_territory"
description: "One row = one assignment of a customer to a salesperson or sales territory, a record of source table `sales_customer_sales_territory` (DERP) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_derp&t=sales_customer_sales_territory&page=table"
project_id: databuffet-nonprd
dataset_id: raw_derp
table_id: sales_customer_sales_territory
tags: ["initial", "raw_derp", "derp"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/derp/create_all_table_raw_derp.sqlx"
    title: "Dataform definition (initial/derp/create_all_table_raw_derp.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/derp_temp/sales_customer_sales_territory/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `sales_customer_sales_territory` table from DERP; nothing is cleaned or deduplicated here. Table meaning: Assignments of CRM customers to salespeople and sales organization units (division, section, department, TA area). Used by: [validated_derp.sales_customer_sales_territory](/validated/validated_derp/sales_customer_sales_territory.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `customer_sales_territory_id` | STRING | UUID of the customer-to-sales-territory assignment. |
| `customer_master_id` | STRING | UUID of the customer in `crm_customer_master`. |
| `customer_code` | STRING | Customer code in the CRM (e.g. `C0000136`; `NCT...` for new customers). |
| `department_id` | STRING | UUID of the sales department of the assignment. |
| `department_code` | STRING | Code of the sales department of the assignment. |
| `department_name` | STRING | Name of the sales department of the assignment. |
| `section_id` | STRING | UUID of the sales section of the assignment. |
| `section_code` | STRING | Code of the sales section of the assignment. |
| `section_name` | STRING | Name of the sales section of the assignment. |
| `division_id` | STRING | UUID of the sales division of the assignment. |
| `division_code` | STRING | Code of the sales division of the assignment. |
| `division_name` | STRING | Name of the sales division of the assignment. |
| `ta_area_id` | STRING | UUID of the TA (territory) area of the assignment. |
| `ta_area_code` | STRING | Code of the TA (territory) area of the assignment. |
| `ta_area_name` | STRING | Name of the TA (territory) area of the assignment. |
| `path_id` | STRING | Chain of territory UUIDs from the top level down to the assigned territory. |
| `path_code` | STRING | Chain of territory codes from the top level down to the assigned territory. |
| `path_name` | STRING | Chain of territory names from the top level down to the assigned territory. |
| `sale_id` | STRING | UUID of the salesperson (employee) assigned to the customer. |
| `sale_no` | STRING | Employee number of the assigned salesperson. |
| `sale_first_name` | STRING | First name of the assigned salesperson. |
| `sale_last_name` | STRING | Last name of the assigned salesperson. |
| `sale_nickname` | STRING | Nickname of the assigned salesperson. |
| `start_date` | STRING | Date the assignment starts. |
| `end_date` | STRING | Date the assignment ends (NULL = open-ended). |
| `is_primary` | BOOL | Flag marking the customer's primary sales assignment. |
| `is_default` | BOOL | Flag marking the default sales assignment of the customer. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_at` | STRING | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | STRING | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_derp` (`definitions/initial/derp/create_all_table_raw_derp.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/derp_temp/sales_customer_sales_territory/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_derp.sales_customer_sales_territory`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_derp.sales_customer_sales_territory`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
