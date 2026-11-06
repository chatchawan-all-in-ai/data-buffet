---
type: BigQuery View
title: "view_fact_salein_director_mdt"
description: "One row = one day x product x marketing group x report line x region/manager/director combination of sell-in sales to the director with DirectorID 00004, aggregated from view_fact_transcation."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_salein_director_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_salein_director_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_salein_director_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_salein_director_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T23:54:24+07:00" }
status: draft
---

# What it is

A pre-aggregated sell-in (sales invoiced to customers) feed for a single director (`DirectorID = '00004'`, `DirectorName = 'MDT'` in [dim_director](/dimension/dim_director.md)). It sums the quantity, discount and net-sales measures of [view_fact_transcation](/view/fact_view/view_fact_transcation.md) per day and product, keeping both the bill-date org assignment (`RegionSK`, `RegionManagerSK`, `DirectorSK`) and the latest assignment (`*SKLast`).

# Grain and key

One row = one `GROUP BY 1..16` group: key `mix_date`, `ProductSK`, `milStk`, `NewProductMktSK`, `FlagSaleExc`, `FlagAccExc`, `ReportSK`, `RegionSK`, `RegionManagerSK`, `DirectorSK`, `RegionSKLast`, `RegionManagerSKLast`, `DirectorSKLast` (unique). milYear/milMonth/milDay are functionally determined by mix_date. Only lines whose `DirectorSK` joins `dim_director` with `DirectorID = '00004'` are included (INNER JOIN), which also drops the zero-filled calendar rows of the source view (their DirectorSK is NULL).

# Schema

| Column | Type | Description |
|---|---|---|
| `mix_date` | DATE | Bill date from `view_fact_transcation.mix_date`. |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milMonth` | INT64 | Month part of the document date. |
| `milDay` | INT64 | Day part of the document date. |
| `ProductSK` | INT64 | SK of `dim_product_master` for the product (`milStk`, case-insensitive match per company); stable (MERGE dim). |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `NewProductMktSK` | INT64 | Marketing product-group SK: `COALESCE(mds NewProductMktSK, ProductMktSK)` from `dim_product_mkt` through `dim_stk_mkt`. |
| `FlagSaleExc` | STRING | Grouping value from `view_fact_transcation`; see its [exclusion rules and calendar-row NULL behavior](/view/fact_view/view_fact_transcation.md#schema). |
| `FlagAccExc` | STRING | `Yes` = line is excluded from finance/accounting sales (cancelled/status 32,33 or accounting-exclusion rebate rule), else `No`. |
| `ReportSK` | INT64 | SK of the `dim_report` reporting line chosen for the line (by region and, where needed, marketing group). |
| `RegionSK` | INT64 | SK of `dim_region` for the line as of the bill date (sale-rep assignment on the date; mapping-invoice adjusted). |
| `RegionManagerSK` | INT64 | SK of `dim_region_manager` as of the bill date. |
| `DirectorSK` | INT64 | SK of `dim_director` as of the bill date; this view keeps only the director with `DirectorID = '00004'`. |
| `RegionSKLast` | INT64 | SK of `dim_region_last` using the latest sale-rep snapshot instead of the bill-date assignment (historical bills are re-assigned to the current structure). |
| `RegionManagerSKLast` | INT64 | SK of the region manager under the latest (`_last`) structure. |
| `DirectorSKLast` | INT64 | SK of the director under the latest (`_last`) structure. |
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milAdisc` | FLOAT64 | Allocated header discount deducted from the line amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milSum` | FLOAT64 | Net sales amount excluding VAT, summed (`NetSalesExcVat`). |
| `milsum_incvat` | FLOAT64 | Net sales including VAT: `milSum + Vat` (VAT allocated to the line from the document VAT), summed. |
| `mildisca_incvat` | FLOAT64 | Discount amount including VAT, summed. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_salein_director_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [dimension_table.dim_director](/dimension/dim_director.md).

# Examples

Monthly net sales excluding VAT for the director, KPI-eligible lines only.

```sql
SELECT DATE_TRUNC(mix_date, MONTH) AS month, SUM(milSum) AS net_sales_exc_vat, SUM(milsum_incvat) AS net_sales_inc_vat, SUM(milQuan) AS qty
FROM `databuffet-nonprd.fact_view.view_fact_salein_director_mdt`
WHERE FlagSaleExc = 'No'
GROUP BY month
ORDER BY month
```
