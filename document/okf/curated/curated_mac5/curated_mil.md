---
type: BigQuery Table
title: "curated_mil"
description: "One row = one document line (order/invoice line) per company, with ag01 lines credited to a split-sale rep duplicated into two rows, unique on (company_id, milType, milVnos, milListno) plus the split."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_mac5&t=curated_mil&page=table"
project_id: databuffet-nonprd
dataset_id: curated_mac5
table_id: curated_mil
tags: ["curated", "curated_mac5", "mac5", "MAC5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/mac5/curated_mil.sqlx"
    title: "Dataform definition (curated/mac5/curated_mil.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Curated MAC5 document line table (MAC5 ERP `mil`), the line-level companion of [curated_mih](/curated/curated_mac5/curated_mih.md). It renames validated_mac5.mil columns to camelCase and, for company ag01 only, applies the split-sale rules: when validated_mac5.mih2 (matched on `milLinkvcno = mih2vnos` and `milCus = mih2cus`) says a document is shared between two sales reps (percentage not 100%), the line is duplicated and its quantity/discount/gross amount/VAT/sum are multiplied by each rep's share, while the `_raw` columns keep the full values.

Read by: [curated_invoice_line_cost](/curated/curated_derp/curated_invoice_line_cost.md), [dim_aging](/dimension/dim_aging.md), [dim_delivery](/dimension/dim_delivery.md), [dim_invoice](/dimension/dim_invoice.md), [dim_order](/dimension/dim_order.md), [dim_quotation](/dimension/dim_quotation.md), [fact_backlog_store](/fact/fact_backlog_store.md), [fact_delivery](/fact/fact_delivery.md), [fact_invoice](/fact/fact_invoice.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_order](/fact/fact_order.md), [fact_order_store](/fact/fact_order_store.md), [fact_transaction_delivery](/fact/fact_transaction_delivery.md), [Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md).

# Grain and key

Declared `uniqueKey`: `company_id` + `milType` + `milVnos` + `milListno` (document line). For ag01 split lines the same key appears twice (once per sales rep, distinguished by `milPer` / `percent_sale`), so the declared key is not unique for them (the split rows have no discriminator in the key). Other companies are one row per line.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02); part of the key. |
| `milDay` | INT64 | Day part of the document date. |
| `milMonth` | INT64 | Month part of the document date. |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
| `milVnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milJob` | STRING | Job code of the line (sales job or project category such as `TT`, `SHOP`, or a project number). |
| `milDep` | STRING | Department code of the line, used as the sales channel code. |
| `milPer` | STRING | Salesperson code of the line, replaced by the second salesperson's code on the second ag01 split-sale row. |
| `milPer_raw` | STRING | Original salesperson code before the split-sale override. |
| `milDoc` | STRING | Document print-form code of the line from the MAC5 `doc` master. |
| `milMec` | STRING | Memo-card code of the line, matching `mec.meccode`. |
| `milSto` | STRING | Warehouse (store) code the line is issued from, matching `sto` store codes. |
| `milStomt` | STRING | Destination warehouse code for transfer lines. |
| `milListno` | INT64 | Line number within the document. |
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milQuan_raw` | FLOAT64 | Full line quantity before split-sale allocation, with negative values for BS credit notes. |
| `milQuanp2` | FLOAT64 | Quantity in the secondary unit. |
| `milAdisc` | FLOAT64 | Allocated header discount deducted from the line amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milAdisc_raw` | FLOAT64 | Full allocated header discount before split-sale allocation, with negative values for BS credit notes. |
| `milCog` | FLOAT64 | Gross line amount before discounts excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milCog_raw` | FLOAT64 | Full gross line amount before discounts excluding VAT and before split-sale allocation, with negative values for BS credit notes. |
| `milConv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion). |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milDisca_raw` | FLOAT64 | Full line discount amount excluding VAT before split-sale allocation, with negative values for BS credit notes. |
| `milDisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milVat` | FLOAT64 | Line VAT amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milVat_raw` | FLOAT64 | Full line VAT amount before split-sale allocation, with negative values for BS credit notes. |
| `milSum` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milSum_raw` | FLOAT64 | Full net line amount excluding VAT after line and allocated header discounts and before split-sale allocation, with negative values for BS credit notes. |
| `milCut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `milStype` | INT64 | Line item type (1 = item, 2 = serial-tracked item, 3 = service). |
| `milUname` | STRING | Unit name of the line (e.g. `SET`, `ชุด`, `Pcs.`). |
| `milDesc` | STRING | Free-text line description. |
| `milVcol1` | STRING | User-defined text column 1 of the line. |
| `milVcol2` | STRING | User-defined text column 2 of the line. |
| `milVcol3` | STRING | User-defined text column 3 of the line. |
| `milVcol4` | STRING | User-defined text column 4 of the line. |
| `milCurc` | INT64 | Currency code (0 = Thai baht). |
| `milExchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `milAcost` | FLOAT64 | Average cost of the line. |
| `milPqm` | INT64 | Price-quantity mode of the line. |
| `milPmfrom` | INT64 | Start of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milPmto` | INT64 | End of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milTag` | INT64 | Tag marker of the line. |
| `milLinkvcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `milLinkvcdate` | DATETIME | Date of the linked source document. |
| `milLinkvctype` | STRING | Document type of the linked source document (e.g. `PS`, `PP`). |
| `milLinkvcdeposit` | STRING | Deposit amount and VAT deducted from the linked document, stored as `amount/VAT` text. |
| `milLinkvcid` | INT64 | Internal ID of the linked source-document line. |
| `milClearum` | INT64 | Flag: outstanding quantity of the line cleared (0 = still open). |
| `milExpdate` | DATETIME | Expiry date of the line item. |
| `milNotes` | STRING | Free-text line notes. |
| `milNotkl` | INT64 | Flag indicating that the line is excluded from stock reservation. |
| `milDelvdt` | DATETIME | Requested delivery date of the line. |
| `milDatesp` | DATETIME | Special date of the line. |
| `milNumcsp` | FLOAT64 | Special numeric field of the line. |
| `milNumisp` | INT64 | Special integer field of the line. |
| `milCost` | FLOAT64 | Cost amount of the line. |
| `milUcost` | FLOAT64 | Unit cost of the line. |
| `milUprice` | FLOAT64 | Unit price of the line, excluding VAT. |
| `milUsequanp` | INT64 | Flag indicating use of the secondary-unit quantity (1 = yes). |
| `milVcol5` | STRING | User-defined text column 5 of the line. |
| `milFitem` | INT64 | Free-item flag of the line. |
| `asatdate` | DATE | Extract date of the validated row (partition column). For ag01 rebuilt rows it is the asatdate of the latest validated row per line. |
| `percent_sale` | STRING | Share of the line credited to this row's salesperson, as a percent string such as '100.00%'. Rows that are not split carry '100.00%'; ag01 split rows carry the first and second rep shares (mih2 percentages, capped at 100) as e.g. '60%' and '33.33%' (`CONCAT(ROUND(x, 2), '%')`). |

# How it is built

- Definition: `definitions/curated/mac5/curated_mil.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `company_id`, `milType`, `milVnos`, `milListno`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["company_id", "milVnos", "milType"]}`.
- Reads: [validated_mac5.mil](/validated/validated_mac5/mil.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md).
- Incremental on `uniqueKey` (tag `curated`, after `validated_mac5.mil` and `mih2`). `pre_operations` builds a TEMP table of the last `BACKFILL_DAYS` day(s) of validated lines (percent_sale hard-coded '100.00%') and DELETEs whole documents (company_id + milType + milVnos) from the table, so lines deleted at source disappear; the body then inserts that temp. `post_operations` rebuilds all ag01 rows from the full validated_mac5.mil (no window): applies the split-sale rule, deletes the documents at document grain and re-inserts.

# Examples

Order lines of one company for the last 30 extract days, with the line value and the full value before split sales.

```sql
SELECT company_id, milVnos, milListno, milStk, milQuan, milSum, milSum_raw, percent_sale
FROM `databuffet-nonprd.curated_mac5.curated_mil`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 30 DAY)
  AND company_id = 'ag01' AND milType = 'PS'
  AND milStype NOT IN (3) AND LEFT(milStk, 1) NOT IN ('บ') AND milStk NOT LIKE 'TEST%'
```

Line values per customer from lines joined to headers on the document key.

```sql
SELECT h.company_id, h.mihCus, SUM(l.milSum) AS total_sum
FROM `databuffet-nonprd.curated_mac5.curated_mih` AS h
JOIN `databuffet-nonprd.curated_mac5.curated_mil` AS l
  ON l.company_id = h.company_id AND l.milType = h.mihType AND l.milVnos = h.mihVnos
WHERE h.mihType = 'IS' AND h.mihCancel = 0
  AND h.asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
GROUP BY h.company_id, h.mihCus
```
