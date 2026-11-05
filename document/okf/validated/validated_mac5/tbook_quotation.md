---
type: BigQuery Table
title: "tbook_quotation"
description: "One row = one quotation revision (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_quotation&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbook_quotation
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_quotation.sqlx"
    title: "Dataform definition (validated/mac5/tbook_quotation.sqlx)"
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

Validated copy of MAC5 `tbook_quotation`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. Phone numbers in `noteforapp` are masked as `xxx-xxx-xxxx` (REGEXP_REPLACE). Table meaning: Sales quotations of the quotation app (header per revision), with customer, project, channel, terms and approval type; source of curated_tbook_quotation.
Used by: [curated_mac5.curated_tbook_quotation](/curated/curated_mac5/curated_tbook_quotation.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md).

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Quotation identifier, referenced by `tbook_quodetail.linkid`. |
| `running` | STRING | Quotation number (e.g. `QT32-61`), referenced by `mih.mihref1` of orders made from it. |
| `atten` | STRING | Attention or contact text of the quotation, including a customer code before a backslash when supplied. |
| `address` | STRING | Customer address text. |
| `sdate` | DATE | Quotation date. |
| `project` | STRING | Project text of the quotation, including a project or customer code before a backslash when supplied. |
| `tel` | BOOL | Flag indicating whether to show the telephone number, TRUE when the source marker is nonblank. |
| `sale` | BOOL | Flag indicating whether to show the salesperson, TRUE when the source marker is nonblank. |
| `price_validity` | STRING | Price validity text. |
| `termdelivery` | STRING | Delivery terms text. |
| `termpayment` | STRING | Payment terms text (e.g. credit 30 days). |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `dinsert` | STRING | Date and time the row was created (text). |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dupdate` | STRING | Date and time the row was last updated (text). |
| `agent1` | STRING | Customer (dealer) code and name the quotation is issued to; the first word is the MAC5 debtor code. |
| `agent2` | STRING | Second customer (dealer) code and name. |
| `period` | STRING | Period text of the quotation. |
| `pos` | STRING | Position of the contact person (e.g. purchasing, project manager). |
| `vat` | INT64 | VAT flag (1 = prices include VAT). |
| `disc` | INT64 | Discount flag (1 = discount shown). |
| `extrasum` | INT64 | Extra amount flag (1 = extra amount applies). |
| `extradesc` | STRING | Extra amount or discount text of the quotation. |
| `date1st` | STRING | Start date of price period 1. |
| `date1end` | STRING | End date of price period 1. |
| `date2st` | STRING | Start date of price period 2. |
| `date2end` | STRING | End date of price period 2. |
| `cashstatus` | INT64 | Cash sale flag (1 = cash). |
| `note` | STRING | Free-text note of the quotation. |
| `noteforapp` | STRING | Note to the approver with matching telephone numbers replaced by xxx-xxx-xxxx. |
| `memoforapp` | STRING | Memo to the approver. |
| `rev` | INT64 | Revision number of the quotation (0 = original). |
| `typecus` | INT64 | Customer type code (0, 1, 2). |
| `channel` | STRING | Sales channel code (e.g. `TT`, `DT`, `DC`, `PS1`, `DD`, `PS2-1`, `DG`, `EX`). |
| `channel2` | STRING | Order channel group code (e.g. `AR`, `CRC`, `A`, `PS1`, `PS2-1`, `EX`). |
| `typeprice` | INT64 | Price type code (1, 2). |
| `fob` | INT64 | FOB flag. |
| `cancel` | INT64 | Cancel flag (1 = cancelled). |
| `apptype` | INT64 | Approval type identifier (`tbook_apptype.id`). |
| `typedeb` | STRING | Customer type text. |
| `saledep` | STRING | Sales department. |
| `typeproject` | STRING | Project type. |
| `selectstatus` | INT64 | Selection status code (0, 1, 2). |
| `conpostatus` | INT64 | Confirmed-PO status flag. |
| `lat` | STRING | Latitude of the delivery location. |
| `long` | STRING | Longitude of the delivery location. |
| `mapnote` | STRING | Map note for the delivery location. |
| `fileupload` | STRING | Uploaded map image file name. |
| `city` | STRING | Province of the delivery address. |
| `rdosend` | INT64 | Delivery method option code (0 to 3). |
| `cname` | BOOL | Flag indicating whether to show the customer name, TRUE when the source marker is nonblank. |
| `ctel` | BOOL | Flag indicating whether to show the customer telephone number, TRUE when the source marker is nonblank. |
| `caddress` | STRING | Customer delivery address. |
| `checknote` | STRING | Delivery checklist note. |
| `textnote` | STRING | Free-text delivery note. |
| `statusspread` | INT64 | Spread status flag (1 = spread into orders). |
| `chkbox` | INT64 | Checkbox flag. |
| `fobstt` | INT64 | FOB status code (0, 2). |
| `quotation_ref` | INT64 | Reference quotation identifier. |
| `customer_id` | INT64 | Customer identifier. |
| `customer_group` | INT64 | Customer group identifier. |
| `quotation_id` | INT64 | Quotation identifier from a linked system. |
| `estatus` | INT64 | E-status code. |
| `area` | STRING | District (amphoe) of the delivery address. |
| `district` | STRING | Sub-district (tambon) of the delivery address. |
| `postcode` | STRING | Postal code of the delivery address. |
| `qtstepprice` | INT64 | Step-price quotation flag. |
| `extradis` | STRING | Extra discount percent (e.g. 3, 4, 5). |

# How it is built

- Definition: `definitions/validated/mac5/tbook_quotation.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_quotation](/initial/raw_mac5_ag01/tbook_quotation.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY extradesc desc, cname desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_quotation`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbook_quotation`
GROUP BY company_id, id
HAVING n > 1
```
