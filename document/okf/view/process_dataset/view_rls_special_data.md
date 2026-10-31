---
type: BigQuery View
title: "view_rls_special_data"
description: "One row = one (employee e-mail, restricted attribute, allowed value) entry of the RLS access map for special and marketing employees, defined in mds rather than by the org hierarchy."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=view_rls_special_data&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: view_rls_special_data
tags: ["view", "process_dataset", "mds"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/process_dataset/view_rls_special_data.sqlx"
    title: "Dataform definition (view/process_dataset/view_rls_special_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The RLS access list for employees whose scope is configured by hand in mds (`mds_data_org_rls_special`) instead of following the sales hierarchy, i.e. employee types `special` and `mkt`. A pipe-separated mds cell (`A|B`) is split into several rows; `ALL` means no restriction; the marketing group/sub-group/segment columns are combined per position. `CustomerID` rows are derived from [rls_customer360](/process/rls_customer360.md): `ALL`, or the customers matching the employee's director/region/section or marketing filters. It has the same three-column shape as [view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md) so one RLS rule can read both.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per distinct (EmployeeEmail, LevelName, LevelValue) after `UNION DISTINCT` of the normal pivot, marketing combination, `ALL` customer rows and customer-filter rows. Only active mds rows (`is_active = TRUE`) of active mapping rows with `employeetype IN ('special','mkt')` are used.

# Schema

| Column | Type | Description |
|---|---|---|
| `EmployeeEmail` | STRING | E-mail of the `special` or `mkt` employee (from `mds_data_org_rls_special` joined to the active `mds_data_org_employee_mapping_center`). |
| `LevelName` | STRING | Restricted attribute: `CompanyID`, `ReportID`, `ReportName`, `DirectorID`, `RegionID`, `SectionID`, the combined `MktGroupID\|MktSubGroupID\|MktSegmentID`, or `CustomerID`. |
| `LevelValue` | STRING | Allowed value; `ALL` means unrestricted for that attribute. For the combined marketing level it is `group\|subgroup\|segment` (e.g. `002\|0022\|00221`); for `CustomerID` it is `ALL` or a customer code (`milCus`). |

# How it is built

- Definition: `definitions/view/process_dataset/view_rls_special_data.sqlx` (`type: "view"`, tags `view`).
- Reads: `mds_dataset.mds_data_org_rls_special` (master data loaded outside this repo), `mds_dataset.mds_data_org_employee_mapping_center` (master data loaded outside this repo), [process_dataset.rls_customer360](/process/rls_customer360.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on the table `process_dataset.rls_customer360` (tag `process`); `mds_dataset.mds_data_org_rls_special` and `mds_data_org_employee_mapping_center` are master data loaded outside this repo.

# Examples

Access entries of one special user.

```sql
SELECT LevelName, LevelValue
FROM `databuffet-nonprd.process_dataset.view_rls_special_data`
WHERE EmployeeEmail = '<employee e-mail>'
ORDER BY LevelName, LevelValue
```

Marketing scope entries for one user.

```sql
SELECT LevelValue
FROM `databuffet-nonprd.process_dataset.view_rls_special_data`
WHERE EmployeeEmail = '<employee e-mail>'
  AND LevelName = 'MktGroupID|MktSubGroupID|MktSegmentID'
```
