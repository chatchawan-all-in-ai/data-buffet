---
type: BigQuery Table
title: "cfs"
description: "One row = one invoice settlement record, a record of source table `cfs` (MAC5 for company `ac02`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ac02&t=cfs&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ac02
table_id: cfs
tags: ["initial", "raw_mac5_ac02", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_ac02.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_ac02.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ac02/cfs/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `cfs` table from MAC5 for company `ac02`; nothing is cleaned or deduplicated here. Table meaning: Settlement status of each invoice: amount due, amount settled and adjusted, billing and clearing flags. Used by: [validated_mac5.cfs](/validated/validated_mac5/cfs.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `cfsvnosid` | STRING | Number of the invoice whose settlement is tracked. |
| `cfsdateid` | STRING | Date of the invoice. |
| `cfscusid` | STRING | Customer code of the invoice, matching `deb.debcode`. |
| `cfstypeid` | STRING | Document type of the invoice (e.g. `IS`, `PS`). |
| `cfsjob` | STRING | Job code of the invoice (sales job or project category). |
| `cfsdep` | STRING | Department code of the invoice, used as the sales channel code. |
| `cfsper` | STRING | Salesperson (employee) code of the invoice. |
| `cfsdoc` | STRING | Document reference code. |
| `cfsmec` | STRING | Memo-card code of the invoice, matching `mec.meccode`. |
| `cfssumreq` | FLOAT64 | Invoice amount to be settled. |
| `cfssumcut1` | FLOAT64 | Amount already settled by receipts. |
| `cfssumcut2` | FLOAT64 | Amount adjusted by credit or debit notes (negative for credit notes). |
| `cfsclearsum` | INT64 | Flag: invoice amount fully settled (-1 = settled). |
| `cfsclearuser` | INT64 | Flag: invoice cleared manually by a user (-1 = yes). |
| `cfsclearall` | INT64 | Flag: invoice fully cleared (-1 = cleared). |
| `cfscurc` | INT64 | Currency code (0 = Thai baht). |
| `cfsexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `cfsbillcut` | FLOAT64 | Amount of the invoice already placed on a billing statement. |
| `cfsbillclr` | INT64 | Flag: invoice fully billed (-1 = billed). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_ac02` (`definitions/initial/mac5/create_all_table_raw_mac5_ac02.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ac02/cfs/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ac02.cfs`
LIMIT 100
```
