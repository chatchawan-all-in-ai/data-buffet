---
type: BigQuery Table
title: "dim_product_mkt_director"
description: "One row = one active MDS marketing-director assignment record, with company, marketing type and validity interval; several records can share a company and type."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_product_mkt_director&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_product_mkt_director
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_product_mkt_director.sqlx"
    title: "Dataform definition (dimension/dim_product_mkt_director.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Maps each top-level marketing type to the director who owns it, with a validity period. Source: mds `mds_data_product_marketing_director_master`.

Read by: [Product_Master_ALL](/view/onetime/Product_Master_ALL.md), [view_dim_product_mkt](/view/dimension_view/view_dim_product_mkt.md).

# Grain and key

One row = one active MDS marketing-director record with its StartDate/EndDate interval. No deduplication or current-date selection is applied, so (CompanyID, TypeMarketingID) can repeat across intervals or overlapping source records. `ProductMktDirectorSK` is `ROW_NUMBER()` over company and type, regenerated every run.

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMktDirectorSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY CompanyID, TypeMarketingID)` over the active mds rows. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `TypeMarketingID` | STRING | Pass-through of mds `TypeMarketingID`, cleaned with `cleanString` (empty string becomes NULL). Marketing type id; joins to [dim_product_mkt](/dimension/dim_product_mkt.md).TypeMarketingID. |
| `TypeMarketing` | STRING | Pass-through of mds `TypeMarketing`, cleaned with `cleanString` (empty string becomes NULL). Marketing type name. |
| `Name` | STRING | Pass-through of mds `Name`, cleaned with `cleanString` (empty string becomes NULL). Director first name. |
| `Surname` | STRING | Pass-through of mds `Surname`, cleaned with `cleanString` (empty string becomes NULL). Director surname. |
| `StartDate` | DATE | First day the director assignment is valid (mds `StartDate`, DATE). |
| `EndDate` | DATE | Last day the assignment is valid (mds `EndDate`, DATE). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_product_marketing_director_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_product_mkt_director.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `ProductMktDirectorSK`.
- Storage options: `{"clusterBy": ["ProductMktDirectorSK"]}`.
- Reads: `mds_dataset.mds_data_product_marketing_director_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Marketing directors valid today per marketing type.

```sql
SELECT CompanyID, TypeMarketingID, TypeMarketing
FROM `databuffet-nonprd.dimension_table.dim_product_mkt_director`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN StartDate AND EndDate;
```

Marketing types with more than one row.

```sql
SELECT CompanyID, TypeMarketingID, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_product_mkt_director`
GROUP BY 1, 2
HAVING n > 1;
```
