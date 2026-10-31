---
type: BigQuery Table
title: "brand"
description: "One row = one cleaned copy of the source table `brand`, unique on (bra_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=brand&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: brand
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/brand.sqlx"
    title: "Dataform definition (validated/mastersku/brand.sqlx)"
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

Validated copy of MASTERSKU `brand`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md).

# Grain and key

One row per `bra_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `bra_id` | STRING | Meaning not documented in the repo. |
| `bra_name` | STRING | Meaning not documented in the repo. |
| `bra_name_th` | STRING | Meaning not documented in the repo. |
| `bra_detail` | STRING | Meaning not documented in the repo. |
| `bra_vendor_id` | STRING | Meaning not documented in the repo. |
| `bra_logo_name` | STRING | Meaning not documented in the repo. |
| `bra_logo_path` | STRING | Meaning not documented in the repo. |
| `bra_is_use` | BOOL | Meaning not documented in the repo. |
| `bra_is_active` | BOOL | Meaning not documented in the repo. |
| `bra_created_date` | DATETIME | Meaning not documented in the repo. |
| `bra_created_by` | STRING | Meaning not documented in the repo. |
| `bra_updated_date` | DATETIME | Meaning not documented in the repo. |
| `bra_updated_by` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/brand.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.brand](/initial/raw_mastersku/brand.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `bra_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 1,531 rows, 308.6 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.brand`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT bra_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.brand`
GROUP BY bra_id
HAVING n > 1
```
