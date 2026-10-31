---
type: BigQuery View
title: "view_rls_sale_data"
description: "One row = one (employee e-mail, restricted attribute, allowed value) entry of the RLS access map for sales employees, combining the org hierarchy with the customers of their sections."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=view_rls_sale_data&page=table"
tags: ["view", "process_dataset", "mds"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/process_dataset/view_rls_sale_data.sqlx"
    title: "Dataform definition (view/process_dataset/view_rls_sale_data.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The final RLS access list for employees of type `sales`. It joins [view_rls_data](/view/process_dataset/view_rls_data.md) (org hierarchy by employee id) to the mds employee mapping to get the e-mail, then adds `CustomerID` rows: every customer in [rls_customer360](/process/rls_customer360.md) whose pipe-separated `SectionID` list contains a section the employee may see. Power BI RLS (Customer360 and sales models) filters on `EmployeeEmail`. Employees of type `special` or `mkt` come from [view_rls_special_data](/view/process_dataset/view_rls_special_data.md).

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per distinct (EmployeeEmail, LevelName, LevelValue) (the UNION ALL of `rls_data` and `rls_customer`, each `DISTINCT`). Only active mapping rows with an employee id and e-mail and `LOWER(TRIM(employeetype)) = 'sales'` are used.

# Schema

| Column | Type | Description |
|---|---|---|
| `EmployeeEmail` | STRING | E-mail of the sales employee from `mds_data_org_employee_mapping_center` (active rows with `employeetype = 'sales'`); the identity matched by Power BI RLS. |
| `LevelName` | STRING | Restricted attribute: `DirectorID`, `RegionID`, `SectionID`, `CompanyID` (from `view_rls_data`) or `CustomerID` (added here). |
| `LevelValue` | STRING | Allowed value for that attribute: an org id, the company report id, or a customer code (`milCus`). |

# How it is built

- Definition: `definitions/view/process_dataset/view_rls_sale_data.sqlx` (`type: "view"`, tags `view`).
- Reads: `mds_dataset.mds_data_org_employee_mapping_center` (master data loaded outside this repo), [process_dataset.view_rls_data](/view/process_dataset/view_rls_data.md), [process_dataset.rls_customer360](/process/rls_customer360.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `view_rls_data` and the table `process_dataset.rls_customer360` (tag `process`, built after `fact_transcation`); `mds_dataset.mds_data_org_employee_mapping_center` is loaded outside this repo.

# Examples

Access entries of one user.

```sql
SELECT LevelName, LevelValue
FROM `databuffet-nonprd.process_dataset.view_rls_sale_data`
WHERE EmployeeEmail = '<employee e-mail>'
ORDER BY LevelName, LevelValue
```

Number of entries per restricted attribute.

```sql
SELECT LevelName, COUNT(*) AS entries, COUNT(DISTINCT EmployeeEmail) AS employees
FROM `databuffet-nonprd.process_dataset.view_rls_sale_data`
GROUP BY LevelName
```
