---
type: BigQuery Table
title: "dim_guarantee"
description: "One row = one bank guarantee (BG) document for a customer at a bank (company, customer code, bank name), with its limit and expiry date, from the MDS guarantee master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_guarantee&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_guarantee
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_guarantee.sqlx"
    title: "Dataform definition (dimension/dim_guarantee.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

Register of customer bank guarantees: which bank issued it, the guarantee limit (`BG_Limit`), the expiry date and renewal status, plus the customer's contact details as typed in MDS. Source: mds `mds_data_guarantee_document_master`.

Read by: [view_dim_guarantee](/view/dimension_view/view_dim_guarantee.md).

# Grain and key

One row = one bank guarantee: key (company, CustomerCode, BankName) among active mds rows; `GuaranteeSK` is the surrogate key, regenerated every run. A customer with guarantees at several banks has several rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `GuaranteeSK` | INT64 | `ROW_NUMBER() OVER(ORDER BY CompanyID, CustomerCode, BankName)` over the active mds rows. Regenerated every run. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `Region` | STRING | Pass-through of mds `Region`, cleaned with `cleanString` (empty string becomes NULL). Sales region label of the customer as typed in MDS. |
| `CustomerCode` | STRING | Pass-through of mds `CustomerCode`, cleaned with `cleanString` (empty string becomes NULL). Customer (debtor) code; join key to the customer dimension together with company. |
| `CustomerName` | STRING | Pass-through of mds `CustomerName`, cleaned with `cleanString` (empty string becomes NULL). Customer name as typed in MDS. |
| `ExpiryDate` | DATE | Expiry date of the guarantee (mds `ExpiryDate`, DATE passed through). |
| `BankName` | STRING | Pass-through of mds `BankName`, cleaned with `cleanString` (empty string becomes NULL). Name of the issuing bank; part of the row key. |
| `BG_Limit` | FLOAT64 | Bank guarantee amount in THB (`castFloat64` of mds `BG_Limit`), e.g. 100000 or 500000. |
| `Renewal` | STRING | Pass-through of mds `Renewal`, cleaned with `cleanString` (empty string becomes NULL). Status of the guarantee in Thai: `ไม่ส่ง` (not sent), `คืน` (returned), `เคลม` (claimed), `รอเครม` (awaiting claim), `ยกเลิก` (cancelled). |
| `Remarks` | STRING | Pass-through of mds `Remarks`, cleaned with `cleanString` (empty string becomes NULL). Free-text remark. |
| `Address` | STRING | Pass-through of mds `Address`, cleaned with `cleanString` (empty string becomes NULL). Address text of the customer/guarantee. |
| `PhoneNumber` | STRING | Pass-through of mds `PhoneNumber`, cleaned with `cleanString` (empty string becomes NULL). Phone number text. |
| `FAX` | STRING | Pass-through of mds `FAX`, cleaned with `cleanString` (empty string becomes NULL). Fax number text. |
| `MdsId` | STRING | `id` of the source row in `mds_dataset.mds_data_guarantee_document_master`, cleaned with `cleanString`; trace column back to MDS. Aliased `MdsID` in the SQL. |

# How it is built

- Definition: `definitions/dimension/dim_guarantee.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `GuaranteeSK`.
- Storage options: `{"clusterBy": ["GuaranteeSK"]}`.
- Reads: `mds_dataset.mds_data_guarantee_document_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Guarantees expiring within the next 60 days.

```sql
SELECT CompanyID, CustomerCode, BankName, BG_Limit, ExpiryDate
FROM `databuffet-nonprd.dimension_table.dim_guarantee`
WHERE ExpiryDate BETWEEN CURRENT_DATE('Asia/Bangkok') AND DATE_ADD(CURRENT_DATE('Asia/Bangkok'), INTERVAL 60 DAY)
ORDER BY ExpiryDate;
```

Total guarantee limit per company.

```sql
SELECT CompanyID, COUNT(*) AS guarantees, SUM(BG_Limit) AS total_limit
FROM `databuffet-nonprd.dimension_table.dim_guarantee`
GROUP BY 1;
```
