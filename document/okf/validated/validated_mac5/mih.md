---
type: BigQuery Table
title: "mih"
description: "One row = one sales or purchase document header (per company), unique on (company_id, MIHtype, MIHvnos)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mih&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mih
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mih.sqlx"
    title: "Dataform definition (validated/mac5/mih.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `mih` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. For credit notes (`mihtype` `BS`) the amount columns are sign-flipped and the values before the flip are kept in the `*_raw` columns; the memo is split into `mihmemo_new` and `memo_extract`; rows with an empty `mihvnos` are dropped. Table meaning: Headers of all MAC5 trading documents (quotations, sales orders, invoices, debit and credit notes, billing statements, receipts and their purchase-side equivalents), one row per company, document type and document number.
Used by: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.mil](/validated/validated_mac5/mil.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [pub_sub.export_credit_note](/view/pub_sub/export_credit_note.md), [pub_sub.export_debit_note](/view/pub_sub/export_debit_note.md), [pub_sub.export_invoice](/view/pub_sub/export_invoice.md), [pub_sub.export_order](/view/pub_sub/export_order.md), [pub_sub.export_receipt](/view/pub_sub/export_receipt.md).

# Grain and key

One row per `company_id`, `MIHtype`, `MIHvnos`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mihday` | INT64 | Day part of the document date. |
| `mihmonth` | INT64 | Month part of the document date. |
| `mihyear` | INT64 | Year part of the document date (Gregorian). |
| `mihtype` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `mihvnos` | STRING | Document number, unique within company and document type. |
| `mihcus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `mihjob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `mihdep` | STRING | Department code of the document, used as the sales channel code. |
| `mihper` | STRING | Salesperson (employee) code, matching `per.percode`. |
| `mihdoc` | STRING | Document print-form code of the header from the MAC5 `doc` master. |
| `mihmec` | STRING | Memo-card code of the document, matching `mec.meccode` (holds the shop or branch name for chain-store customers). |
| `mihvatno` | STRING | Tax invoice number of the document. |
| `mihdesc` | STRING | Free-text document description. |
| `mihmemo` | STRING | Free-text document memo with an optional tag enclosed in `฿` signs. |
| `mihnotes` | STRING | Free-text notes such as delivery instructions or site details. |
| `mihref1` | STRING | Reference document number 1 for the source quotation or sales order. |
| `mihref2` | STRING | Customer purchase-order or external order reference number. |
| `mihref3` | STRING | Free-text reference 3 of the document. |
| `mihdischt1` | STRING | Header discount 1 as entered (percentage or amount text). |
| `mihdischt2` | STRING | Header discount 2 as entered (percentage or amount text). |
| `mihdelvsite` | STRING | Delivery site code (e.g. `0002`). |
| `mihdelvdate` | DATETIME | Requested delivery date. |
| `mihstanding` | INT64 | Credit term in days; due date = document date + this value. |
| `mihlinkgl` | INT64 | General-ledger posting link status (0 = not posted). |
| `mihnouplink` | INT64 | Code controlling updates to linked documents. |
| `mihnolist` | INT64 | Number of line items on the document. |
| `mihcurc` | INT64 | Currency code (0 = Thai baht). |
| `mihvatinlist` | INT64 | Flag indicating VAT-inclusive line prices (-1 = yes, 0 = no). |
| `mihlock` | INT64 | Flag: document locked against editing (-1 = locked). |
| `mihprintn` | INT64 | Number of times the document has been printed. |
| `mihcheque` | INT64 | Flag: document settled by cheque. |
| `mihcancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihstatus` | INT64 | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `mihclearum` | INT64 | Flag: outstanding quantities of the document cleared (0 = still open). |
| `mihctermno` | INT64 | Payment-term number of the document. |
| `mihcog` | FLOAT64 | Gross document amount before discounts, excluding VAT; negative for credit notes (`BS`). |
| `mihcog_raw` | FLOAT64 | Gross document amount before discounts as recorded at source, without the credit-note sign flip. |
| `mihvatsum` | FLOAT64 | VAT amount of the document; negative for credit notes (`BS`). |
| `mihvatsum_raw` | FLOAT64 | VAT amount as recorded at source, without the credit-note sign flip. |
| `mihnetsum` | FLOAT64 | Net document total including VAT, after all discounts; negative for credit notes (`BS`). |
| `mihnetsum_raw` | FLOAT64 | Net document total as recorded at source, without the credit-note sign flip. |
| `mihdisclst` | FLOAT64 | Total of line-level discounts on the document; negative for credit notes (`BS`). |
| `mihdisclst_raw` | FLOAT64 | Total line-level discounts as recorded at source, without the credit-note sign flip. |
| `mihdischf1` | FLOAT64 | Header discount 1 amount; negative for credit notes (`BS`). |
| `mihdischf1_raw` | FLOAT64 | Header discount 1 amount as recorded at source, without the credit-note sign flip. |
| `mihdischf2` | FLOAT64 | Header discount 2 amount; negative for credit notes (`BS`). |
| `mihdischf2_raw` | FLOAT64 | Header discount 2 amount as recorded at source, without the credit-note sign flip. |
| `mihexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `mihextrasum` | FLOAT64 | Deposit amount deducted on the document, excluding VAT. |
| `mihextravat` | FLOAT64 | VAT on the deducted deposit amount. |
| `mihextracut` | INT64 | Flag indicating that a deposit deduction is applied. |
| `mihextramem` | STRING | Memo of the deducted deposit, listing the deposit receipt numbers and dates. |
| `mihrecno` | STRING | Number of the related receipt or received document. |
| `mihrecdate` | DATETIME | Date of the related receipt or received document. |
| `mihsavetag` | STRING | Save-tag marker set by the ERP when the document is saved. |
| `mihkeyuser` | STRING | User code of the person who keyed the document. |
| `mihkeydate` | DATETIME | Date and time the document was keyed. |
| `mihdocrunno` | STRING | Document running number. |
| `mihdategl` | DATETIME | General-ledger posting date. |
| `mihduepo` | DATETIME | Purchase-order due date and time. |
| `miheditlk` | DATETIME | Timestamp of the current edit lock on the document. |
| `mihiscf` | INT64 | Flag indicating a carry-forward (opening balance) document. |
| `mihissp` | INT64 | Special-document flag. |
| `mihdates1` | DATETIME | Special date 1 of the document. |
| `mihdates2` | DATETIME | Special date 2 of the document. |
| `mihnumsi` | INT64 | Special integer field of the document. |
| `mihnumsc` | FLOAT64 | Special numeric field of the document. |
| `mihvatpc` | FLOAT64 | VAT rate in percent (e.g. 7). |
| `mihincluded` | INT64 | Flag indicating VAT-inclusive document amounts. |
| `mihtaxvnos` | STRING | Separate tax invoice number issued for the document. |
| `mihtaxdate` | DATETIME | Date of the separate tax invoice. |
| `mihtaxsum` | FLOAT64 | Amount of the separate tax invoice. |
| `mihload` | INT64 | Flag indicating goods loaded for delivery (1 = loaded). |
| `mihpaiddate` | DATETIME | Date the document was fully paid. |
| `mihbookordernum` | STRING | Number of the booking (order) document linked to this document. |
| `mihsenddate` | DATETIME | Date the goods were sent. |
| `mihbl` | INT64 | Billing-note flag of the document. |
| `mihrpv` | INT64 | Receipt/payment-voucher flag of the document. |
| `mihclearcut` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `mihsettlecut` | INT64 | Flag: settlement completed (-1 = settled). |
| `moddate` | DATETIME | Date and time the document was last modified (ag01 only; NULL for the other companies). |
| `mihmemo_new` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `memo_extract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mih.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mih](/initial/raw_mac5_ag01/mih.md), [raw_mac5_aa05.mih](/initial/raw_mac5_aa05/mih.md), [raw_mac5_ab01.mih](/initial/raw_mac5_ab01/mih.md), [raw_mac5_ac02.mih](/initial/raw_mac5_ac02/mih.md), [raw_mac5_ak02.mih](/initial/raw_mac5_ak02/mih.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `MIHtype`, `MIHvnos`.
- Same document-grain purge pattern as `mil`/`mir`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mih`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MIHtype, MIHvnos, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mih`
GROUP BY company_id, MIHtype, MIHvnos
HAVING n > 1
```
