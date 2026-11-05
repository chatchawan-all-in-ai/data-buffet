---
type: BigQuery Table
title: "per"
description: "One row = one employee, a record of source table `per` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=per&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: per
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/per/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `per` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Employee master of the MAC5 ERP (mainly salespeople): name, department, position, employment dates and contact details. Used by: [validated_mac5.per](/validated/validated_mac5/per.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `PERcode` | STRING | Employee (salesperson) code. |
| `PERdep` | STRING | Department code of the employee (joins `dep.depcode`). |
| `PERtaxnos` | STRING | Tax ID of the employee. |
| `PERnameT` | STRING | Employee name in Thai (first name, surname and nickname in parentheses). |
| `PERnameE` | STRING | Employee name in English. |
| `PERbdate` | STRING | Birth date of the employee. |
| `PERworkS` | STRING | Employment start date. |
| `PERworkF` | STRING | Employment end date. |
| `PERadd1` | STRING | Address line 1 of the employee. |
| `PERadd2` | STRING | Address line 2 of the employee. |
| `PERadd3` | STRING | Address line 3 of the employee. |
| `PERtel` | STRING | Phone number of the employee. |
| `PERpositn` | STRING | Job position title in Thai (e.g. Agent salesperson, TA Water Solution). |
| `PERstatus` | INT64 | Employment status code (0, 1, 2). |
| `PERnchild` | INT64 | Number of children of the employee. |
| `PERcisstudy` | INT64 | Number of the employee's children in school. |
| `PERnotstudy` | INT64 | Number of the employee's children not in school. |
| `PERsalary` | FLOAT64 | Salary of the employee. |
| `PERhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `PERlock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `PERmemo` | STRING | Free-text memo on the employee. |
| `PEReditLK` | STRING | Date and time the record was locked for editing. |
| `PERrefWE` | STRING | External reference code of the record. |
| `PEReditDT` | STRING | Date and time the record was last edited. |
| `PEReditMF` | STRING | User code of the person who last edited the record. |
| `rowguid` | STRING | Row GUID that uniquely identifies the record in the source database. |
| `PERzone` | STRING | Sales zone of the employee. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/per/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.per`
LIMIT 100
```
