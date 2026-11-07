---
type: BigQuery Table
title: "dim_target_product_group_by_sale"
description: "One row = one company-level product-group target (TargetProductGroupSK) allocated to one employee and department through a rate rule (RateTargetSK), with the allocated amount and quantity (CalAmt, CalQty) and the latest-snapshot org keys of that employee."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_target_product_group_by_sale&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_target_product_group_by_sale
tags: ["dimension", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_target_product_group_by_sale.sqlx"
    title: "Dataform definition (dimension/dim_target_product_group_by_sale.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-07T19:53:32+00:00" }
status: draft
---

# What it is

Per-employee sales targets: each target in [dim_target_product_group](/dimension/dim_target_product_group.md) is multiplied by the matching `Percent / 100` of [dim_rate_target](/dimension/dim_rate_target.md) to give `CalAmt` / `CalQty`, and enriched with the employee's current department, region, section, managers, director (`*Last` columns) and `ReportSK`. [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md) spreads it over days and `view_dim_target_by_agent_dayofwork` reads it.

Read by: [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md).

# Grain and key

One row = one target allocated to one employee and department by a rate rule, retaining the allocation and hierarchy combinations in the definition’s `QUALIFY` partition. The row key is `TargetBySaleSK`; (`TargetProductGroupSK`, `RateTargetSK`) supplies its numbering order, not a uniqueness constraint. Three allocation branches are combined with UNION ALL: (1) year-wide rate rows (Month and ProductGroupID NULL), (2) monthly rows (Month set, ProductGroupID NULL), and (3) month plus product-group rows (`MarketingGroupID = ProductGroupID`). The later branches exclude only matches with the same TargetProductGroupSK, CompanySK and RateTargetSK already emitted by an earlier branch. Distinct yearly and monthly rules therefore both survive; there is no first-match precedence per target. The monthly branches use LEFT JOINs, so NULL-rule rows can coexist with successful allocations from other branches. The final `DISTINCT` + `QUALIFY ROW_NUMBER()` removes duplicates created by the report join. `TargetBySaleSK` is `ROW_NUMBER()` over TargetProductGroupSK, RateTargetSK and is regenerated on every rebuild; ordering within ties is unspecified, so the key identifies a row only within that rebuild.

# Schema

| Column | Type | Description |
|---|---|---|
| `TargetBySaleSK` | INT64 | Row key; see [Grain and key](#grain-and-key) for allocation and lifetime. |
| `SaleRepSKLast` | INT64 | SK in [dim_sale_representative_last](/dimension/dim_sale_representative_last.md) matched on EmployeeID + DepartmentID + CompanySK; when that fails, falls back to the employee's row with DepartmentID NULL; NULL if neither exists. |
| `DepartmentSKLast` | INT64 | `DepartmentSK` of the matched dim_sale_representative_last row. |
| `RegionSKLast` | INT64 | RegionSK in dim_region_last, reached through dim_department_last (DepartmentID + CompanySK). |
| `RegionManagerSKLast` | INT64 | RegionManagerSK of that dim_region_last row. |
| `SectionSKLast` | INT64 | SectionSK in dim_section_last, reached through dim_department_last. |
| `SectionManagerSKLast` | INT64 | SectionManagerSK of that dim_section_last row. |
| `DirectorSKLast` | INT64 | DirectorSK of that dim_region_last row. |
| `ReportSK` | INT64 | SK in [dim_report](/dimension/dim_report.md) chosen by the Segment rule (RegionID only, or RegionID plus MarketingGroupID, or RegionID with no group) using the region of the department; NULL when no report group matches. |
| `TargetProductGroupSK` | INT64 | SK of the source target row in [dim_target_product_group](/dimension/dim_target_product_group.md#grain-and-key); see its key contract. |
| `RateTargetSK` | INT64 | SK of the matching rule in dim_rate_target; NULL for an unmatched branch row, even if another branch allocated the same target. |
| `ProductMktSK` | INT64 | SK in [dim_product_mkt](/dimension/dim_product_mkt.md) for the target's MarketingGroupID + SubMarketingID + SegmentID + CompanySK; NULL when not found. |
| `CompanySK` | INT64 | Copied from [dim_target_product_group](/dimension/dim_target_product_group.md).CompanySK. |
| `companyID` | STRING | Company code of the target. |
| `Year` | INT64 | Target year (from dim_target_product_group.Year). |
| `Month` | INT64 | Target month (from dim_target_product_group.Month). |
| `MarketingGroupID` | STRING | Marketing group code of the target. |
| `MarketingGroupName` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub group code. |
| `SubMarketingName` | STRING | Sub group name. |
| `SegmentID` | STRING | Segment code. |
| `SegmentName` | STRING | Segment name. |
| `ChannelTargetGroup` | STRING | Channel group of the target, e.g. `AGENT`, `MDT`, `PS1`, `PS2`, `IMP`, `ASIAN`, `HO`, `Non TargetID`; `MDT` rows feed view_fact_target_product_group_mdt. |
| `TargetID` | STRING | Target code (join key to dim_rate_target). |
| `Amt` | FLOAT64 | The whole target amount before allocation (dim_target_product_group.Amt). Repeated on every employee row of the same target. |
| `Qty` | FLOAT64 | The whole target quantity before allocation. |
| `EmployeeID` | STRING | Employee receiving the share, from dim_rate_target; NULL when no rule matched. |
| `Percent` | FLOAT64 | Share in percent from dim_rate_target (after its MDT recalculation). |
| `DepartmentID` | STRING | Department of the employee, from dim_rate_target. |
| `StartDate` | DATE | Start date of the rate rule (dim_rate_target.StartDate). |
| `EndDate` | DATE | End date of the rate rule (dim_rate_target.EndDate). |
| `CalAmt` | FLOAT64 | Allocated target amount = Amt * Percent / 100. |
| `CalQty` | FLOAT64 | Allocated target quantity = Qty * Percent / 100. |

# How it is built

- Definition: `definitions/dimension/dim_target_product_group_by_sale.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `TargetBySaleSK`.
- Storage options: `{"clusterBy": ["TargetBySaleSK"]}`.
- Reads: [dimension_table.dim_target_product_group](/dimension/dim_target_product_group.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_report](/dimension/dim_report.md), [dimension_table.dim_rate_target](/dimension/dim_rate_target.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_product_mkt, dim_report, dim_rate_target, dim_target_product_group, `update_sk_sale_rep_group` and the `_last` dims dim_sale_representative_last, dim_department_last, dim_region_last, dim_region_manager_last, dim_section_last and dim_section_manager_last.

# Examples

Allocated target per employee for the current year.

```sql
SELECT companyID, EmployeeID, DepartmentID, MarketingGroupID, SUM(CalAmt) AS target_amt, SUM(CalQty) AS target_qty
FROM `databuffet-nonprd.dimension_table.dim_target_product_group_by_sale`
WHERE Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY 1, 2, 3, 4
ORDER BY target_amt DESC
LIMIT 100;
```

Targets with no matched allocation rule in any branch (targets with a successful allocation row excluded).

```sql
SELECT DISTINCT t.companyID, t.Year, t.Month, t.TargetID, t.MarketingGroupID, t.Amt, t.Qty
FROM `databuffet-nonprd.dimension_table.dim_target_product_group_by_sale` AS t
WHERE t.RateTargetSK IS NULL
  AND NOT EXISTS (
    SELECT 1
    FROM `databuffet-nonprd.dimension_table.dim_target_product_group_by_sale` AS allocated
    WHERE allocated.CompanySK = t.CompanySK
      AND allocated.TargetProductGroupSK = t.TargetProductGroupSK
      AND allocated.RateTargetSK IS NOT NULL
  )
ORDER BY t.Year, t.Month, t.TargetID
LIMIT 100;
```
