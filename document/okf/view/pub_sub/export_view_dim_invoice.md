---
type: BigQuery View
title: "export_view_dim_invoice"
description: "One row = one invoice document, exposed for the Pub/Sub export of the AI team sample table dimension_view.view_dim_invoice with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_invoice&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_invoice
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_invoice.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_invoice.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Workflow `datamart-publish` compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `view_dim_invoice` to topic `export-ta-view_dim_invoice`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one invoice document: key `InvoiceSK` (unique); `row_key` is the JSON of that key. Rows on 2026-11-02: 1,686,727.

# Schema

| Column | Type | Description |
|---|---|---|
| `InvoiceSK` | INT64 | Stable SK of the invoice row in dim_invoice (MERGE). |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `mihType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `StatusDesc` | STRING | Status name from MAC5 ar_s (sales document types) or ap_s (purchase types). |
| `mihMec` | STRING | Memo-card code of the document, matching `mec.meccode` (holds the shop or branch name for chain-store customers). |
| `mecdesc` | STRING | Card title, used as the shop or branch name of chain-store customers in invoice reporting. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_invoice.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `dimension_view.view_dim_invoice`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_invoice`
GROUP BY row_key
HAVING n > 1
```
