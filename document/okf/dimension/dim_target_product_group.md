---
type: BigQuery Table
title: "dim_target_product_group"
description: "One row = one company-level sales target (Amt and Qty) for a year and month by marketing group, sub group, segment, channel target group and TargetID, from the MDS target by product group master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_target_product_group&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_target_product_group
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_target_product_group.sqlx"
    title: "Dataform definition (dimension/dim_target_product_group.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Target amounts before they are split among employees. `dim_target_product_group_by_sale` joins it to [dim_rate_target](/dimension/dim_rate_target.md) to allocate the target by employee, and `view_dim_target_by_agent` and `Model_Target_DayOfWork` consume the result.

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md).

# Grain and key

One row = one active MDS target row. Natural key: (`companyID`, `Year`, `Month`, `MarketingGroupID`, `SubMarketingID`, `SegmentID`, `ChannelTargetGroup`, `TargetID`). `TargetProductGroupSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetProductGroupSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `Year` | INT64 | Target year (INT64 via `castInt64`). |
| `Month` | INT64 | Target month (INT64 via `castInt64`). |
| `MarketingGroupID` | STRING | Marketing group code of the target; matches `dim_product_mkt.MarketingGroupID` and `dim_rate_target.ProductGroupID`. |
| `MarketingGroupName` | STRING | Name of the marketing group. |
| `SubMarketingID` | STRING | Sub marketing group code. |
| `SubMarketingName` | STRING | Name of the sub marketing group. |
| `SegmentID` | STRING | Segment code. |
| `SegmentName` | STRING | Segment name. |
| `ChannelTargetGroup` | STRING | Sales channel group the target belongs to, e.g. `AGENT`, `MDT`, `PS1`, `PS2`, `IMP`, `ASIAN`, `HO`, `Non TargetID`; `MDT` rows feed view_fact_target_product_group_mdt. |
| `TargetID` | STRING | Target code; the join key to `dim_rate_target.TargetID` (with CompanySK, Year, Month). |
| `Amt` | FLOAT64 | Target sales amount in THB for the month (FLOAT64 via `castFloat64`). |
| `Qty` | FLOAT64 | Target quantity (FLOAT64 via `castFloat64`). |
| `MdsId` | STRING | `id` of the source row in `mds_dataset.mds_data_sales_target_by_product_group_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_target_product_group.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_sales_target_by_product_group_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Target by marketing group for the current year.

```sql
SELECT Month, MarketingGroupID, MarketingGroupName, TargetID, SUM(Amt) AS target_amt, SUM(Qty) AS target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_product_group`
WHERE companyID = 'ag01' AND Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2;
```
