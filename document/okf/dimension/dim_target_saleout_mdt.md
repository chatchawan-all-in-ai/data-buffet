---
type: BigQuery Table
title: "dim_target_saleout_mdt"
description: "One row = the daily sales target (Amt, Qty) of one MDT branch for one marketing group, sub group and segment on one date, derived by splitting the monthly MDS target evenly over the days of the month, plus a reserved -1 row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_target_saleout_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_target_saleout_mdt
tags: ["dimension", "mds", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_target_saleout_mdt.sqlx"
    title: "Dataform definition (dimension/dim_target_saleout_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Daily saleout target for MDT branches. `fact_target_saleout_mdt` reads it to compare the target with actual saleout; the SKs point to [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) and [dim_product_mkt](/dimension/dim_product_mkt.md).

Read by: [fact_target_saleout_mdt](/fact/fact_target_saleout_mdt.md).

# Grain and key

One row = one MDT branch, marketing group, sub group and segment on one calendar day: key `TargetSaleoutMdtSK`. Monthly MDS rows are first de-duplicated per `(branch_code, marketinggroupid, submarketingid, segmentid, year, month)` keeping the latest `updated_at`, then expanded to one row per calendar day of the month. SK ordered by TargetDate, BranchCodeMdt, MarketingGroupID, SubMarketingID, SegmentID. Reserved row `TargetSaleoutMdtSK = -1` (BranchCodeMdt 'NotBranch', MarketingGroupID 'NotGroup', SubMarketingID 'NotSubGroup', SegmentID 'NotSegment', NULL date and amounts). Partitioned by TargetDate, so the -1 row sits in the NULL partition.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetSaleoutMdtSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by TargetDate, BranchCodeMdt, MarketingGroupID, SubMarketingID, SegmentID; -1 for the reserved row. Regenerated every run. |
| `BranchMdtSK` | INT64 | SK from dim_sales_branch_mdt joined on BranchCodeMdt (a `GH_` prefix is rewritten to `GB_`); -1 when the branch is not found. |
| `ProductMktSK` | INT64 | SK from dim_product_mkt joined on MarketingGroupID + SubMarketingID + SegmentID, restricted to CompanyID ag01 (one SK per set); -1 when not found. |
| `StoreCode` | STRING | Store chain code from dim_sales_branch_mdt (NULL if the branch was not matched); 'NotStore' on the -1 row. |
| `BranchCodeMdt` | STRING | MDT branch code from the target file (`branch_code`, trimmed); 'NotBranch' on the -1 row. |
| `MarketingGroupID` | STRING | Marketing group code of the target (trimmed); 'NotGroup' on the -1 row. |
| `MarketingGroupName` | STRING | Marketing group name; 'ไม่ระบุกลุ่มสินค้า' on the -1 row. |
| `SubMarketingID` | STRING | Sub group code; 'NotSubGroup' on the -1 row. |
| `SubMarketingName` | STRING | Sub group name; 'ไม่ระบุกลุ่มย่อย' on the -1 row. |
| `SegmentID` | STRING | Segment code; 'NotSegment' on the -1 row. |
| `SegmentName` | STRING | Segment name; 'ไม่ระบุเซกเมนต์' on the -1 row. |
| `TargetDate` | DATE | Calendar day the daily target applies to (every day of the target month, holidays included); partition column; NULL on the -1 row. |
| `TargetYear` | INT64 | Year of the monthly target row. |
| `TargetMonth` | INT64 | Month (1-12) of the monthly target row. |
| `DaysInMonth` | INT64 | Number of calendar days in the target month; the divisor used for Amt and Qty. |
| `Amt` | FLOAT64 | Daily target amount = monthly `value` / DaysInMonth (FLOAT64); NULL on the -1 row. |
| `Qty` | FLOAT64 | Daily target quantity = monthly `Quantity` / DaysInMonth (FLOAT64); NULL on the -1 row. |
| `MdsID` | STRING | `id` of the source row in `mds_data_mdt_sales_target_by_product_master`; trace column back to MDS. NULL on the -1 row. |

# How it is built

- Definition: `definitions/dimension/dim_target_saleout_mdt.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `TargetSaleoutMdtSK`.
- Storage options: `{"partitionBy": "TargetDate", "clusterBy": ["BranchMdtSK", "MarketingGroupID", "ProductMktSK"]}`.
- Reads: `mds_dataset.mds_data_mdt_sales_target_by_product_master` (master data loaded outside this repo), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).
- Full daily rebuild (`type: "table"`, tags `dimension_daily`, `saleout_daily`); runs after dim_sales_branch_mdt and dim_product_mkt.

# Examples

Monthly target by branch for the current month.

```sql
SELECT BranchMdtSK, BranchCodeMdt, SUM(Amt) AS month_target_amt, SUM(Qty) AS month_target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_saleout_mdt`
WHERE TargetDate >= DATE_TRUNC(CURRENT_DATE('Asia/Bangkok'), MONTH)
  AND TargetDate < DATE_ADD(DATE_TRUNC(CURRENT_DATE('Asia/Bangkok'), MONTH), INTERVAL 1 MONTH)
GROUP BY 1, 2
ORDER BY month_target_amt DESC;
```
