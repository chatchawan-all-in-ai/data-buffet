---
type: BigQuery Table
title: "product_group"
description: "One row = one product group from source table `product_group`, unique on (pg_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mastersku&t=product_group&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mastersku
table_id: product_group
tags: ["validated", "validated_mastersku", "mastersku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mastersku/product_group.sqlx"
    title: "Dataform definition (validated/mastersku/product_group.sqlx)"
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

Validated copy of MASTERSKU `product_group`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product groups (families of variant SKUs) of MASTERSKU with their variant dimension labels, brand and vendor.
No other table or view in this repository reads it.

# Grain and key

One row per `pg_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `pg_id` | STRING | Unique identifier (UUID) of the product group. |
| `pg_description` | STRING | Description of the product group. |
| `pg_dimension1` | STRING | Label of variant dimension 1 used by products in the group (e.g. Size, Color, Model). |
| `pg_dimension2` | STRING | Label of variant dimension 2 used by products in the group (e.g. Size, Color, Model). |
| `pg_dimension3` | STRING | Label of variant dimension 3 used by products in the group (e.g. Size, Color, Model). |
| `pg_dimension4` | STRING | Label of variant dimension 4 used by products in the group (e.g. Size, Color, Model). |
| `pg_dimension_d365_1` | STRING | Dynamics 365 dimension mapped to variant dimension 1. |
| `pg_dimension_d365_2` | STRING | Dynamics 365 dimension mapped to variant dimension 2. |
| `pg_dimension_d365_3` | STRING | Dynamics 365 dimension mapped to variant dimension 3. |
| `pg_dimension_d365_4` | STRING | Dynamics 365 dimension mapped to variant dimension 4. |
| `pg_vendor_id` | STRING | Vendor that owns the product group (FK to `vendor.vd_id`). |
| `pg_is_system` | BOOL | System flag of the product group. |
| `pg_is_active` | BOOL | Active flag of the record. |
| `pg_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `pg_created_date` | DATETIME | Timestamp when the record was created. |
| `pg_created_by` | STRING | Identifier of the user who created the record. |
| `pg_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `pg_updated_by` | STRING | Identifier of the user who last updated the record. |
| `pg_brand_id` | STRING | Brand of the product group (FK to `brand.bra_id`). |
| `pg_code` | STRING | Product group code. |
| `pg_name` | STRING | Product group name. |
| `pg_sku` | STRING | SKU code of the product group. |
| `pg_barcode` | STRING | Barcode of the product group. |
| `pg_er_source` | STRING | Comma-separated attribute labels from the source group definition (e.g. grade, size, color). |
| `pg_tag` | STRING | Search tags of the group as JSON (`{"group_tag":[...]}`). |
| `pg_file_name` | STRING | File name of the product group image. |
| `pg_cg_id` | STRING | Cost group of the product group. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/product_group.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.product_group](/initial/raw_mastersku/product_group.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `pg_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mastersku.product_group`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT pg_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mastersku.product_group`
GROUP BY pg_id
HAVING n > 1
```
