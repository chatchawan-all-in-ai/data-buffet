---
type: BigQuery Table
title: "curated_mih"
description: "One row = one MAC5 document header (order, invoice, billing, etc.) per company, unique on (company_id, mihType, mihVnos)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mac5&t=curated_mih&page=table"
project_id: databuffet-nonprd
dataset_id: curated_mac5
table_id: curated_mih
tags: ["curated", "curated_mac5", "mac5", "MAC5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/mac5/curated_mih.sqlx"
    title: "Dataform definition (curated/mac5/curated_mih.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Curated MAC5 document header table (MAC5 ERP `mih`). It renames the validated_mac5.mih columns to camelCase, adds the status description (`mihstatus_desc`) from the AR/AP status lookups and, for company ag01 only, the split-sale percentages (`percentSale1`, `percentSale2`) from validated_mac5.mih2. Pairs with [curated_mil](/curated/curated_mac5/curated_mil.md) (the line items).

Read by: [curated_journal_invoice](/curated/curated_derp/curated_journal_invoice.md), [dim_aging](/dimension/dim_aging.md), [dim_customer_grade](/dimension/dim_customer_grade.md), [dim_delivery](/dimension/dim_delivery.md), [dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [dim_invoice](/dimension/dim_invoice.md), [dim_order](/dimension/dim_order.md), [dim_quotation](/dimension/dim_quotation.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_delivery](/fact/fact_delivery.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_mir_rs](/fact/fact_mir_rs.md), [fact_mir_vs](/fact/fact_mir_vs.md), [fact_order_store](/fact/fact_order_store.md), [view_aging_ri](/view/fact_view/view_aging_ri.md), [view_fact_mir_rs](/view/fact_view/view_fact_mir_rs.md), [Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md).

# Grain and key

One row per document: `company_id` + `mihType` + `mihVnos` (the `uniqueKey`; documents with an empty `mihVnos` are excluded). The key is the document key itself, so each document is exactly one row. Not one row per customer: a document is identified by type and number within a company.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02); part of the key. |
| `mihDay` | INT64 | Day part of the document date. |
| `mihMonth` | INT64 | Month part of the document date. |
| `mihYear` | INT64 | Year part of the document date (Gregorian). |
| `mihType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `mihVnos` | STRING | Document number, unique within company and document type. |
| `mihCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mihJob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `mihDep` | STRING | Department code of the document, used as the sales channel code. |
| `mihPer` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `mihDoc` | STRING | Document print-form code of the header from the MAC5 `doc` master. |
| `mihMec` | STRING | Memo-card code of the document, matching `mec.meccode` (holds the shop or branch name for chain-store customers). |
| `mihVatno` | STRING | Tax invoice number of the document. |
| `mihDesc` | STRING | Free-text document description. |
| `mihMemo` | STRING | Free-text document memo with an optional tag enclosed in `฿` signs. |
| `mihNotes` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihRef1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihRef2` | STRING | Customer purchase-order or external order reference number. |
| `mihRef3` | STRING | Free-text reference 3 of the document. |
| `mihDischt1` | STRING | Header discount 1 as entered (percentage or amount text). |
| `mihDischt2` | STRING | Header discount 2 as entered (percentage or amount text). |
| `mihDelvsite` | STRING | Delivery site code (e.g. `0002`). |
| `mihDelvdate` | DATETIME | Requested delivery date. |
| `mihStanding` | INT64 | Credit term in days; due date = document date + this value. |
| `mihLinkgl` | INT64 | General-ledger posting link status (0 = not posted). |
| `mihNouplink` | INT64 | Code controlling updates to linked documents. |
| `mihNolist` | INT64 | Number of line items on the document. |
| `mihCurc` | INT64 | Currency code (0 = Thai baht). |
| `mihVatinlist` | INT64 | Flag indicating VAT-inclusive line prices (-1 = yes, 0 = no). |
| `mihLock` | INT64 | Flag: document locked against editing (-1 = locked). |
| `mihPrintn` | INT64 | Number of times the document has been printed. |
| `mihCheque` | INT64 | Flag: document settled by cheque. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihStatus` | INT64 | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `mihClearum` | INT64 | Flag: outstanding quantities of the document cleared (0 = still open). |
| `mihCtermno` | INT64 | Payment-term number of the document. |
| `mihCog` | FLOAT64 | Gross document amount before discounts, excluding VAT; negative for credit notes (`BS`). |
| `mihVatsum` | FLOAT64 | VAT amount of the document; negative for credit notes (`BS`). |
| `mihNetsum` | FLOAT64 | Net document total including VAT, after all discounts; negative for credit notes (`BS`). |
| `mihDisclst` | FLOAT64 | Total of line-level discounts on the document; negative for credit notes (`BS`). |
| `mihDischf1` | FLOAT64 | Header discount 1 amount; negative for credit notes (`BS`). |
| `mihDischf2` | FLOAT64 | Header discount 2 amount; negative for credit notes (`BS`). |
| `mihExchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `mihExtrasum` | FLOAT64 | Deposit amount deducted on the document, excluding VAT. |
| `mihExtravat` | FLOAT64 | VAT on the deducted deposit amount. |
| `mihExtracut` | INT64 | Flag indicating that a deposit deduction is applied. |
| `mihExtramem` | STRING | Memo of the deducted deposit, listing the deposit receipt numbers and dates. |
| `mihRecno` | STRING | Number of the related receipt or received document. |
| `mihRecdate` | DATETIME | Date of the related receipt or received document. |
| `mihSavetag` | STRING | Save-tag marker set by the ERP when the document is saved. |
| `mihKeyuser` | STRING | User code of the person who keyed the document. |
| `mihKeydate` | DATETIME | Date and time the document was keyed. |
| `mihDocrunno` | STRING | Document running number. |
| `mihDategl` | DATETIME | General-ledger posting date. |
| `mihDuepo` | DATETIME | Purchase-order due date and time. |
| `mihEditlk` | DATETIME | Timestamp of the current edit lock on the document. |
| `mihIscf` | INT64 | Flag indicating a carry-forward (opening balance) document. |
| `mihIssp` | INT64 | Special-document flag. |
| `mihDates1` | DATETIME | Special date 1 of the document. |
| `mihDates2` | DATETIME | Special date 2 of the document. |
| `mihNumsi` | INT64 | Special integer field of the document. |
| `mihNumsc` | FLOAT64 | Special numeric field of the document. |
| `mihVatpc` | FLOAT64 | VAT rate in percent (e.g. 7). |
| `mihIncluded` | INT64 | Flag indicating VAT-inclusive document amounts. |
| `mihTaxvnos` | STRING | Separate tax invoice number issued for the document. |
| `mihTaxdate` | DATETIME | Date of the separate tax invoice. |
| `mihTaxsum` | FLOAT64 | Amount of the separate tax invoice. |
| `mihLoad` | INT64 | Flag indicating goods loaded for delivery (1 = loaded). |
| `mihPaiddate` | DATETIME | Date the document was fully paid. |
| `mihBookordernum` | STRING | Number of the booking (order) document linked to this document. |
| `mihSenddate` | DATETIME | Date the goods were sent. |
| `mihBl` | INT64 | Billing-note flag of the document. |
| `mihRpv` | INT64 | Receipt/payment-voucher flag of the document. |
| `mihClearcut` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `mihSettlecut` | INT64 | Flag: settlement completed (-1 = settled). |
| `moddate` | DATETIME | Date and time the document was last modified (ag01 only; NULL for the other companies). |
| `mihMemoNew` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `memoExtract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `asatdate` | DATE | Extract date of the winning row (from validated_mac5.mih); partition column. The incremental window compares against it. |
| `mihstatus_desc` | STRING | Thai status name resolved from mihStatus: for sales types (QS, PS, IS, AS, BS, VS, RS) `ar_s.ar_snamet`, for purchase types (QP, PP, IP, AP, BP, VP, RP) `ap_s.ap_snamet`, NULL for other types (joined on company_id). |
| `percentSale1` | STRING | Share of the document credited to sales rep 1, as a percent string like '100.00%' or '33.33%' (`CONCAT(ROUND(x, 2), '%')`; not capped at 100). For ag01 it comes from validated_mac5.mih2.mih2perpc (split-sale) matched on mihRef1 = mih2vnos and mihCus = mih2cus; when no split exists, and for every other company, it is the default '100.00%'. |
| `percentSale2` | STRING | Share credited to sales rep 2 as a percent string such as '40%' (from mih2.mih2per2pc, ag01 only; not capped at 100); default '0.00%' when there is no split and for every other company. |

# How it is built

- Definition: `definitions/curated/mac5/curated_mih.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `company_id`, `mihType`, `mihVnos`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["company_id", "mihVnos", "mihType"]}`.
- Reads: [validated_mac5.mih](/validated/validated_mac5/mih.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.ap_s](/validated/validated_mac5/ap_s.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md).
- Incremental MERGE on `uniqueKey` (tag `curated`, built after `validated_mac5.mih`, `ar_s`, `ap_s`, `mih2`); each run re-reads only validated rows with `asatdate` within the last `BACKFILL_DAYS` days (Asia/Bangkok) and replaces those documents. No pre/post operations.

# Examples

Active sales orders (PS) of one company in the last 30 days of extract data, with the business date built from the split columns.

```sql
SELECT company_id, mihVnos, mihCus, mihNetsum,
       PARSE_DATE('%Y%m%d', CONCAT(mihYear, FORMAT('%02d', mihMonth), FORMAT('%02d', mihDay))) AS doc_date
FROM `databuffet-nonprd.curated_mac5.curated_mih`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 30 DAY)
  AND company_id = 'ag01' AND mihType = 'PS' AND mihCancel = 0
```

Document counts per type and status description for one company.

```sql
SELECT mihType, mihstatus_desc, COUNT(*) AS n
FROM `databuffet-nonprd.curated_mac5.curated_mih`
WHERE company_id = 'ag01' AND asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
GROUP BY mihType, mihstatus_desc
ORDER BY n DESC
```
