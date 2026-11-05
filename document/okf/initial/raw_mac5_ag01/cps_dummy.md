---
type: BigQuery Table
title: "cps_dummy"
description: "One row = one outstanding sales order line, a record of source table `cps_dummy` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cps_dummy&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: cps_dummy
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cps_dummy/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `cps_dummy` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Outstanding sales order lines from the ERP's dummy (staging) table, same layout as `cps`.

Read by: [validated_mac5.cps_dummy](/validated/validated_mac5/cps_dummy.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `cpsstkid` | STRING | Product (stock) code of the outstanding line, matching `stk.stkcode`. |
| `cpslinkid` | INT64 | Internal ID linking the outstanding record to its document line. |
| `cpsvnosid` | STRING | Number of the sales order document that has the outstanding line (e.g. a `PS` sales order). |
| `cpsdateid` | STRING | Date of the sales order document. |
| `cpscusid` | STRING | Customer code of the document, matching `deb.debcode`. |
| `cpsjob` | STRING | Job code of the document (sales job or project category). |
| `cpsdep` | STRING | Department code of the document, used as the sales channel code. |
| `cpsper` | STRING | Salesperson (employee) code of the document. |
| `cpsdoc` | STRING | Document reference code. |
| `cpsmec` | STRING | Memo-card code of the document, matching `mec.meccode`. |
| `cpssto` | STRING | Warehouse (store) code the line is issued from or received into. |
| `cpsstkreq` | FLOAT64 | Quantity ordered on the line. |
| `cpsstkcut1` | FLOAT64 | Quantity already delivered or received against the line. |
| `cpsstkcut2` | FLOAT64 | Quantity cut against the line by adjustment documents. |
| `cpssumreq` | FLOAT64 | Amount ordered on the line. |
| `cpssumcut1` | FLOAT64 | Amount already delivered or invoiced against the line. |
| `cpssumcut2` | FLOAT64 | Amount cut against the line by adjustment documents. |
| `cpsclearstk` | INT64 | Flag: outstanding quantity cleared (-1 = cleared). |
| `cpsclearsum` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `cpsclearuser` | INT64 | Flag: line cleared manually by a user (-1 = yes). |
| `cpsclearall` | INT64 | Flag: line fully cleared (-1 = cleared). |
| `cpscurc` | INT64 | Currency code (0 = Thai baht). |
| `cpsexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `cpscut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `cpsdelvdate` | STRING | Requested delivery date of the line. |
| `cpslistno` | INT64 | Line number within the document. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cps_dummy/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cps_dummy`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.cps_dummy`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
