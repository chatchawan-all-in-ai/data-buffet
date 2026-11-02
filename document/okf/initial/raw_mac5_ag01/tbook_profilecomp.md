---
type: BigQuery Table
title: "tbook_profilecomp"
description: "One row = one project profile, a record of source table `tbook_profilecomp` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_profilecomp&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbook_profilecomp
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_profilecomp/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_profilecomp` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Construction project and company profiles of the quotation app, with project dates, value, location and contacts; source of dim_project. Used by: [validated_mac5.tbook_profilecomp](/validated/validated_mac5/tbook_profilecomp.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is whatever the files currently contain.

# Schema

| Column | Type | Description |
|---|---|---|
| `docno` | INT64 | Document number of the project profile. |
| `projectcode` | INT64 | Project code, referenced by the quotation project text. |
| `projectname` | STRING | Project name. |
| `statuscomp` | STRING | Project status colour (`เขียว` = green, `เหลือง` = yellow, `แดง` = red). |
| `compname` | STRING | Company name of the project owner or contractor. |
| `register` | STRING | Company registration (tax ID) number. |
| `addresscomp` | STRING | Company address. |
| `province` | STRING | Province of the project. |
| `district` | STRING | District of the project. |
| `country` | STRING | Country of the project. |
| `status` | STRING | Work category of the project (e.g. residential, hotel, housing estate, school). |
| `capital` | STRING | Registered capital of the company. |
| `place` | STRING | Location of the project. |
| `tel` | STRING | Company phone number. |
| `mobile` | STRING | Contact mobile number. |
| `fax` | STRING | Company fax number. |
| `mail` | STRING | Contact email address. |
| `namedirector` | STRING | Name of the company director or decision maker. |
| `nickname` | STRING | Nickname of the contact person. |
| `teldirector` | STRING | Phone number of the director. |
| `profilecomp` | STRING | Project profile description (e.g. condominium, hotel). |
| `typecomp` | STRING | Business type of the company (e.g. construction contractor, hotel). |
| `startdate` | STRING | Date the profile was opened. |
| `history` | STRING | Background history of the project or company. |
| `pjstart` | STRING | Project start date (text). |
| `pjend` | STRING | Project end date (text). |
| `pjval` | STRING | Project value (text). |
| `pjfor` | STRING | Expected purchase value for the project (text). |
| `compgroup` | STRING | Company group of the project. |
| `acccode` | STRING | Account code linked to the project (e.g. `AC958-60`). |
| `accname` | STRING | Account name linked to the project. |
| `closedby` | STRING | User who closed the project. |
| `projectfrom` | STRING | Source of the project lead. |
| `ptype` | STRING | Profile type (e.g. `Project`). |
| `ppc` | STRING | PPC code of the project. |
| `pecom` | STRING | PE commission value of the project. |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `dinsert` | STRING | Date and time the row was created. |
| `insertby` | STRING | Employee code of the user who created the profile. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dupdate` | STRING | Date and time the row was last updated. |
| `meccode` | STRING | Customer branch (ship-to) code, matching `mec.meccode`. |
| `contactdebcode` | STRING | MAC5 customer (debtor) code of the contact. |
| `refallkon` | STRING | Allkons reference code of the project. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_profilecomp/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_profilecomp`
LIMIT 100
```
