---
type: BigQuery View
title: "export_dim_quotation"
description: "One row = one quotation, exposed for the Pub/Sub export of the AI team sample table dimension_table.dim_quotation with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_quotation
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_quotation.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_quotation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_quotation](/dimension/dim_quotation.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `dim_quotation` to topic `export-ta-dim_quotation`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one quotation: key `QuotationSK` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `QuotationSK` | INT64 | Stable surrogate key; never regenerated, stored in [fact_quotation](/fact/fact_quotation.md). |
| `Running` | STRING | Quotation number referenced by orders, with missing source numbers represented as an empty string. |
| `ProjectSK` | INT64 | Project SK from [dim_project](/dimension/dim_project.md), joined on parsed `ProjectCode` and `CompanySK`; NULL when no project code was parsed or found. |
| `OrderStatus` | STRING | Fulfilment status: per quoted item 'On Order' (no PS order line with `mihRef1 = Running`), 'Complete' (ordered quantity and amount >= quoted), else 'In Process'; per quotation any 'In Process' wins, then 'On Order', else 'Complete'. NULL when the quotation has no detail lines. |
| `Project` | STRING | Project text of the quotation, including a project or customer code before a backslash when supplied. |
| `PriceValidity` | STRING | Price validity text. |
| `TermPayment` | STRING | Payment terms text (e.g. credit 30 days). |
| `Atten` | STRING | Attention or contact text of the quotation, including a customer code before a backslash when supplied. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_quotation.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_quotation](/dimension/dim_quotation.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_table.dim_quotation`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_quotation`
GROUP BY row_key
HAVING n > 1
```
