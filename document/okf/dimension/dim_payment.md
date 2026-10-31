---
type: BigQuery Table
title: "dim_payment"
description: "One row = one payment memo code (CodeMemo) per company with its payment id, name, method (EN/TH) and type, from the MDS payment master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_payment&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_payment
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_payment.sqlx"
    title: "Dataform definition (dimension/dim_payment.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Lookup that classifies how a sale is paid, keyed by the document memo code (`CodeMemo`). [fact_transcation](/fact/fact_transcation.md) stores `PaymentSK`, and [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md) joins it for reporting. Source: mds `mds_data_payment_master`.

# Grain and key

One row per (company, CodeMemo) among active mds rows. Key: `PaymentSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `PaymentSK` | INT64 | `PaymentSK` is `ROW_NUMBER() OVER(ORDER BY companyID, CodeMemo)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `CodeMemo` | STRING | Pass-through of mds `CodeMemo`, cleaned with `cleanString` (empty string becomes NULL). Memo code from the sales document that identifies the payment term; the natural key with companyID. |
| `PaymentID` | STRING | Pass-through of mds `PaymentID`, cleaned with `cleanString` (empty string becomes NULL). Payment identifier/code grouping several memo codes. |
| `PaymentName` | STRING | Pass-through of mds `PaymentName`, cleaned with `cleanString` (empty string becomes NULL). Payment name. |
| `PaymentMethodEN` | STRING | Pass-through of mds `PaymentMethodEN`, cleaned with `cleanString` (empty string becomes NULL). Payment method, English. |
| `PaymentMethodTH` | STRING | Pass-through of mds `PaymentMethodTH`, cleaned with `cleanString` (empty string becomes NULL). Payment method, Thai. |
| `PaymentType` | STRING | Pass-through of mds `PaymentType`, cleaned with `cleanString` (empty string becomes NULL). Payment type category (code values not documented in the repo). |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_payment.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `PaymentSK`.
- Storage options: `{"clusterBy": ["PaymentSK"]}`.
- Reads: `mds_dataset.mds_data_payment_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).
- Approximate size (BigQuery metadata, 2026-10-31): 15 rows, 2.5 KB.

# Examples

Payment codes of one company.

```sql
SELECT CodeMemo, PaymentID, PaymentName, PaymentMethodEN, PaymentType
FROM `databuffet-nonprd.dimension_table.dim_payment`
WHERE companyID = 'ag01'
ORDER BY CodeMemo;
```

Duplicate (company, CodeMemo) keys.

```sql
SELECT companyID, CodeMemo, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_payment`
GROUP BY 1, 2
HAVING n > 1;
```
