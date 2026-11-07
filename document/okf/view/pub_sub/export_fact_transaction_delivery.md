---
type: BigQuery View
title: "export_fact_transaction_delivery"
description: "One row = one invoice line that is delivered, exposed for the Pub/Sub export of fact_table.fact_transaction_delivery with row_key and row_hash."
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
generated: { by: "agent:codex", at: "2026-11-07T07:42:49+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-fact_transaction_delivery`.

# Grain and key

One row = one invoice line that is delivered: key `companyID`, `milType`, `milvnos`, `milStk`, `occurrence` (unique); `row_key` is the JSON of that key. `occurrence` is computed as the position of the row among source rows with the same business key, ordered by their data JSON; it appears only inside `row_key`. `companyID`, `milType`, `milStk` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactTransDeliverySK` | INT64 | Row key of [fact_transaction_delivery](/fact/fact_transaction_delivery.md#schema). |
| `InvoiceSK` | INT64 | Surrogate key of [dim_invoice](/dimension/dim_invoice.md) (join on date, type, vnos, customer, company; only milType 'IS'). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (company + case-insensitive product code); NULL if unmatched. |
| `company_id` | STRING | MAC5 company code from curated_mil (same value as companyID). |
| `mix_date` | DATE | Invoice business date (PARSE_DATE of year/month/day); partition column. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milQuan` | FLOAT64 | SUM of `curated_mil.milQuan` over the grain; the salesperson share is already applied on split-sale lines. |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, line net amount in THB; the salesperson share is already applied on split-sale lines. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_fact_transaction_delivery.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_fact_transaction_delivery`
GROUP BY row_key
HAVING n > 1
```
