---
type: BigQuery Table
title: "dim_product_series"
description: "One row = one MDT product series (SeriesCode and SeriesName), from the MDS product-series master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_product_series&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_product_series
tags: ["dimension", "mds", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_product_series.sqlx"
    title: "Dataform definition (dimension/dim_product_series.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Small lookup of product series (e.g. TITAN, OTHERS). Used by [dim_target_series_mdt](/dimension/dim_target_series_mdt.md), which maps unknown series codes to OTHERS (there is no -1 row), and by the product attribute model [Product_Attribute](/view/onetime/Product_Attribute.md). It reads mds `mds_data_mdt_product_series_master`.

# Grain and key

One row per `SeriesCode` among active mds rows; duplicates on the trimmed code are collapsed keeping the latest `updated_at` (then lowest id), to stop targets in dim_target_series_mdt multiplying. Key: `SeriesSK` (surrogate, unstable across days). No sentinel row.

# Schema

| Column | Type | Description |
|---|---|---|
| `SeriesSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY SeriesCode)` over deduped rows; regenerates every run. |
| `SeriesCode` | STRING | Series code (mds `SeriesCode`, trimmed, empty to NULL); unique key. |
| `SeriesName` | STRING | Series name (mds `SeriesName`, trimmed, empty to NULL). |
| `MdsID` | STRING | Row id of the source record in the mds master (`id`, not run through `cleanString`; trace column). |

# How it is built

- Definition: `definitions/dimension/dim_product_series.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `SeriesSK`.
- Storage options: `{"clusterBy": ["SeriesSK"]}`.
- Reads: `mds_dataset.mds_data_mdt_product_series_master` (master data loaded outside this repo).
- Full daily rebuild (`type: "table"`, tags `dimension_daily` and the saleout daily tag) from active mds rows with a QUALIFY dedup on trimmed `SeriesCode`; no dim_company dependency. Clustered by `SeriesSK`.
- Approximate size (BigQuery metadata, 2026-10-31): 2 rows, 123 B.

# Examples

All product series.

```sql
SELECT SeriesSK, SeriesCode, SeriesName
FROM `databuffet-nonprd.dimension_table.dim_product_series`
ORDER BY SeriesCode;
```

Duplicate series codes.

```sql
SELECT SeriesCode, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_product_series`
GROUP BY 1
HAVING n > 1;
```
