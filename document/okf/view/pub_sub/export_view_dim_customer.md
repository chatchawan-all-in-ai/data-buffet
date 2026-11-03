---
type: BigQuery View
title: "export_view_dim_customer"
description: "One row = one customer, exposed for the Pub/Sub export of the AI team sample table dimension_view.view_dim_customer with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_customer&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_customer
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_customer.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_customer.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `view_dim_customer` to topic `export-ta-view_dim_customer`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one customer: key `CustomerSK` (unique); `row_key` is the JSON of that key. Rows on 2026-11-02: 98,339.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerSK` | INT64 | Stable SK of the customer in dim_customer. |
| `companyID` | STRING | MAC5 company code. |
| `debcode` | STRING | Customer (debtor) code. |
| `debnamet` | STRING | Customer name in Thai. |
| `NicknameCustomer` | STRING | MDS customer nickname if one exists, else `debnamet`. |
| `customer_status_name` | STRING | Customer status name in Thai. |
| `debbranch` | STRING | Tax branch number of the customer (`00000` = head office). |
| `District` | STRING | Thai district name of the invoice address (`dim_districts.name_th`). |
| `DEBcreditTerm` | INT64 | Credit term in days. |
| `debgrade` | STRING | Customer grade code. |
| `customer_type_name` | STRING | Customer type name in Thai. |
| `customer_type_name_en` | STRING | Customer type name in English. |
| `debgroup` | STRING | Customer group code (e.g. HP, TW, BT, GB, MH, DOHOME); drives channel matching in the sale-rep rules. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_customer.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_view.view_dim_customer`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_customer`
GROUP BY row_key
HAVING n > 1
```
