---
type: BigQuery Table
title: "dim_collection_status"
description: "One row = one collection follow-up record (company, year, month, customer) with the action, justification and responsible person, from the MDS collection-status master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_collection_status&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_collection_status.sqlx"
    title: "Dataform definition (dimension/dim_collection_status.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Manually maintained collection status notes for customers with overdue balances: what action is being taken, why, and who is responsible, per month. [fact_mir_vs](/fact/fact_mir_vs.md) and [fact_mir_rs](/fact/fact_mir_rs.md) store its `CollectSK` for the AR/receipt chain. Source: mds `mds_data_collection_status_master`.

# Grain and key

One row per active mds record, intended as (company, Year, Month, CustomerID). Key: `CollectSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `CollectSK` | INT64 | `CollectSK` is `ROW_NUMBER() OVER(ORDER BY CompanyID, Year, Month, CustomerID)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `Year` | INT64 | Calendar year of the follow-up record (`castInt64` of mds `Year`; fails the run on a non-numeric value). |
| `Month` | INT64 | Month number 1-12 of the follow-up record (`castInt64` of mds `Month`). |
| `CustomerID` | INT64 | Customer identifier as INT64 (`castInt64` of mds `CustomerID`); presumably the numeric customer code used by the AR facts (inferred from the name, not documented). |
| `CustomerName` | STRING | Customer name as typed in MDS (`cleanString`); descriptive. |
| `Actions` | STRING | Collection action taken or planned (free text from MDS). |
| `Justification` | STRING | Reason or explanation recorded for the status (free text from MDS). |
| `Responsible` | STRING | Person or team responsible for the collection follow-up (free text from MDS; contains personal names, not shown here). |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_collection_status.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `CollectSK`.
- Storage options: `{"clusterBy": ["CollectSK"]}`.
- Reads: `mds_dataset.mds_data_collection_status_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows; runs after dim_company. Stored-SK consumers `fact_mir_vs`/`fact_mir_rs` are daily full rebuilds, which keeps the regenerating SK consistent.
- Approximate size (BigQuery metadata, 2026-10-31): 538 rows, 138.4 KB.

# Examples

Collection notes for one company and month.

```sql
SELECT CompanyID, Year, Month, CustomerID, Actions, Justification
FROM `databuffet-nonprd.dimension_table.dim_collection_status`
WHERE CompanyID = 'ag01' AND Year = 2026 AND Month = 10;
```

Follow-up record counts per company and year-month.

```sql
SELECT CompanyID, Year, Month, COUNT(*) AS records
FROM `databuffet-nonprd.dimension_table.dim_collection_status`
GROUP BY 1, 2, 3
ORDER BY 1, 2, 3;
```
