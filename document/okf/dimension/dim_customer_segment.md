---
type: BigQuery Table
title: "dim_customer_segment"
description: "One row = one customer segment code (Segment1/2/3 with Thai and English descriptions) per company, plus a reserved -1 'Non-Segment' row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_customer_segment&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_customer_segment
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_customer_segment.sqlx"
    title: "Dataform definition (dimension/dim_customer_segment.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Customer-segment master used to classify customers on reports. [dim_customer_report_info](/dimension/dim_customer_report_info.md) matches a customer's segment code to `Segment3` within the company; when nothing matches it uses the company's `DC` segment, and then the `-1` Non-Segment row. Source: mds `mds_data_customer_segment_master`.

Read by: [dim_customer_report_info](/dimension/dim_customer_report_info.md), [export_dim_customer_segment](/view/pub_sub/export_dim_customer_segment.md).

# Grain and key

One row = one segment of a company: key `CustomerSegmentSK` (surrogate for mds rows, regenerated every run); natural key `companyID` + `Segment3`, from active mds rows, plus exactly one sentinel row with `CustomerSegmentSK = -1` (stable).

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerSegmentSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY companyID, Segment3)` over active mds rows. Regenerated every run; the fixed value `-1` is reserved for the 'Non-Segment' fallback row. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. NULL on the -1 row. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. NULL on the -1 row. |
| `Segment1` | STRING | Pass-through of mds `Segment1`, cleaned with `cleanString` (empty string becomes NULL). Top level of the three-level segment code; 'Non-Segment' on the -1 row. |
| `Segment2` | STRING | Pass-through of mds `Segment2`, cleaned with `cleanString` (empty string becomes NULL). Middle segment level; 'Non-Segment' on the -1 row. |
| `Segment3` | STRING | Pass-through of mds `Segment3`, cleaned with `cleanString` (empty string becomes NULL). Leaf segment level (the row key together with company); 'Non-Segment' on the -1 row. |
| `DescriptionThai` | STRING | Pass-through of mds `DescriptionThai`, cleaned with `cleanString` (empty string becomes NULL); `Non-Segment` on the reserved -1 row. Thai description of the segment. |
| `DescriptionEng` | STRING | Pass-through of mds `DescriptionEng`, cleaned with `cleanString` (empty string becomes NULL); `Non-Segment` on the reserved -1 row. English description of the segment. |
| `SortOrder` | INT64 | Display sort order (`castInt64` of mds `SortOrder`); the -1 row uses 99 so it sorts last. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_customer_segment_master`, cleaned with `cleanString`; trace column back to MDS. NULL on the -1 row. |

# How it is built

- Definition: `definitions/dimension/dim_customer_segment.sqlx` (`type: "table"`, tag `dimension_daily`); CTE `segment_master` is the active mds rows UNION ALL the literal `non_segment` row (SK -1).
- `uniqueKey`: `CustomerSegmentSK`.
- Storage options: `{"clusterBy": ["CustomerSegmentSK"]}`.
- Reads: `mds_dataset.mds_data_customer_segment_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Real segments of one company in display order.

```sql
SELECT CustomerSegmentSK, Segment1, Segment2, Segment3, DescriptionEng
FROM `databuffet-nonprd.dimension_table.dim_customer_segment`
WHERE CustomerSegmentSK <> -1 AND CompanyID = 'ag01'
ORDER BY SortOrder;
```

Confirm the fallback row exists.

```sql
SELECT *
FROM `databuffet-nonprd.dimension_table.dim_customer_segment`
WHERE CustomerSegmentSK = -1;
```
