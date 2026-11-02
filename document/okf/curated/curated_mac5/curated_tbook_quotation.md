---
type: BigQuery Table
title: "curated_tbook_quotation"
description: "One row = the latest revision of one quotation per company, unique on (company_id, Running)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mac5&t=curated_tbook_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: curated_mac5
table_id: curated_tbook_quotation
tags: ["curated", "curated_mac5", "mac5", "MAC5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/mac5/curated_tbook_quotation.sqlx"
    title: "Dataform definition (curated/mac5/curated_tbook_quotation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Curated MAC5 sales quotation header (source table tbook_quotation of the MAC5 booking module): the latest revision per quotation, with columns renamed to PascalCase. Used to build dim_quotation (quotation attributes, customer and project parsed out of the Atten/Project text, tied to the orders and invoices that reference the quotation code) and by the Transaction_Data_Mart view (QuotationID, QuotationCode for each order).

# Grain and key

One row per `company_id` + `Running` (quotation code). Duplicates across revisions are removed with `QUALIFY ROW_NUMBER() OVER (PARTITION BY company_id, running ORDER BY rev DESC, id DESC) = 1`, so only the highest `Rev` survives.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `ID` | INT64 | Quotation identifier, referenced by `tbook_quodetail.linkid`. |
| `Running` | STRING | Quotation number referenced by orders, with missing source numbers represented as an empty string. |
| `Atten` | STRING | Attention or contact text of the quotation, including a customer code before a backslash when supplied. |
| `Address` | STRING | Customer address text. |
| `SDate` | DATE | Quotation date. |
| `Project` | STRING | Project text of the quotation, including a project or customer code before a backslash when supplied. |
| `TelePhone` | BOOL | Flag indicating whether to show the telephone number, TRUE when the source marker is nonblank. |
| `Sale` | BOOL | Flag indicating whether to show the salesperson, TRUE when the source marker is nonblank. |
| `PriceValidity` | STRING | Price validity text. |
| `TermDelivery` | STRING | Delivery terms text. |
| `TermPayment` | STRING | Payment terms text (e.g. credit 30 days). |
| `UInsert` | STRING | Employee code of the user who created the row. |
| `DInsert` | STRING | Date and time the row was created (text). |
| `UUpdate` | STRING | Employee code of the user who last updated the row. |
| `Dupdate` | STRING | Date and time the row was last updated (text). |
| `Agent1` | STRING | Customer (dealer) code and name the quotation is issued to; the first word is the MAC5 debtor code. |
| `Agent2` | STRING | Second customer (dealer) code and name. |
| `Period` | STRING | Period text of the quotation. |
| `Position` | STRING | Position of the contact person (e.g. purchasing, project manager). |
| `Vat` | INT64 | VAT flag (1 = prices include VAT). |
| `Disc` | INT64 | Discount flag (1 = discount shown). |
| `ExtraSum` | INT64 | Extra amount flag (1 = extra amount applies). |
| `ExtraDesc` | STRING | Extra amount or discount text of the quotation. |
| `DateStart1` | STRING | Start date of price period 1. |
| `DateEnd1` | STRING | End date of price period 1. |
| `DateStart2` | STRING | Start date of price period 2. |
| `DateEnd2` | STRING | End date of price period 2. |
| `CashStatus` | INT64 | Cash sale flag (1 = cash). |
| `Note` | STRING | Free-text note of the quotation. |
| `NoteForApp` | STRING | Note to the approver with matching telephone numbers replaced by xxx-xxx-xxxx. |
| `MemoForApp` | STRING | Memo to the approver. |
| `Rev` | INT64 | Revision number of the quotation (0 = original). |
| `TypeCus` | INT64 | Customer type code (0, 1, 2). |
| `Channel` | STRING | Sales channel code (e.g. `TT`, `DT`, `DC`, `PS1`, `DD`, `PS2-1`, `DG`, `EX`). |
| `Channel2` | STRING | Order channel group code (e.g. `AR`, `CRC`, `A`, `PS1`, `PS2-1`, `EX`). |
| `TypePrice` | INT64 | Price type code (1, 2). |
| `FOB` | INT64 | FOB flag. |
| `Cancel` | INT64 | Cancel flag (1 = cancelled). |
| `AppType` | INT64 | Approval type identifier (`tbook_apptype.id`). |
| `TypeDeb` | STRING | Customer type text. |
| `SaleDep` | STRING | Sales department. |
| `TypeProject` | STRING | Project type. |
| `SelectStatus` | INT64 | Selection status code (0, 1, 2). |
| `ConpoStatus` | INT64 | Confirmed-PO status flag. |
| `Lat` | STRING | Latitude of the delivery location. |
| `Long` | STRING | Longitude of the delivery location. |
| `MapNote` | STRING | Map note for the delivery location. |
| `FileUpload` | STRING | Uploaded map image file name. |
| `City` | STRING | Province of the delivery address. |
| `RdoSend` | INT64 | Delivery method option code (0 to 3). |
| `CustomerName` | BOOL | Flag indicating whether to show the customer name, TRUE when the source marker is nonblank. |
| `CustomerTelePhone` | BOOL | Flag indicating whether to show the customer telephone number, TRUE when the source marker is nonblank. |
| `CustomerAddress` | STRING | Customer delivery address. |
| `CheckNote` | STRING | Delivery checklist note. |
| `TextNote` | STRING | Free-text delivery note. |
| `StatusSpread` | INT64 | Spread status flag (1 = spread into orders). |
| `ChkBox` | INT64 | Checkbox flag. |
| `FobStt` | INT64 | FOB status code (0, 2). |
| `QuotationRef` | INT64 | Reference quotation identifier. |
| `CustomerId` | INT64 | Customer identifier. |
| `CustomerGroup` | INT64 | Customer group identifier. |
| `QuotationId` | INT64 | Quotation identifier from a linked system. |
| `EStatus` | INT64 | E-status code. |
| `Area` | STRING | District (amphoe) of the delivery address. |
| `District` | STRING | Sub-district (tambon) of the delivery address. |
| `PostCode` | STRING | Postal code of the delivery address. |
| `QtStepPrice` | INT64 | Step-price quotation flag. |
| `ExtraDis` | STRING | Extra discount percent (e.g. 3, 4, 5). |

# How it is built

- Definition: `definitions/curated/mac5/curated_tbook_quotation.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `company_id`, `running`.
- Storage options: `{"clusterBy": ["company_id", "running", "cashstatus", "cancel"]}`.
- Reads: [validated_mac5.tbook_quotation](/validated/validated_mac5/tbook_quotation.md).
- Declared `type: "incremental"` (tag `curated`, after `validated_mac5.tbook_quotation`) with MERGE on `uniqueKey`, but the partition and the incremental window filter are commented out, so every run reads the whole validated table and behaves like a full rebuild.
- Approximate size (BigQuery metadata, 2026-10-31): 260,034 rows, 211.4 MB.

# Examples

Latest revision of one quotation.

```sql
SELECT company_id, Running, Rev, SDate, Channel, Cancel, CashStatus
FROM `databuffet-nonprd.curated_mac5.curated_tbook_quotation`
WHERE company_id = 'ag01' AND Running = 'REPLACE_WITH_QUOTATION_CODE'
```

Quotation counts per channel and cancel flag.

```sql
SELECT company_id, Channel, Cancel, COUNT(*) AS n
FROM `databuffet-nonprd.curated_mac5.curated_tbook_quotation`
GROUP BY company_id, Channel, Cancel
ORDER BY n DESC
```
