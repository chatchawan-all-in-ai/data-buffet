---
type: BigQuery Table
title: "sales_employee"
description: "One row = one employee from source table `sales_employee`, unique on (employee_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=sales_employee&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: sales_employee
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/sales_employee.sqlx"
    title: "Dataform definition (validated/derp/sales_employee.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of DERP `sales_employee`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Sales-side employees of the DERP system (salespeople, managers, credit staff) with employee number, role group and status.
No other repo object reads it.

# Grain and key

One row per `employee_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `position` | STRING | Job position of the employee. |
| `phone_number` | STRING | Employee phone number. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/sales_employee.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.sales_employee](/initial/raw_derp/sales_employee.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `employee_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.sales_employee`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT employee_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.sales_employee`
GROUP BY employee_id
HAVING n > 1
```
