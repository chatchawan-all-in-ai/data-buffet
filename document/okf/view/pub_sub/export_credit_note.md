---
type: BigQuery View
title: "export_credit_note"
description: "One row = one line of an ag01 credit note (BS) across all years, not cancelled; commission set `credit_note` for the TF team, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_credit_note&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_credit_note
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_credit_note.sqlx"
    title: "Dataform definition (view/pub_sub/export_credit_note.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-05T16:27:50+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `credit_note` for the TF team (company ag01): one line of an ag01 credit note (BS) across all years, not cancelled. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-commission-credit_note`.

# Grain and key

One row = one line of an ag01 credit note (BS) across all years, not cancelled: key `company_source_id`, `CN_id`, `no` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of validated_mac5.mih (document header). Part of the natural key. |
| `INV_No` | STRING | From `millinkvcno` of validated_mac5.mil (document line). |
| `Invoiceid` | STRING | Constant ''. |
| `CN_id` | STRING | From `mihvnos` of validated_mac5.mih (document header). Part of the natural key. |
| `CN_Date` | STRING | Computed: `FORMAT('%d/%d/%d', m.mihday, m.mihmonth, m.mihyear)`. |
| `companyid` | STRING | From `mihcus` of validated_mac5.mih (document header). |
| `no` | INT64 | From `millistno` of validated_mac5.mil (document line). Part of the natural key. |
| `stkcut` | INT64 | From `milcut` of validated_mac5.mil (document line). |
| `milstk` | STRING | From `milstk` of validated_mac5.mil (document line). |
| `mildesc` | STRING | From `mildesc` of validated_mac5.mil (document line). |
| `Product_Barcode` | STRING | From `stkcode885` of validated_mac5.stk (product). |
| `Unit` | FLOAT64 | From `milquan` of validated_mac5.mil (document line). |
| `Unit_Price` | FLOAT64 | Computed: `SAFE_DIVIDE(l.milcog, l.milquan)`. |
| `TotalPriceAmt` | FLOAT64 | From `milcog` of validated_mac5.mil (document line). |
| `invoice_value` | FLOAT64 | From `milsum` of validated_mac5.mil (document line). |
| `Actual_amt` | FLOAT64 | From `milsum` of validated_mac5.mil (document line). |
| `MIHkeyDate` | DATETIME | From `mihkeydate` of validated_mac5.mih (document header). |
| `CNType` | STRING | From `ar_snamet` of validated_mac5.ar_s (status code). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_credit_note.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.mih](/validated/validated_mac5/mih.md), [validated_mac5.mil](/validated/validated_mac5/mil.md), [validated_mac5.stk](/validated/validated_mac5/stk.md).
- Scope: company `ag01`, all years. Aliases in the column descriptions: `ars` = validated_mac5.ar_s (status code); `l` = validated_mac5.mil (document line); `m` = validated_mac5.mih (document header); `s` = validated_mac5.stk (product).

# Examples


Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_credit_note`
GROUP BY row_key
HAVING n > 1
```
