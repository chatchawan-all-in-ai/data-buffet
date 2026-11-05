---
type: BigQuery Table
title: "brand"
description: "One row = one brand from source table `brand`, unique on (bra_id)."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MASTERSKU `brand`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Product brands of the old product master MASTERSKU, each owned by a vendor.

Read by: [curated_mastersku.product_for_aisearch](/curated/curated_mastersku/product_for_aisearch.md), [pub_sub.export_brand](/view/pub_sub/export_brand.md).

# Grain and key

One row per `bra_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `bra_id` | STRING | Unique identifier (UUID) of the brand. |
| `bra_name` | STRING | Brand name. |
| `bra_name_th` | STRING | Brand name in Thai. |
| `bra_detail` | STRING | Brand description. |
| `bra_vendor_id` | STRING | Vendor that owns the brand (FK to `vendor.vd_id`). |
| `bra_logo_name` | STRING | File name of the brand logo. |
| `bra_logo_path` | STRING | Storage path of the brand logo. |
| `bra_is_use` | BOOL | In-use flag of the record (FALSE = retired from use). |
| `bra_is_active` | BOOL | Active flag of the record. |
| `bra_created_date` | DATETIME | Timestamp when the record was created. |
| `bra_created_by` | STRING | Identifier of the user who created the record. |
| `bra_updated_date` | DATETIME | Timestamp when the record was last updated. |
| `bra_updated_by` | STRING | Identifier of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mastersku/brand.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mastersku.brand](/initial/raw_mastersku/brand.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `bra_id`.

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
