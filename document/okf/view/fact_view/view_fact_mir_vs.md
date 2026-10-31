---
type: BigQuery View
title: "view_fact_mir_vs"
description: "One row = one billing (mirtype VS) line of fact_mir_vs per company, extended with the AgingSK of the invoice it bills; BillingSK is unique."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_mir_vs&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_mir_vs
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_mir_vs.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_mir_vs.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The BI-facing version of the `fact_mir_vs` billing fact. It returns every `fact_mir_vs` column plus `AgingSK`, the link to the AR aging dimension ([dim_aging](/dimension/dim_aging.md)), so a billing line can be analysed together with the invoice's outstanding amount and aging bucket.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

One row per `BillingSK` (the key of [fact_mir_vs](/fact/fact_mir_vs.md)); natural key (company_id, mirtype, mirvnos, mirlistno, mirbinvno). `dim_aging` can have more than one row per invoice number (different `cfsTypeID`), so the join would multiply rows; the view ends with `QUALIFY ROW_NUMBER() OVER (PARTITION BY t1.BillingSK ORDER BY t2.AgingSK DESC) = 1`, keeping the row count exactly equal to `fact_mir_vs`.

# Schema

| Column | Type | Description |
|---|---|---|
| `AgingSK` | INT64 | SK of `dim_aging` for the invoice, joined on `mirbinvno = cfsvnosid` and `company_id = companyID`. When several `dim_aging` rows match (different `cfsTypeID`) the highest AgingSK is kept. NULL when the invoice has no aging row. Regenerated daily. |
| `BillingSK` | INT64 | Row key of `fact_mir_vs` = `ROW_NUMBER()` over (company_id, mirtype, mirvnos, mirlistno, mirbinvno). Unique in this view (the QUALIFY guarantees it). Regenerated daily. |
| `CollectSK` | INT64 | SK of `dim_collection_status`, matched on company + year + month + customer of the document; NULL when no collection-status row exists. Regenerated daily like all full-rebuild dim SKs. |
| `Actions` | STRING | Collection action text from `dim_collection_status` (matched as for CollectSK). |
| `Justification` | STRING | Collection justification text from `dim_collection_status`. |
| `Responsible` | STRING | Person/role responsible for collection, from `dim_collection_status`. |
| `CustomerSK` | INT64 | SK of `dim_customer` (match `mircus` = `debcode` + company). `dim_customer` is a MERGE dim with stable SKs. |
| `InvoiceSK` | INT64 | SK of `dim_invoice` (match on invoice number, type, customer, date and company, first SK kept). `dim_invoice` is a MERGE dim with stable SKs. |
| `CompanySK` | INT64 | SK of `dim_company` (match `company_id`); stable across days. |
| `duedate` | DATE | Due date of the billed invoice: `PARSE_DATE('%d/%m/%Y', SUBSTR(mie.miectermdx, 1, 10))` from validated `mie`, joined on invoice number + customer + company. NULL when no `mie` row matches. |
| `company_id` | STRING | Company code (ag01/aa05/ab01/ac02/ak02), pass-through of `validated_mac5.mir.company_id`. Joins to `dim_company.companyID`. |
| `mirday` | INT64 | Day of month of the receipt/billing document date (`validated_mac5.mir.mirday`). Combine with `miryear`/`mirmonth` to get the date. |
| `mirmonth` | INT64 | Month of the document date (`validated_mac5.mir.mirmonth`). |
| `miryear` | INT64 | Year of the document date (`validated_mac5.mir.miryear`). |
| `mirtype` | STRING | Document type of the `mir` row; always `'VS'` here (fact_mir_vs keeps only mirtype = 'VS' rows of non-cancelled documents). |
| `mirvnos` | STRING | Document number of the MAC5 `mir` document itself (voucher number); pass-through of `validated_mac5.mir.mirvnos`. Joins to `curated_mih.mihvnos` with `mirtype`. |
| `mircus` | STRING | Customer code on the document (`validated_mac5.mir.mircus`); matches `dim_customer.debcode`. |
| `mirlistno` | INT64 | Line number within the `mir` document (`validated_mac5.mir.mirlistno`). |
| `mirbinvno` | STRING | Number of the invoice (`mih` document) that this line pays or bills; matches `cfsVnosID` in `dim_aging` and `mihVnos` in `dim_invoice`. |
| `mirbinvdate` | DATETIME | Date of that invoice (`validated_mac5.mir.mirbinvdate`, DATETIME). |
| `mirbinvtype` | STRING | Document type of that invoice (`validated_mac5.mir.mirbinvtype`), e.g. IS/BS/AS. |
| `mirdesc` | STRING | Free-text line description from MAC5 (`validated_mac5.mir.mirdesc`). |
| `mircog` | FLOAT64 | Pass-through of `validated_mac5.mir.mircog` (FLOAT64). Meaning not documented in the repo (likely a cost/gross amount, inferred from the name). |
| `mirvat` | FLOAT64 | VAT amount of the line, pass-through of `validated_mac5.mir.mirvat` (inferred from the name). |
| `mirsum` | FLOAT64 | Line amount (`validated_mac5.mir.mirsum`); this is the amount `SUM`med by `view_aging_ri` / `dim_aging` as the paid amount for RS rows. |
| `mircurc` | INT64 | Currency code of the line (`validated_mac5.mir.mircurc`); meaning of the codes not documented in the repo. |
| `mirexchg` | FLOAT64 | Exchange rate of the line (`validated_mac5.mir.mirexchg`). |
| `mirtag` | INT64 | Pass-through of `validated_mac5.mir.mirtag`. Meaning not documented in the repo. |
| `mirnotes` | STRING | Free-text notes on the line (`validated_mac5.mir.mirnotes`). |
| `miraccount` | STRING | Account code on the line (`validated_mac5.mir.miraccount`); meaning not further documented in the repo. |
| `asatdate` | DATE | Load date (ASATDATE partition value) of the source `validated_mac5.mir` row; not a business date. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_mir_vs.sqlx` (`type: "view"`, tags `view`).
- Reads: [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [dimension_table.dim_aging](/dimension/dim_aging.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; `fact_mir_vs` and `dim_aging` are rebuilt first (both `dimension_daily`/`fact_daily`; `dim_aging` itself depends on `fact_mir_vs`). The view declares those two as `dependencies`.

# Examples

Billing amount per company and month, with the aging link available.

```sql
SELECT company_id, miryear, mirmonth, COUNT(*) AS lines, SUM(mirsum) AS billed_amount
FROM `databuffet-nonprd.fact_view.view_fact_mir_vs`
GROUP BY company_id, miryear, mirmonth
ORDER BY company_id, miryear, mirmonth
```

Billings of invoices that have no aging row.

```sql
SELECT company_id, mirbinvno, mirsum
FROM `databuffet-nonprd.fact_view.view_fact_mir_vs`
WHERE AgingSK IS NULL
```
