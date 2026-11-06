---
type: BigQuery View
title: "export_dim_payment"
description: "One row = one payment method code of a company, exposed for the Pub/Sub export of dimension_table.dim_payment with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_dim_payment&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_dim_payment
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_dim_payment.sqlx"
    title: "Dataform definition (view/pub_sub/export_dim_payment.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_table.dim_payment](/dimension/dim_payment.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-dim_payment`.

# Grain and key

One row = one payment method code of a company: key `companyID`, `CodeMemo` (unique); `row_key` is the JSON of that key. `companyID` is a column of the source table that is not exported as a data column; it appears only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `CodeMemo` | STRING | Pass-through of mds `CodeMemo`, cleaned with `cleanString` (empty string becomes NULL). Memo code from the sales document that identifies the payment term; the natural key with companyID. |
| `PaymentMethodTH` | STRING | Pass-through of mds `PaymentMethodTH`, cleaned with `cleanString` (empty string becomes NULL). Payment method, Thai. |
| `PaymentType` | STRING | Pass-through of mds `PaymentType`, cleaned with `cleanString` (empty string becomes NULL). Payment term category: `Cash`, `Credit` or `No Memo Code` (the default ฿00฿ row). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_dim_payment.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_table.dim_payment](/dimension/dim_payment.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_dim_payment`
GROUP BY row_key
HAVING n > 1
```
