---
type: BigQuery Table
title: "fact_backlog_store"
description: "One row = one product (cpsStkID) on one open sales order (cpsVnosID) per customer and store, with requested and cut quantities from the latest cps snapshot."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_backlog_store&page=table"
tags: ["fact", "mac5", "mds", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_backlog_store.sqlx"
    title: "Dataform definition (fact/fact_backlog_store.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Order backlog (unfilled quantity) by store: for each PS sales order that is not cancelled and has no clear/extra sum, the requested quantity (`cpsStkREQ`) minus the quantity cut/shipped (`cpsStkCUT1`) taken from the latest `validated_mac5.cps` snapshot per company. Answers how much is still to be delivered per store/product. Sister of [fact_order_store](/fact/fact_order_store.md) and [fact_invoice_store](/fact/fact_invoice_store.md); no other table reads it.

Used by / context: used by nothing else in the repo.

# Grain and key

One row per `FactBacklogStoreSK` (ROW_NUMBER over CompanySK, date parts, cpsVnosID, cpsCusID, cpsStkID). Rows are SUMs grouped by company, order date, order/customer/product/store and `FlagFree`. Only the latest `asatdate` of cps per company is read (snapshot, not history). Order header filters: `mihType = 'PS'`, `mihCancel = 0`, `mihClearUM = 0`, `mihExtraSUM = 0`, description not LIKE '%PO.วางบิล%', 4-year window. Lines are restricted to those in `mil_line_scope` (same filters as the order-store line scope). Only company_id ag01 and ab01, only products whose `TypeMarketing` is not 'Sourcing', and (store facts) lines with `milstype <> 3`, product code not starting with the Thai letter bo, and not `TEST%`.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactBacklogStoreSK` | INT64 | Surrogate key: ROW_NUMBER over CompanySK, date parts, cpsVnosID, cpsCusID, cpsStkID. Regenerates daily. |
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md). |
| `company_id` | STRING | MAC5 company code; only 'ag01' and 'ab01' are loaded. |
| `sDate` | DATE | Order date: SAFE.PARSE_DATE of mihYear, mihMonth, mihDay of the order header; partition column. |
| `mihYear` | INT64 | Year of the document header (curated_mih). |
| `mihMonth` | INT64 | Month of the document header (curated_mih). |
| `mihDay` | INT64 | Day of the document header (curated_mih). |
| `OrderSK` | INT64 | Surrogate key of [dim_order](/dimension/dim_order.md) via `mihVnos`; never NULL (INNER JOIN). |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`debcode = mihCus`, same company); NULL when unmatched. |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (case-insensitive product code match); rows without a product (or with TypeMarketing 'Sourcing') are dropped by an INNER JOIN, so never NULL. |
| `StoreSK` | INT64 | Surrogate key of [dim_store](/dimension/dim_store.md) (warehouse/branch) matched on company and store code; -1 when the store code is not in dim_store. |
| `cpsVnosID` | STRING | Sales order number from cps (`cpsVnosID`); equals `mihVnos`. |
| `cpsCusID` | STRING | Customer code from cps (equals `mihCus`). |
| `cpsStkID` | STRING | Product code from cps (compared exactly to `ProductCode`). |
| `cpsSto` | STRING | Store/warehouse code from cps (joins `dim_store.StoreCode`). |
| `FlagFree` | STRING | 'Yes' when `cps.cpssumreq = 0` OR `ProductGroupMAC5 = '5000'`; else 'No'. Part of the GROUP BY. |
| `cpsStkREQ` | FLOAT64 | SUM of `cps.cpsStkREQ`, quantity requested on the order. |
| `cpsStkCUT1` | FLOAT64 | SUM of `cps.cpsStkCUT1`, quantity already cut (delivered/reserved out); meaning inferred from the name. |
| `qty` | FLOAT64 | Backlog quantity = SUM(cpsStkREQ) - SUM(cpsStkCUT1). |

# How it is built

- Definition: `definitions/fact/fact_backlog_store.sqlx` (`type: "table"`, tags `fact_daily`).
- `uniqueKey`: `FactBacklogStoreSK`.
- Storage options: `{"partitionBy": "sDate", "clusterBy": ["FactBacklogStoreSK"]}`.
- Reads: [validated_mac5.cps](/validated/validated_mac5/cps.md), [dimension_table.dim_order](/dimension/dim_order.md), `mds_dataset.mds_data_status_control_master` (master data loaded outside this repo), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_store](/dimension/dim_store.md).
- Refresh: full daily rebuild (`type: "table"`, tag `fact_daily`, uniqueKey `FactBacklogStoreSK`, partition `sDate`, cluster `FactBacklogStoreSK`), after `dim_order`, `dim_customer`, `dim_product_master`, `dim_company`, `dim_store`; reads the newest cps snapshot, so it reflects the state at the last validated cps load.
- Approximate size (BigQuery metadata, 2026-10-31): 303,756 rows, 45.9 MB.

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
