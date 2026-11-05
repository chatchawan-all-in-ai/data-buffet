---
type: BigQuery Table
title: "tmp_pdf_supalai"
description: "One row = one purchase order line imported from a Supalai PDF purchase order, a record of source table `tmp_pdf_supalai` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tmp_pdf_supalai&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tmp_pdf_supalai
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tmp_pdf_supalai/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tmp_pdf_supalai` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Purchase order lines read from PDF purchase orders of the developer Supalai, one row per PO line, staged for order entry. Used by: [validated_mac5.tmp_pdf_supalai](/validated/validated_mac5/tmp_pdf_supalai.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `crdate` | STRING | Creation date of the developer purchase order as printed in the PDF (text, format varies by developer). |
| `vendorno` | STRING | Vendor number printed on the developer purchase order. |
| `vendorname` | STRING | Name of the developer company that issued the purchase order. |
| `newpo` | STRING | New purchase order flag from the PDF import. |
| `pono` | STRING | Purchase order number of the developer. |
| `podate` | STRING | Purchase order date as printed in the PDF (text). |
| `potype` | STRING | Purchase order type printed on the PDF. |
| `deliverydate` | STRING | Requested delivery date printed on the purchase order (text). |
| `siteno` | STRING | Developer project (site) code printed on the purchase order. |
| `sitename` | STRING | Developer project (site) name printed on the purchase order. |
| `siteaddress` | STRING | Site or delivery address text printed on the purchase order. |
| `totalqty` | STRING | Total quantity of the purchase order. |
| `totalamount` | STRING | Total amount of the purchase order as printed (text, may include thousand separators and currency). |
| `totalitem` | STRING | Total number of items on the purchase order. |
| `cancelpo` | STRING | Cancelled purchase order flag. |
| `termcode` | STRING | Payment term code printed on the purchase order (e.g. `PK45`, `PK30`). |
| `poremark` | STRING | Remark printed on the purchase order, such as the house plot or unit reference. |
| `quotationno` | STRING | Quotation number referenced by the purchase order. |
| `quotationdate` | STRING | Quotation date referenced by the purchase order. |
| `poitemno` | STRING | Line item number within the purchase order. |
| `artno` | STRING | Developer article (item) code of the purchase order line. |
| `artdesc` | STRING | Developer article (item) description of the purchase order line. |
| `hpeancode` | STRING | EAN barcode of the item as assigned by the developer. |
| `vdeancode` | STRING | EAN barcode of the item as assigned by the vendor. |
| `vdproductname` | STRING | Vendor product name of the purchase order line. |
| `qty` | STRING | Ordered quantity of the purchase order line (text). |
| `purchunit` | STRING | Purchase unit of the ordered quantity (e.g. `SET`, `each`, `ชุด`). |
| `price` | STRING | Line amount of the purchase order line as printed (text). |
| `qtyperunit` | STRING | Quantity per purchase unit. |
| `priceperunit` | STRING | Unit price of the purchase order line as printed (text). |
| `priceunit` | STRING | Unit that the unit price refers to (e.g. `SET`, `each`). |
| `packsize` | STRING | Pack size of the purchase order line. |
| `articleremark` | STRING | Remark of the purchase order line, such as the unit type or plot reference. |
| `freegoodsflag` | STRING | Free goods flag of the purchase order line. |
| `stk` | STRING | MAC5 stock code matched to the purchase order line. |
| `novat` | STRING | Amount or flag for the price before VAT. |
| `status` | STRING | Import status flag of the purchase order row. |
| `statusticket` | STRING | Processing status code of the imported purchase order (0 to 3). |
| `duedate` | STRING | Due date printed on the purchase order. |
| `reciver` | STRING | Receiver of the goods as entered on the purchase order (a name or the flag `1`). |
| `deladd` | STRING | Delivery address printed on the purchase order. |
| `que` | STRING | Queue number of the delivery. |
| `delvname` | STRING | Name of the delivery contact on the purchase order. |
| `delvtel` | STRING | Phone number of the delivery contact on the purchase order. |
| `credit` | STRING | Credit term code of the purchase order (e.g. `PK45`). |
| `dinsert` | STRING | Date and time the purchase order was imported. |
| `tel` | STRING | Phone number printed on the purchase order. |
| `objective` | STRING | Item purpose or description text printed on the purchase order. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tmp_pdf_supalai/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tmp_pdf_supalai`
LIMIT 100
```
