---
type: BigQuery View
title: "export_view_fact_transcation"
description: "One row = one sales transaction line, exposed for the Pub/Sub export of fact_view.view_fact_transcation with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_fact_transcation&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_fact_transcation
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_fact_transcation.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_fact_transcation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T23:54:24+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-fact_transcation`.

# Grain and key

One row = one sales transaction line: key `companyID`, `milType`, `milVnos`, `milListno`, `occurrence` (unique); `row_key` is the JSON of that key. `occurrence` is computed as the position of the row among source rows with the same business key, ordered by their data JSON; it appears only inside `row_key`. `companyID`, `milListno` are columns of the source table that are not exported as data columns; they appear only inside `row_key`.

# Schema

| Column | Type | Description |
|---|---|---|
| `milYear` | INT64 | Year of the bill date. |
| `milMonth` | INT64 | Month of the bill date. |
| `milDay` | INT64 | Day of the bill date. |
| `milType` | STRING | Document type code (`IS` = invoice, `AS` = debit note, `BS` = credit note, `QS` = sales quotation). |
| `CustomerSK` | INT64 | SK of `dim_customer` (stable MERGE dim). |
| `CustomerReportInfoSK` | INT64 | SK of `dim_customer_report_info` for the customer-report name on the invoice (whitespace-insensitive match); `-1` (reserved row) when the line has an invoice but the name is not found; NULL when there is no invoice. |
| `ProductSK` | INT64 | SK of `dim_product_master` (stable MERGE dim). |
| `NewProductMktSK` | INT64 | `COALESCE(mds NewProductMktSK, ProductMktSK)`: the marketing product-group SK to report on. |
| `PumpSK` | INT64 | SK of `dim_pump_information` matched on product, `FlagNewProductMKT`, region id and company. |
| `SaleRepSKLast` | INT64 | SK of `dim_sale_representative_last` chosen for the line using the LATEST sale-rep snapshot (matching employee id, channel/dep, customer flag, province, order window by `seq_condition`); historical bills are re-assigned to the latest structure. |
| `ChangeSectionSKLast` | INT64 | Passed through from `view_fact_transcation`; see its [ordered section rules](/view/fact_view/view_fact_transcation.md#schema). |
| `InvoiceSK` | INT64 | SK of `dim_invoice` carried through `fact_invoice`; stable (MERGE dim). NULL for lines without an invoice row. |
| `OrderSK` | INT64 | SK of `dim_order`: `COALESCE(fact_invoice.OrderSK, fact_order.OrderSK)` (invoice's order first). |
| `ChannelSK` | INT64 | SK of `dim_channel`/`view_dim_channel` from the line's department code (`milDep`). |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`). |
| `memoextract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `CompanySK` | INT64 | SK of `dim_company`; filled from the calendar on zero-filled rows. |
| `FactOrderSK` | INT64 | `COALESCE(fact_invoice.FactOrderSK, fact_order.FactOrderSK)`. |
| `FlagSaleExc` | STRING | Passed through from `view_fact_transcation`; see its [exclusion rules and calendar-row NULL behavior](/view/fact_view/view_fact_transcation.md#schema). |
| `milSum` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milsum_incvat` | FLOAT64 | Net amount including VAT: `milSum + Vat`. |
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milVnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milDisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milUprice` | FLOAT64 | Unit price of the line, excluding VAT; zero on calendar rows without a transaction. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_fact_transcation.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_fact_transcation`
GROUP BY row_key
HAVING n > 1
```
