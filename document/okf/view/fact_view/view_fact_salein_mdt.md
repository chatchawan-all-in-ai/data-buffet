---
type: BigQuery View
title: "view_fact_salein_mdt"
description: "One row = one sales document line of fact_transcation sold to a modern-trade chain customer (MH, HP, TW, GB, DH, BT), tagged with chain code and the matching MDT branch/zone SK."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_salein_mdt&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_salein_mdt
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_salein_mdt.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_salein_mdt.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

The bridge between sell-in (our invoices to the chains) and the sell-out MDT facts (what the chains report selling per branch). It keeps only [fact_transcation](/fact/fact_transcation.md) lines whose customer is a modern-trade chain branch, classifies the chain (`store_code`) from `debgroup`/customer name, and tries to find the MDT branch ([dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md)) from the branch name embedded in the customer name.

# Grain and key

One row = one `fact_transcation` row of a customer with a chain code (INNER JOIN; `store_code IS NULL` rows are dropped). No set of this view's columns is unique: `fact_transcation` also carries `milCus` and `milPer`, which this view does not expose. The `branch_lookup` CTE keeps one SK per (store, cleaned branch name), so the LEFT JOIN to `dim_sales_branch_mdt` adds no rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Bill date (`fact_transcation.mix_date`). |
| `store_code` | STRING | Modern-trade chain code derived from the customer master: MH (Mega Home; `debgroup = 'MH'` or name contains Mega), HP (HomePro; `debgroup` starts with HP), TW (`TW`/`TWEXPO`), GB, DH (`DOHOME`), BT (`BT`/`BT.C` or name contains Boonthavorn). Same codes as `StoreCode` in `dim_sales_branch_mdt`. |
| `CustomerSK` | INT64 | SK of `dim_customer` (the chain branch as a customer); `dim_customer` is a MERGE dim with stable SKs. |
| `customer_code` | STRING | `dim_customer.customer_code` of the chain customer. |
| `customer_name` | STRING | Thai customer name (`dim_customer.debnamet`) of the chain branch; used to extract the branch name after the word `สาขา`. |
| `customer_branch_no` | STRING | `dim_customer.debbranch`, the branch number in the customer master. |
| `customer_branch_name` | STRING | Branch name cut from the customer name after `สาขา` (trailing brackets/spaces trimmed); NULL when the name has no `สาขา`. |
| `branch_sk` | INT64 | SK of `dim_sales_branch_mdt` (BranchMdtSK) found by matching store_code + a cleaned branch name key (store prefixes, spaces, brackets, dashes removed); `-1` when no branch matches. |
| `zone_sk` | INT64 | ZoneMdtSK of the matched branch in `dim_sales_branch_mdt`; `-1` when unmatched. |
| `CompanySK` | INT64 | SK of `dim_company` (from `fact_transcation`). |
| `companyID` | STRING | MAC5 company code from `fact_transcation.companyID`. |
| `ProductSK` | INT64 | SK of `dim_product_master` for the product on the line. |
| `SaleRepSK` | INT64 | SK of the sale representative on the line (`fact_transcation.SaleRepSK`, daily-regenerated). |
| `doc_type_code` | STRING | Document type code (`IS` = invoice, `AS` = debit note, `BS` = credit note, `QS` = sales quotation). |
| `doc_no` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `doc_line_no` | INT64 | Line number within the document. |
| `product_code_mac5` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `sale_qty` | FLOAT64 | Quantity on the line (`milQuan`). |
| `sale_amount` | FLOAT64 | Line amount excluding VAT (`milSum`). |
| `sale_amount_incvat` | FLOAT64 | Line amount including VAT (`milsum_incvat`). |
| `asatdate` | DATE | Load date of the `fact_transcation` row. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_salein_mdt.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_sales_branch_mdt](/dimension/dim_sales_branch_mdt.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [fact_table.fact_transcation](/fact/fact_transcation.md).

# Examples

Monthly sell-in per chain, VAT-inclusive.

```sql
SELECT DATE_TRUNC(sale_date, MONTH) AS month, store_code,
       SUM(sale_amount_incvat) AS sell_in_incvat, SUM(sale_qty) AS qty
FROM `databuffet-nonprd.fact_view.view_fact_salein_mdt`
GROUP BY month, store_code
ORDER BY month, store_code
```

Document lines per chain and how many have no matching MDT branch.

```sql
SELECT store_code, COUNTIF(branch_sk = -1) AS unmatched_lines, COUNT(*) AS lines
FROM `databuffet-nonprd.fact_view.view_fact_salein_mdt`
GROUP BY store_code
ORDER BY store_code
```
