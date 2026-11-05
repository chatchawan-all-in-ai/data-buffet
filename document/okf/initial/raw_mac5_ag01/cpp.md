---
type: BigQuery Table
title: "cpp"
description: "One row = one outstanding purchase order line, a record of source table `cpp` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=cpp&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: cpp
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/cpp/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `cpp` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Outstanding purchase order lines: ordered versus received quantity and amount, with clearing flags. Used by: [validated_mac5.cpp](/validated/validated_mac5/cpp.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `cppstkid` | STRING | Product (stock) code of the outstanding purchase line, matching `stk.stkcode`. |
| `cpplinkid` | INT64 | Internal ID linking the outstanding record to its document line. |
| `cppvnosid` | STRING | Number of the purchase order document that has the outstanding line (e.g. a `POF...` purchase order). |
| `cppdateid` | STRING | Date of the purchase order document. |
| `cppcusid` | STRING | Supplier code of the document, matching `cre.crecode`. |
| `cppjob` | STRING | Job code of the document (sales job or project category). |
| `cppdep` | STRING | Department code of the document, used as the sales channel code. |
| `cppper` | STRING | Purchaser (employee) code of the document. |
| `cppdoc` | STRING | Document reference code. |
| `cppmec` | STRING | Memo-card code of the document, matching `mec.meccode`. |
| `cppsto` | STRING | Warehouse (store) code the line is received into. |
| `cppstkreq` | FLOAT64 | Quantity ordered on the purchase line. |
| `cppstkcut1` | FLOAT64 | Quantity already received against the purchase line. |
| `cppstkcut2` | FLOAT64 | Quantity cut against the line by adjustment documents. |
| `cppsumreq` | FLOAT64 | Amount ordered on the line. |
| `cppsumcut1` | FLOAT64 | Amount already received or invoiced against the purchase line. |
| `cppsumcut2` | FLOAT64 | Amount cut against the line by adjustment documents. |
| `cppclearstk` | INT64 | Flag: outstanding quantity cleared (-1 = cleared). |
| `cppclearsum` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `cppclearuser` | INT64 | Flag: line cleared manually by a user (-1 = yes). |
| `cppclearall` | INT64 | Flag: line fully cleared (-1 = cleared). |
| `cppcurc` | INT64 | Currency code (0 = Thai baht). |
| `cppexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `cppcut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `cppdelvdate` | STRING | Expected delivery date of the purchase line. |
| `cpplistno` | INT64 | Line number within the document. |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/cpp/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.cpp`
LIMIT 100
```
