---
type: BigQuery Table
title: "juristic_profile"
description: "One row = one juristic profile of a customer from source table `juristic_profile`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=juristic_profile&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: juristic_profile
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/juristic_profile.sqlx"
    title: "Dataform definition (validated/cis360/juristic_profile.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of CIS360 `juristic_profile`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Company details of juristic-person customers in CIS360: head office or branch, juristic entity type, highest authority and contact person.
No other repo object reads it.

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Unique identifier (UUID) of the juristic profile. |
| `customer_profile_id` | STRING | Customer profile this juristic detail belongs to (`customer_profile.id`). |
| `organize_type_id` | INT64 | Organization type (`organize_type.id`: 1 = HEAD_OFFICE, 2 = BRANCH). |
| `juristic_type_id` | INT64 | Juristic entity type (`juristic_type.id`). |
| `juristic_type_remark` | STRING | Free-text remark on the juristic entity type. |
| `nature_business_remark` | STRING | Free-text remark on the nature of business. |
| `highest_authority_name` | STRING | Name of the highest authority (e.g. managing director) of the juristic person. |
| `highest_authority_position` | STRING | Position title of the highest authority. |
| `highest_authority_phone_number` | BOOL | Whether a phone number of the highest authority is recorded. |
| `highest_authority_email` | BOOL | Whether an email of the highest authority is recorded. |
| `contact_name` | STRING | Name of the contact person of the juristic person. |
| `contact_phone_number` | BOOL | Whether a contact phone number is recorded. |
| `contact_email` | BOOL | Whether a contact email is recorded. |
| `contact_shown_highest_authority` | BOOL | Whether the contact person is the highest authority. |
| `is_delete` | BOOL | Soft-delete flag (TRUE = record deleted). |
| `create_date` | DATETIME | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | DATETIME | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/juristic_profile.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.juristic_profile](/initial/raw_cis360/juristic_profile.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.juristic_profile`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.juristic_profile`
GROUP BY id
HAVING n > 1
```
