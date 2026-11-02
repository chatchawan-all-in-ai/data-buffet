---
type: BigQuery Table
title: "mih_billing"
description: "One row = one billing document header from source table `mih_billing` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mih_billing&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mih_billing
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mih_billing.sqlx"
    title: "Dataform definition (validated/mac5/mih_billing.sqlx)"
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

Validated copy of MAC5 `mih_billing`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Billing document (`BL`) headers with the customer's tax ID and branch, same layout as `mih`.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

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
| `mihcog` | FLOAT64 | Gross document amount before discounts, excluding VAT. |
| `mihvatsum` | FLOAT64 | VAT amount of the document. |
| `mihnetsum` | FLOAT64 | Net document total including VAT, after all discounts. |
| `mihdisclst` | FLOAT64 | Total of line-level discounts on the document. |
| `mihdischf1` | FLOAT64 | Header discount 1 amount. |
| `mihdischf2` | FLOAT64 | Header discount 2 amount. |
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
| `mihdebbranch` | STRING | Customer branch number for the tax invoice (`00000` = head office). |
| `mihdebtaxnos` | STRING | Customer 13-digit tax identification number. |

# How it is built

- Definition: `definitions/validated/mac5/mih_billing.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mih_billing](/initial/raw_mac5_ag01/mih_billing.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `mihtype`, `mihvnos`, `mihcus`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,971 rows, 3.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mih_billing`
LIMIT 100
```
