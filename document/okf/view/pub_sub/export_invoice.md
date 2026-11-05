---
type: BigQuery View
title: "export_invoice"
description: "One row = one line of an ag01 invoice (IS) of 2026, not cancelled; commission set `invoice` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_invoice&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_invoice
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_invoice.sqlx"
    title: "Dataform definition (view/pub_sub/export_invoice.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-05T16:48:25+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `invoice` for the TF team (company ag01): one line of an ag01 invoice (IS) of 2026, not cancelled. Its columns, names, order and JSON types are those of the commission sample sent to TF (`commission_tf_ag01_2026`). The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `invoice` to topic `export-commission-invoice`. It is registered in [mart_export_config](/process/mart_export_config.md). First-load files are split into date folders by `Invoice_Date` (`snapshot_date` in the export config).

# Grain and key

One row = one line of an ag01 invoice (IS) of 2026, not cancelled: key `company_source_id`, `Invoice_No`, `No` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of validated_mac5.mih (document header). Part of the natural key. |
| `No` | INT64 | From `millistno` of validated_mac5.mil (document line). Part of the natural key. |
| `Invoice_Date` | STRING | Computed: `FORMAT('%02d/%02d/%d', m.mihday, m.mihmonth, m.mihyear)`. |
| `Invoice_No` | STRING | From `mihvnos` of validated_mac5.mih (document header). Part of the natural key. |
| `Order_id` | STRING | Constant '' (as in the sample). |
| `Order_No` | STRING | From `millinkvcno` of validated_mac5.mil (document line). |
| `Condition_payment_id` | STRING | Always NULL (as in the sample). |
| `Credit_startDate` | STRING | Computed: `FORMAT('%02d/%02d/%d', m.mihday, m.mihmonth, m.mihyear)`. |
| `CreditTerm` | STRING | Computed: `REPLACE(SUBSTR(mie.miectermcx, 1, 4), '\|', '')`. |
| `Chq_No` | STRING | Constant '' (as in the sample). |
| `Chq_statusN` | STRING | Constant '' (as in the sample). |
| `Payment_Date` | STRING | Constant '' (as in the sample). |
| `Payment_Amt` | STRING | Constant '' (as in the sample). |
| `BankAccount` | STRING | Constant '' (as in the sample). |
| `companyid` | STRING | From `mihcus` of validated_mac5.mih (document header). |
| `statusid` | INT64 | From `mihstatus` of validated_mac5.mih (document header). |
| `Sell_id` | STRING | From `mihper` of validated_mac5.mih (document header). |
| `stk` | STRING | From `milstk` of validated_mac5.mil (document line). |
| `mildesc` | STRING | From `mildesc` of validated_mac5.mil (document line). |
| `Product_Barcode` | STRING | From `stkcode885` of validated_mac5.stk (product). |
| `Unit` | FLOAT64 | From `milquan` of validated_mac5.mil (document line). |
| `Unit_Price` | FLOAT64 | Computed: `ROUND(l.milcog / NULLIF(l.milquan, 0), 2)`. |
| `TotalPriceAmt` | FLOAT64 | From `milcog` of validated_mac5.mil (document line). |
| `Deposit_Amt` | FLOAT64 | Computed: `CASE WHEN l.milstk = 'บ-0027' THEN l.milsum ELSE 0 END`. |
| `Discount_Type` | STRING | Constant 'baht' (as in the sample). |
| `DiscountAmt` | FLOAT64 | Computed: `ROUND(l.mildisca / NULLIF(l.milquan, 0), 2)`. |
| `TotalAmt` | FLOAT64 | From `milsum` of validated_mac5.mil (document line). |
| `Discount1_Type` | STRING | Constant 'baht' (as in the sample). |
| `Discount1Amt` | FLOAT64 | Computed: `CASE WHEN m.mihdischf1 > 0 THEN ROUND(((l.milsum / NULLIF(l.milquan, 0)) / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1, 2) ELSE 0 END`. |
| `Total1Amt` | FLOAT64 | Computed: `CASE WHEN m.mihdischf1 > 0 THEN ROUND(l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1), 2) ELSE l.milsum END`. |
| `Discount2_Type` | STRING | Constant 'baht' (as in the sample). |
| `Discount2Amt` | FLOAT64 | Computed: `CASE WHEN m.mihdischf2 > 0 THEN ROUND((((l.milsum / NULLIF(l.milquan, 0)) - (((l.milsum / NULLIF(l.milquan, 0)) / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1)) / NULLIF(m.mihnetsum - m.mihvatsum - m.mihdischf1 + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf2, 2) ELSE 0 END`. |
| `Total2Amt` | FLOAT64 | Computed: `CASE WHEN m.mihdischf2 > 0 THEN ROUND(l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1) - (((l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1)) / NULLIF(m.mihnetsum - m.mihvatsum - m.mihdischf1 + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf2), 2) WHEN m.mihdischf1 > 0 THEN ROUND(l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1), 2) ELSE l.milsum END`. |
| `TotalDisAmt` | STRING | Constant '' (as in the sample). |
| `PriceExvat` | FLOAT64 | Computed: `CASE WHEN m.mihdischf2 > 0 THEN ROUND(l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1) - (((l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1)) / NULLIF(m.mihnetsum - m.mihvatsum - m.mihdischf1 + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf2), 2) WHEN m.mihdischf1 > 0 THEN ROUND(l.milsum - ((l.milsum / NULLIF(m.mihnetsum - m.mihvatsum + m.mihdischf1 + m.mihdischf2, 0)) * m.mihdischf1), 2) ELSE l.milsum END`. |
| `ลดหนี้` | STRING | Constant '' (as in the sample). |
| `PerDisCN` | STRING | Constant '' (as in the sample). |
| `CN_No` | STRING | Constant '' (as in the sample). |
| `TotalDisCN` | STRING | Constant '' (as in the sample). |
| `PercentMargin` | STRING | Constant '' (as in the sample). |
| `Warehouse_id` | STRING | From `milsto` of validated_mac5.mil (document line). |
| `SaleChannel` | STRING | Computed: `REGEXP_EXTRACT(l.millinkvcno, r'^[^0-9]*')`. |
| `MIHkeyDate` | DATETIME | From `mihkeydate` of validated_mac5.mih (document header). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key` and the row key in `mart_sent_state`; never NULL (a NULL key value is JSON null). |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_invoice.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.mie](/validated/validated_mac5/mie.md), [validated_mac5.mih](/validated/validated_mac5/mih.md), [validated_mac5.mil](/validated/validated_mac5/mil.md), [validated_mac5.stk](/validated/validated_mac5/stk.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Company `ag01` only; documents of 2026. Aliases in the column descriptions: `l` = validated_mac5.mil (document line); `m` = validated_mac5.mih (document header); `mie` = validated_mac5.mie (latest row per document); `s` = validated_mac5.stk (product).

# Examples

Rows per folder date of the first-load files.

```sql
SELECT DATE(PARSE_DATETIME('%d/%m/%Y', Invoice_Date)) AS folder_date, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_invoice`
GROUP BY folder_date
ORDER BY folder_date
```

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_invoice`
GROUP BY row_key
HAVING n > 1
```
