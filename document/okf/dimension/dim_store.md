---
type: BigQuery Table
title: "dim_store"
description: "One row = one warehouse or branch store (StoreCode) of a company from the MAC5 stock-location master, plus a reserved -1 row for unknown stores."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_store&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_store
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_store.sqlx"
    title: "Dataform definition (dimension/dim_store.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Warehouse (คลัง) dimension built from `validated_mac5.sto`. `StoreGroup` is the MAC5 warehouse group code (`sto.stogroup`) and `ReportStore` is the report slicer that keeps the groups KK, LP, HY, UB and PK and collapses every other group into one bucket named KTB. The three store-grain facts `fact_order_store`, `fact_invoice_store` and `fact_backlog_store` join it through `milSto` / `cpsSto`.

Read by: [fact_backlog_store](/fact/fact_backlog_store.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_order_store](/fact/fact_order_store.md).

# Grain and key

One row = one warehouse: key `(company_id, stocode)` of `validated_mac5.sto`, restricted to companies ag01 and ab01; `StoreSK` is `ROW_NUMBER()` ordered by company_id, stocode. Plus one reserved row `StoreSK = -1` (CompanySK, companyID, StoreCode, StoreGroup all NULL; StoreNameT 'ไม่ระบุคลัง', StoreNameE 'Unknown', ReportStore 'KTB') for store codes not found in `sto`.

# Schema

| Column | Type | Description |
|---|---|---|
| `StoreSK` | INT64 | Surrogate key, `ROW_NUMBER()` ordered by company_id, stocode; -1 for the unknown-store row. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. NULL on the -1 row. |
| `companyID` | STRING | Company code, from `sto.company_id`; NULL on the -1 row. |
| `StoreCode` | STRING | Warehouse code; NULL on the -1 row. |
| `StoreGroup` | STRING | Warehouse group code (`sto.stogroup`); NULL on the -1 row. |
| `StoreNameT` | STRING | Thai name of the warehouse; 'ไม่ระบุคลัง' on the -1 row. |
| `StoreNameE` | STRING | English name of the warehouse; 'Unknown' on the -1 row. |
| `ReportStore` | STRING | Report slicer: `StoreGroup` as is when its lower-case value is one of kk, pk, lp, ub, hy; otherwise (including NULL group) the bucket 'KTB'. The -1 row is 'KTB'. |

# How it is built

- Definition: `definitions/dimension/dim_store.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `StoreSK`.
- Storage options: `{"clusterBy": ["StoreSK"]}`.
- Reads: [validated_mac5.sto](/validated/validated_mac5/sto.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company. The hand-written -1 row is UNION ALL'd in the same statement.

# Examples

Warehouse group slicer values and counts.

```sql
SELECT ReportStore, COUNT(*) AS stores
FROM `databuffet-nonprd.dimension_table.dim_store`
GROUP BY ReportStore
ORDER BY stores DESC;
```
