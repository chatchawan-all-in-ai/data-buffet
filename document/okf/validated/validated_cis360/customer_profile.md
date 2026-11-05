---
type: BigQuery Table
title: "customer_profile"
description: "One row = one customer profile from source table `customer_profile`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=customer_profile&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: customer_profile
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/customer_profile.sqlx"
    title: "Dataform definition (validated/cis360/customer_profile.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of CIS360 `customer_profile`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Master customer profiles of the CIS360 customer 360 system (individuals and juristic persons) with type, status, KYC and verification flags; `customer_code` links them to MAC5 customers in `dim_customer`.
Used by: [dimension_table.dim_customer](/dimension/dim_customer.md).

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

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
| `create_date` | DATETIME | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | DATETIME | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/customer_profile.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.customer_profile](/initial/raw_cis360/customer_profile.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.customer_profile`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.customer_profile`
GROUP BY id
HAVING n > 1
```
