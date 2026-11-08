---
type: BigQuery Table
title: "fact_order_store"
description: "One row = one product line (milListNo) of a sales order (PS) in a warehouse-flagged status for ag01/ab01, with product, customer and store SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_order_store&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_order_store
tags: ["fact", "mds", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_order_store.sqlx"
    title: "Dataform definition (fact/fact_order_store.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Order-line fact sliced by store/warehouse (branch) for the store reporting use case: PS (sales order) lines from `curated_mil` joined to their `curated_mih` header, restricted to orders that are in an MDS status with `flagwarehouse = true`, excluding 'PO.วางบิล' orders. Answers which products are ordered per store and when. Sister tables: [fact_invoice_store](/fact/fact_invoice_store.md) and [fact_backlog_store](/fact/fact_backlog_store.md).

Read by: none in this repository.

# Grain and key

One row = one line (`milListNo`) of one PS sales order per company: key `FactOrderStoreSK` (see [Schema](#schema) for key generation). Orders are restricted to those in `dim_order_dedup` (active MDS status with `flagwarehouse = true`, description not LIKE '%PO.วางบิล%', order date inside the 4-year window, one OrderSK per company + vnos). Only company_id ag01 and ab01; only products whose `TypeMarketing` is not 'Sourcing' (products with no marketing type are dropped too); lines with `milstype <> 3`, product code not starting with the Thai letter bo and not `TEST%`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactOrderStoreSK` | INT64 | Stable row key: FARM_FINGERPRINT of the typed company/date/type/order/line grain plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `company_id` | STRING | MAC5 company code; only 'ag01' and 'ab01' are loaded. |
| `mix_date` | DATE | Order date: SAFE.PARSE_DATE of mihYear, mihMonth, mihDay (Asia/Bangkok business date); partition column. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihDay` | INT64 | Day part of the document date. |
| `OrderSK` | INT64 | Surrogate key of [dim_order](/dimension/dim_order.md) via `mihVnos`; never NULL (INNER JOIN). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`debcode = mihCus`, same company); NULL when unmatched. |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (case-insensitive product code match); rows without a product (or with TypeMarketing 'Sourcing') are dropped by an INNER JOIN, so never NULL. |
| `StoreSK` | INT64 | Surrogate key of [dim_store](/dimension/dim_store.md) (warehouse/branch) matched on company and store code; -1 when the store code is not in dim_store. |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milVnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milListNo` | INT64 | Line number within the document. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milDesc` | STRING | Free-text line description. |
| `milSto` | STRING | Warehouse (store) code the line is issued from, matching `sto` store codes. |
| `milQuan` | FLOAT64 | Line quantity from curated_mil (not summed; one row per line). |
| `mihPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `milSType` | STRING | Line item type label: 'Item' (milstype 1), 'Serial' (2), otherwise 'Unknown'; service lines (3) are excluded. |
| `FlagFree` | STRING | 'Yes' when `milsum = 0` OR `ProductGroupMAC5 = '5000'` OR `milDesc` starts with the Thai word for promotion; else 'No'. |

# How it is built

- Definition: `definitions/fact/fact_order_store.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactOrderStoreSK`.
- Storage options: `{"partitionBy": "mix_date", "clusterBy": ["FactOrderStoreSK"]}`.
- Reads: [dimension_table.dim_order](/dimension/dim_order.md), `mds_dataset.mds_data_status_control_master` (master data loaded outside this repo), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_store](/dimension/dim_store.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactOrderStoreSK`, partition `mix_date`, cluster `FactOrderStoreSK`), after `dim_order`, `dim_customer`, `dim_product_master`, `dim_company`, `dim_store`. Retention: rolling 4 years truncated to start-of-year.

# Examples

Ordered quantity per store in a month.
```sql
SELECT StoreSK, SUM(milQuan) AS qty
FROM `databuffet-nonprd.fact_table.fact_order_store`
WHERE mix_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31' AND FlagFree = 'No'
GROUP BY StoreSK;
```
Lines of one order.
```sql
SELECT milListNo, milStk, milDesc, milQuan, FlagFree
FROM `databuffet-nonprd.fact_table.fact_order_store`
WHERE milVnos = '<order no>' AND company_id = 'ag01'
ORDER BY milListNo;
```
