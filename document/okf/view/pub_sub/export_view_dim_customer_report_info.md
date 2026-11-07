---
type: BigQuery View
title: "export_view_dim_customer_report_info"
description: "One row = one customer report name with its segment and TA assignment, exposed for the Pub/Sub export of dimension_view.view_dim_customer_report_info with row_key and row_hash."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=pub_sub&t=export_view_dim_customer_report_info&page=table"
project_id: databuffet-nonprd
dataset_id: pub_sub
table_id: export_view_dim_customer_report_info
tags: ["view", "pub_sub"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/pub_sub/export_view_dim_customer_report_info.sqlx"
    title: "Dataform definition (view/pub_sub/export_view_dim_customer_report_info.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T16:28:08+07:00" }
status: draft
---

# What it is

The Pub/Sub export view of [dimension_view.view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), for the whole table. After each successful `daily_process` run, its publisher sends NEW/UPDATE/DELETE messages based on `row_hash` to topic `export-ta-view_dim_customer_report_info`.

# Grain and key

One row = one customer report name with its segment and TA assignment: key `CustomerReportInfoSK` (unique); `row_key` is the JSON of that key.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerReportInfoSK` | INT64 | Stable SK of the report-info row (MERGE key CompanyID + CustomerReportKey in dim_customer_report_info); joined from view_fact_transcation. |
| `CustomerSegmentSK` | INT64 | Stable SK of the segment in [dim_customer_segment](/dimension/dim_customer_segment.md). |
| `CustomerReportName` | STRING | Report shop name (from MDS Customer_Report_Master / invoice names; matches view_dim_invoice `CustomerReportName`). |
| `ShopOnline` | STRING | Online-shop indicator text from the MDS customer report master (NULL for names that come only from invoices). |
| `FlagPC` | STRING | 'Yes' if the shop is a PC (flag in MDS), else 'No' (NULL becomes 'No'). |
| `TAEmployeeID` | STRING | Employee ID of the TA salesperson (dim_sale_representative_last). |
| `TAEmployeeName` | STRING | Salesperson display name 'name surname (nickname)'; NULL if empty. |
| `TADepartmentID` | STRING | Department ID of the TA (from dim_department_last). |
| `TADepartmentName` | STRING | Department name of the TA. |
| `TASectionID` | STRING | Section ID of the TA (dim_section_last). |
| `TASectionName` | STRING | Section name of the TA. |
| `TASectionManagerID` | STRING | Employee ID of the TA section manager. |
| `TASectionManagerName` | STRING | Section manager display name 'name surname (nickname)'; NULL if empty. |
| `TARegionID` | STRING | Region ID of the TA (dim_region_last). |
| `TARegionName` | STRING | Region name of the TA. |
| `TARegionManagerID` | STRING | Employee ID of the TA region manager. |
| `TARegionManagerName` | STRING | Region manager display name 'name surname (nickname)'; NULL if empty. |
| `TADirectorID` | STRING | Director ID of the TA (dim_director_last). |
| `TADirectorName` | STRING | Director name. |
| `SubDistrict` | STRING | Thai sub-district name (dim_sub_districts.name_th), same method as view_dim_customer. |
| `District` | STRING | Thai district name (dim_districts.name_th). |
| `Province` | STRING | Thai province name (dim_provinces.name_th). |
| `DEBcreditTerm` | INT64 | Credit term in days. |
| `row_key` | STRING | JSON of the key defined in [Grain and key](#grain-and-key), used as the message `primary_key`; never NULL. |
| `row_hash` | INT64 | `FARM_FINGERPRINT` of the JSON of every data column, i.e. of exactly the message `data`. |

# How it is built

- Definition: `definitions/view/pub_sub/export_view_dim_customer_report_info.sqlx` (`type: "view"`, tags `view`, `pub_sub`).
- Reads: [dimension_view.view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md).

# Examples

Duplicate natural keys.

```sql
SELECT row_key, COUNT(*) AS n
FROM `databuffet-nonprd.pub_sub.export_view_dim_customer_report_info`
GROUP BY row_key
HAVING n > 1
```
