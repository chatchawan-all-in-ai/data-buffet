---
type: BigQuery View
title: "export_chqri"
description: "One row = one ag01 received cheque (chqtype 1) per receipt (RS) payment line across all years; commission set `chqri` for the TF team, exposed for the Pub/Sub export with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_chqri&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_chqri
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_chqri.sqlx"
    title: "Dataform definition (view/pub_sub/export_chqri.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-05T16:27:42+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of commission set `chqri` for the TF team (company ag01): one ag01 received cheque (chqtype 1) per receipt (RS) payment line across all years. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-commission-chqri`.

# Grain and key

One row = one ag01 received cheque (chqtype 1) per receipt (RS) payment line across all years: key `company_source_id`, `chqno`, `chqbank`, `chqdatec`, `chqtag`, `cqlvnos`, `cqlbank`, `cqlautono`, `cqlsys` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_source_id` | STRING | From `company_id` of validated_mac5.chq (cheque). Part of the natural key. |
| `chqbank` | STRING | From `chqbank` of validated_mac5.chq (cheque). Part of the natural key. |
| `chqdatec` | DATETIME | From `chqdatec` of validated_mac5.chq (cheque). Part of the natural key. |
| `chqtag` | INT64 | From `chqtag` of validated_mac5.chq (cheque). Part of the natural key. |
| `cqlautono` | INT64 | From `cqlautono` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `cqlsys` | INT64 | From `cqlsys` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `cqldate` | DATETIME | From `cqldate` of validated_mac5.cql (cheque/payment line). |
| `cqlbank` | STRING | From `cqlbank` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `Paymen_Method` | STRING | Computed: `CASE WHEN q.chqno IS NOT NULL AND q.chqno <> '' THEN 'Chq' ELSE 'Cash' END`. |
| `chqno` | STRING | Computed: `IFNULL(q.chqno, '')`. Part of the natural key. |
| `chqstatus` | STRING | Computed: `CASE q.chqstatus WHEN 2 THEN 'Bounced' WHEN 1 THEN 'Cleared' WHEN 0 THEN 'Due' ELSE '' END`. |
| `cqlvnos` | STRING | From `cqlvnos` of validated_mac5.cql (cheque/payment line). Part of the natural key. |
| `cqlcus` | STRING | From `cqlcus` of validated_mac5.cql (cheque/payment line). |
| `payment_amount` | FLOAT64 | From `cqlsuml` of validated_mac5.cql (cheque/payment line). |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_chqri.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md).
- Scope: company `ag01`, all years by payment-line date. Aliases in the column descriptions: `c` = validated_mac5.cql (cheque/payment line); `q` = validated_mac5.chq (cheque).

# Examples


Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_chqri`
GROUP BY row_key
HAVING n > 1
```
