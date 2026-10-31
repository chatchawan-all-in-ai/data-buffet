---
type: BigQuery Table
title: "dim_sale_representative_last"
description: "One row = one sales-representative rule (latest interval per company, department, employee, DepCode, CostChannelID, ProvinceID and order window), collapsed to a single normal row per employee when one exists, plus one ledger row per employee with no department."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_sale_representative_last&page=table"
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_sale_representative_last.sqlx"
    title: "Dataform definition (dimension/dim_sale_representative_last.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Latest-row snapshot of [dim_sale_representative](/dimension/dim_sale_representative.md) used for the `*Last` columns (the current sales rep of a customer or sale, independent of date): `view_fact_transcation`, `dim_target_product_group_by_sale`, customer-report info, org-center members. It also carries hierarchy SKs (department, section, section manager, region, region manager, director).

Read by: [dim_target_product_group_by_sale](/dimension/dim_target_product_group_by_sale.md), [org_center_member](/org_center/org_center_member.md), [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [view_dim_sale_representative_last](/view/dimension_view/view_dim_sale_representative_last.md), [view_dim_target_by_agent](/view/dimension_view/view_dim_target_by_agent.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [Model_Target_DayOfWork](/view/onetime/Model_Target_DayOfWork.md), [dim_customer_report_info](/dimension/dim_customer_report_info.md).

# Grain and key

Built in three CTEs. `raw`: rows of dim_sale_representative with DepartmentID not NULL, latest EndDate/StartDate kept per `(CompanyID, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, OrderStartDate, OrderEndDate)`. `agg_normal`: rows with no DepCode, CostChannelID, ProvinceID, ChangeSectionFlag or OrderStartDate, one per `(CompanyID, EmployeeID)`. `final`: all order-window rows, plus other rows only for employees that have no normal row, plus the normal rows. Then `post_operations` MERGEs one ledger row per employee from `validated_mac5.per` with DepartmentID NULL and NULL dates/hierarchy, SK = MAX(SaleRepSK) + row number. The table has no MdsID column. `SaleRepSK` is renumbered here (ordered by CompanySK, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID) and is not dim_sale_representative.SaleRepSK.

# Schema

| Column | Type | Description |
|---|---|---|
| `SaleRepSK` | INT64 | Surrogate key of this snapshot: `ROW_NUMBER()` ordered by CompanySK, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID; ledger rows get MAX + row number in post_operations. Regenerated every run. |
| `DepartmentSK` | INT64 | SK in dim_department_last for the row's DepartmentID. Built NULL, backfilled by `update_sk_sale_rep_group`; stays NULL on ledger rows (no DepartmentID). |
| `SectionSK` | INT64 | SK in dim_section_last, copied from the department by `update_sk_sale_rep_group`; NULL until then. |
| `SectionManagerSK` | INT64 | SK in dim_section_manager_last, from the department by `update_sk_sale_rep_group`; NULL until then. |
| `RegionSK` | INT64 | SK in dim_region_last, from the department by `update_sk_sale_rep_group`; NULL until then. |
| `RegionManagerSK` | INT64 | SK in dim_region_manager_last, from the department by `update_sk_sale_rep_group`; NULL until then. |
| `DirectorSK` | INT64 | SK in dim_director_last, from the department by `update_sk_sale_rep_group`; NULL until then. |
| `CompanySK` | INT64 | Company SK re-joined from dim_company by companyID. |
| `companyID` | STRING | Company code from dim_company. |
| `DepartmentID` | STRING | Department code of the kept rule row; NULL on ledger rows. |
| `EmployeeID` | STRING | Employee (sales person) code. |
| `EmployeeName` | STRING | Given name (MDS or parsed from the MAC5 ledger name; the MERGE refreshes names on matching ledger rows). |
| `EmployeeSurname` | STRING | Surname (same source as EmployeeName). |
| `EmployeeNickname` | STRING | Nickname (same source). |
| `DepCode` | STRING | MAC5 department code(s) of the rule (possibly several joined by '\|'); NULL on normal and ledger rows. |
| `CostChannelID` | STRING | Cost channel code of the rule; NULL when unused. |
| `ProvinceID` | STRING | Province code of the rule; NULL when unused. |
| `ChangeSectionFlag` | STRING | Section-change flag copied from dim_sale_representative (exact values not documented in the repo). |
| `CustomerFlag` | STRING | '\|' separated customer list copied from dim_sale_representative; NULL on ledger rows. |
| `StartDate` | DATE | Start of the kept validity interval; NULL on ledger rows. |
| `EndDate` | DATE | End of the kept validity interval; NULL on ledger rows. |
| `OrderStartDate` | DATE | Start of the order-date window (rows with a window are always kept); NULL otherwise. |
| `OrderEndDate` | DATE | End of the order-date window; NULL otherwise. |

# How it is built

- Definition: `definitions/dimension/dim_sale_representative_last.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `SaleRepSK`.
- Storage options: `{"clusterBy": ["SaleRepSK"]}`.
- Reads: [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_company](/dimension/dim_company.md), [validated_mac5.per](/validated/validated_mac5/per.md).
- Full daily rebuild (`type: "table"`) from dim_sale_representative + dim_company, tag `dimension_daily`, then a `post_operations` MERGE inserts the ledger employees; the hierarchy SKs are filled afterwards by `update_sk_sale_rep_group`, which depends on this table.
- Approximate size (BigQuery metadata, 2026-10-31): 2,242 rows, 227.4 KB.

# Examples

Latest rule rows with their department keys filled in.

```sql
SELECT SaleRepSK, companyID, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, DepartmentSK, RegionSK
FROM `databuffet-nonprd.dimension_table.dim_sale_representative_last`
WHERE DepartmentID IS NOT NULL AND companyID = 'ag01'
ORDER BY EmployeeID, DepartmentID;
```

Rows without hierarchy keys after backfill.

```sql
SELECT COUNTIF(DepartmentSK IS NULL) AS missing_department_sk, COUNT(*) AS total_rows
FROM `databuffet-nonprd.dimension_table.dim_sale_representative_last`
WHERE DepartmentID IS NOT NULL;
```
