---
type: BigQuery Table
title: "tmp_pdf_pruksa"
description: "One row = one purchase order line imported from a Pruksa PDF purchase order from source table `tmp_pdf_pruksa` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tmp_pdf_pruksa&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tmp_pdf_pruksa
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tmp_pdf_pruksa.sqlx"
    title: "Dataform definition (validated/mac5/tmp_pdf_pruksa.sqlx)"
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

Validated copy of MAC5 `tmp_pdf_pruksa`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Purchase order lines read from PDF purchase orders of the developer Pruksa Real Estate, one row per PO line, staged for order entry.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
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
| `attfile` | STRING | Attachment flag of the purchase order row (1 = file attached). |
| `statusticket` | STRING | Processing status code of the imported purchase order (0 to 3). |
| `duedate` | STRING | Due date printed on the purchase order. |
| `reciver` | STRING | Receiver of the goods as entered on the purchase order (a name or the flag `1`). |
| `deladd` | STRING | Delivery address printed on the purchase order. |
| `que` | STRING | Queue number of the delivery. |
| `delvname` | STRING | Name of the delivery contact on the purchase order. |
| `delvtel` | STRING | Phone number of the delivery contact on the purchase order. |
| `credit` | STRING | Credit term code of the purchase order (e.g. `PK45`). |
| `dinsert` | DATETIME | Date and time the purchase order was imported. |

# How it is built

- Definition: `definitions/validated/mac5/tmp_pdf_pruksa.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tmp_pdf_pruksa](/initial/raw_mac5_ag01/tmp_pdf_pruksa.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `vendorno`.
- Approximate size (BigQuery metadata, 2026-10-31): 19,992 rows, 3.2 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tmp_pdf_pruksa`
LIMIT 100
```
