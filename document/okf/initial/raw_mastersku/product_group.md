---
type: BigQuery Table
title: "product_group"
description: "One row = one product group, a record of source table `product_group` (MASTERSKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mastersku&t=product_group&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mastersku
table_id: product_group
tags: ["initial", "raw_mastersku", "mastersku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx"
    title: "Dataform definition (initial/mastersku/create_all_table_raw_mastersku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mastersku/product_group/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `product_group` table from MASTERSKU; nothing is cleaned or deduplicated here. Table meaning: Product groups (families of variant SKUs) of MASTERSKU with their variant dimension labels, brand and vendor.

Read by: [validated_mastersku.product_group](/validated/validated_mastersku/product_group.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

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
| `pg_created_date` | STRING | Timestamp when the record was created. |
| `pg_created_by` | STRING | Identifier of the user who created the record. |
| `pg_updated_date` | STRING | Timestamp when the record was last updated. |
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
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mastersku` (`definitions/initial/mastersku/create_all_table_raw_mastersku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mastersku/product_group/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mastersku.product_group`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mastersku.product_group`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
