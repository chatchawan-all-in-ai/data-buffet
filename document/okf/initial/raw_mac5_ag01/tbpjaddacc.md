---
type: BigQuery Table
title: "tbpjaddacc"
description: "One row = one contact person attached to a project, a record of source table `tbpjaddacc` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbpjaddacc&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbpjaddacc
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbpjaddacc/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbpjaddacc` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Contact persons attached to sales projects, with their role, decision power and personal profile fields.

Read by: [validated_mac5.tbpjaddacc](/validated/validated_mac5/tbpjaddacc.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Running ID of the project contact row. |
| `pjid` | STRING | Project ID the contact is attached to. |
| `accid` | STRING | Account (organisation) code of the contact. |
| `accname` | STRING | Account (organisation) name of the contact. |
| `acctype` | STRING | Position or role of the contact (Thai, e.g. managing director, purchasing officer, contractor). |
| `acctype2` | STRING | Secondary position or role of the contact. |
| `accpow` | STRING | Decision-power flag (1 = the contact has decision power, 0 = not). |
| `conid` | STRING | Contact ID (e.g. `ICM`-prefixed code). |
| `conname` | STRING | Contact person name. |
| `contel` | STRING | Phone number of the contact. |
| `condetail` | STRING | Free-text detail about the contact. |
| `uinsert` | STRING | User code of the person who created the record. |
| `insertdate` | STRING | Date the record was created. |
| `textnote` | STRING | Free-text note on the contact. |
| `nickname` | STRING | Nickname of the contact. |
| `religion` | STRING | Religion of the contact. |
| `birthdate` | STRING | Birth date of the contact. |
| `lineidper` | STRING | Personal LINE ID of the contact. |
| `emailper` | STRING | Personal email address of the contact. |
| `idcardper` | STRING | National ID card number of the contact. |
| `addressper` | STRING | Personal address of the contact. |
| `country` | STRING | Country of the contact's address. |
| `province` | STRING | Province of the contact's address. |
| `district` | STRING | District of the contact's address. |
| `sub_district` | STRING | Sub-district of the contact's address. |
| `zipcode` | STRING | Postal code of the contact's address. |
| `spousefullname` | STRING | Full name of the contact's spouse. |
| `birthdatespouse` | STRING | Birth date of the contact's spouse. |
| `numberofchildren` | STRING | Number of children of the contact. |
| `favoriteactivity` | STRING | Activities the contact likes. |
| `unfavoriteactivity` | STRING | Activities the contact dislikes. |
| `trait` | STRING | Personality traits of the contact. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbpjaddacc/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbpjaddacc`
LIMIT 100
```
