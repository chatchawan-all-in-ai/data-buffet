---
type: BigQuery Table
title: "inventory_item_price"
description: "One row = one cleaned copy of the source table `inventory_item_price`, unique on (inventory_item_price_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=inventory_item_price&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: inventory_item_price
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/inventory_item_price.sqlx"
    title: "Dataform definition (validated/derp/inventory_item_price.sqlx)"
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

Validated copy of DERP `inventory_item_price`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

One row per `inventory_item_price_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `inventory_item_price_id` | STRING | Meaning not documented in the repo. |
| `record_id` | INT64 | Meaning not documented in the repo. |
| `item_number` | STRING | Meaning not documented in the repo. |
| `costing_version_id` | STRING | Meaning not documented in the repo. |
| `price_type` | STRING | Meaning not documented in the repo. |
| `from_date` | DATE | Meaning not documented in the repo. |
| `price_site_id` | STRING | Meaning not documented in the repo. |
| `product_configuration_id` | STRING | Meaning not documented in the repo. |
| `product_color_id` | STRING | Meaning not documented in the repo. |
| `product_size_id` | STRING | Meaning not documented in the repo. |
| `product_style_id` | STRING | Meaning not documented in the repo. |
| `product_version_id` | STRING | Meaning not documented in the repo. |
| `product_unit_symbol` | STRING | Meaning not documented in the repo. |
| `price` | FLOAT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `price_quantity` | FLOAT64 | Meaning not documented in the repo. |
| `price_charges_quantity` | FLOAT64 | Meaning not documented in the repo. |
| `fixed_price_charges` | FLOAT64 | Meaning not documented in the repo. |
| `is_price_including_charges` | BOOL | Meaning not documented in the repo. |
| `calculation_number` | STRING | Meaning not documented in the repo. |
| `is_active` | BOOL | Active flag from the source (inferred from the column name). |
| `price_created_datetime` | DATETIME | Meaning not documented in the repo. |
| `created_datetime` | DATETIME | Meaning not documented in the repo. |
| `created_by` | STRING | Meaning not documented in the repo. |
| `updated_datetime` | DATETIME | Meaning not documented in the repo. |
| `updated_by` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/inventory_item_price.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.inventory_item_price](/initial/raw_derp/inventory_item_price.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY updated_datetime DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `inventory_item_price_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 174,967 rows, 28.0 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.inventory_item_price`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT inventory_item_price_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.inventory_item_price`
GROUP BY inventory_item_price_id
HAVING n > 1
```
