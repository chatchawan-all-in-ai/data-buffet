---
type: BigQuery Table
title: "tbook_quodetail"
description: "One row = one quotation detail line, a record of source table `tbook_quodetail` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tbook_quodetail&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tbook_quodetail
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tbook_quodetail/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tbook_quodetail` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Item lines of quotations: stock code, quantity, list price, discounts, net price, total and line type; source of fact_quotation.

Read by: [validated_mac5.tbook_quodetail](/validated/validated_mac5/tbook_quodetail.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Quotation detail line identifier. |
| `linkid` | INT64 | Quotation identifier (`tbook_quotation.id`) the line belongs to. |
| `stkcode` | STRING | MAC5 stock code of the item. |
| `stkdesc` | STRING | Item description. |
| `quantity` | FLOAT64 | Quoted quantity. |
| `lp` | FLOAT64 | List price per unit. |
| `nd` | FLOAT64 | Normal discount percent applied to the list price. |
| `sd1` | FLOAT64 | Step discount 1 percent. |
| `sd2` | FLOAT64 | Step discount 2 percent. |
| `sd3` | FLOAT64 | Step discount 3 percent. |
| `dispercent` | FLOAT64 | Discount amount of the line (negative value). |
| `crc` | FLOAT64 | CRC rate percent of the line. |
| `price` | FLOAT64 | Net unit price. |
| `total` | FLOAT64 | Line total amount. |
| `priceforag` | FLOAT64 | Unit price for the dealer (agent). |
| `com` | FLOAT64 | Commission amount of the line. |
| `setcb` | INT64 | Number of sets in the combo line. |
| `type` | STRING | Line type (`ขาย` = sale, `แถม` = free item, `แถมจากโปรโมชั่น` = promotion giveaway, `ข้อมูล Comboset` = combo-set component, `ชุดข้อมูลสี` = colour set). |
| `status` | STRING | Line status label (e.g. `ขายได้`, `ทำสลพ`, `แถมจากโปรโมชั่น`, `ข้อมูล Comboset`). |
| `sent` | STRING | Delivery date of the line (text). |
| `datepart` | STRING | Delivery time slot (`เช้า` = morning, `บ่าย` = afternoon). |
| `fg` | STRING | Factory or warehouse code that supplies the item (e.g. `KTB`, `HY`, `LP`, `KK`, `PK`, `UB`). |
| `pic` | STRING | Image file name attached to the line. |
| `productcp` | STRING | Competitor product or brand quoted against (e.g. `WAVE`, `BUDDY`). |
| `pricecp` | FLOAT64 | Competitor price. |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dinsert` | STRING | Date and time the row was created (text). |
| `dupdate` | STRING | Date and time the row was last updated (text). |
| `giveaway` | STRING | Giveaway flag of the line. |
| `givestk` | STRING | Stock code of the giveaway item. |
| `bgcount` | STRING | Count value of the line. |
| `orderno` | INT64 | Order number of the line. |
| `lat` | STRING | Latitude of the delivery location. |
| `long` | STRING | Longitude of the delivery location. |
| `mapnote` | STRING | Map note for the delivery location. |
| `fileupload` | STRING | Uploaded file name. |
| `city` | STRING | Province of the delivery address. |
| `rdosend` | INT64 | Delivery method option code. |
| `cname` | STRING | Customer contact name. |
| `ctel` | STRING | Customer contact phone number. |
| `caddress` | STRING | Customer delivery address. |
| `checknote` | STRING | Delivery checklist note. |
| `textnote` | STRING | Free-text note of the line, such as a paint colour formula. |
| `ref_quodetail` | INT64 | Parent quotation detail line in the same quotation (`tbook_quodetail.id`). |
| `productgrade` | INT64 | Product grade code (0, 1, 2). |
| `fobprice` | STRING | FOB price of the line. |
| `isshow` | INT64 | Show-on-quotation flag (1 = shown). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tbook_quodetail/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tbook_quodetail`
LIMIT 100
```
