---
type: BigQuery View
title: "export_view_dim_order"
description: "One row = one order document, exposed for the Pub/Sub export of the AI team sample table dimension_view.view_dim_order with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_order&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_order
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_order.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_order.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_order](/view/dimension_view/view_dim_order.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `view_dim_order` to topic `export-ta-view_dim_order`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one order document: key `OrderSK` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `OrderSK` | INT64 | Stable SK of the order in dim_order (MERGE). |
| `mix_date` | DATE | Document date, `PARSE_DATE('%Y%m%d', CONCAT(mihYear, mihMonth, mihDay))`. |
| `mihRef1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `OrderType` | STRING | Order type derived by `fn_order_type(mihref2)`. |
| `StatusName` | STRING | Thai status name. |
| `OrderStatus` | STRING | Fulfilment status computed in dim_order from PS vs IS quantities per item: 'In Process' if any item partly delivered, else 'On Order' if any item undelivered, else 'Complete'. |
| `CustomerShipTo` | STRING | Ship-to location of the order (customer branch, plot or house). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_order.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_order](/view/dimension_view/view_dim_order.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_view.view_dim_order`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_order`
GROUP BY row_key
HAVING n > 1
```
