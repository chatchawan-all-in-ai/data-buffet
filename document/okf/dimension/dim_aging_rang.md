---
type: BigQuery Table
title: "dim_aging_rang"
description: "One row = one aging bucket (min and max days past due, with its report label) defined per company in MDS master data."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_aging_rang&page=table"
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_aging_rang.sqlx"
    title: "Dataform definition (dimension/dim_aging_rang.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Lookup of AR aging buckets (e.g. 0-30 days, 31-60 days) that [view_dim_aging](/view/dimension_view/view_dim_aging.md) and [view_aging_ri](/view/fact_view/view_aging_ri.md) use to classify an invoice by `DayRange`. The bucket boundaries are maintained by the business in the externally loaded `mds_dataset.mds_data_aging_rang_master`; this table copies them and attaches a stable surrogate key and `CompanySK`. Its SK is frozen into [dim_aging_history](/dimension/dim_aging_history.md), which is why this is one of the two legacy MERGE dims.

Used by: [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md).

# Grain and key

One row per (`companyID`, `AgingDayMin`, `AgingDayMax`) bucket; `AgingRangSK` is the surrogate key (`max_sk + ROW_NUMBER()` for new rows, existing SKs never change). Rows are matched to MDS first by `MdsId` and then by the natural key (company + min + max), so editing a label keeps the SK. About 8 rows in total.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingRangSK` | INT64 | Stable surrogate key of the bucket. Assigned once (MERGE with `max_sk`) and never regenerated. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), joined on `companyID`. Written at insert only (not updated by the MATCHED branch). |
| `companyID` | STRING | MAC5 company code the bucket belongs to (MDS `companyID`, cleaned). Part of the natural key. |
| `AgingDayMin` | INT64 | Lower bound of the bucket in days past due (inclusive; cast to INT64 from MDS). Used as `DayRange BETWEEN AgingDayMin AND AgingDayMax`. |
| `AgingDayMax` | INT64 | Upper bound of the bucket in days past due (inclusive; cast to INT64 from MDS). |
| `ReportName` | STRING | Display label of the bucket as shown on aging reports (MDS `ReportName`). |
| `MdsId` | STRING | Id of the source row in `mds_dataset.mds_data_aging_rang_master` (trace column; used to keep the SK when the natural key is edited and for tombstone deletes). |

# How it is built

- Definition: `definitions/dimension/dim_aging_rang.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: `mds_dataset.mds_data_aging_rang_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK (legacy pattern, see [merge-sk-pattern](../../project_wiki/dimension/merge-sk-pattern.md)) in a `type: "operations"` file, tag `dimension_daily`; the target table pre-exists in BigQuery. Source window is `MDS_BACKFILL_DAYS` (1 day) on `updated_at` with `is_active = TRUE`, then a tombstone DELETE of rows whose MDS row is `is_active = FALSE`. Runs after `dim_company`.
- Approximate size (BigQuery metadata, 2026-10-31): 8 rows, 975 B.

# Examples

Buckets per company in order.

```sql
SELECT companyID, AgingRangSK, AgingDayMin, AgingDayMax, ReportName
FROM `databuffet-nonprd.dimension_table.dim_aging_rang`
ORDER BY companyID, AgingDayMin;
```

Classify a day-range value into its bucket (here 45 days past due for one company SK).

```sql
SELECT AgingRangSK, ReportName
FROM `databuffet-nonprd.dimension_table.dim_aging_rang`
WHERE CompanySK = 1 AND 45 BETWEEN AgingDayMin AND AgingDayMax;
```
