---
type: BigQuery Table
title: "product"
description: "One row = one cleaned copy of the source table `product`, unique on (prd_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product&page=table"
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product.sqlx"
    title: "Dataform definition (validated/mastersku/product.sqlx)"
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

Validated copy of MASTERSKU `product`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_mastersku.curated_product](/curated/curated_mastersku/curated_product.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `prd_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `prd_id` | STRING | Meaning not documented in the repo. |
| `prd_sku` | STRING | Meaning not documented in the repo. |
| `prd_description` | STRING | Meaning not documented in the repo. |
| `prd_d365_sku` | STRING | Meaning not documented in the repo. |
| `prd_item_text` | STRING | Meaning not documented in the repo. |
| `prd_item_code` | STRING | Meaning not documented in the repo. |
| `prd_stopped_sate` | STRING | Meaning not documented in the repo. |
| `prd_made_to_order` | STRING | Meaning not documented in the repo. |
| `prd_sale_unite` | STRING | Meaning not documented in the repo. |
| `prd_tag` | STRING | Meaning not documented in the repo. |
| `prd_universal_barcode` | STRING | Meaning not documented in the repo. |
| `prd_internal_barcode` | STRING | Meaning not documented in the repo. |
| `prd_cat_id` | STRING | Meaning not documented in the repo. |
| `prd_filter1` | STRING | Meaning not documented in the repo. |
| `prd_filter2` | STRING | Meaning not documented in the repo. |
| `prd_brand_id` | STRING | Meaning not documented in the repo. |
| `prd_size` | STRING | Meaning not documented in the repo. |
| `prd_line` | STRING | Meaning not documented in the repo. |
| `prd_color` | STRING | Meaning not documented in the repo. |
| `prd_model` | STRING | Meaning not documented in the repo. |
| `prd_dimension1` | STRING | Meaning not documented in the repo. |
| `prd_dimension2` | STRING | Meaning not documented in the repo. |
| `prd_dimension3` | STRING | Meaning not documented in the repo. |
| `prd_dimension4` | STRING | Meaning not documented in the repo. |
| `prd_vendor_id` | STRING | Meaning not documented in the repo. |
| `prd_is_active` | BOOL | Meaning not documented in the repo. |
| `prd_is_use` | BOOL | Meaning not documented in the repo. |
| `prd_created_date` | DATETIME | Meaning not documented in the repo. |
| `prd_created_by` | STRING | Meaning not documented in the repo. |
| `prd_updated_date` | DATETIME | Meaning not documented in the repo. |
| `prd_updated_by` | STRING | Meaning not documented in the repo. |
| `prd_pg_id` | STRING | Meaning not documented in the repo. |
| `prd_ps_id` | STRING | Meaning not documented in the repo. |
| `prd_id_source` | STRING | Meaning not documented in the repo. |
| `prd_mc_id` | STRING | Meaning not documented in the repo. |
| `prd_diminsion_data` | STRING | Meaning not documented in the repo. |
| `prd_pas_id` | STRING | Meaning not documented in the repo. |
| `prd_barcode` | STRING | Meaning not documented in the repo. |
| `prd_reject_remark` | STRING | Meaning not documented in the repo. |
| `prd_ref_mp_id` | STRING | Meaning not documented in the repo. |
| `prd_is_combo` | BOOL | Meaning not documented in the repo. |
| `prd_combo_price` | FLOAT64 | Meaning not documented in the repo. |
| `prd_is_time` | BOOL | Meaning not documented in the repo. |
| `prd_combo_start` | DATETIME | Meaning not documented in the repo. |
| `prd_combo_end` | DATETIME | Meaning not documented in the repo. |
| `prd_total_combo_price` | FLOAT64 | Meaning not documented in the repo. |
| `prd_total_cost_combo_price` | FLOAT64 | Meaning not documented in the repo. |
| `prd_barcode_format` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product](/initial/raw_mastersku/product.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `prd_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 109,833 rows, 91.7 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT prd_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product`
GROUP BY prd_id
HAVING n > 1
```
