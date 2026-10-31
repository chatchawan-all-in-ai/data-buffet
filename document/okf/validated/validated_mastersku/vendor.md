---
type: BigQuery Table
title: "vendor"
description: "One row = one cleaned copy of the source table `vendor`, unique on (vd_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=vendor&page=table"
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/vendor.sqlx"
    title: "Dataform definition (validated/mastersku/vendor.sqlx)"
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

Validated copy of MASTERSKU `vendor`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md).

# Grain and key

One row per `vd_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `vd_id` | STRING | Meaning not documented in the repo. |
| `vd_api_id` | STRING | Meaning not documented in the repo. |
| `vd_code` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `vd_name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `vd_coporate_no` | STRING | Meaning not documented in the repo. |
| `vd_tel` | STRING | Meaning not documented in the repo. |
| `vd_country_name` | STRING | Meaning not documented in the repo. |
| `vd_province_name` | STRING | Meaning not documented in the repo. |
| `vd_district_name` | STRING | Meaning not documented in the repo. |
| `vd_sub_district_name` | STRING | Meaning not documented in the repo. |
| `vd_zipcode` | STRING | Meaning not documented in the repo. |
| `vd_email` | STRING | Meaning not documented in the repo. |
| `vd_address` | STRING | Meaning not documented in the repo. |
| `vd_organize_name` | STRING | Meaning not documented in the repo. |
| `vd_business_type_name` | STRING | Meaning not documented in the repo. |
| `vd_document_id` | STRING | Meaning not documented in the repo. |
| `vd_document_path` | STRING | Meaning not documented in the repo. |
| `vd_is_dbd` | BOOL | Meaning not documented in the repo. |
| `vd_account_type` | STRING | Meaning not documented in the repo. |
| `vd_kyc_status` | STRING | Meaning not documented in the repo. |
| `vd_is_active` | BOOL | Meaning not documented in the repo. |
| `vd_is_use` | BOOL | Meaning not documented in the repo. |
| `vd_created_date` | DATETIME | Meaning not documented in the repo. |
| `vd_updated_date` | DATETIME | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/vendor.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.vendor](/initial/raw_mastersku/vendor.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `vd_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,386 rows, 1.2 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.vendor`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT vd_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.vendor`
GROUP BY vd_id
HAVING n > 1
```
