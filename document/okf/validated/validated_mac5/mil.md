---
type: BigQuery Table
title: "mil"
description: "One row = one document line (per company), unique on (company_id, MILtype, MILvnos, MILlistNo)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mil&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mil
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mil.sqlx"
    title: "Dataform definition (validated/mac5/mil.sqlx)"
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

Validated copy of MAC5 `mil` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. For credit notes (`miltype` `BS`) the quantity and amount columns are sign-flipped and the values before the flip are kept in the `*_raw` columns; the lines are LEFT JOINed to [mih](/validated/validated_mac5/mih.md) on company, date, type, number and customer; rows with an empty `milvnos` are dropped. Table meaning: Line items of all MAC5 trading documents (product, quantity, prices, discounts, link to the source document), one row per company, document type, document number and line number.
Used by: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [pub_sub.export_credit_note](/view/pub_sub/export_credit_note.md), [pub_sub.export_debit_note](/view/pub_sub/export_debit_note.md), [pub_sub.export_invoice](/view/pub_sub/export_invoice.md), [pub_sub.export_order](/view/pub_sub/export_order.md).

# Grain and key

One row per `company_id`, `MILtype`, `MILvnos`, `MILlistNo`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
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
| `milquan` | FLOAT64 | Quantity in the line's unit; negative for credit notes (`BS`). |
| `milquan_raw` | FLOAT64 | Quantity as recorded at source, without the credit-note sign flip. |
| `milquanp2` | FLOAT64 | Quantity in the secondary unit. |
| `miladisc` | FLOAT64 | Header discount amount allocated to the line; negative for credit notes (`BS`). |
| `miladisc_raw` | FLOAT64 | Allocated header discount as recorded at source, without the credit-note sign flip. |
| `milcog` | FLOAT64 | Line gross amount (quantity times unit price) before discounts, excluding VAT; negative for credit notes (`BS`). |
| `milcog_raw` | FLOAT64 | Line gross amount as recorded at source, without the credit-note sign flip. |
| `milconv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion). |
| `mildisca` | FLOAT64 | Line discount amount; negative for credit notes (`BS`). |
| `mildisca_raw` | FLOAT64 | Line discount amount as recorded at source, without the credit-note sign flip. |
| `mildisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milvat` | FLOAT64 | VAT amount of the line; negative for credit notes (`BS`). |
| `milvat_raw` | FLOAT64 | Line VAT amount as recorded at source, without the credit-note sign flip. |
| `milsum` | FLOAT64 | Line net amount excluding VAT, after the line discount and the allocated header discount `miladisc`; negative for credit notes (`BS`). |
| `milsum_raw` | FLOAT64 | Line net amount after the line discount as recorded at source, without the header-discount deduction or credit-note sign flip. |
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

- Definition: `definitions/validated/mac5/mil.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mil](/initial/raw_mac5_ag01/mil.md), [raw_mac5_aa05.mil](/initial/raw_mac5_aa05/mil.md), [raw_mac5_ab01.mil](/initial/raw_mac5_ab01/mil.md), [raw_mac5_ac02.mil](/initial/raw_mac5_ac02/mil.md), [raw_mac5_ak02.mil](/initial/raw_mac5_ak02/mil.md), [validated_mac5.mih](/validated/validated_mac5/mih.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `miltype`, `milvnos`.
- **Document-grain purge**: `pre_operations` builds a TEMP table of the batch and DELETEs whole documents (company_id + type + vnos) from the target before the MERGE, so lines deleted at source disappear.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mil`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MILtype, MILvnos, MILlistNo, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mil`
GROUP BY company_id, MILtype, MILvnos, MILlistNo
HAVING n > 1
```
