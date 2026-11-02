---
type: BigQuery Table
title: "crm_sale_order_sales_person"
description: "One row = one salesperson assigned to a sale order from source table `crm_sale_order_sales_person`, unique on (sale_order_sales_person_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_sales_person&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_sales_person
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_sales_person.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_sales_person.sqlx)"
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

Validated copy of DERP `crm_sale_order_sales_person`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Salespeople credited on DERP sale orders with their sales and commission shares.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_sales_person_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_sales_person_id` | STRING | Unique identifier of the salesperson assignment. |
| `sale_order_id` | STRING | Identifier of the parent sale order (`crm_sale_order.sale_order_id`). |
| `so_no` | STRING | Sale order number of the parent sale order (e.g. `A2610000106`). |
| `so_date` | DATETIME | Date and time of the parent sale order. |
| `sales_seq` | INT64 | Sequence number of the salesperson on the order, starting at 1. |
| `sales_id` | STRING | Identifier of the salesperson. |
| `sales_code` | STRING | Employee code of the salesperson. |
| `sales_name` | STRING | Name of the salesperson. |
| `sales_amount` | FLOAT64 | Sales amount credited to the salesperson (THB). |
| `sales_amount_pct` | FLOAT64 | Share of the order sales amount credited to the salesperson, in percent. |
| `commission_pct` | FLOAT64 | Share of the commission paid to the salesperson, in percent. |
| `order_sort` | INT64 | Display order of the salesperson within its sale order, starting at 0. |
| `path_id` | STRING | Identifier of the sales channel path of the salesperson. |
| `path_code` | STRING | Code of the sales channel path of the salesperson. |
| `status` | STRING | Status of the salesperson assignment. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_sales_person.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_sales_person](/initial/raw_derp/crm_sale_order_sales_person.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_sales_person_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,651 rows, 930.8 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_sales_person`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_sales_person_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_sales_person`
GROUP BY sale_order_sales_person_id
HAVING n > 1
```
