---
type: BigQuery Table
title: "crm_quotation_sale"
description: "One row = one salesperson on a quotation from source table `crm_quotation_sale`, unique on (quotation_sale_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_quotation_sale&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_quotation_sale
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_quotation_sale.sqlx"
    title: "Dataform definition (validated/derp/crm_quotation_sale.sqlx)"
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

Validated copy of DERP `crm_quotation_sale`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Salespeople credited on each quotation with their share of the sales amount and commission rate.
No other table or view in this repository reads it.

# Grain and key

One row per `quotation_sale_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_sale_id` | STRING | UUID of the quotation salesperson record. |
| `quotation_id` | STRING | UUID of the quotation in `crm_quotation`. |
| `quotation_no` | STRING | Quotation document number (e.g. `QT2607...` or `MDT2610...`). |
| `quotation_date` | DATE | Quotation document date. |
| `sales_seq` | INT64 | Sequence number of the salesperson on the quotation (1 = first). |
| `sales_id` | STRING | UUID of the salesperson (employee) record. |
| `sales_code` | STRING | Employee number of the salesperson. |
| `sales_name` | STRING | Name of the salesperson. |
| `sales_amount` | FLOAT64 | Sales amount credited to the salesperson, in THB. |
| `sales_amount_pct` | FLOAT64 | Share of the quotation amount credited to the salesperson, in percent. |
| `commission_pct` | FLOAT64 | Commission rate of the salesperson, in percent. |
| `order_sort` | INT64 | Display order of the row within its parent record. |
| `path_id` | STRING | Chain of sales-territory UUIDs of the salesperson. |
| `path_code` | STRING | Chain of sales-territory codes of the salesperson. |
| `path_name` | STRING | Chain of sales-territory names of the salesperson. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_quotation_sale.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_quotation_sale](/initial/raw_derp/crm_quotation_sale.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `quotation_sale_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_quotation_sale`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT quotation_sale_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_quotation_sale`
GROUP BY quotation_sale_id
HAVING n > 1
```
