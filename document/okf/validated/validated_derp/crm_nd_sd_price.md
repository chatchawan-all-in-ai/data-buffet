---
type: BigQuery Table
title: "crm_nd_sd_price"
description: "One row = one cleaned copy of the source table `crm_nd_sd_price`, unique on (nd_sd_price_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_nd_sd_price&page=table"
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_nd_sd_price.sqlx"
    title: "Dataform definition (validated/derp/crm_nd_sd_price.sqlx)"
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

Validated copy of DERP `crm_nd_sd_price`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `nd_sd_price_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `nd_sd_price_id` | STRING | Meaning not documented in the repo. |
| `product_id` | STRING | Meaning not documented in the repo. |
| `product_code` | STRING | Meaning not documented in the repo. |
| `product_barcode` | STRING | Meaning not documented in the repo. |
| `effective_from` | DATE | Meaning not documented in the repo. |
| `expiry_to` | DATE | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `list_price_incl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `list_price_excl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `list_price_vat_rate` | FLOAT64 | Meaning not documented in the repo. |
| `floor_pct` | FLOAT64 | Meaning not documented in the repo. |
| `floor_price_incl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `nd_min_qty` | INT64 | Meaning not documented in the repo. |
| `nd_max_qty` | INT64 | Meaning not documented in the repo. |
| `sd1_rate` | FLOAT64 | Meaning not documented in the repo. |
| `sd1_rate_type` | STRING | Meaning not documented in the repo. |
| `sd1_price_excl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `sd1_min_qty` | INT64 | Meaning not documented in the repo. |
| `sd1_max_qty` | INT64 | Meaning not documented in the repo. |
| `sd2_rate` | FLOAT64 | Meaning not documented in the repo. |
| `sd2_rate_type` | STRING | Meaning not documented in the repo. |
| `sd2_price_excl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `sd2_min_qty` | INT64 | Meaning not documented in the repo. |
| `sd2_max_qty` | INT64 | Meaning not documented in the repo. |
| `sd3_rate` | FLOAT64 | Meaning not documented in the repo. |
| `sd3_rate_type` | STRING | Meaning not documented in the repo. |
| `sd3_price_excl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `sd3_min_qty` | INT64 | Meaning not documented in the repo. |
| `sd3_max_qty` | INT64 | Meaning not documented in the repo. |
| `bigpro_rate` | FLOAT64 | Meaning not documented in the repo. |
| `bigpro_rate_type` | STRING | Meaning not documented in the repo. |
| `bigpro_price_excl_vat` | FLOAT64 | Meaning not documented in the repo. |
| `remark` | STRING | Likely free-text remark (inferred from the column name only; not documented in the repo). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `deleted_at` | DATETIME | Meaning not documented in the repo. |
| `floor_rate_type` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_nd_sd_price.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_nd_sd_price](/initial/raw_derp/crm_nd_sd_price.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `nd_sd_price_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 751 rows, 274.8 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT nd_sd_price_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_nd_sd_price`
GROUP BY nd_sd_price_id
HAVING n > 1
```
