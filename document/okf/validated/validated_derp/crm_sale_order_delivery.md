---
type: BigQuery Table
title: "crm_sale_order_delivery"
description: "One row = one cleaned copy of the source table `crm_sale_order_delivery`, unique on (sale_order_delivery_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_sale_order_delivery&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_sale_order_delivery
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_sale_order_delivery.sqlx"
    title: "Dataform definition (validated/derp/crm_sale_order_delivery.sqlx)"
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

Validated copy of DERP `crm_sale_order_delivery`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `sale_order_delivery_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_order_delivery_id` | STRING | Meaning not documented in the repo. |
| `sale_order_id` | STRING | Meaning not documented in the repo. |
| `so_no` | STRING | Meaning not documented in the repo. |
| `so_date` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `round_no` | INT64 | Meaning not documented in the repo. |
| `delivery_date` | DATETIME | Meaning not documented in the repo. |
| `delivery_address_id` | STRING | Meaning not documented in the repo. |
| `delivery_address_code` | STRING | Meaning not documented in the repo. |
| `delivery_address_text` | STRING | Meaning not documented in the repo. |
| `receiver_name` | STRING | Meaning not documented in the repo. |
| `receiver_phone` | STRING | Meaning not documented in the repo. |
| `remark_logistic` | STRING | Meaning not documented in the repo. |
| `order_sort` | INT64 | Meaning not documented in the repo. |
| `created_at` | DATETIME | Source row creation timestamp (inferred from the column name). |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_at` | DATETIME | Source row last-update timestamp (inferred from the column name). |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `created_by_name` | STRING | Meaning not documented in the repo. |
| `updated_by_name` | STRING | Meaning not documented in the repo. |
| `time_start` | STRING | Meaning not documented in the repo. |
| `time_end` | STRING | Meaning not documented in the repo. |
| `ship_type` | STRING | Meaning not documented in the repo. |
| `phase` | STRING | Meaning not documented in the repo. |
| `house_no` | STRING | Meaning not documented in the repo. |
| `plot` | STRING | Meaning not documented in the repo. |
| `latitude` | FLOAT64 | Meaning not documented in the repo. |
| `longitude` | FLOAT64 | Meaning not documented in the repo. |
| `site_id` | STRING | Meaning not documented in the repo. |
| `site_code` | STRING | Meaning not documented in the repo. |
| `delivery_address_full` | STRING | Meaning not documented in the repo. |
| `delivery_sub_district` | STRING | Meaning not documented in the repo. |
| `delivery_sub_district_code` | STRING | Meaning not documented in the repo. |
| `delivery_district` | STRING | Meaning not documented in the repo. |
| `delivery_district_code` | STRING | Meaning not documented in the repo. |
| `delivery_province` | STRING | Meaning not documented in the repo. |
| `delivery_province_code` | STRING | Meaning not documented in the repo. |
| `delivery_postal_code` | STRING | Meaning not documented in the repo. |
| `delivery_country_code` | STRING | Meaning not documented in the repo. |
| `delivery_map_url` | STRING | Meaning not documented in the repo. |
| `nearby_landmark` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_sale_order_delivery.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_sale_order_delivery](/initial/raw_derp/crm_sale_order_delivery.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `sale_order_delivery_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,450 rows, 3.1 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_sale_order_delivery`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT sale_order_delivery_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_sale_order_delivery`
GROUP BY sale_order_delivery_id
HAVING n > 1
```
