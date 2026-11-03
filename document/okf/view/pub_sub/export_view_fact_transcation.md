---
type: BigQuery View
title: "export_view_fact_transcation"
description: "One row = one sales transaction line, exposed for the Pub/Sub export of the AI team sample table fact_view.view_fact_transcation with row_key and row_hash."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-03T00:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), with the columns, names and order of the sample table sent to the AI team, for the whole table. The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `view_fact_transcation` to topic `export-ta-view_fact_transcation`. It is registered in [mart_export_config](/process/mart_export_config.md).

# Grain and key

One row = one sales transaction line: key `companyID`, `milType`, `milVnos`, `milListno` plus `occurrence` (the position of the row among rows with the same key, ordered by their data JSON); `row_key` is the JSON of that key. Rows on 2026-11-02: 2,719,389.

# Schema

| Column | Type | Description |
|---|---|---|
| `milYear` | INT64 | Year of the bill date. |
| `milMonth` | INT64 | Month of the bill date. |
| `milDay` | INT64 | Day of the bill date. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `CustomerSK` | INT64 | SK of `dim_customer` (stable MERGE dim). |
| `CustomerReportInfoSK` | INT64 | SK of `dim_customer_report_info` for the customer-report name on the invoice (whitespace-insensitive match); `-1` (reserved row) when the line has an invoice but the name is not found; NULL when there is no invoice. |
| `ProductSK` | INT64 | SK of `dim_product_master` (stable MERGE dim). |
| `NewProductMktSK` | INT64 | `COALESCE(mds NewProductMktSK, ProductMktSK)`: the marketing product-group SK to report on. |
| `PumpSK` | INT64 | SK of `dim_pump_information` matched on product, `FlagNewProductMKT`, region id and company. |
| `SaleRepSKLast` | INT64 | SK of `dim_sale_representative_last` chosen for the line using the LATEST sale-rep snapshot (matching employee id, channel/dep, customer flag, province, order window by `seq_condition`); historical bills are re-assigned to the latest structure. |
| `ChangeSectionSKLast` | INT64 | Section SK after the change-section rules under the latest structure: Agent/PS customers moved to the new section from `dim_change_district` or a `Dummy999990` section when `ChangeSectionFlag = 'Yes'`; otherwise the same as `SectionSKLast`. |
| `InvoiceSK` | INT64 | SK of `dim_invoice` carried through `fact_invoice`; stable (MERGE dim). NULL for lines without an invoice row. |
| `OrderSK` | INT64 | SK of `dim_order`: `COALESCE(fact_invoice.OrderSK, fact_order.OrderSK)` (invoice's order first). |
| `ChannelSK` | INT64 | SK of `dim_channel`/`view_dim_channel` from the line's department code (`milDep`). |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`). |
| `memoextract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `CompanySK` | INT64 | SK of `dim_company`; filled from the calendar on zero-filled rows. |
| `FactOrderSK` | INT64 | `COALESCE(fact_invoice.FactOrderSK, fact_order.FactOrderSK)`. |
| `FlagSaleExc` | STRING | `Yes` when the line is flagged for exclusion from sales KPI: document cancelled or status 32/33 (`fn_flag_exc`), no linked order (`RefOrder` empty or doc no `0001`/`PRE...`), or matched by a rebate rule (customer, sales, product, text-split, dep) with `salesExc = 'Yes'`; otherwise `No`. |
| `milSum` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milsum_incvat` | FLOAT64 | Net amount including VAT: `milSum + Vat`. |
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milVnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milDisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milUprice` | FLOAT64 | Unit price of the line, excluding VAT; zero on calendar rows without a transaction. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_fact_transcation.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Columns follow the AI team sample table `fact_view.view_fact_transcation`.

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_fact_transcation`
GROUP BY row_key
HAVING n > 1
```
