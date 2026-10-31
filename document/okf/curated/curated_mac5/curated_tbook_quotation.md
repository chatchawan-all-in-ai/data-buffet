---
type: BigQuery Table
title: "curated_tbook_quotation"
description: "One row = the latest revision of one quotation per company, unique on (company_id, Running)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mac5&t=curated_tbook_quotation&page=table"
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
| `company_id` | STRING | Company code; part of the key. |
| `ID` | INT64 | Numeric row id of the quotation in the source (tbook_quotation.id); joined to tbook_quodetail.linkid for detail lines; larger id wins a tie on Rev. |
| `Running` | STRING | Quotation code (running number), part of the key; NULL becomes ''. Matches curated_mih.mihRef1 of the sales orders created from the quotation. |
| `Atten` | STRING | Attention / contact text of the quotation (free text; dim_quotation parses a customer id from the part before a backslash). |
| `Address` | STRING | Address text of the quotation. |
| `SDate` | DATE | Quotation date. |
| `Project` | STRING | Project text of the quotation (dim_quotation splits it on a backslash to extract a customer id or a numeric project code). |
| `TelePhone` | BOOL | Telephone of the contact (typed BOOL in the table). |
| `Sale` | BOOL | Sales person field (typed BOOL in the table). |
| `PriceValidity` | STRING | Price validity text (pass-through of price_validity). |
| `TermDelivery` | STRING | Delivery terms text. |
| `TermPayment` | STRING | Payment terms text. |
| `UInsert` | STRING | User who inserted the row (pass-through of uinsert). |
| `DInsert` | STRING | Insert datetime-like text (pass-through of dinsert); the channel logic in dim_customer_report_info orders by it. |
| `UUpdate` | STRING | User who last updated the row. |
| `Dupdate` | STRING | Last update datetime-like text. |
| `Agent1` | STRING | First agent field; the first non-empty word is used as the customer debcode in the segment-by-channel logic of dim_customer_report_info. |
| `Agent2` | STRING | Second agent field; meaning not documented in the repo. |
| `Period` | STRING | Meaning not documented in the repo |
| `Position` | STRING | Meaning not documented in the repo |
| `Vat` | INT64 | VAT field of the quotation (pass-through of vat; likely VAT rate or flag). |
| `Disc` | INT64 | Discount field of the quotation (pass-through of disc). |
| `ExtraSum` | INT64 | Extra amount field (pass-through of extrasum). |
| `ExtraDesc` | STRING | Meaning not documented in the repo |
| `DateStart1` | STRING | Meaning not documented in the repo |
| `DateEnd1` | STRING | Meaning not documented in the repo |
| `DateStart2` | STRING | Meaning not documented in the repo |
| `DateEnd2` | STRING | Meaning not documented in the repo |
| `CashStatus` | INT64 | Cash status code (pass-through of cashstatus; also a cluster column). |
| `Note` | STRING | Free-text note. |
| `NoteForApp` | STRING | Meaning not documented in the repo |
| `MemoForApp` | STRING | Meaning not documented in the repo |
| `Rev` | INT64 | Revision number of the quotation; the row with the highest Rev (then highest ID) is kept per (company_id, Running). |
| `TypeCus` | INT64 | Meaning not documented in the repo |
| `Channel` | STRING | Sales channel code of the quotation (e.g. TT/DC/DA/DG/DD/DT/DR are the values the channel-segment logic uses). |
| `Channel2` | STRING | Meaning not documented in the repo |
| `TypePrice` | INT64 | Meaning not documented in the repo |
| `FOB` | INT64 | Meaning not documented in the repo |
| `Cancel` | INT64 | Cancel flag of the quotation (pass-through of cancel; also a cluster column). |
| `AppType` | INT64 | Meaning not documented in the repo |
| `TypeDeb` | STRING | Meaning not documented in the repo |
| `SaleDep` | STRING | Meaning not documented in the repo |
| `TypeProject` | STRING | Meaning not documented in the repo |
| `SelectStatus` | INT64 | Meaning not documented in the repo |
| `ConpoStatus` | INT64 | Meaning not documented in the repo |
| `Lat` | STRING | Latitude text (pass-through of lat). |
| `Long` | STRING | Longitude text (pass-through of long). |
| `MapNote` | STRING | Meaning not documented in the repo |
| `FileUpload` | STRING | Meaning not documented in the repo |
| `City` | STRING | City text. |
| `RdoSend` | INT64 | Meaning not documented in the repo |
| `CustomerName` | BOOL | Customer name field (typed BOOL in the table). |
| `CustomerTelePhone` | BOOL | Customer telephone field (typed BOOL in the table). |
| `CustomerAddress` | STRING | Customer address text. |
| `CheckNote` | STRING | Meaning not documented in the repo |
| `TextNote` | STRING | Meaning not documented in the repo |
| `StatusSpread` | INT64 | Meaning not documented in the repo |
| `ChkBox` | INT64 | Meaning not documented in the repo |
| `FobStt` | INT64 | Meaning not documented in the repo |
| `QuotationRef` | INT64 | Pass-through of quotation_ref; meaning not documented in the repo. |
| `CustomerId` | INT64 | Pass-through of customer_id (numeric); meaning not documented in the repo. |
| `CustomerGroup` | INT64 | Meaning not documented in the repo |
| `QuotationId` | INT64 | Pass-through of quotation_id; meaning not documented in the repo. |
| `EStatus` | INT64 | Meaning not documented in the repo |
| `Area` | STRING | Area text. |
| `District` | STRING | District text. |
| `PostCode` | STRING | Postal code text. |
| `QtStepPrice` | INT64 | Meaning not documented in the repo |
| `ExtraDis` | STRING | Meaning not documented in the repo |

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
