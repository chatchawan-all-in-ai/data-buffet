---
type: BigQuery Table
title: "dim_aging_rang"
description: "One row = one aging bucket (min and max days past due, with its report label) defined per company in MDS master data."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_aging_rang&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_aging_rang
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_aging_rang.sqlx"
    title: "Dataform definition (dimension/dim_aging_rang.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Lookup of AR aging buckets (e.g. 0-30 days, 31-60 days) used to classify an invoice by `DayRange`. The bucket boundaries are maintained by the business in the externally loaded `mds_dataset.mds_data_aging_rang_master`; this table copies them and attaches a stable surrogate key and `CompanySK`. Its SK is stored in [dim_aging_history](/dimension/dim_aging_history.md).

Read by: [view_dim_aging](/view/dimension_view/view_dim_aging.md), [view_aging_ri](/view/fact_view/view_aging_ri.md), [export_dim_aging_rang](/view/pub_sub/export_dim_aging_rang.md).

# Grain and key

One row = one aging bucket. Natural key: (`companyID`, `AgingDayMin`, `AgingDayMax`). `AgingRangSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingRangSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. refreshed from dim_company by CompanyID. |
| `companyID` | STRING | MAC5 company code the bucket belongs to (MDS `companyID`, cleaned). Part of the natural key. |
| `AgingDayMin` | INT64 | Lower bound of the bucket in days past due (inclusive; cast to INT64 from MDS). Used as `DayRange BETWEEN AgingDayMin AND AgingDayMax`. |
| `AgingDayMax` | INT64 | Upper bound of the bucket in days past due (inclusive; cast to INT64 from MDS). |
| `ReportName` | STRING | Display label of the bucket as shown on aging reports (MDS `ReportName`). |
| `MdsId` | STRING | `id` of the source row in `mds_dataset.mds_data_aging_rang_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_aging_rang.sqlx` (`type: "operations"`, `hasOutput: true`, tag `dimension_daily`); the operation owns this table.
- Reads: `mds_dataset.mds_data_aging_rang_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed.
# Examples

Buckets per company in order.

```sql
SELECT companyID, AgingRangSK, AgingDayMin, AgingDayMax, ReportName
FROM `databuffet-nonprd.dimension_table.dim_aging_rang`
ORDER BY companyID, AgingDayMin;
```

Classify a day-range value into its bucket (here 45 days past due for company `ag01`).

```sql
SELECT AgingRangSK, ReportName
FROM `databuffet-nonprd.dimension_table.dim_aging_rang`
WHERE CompanySK = (SELECT CompanySK FROM `databuffet-nonprd.dimension_table.dim_company` WHERE CompanyID = 'ag01')
  AND 45 BETWEEN AgingDayMin AND AgingDayMax;
```
