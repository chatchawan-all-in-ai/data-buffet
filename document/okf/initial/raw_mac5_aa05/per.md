---
type: BigQuery Table
title: "per"
description: "One row = one employee, a record of source table `per` (MAC5 for company `aa05`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_aa05&t=per&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_aa05
table_id: per
tags: ["initial", "raw_mac5_aa05", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5_aa05.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5_aa05.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_aa05/per/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `per` table from MAC5 for company `aa05`; nothing is cleaned or deduplicated here. Table meaning: Employee master of the MAC5 ERP (mainly salespeople): name, department, position, employment dates and contact details. Used by: [validated_mac5.per](/validated/validated_mac5/per.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `percode` | STRING | Employee (salesperson) code. |
| `perdep` | STRING | Department code of the employee (joins `dep.depcode`). |
| `pertaxnos` | STRING | Tax ID of the employee. |
| `pernamet` | STRING | Employee name in Thai (first name, surname and nickname in parentheses). |
| `pernamee` | STRING | Employee name in English. |
| `perbdate` | STRING | Birth date of the employee. |
| `perworks` | STRING | Employment start date. |
| `perworkf` | STRING | Employment end date. |
| `peradd1` | STRING | Address line 1 of the employee. |
| `peradd2` | STRING | Address line 2 of the employee. |
| `peradd3` | STRING | Address line 3 of the employee. |
| `pertel` | STRING | Phone number of the employee. |
| `perpositn` | STRING | Job position title in Thai (e.g. Agent salesperson, TA Water Solution). |
| `perstatus` | INT64 | Employment status code (0, 1, 2). |
| `pernchild` | INT64 | Number of children of the employee. |
| `percisstudy` | INT64 | Number of the employee's children in school. |
| `pernotstudy` | INT64 | Number of the employee's children not in school. |
| `persalary` | FLOAT64 | Salary of the employee. |
| `perhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `perlock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `permemo` | STRING | Free-text memo on the employee. |
| `pereditlk` | STRING | Date and time the record was locked for editing. |
| `perrefwe` | STRING | External reference code of the record. |
| `pereditdt` | STRING | Date and time the record was last edited. |
| `pereditmf` | STRING | User code of the person who last edited the record. |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5_aa05` (`definitions/initial/mac5/create_all_table_raw_mac5_aa05.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_aa05/per/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_aa05.per`
LIMIT 100
```
