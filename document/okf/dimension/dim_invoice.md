---
type: BigQuery Table
title: "dim_invoice"
description: "One row = one sales document line-link (invoice IS, credit note BS, debit note AS or quotation QS) per company, identified by document number, customer and linked order number, with sales-split percentages."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_invoice&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_invoice
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_invoice.sqlx"
    title: "Dataform definition (dimension/dim_invoice.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Invoice dimension of the star schema, covering MAC5 sales documents of type IS (invoice), BS (credit note), AS (debit note) and QS from `curated_mih` that have at least one line in `curated_mil`. Each row carries the document header attributes (date, customer, salesperson, status description, department, job, notes, branch `mihMec`), the order it fulfils (`milLinkVcno` and the resolved `OrderSK` from [dim_order](/dimension/dim_order.md)) and, for ag01, the sale-split percentages from `mih2` (`per_sale1`, `mih2per2`, `per_sale2`) with an `InvoiceSalesFlag`. It is the source of `InvoiceSK` for [fact_mir_vs](/fact/fact_mir_vs.md), [fact_mir_rs](/fact/fact_mir_rs.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_transaction_delivery](/fact/fact_transaction_delivery.md) and [dim_aging](/dimension/dim_aging.md), and is exposed through [view_dim_invoice](/view/dimension_view/view_dim_invoice.md).

Used by: [fact_table.fact_invoice_store](/fact/fact_invoice_store.md), [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [onetime.Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [fact_table.fact_transaction_delivery](/fact/fact_transaction_delivery.md).

# Grain and key

One row per (`CompanySK`, `mihYear`, `mihMonth`, `mihDay`, `mihVnos`, `mihCus`, `milLinkVcno`): a document number can appear several times when its lines link to different order numbers. `InvoiceSK` is a stable surrogate key (existing combos keep it; new ones get `max_sk + ROW_NUMBER()`). Rolling window: only documents dated from 1 January four years ago are loaded.

# Schema

| Column | Type | Description |
|---|---|---|
| `InvoiceSK` | INT64 | Stable surrogate key; never regenerated, stored in fact tables. |
| `OrderSK` | INT64 | Order SK from [dim_order](/dimension/dim_order.md), joined on `milLinkVcno = dim_order.mihVnos` and company (first SK per document). NULL when the line is not linked to a known order. Set at insert only (not updated by the MATCHED branch). |
| `mix_date` | DATE | Document date built from `mihYear`/`mihMonth`/`mihDay`. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md). |
| `companyID` | STRING | MAC5 company code. |
| `mihDay` | INT64 | Day part of the document date. |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `mihCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `mihPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `pernamet` | STRING | Employee name in Thai (first name, surname and nickname in parentheses). |
| `per_sale1` | FLOAT64 | Sale-split percent for the first salesperson (parsed from `mih2perpc`, ag01 only); 100 when the invoice has no split row. |
| `mih2per2` | STRING | Second salesperson code from `mih2.mih2per2` when the invoice's order has a split; '0' otherwise. |
| `per_sale2` | FLOAT64 | Sale-split percent for the second salesperson (parsed from `mih2per2pc`); 0 when no split. |
| `mihStatus` | INT64 | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `StatusDesc` | STRING | Status description looked up in `ar_s.ar_snamet` for sales types (QS/PS/IS/AS/BS/VS/RS) or `ap_s.ap_snamet` for purchase types. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihRef1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihRef2` | STRING | Customer purchase-order or external order reference number. |
| `mihDep` | STRING | Department code of the document, used as the sales channel code. |
| `mihJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `InvoiceSalesFlag` | STRING | 'Yes' when the invoice has a split (`per_sale1 <> 100`), else 'No'. |
| `milLinkVcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `mihNotes` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihDesc` | STRING | Free-text document description. |
| `mihMec` | STRING | Memo-card code of the document, matching `mec.meccode` (holds the shop or branch name for chain-store customers). |

# How it is built

- Definition: `definitions/dimension/dim_invoice.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.ap_s](/validated/validated_mac5/ap_s.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.per](/validated/validated_mac5/per.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `InvoiceSK` found via (year, month, day, `mihVnos`, `mihCus`, `milLinkVcno`, `CompanySK`). Source rows are limited to curated_mih documents with `asatdate >= yesterday` (incremental window) and dated within the last 4 years (from 1 Jan); updates attributes, inserts new combos, no delete. Runs after `dim_company` and `dim_order`. The target table pre-exists in BigQuery.

# Examples

Invoices per company and month for the last year (active documents only).

```sql
SELECT companyID, DATE_TRUNC(mix_date, MONTH) AS month, COUNT(DISTINCT mihVnos) AS invoices
FROM `databuffet-nonprd.dimension_table.dim_invoice`
WHERE mihType = 'IS' AND mihCancel <> -1
  AND mix_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 YEAR)
GROUP BY companyID, month
ORDER BY companyID, month;
```

Invoices with a sale split and the order they link to.

```sql
SELECT companyID, mihVnos, milLinkVcno, OrderSK, mihPer, per_sale1, mih2per2, per_sale2
FROM `databuffet-nonprd.dimension_table.dim_invoice`
WHERE InvoiceSalesFlag = 'Yes'
ORDER BY mix_date DESC
LIMIT 50;
```
