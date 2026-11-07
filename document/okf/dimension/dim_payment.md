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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Lookup that classifies how a sale is paid, keyed by the document memo code (`CodeMemo`). Source: mds `mds_data_payment_master`.

Read by: [fact_transcation](/fact/fact_transcation.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [export_dim_payment](/view/pub_sub/export_dim_payment.md).

# Grain and key

One row = one payment memo code per company. Natural key: (`companyID`, `CodeMemo`). `PaymentSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `PaymentSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `CodeMemo` | STRING | Pass-through of mds `CodeMemo`, cleaned with `cleanString` (empty string becomes NULL). Memo code from the sales document that identifies the payment term; the natural key with companyID. |
| `PaymentID` | STRING | Pass-through of mds `PaymentID`, cleaned with `cleanString` (empty string becomes NULL). Payment identifier/code grouping several memo codes. |
| `PaymentName` | STRING | Pass-through of mds `PaymentName`, cleaned with `cleanString` (empty string becomes NULL). Payment name. |
| `PaymentMethodEN` | STRING | Pass-through of mds `PaymentMethodEN`, cleaned with `cleanString` (empty string becomes NULL). Payment method, English. |
| `PaymentMethodTH` | STRING | Pass-through of mds `PaymentMethodTH`, cleaned with `cleanString` (empty string becomes NULL). Payment method, Thai. |
| `PaymentType` | STRING | Pass-through of mds `PaymentType`, cleaned with `cleanString` (empty string becomes NULL). Payment term category: `Cash`, `Credit` or `No Memo Code` (the default ฿00฿ row). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_payment_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_payment.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_payment_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
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
