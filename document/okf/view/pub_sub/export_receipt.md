---
type: BigQuery View
title: "export_receipt"
description: "One row = one line of an ag01 receipt (RS) across all years per cheque line paying it, document not cancelled; commission set `receipt` for the TF team, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_receipt&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_receipt
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_receipt.sqlx"
    title: "Dataform definition (view/pub_sub/export_receipt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `receipt` for the TF team (company ag01): one line of an ag01 receipt (RS) across all years per cheque line paying it, document not cancelled. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-commission-receipt`.

# Grain and key

One row = one line of an ag01 receipt (RS) across all years per cheque line paying it, document not cancelled: key `company_source_id`, `mirvnos`, `mirlistno`, `cqlno`, `cqlbank`, `cqlautono`, `chqbank`, `chqdatec`, `chqtag` (unique); `row_key` is the JSON of that key. The cheque columns are NULL for a cash receipt; a receipt line paid by several cheques gives several rows and repeats Payment_AmtInVat.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of validated_mac5.mir (receipt line). Part of the natural key. |
| `mirlistno` | INT64 | From `mirlistno` of validated_mac5.mir (receipt line). Part of the natural key. |
| `cqlno` | STRING | From `cqlno` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `cqlbank` | STRING | From `cqlbank` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `cqlautono` | INT64 | From `cqlautono` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `chqbank` | STRING | From `chqbank` of validated_mac5.chq (cheque). Part of the natural key. |
| `chqdatec` | DATETIME | From `chqdatec` of validated_mac5.chq (cheque). Part of the natural key. |
| `chqtag` | INT64 | From `chqtag` of validated_mac5.chq (cheque). Part of the natural key. |
| `mirvnos` | STRING | From `mirvnos` of validated_mac5.mir (receipt line). Part of the natural key. |
| `invoiceid` | STRING | Constant ''. |
| `mirbinvno` | STRING | From `mirbinvno` of validated_mac5.mir (receipt line). |
| `Paymen_Method` | STRING | Computed: `CASE WHEN q.chqno IS NOT NULL AND q.chqno <> '' THEN 'Chq' ELSE 'Cash' END`. |
| `chqno` | STRING | Computed: `IFNULL(q.chqno, '')`. |
| `chqstatus` | STRING | Computed: `CASE q.chqstatus WHEN 2 THEN 'Bounced' WHEN 1 THEN 'Cleared' WHEN 0 THEN 'Due' ELSE '' END`. |
| `Payment_Date` | STRING | Computed: `FORMAT('%02d/%02d/%d', r.mirday, r.mirmonth, r.miryear)`. |
| `Payment_AmtInVat` | FLOAT64 | From `mirsum` of validated_mac5.mir (receipt line). |
| `BankAccount` | STRING | From `ar_snamet` of validated_mac5.ar_s (status code). |
| `Statusid` | INT64 | From `mihstatus` of validated_mac5.mih (document header). |
| `CompanyId` | STRING | From `mihcus` of validated_mac5.mih (document header). |
| `Sell_id` | STRING | From `mihper` of validated_mac5.mih (document header). |
| `Product_Barcode` | STRING | Constant ''. |
| `Unit` | STRING | Constant ''. |
| `Unit_Price` | STRING | Constant ''. |
| `TotalPriceAmt` | STRING | Constant ''. |
| `Discount_Type` | STRING | Constant ''. |
| `DiscountAmt` | STRING | Constant ''. |
| `TotalAmt` | STRING | Constant ''. |
| `Discount1_Type` | STRING | Constant ''. |
| `Discount1Amt` | STRING | Constant ''. |
| `TotalAmt1` | STRING | Constant ''. |
| `Discount2_Type` | STRING | Constant ''. |
| `Discount2Amt` | STRING | Constant ''. |
| `Total2Amt` | STRING | Constant ''. |
| `TotalDisAmt` | STRING | Constant ''. |
| `PriceExvat` | STRING | Constant ''. |
| `ลดหนี้` | STRING | Constant ''. |
| `PerDisCN` | STRING | Constant ''. |
| `CN_No` | STRING | Constant ''. |
| `TotalDisCN` | STRING | Constant ''. |
| `PercentMargin` | STRING | Constant ''. |
| `Warehouse_id` | STRING | Constant ''. |
| `SaleChannel` | STRING | Constant ''. |
| `MIHkeyDate` | DATETIME | From `mihkeydate` of validated_mac5.mih (document header). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_receipt.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [validated_mac5.mih](/validated/validated_mac5/mih.md), [validated_mac5.mir](/validated/validated_mac5/mir.md).
- Scope: company `ag01`, all years. Aliases in the column descriptions: `ars` = validated_mac5.ar_s (status code); `c` = validated_mac5.cql (cheque/payment line); `m` = validated_mac5.mih (document header); `q` = validated_mac5.chq (cheque); `r` = validated_mac5.mir (receipt line).

# Examples


Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_receipt`
GROUP BY row_key
HAVING n > 1
```
