---
type: BigQuery Table
title: "dim_sales_branch_mdt"
description: "One row = one MDT (modern-trade) retail branch identified by store chain (StoreCode) and branch number (BranchCode), with its region, section and zone keys, plus waiting rows for branches that appear in the saleout feeds but not yet in the master and a reserved -1 row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_sales_branch_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_sales_branch_mdt
tags: ["dimension", "mds", "saleout", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_sales_branch_mdt.sqlx"
    title: "Dataform definition (dimension/dim_sales_branch_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Branch dimension of the MDT saleout pipeline. The saleout, monthly saleout, stock and target facts (`fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `fact_stock_mdt`, `fact_target_saleout_mdt`, `fact_target_series_mdt`) and the target dims join it through `BranchMdtSK`; it also feeds `dim_pc`. It resolves each branch to its region (and region manager), section (and section manager) and zone (and zone manager).

Read by: [dim_pc](/dimension/dim_pc.md), [dim_target_saleout_mdt](/dimension/dim_target_saleout_mdt.md), [dim_target_series_mdt](/dimension/dim_target_series_mdt.md), [fact_saleout_mdt](/fact/fact_saleout_mdt.md), [fact_saleout_monthly_mdt](/fact/fact_saleout_monthly_mdt.md), [fact_stock_mdt](/fact/fact_stock_mdt.md), [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md), [fact_target_series_mdt](/fact/fact_target_series_mdt.md), [view_fact_salein_mdt](/view/fact_view/view_fact_salein_mdt.md).

# Grain and key

One row = one MDT branch. Natural key: (`StoreCode`, `BranchCode`, `StartDate`, `EndDate`). `BranchMdtSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `BranchMdtSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `RegionSK` | INT64 | SK in [dim_region_last](/dimension/dim_region_last.md) (the `_last` numbering), joined on StoreCode = RegionID for company ag01; -1 when not found. |
| `RegionManagerSK` | INT64 | Region manager SK, read from `dim_region_last.RegionManagerSK` (backfilled there by `update_sk_sale_rep_group`); -1 when NULL or not found. |
| `SectionSK` | INT64 | SK in [dim_section_last](/dimension/dim_section_last.md) for ag01, joined on `StoreCode_<parsed section>` = `dim_section_last.SectionID`, where the section is parsed from BranchCodeMdt (pattern `<chain>_<Section>_<seq>`, with single-letter-digit codes zero-padded and CEN treated as empty); -1 for waiting rows or no match. |
| `SectionManagerSK` | INT64 | Section manager SK, read from `dim_section_last.SectionManagerSK` (backfilled there by `update_sk_sale_rep_group`); -1 when NULL or not found. |
| `ZoneMdtSK` | INT64 | SK in [dim_zone_mdt](/dimension/dim_zone_mdt.md), joined on ZoneCode; -1 when the zone is unknown or waiting. |
| `ZoneTaMdtSK` | INT64 | SK of the zone manager in [dim_zone_ta_mdt](/dimension/dim_zone_ta_mdt.md) (first numeric EmployeeID per ZoneCode, excluding -1); -1 when none. |
| `StoreCode` | STRING | Store chain (department store) code: MDS `region_id` for master rows, `store_code` of the feed for waiting rows. Equals `dim_region_last.RegionID` of ag01; 'NotStore' on the -1 row. |
| `RegionName` | STRING | Name of the region, from dim_region_last.RegionName; 'ไม่ระบุภูมิภาค' on the -1 row. |
| `SubRegionID` | STRING | Sub-region code, from dim_region_last.SubRegionID; 'NotSubRegion' on the -1 row. |
| `BranchCode` | STRING | Branch number within the store chain: MDS `store_id` (feed `branch_code` for waiting rows); 'NotBranch' on the -1 row. With StoreCode it is the natural key matching the saleout feeds. |
| `BranchCodeMdt` | STRING | MDT branch code from the MDS master (`branch_code`, shaped like chain_section_seq); NULL on waiting rows, 'NotBranch' on the -1 row. Target tables join on it (after mapping a GH_ prefix to GB_). |
| `BranchName` | STRING | Branch name; for waiting rows the feed name or the BranchCode when the feed has no name; 'ไม่ระบุสาขา' on the -1 row. |
| `ZoneCode` | STRING | Zone code (`zone_id`); 'WAITING' for waiting rows, 'NotZone' on the -1 row. |
| `ZoneName` | STRING | Zone name from dim_zone_mdt; 'Waiting Master' for waiting rows, 'ไม่ระบุโซน' on the -1 row. |
| `Warehouse` | STRING | Company warehouse/site code serving the branch (`KTB`, `LP`, `KK`, `UB`, `PK`, `HY`); NULL on waiting rows, 'NotWarehouse' on the -1 row. |
| `StartDate` | DATE | MDS start_date for master rows; first sale date seen in the feeds for waiting rows; NULL on the -1 row. |
| `EndDate` | DATE | MDS end_date for master rows; NULL for waiting and -1 rows. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_mdt_sales_branch_master`; trace column back to MDS. NULL on waiting and -1 rows. |
# How it is built

- Definition: `definitions/dimension/dim_sales_branch_mdt.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`, `saleout_daily`).
- Reads: [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_zone_ta_mdt](/dimension/dim_zone_ta_mdt.md), `mds_dataset.mds_data_mdt_sales_branch_master` (master data loaded outside this repo), [dimension_table.dim_zone_mdt](/dimension/dim_zone_mdt.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md), [curated_saleout_mdt.curated_saleout_monthly_mdt](/curated/curated_saleout_mdt/curated_saleout_monthly_mdt.md), [curated_saleout_mdt.curated_stock_mdt](/curated/curated_saleout_mdt/curated_stock_mdt.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_zone_mdt, dim_zone_ta_mdt, dim_region_last and dim_section_last.
# Examples

Branches that still wait for master data.

```sql
SELECT BranchMdtSK, StoreCode, BranchCode, BranchName, StartDate AS first_sale_date
FROM `databuffet-nonprd.dimension_table.dim_sales_branch_mdt`
WHERE ZoneCode = 'WAITING'
ORDER BY StoreCode, BranchCode;
```

Branches per zone.

```sql
SELECT ZoneCode, ZoneName, COUNT(*) AS branches
FROM `databuffet-nonprd.dimension_table.dim_sales_branch_mdt`
WHERE BranchMdtSK <> -1
GROUP BY 1, 2
ORDER BY branches DESC;
```
