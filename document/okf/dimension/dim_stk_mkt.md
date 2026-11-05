---
type: BigQuery Table
title: "dim_stk_mkt"
description: "One row = one MAC5 stock code of a company with its marketing group, sub group and segment, from the MDS product market group master, plus placeholder rows for stock codes MDS does not know yet."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_stk_mkt&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_stk_mkt
tags: ["dimension", "mds", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_stk_mkt.sqlx"
    title: "Dataform definition (dimension/dim_stk_mkt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Maps each MAC5 stock code (StkCode) to the marketing hierarchy (MarketingGroup, SubMarketing, Segment) that product reporting uses. `fact_transcation` takes `StkMktSK` from it, `dim_product_master` and `dim_product_mdt` join it for the group columns, and `view_fact_transcation` exposes the group names.

Read by: [dim_product_master](/dimension/dim_product_master.md), [dim_product_mdt](/dimension/dim_product_mdt.md), [fact_transcation](/fact/fact_transcation.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one stock code: key `StkMktSK`; two blocks UNION ALL'd and numbered once: (1) active MDS rows (`MdsID` set); (2) 'Waiting Master' placeholders, one per distinct stock code of `validated_mac5.stk` that has no MDS row for the same StkCode + companyID (`MdsID` NULL, MarketingGroupID '999', SubMarketingID '9999', SegmentID '99999', all names 'Waiting Master', Size and Color NULL). SK order puts MDS rows first, then placeholders, then companyID, StkCode. Natural key `(companyID, StkCode)` (plus Size/Color when MDS carries several variants; uniqueness is not enforced).

# Schema

| Column | Type | Description |
|---|---|---|
| `StkMktSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by (MDS rows before placeholders), companyID, StkCode. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (ag01, aa05, ab01, ac02, ak02 style), cleaned with `cleanString`; natural join key with dim_company.companyID. |
| `StkCode` | STRING | MAC5 stock (product) code; join key to the product code of order/invoice lines (`milstk` in transactions). |
| `Size` | STRING | Product size attribute from MDS; NULL for placeholders. |
| `Color` | STRING | Product colour attribute from MDS; NULL for placeholders. |
| `MarketingGroupID` | STRING | Marketing group code (level 2 of the marketing hierarchy); '999' for placeholders. |
| `MarketingGroup` | STRING | Name of the marketing group; 'Waiting Master' for placeholders. |
| `SubMarketingID` | STRING | Sub marketing group code (level 3); '9999' for placeholders. |
| `SubMarketing` | STRING | Name of the sub marketing group; 'Waiting Master' for placeholders. |
| `SegmentID` | STRING | Segment code (level 4); '99999' for placeholders. |
| `Segment` | STRING | Segment name; 'Waiting Master' for placeholders. |
| `MdsID` | STRING | `id` of the source row in `mds_data_product_market_group_by_product_id_master`, cleaned with `cleanString`; trace column back to MDS. NULL for 'Waiting Master' rows. |

# How it is built

- Definition: `definitions/dimension/dim_stk_mkt.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `StkMktSK`.
- Storage options: `{"clusterBy": ["StkMktSK"]}`.
- Reads: `mds_dataset.mds_data_product_market_group_by_product_id_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md), [validated_mac5.stk](/validated/validated_mac5/stk.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Stock codes that MDS has not classified yet.

```sql
SELECT companyID, StkCode
FROM `databuffet-nonprd.dimension_table.dim_stk_mkt`
WHERE MdsID IS NULL
ORDER BY companyID, StkCode;
```

Marketing group coverage per company.

```sql
SELECT companyID, MarketingGroupID, MarketingGroup, COUNT(*) AS stock_codes
FROM `databuffet-nonprd.dimension_table.dim_stk_mkt`
GROUP BY 1, 2, 3
ORDER BY 1, stock_codes DESC;
```
