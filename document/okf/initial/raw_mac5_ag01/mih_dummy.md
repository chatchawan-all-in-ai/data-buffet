---
type: BigQuery Table
title: "mih_dummy"
description: "One row = one sales order header, a record of source table `mih_dummy` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mih_dummy&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mih_dummy
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mih_dummy/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mih_dummy` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Sales order (`PS`) headers from the ERP's dummy (staging) header table, same layout as `mih`. Used by: [validated_mac5.mih_dummy](/validated/validated_mac5/mih_dummy.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
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
| `mihdelvdate` | STRING | Requested delivery date. |
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
| `mihrecdate` | STRING | Date of the related receipt or received document. |
| `mihsavetag` | STRING | Save-tag marker set by the ERP when the document is saved. |
| `mihkeyuser` | STRING | User code of the person who keyed the document. |
| `mihkeydate` | STRING | Date and time the document was keyed. |
| `mihdocrunno` | STRING | Document running number. |
| `mihdategl` | STRING | General-ledger posting date. |
| `mihduepo` | STRING | Purchase-order due date and time. |
| `miheditlk` | STRING | Timestamp of the current edit lock on the document. |
| `mihiscf` | INT64 | Flag indicating a carry-forward (opening balance) document. |
| `mihissp` | INT64 | Special-document flag. |
| `mihdates1` | STRING | Special date 1 of the document. |
| `mihdates2` | STRING | Special date 2 of the document. |
| `mihnumsi` | INT64 | Special integer field of the document. |
| `mihnumsc` | FLOAT64 | Special numeric field of the document. |
| `mihvatpc` | FLOAT64 | VAT rate in percent (e.g. 7). |
| `mihincluded` | INT64 | Flag indicating VAT-inclusive document amounts. |
| `mihtaxvnos` | STRING | Separate tax invoice number issued for the document. |
| `mihtaxdate` | STRING | Date of the separate tax invoice. |
| `mihtaxsum` | FLOAT64 | Amount of the separate tax invoice. |
| `mihload` | INT64 | Flag indicating goods loaded for delivery (1 = loaded). |
| `mihpaiddate` | STRING | Date the document was fully paid. |
| `mihbookordernum` | STRING | Number of the booking (order) document linked to this document. |
| `mihsenddate` | STRING | Date the goods were sent. |
| `mihbl` | INT64 | Billing-note flag of the document. |
| `mihrpv` | INT64 | Receipt/payment-voucher flag of the document. |
| `mihclearcut` | INT64 | Flag: outstanding amount cleared (-1 = cleared). |
| `mihsettlecut` | INT64 | Flag: settlement completed (-1 = settled). |
| `rowguid` | STRING | Row GUID assigned to the record by the source database. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mih_dummy/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mih_dummy`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.mih_dummy`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
