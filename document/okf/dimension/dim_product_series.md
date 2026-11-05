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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Lookup of MDT product series (e.g. TITAN, OTHERS). Source: mds `mds_data_mdt_product_series_master`.

Read by: [dim_target_series_mdt](/dimension/dim_target_series_mdt.md), [Product_Attribute](/view/onetime/Product_Attribute.md), [export_dim_product_series](/view/pub_sub/export_dim_product_series.md).

# Grain and key

One row = one MDT product series: key `SeriesCode` among active mds rows; duplicates on the trimmed code are collapsed keeping the latest `updated_at` (then lowest id). `SeriesSK` is the surrogate key, regenerated every run. No sentinel row.

# Schema

| Column | Type | Description |
|---|---|---|
| `SeriesSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY SeriesCode)` over deduped rows. Regenerated every run. |
| `SeriesCode` | STRING | Series code (mds `SeriesCode`, trimmed, empty to NULL); unique key. |
| `SeriesName` | STRING | Series name (mds `SeriesName`, trimmed, empty to NULL). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_mdt_product_series_master`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_product_series.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `SeriesSK`.
- Storage options: `{"clusterBy": ["SeriesSK"]}`.
- Reads: `mds_dataset.mds_data_mdt_product_series_master` (master data loaded outside this repo).
- QUALIFY dedup on trimmed `SeriesCode`.
- Full daily rebuild (`type: "table"`, tags `dimension_daily`, `saleout_daily`); no declared dependencies.

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
