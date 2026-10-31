---
type: BigQuery Table
title: "product_detail"
description: "One row = one cleaned copy of the source table `product_detail`, unique on (pd_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_detail&page=table"
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_detail.sqlx"
    title: "Dataform definition (validated/mastersku/product_detail.sqlx)"
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

Validated copy of MASTERSKU `product_detail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_mastersku.curated_product](/curated/curated_mastersku/curated_product.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `pd_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `pd_id` | STRING | Meaning not documented in the repo. |
| `pd_prd_id` | STRING | Meaning not documented in the repo. |
| `pd_url_video` | STRING | Meaning not documented in the repo. |
| `pd_detail` | STRING | Meaning not documented in the repo. |
| `pd_series` | STRING | Meaning not documented in the repo. |
| `pd_model` | STRING | Meaning not documented in the repo. |
| `pd_material` | STRING | Meaning not documented in the repo. |
| `pd_certificate` | STRING | Meaning not documented in the repo. |
| `pd_garantee` | STRING | Meaning not documented in the repo. |
| `pd_garantee_detail` | STRING | Meaning not documented in the repo. |
| `pd_shape` | STRING | Meaning not documented in the repo. |
| `pd_supplier_country` | STRING | Meaning not documented in the repo. |
| `pd_package_wide` | FLOAT64 | Meaning not documented in the repo. |
| `pd_package_long` | FLOAT64 | Meaning not documented in the repo. |
| `pd_package_hight` | FLOAT64 | Meaning not documented in the repo. |
| `pd_size_wide` | FLOAT64 | Meaning not documented in the repo. |
| `pd_size_long` | FLOAT64 | Meaning not documented in the repo. |
| `pd_sl_id` | STRING | Meaning not documented in the repo. |
| `pd_size_hight` | FLOAT64 | Meaning not documented in the repo. |
| `pd_sh_id` | STRING | Meaning not documented in the repo. |
| `pd_net_weight` | FLOAT64 | Meaning not documented in the repo. |
| `pd_gross_weight` | FLOAT64 | Meaning not documented in the repo. |
| `pd_uw_id` | STRING | Meaning not documented in the repo. |
| `pd_ul_id` | STRING | Meaning not documented in the repo. |
| `pd_uh_id` | STRING | Meaning not documented in the repo. |
| `pd_sw_id` | STRING | Meaning not documented in the repo. |
| `pd_net_unit_id` | STRING | Meaning not documented in the repo. |
| `pd_gross_unit_id` | STRING | Meaning not documented in the repo. |
| `pd_how_to` | STRING | Meaning not documented in the repo. |
| `pd_how_to_url` | STRING | Meaning not documented in the repo. |
| `pd_how_to_path` | STRING | Meaning not documented in the repo. |
| `pd_suggest` | STRING | Meaning not documented in the repo. |
| `pd_suggest_url` | STRING | Meaning not documented in the repo. |
| `pd_suggest_path` | STRING | Meaning not documented in the repo. |
| `pd_caution` | STRING | Meaning not documented in the repo. |
| `pd_caution_url` | STRING | Meaning not documented in the repo. |
| `pd_caution_path` | STRING | Meaning not documented in the repo. |
| `pd_file_name` | STRING | Meaning not documented in the repo. |
| `pd_file_path` | STRING | Meaning not documented in the repo. |
| `pd_is_system` | BOOL | Meaning not documented in the repo. |
| `pd_created_date` | DATETIME | Meaning not documented in the repo. |
| `pd_created_by` | STRING | Meaning not documented in the repo. |
| `pd_updated_date` | DATETIME | Meaning not documented in the repo. |
| `pd_updated_by` | STRING | Meaning not documented in the repo. |
| `pd_product_name` | STRING | Meaning not documented in the repo. |
| `pd_vendor_code` | STRING | Meaning not documented in the repo. |
| `pd_barcode` | STRING | Meaning not documented in the repo. |
| `pd_sale_unit` | STRING | Meaning not documented in the repo. |
| `pd_spacific_fields` | STRING | Meaning not documented in the repo. |
| `pd_remark_inactive` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_detail.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_detail](/initial/raw_mastersku/product_detail.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `pd_id`.
- Approximate size (BigQuery metadata, 2026-10-31): 109,833 rows, 273.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_detail`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT pd_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_detail`
GROUP BY pd_id
HAVING n > 1
```
