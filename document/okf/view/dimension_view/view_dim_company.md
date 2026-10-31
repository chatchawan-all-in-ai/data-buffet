---
type: BigQuery View
title: "view_dim_company"
description: "One row = one company (CompanySK) with report-friendly company names and a merged report company code."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_company&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_company
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_company.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_company.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Presentation view over [dim_company](/dimension/dim_company.md). It passes the company columns through and adds `CompanyReportID` (ag01 and ab01 merged into 'ag01') plus the Thai and English legal names used on reports (hard-coded per company in the view). Used by [view_rls_data](/view/process_dataset/view_rls_data.md).

# Grain and key

One row per company (CompanySK / CompanyID; 5 MAC5 companies). Unknown CompanyIDs get 'ไม่มีข้อมูล' / 'No Data' as report names.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Stable SK of the company in dim_company. |
| `CompanyID` | STRING | MAC5 company code (ag01/aa05/ab01/ac02/ak02). |
| `CompanyCode` | STRING | Company code from dim_company (pass-through from mds company master). |
| `CompanyNameTH` | STRING | Company name in Thai from dim_company (pass-through). |
| `CompanyNameEN` | STRING | Company name in English from dim_company (pass-through). |
| `CompanyReportID` | STRING | CompanyID for reporting: 'ag01' for both ag01 and ab01, otherwise CompanyID. |
| `CompanyNameReportTH` | STRING | Hard-coded Thai legal name for reports (ag01/ab01 share one; 'ไม่มีข้อมูล' for any other ID). |
| `CompanyNameReportEN` | STRING | Hard-coded English legal name for reports (ag01/ab01 share one; 'No Data' for any other ID). |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_company.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_company](/dimension/dim_company.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads only dim_company (a stable MERGE-SK dim from mds). The report names are literals in the view.

# Examples

Company list with report names:

```sql
SELECT CompanySK, CompanyID, CompanyReportID, CompanyNameReportEN
FROM `databuffet-nonprd.dimension_view.view_dim_company`
ORDER BY CompanySK
```

Companies rolled up to the report ID:

```sql
SELECT CompanyReportID, ARRAY_AGG(CompanyID) AS companies
FROM `databuffet-nonprd.dimension_view.view_dim_company`
GROUP BY CompanyReportID
```
