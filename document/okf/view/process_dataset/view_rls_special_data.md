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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The RLS access list for employees whose scope is configured by hand in mds (`mds_data_org_rls_special`) instead of following the sales hierarchy, i.e. employee types `special` and `mkt`. A pipe-separated mds cell (`A|B`) is split into several rows; `ALL` means no restriction; the marketing group/sub-group/segment columns are combined per position. `CustomerID` rows are derived from [rls_customer360](/process/rls_customer360.md): `ALL`, or the customers matching the employee's director/region/section or marketing filters. It has the same three columns as [view_rls_sale_data](/view/process_dataset/view_rls_sale_data.md).

# Grain and key

One row = one allowed value of one attribute of one special or marketing employee: intended key `EmployeeEmail`, `LevelName`, `LevelValue`. Rows are distinct on `EmployeeID`, `EmployeeEmail`, `EmployeeType`, `LevelName`, `LevelValue` (`UNION DISTINCT` of the normal pivot, marketing combination, `ALL` customer rows and customer-filter rows) before the view keeps three columns, so the key repeats only if one e-mail has several `EmployeeID` or type values. Only active mds rows (`is_active = TRUE`) of active mapping rows with `employeetype IN ('special','mkt')` are used.

`CustomerID` rows follow `employeetype` and the mds `FlagCustomer` flag (NULL = false):

- `special` with `FlagCustomer` false, or with director, region and section all `ALL`: one `CustomerID` row with `ALL`.
- `special` with `FlagCustomer` true and a director, region or section list that is not all `ALL`: the customers of [rls_customer360](/process/rls_customer360.md) whose `DirectorID`, `RegionID` and `SectionID` lists match the employee's lists (a column set to `ALL` matches any value).
- `mkt` (employee type `MKT`): one `CustomerID` row with `ALL` when the marketing combination is `ALL|ALL|ALL`; otherwise the customers whose `ProductMkt` (`group:sub group:segment`) matches a marketing combination. `MktGroupID = 'ALL'` bypasses group, sub-group and segment checks; otherwise the group must match. `MktSubGroupID = 'ALL'` bypasses sub-group and segment checks within that group; otherwise the sub-group must match. The segment must match unless an ancestor or `MktSegmentID` is `ALL`.

# Schema

| Column | Type | Description |
|---|---|---|
| `EmployeeEmail` | STRING | E-mail of the `special` or `mkt` employee (from `mds_data_org_rls_special` joined to the active `mds_data_org_employee_mapping_center`). |
| `LevelName` | STRING | Restricted attribute: `CompanyID`, `ReportID`, `ReportName`, `DirectorID`, `RegionID`, `SectionID`, the combined `MktGroupID\|MktSubGroupID\|MktSegmentID`, or `CustomerID`. |
| `LevelValue` | STRING | Allowed value; `ALL` means unrestricted for that attribute. For the combined marketing level it is `group\|subgroup\|segment`; for `CustomerID` it is `ALL` or a customer code (`milCus`). |

# How it is built

- Definition: `definitions/view/process_dataset/view_rls_special_data.sqlx` (`type: "view"`, tags `view`).
- Reads: `mds_dataset.mds_data_org_rls_special` (master data loaded outside this repo), `mds_dataset.mds_data_org_employee_mapping_center` (master data loaded outside this repo), [process_dataset.rls_customer360](/process/rls_customer360.md).

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
