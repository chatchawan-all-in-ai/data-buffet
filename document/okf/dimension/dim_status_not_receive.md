---
type: BigQuery Table
title: "dim_status_not_receive"
description: "One row = one invoice status code (StatusID) of a company that counts as paid-without-receipt, with Thai and English names, from the MDS payment status master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_status_not_receive&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_status_not_receive
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_status_not_receive.sqlx"
    title: "Dataform definition (dimension/dim_status_not_receive.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

List of MAC5 invoice header statuses (`mihstatus`) that are treated as not receiving a payment. `dim_aging` joins it on `mih.mihstatus = StatusID` per company: for receipts in years up to 2023 a match marks the invoice as complete (`status_complete`), so it is not aged as open debt. `view_aging_ri` and the customer-grade dims (`dim_customer_grade`, `dim_group_customer_grade`) also read it.

Read by: [dim_aging](/dimension/dim_aging.md), [dim_customer_grade](/dimension/dim_customer_grade.md), [dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [view_aging_ri](/view/fact_view/view_aging_ri.md).

# Grain and key

One row = one active MDS status row. Natural key: (`CompanyID`, `StatusID`). `NotReceiveSK` is retained for a matching key; new keys are allocated after the current maximum. Rows absent from the complete source snapshot are removed.

# Schema

| Column | Type | Description |
|---|---|---|
| `NotReceiveSK` | INT64 | Stable surrogate key for the natural key; new keys are allocated after the current maximum. |
| `CompanyID` | STRING | Company code (cleaned string); join to `mih.company_id` / dim_company.companyID. No CompanySK column in this table. |
| `StatusID` | INT64 | Invoice status code (INT64 via `castInt64`, fails the run on a non-numeric value); compared with `mihstatus` of the invoice header. |
| `StatusNameTH` | STRING | Thai name of the status. |
| `StatusNameENG` | STRING | English name of the status. |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_payment_status_not_receive_master`, cleaned with `cleanString`; trace column back to MDS. |
# How it is built

- Definition: `definitions/dimension/dim_status_not_receive.sqlx` (`type: "operations"`, `hasOutput: true`, tags `dimension_daily`).
- Reads: `mds_dataset.mds_data_payment_status_not_receive_master` (master data loaded outside this repo).
- Stable-key sync from a complete source snapshot; matching keys retain their SK and update attributes, new rows are inserted, and absent rows are removed; runs after dim_company.
# Examples

Status codes treated as not-received for one company.

```sql
SELECT CompanyID, StatusID, StatusNameENG, StatusNameTH
FROM `databuffet-nonprd.dimension_table.dim_status_not_receive`
ORDER BY CompanyID, StatusID;
```
