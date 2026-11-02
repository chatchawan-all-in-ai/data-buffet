---
type: BigQuery Table
title: "customer_profile"
description: "One row = one customer profile, a record of source table `customer_profile` (CIS360) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_cis360&t=customer_profile&page=table"
project_id: databuffet-nonprd
dataset_id: raw_cis360
table_id: customer_profile
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

External table over AVRO files in `gs://file-raw-data/cis360/customer_profile/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `customer_profile` table from CIS360; nothing is cleaned or deduplicated here. Table meaning: Master customer profiles of the CIS360 customer 360 system (individuals and juristic persons) with type, status, KYC and verification flags; `customer_code` links them to MAC5 customers in `dim_customer`. Used by: [validated_cis360.customer_profile](/validated/validated_cis360/customer_profile.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the customer profile. |
| `allkons_id` | STRING | Identifier of the customer's Allkons ID account (32-character ID). |
| `tax_id` | STRING | Tax identification number of the customer (13-digit Thai tax or national ID). |
| `customer_id` | STRING | External customer identifier (not populated in current data). |
| `customer_type_id` | INT64 | Customer type (`customer_type.id`: 1 = PERSONAL, 2 = JURISTIC). |
| `customer_profile_type_id` | INT64 | Customer profile type (`customer_profile_type.id`: 1 = PERSONAL, 2 = JURISTIC, 3 = OFFICE_BRAND, 4 = OFFICE). |
| `customer_status_id` | INT64 | Customer status (`customer_status.id`: 1 = VISITOR, 2 = CUSTOMER). |
| `image_profile_id` | STRING | Identifier of the customer's profile image file. |
| `customer_code` | STRING | CIS360 customer code (`C` + 7 digits), matched to `match_customer.customer_allkon` to link MAC5 customers. |
| `prefix_id` | INT64 | Name prefix (title) of the customer (`prefix.id`). |
| `first_name` | STRING | First name of the customer (individual). |
| `middle_name` | STRING | Middle name of the customer (individual). |
| `last_name` | STRING | Last name of the customer (individual). |
| `full_name` | STRING | Full display name of the customer (person or company). |
| `kyc_status` | STRING | KYC verification status (`APPROVE`, `WAIT_FOR_APPROVE`, `REQUEST_MORE`, `REJECT`, `NONE`). |
| `active_status` | BOOL | Whether the customer profile is active. |
| `is_dopa` | BOOL | Whether the person's identity was verified with the Department of Provincial Administration (DOPA). |
| `is_dbd` | BOOL | Whether the juristic person was verified with the Department of Business Development (DBD). |
| `is_allow_concern` | BOOL | Whether the customer gave consent for use of personal data. |
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
- Format `AVRO`, URI `gs://file-raw-data/cis360/customer_profile/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_cis360.customer_profile`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_cis360.customer_profile`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
