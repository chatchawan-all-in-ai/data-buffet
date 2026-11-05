---
type: BigQuery Table
title: "cst"
description: "One row = one cost line of one stock document line, a record of source table `cst` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cst&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: cst
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cst/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `cst` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Cost-of-goods lines per document line (invoices, sales orders), with quantity, warehouse, salesperson and COGS.

Read by: [validated_mac5.cst](/validated/validated_mac5/cst.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `cstdate` | STRING | Document date. |
| `csttype` | STRING | Document type code (IS = invoice, PS = sales order). |
| `cstvnos` | STRING | Document number. |
| `cstcus` | STRING | Customer code (joins `deb.debcode`). |
| `cststk` | STRING | Stock code of the line (joins `stk.stkcode`). |
| `cstjob` | STRING | Job code of the line. |
| `cstdep` | STRING | Department code of the line. |
| `cstper` | STRING | Salesperson code of the line (joins `per.percode`). |
| `cstdoc` | STRING | Document reference code of the line. |
| `cstmec` | STRING | Branch (mec) code of the document. |
| `cststo` | STRING | Warehouse code of the line (joins `sto.stocode`). |
| `cstquan` | FLOAT64 | Quantity in the base unit. |
| `cstquanp2` | FLOAT64 | Quantity in the second unit. |
| `cstcogsp` | FLOAT64 | Cost of goods sold of the line in baht. |
| `cstexpdate` | STRING | Expiry date of the item on the line. |
| `cstlinkvc` | STRING | Document type code of the linked source document (e.g. `PS` = sales order). |
| `cstlinkvcid` | INT64 | Line ID of the linked source document line. |
| `cstio` | INT64 | Stock in/out direction code (0, 2). |
| `cstiozw` | INT64 | Stock movement kind code (0, 5). |
| `cstlist` | INT64 | Line number within the document. |
| `cstcosta` | FLOAT64 | Average-cost flag of the line (-1 = yes, 0 = no). |
| `cstcostf` | FLOAT64 | FIFO-cost flag of the line (-1 = yes, 0 = no). |
| `cstcostl` | FLOAT64 | LIFO-cost flag of the line (-1 = yes, 0 = no). |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |
| `ASATDATE` | STRING | Extract (snapshot) date of the source file, taken from the `ASATDATE` partition. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cst/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cst`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.cst`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
