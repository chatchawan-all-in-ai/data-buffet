---
type: BigQuery Table
title: "userloginanyprogram"
description: "One row = one login account for one web application, a record of source table `userloginanyprogram` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=userloginanyprogram&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: userloginanyprogram
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/userloginanyprogram/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `userloginanyprogram` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Login accounts for the MAC5 companion web applications (pay-in, bill payment, billing, promotion master), with user department and permission level.

Read by: [validated_mac5.userloginanyprogram](/validated/validated_mac5/userloginanyprogram.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Running ID of the login account row. |
| `username` | STRING | Login user name (usually the employee code). |
| `password` | STRING | Account password, stored as a bcrypt hash or as plain text. |
| `actionapp` | STRING | Web application the login is for (PayinOnline, Billpayment, BillingOnline, MasterPromotion, ManagementTAOut). |
| `name` | STRING | Full name of the user. |
| `notes` | STRING | Free-text note on the user's section or role (e.g. general accounting, credit). |
| `department` | STRING | Department of the user (e.g. Account, Admin, Marketing, IT). |
| `levelaction` | STRING | Extra permission level in the application (e.g. `printBilling`, `CheckPayment`). |
| `email` | STRING | Email address of the user. |
| `token` | STRING | Access or reset token issued to the account. |
| `tokenexpiry` | STRING | Expiry date and time of `token`. |
| `istokenvalid` | STRING | Flag whether `token` is still valid (1 = valid, 0 = not). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/userloginanyprogram/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.userloginanyprogram`
LIMIT 100
```
