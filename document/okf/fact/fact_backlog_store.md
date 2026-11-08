---
type: BigQuery Table
title: "fact_backlog_store"
description: "One row = one product (cpsStkID) on one open sales order (cpsVnosID) per customer and store, with requested and cut quantities from the latest cps snapshot."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_backlog_store&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_backlog_store
tags: ["fact", "mac5", "mds", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_backlog_store.sqlx"
    title: "Dataform definition (fact/fact_backlog_store.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

Order backlog (unfilled quantity) by store: for each PS sales order that is not cancelled and has no clear/extra sum, the requested quantity (`cpsStkREQ`) minus the quantity cut/shipped (`cpsStkCUT1`) taken from the latest `validated_mac5.cps` snapshot per company. Answers how much is still to be delivered per store/product. Sister of [fact_order_store](/fact/fact_order_store.md) and [fact_invoice_store](/fact/fact_invoice_store.md).

Read by: none in this repository.

# Grain and key

One row = one product on one open PS sales order per customer and store: key `FactBacklogStoreSK` (see [Schema](#schema) for key generation). Rows are SUMs grouped by company, order date, order/customer/product/store and `FlagFree`. Only the latest `asatdate` of cps per company is read (snapshot, not history). Order header filters: `mihType = 'PS'`, `mihCancel = 0`, `mihClearUM = 0`, `mihExtraSUM = 0`, description not LIKE '%PO.วางบิล%', order date within the 4-year window (truncated to start-of-year); the order must also be in `dim_order` with an active MDS status that has `flagwarehouse = true`. Lines are restricted to PS lines of `curated_mil` with `milstype <> 3`, product code not starting with the Thai letter bo and not `TEST%`. Only company_id ag01 and ab01; only products whose `TypeMarketing` is not 'Sourcing' (products with no marketing type are dropped too).

# Schema

| Column | Type | Description |
|---|---|---|
| `FactBacklogStoreSK` | INT64 | Stable row key: FARM_FINGERPRINT of the typed company/date/order/customer/product grain plus `occ`; `occ` follows the [shared occurrence rule](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `company_id` | STRING | MAC5 company code; only 'ag01' and 'ab01' are loaded. |
| `sDate` | DATE | Order date: SAFE.PARSE_DATE of mihYear, mihMonth, mihDay of the order header; partition column. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihDay` | INT64 | Day part of the document date. |
| `OrderSK` | INT64 | Surrogate key of [dim_order](/dimension/dim_order.md) via `mihVnos`; never NULL (INNER JOIN). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`debcode = mihCus`, same company); NULL when unmatched. |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (exact product code match on `cpsStkID`); rows without a product (or with TypeMarketing 'Sourcing') are dropped by an INNER JOIN, so never NULL. |
| `StoreSK` | INT64 | Surrogate key of [dim_store](/dimension/dim_store.md) (warehouse/branch) matched on company and store code; -1 when the store code is not in dim_store. |
| `cpsVnosID` | STRING | Number of the sales order document that has the outstanding line (e.g. a `PS` sales order). |
| `cpsCusID` | STRING | Customer code of the document, matching `deb.debcode`. |
| `cpsStkID` | STRING | Product (stock) code of the outstanding line, matching `stk.stkcode`. |
| `cpsSto` | STRING | Warehouse (store) code the line is issued from or received into. |
| `FlagFree` | STRING | 'Yes' when `cps.cpssumreq = 0` OR `ProductGroupMAC5 = '5000'`; else 'No'. Part of the GROUP BY. |
| `cpsStkREQ` | FLOAT64 | SUM of `cps.cpsStkREQ`, quantity requested on the order. |
| `cpsStkCUT1` | FLOAT64 | SUM of `cps.cpsStkCUT1`: ordered quantity already cut from stock (delivered); qty = cpsStkREQ - cpsStkCUT1. |
| `qty` | FLOAT64 | Backlog quantity = SUM(cpsStkREQ) - SUM(cpsStkCUT1). |

# How it is built

- Definition: `definitions/fact/fact_backlog_store.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactBacklogStoreSK`.
- Storage options: `{"partitionBy": "sDate", "clusterBy": ["FactBacklogStoreSK"]}`.
- Reads: [validated_mac5.cps](/validated/validated_mac5/cps.md), [dimension_table.dim_order](/dimension/dim_order.md), `mds_dataset.mds_data_status_control_master` (master data loaded outside this repo), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_store](/dimension/dim_store.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactBacklogStoreSK`, partition `sDate`, cluster `FactBacklogStoreSK`), after `dim_order`, `dim_customer`, `dim_product_master`, `dim_company`, `dim_store`; reads the newest cps snapshot, so it reflects the state at the last validated cps load.

# Examples

Open backlog quantity per store.
```sql
SELECT StoreSK, SUM(qty) AS backlog_qty
FROM `databuffet-nonprd.fact_table.fact_backlog_store`
WHERE qty > 0 AND FlagFree = 'No'
GROUP BY StoreSK;
```
Open lines of one order.
```sql
SELECT cpsStkID, cpsStkREQ, cpsStkCUT1, qty
FROM `databuffet-nonprd.fact_table.fact_backlog_store`
WHERE cpsVnosID = '<order no>' AND company_id = 'ag01';
```
