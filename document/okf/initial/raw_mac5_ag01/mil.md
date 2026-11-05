---
type: BigQuery Table
title: "mil"
description: "One row = one document line, a record of source table `mil` (MAC5 for company `ag01`) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=mil&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: mil
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/mil/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `mil` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Line items of all MAC5 trading documents (product, quantity, prices, discounts, link to the source document), one row per company, document type, document number and line number.

Read by: [validated_mac5.mil](/validated/validated_mac5/mil.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `milday` | INT64 | Day part of the document date. |
| `milmonth` | INT64 | Month part of the document date. |
| `milyear` | INT64 | Year part of the document date (Gregorian). |
| `miltype` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milvnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milcus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milstk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `miljob` | STRING | Job code of the line (sales job or project category such as `TT`, `SHOP`, or a project number). |
| `mildep` | STRING | Department code of the line, used as the sales channel code. |
| `milper` | STRING | Salesperson (employee) code of the line. |
| `mildoc` | STRING | Document print-form code of the line from the MAC5 `doc` master. |
| `milmec` | STRING | Memo-card code of the line, matching `mec.meccode`. |
| `milsto` | STRING | Warehouse (store) code the line is issued from, matching `sto` store codes. |
| `milstomt` | STRING | Destination warehouse code for transfer lines. |
| `millistno` | INT64 | Line number within the document. |
| `milquan` | FLOAT64 | Quantity in the line's unit, as recorded at source. |
| `milquanp2` | FLOAT64 | Quantity in the secondary unit. |
| `miladisc` | FLOAT64 | Header discount amount allocated to the line, as recorded at source. |
| `milcog` | FLOAT64 | Line gross amount (quantity times unit price) before discounts, excluding VAT, as recorded at source. |
| `milconv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion). |
| `mildisca` | FLOAT64 | Line discount amount, as recorded at source. |
| `mildisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milvat` | FLOAT64 | VAT amount of the line, as recorded at source. |
| `milsum` | FLOAT64 | Line net amount excluding VAT after the line discount, before the allocated header discount, as recorded at source. |
| `milcut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `milstype` | INT64 | Line item type (1 = item, 2 = serial-tracked item, 3 = service). |
| `miluname` | STRING | Unit name of the line (e.g. `SET`, `ชุด`, `Pcs.`). |
| `mildesc` | STRING | Free-text line description. |
| `milvcol1` | STRING | User-defined text column 1 of the line. |
| `milvcol2` | STRING | User-defined text column 2 of the line. |
| `milvcol3` | STRING | User-defined text column 3 of the line. |
| `milvcol4` | STRING | User-defined text column 4 of the line. |
| `milcurc` | INT64 | Currency code (0 = Thai baht). |
| `milexchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `milacost` | FLOAT64 | Average cost of the line. |
| `milpqm` | INT64 | Price-quantity mode of the line. |
| `milpmfrom` | INT64 | Start of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milpmto` | INT64 | End of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `miltag` | INT64 | Tag marker of the line. |
| `millinkvcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `millinkvcdate` | STRING | Date of the linked source document. |
| `millinkvctype` | STRING | Document type of the linked source document (e.g. `PS`, `PP`). |
| `millinkvcdeposit` | STRING | Deposit amount and VAT deducted from the linked document, stored as `amount/VAT` text. |
| `millinkvcid` | INT64 | Internal ID of the linked source-document line. |
| `milclearum` | INT64 | Flag: outstanding quantity of the line cleared (0 = still open). |
| `milexpdate` | STRING | Expiry date of the line item. |
| `milnotes` | STRING | Free-text line notes. |
| `milnotkl` | INT64 | Flag indicating that the line is excluded from stock reservation. |
| `mildelvdt` | STRING | Requested delivery date of the line. |
| `mildatesp` | STRING | Special date of the line. |
| `milnumcsp` | FLOAT64 | Special numeric field of the line. |
| `milnumisp` | INT64 | Special integer field of the line. |
| `milcost` | FLOAT64 | Cost amount of the line. |
| `milucost` | FLOAT64 | Unit cost of the line. |
| `miluprice` | FLOAT64 | Unit price of the line, excluding VAT. |
| `milusequanp` | INT64 | Flag indicating use of the secondary-unit quantity (1 = yes). |
| `milvcol5` | STRING | User-defined text column 5 of the line. |
| `milfitem` | INT64 | Free-item flag of the line. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/mil/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.mil`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_mac5_ag01.mil`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
