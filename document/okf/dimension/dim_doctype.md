---
type: BigQuery Table
title: "dim_doctype"
description: "One row = one document-type code (AccountCategory + Code) per company with English and Thai descriptions, from the MDS document-type master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_doctype&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_doctype
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_doctype.sqlx"
    title: "Dataform definition (dimension/dim_doctype.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Lookup that explains document type codes appearing on accounting/sales documents (category plus code, with EN and TH descriptions). It has no surrogate key. Source: mds `mds_data_document_type_master`.

Read by: [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [export_dim_doctype](/view/pub_sub/export_dim_doctype.md).

# Grain and key

One row = one document-type code: key (company, AccountCategory, Code) among active mds rows. No SK and no `uniqueKey`; `MdsID` identifies the source row.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `AccountCategory` | STRING | Pass-through of mds `AccountCategory`, cleaned with `cleanString` (empty string becomes NULL). Category of the accounting document family the code belongs to. |
| `Code` | STRING | Pass-through of mds `Code`, cleaned with `cleanString` (empty string becomes NULL). MAC5 document type code as used in the `type` columns of document headers and lines, e.g. AR: QS quotation, PS sales order, IS invoice, AS debit note, BS credit note, VS billing statement, RS receipt; AP: QP, PP, IP, AP, BP, VP, RP; IC: PX, TP, JX, SP, SS, TS, MX. |
| `DescriptionEN` | STRING | Pass-through of mds `DescriptionEN`, cleaned with `cleanString` (empty string becomes NULL). English description. |
| `DescriptionTH` | STRING | Pass-through of mds `DescriptionTH`, cleaned with `cleanString` (empty string becomes NULL). Thai description. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_document_type_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_doctype.sqlx` (`type: "table"`, tags `dimension_daily`).
- Storage options: `{"clusterBy": ["AccountCategory", "Code"]}`.
- Reads: `mds_dataset.mds_data_document_type_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Plain SELECT of active mds rows; no surrogate key.
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Document-type descriptions for a company.

```sql
SELECT AccountCategory, Code, DescriptionEN, DescriptionTH
FROM `databuffet-nonprd.dimension_table.dim_doctype`
WHERE companyID = 'ag01'
ORDER BY AccountCategory, Code;
```

Duplicate (company, category, code) keys.

```sql
SELECT companyID, AccountCategory, Code, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_doctype`
GROUP BY 1, 2, 3
HAVING n > 1;
```
