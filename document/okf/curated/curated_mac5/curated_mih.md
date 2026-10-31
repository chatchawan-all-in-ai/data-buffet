---
type: BigQuery Table
title: "curated_mih"
description: "One row = one MAC5 document header (order, invoice, billing, etc.) per company, unique on (company_id, mihType, mihVnos)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mac5&t=curated_mih&page=table"
tags: ["curated", "curated_mac5", "mac5", "MAC5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/mac5/curated_mih.sqlx"
    title: "Dataform definition (curated/mac5/curated_mih.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Curated MAC5 document header table (MAC5 ERP `mih`). It renames the validated_mac5.mih columns to camelCase, adds the status description (`mihstatus_desc`) from the AR/AP status lookups and, for company ag01 only, the split-sale percentages (`percentSale1`, `percentSale2`) from validated_mac5.mih2. It is the main source of order (`mihType = 'PS'`) and invoice (`'IS'`) headers for dim_order, dim_invoice, dim_quotation, dim_delivery, the AR facts (fact_mir_vs, fact_mir_rs), the store facts (fact_order_store, fact_invoice_store, fact_backlog_store) and the Transaction_Data_Mart view. Pairs with [curated_mil](/curated/curated_mac5/curated_mil.md) (the line items).

# Grain and key

One row per document: `company_id` + `mihType` + `mihVnos` (the `uniqueKey`; documents with an empty `mihVnos` are excluded). The key is the document key itself, so each document is exactly one row. Not one row per customer: a document is identified by type and number within a company.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02); part of the key. |
| `mihDay` | INT64 | Day part of the document date (pass-through of mihday); combine with mihYear and mihMonth (`PARSE_DATE('%Y%m%d', CONCAT(mihYear, LPAD(mihMonth,2,'0'), LPAD(mihDay,2,'0')))`, as dim_order does) to get the business date. |
| `mihMonth` | INT64 | Month part of the document date (pass-through of mihmonth). |
| `mihYear` | INT64 | Year part of the document date (pass-through of mihyear). |
| `mihType` | STRING | Document type code, part of the key. Sales-side types seen in the code: QS, PS (sales order, used by dim_order/fact_order_store), IS (invoice, used by fact_invoice_store), AS, BS, VS, RS (meanings of QS/AS/BS/VS/RS not documented in the repo); purchase-side types QP, PP, IP, AP, BP, VP, RP. |
| `mihVnos` | STRING | Document number, part of the key (documents with an empty number are dropped by this table). |
| `mihCus` | STRING | Customer code (joins to validated_mac5.deb.debcode / mir.mircus / mil.milCus in downstream code). |
| `mihJob` | STRING | Pass-through of validated_mac5.mih.mihjob; carried into dim_order; meaning not documented in the repo (likely job/project code). |
| `mihDep` | STRING | Department / area code of the document (pass-through of mihdep); dim_customer_report_info matches it against the pipe-separated `DepCode` of the sales-unit master to pick the TA. |
| `mihPer` | STRING | Salesperson code (pass-through of mihper): joined to validated_mac5.per.percode for the name (`pernamet`) and matched to deb.debsalesp. |
| `mihDoc` | STRING | Meaning not documented in the repo |
| `mihMec` | STRING | Meaning not documented in the repo |
| `mihVatno` | STRING | Meaning not documented in the repo |
| `mihDesc` | STRING | Document description (pass-through of mihdesc; carried into dim_order); free text. |
| `mihMemo` | STRING | Free-text memo (pass-through of mihmemo). |
| `mihNotes` | STRING | Free-text notes (pass-through of mihnotes; carried into dim_order). |
| `mihRef1` | STRING | Reference number 1 (pass-through of mihref1). It is the join key to validated_mac5.mih2.mih2vnos for the split-sale percentages (ag01 only). |
| `mihRef2` | STRING | Reference number 2 (pass-through of mihref2; carried into dim_order); meaning not documented in the repo. |
| `mihRef3` | STRING | Reference number 3 (pass-through of mihref3; carried into dim_order); meaning not documented in the repo. |
| `mihDischt1` | STRING | Document-level discount field (pass-through of validated_mac5.mih.mihdischt1); exact semantics (text vs. amount) not documented in the repo |
| `mihDischt2` | STRING | Document-level discount field (pass-through of validated_mac5.mih.mihdischt2); exact semantics (text vs. amount) not documented in the repo |
| `mihDelvsite` | STRING | Meaning not documented in the repo |
| `mihDelvdate` | DATETIME | Delivery date of the document (pass-through of mihdelvdate; dim_order carries it as the order delivery date). Asia/Bangkok local datetime. |
| `mihStanding` | INT64 | Meaning not documented in the repo |
| `mihLinkgl` | INT64 | Meaning not documented in the repo |
| `mihNouplink` | INT64 | Meaning not documented in the repo |
| `mihNolist` | INT64 | Meaning not documented in the repo |
| `mihCurc` | INT64 | Meaning not documented in the repo |
| `mihVatinlist` | INT64 | Meaning not documented in the repo |
| `mihLock` | INT64 | Meaning not documented in the repo |
| `mihPrintn` | INT64 | Meaning not documented in the repo |
| `mihCheque` | INT64 | Meaning not documented in the repo |
| `mihCancel` | INT64 | Cancel flag (pass-through of mihcancel). 0 = active; -1 = cancelled. Some downstream paths filter cancellations, but dim_invoice/view_dim_invoice and Transaction_Data_Mart can retain them. |
| `mihStatus` | INT64 | Status code of the document (pass-through of mihstatus). Looked up in validated_mac5.ar_s (sales types) or ap_s (purchase types); status description in mihstatus_desc. |
| `mihClearum` | INT64 | Pass-through of mihclearum; carried into dim_order; meaning not documented in the repo. |
| `mihCtermno` | INT64 | Meaning not documented in the repo |
| `mihCog` | FLOAT64 | Meaning not documented in the repo |
| `mihVatsum` | FLOAT64 | VAT amount of the document (likely, inferred from the name; pass-through of mihvatsum). |
| `mihNetsum` | FLOAT64 | Net total amount of the document (likely, inferred from the name; pass-through of mihnetsum). |
| `mihDisclst` | FLOAT64 | Document-level discount field (pass-through of validated_mac5.mih.mihdisclst); exact semantics (text vs. amount) not documented in the repo |
| `mihDischf1` | FLOAT64 | Document-level discount field (pass-through of validated_mac5.mih.mihdischf1); exact semantics (text vs. amount) not documented in the repo |
| `mihDischf2` | FLOAT64 | Document-level discount field (pass-through of validated_mac5.mih.mihdischf2); exact semantics (text vs. amount) not documented in the repo |
| `mihExchg` | FLOAT64 | Meaning not documented in the repo |
| `mihExtrasum` | FLOAT64 | Extra amount on the document (pass-through of mihextrasum; carried into dim_order); meaning not documented in the repo. |
| `mihExtravat` | FLOAT64 | Meaning not documented in the repo |
| `mihExtracut` | INT64 | Meaning not documented in the repo |
| `mihExtramem` | STRING | Meaning not documented in the repo |
| `mihRecno` | STRING | Meaning not documented in the repo |
| `mihRecdate` | DATETIME | Meaning not documented in the repo |
| `mihSavetag` | STRING | Meaning not documented in the repo |
| `mihKeyuser` | STRING | Likely the user who keyed the document in (inferred from the name; pass-through of mihkeyuser). |
| `mihKeydate` | DATETIME | Likely the date the document was keyed in (inferred from the name; pass-through of mihkeydate; carried into dim_order). |
| `mihDocrunno` | STRING | Meaning not documented in the repo |
| `mihDategl` | DATETIME | Meaning not documented in the repo |
| `mihDuepo` | DATETIME | Meaning not documented in the repo |
| `mihEditlk` | DATETIME | Meaning not documented in the repo |
| `mihIscf` | INT64 | Meaning not documented in the repo |
| `mihIssp` | INT64 | Meaning not documented in the repo |
| `mihDates1` | DATETIME | Meaning not documented in the repo |
| `mihDates2` | DATETIME | Meaning not documented in the repo |
| `mihNumsi` | INT64 | Meaning not documented in the repo |
| `mihNumsc` | FLOAT64 | Meaning not documented in the repo |
| `mihVatpc` | FLOAT64 | Meaning not documented in the repo |
| `mihIncluded` | INT64 | Meaning not documented in the repo |
| `mihTaxvnos` | STRING | Meaning not documented in the repo |
| `mihTaxdate` | DATETIME | Meaning not documented in the repo |
| `mihTaxsum` | FLOAT64 | Meaning not documented in the repo |
| `mihLoad` | INT64 | Meaning not documented in the repo |
| `mihPaiddate` | DATETIME | Meaning not documented in the repo |
| `mihBookordernum` | STRING | Meaning not documented in the repo |
| `mihSenddate` | DATETIME | Meaning not documented in the repo |
| `mihBl` | INT64 | Pass-through of mihbl; carried into dim_order; meaning not documented in the repo. |
| `mihRpv` | INT64 | Meaning not documented in the repo |
| `mihClearcut` | INT64 | Meaning not documented in the repo |
| `mihSettlecut` | INT64 | Meaning not documented in the repo |
| `moddate` | DATETIME | Likely last-modified datetime of the source row (inferred from the name; pass-through of moddate). |
| `mihMemoNew` | STRING | Pass-through of mihmemo_new (newer memo text); carried into dim_order; meaning not documented in the repo. |
| `memoExtract` | STRING | Pass-through of memo_extract; carried into dim_order; meaning not documented in the repo (likely a value extracted from the memo text). |
| `asatdate` | DATE | Extract date of the winning row (from validated_mac5.mih); partition column. The incremental window compares against it. |
| `mihstatus_desc` | STRING | Thai status name resolved from mihStatus: for sales types (QS, PS, IS, AS, BS, VS, RS) `ar_s.ar_snamet`, for purchase types (QP, PP, IP, AP, BP, VP, RP) `ap_s.ap_snamet`, NULL for other types (joined on company_id). |
| `percentSale1` | STRING | Share of the document credited to sales rep 1, as a percent string like '100.00%'. For ag01 it comes from validated_mac5.mih2.mih2perpc (split-sale) matched on mihRef1 = mih2vnos and mihCus = mih2cus; when no split exists, and for every other company, it is the default '100.00%'. |
| `percentSale2` | STRING | Share credited to sales rep 2 as a percent string (from mih2.mih2per2pc, ag01 only); default '0.00%' when there is no split and for every other company. |

# How it is built

- Definition: `definitions/curated/mac5/curated_mih.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `company_id`, `mihType`, `mihVnos`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["company_id", "mihVnos", "mihType"]}`.
- Reads: [validated_mac5.mih](/validated/validated_mac5/mih.md), [validated_mac5.ar_s](/validated/validated_mac5/ar_s.md), [validated_mac5.ap_s](/validated/validated_mac5/ap_s.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md).
- Incremental MERGE on `uniqueKey` (tag `curated`, built after `validated_mac5.mih`, `ar_s`, `ap_s`, `mih2`); each run re-reads only validated rows with `asatdate` within the last `BACKFILL_DAYS` days (currently 1, Asia/Bangkok) and replaces those documents. No pre/post operations (unlike curated_mil).
- Approximate size (BigQuery metadata, 2026-10-31): 3,965,212 rows, 2.9 GB.

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
