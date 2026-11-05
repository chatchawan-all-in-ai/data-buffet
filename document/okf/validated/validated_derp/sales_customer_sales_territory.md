---
type: BigQuery Table
title: "sales_customer_sales_territory"
description: "One row = one assignment of a customer to a salesperson or sales territory from source table `sales_customer_sales_territory`, unique on (customer_sales_territory_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=sales_customer_sales_territory&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: sales_customer_sales_territory
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/sales_customer_sales_territory.sqlx"
    title: "Dataform definition (validated/derp/sales_customer_sales_territory.sqlx)"
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

Validated copy of DERP `sales_customer_sales_territory`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Assignments of CRM customers to salespeople and sales organization units (division, section, department, TA area).
No other repo object reads it.

# Grain and key

One row per `customer_sales_territory_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `start_date` | DATE | Date the assignment starts. |
| `end_date` | DATE | Date the assignment ends (NULL = open-ended). |
| `is_primary` | BOOL | Flag marking the customer's primary sales assignment. |
| `is_default` | BOOL | Flag marking the default sales assignment of the customer. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `is_sync` | BOOL | Flag set when the record has been synchronized with the ERP (true for migrated customers, false for records created only in the CRM). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/sales_customer_sales_territory.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.sales_customer_sales_territory](/initial/raw_derp/sales_customer_sales_territory.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `customer_sales_territory_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.sales_customer_sales_territory`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT customer_sales_territory_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.sales_customer_sales_territory`
GROUP BY customer_sales_territory_id
HAVING n > 1
```
