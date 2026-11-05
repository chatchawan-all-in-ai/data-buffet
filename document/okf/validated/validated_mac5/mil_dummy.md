---
type: BigQuery Table
title: "mil_dummy"
description: "One row = one document line (per company), unique on (company_id, MILday, MILmonth, MILyear, MILtype, MILvnos, MILcus, MILlistNo)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mil_dummy&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mil_dummy
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mil_dummy.sqlx"
    title: "Dataform definition (validated/mac5/mil_dummy.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `mil_dummy`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Document lines from the ERP's dummy (staging) line table, same layout as `mil`.
No other repo object reads it.

# Grain and key

One row per `company_id`, `MILday`, `MILmonth`, `MILyear`, `MILtype`, `MILvnos`, `MILcus`, `MILlistNo`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
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
| `milquan` | FLOAT64 | Quantity in the line's unit. |
| `milquanp2` | FLOAT64 | Quantity in the secondary unit. |
| `miladisc` | FLOAT64 | Header discount amount allocated to the line. |
| `milcog` | FLOAT64 | Line gross amount (quantity times unit price) before discounts, excluding VAT. |
| `milconv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion). |
| `mildisca` | FLOAT64 | Line discount amount. |
| `mildisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milvat` | FLOAT64 | VAT amount of the line. |
| `milsum` | FLOAT64 | Line net amount after the line discount, excluding VAT. |
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
| `millinkvcdate` | DATETIME | Date of the linked source document. |
| `millinkvctype` | STRING | Document type of the linked source document (e.g. `PS`, `PP`). |
| `millinkvcdeposit` | STRING | Deposit amount and VAT deducted from the linked document, stored as `amount/VAT` text. |
| `millinkvcid` | INT64 | Internal ID of the linked source-document line. |
| `milclearum` | INT64 | Flag: outstanding quantity of the line cleared (0 = still open). |
| `milexpdate` | DATETIME | Expiry date of the line item. |
| `milnotes` | STRING | Free-text line notes. |
| `milnotkl` | INT64 | Flag indicating that the line is excluded from stock reservation. |
| `mildelvdt` | DATETIME | Requested delivery date of the line. |
| `mildatesp` | DATETIME | Special date of the line. |
| `milnumcsp` | FLOAT64 | Special numeric field of the line. |
| `milnumisp` | INT64 | Special integer field of the line. |
| `milcost` | FLOAT64 | Cost amount of the line. |
| `milucost` | FLOAT64 | Unit cost of the line. |
| `miluprice` | FLOAT64 | Unit price of the line, excluding VAT. |
| `milusequanp` | INT64 | Flag indicating use of the secondary-unit quantity (1 = yes). |
| `milvcol5` | STRING | User-defined text column 5 of the line. |
| `milfitem` | INT64 | Free-item flag of the line. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mil_dummy.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mil_dummy](/initial/raw_mac5_ag01/mil_dummy.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `miltype`, `milvnos`, `milcus`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mil_dummy`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MILday, MILmonth, MILyear, MILtype, MILvnos, MILcus, MILlistNo, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mil_dummy`
GROUP BY company_id, MILday, MILmonth, MILyear, MILtype, MILvnos, MILcus, MILlistNo
HAVING n > 1
```
