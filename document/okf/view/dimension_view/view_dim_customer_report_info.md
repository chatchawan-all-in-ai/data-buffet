---
type: BigQuery View
title: "view_dim_customer_report_info"
description: "One row = one report shop name (CustomerReportName) per company, with its segment, PC flag, online info, responsible sales chain (TA) and address names."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_customer_report_info&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_customer_report_info
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_customer_report_info.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_customer_report_info.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Read-model for the Power BI table 'Dimension Customer Report Info'. [dim_customer_report_info](/dimension/dim_customer_report_info.md) stores only SKs of the TA (responsible salesperson) chain; this view resolves them into IDs and names (department, section, region, section manager, region manager, director, employee) from the `_last` dimensions, converts `FlagPC` to Yes/No and `OnlinePercent` to text with '%', and adds the Thai address names. `CustomerSegmentSK` is passed through for Power BI to relate to `dim_customer_segment`. In Power BI the chain is `view_fact_transcation` (`CustomerReportInfoSK`) -> this view -> `dim_customer_segment`.

# Grain and key

One row per `CustomerReportInfoSK` (company + report name key). All SKs are unique in their target dims, so the LEFT JOINs do not multiply rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerReportInfoSK` | INT64 | Stable SK of the report-info row (MERGE key CompanyID + CustomerReportKey in dim_customer_report_info); joined from view_fact_transcation. |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `CustomerSegmentSK` | INT64 | SK of the segment in `dim_customer_segment` (full rebuild, regenerated daily); passed through for Power BI to relate. |
| `CompanyID` | STRING | MAC5 company code. |
| `CustomerReportName` | STRING | Report shop name (from MDS Customer_Report_Master / invoice names; matches view_dim_invoice `CustomerReportName`). |
| `FlagPC` | STRING | 'Yes' if the shop is a PC (flag in MDS), else 'No' (NULL becomes 'No'). |
| `ShopOnline` | STRING | Online-shop indicator text from MDS (pass-through; values not documented in the repo). |
| `OnlinePercent` | STRING | Online share as text with '%' appended (e.g. '80%'); NULL if no value. |
| `SegmentSource` | STRING | How the segment was assigned: 'MDS' (tier found), 'CHANNEL' (by channel), or 'DEFAULT'. |
| `SegmentDebcode` | STRING | Customer code used to look up the segment (pass-through). |
| `SegmentChannel` | STRING | Channel used for segment assignment (pass-through). |
| `MdsID` | STRING | Id of the source row in the MDS report master (trace column). |
| `DepartmentSK` | INT64 | SK of the TA department in dim_department_last. |
| `SectionSK` | INT64 | SK of the TA section in dim_section_last. |
| `RegionSK` | INT64 | SK of the TA region in dim_region_last. |
| `SectionManagerSK` | INT64 | SK of the TA section manager in dim_section_manager_last. |
| `RegionManagerSK` | INT64 | SK of the TA region manager in dim_region_manager_last. |
| `DirectorSK` | INT64 | SK of the TA director in dim_director_last. |
| `TASource` | STRING | 'DEBSALESP' when the TA department was found from the customer's debsalesp, 'MDT' when from the MDT chain; NULL when none. |
| `TADebcode` | STRING | Customer code used to find the TA (kept to check shops whose TA is empty). |
| `SaleRepSK` | INT64 | SK of the TA employee in dim_sale_representative_last. |
| `ReportDebcode` | STRING | Representative customer code of the report name: COALESCE(SegmentDebcode, TADebcode). |
| `DEBcreditTerm` | INT64 | Credit term in days of the representative customer (pass-through). |
| `InvoiceProvinceSK` | INT64 | SK of the invoice-address province of the representative customer. |
| `InvoiceDistrictSK` | INT64 | SK of the invoice-address district. |
| `InvoiceSubDistrictSK` | INT64 | SK of the invoice-address sub-district. |
| `TADepartmentID` | STRING | Department ID of the TA (from dim_department_last). |
| `TADepartmentName` | STRING | Department name of the TA. |
| `TASectionID` | STRING | Section ID of the TA (dim_section_last). |
| `TASectionName` | STRING | Section name of the TA. |
| `TARegionID` | STRING | Region ID of the TA (dim_region_last). |
| `TARegionName` | STRING | Region name of the TA. |
| `TASectionManagerID` | STRING | Employee ID of the TA section manager. |
| `TASectionManagerName` | STRING | Section manager display name 'name surname (nickname)'; NULL if empty. Personal data. |
| `TARegionManagerID` | STRING | Employee ID of the TA region manager. |
| `TARegionManagerName` | STRING | Region manager display name 'name surname (nickname)'; NULL if empty. Personal data. |
| `TADirectorID` | STRING | Director ID of the TA (dim_director_last). |
| `TADirectorName` | STRING | Director name. |
| `TAEmployeeID` | STRING | Employee ID of the TA salesperson (dim_sale_representative_last). |
| `TAEmployeeName` | STRING | Salesperson display name 'name surname (nickname)'; NULL if empty. Personal data. |
| `SubDistrict` | STRING | Thai sub-district name (dim_sub_districts.name_th), same method as view_dim_customer. |
| `District` | STRING | Thai district name (dim_districts.name_th). |
| `Province` | STRING | Thai province name (dim_provinces.name_th). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_customer_report_info.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), `dimension_table.dim_sub_districts`, `dimension_table.dim_districts`, `dimension_table.dim_provinces`.
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_customer_report_info (MERGE, stable SK, built after the invoice/customer dims) and the `_last` family dims. The `view` tag is not in the nightly run; `view_fact_transcation` is deployed before this view.

# Examples

Shops of one region TA with their segment:

```sql
SELECT CustomerReportName, CustomerSegmentSK, TARegionName, TAEmployeeID, Province
FROM `databuffet-nonprd.dimension_view.view_dim_customer_report_info`
WHERE CompanyID = 'ag01' AND FlagPC = 'Yes'
```

Count of shops by segment source:

```sql
SELECT SegmentSource, COUNT(*) AS shops
FROM `databuffet-nonprd.dimension_view.view_dim_customer_report_info`
GROUP BY SegmentSource
```
