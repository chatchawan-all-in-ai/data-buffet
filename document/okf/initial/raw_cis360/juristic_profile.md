---
type: BigQuery Table
title: "juristic_profile"
description: "One row = one juristic profile of a customer, a record of source table `juristic_profile` (CIS360) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_cis360&t=juristic_profile&page=table"
project_id: databuffet-nonprd
dataset_id: raw_cis360
table_id: juristic_profile
tags: ["initial", "raw_cis360", "cis360"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/cis360/create_all_table_raw_cis360.sqlx"
    title: "Dataform definition (initial/cis360/create_all_table_raw_cis360.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/cis360/juristic_profile/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `juristic_profile` table from CIS360; nothing is cleaned or deduplicated here. Table meaning: Company details of juristic-person customers in CIS360: head office or branch, juristic entity type, highest authority and contact person. Used by: [validated_cis360.juristic_profile](/validated/validated_cis360/juristic_profile.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the juristic profile. |
| `customer_profile_id` | STRING | Customer profile this juristic detail belongs to (`customer_profile.id`). |
| `organize_type_id` | INT64 | Organization type (`organize_type.id`: 1 = HEAD_OFFICE, 2 = BRANCH). |
| `juristic_type_id` | INT64 | Juristic entity type (`juristic_type.id`). |
| `juristic_type_remark` | STRING | Free-text remark on the juristic entity type. |
| `nature_business_remark` | STRING | Free-text remark on the nature of business. |
| `branch_number` | STRING | Branch number of the juristic person. |
| `highest_authority_name` | STRING | Name of the highest authority (e.g. managing director) of the juristic person. |
| `highest_authority_position` | STRING | Position title of the highest authority. |
| `highest_authority_phone_number` | STRING | Whether a phone number of the highest authority is recorded. |
| `highest_authority_email` | STRING | Whether an email of the highest authority is recorded. |
| `contact_name` | STRING | Name of the contact person of the juristic person. |
| `contact_phone_number` | STRING | Whether a contact phone number is recorded. |
| `contact_email` | STRING | Whether a contact email is recorded. |
| `contact_shown_highest_authority` | BOOL | Whether the contact person is the highest authority. |
| `is_delete` | BOOL | Soft-delete flag (TRUE = record deleted). |
| `create_date` | STRING | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | STRING | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_cis360` (`definitions/initial/cis360/create_all_table_raw_cis360.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/cis360/juristic_profile/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_cis360.juristic_profile`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_cis360.juristic_profile`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
