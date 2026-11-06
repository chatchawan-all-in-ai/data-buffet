---
type: BigQuery View
title: "export_fact_quotation"
description: "One row = one quotation line, exposed for the Pub/Sub export of fact_table.fact_quotation with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_fact_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_fact_quotation
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_fact_quotation.sqlx"
    title: "Dataform definition (view/pub_sub/export_fact_quotation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:47:32+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_table.fact_quotation](/fact/fact_quotation.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-fact_quotation`.

# Grain and key

One row = one quotation line: key `companyID`, `Running`, `StkCode`, `occurrence` (unique); `row_key` is the JSON of that key. `occurrence` is computed as the position of the row among source rows with the same business key, ordered by their data JSON; it appears only inside `row_key`. `companyID`, `Running`, `StkCode` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactQuotationSK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, Running, StkCode. Regenerates every run. |
| `QuotationSK` | INT64 | Surrogate key of [dim_quotation](/dimension/dim_quotation.md) (join `dim_quotation.id = tbook_quodetail.linkid`, same company). |
| `SDate` | DATE | Quotation date from dim_quotation (`SDate`). |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (`stkcode = ProductCode`, company). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`CustomerId = debcode`, company). |
| `Total` | FLOAT64 | Quoted line total: SUM(total). |
| `Quantity` | FLOAT64 | Quoted quantity: SUM(quantity). |
| `Price` | FLOAT64 | Unit price: AVG(price) over the group. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_fact_quotation.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_table.fact_quotation](/fact/fact_quotation.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_fact_quotation`
GROUP BY row_key
HAVING n > 1
```
