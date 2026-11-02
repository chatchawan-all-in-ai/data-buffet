---
type: BigQuery Table
title: "dim_company"
description: "One row = one MAC5 company (ag01, aa05, ab01, ac02, ak02) with its code, Thai and English names and a stable surrogate key."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_company&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_company
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_company.sqlx"
    title: "Dataform definition (dimension/dim_company.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Root company dimension. Almost every other dimension, fact and view carries `CompanySK` from this table (the card lists a few dozen consumers) because MAC5 data is multi-company and keys are only unique within a company. Master data comes from the externally loaded `mds_dataset.mds_data_company_master`. It has no dependencies of its own and runs before the other dimensions.

Used by: [dimension_table.dim_avg_collection_score](/dimension/dim_avg_collection_score.md), [dimension_table.dim_bounce_cheque_score](/dimension/dim_bounce_cheque_score.md), [dimension_table.dim_change_district](/dimension/dim_change_district.md), [dimension_table.dim_channel](/dimension/dim_channel.md), [dimension_table.dim_channel_cost](/dimension/dim_channel_cost.md), [dimension_table.dim_channel_finance](/dimension/dim_channel_finance.md), [dimension_table.dim_channel_sales](/dimension/dim_channel_sales.md), [dimension_table.dim_collection_status](/dimension/dim_collection_status.md), [dimension_table.dim_contact_score](/dimension/dim_contact_score.md), [dimension_table.dim_cost_group](/dimension/dim_cost_group.md), [dimension_table.dim_cost_stk](/dimension/dim_cost_stk.md), [dimension_table.dim_customer_segment](/dimension/dim_customer_segment.md), [dimension_table.dim_department](/dimension/dim_department.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_doctype](/dimension/dim_doctype.md), [dimension_table.dim_grade](/dimension/dim_grade.md), [dimension_table.dim_guarantee](/dimension/dim_guarantee.md), [dimension_table.dim_payment](/dimension/dim_payment.md), [dimension_table.dim_payment_receive_score](/dimension/dim_payment_receive_score.md), [dimension_table.dim_product_master_fc](/dimension/dim_product_master_fc.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_product_mkt_director](/dimension/dim_product_mkt_director.md), [dimension_table.dim_rate_target](/dimension/dim_rate_target.md), and 47 more.

# Grain and key

One row per (`CompanyID`, `CompanyCode`); `CompanySK` is a stable surrogate key (`max_sk + ROW_NUMBER()` for new rows, existing SKs never change). About 5 rows. Matched to MDS first by `MdsId`, then by the natural key.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Stable surrogate key of the company; referenced as `CompanySK` throughout dimension and fact tables. Never regenerated. |
| `CompanyID` | STRING | MAC5 company id such as ag01, aa05, ab01, ac02, ak02; matches `company_id` in validated/curated MAC5 tables. Part of the natural key. |
| `CompanyCode` | STRING | Short company code from MDS (`CompanyCode`): TM = ag01, TE = ac02, IM = ab01, SHANTA = aa05, SWAS = ak02; second part of the natural key. |
| `CompanyNameTH` | STRING | Company name in Thai (MDS `CompanyNameTH`). |
| `CompanyNameEN` | STRING | Company name in English (MDS `CompanyNameEN`). |
| `MdsId` | STRING | Id of the source row in `mds_dataset.mds_data_company_master` (trace column; used to keep the SK when keys are edited and for tombstone deletes). |

# How it is built

- Definition: `definitions/dimension/dim_company.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: `mds_dataset.mds_data_company_master` (master data loaded outside this repo).
- Refresh: MERGE with stable SK (legacy pattern, see [merge-sk-pattern](../../project_wiki/dimension/merge-sk-pattern.md)) in a `type: "operations"` file, tag `dimension_daily`, `dependencies: []`; the target table pre-exists in BigQuery. Source window is `MDS_BACKFILL_DAYS` (1 day) on `updated_at` with `is_active = TRUE`, then a tombstone DELETE of rows whose MDS row is `is_active = FALSE`. Runs first among dimensions.
- Approximate size (BigQuery metadata, 2026-10-31): 5 rows, 899 B.

# Examples

Company SK for each MAC5 company id.

```sql
SELECT CompanySK, CompanyID, CompanyCode, CompanyNameEN
FROM `databuffet-nonprd.dimension_table.dim_company`
ORDER BY CompanyID;
```

Typical join from a dimension that carries `CompanySK`.

```sql
SELECT c.CompanyID, COUNT(*) AS customers
FROM `databuffet-nonprd.dimension_table.dim_customer` AS cu
JOIN `databuffet-nonprd.dimension_table.dim_company` AS c USING (CompanySK)
GROUP BY c.CompanyID;
```
