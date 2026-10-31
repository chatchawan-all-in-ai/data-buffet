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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Curated MAC5 document line table (MAC5 ERP `mil`), the line-level companion of [curated_mih](/curated/curated_mac5/curated_mih.md). It renames validated_mac5.mil columns to camelCase and, for company ag01 only, applies the split-sale rules: when validated_mac5.mih2 says a document is shared between two sales reps (percentage not 100%), the line is duplicated and its quantity/discount/gross amount/VAT/sum are multiplied by each rep's share, while the `_raw` columns keep the full values. It feeds dim_order, dim_invoice, dim_quotation, dim_delivery, fact_order, fact_invoice, the store facts (fact_order_store, fact_invoice_store, fact_backlog_store), fact_delivery and Transaction_Data_Mart.

# Grain and key

Declared `uniqueKey`: `company_id` + `milType` + `milVnos` + `milListno` (document line). For ag01 split lines the same key appears twice (once per sales rep, distinguished by `milPer` / `percent_sale`), so the declared key is not unique for them (the split rows have no discriminator in the key). Other companies are one row per line.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02); part of the key. |
| `milDay` | INT64 | Day part of the document date (pass-through of milday; same value as the header's mihDay). |
| `milMonth` | INT64 | Month part of the document date (pass-through of milmonth). |
| `milYear` | INT64 | Year part of the document date (pass-through of milyear). |
| `milType` | STRING | Document type code of the line, part of the key; joins to curated_mih.mihType (PS = sales order, IS = invoice are the types used by the store facts). |
| `milVnos` | STRING | Document number of the line, part of the key; joins to curated_mih.mihVnos. |
| `milCus` | STRING | Customer code (joins to curated_mih.mihCus; used in the split-sale match with mih2). |
| `milStk` | STRING | Stock (SKU) code of the line (joins to the product master, lowercased on both sides in downstream joins). Lines whose code starts with the Thai prefix 'บ' or 'TEST' are excluded by the store facts. |
| `milJob` | STRING | Pass-through of validated_mac5.mil.miljob; meaning not documented in the repo (likely job/project code). |
| `milDep` | STRING | Pass-through of mildep; likely department/area code (same family as mihDep), not documented for lines. |
| `milPer` | STRING | Salesperson code of the line (pass-through of milper). For split-sale rows of ag01 the second split row carries mih2.mih2per2 (the second rep) instead. |
| `milPer_raw` | STRING | Salesperson code before the split-sale override (always the original milper). |
| `milDoc` | STRING | Meaning not documented in the repo |
| `milMec` | STRING | Meaning not documented in the repo |
| `milSto` | STRING | Meaning not documented in the repo |
| `milStomt` | STRING | Meaning not documented in the repo |
| `milListno` | INT64 | Line number within the document, part of the key. |
| `milQuan` | FLOAT64 | Quantity of the line. For split-sale ag01 lines it is milQuan_raw multiplied by the rep's share (per_sale1/100 or per_sale2/100); otherwise equal to milQuan_raw. |
| `milQuan_raw` | FLOAT64 | Full quantity of the line before the split-sale share is applied. |
| `milQuanp2` | FLOAT64 | Meaning not documented in the repo |
| `milAdisc` | FLOAT64 | Line discount amount (pass-through of miladisc; likely, from the name) after the split-sale share is applied for ag01 split lines. |
| `milAdisc_raw` | FLOAT64 | milAdisc before the split-sale share is applied. |
| `milCog` | FLOAT64 | Gross line amount excluding VAT (exposed as `GrossAmountExcVat` in `Model_Invoice_Transaction`), after the split-sale share is applied for ag01 split lines. |
| `milCog_raw` | FLOAT64 | Full gross line amount excluding VAT before the split-sale share is applied. |
| `milConv` | FLOAT64 | Meaning not documented in the repo |
| `milDisca` | FLOAT64 | Pass-through of mildisca (discount amount, likely) after the split-sale share is applied for ag01 split lines. |
| `milDisca_raw` | FLOAT64 | milDisca before the split-sale share is applied. |
| `milDisct` | STRING | Meaning not documented in the repo |
| `milVat` | FLOAT64 | VAT amount of the line (likely, from the name) after the split-sale share is applied for ag01 split lines. |
| `milVat_raw` | FLOAT64 | milVat before the split-sale share is applied. |
| `milSum` | FLOAT64 | Line amount (value of the line, likely net of VAT; downstream facts sum it as sales value) after the split-sale share is applied for ag01 split lines. |
| `milSum_raw` | FLOAT64 | Full line amount before the split-sale share is applied. |
| `milCut` | INT64 | Meaning not documented in the repo |
| `milStype` | INT64 | Line type code (pass-through of milstype). Value 3 marks service/freight lines that the store facts exclude (`milstype not in (3)`). |
| `milUname` | STRING | Likely the unit-of-measure name (inferred from the name; pass-through of miluname). |
| `milDesc` | STRING | Line description (pass-through of mildesc). |
| `milVcol1` | STRING | Meaning not documented in the repo |
| `milVcol2` | STRING | Meaning not documented in the repo |
| `milVcol3` | STRING | Meaning not documented in the repo |
| `milVcol4` | STRING | Meaning not documented in the repo |
| `milCurc` | INT64 | Meaning not documented in the repo |
| `milExchg` | FLOAT64 | Meaning not documented in the repo |
| `milAcost` | FLOAT64 | Meaning not documented in the repo |
| `milPqm` | INT64 | Meaning not documented in the repo |
| `milPmfrom` | INT64 | Meaning not documented in the repo |
| `milPmto` | INT64 | Meaning not documented in the repo |
| `milTag` | INT64 | Meaning not documented in the repo |
| `milLinkvcno` | STRING | Linked document number (pass-through of millinkvcno): for invoice lines the order (PS) document they were created from, used by fact_invoice_store to find OrderSK; also the join key to mih2.mih2vnos for the split-sale percentages. |
| `milLinkvcdate` | DATETIME | Date of the linked document (pass-through of millinkvcdate). |
| `milLinkvctype` | STRING | Type of the linked document (pass-through of millinkvctype). |
| `milLinkvcdeposit` | STRING | Meaning not documented in the repo |
| `milLinkvcid` | INT64 | Pass-through of millinkvcid; id of the linked document line (likely, from the name); not documented in the repo. |
| `milClearum` | INT64 | Meaning not documented in the repo |
| `milExpdate` | DATETIME | Likely an expiry date (inferred from the name; pass-through of milexpdate). |
| `milNotes` | STRING | Free-text notes of the line (pass-through of milnotes). |
| `milNotkl` | INT64 | Meaning not documented in the repo |
| `milDelvdt` | DATETIME | Pass-through of mildelvdt; likely delivery date of the line, not documented in the repo. |
| `milDatesp` | DATETIME | Meaning not documented in the repo |
| `milNumcsp` | FLOAT64 | Meaning not documented in the repo |
| `milNumisp` | INT64 | Meaning not documented in the repo |
| `milCost` | FLOAT64 | Pass-through of milcost; likely line cost, not documented in the repo. |
| `milUcost` | FLOAT64 | Pass-through of milucost; likely unit cost, not documented in the repo. |
| `milUprice` | FLOAT64 | Likely unit price (inferred from the name; pass-through of miluprice). |
| `milUsequanp` | INT64 | Meaning not documented in the repo |
| `milVcol5` | STRING | Meaning not documented in the repo |
| `milFitem` | INT64 | Meaning not documented in the repo |
| `asatdate` | DATE | Extract date of the validated row (partition column). For ag01 rebuilt rows it is the asatdate of the latest validated row per line. |
| `percent_sale` | STRING | Share of the line credited to this row's salesperson, as a percent string such as '100.00%'. Rows that are not split carry '100.00%'; ag01 split rows carry the first and second rep shares (mih2 percentages, capped at 100) as e.g. '60.00%' and '40.00%'. |

# How it is built

- Definition: `definitions/curated/mac5/curated_mil.sqlx` (`type: "incremental"`, tags `curated`).
- `uniqueKey`: `company_id`, `milType`, `milVnos`, `milListno`.
- Storage options: `{"partitionBy": "asatdate", "clusterBy": ["company_id", "milVnos", "milType"]}`.
- Reads: [validated_mac5.mil](/validated/validated_mac5/mil.md), [validated_mac5.mih2](/validated/validated_mac5/mih2.md).
- Incremental on `uniqueKey` (tag `curated`, after `validated_mac5.mil` and `mih2`). `pre_operations` builds a TEMP table of the last `BACKFILL_DAYS` day(s) of validated lines (percent_sale hard-coded '100.00%') and DELETEs whole documents (company_id + milType + milVnos) from the table, so lines deleted at source disappear; the body then inserts that temp. `post_operations` rebuilds all ag01 rows from the full validated_mac5.mil (no window): applies the split-sale rule, deletes the documents at document grain and re-inserts (this is the expensive part).
- Approximate size (BigQuery metadata, 2026-10-31): 9,370,397 rows, 4.3 GB.

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
