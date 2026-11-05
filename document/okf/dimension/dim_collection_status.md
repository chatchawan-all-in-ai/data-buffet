---
type: BigQuery Table
title: "dim_collection_status"
description: "One row = one collection follow-up record (company, year, month, customer) with the action, justification and responsible person, from the MDS collection-status master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_collection_status&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_collection_status
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_collection_status.sqlx"
    title: "Dataform definition (dimension/dim_collection_status.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Manually maintained collection status notes for customers with overdue balances: what action is being taken, why, and who is responsible, per month. [fact_mir_vs](/fact/fact_mir_vs.md) and [fact_mir_rs](/fact/fact_mir_rs.md) store its `CollectSK` for the AR/receipt chain. Source: mds `mds_data_collection_status_master`.

Read by: [fact_mir_vs](/fact/fact_mir_vs.md), [fact_mir_rs](/fact/fact_mir_rs.md).

# Grain and key

One row = one active mds record (company, Year, Month, CustomerID): key `CollectSK` (surrogate, regenerated every run).

# Schema

| Column | Type | Description |
|---|---|---|
| `CollectSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY CompanyID, Year, Month, CustomerID)` over the active mds rows. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `Year` | INT64 | Calendar year of the follow-up record (`castInt64` of mds `Year`). |
| `Month` | INT64 | Month number 1-12 of the follow-up record (`castInt64` of mds `Month`). |
| `CustomerID` | INT64 | MAC5 customer code as INT64 (`castInt64` of mds `CustomerID`); [fact_mir_rs](/fact/fact_mir_rs.md) and [fact_mir_vs](/fact/fact_mir_vs.md) join it to the receipt or billing customer `mircus` (cast to STRING) with company, year and month. |
| `CustomerName` | STRING | Customer name as typed in MDS (`cleanString`); descriptive. |
| `Actions` | STRING | Collection action taken or planned (free text from MDS). |
| `Justification` | STRING | Reason or explanation recorded for the status (free text from MDS). |
| `Responsible` | STRING | Person or team responsible for the collection follow-up (free text from MDS). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_collection_status_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_collection_status.sqlx` (`type: "table"`, tag `dimension_daily`).
- `uniqueKey`: `CollectSK`.
- Storage options: `{"clusterBy": ["CollectSK"]}`.
- Reads: `mds_dataset.mds_data_collection_status_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

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
