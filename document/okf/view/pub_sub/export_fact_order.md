---
type: BigQuery View
title: "export_fact_order"
description: "One row = one order line, exposed for the Pub/Sub export of fact_table.fact_order with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_fact_order&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_fact_order
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_fact_order.sqlx"
    title: "Dataform definition (view/pub_sub/export_fact_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:47:32+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_table.fact_order](/fact/fact_order.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-fact_order`.

# Grain and key

One row = one order line: key `companyID`, `milType`, `milvnos`, `milStk`, `occurrence` (unique); `row_key` is the JSON of that key. `occurrence` is computed as the position of the row among source rows with the same business key, ordered by their data JSON; it appears only inside `row_key`. `companyID`, `milType`, `milvnos`, `milStk` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactOrderSk` | INT64 | Stable row key of [fact_order](/fact/fact_order.md#grain-and-key), passed through unchanged. |
| `OrderSK` | INT64 | Surrogate key of [dim_order](/dimension/dim_order.md) (join on date, type, vnos, customer, company). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md), joined on company and `lower(milStk) = lower(ProductCode)`; NULL if unmatched. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`milCus = debcode`, same CompanySK). |
| `FactQuotationSK` | INT64 | [fact_quotation](/fact/fact_quotation.md).FactQuotationSK of the matching quotation line (join `mihRef1 = Running`, `milStk = StkCode`, CompanySK). |
| `milSum` | FLOAT64 | SUM of `curated_mil.milSum`, the line net amount in THB; the salesperson share is already applied on split-sale lines. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_fact_order.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_table.fact_order](/fact/fact_order.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_fact_order`
GROUP BY row_key
HAVING n > 1
```
