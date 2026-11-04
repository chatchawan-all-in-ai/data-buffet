---
type: BigQuery View
title: "export_fact_transaction_delivery"
description: "One row = one invoice line that is delivered, exposed for the Pub/Sub export of the AI team sample table fact_table.fact_transaction_delivery with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_fact_transaction_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_fact_transaction_delivery
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_fact_transaction_delivery.sqlx"
    title: "Dataform definition (view/pub_sub/export_fact_transaction_delivery.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `fact_transaction_delivery` to topic `export-ta-fact_transaction_delivery`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one invoice line that is delivered: key `companyID`, `milType`, `milvnos`, `milStk` plus `occurrence` (the position of the row among rows with the same key, ordered by their data JSON); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactTransDeliverySK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, date parts, milType, milvnos, lower(milStk). Regenerates every run. |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) (join on date, type, vnos, customer, company; only milType 'IS'). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (company + case-insensitive product code); NULL if unmatched. |
| `company_id` | STRING | MAC5 company code from curated_mil (same value as companyID). |
| `mix_date` | DATE | Invoice business date (PARSE_DATE of year/month/day); partition column. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain. |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, line net amount in THB. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_fact_transaction_delivery.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `fact_table.fact_transaction_delivery`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_fact_transaction_delivery`
GROUP BY row_key
HAVING n > 1
```
