---
type: BigQuery Table
title: "dim_waterpac"
description: "One row = one WaterPac (pump variant) code of a company with its name and brand, from the MDS WaterPac master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_waterpac&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_waterpac
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_waterpac.sqlx"
    title: "Dataform definition (dimension/dim_waterpac.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Lookup of WaterPac codes used to label pump-type products. `view_dim_product_master` extracts the suffix after the slash that starts with P or U from the product code (or code 1, or the MAC5 description), matches it on `UPPER(WaterPacCode)` and, for products in segment 00111 or 00112, uses `WaterPacName` as the `PumpSegment`.

Read by: [view_dim_product_master](/view/dimension_view/view_dim_product_master.md).

# Grain and key

One row per active MDS row, ordered and SK-numbered by CompanyID, WaterPacCode. Natural key `(CompanyID, WaterPacCode)`. No -1 row.

# Schema

| Column | Type | Description |
|---|---|---|
| `WaterPacSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by CompanyID, WaterPacCode. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on companyID; NULL if no match. |
| `CompanyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `WaterPacCode` | STRING | WaterPac code; matched case-insensitively to the product-code suffix extracted by `view_dim_product_master`. |
| `WaterPacName` | STRING | Display name of the WaterPac, used as `PumpSegment` for water-pac segments. |
| `Brand` | STRING | Pump brand of the WaterPac set as entered in MDS, e.g. `HITACHI`, `MITSUBISHI`, `CMB`, `DAB`, `RINNAI`. |
| `MdsID` | STRING | `id` of the source row in `mds_data_waterpac_master`; trace column. |

# How it is built

- Definition: `definitions/dimension/dim_waterpac.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `WaterPacSK`.
- Storage options: `{"clusterBy": ["WaterPacSK"]}`.
- Reads: `mds_dataset.mds_data_waterpac_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`), tag `dimension_daily`; `CREATE OR REPLACE` each run from `mds_dataset` (loaded outside this repo). Runs after `dim_company`. Reads `mds_data_waterpac_master`; it is the reference implementation of the full-rebuild pattern (`dim_waterpac.sqlx`).
- Approximate size (BigQuery metadata, 2026-10-31): 229 rows, 18.7 KB.

# Examples

WaterPac codes and brands for one company.

```sql
SELECT WaterPacCode, WaterPacName, Brand
FROM `databuffet-nonprd.dimension_table.dim_waterpac`
WHERE CompanyID = 'ag01'
ORDER BY WaterPacCode;
```
