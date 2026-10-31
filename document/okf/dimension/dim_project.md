---
type: BigQuery Table
title: "dim_project"
description: "One row = one customer project profile (project code) per company from the MAC5 quotation-book company/project profiles."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_project&page=table"
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_project.sqlx"
    title: "Dataform definition (dimension/dim_project.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Project dimension built from MAC5 `tbook_profilecomp` (the profile of a customer company and its project in the quotation book): company name, type, status, group, history, place and location, project name, source, start and end, plus a computed project duration in days. It is used to tag quotations with a project: [dim_quotation](/dimension/dim_quotation.md) takes `ProjectSK` from it by matching the project code parsed from the quotation text.

Used by: [dimension_table.dim_quotation](/dimension/dim_quotation.md).

# Grain and key

One row per (`CompanySK`, `projectCode`). `ProjectSK` is a stable surrogate key (existing project codes keep it; new ones get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `projectCode`).

# Schema

| Column | Type | Description |
|---|---|---|
| `ProjectSK` | INT64 | Stable surrogate key; never regenerated. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `projectCode` | INT64 | Numeric project code (`tbook_profilecomp.projectcode`); the natural key with company, matched by quotations through the numeric prefix in the project text. |
| `docNo` | INT64 | Document number of the profile (`docno`). |
| `companyName` | STRING | Name of the customer company owning the project (`compname`). |
| `companyType` | STRING | Type of the customer company (`typecomp`); code list not documented in the repo. |
| `companyStatus` | STRING | Status of the customer company (`statuscomp`); code list not documented in the repo. |
| `companyGroup` | STRING | Group of the customer company (`compgroup`). |
| `history` | STRING | Free-text history of the profile (`history`). |
| `place` | STRING | Project/company place text (`place`). |
| `district` | STRING | District text (`district`) of the place; free text, not linked to the geography dims. |
| `province` | STRING | Province text (`province`) of the place; free text, not linked to the geography dims. |
| `profileComp` | STRING | Profile text of the company (`profilecomp`). |
| `projectName` | STRING | Project name (`projectname`). |
| `projectFrom` | STRING | Origin/source of the project (`projectfrom`); Meaning not documented in the repo. |
| `projectStart` | STRING | Project start (`pjstart`), kept as STRING; parsed with SAFE_CAST AS DATE for `projectDay`. |
| `projectEnd` | STRING | Project end (`pjend`), kept as STRING. |
| `projectDay` | INT64 | Project length in days: 0 when `projectStart` is not a valid date; days from start to today (Asia/Bangkok) when `projectEnd` is not a valid date; otherwise end minus start. |

# How it is built

- Definition: `definitions/dimension/dim_project.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.tbook_profilecomp](/validated/validated_mac5/tbook_profilecomp.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `projectCode` + `CompanySK`; updates attribute columns, inserts new projects, no delete. Reads the whole `tbook_profilecomp` each run. Runs after `dim_company`; the target table pre-exists in BigQuery.
- Approximate size (BigQuery metadata, 2026-10-31): 8,777 rows, 2.5 MB.

# Examples

Projects per company and status.

```sql
SELECT companyID, companyStatus, COUNT(*) AS projects, AVG(projectDay) AS avg_days
FROM `databuffet-nonprd.dimension_table.dim_project`
GROUP BY companyID, companyStatus
ORDER BY companyID, projects DESC;
```

Quotations linked to a project (via ProjectSK).

```sql
SELECT p.projectCode, p.projectName, COUNT(*) AS quotations
FROM `databuffet-nonprd.dimension_table.dim_project` AS p
JOIN `databuffet-nonprd.dimension_table.dim_quotation` AS q USING (ProjectSK)
GROUP BY p.projectCode, p.projectName
ORDER BY quotations DESC
LIMIT 20;
```
