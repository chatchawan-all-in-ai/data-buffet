---
type: BigQuery Table
title: "main_qtspread"
description: "One row = one quotation spread (one order raised from a quotation), a record of source table `main_qtspread` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=main_qtspread&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: main_qtspread
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/main_qtspread/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `main_qtspread` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Orders raised from quotations (quotation spreads), with delivery address, contact, delivery notes, payment terms and project details.

Read by: [validated_mac5.main_qtspread](/validated/validated_mac5/main_qtspread.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Quotation spread identifier, referenced by `detail_qtspread.ref_id`, `qt_spread_to_mih.qt_spread_ref_id` and `pathfilestamper.mainqtid`. |
| `ref_id` | INT64 | Sequence number of the spread within the quotation (1 = first order from the quotation). |
| `qtid` | STRING | Quotation identifier (`tbook_quotation.id`). |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dinsert` | STRING | Date and time the row was created. |
| `dupdate` | STRING | Date and time the row was last updated. |
| `atten` | STRING | Attention or contact name for the delivery. |
| `lat` | STRING | Latitude of the delivery location. |
| `long` | STRING | Longitude of the delivery location. |
| `mapnote` | STRING | Map note for the delivery location. |
| `city` | STRING | Province of the delivery address. |
| `ctel` | STRING | Contact phone number for the delivery. |
| `ctel2` | STRING | Second contact phone number for the delivery. |
| `road` | STRING | Road of the delivery address. |
| `area` | STRING | District (amphoe) of the delivery address. |
| `district` | STRING | Sub-district (tambon) of the delivery address. |
| `postcode` | STRING | Postal code of the delivery address. |
| `caddress` | STRING | Delivery address text. |
| `podocno` | STRING | Customer purchase order number. |
| `rdosend` | STRING | Delivery method option code (1 to 6). |
| `checknote` | STRING | Delivery checklist note (e.g. notify the customer before delivery). |
| `checknote2` | STRING | Second delivery checklist note (e.g. deliver with the tax invoice). |
| `checknote3` | STRING | Third delivery checklist note (e.g. collect cheque or cash on delivery). |
| `checknote4` | STRING | Fourth delivery checklist note. |
| `checknotemoney` | STRING | Amount to collect on delivery. |
| `textnote` | STRING | Free-text delivery note. |
| `status` | STRING | Status code of the quotation spread (1, 2, 3). |
| `editnote` | STRING | Note explaining an edit of the spread (e.g. wrong price, duplicate). |
| `editnotedate` | STRING | Date and time of the edit note. |
| `delvdate` | STRING | Requested delivery date (text). |
| `transferfg` | STRING | Factory or warehouse code to transfer the goods from (e.g. `LP`, `KK`, `HY`, `UB`, `PK`, `KTB`). |
| `meccode` | STRING | Customer branch (ship-to) code, matching `mec.meccode`. |
| `subcontract` | STRING | MAC5 customer (debtor) code of the subcontractor, or a placeholder when none is chosen. |
| `blueprint` | STRING | House plot or unit reference of the delivery. |
| `projectname` | STRING | Developer project name of the order. |
| `mihjob` | STRING | Job code of the document (sales job or project category such as `TT`, `REL`, `GOV`, or a project number). |
| `repeatblueprint` | INT64 | Repeat-delivery flag for the same plot (1 = repeat). |
| `noteblueprint` | STRING | Note for a repeat delivery to the same plot. |
| `discountthreepercent` | INT64 | Three-percent discount flag (1 = applied). |
| `paybycash` | INT64 | Pay-by-cash flag (1 = cash). |
| `creditterm` | INT64 | Credit term option code (0, 1, 2). |
| `moneydeposit` | FLOAT64 | Deposit amount paid for the order. |
| `extrasum` | INT64 | Extra charge flag or amount of the order. |
| `agent` | STRING | Dealer customer code and name the order goes through. |
| `termpayment` | STRING | Payment terms text (e.g. transfer before delivery). |
| `discountcash` | INT64 | Cash discount flag. |
| `paytype` | STRING | Payment type (e.g. transfer, cash, credit card). |
| `amount` | FLOAT64 | Order amount entered for the payment. |
| `refer_order_allkons_m` | STRING | Allkons order number referenced by this order (`order_from_allkon_m.order_no`). |
| `etax` | INT64 | E-tax invoice flag (1 = issue an e-tax invoice). |
| `etax_email` | STRING | Email address that receives the e-tax invoice. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/main_qtspread/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.main_qtspread`
LIMIT 100
```
