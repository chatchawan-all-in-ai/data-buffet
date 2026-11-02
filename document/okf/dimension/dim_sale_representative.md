---
type: BigQuery Table
title: "dim_sale_representative"
description: "One row = one sales-representative rule row: an employee in a department (with optional DepCode, CostChannelID, ProvinceID, CustomerFlag and order window) over a StartDate to EndDate interval from the MDS representative master, plus one catch-all row per employee from the MAC5 personnel ledger."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_sale_representative&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_sale_representative
tags: ["dimension", "mds", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_sale_representative.sqlx"
    title: "Dataform definition (dimension/dim_sale_representative.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Rule table that matches a transaction line to a sales representative (and through the department to section, region and director). `fact_transcation` and `view_fact_transcation` join it on `EmployeeID` plus whichever of DepCode / CostChannelID / ProvinceID / CustomerFlag / order window apply, and rank the matches with `seq_condition`. `dim_target_product_group_by_sale_dayofwork` joins it by natural keys and dates, and [dim_sale_representative_last](/dimension/dim_sale_representative_last.md) is its one-row-per-rule snapshot.

Read by: [dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [view_dim_sale_representative](/view/dimension_view/view_dim_sale_representative.md), [view_dim_target_by_agent_dayofwork](/view/dimension_view/view_dim_target_by_agent_dayofwork.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [fact_transcation](/fact/fact_transcation.md).

# Grain and key

UNION ALL of two sources with one `ROW_NUMBER()`. (a) `mds_rep`: active MDS rows (MdsID set) after the CustomerFlag roll-up (flag-only rows, which have CustomerFlag but no DepCode, CostChannelID, ProvinceID or OrderStartDate, are folded into the rule row of the same company, employee, department and overlapping dates; a flag row with no rule row to join is dropped silently). (b) `ledger_rep`: every distinct employee of `validated_mac5.per` with names parsed from `pernamet`, DepartmentID and all rule columns NULL, StartDate 1900-01-01, EndDate 2499-12-31, MdsID NULL. SK ordering: MDS rows first, then ledger, then companyID, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, StartDate, EndDate. `(CompanySK, EmployeeID)` is NOT unique (employee appears in rule rows and in the ledger row). No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `SaleRepSK` | INT64 | Surrogate key, `ROW_NUMBER()` in the order described under grain. Regenerated every run; fact SKs derived from it are rebuilt nightly. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `DepartmentID` | STRING | Department code the employee belongs to for this rule (MDS); NULL on ledger rows. Joins to dim_department.DepartmentID. |
| `EmployeeID` | STRING | Employee (sales person) code; for ledger rows it is `per.percode`. Matches the sales person field of the transaction (`milPer`). |
| `EmployeeName` | STRING | Given name; for ledger rows parsed with a regex from `pernamet` (first token). |
| `EmployeeSurname` | STRING | Surname; for ledger rows the second token of `pernamet`. |
| `EmployeeNickname` | STRING | Nickname; for ledger rows the text in parentheses of `pernamet`. |
| `DepCode` | STRING | MAC5 department code(s) the rule matches against the line department (`milDep`); several codes may be joined by '\|' (for example a pair of codes). NULL on ledger rows and plain employee rows. |
| `CostChannelID` | STRING | Cost channel code the rule matches; rule priority 1 with DepCode, 2 alone (business-flags `seq_condition`). NULL when unused. |
| `ProvinceID` | STRING | Province code the rule matches (priority 4). NULL when unused. |
| `ChangeSectionFlag` | STRING | Flag from MDS marking a change of section: `Yes` on such rows, NULL otherwise; dim_sale_representative_last excludes `Yes` rows from the normal row. |
| `CustomerFlag` | STRING | List of customer codes separated by '\|' that this rule applies to, rolled up from flag-only MDS rows (only onto rows with a DepCode); the rule then also matches those customers (priority 2.5). NULL when none. |
| `StartDate` | DATE | First date the rule is valid (MDS DATE); 1900-01-01 on ledger rows. |
| `EndDate` | DATE | Last date the rule is valid; 2499-12-31 on ledger rows. |
| `OrderStartDate` | DATE | Start of an order-date window: a row with an order window wins the match for bills ordered inside the window (`seq_condition` 0). NULL when no window. |
| `OrderEndDate` | DATE | End of the order-date window; NULL when no window. |
| `MdsID` | STRING | `id` of the source row in `mds_data_sales_representative_master`; NULL for ledger rows. |

# How it is built

- Definition: `definitions/dimension/dim_sale_representative.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `SaleRepSK`.
- Storage options: `{"clusterBy": ["SaleRepSK"]}`.
- Reads: `mds_dataset.mds_data_sales_representative_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md), [validated_mac5.per](/validated/validated_mac5/per.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; reads `mds_data_sales_representative_master`, dim_company and `validated_mac5.per` (via `ref`). Finishes before `dim_sale_representative_last`.
- Approximate size (BigQuery metadata, 2026-10-31): 2,371 rows, 271.4 KB.

# Examples

Rule rows (MDS) of one employee valid today.

```sql
SELECT SaleRepSK, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, CustomerFlag, OrderStartDate, OrderEndDate
FROM `databuffet-nonprd.dimension_table.dim_sale_representative`
WHERE MdsID IS NOT NULL
  AND CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate
  AND companyID = 'ag01'
ORDER BY EmployeeID, DepartmentID;
```

Employees whose only row is the ledger catch-all (no MDS rule).

```sql
SELECT companyID, EmployeeID
FROM `databuffet-nonprd.dimension_table.dim_sale_representative`
GROUP BY 1, 2
HAVING COUNTIF(MdsID IS NOT NULL) = 0;
```
