---
type: BigQuery Table
title: "sales_employee_sale_territory"
description: "One row = one assignment of an employee to a sales territory from source table `sales_employee_sale_territory`, unique on (employee_sale_territory_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=sales_employee_sale_territory&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: sales_employee_sale_territory
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/sales_employee_sale_territory.sqlx"
    title: "Dataform definition (validated/derp/sales_employee_sale_territory.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of DERP `sales_employee_sale_territory`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Assignments of sales employees to sales territories, with primary flag and validity dates.
No other table or view in this repository reads it.

# Grain and key

One row per `employee_sale_territory_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_sale_territory_id` | STRING | UUID of the employee-to-sales-territory assignment. |
| `employee_id` | STRING | UUID of the employee in `sales_employee`. |
| `employee_no` | STRING | Employee number. |
| `sale_territory_id` | STRING | UUID of the sales territory in `sales_sales_territory`. |
| `start_date` | DATETIME | Timestamp the assignment starts. |
| `end_date` | DATE | Date the assignment ends (NULL = open-ended). |
| `alternate_level` | INT64 | Assignment level of the employee in the territory (1 = main, 2 = alternate). |
| `is_primary` | BOOL | Flag marking the employee's primary territory. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/sales_employee_sale_territory.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.sales_employee_sale_territory](/initial/raw_derp/sales_employee_sale_territory.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `employee_sale_territory_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.sales_employee_sale_territory`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT employee_sale_territory_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.sales_employee_sale_territory`
GROUP BY employee_sale_territory_id
HAVING n > 1
```
