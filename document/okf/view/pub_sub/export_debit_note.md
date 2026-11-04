---
type: BigQuery View
title: "export_debit_note"
description: "One row = one line of an ag01 debit note (AS) of 2026, not cancelled; commission set `debit_note` for the TF team, exposed for the Pub/Sub export with the sample's columns plus row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_debit_note&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_debit_note
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_debit_note.sqlx"
    title: "Dataform definition (view/pub_sub/export_debit_note.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-02T18:00:00+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `debit_note` for the TF team (company ag01): one line of an ag01 debit note (AS) of 2026, not cancelled. Its columns, names, order and JSON types are those of the commission sample sent to TF on 2026-10-14 (`commission_tf_ag01_2026`). The Cloud Run publisher (jobs `datamart-publish-check` and `datamart-publish-send`) compares `row_hash` with [mart_sent_state](/process/mart_sent_state.md) after each successful `daily_process` run and publishes NEW/UPDATE/DELETE messages with `table` = `debit_note` to topic `export-commission-debit_note`. It is registered in [mart_export_config](/process/mart_export_config.md). First-load files are split into date folders by `DN_Date` (`snapshot_date` in the export config).

# Grain and key

One line of an ag01 debit note (AS) of 2026, not cancelled: key `company_source_id, DN_id, no` (unique). `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of validated_mac5.mih (document header). Part of the natural key. |
| `INV_No` | STRING | From `millinkvcno` of validated_mac5.mil (document line). |
| `Invoiceid` | STRING | Constant '' (as in the sample). |
| `DN_id` | STRING | From `mihvnos` of validated_mac5.mih (document header). Part of the natural key. |
| `DN_Date` | STRING | Computed: `FORMAT('%d/%d/%d', m.mihday, m.mihmonth, m.mihyear)`. |
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
| `DNType` | STRING | From `ar_snamet` of validated_mac5.ar_s (status code). |
| `row_key` | STRING | `TO_JSON_STRING(STRUCT(company_source_id, DN_id, no))`: JSON of the natural key, used as the message `primary_key` and the row key in `mart_sent_state`; never NULL (a NULL key value is JSON null). |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`; the publisher sends a row only when it differs from the sent state. |

# How it is built

- Definition: `definitions/view/pub_sub/export_debit_note.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.mih](/validated/validated_mac5/mih.md), [validated_mac5.mil](/validated/validated_mac5/mil.md), [validated_mac5.stk](/validated/validated_mac5/stk.md).
- Logical view: `CREATE OR REPLACE VIEW`, no data stored; deployed by running tag `pub_sub` by hand (no scheduler runs it). Company `ag01` only; documents of 2026. Aliases in the column descriptions: `ars` = validated_mac5.ar_s (status code); `l` = validated_mac5.mil (document line); `m` = validated_mac5.mih (document header); `s` = validated_mac5.stk (product).

# Examples

Rows per folder date of the first-load files.

```sql
SELECT DATE(PARSE_DATETIME('%d/%m/%Y', DN_Date)) AS folder_date, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_debit_note`
GROUP BY folder_date
ORDER BY folder_date
```

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_debit_note`
GROUP BY row_key
HAVING n > 1
```
