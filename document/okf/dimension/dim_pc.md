---
type: BigQuery Table
title: "dim_pc"
description: "One row = one promoter/PC (product consultant) assignment (employee, MDT branch, marketing group, period) from the MDS PC master, plus a reserved -1 'unknown' row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_pc&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_pc
tags: ["dimension", "mds", "dimension_daily", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_pc.sqlx"
    title: "Dataform definition (dimension/dim_pc.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Roster of PCs (sales promoters) of the MDT (modern trade / saleout) business, assigned to a branch and a marketing group for a period. It feeds the PC views [view_fact_saleout_pc_mdt](/view/fact_view/view_fact_saleout_pc_mdt.md) and [view_fact_target_pc_mdt](/view/fact_view/view_fact_target_pc_mdt.md), which allocate branch saleout/targets to PCs by branch + `MarketingGroupID` (PC assignment is at marketing-group level, not product SK). Source: mds `mds_data_mdt_sales_pc_master`; branch SK from [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md). Contains employee names (personal data).

# Grain and key

One row per assignment: unique per (EmployeeID, BranchCodeMdt, MarketingGroupID) among active mds rows (duplicates collapsed, keeping the most recently updated row), plus one sentinel row with `PcSK = -1`. Key: `PcSK` (surrogate for mds rows, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `PcSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY EmployeeID, BranchCodeMdt, MarketingGroupID)` over deduped mds rows; regenerates every run. `-1` is the reserved unknown PC. |
| `BranchMdtSK` | INT64 | Branch surrogate key from [dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md) matched on `BranchCodeMdt`; `-1` when the branch code is not found (`IFNULL(..., -1)`) and on the -1 row. |
| `BranchCodeMdt` | STRING | Branch code of the MDT store (mds `branch_code`, trimmed, empty to NULL). The -1 row uses the sentinel 'NotBranch' (never NULL, because BI shows NULL IDs as blanks). |
| `EmployeeID` | STRING | PC employee id (mds `employee_id`, trimmed, empty to NULL); the -1 row uses 'NotEmployee'. 'Dummy_NotPC' marks a placeholder assignment. |
| `EmployeeName` | STRING | PC first name (mds `employee_name`); the -1 row is the Thai text for 'unspecified'. Personal data. |
| `EmployeeSurname` | STRING | PC surname (mds `employee_surname`); NULL on the -1 row. Personal data. |
| `EmployeeType` | STRING | Employment type of the PC from mds `employee_type`: `พันธมิตร` (partner staff) or NULL; 'NotType' on the -1 row. |
| `MarketingGroupID` | STRING | Marketing group id the PC is assigned to (mds `marketinggroupid`); the join key to product marketing groups; 'NotGroup' on the -1 row. |
| `MarketingGroupName` | STRING | Marketing group name (mds `marketinggroup`); Thai 'unspecified marketing group' text on the -1 row. |
| `StartDate` | DATE | First day of the assignment (mds `start_date`, DATE); NULL on the -1 row. |
| `EndDate` | DATE | Last day of the assignment (mds `end_date`, DATE); NULL on the -1 row. |
| `IsPlaceholder` | BOOL | TRUE when the row is not a real PC: employee_id empty or 'Dummy_NotPC', or the name is 'ไม่มี PC' / 'Not PC'. NULL on the -1 row. The PC views filter `PcSK <> -1 AND IsPlaceholder = FALSE`. |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. NULL on the -1 row. |

# How it is built

- Definition: `definitions/dimension/dim_pc.sqlx` (`type: "table"`, tags `dimension_daily`, `saleout_daily`).
- `uniqueKey`: `PcSK`.
- Storage options: `{"clusterBy": ["PcSK", "BranchMdtSK", "MarketingGroupID"]}`.
- Reads: `mds_dataset.mds_data_mdt_sales_pc_master` (master data loaded outside this repo), [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md).
- Full daily rebuild (`type: "table"`, tags `dimension_daily` and the saleout daily tag): CTE `pc_source` (active mds rows, QUALIFY dedup on employee_id + branch_code + marketinggroupid keeping latest `updated_at`), `pc_master` (SK + branch SK) UNION ALL the literal `unknown_pc` row. Depends on `dim_sales_branch_mdt`; clustered by `PcSK, BranchMdtSK, MarketingGroupID`.

# Examples

Real PCs assigned to each branch and marketing group today.

```sql
SELECT BranchCodeMdt, MarketingGroupID, COUNT(*) AS pcs
FROM `databuffet-nonprd.dimension_table.dim_pc`
WHERE PcSK <> -1 AND IsPlaceholder = FALSE
  AND CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
GROUP BY 1, 2;
```

Assignment counts for branches not found in dim_sales_branch_mdt.

```sql
SELECT COUNT(*) AS unmatched_branch
FROM `databuffet-nonprd.dimension_table.dim_pc`
WHERE PcSK <> -1 AND BranchMdtSK = -1;
```
