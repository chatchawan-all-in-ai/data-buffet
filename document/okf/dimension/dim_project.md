---
type: BigQuery Table
title: "dim_project"
description: "One row = one customer project profile (project code) per company from the MAC5 quotation-book company/project profiles."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_project&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_project
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_project.sqlx"
    title: "Dataform definition (dimension/dim_project.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Project dimension built from MAC5 `tbook_profilecomp` (the profile of a customer company and its project in the quotation book): company name, type, status, group, history, place and location, project name, source, start and end, plus a computed project duration in days.

Read by: [dim_quotation](/dimension/dim_quotation.md), [export_dim_project](/view/pub_sub/export_dim_project.md).

# Grain and key

One row = one project profile per company: key (`CompanySK`, `projectCode`). `ProjectSK` is a stable surrogate key (existing project codes keep it; new ones get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `projectCode`).

# Schema

| Column | Type | Description |
|---|---|---|
| `ProjectSK` | INT64 | Stable surrogate key; never regenerated. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code. |
| `projectCode` | INT64 | Project code, referenced by the quotation project text. |
| `docNo` | INT64 | Document number of the project profile. |
| `companyName` | STRING | Company name of the project owner or contractor. |
| `companyType` | STRING | Business type of the company (e.g. construction contractor, hotel). |
| `companyStatus` | STRING | Project status colour (`เขียว` = green, `เหลือง` = yellow, `แดง` = red). |
| `companyGroup` | STRING | Company group of the project. |
| `history` | STRING | Background history of the project or company. |
| `place` | STRING | Location of the project. |
| `district` | STRING | District of the project. |
| `province` | STRING | Province of the project. |
| `profileComp` | STRING | Project profile description (e.g. condominium, hotel). |
| `projectName` | STRING | Project name. |
| `projectFrom` | STRING | Source of the project lead. |
| `projectStart` | STRING | Project start date (text). |
| `projectEnd` | STRING | Project end date (text). |
| `projectDay` | INT64 | Project length in days: 0 when `projectStart` is not a valid date; days from start to today (Asia/Bangkok) when `projectEnd` is not a valid date; otherwise end minus start. |

# How it is built

- Definition: `definitions/dimension/dim_project.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.tbook_profilecomp](/validated/validated_mac5/tbook_profilecomp.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `projectCode` + `CompanySK`; updates attribute columns, inserts new projects, no delete. Reads the whole `tbook_profilecomp` each run. Runs after `dim_company`; the target table pre-exists in BigQuery.

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
