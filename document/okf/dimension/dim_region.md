---
type: BigQuery Table
title: "dim_region"
description: "One row = one sales region or sub-region (RegionID, SubRegionID) of one company over one StartDate to EndDate validity interval, from the MDS region master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_region&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_region
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_region.sqlx"
    title: "Dataform definition (dimension/dim_region.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Region master of the sales organisation: it ties a RegionID / SubRegionID to its director (DirectorID), name and validity window. It answers which region a sale, a MDT branch or a target belongs to. It is the region dimension that `fact_transcation` and the MDT saleout/target facts point to through `RegionSK`, and the source of the one-row-per-code snapshot [dim_region_last](/dimension/dim_region_last.md).

Read by: [dim_pump_information](/dimension/dim_pump_information.md), [dim_region_last](/dimension/dim_region_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md), [fact_target_series_mdt](/fact/fact_target_series_mdt.md), [rls_customer360](/process/rls_customer360.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per active MDS row; ordered (and SK-numbered) by companyID, RegionID, SubRegionID, StartDate, EndDate. A region whose director or name changed over time appears once per validity interval, so `(companyID, RegionID, SubRegionID)` is not unique here. When `RegionID` differs from `SubRegionID` the row is a sub-region (section-level) of the region; `dim_target_product_group_by_sale_dayofwork` then matches it on `dep.SectionID = SubRegionID`. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `RegionSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by companyID, RegionID, SubRegionID, StartDate, EndDate. Regenerated every run. Referenced by `fact_transcation.RegionSK`, [dim_pump_information](/dimension/dim_pump_information.md) lookups and the MDT facts. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `DirectorID` | STRING | Code of the director that owns the region; join key to `dim_director.DirectorID` (+ CompanySK), as used by `dim_target_product_group_by_sale_dayofwork`. |
| `RegionID` | STRING | Region code. Also the join key used by consumers (for example `dim_region_manager.RegionID`, `dim_report.RegionID`, MDT `StoreCode`). |
| `SubRegionID` | STRING | Sub-region code inside the region; equals RegionID when the region has no sub-division. |
| `RegionName` | STRING | Display name of the region (or sub-region) as entered in MDS. |
| `StartDate` | DATE | First date the row is valid, straight from MDS (DATE, no cleaning). |
| `EndDate` | DATE | Last date the row is valid, straight from MDS (DATE). |
| `MdsID` | STRING | Primary key (`id`) of the source row in `mds_data_sales_region_master`; trace column only. |

# How it is built

- Definition: `definitions/dimension/dim_region.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `RegionSK`.
- Storage options: `{"clusterBy": ["RegionSK"]}`.
- Reads: `mds_dataset.mds_data_sales_region_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_sales_region_master`.
- Approximate size (BigQuery metadata, 2026-10-31): 56 rows, 6.4 KB.

# Examples

Regions valid today, with their director.

```sql
SELECT RegionSK, companyID, DirectorID, RegionID, SubRegionID, RegionName
FROM `databuffet-nonprd.dimension_table.dim_region`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
ORDER BY companyID, RegionID, SubRegionID;
```

Number of validity intervals per region code (history depth).

```sql
SELECT companyID, RegionID, SubRegionID, COUNT(*) AS intervals
FROM `databuffet-nonprd.dimension_table.dim_region`
GROUP BY 1, 2, 3
HAVING COUNT(*) > 1;
```
