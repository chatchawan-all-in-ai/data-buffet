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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Register of customer bank guarantees: which bank issued it, the guarantee limit (`BG_Limit`), the expiry date and renewal status, plus the customer's contact details as typed in MDS. Used by the BI view [view_dim_guarantee](/view/dimension_view/view_dim_guarantee.md), which joins it to the customer dimension. Source: mds `mds_data_guarantee_document_master`. Contains personal/contact fields (address, phone, fax); handle accordingly.

# Grain and key

One row per (company, CustomerCode, BankName) among active mds rows. Key: `GuaranteeSK` (surrogate, unstable across days). A customer with guarantees at several banks has several rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `GuaranteeSK` | INT64 | `GuaranteeSK` is `ROW_NUMBER() OVER(ORDER BY CompanyID, CustomerCode, BankName)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `CompanyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `CompanyID`; natural join key to dim_company.companyID. |
| `Region` | STRING | Pass-through of mds `Region`, cleaned with `cleanString` (empty string becomes NULL). Sales region label of the customer as typed in MDS. |
| `CustomerCode` | STRING | Pass-through of mds `CustomerCode`, cleaned with `cleanString` (empty string becomes NULL). Customer (debtor) code; join key to the customer dimension together with company. |
| `CustomerName` | STRING | Pass-through of mds `CustomerName`, cleaned with `cleanString` (empty string becomes NULL). Customer name as typed in MDS. |
| `ExpiryDate` | DATE | Expiry date of the guarantee (mds `ExpiryDate`, DATE passed through). |
| `BankName` | STRING | Pass-through of mds `BankName`, cleaned with `cleanString` (empty string becomes NULL). Name of the issuing bank; part of the row key. |
| `BG_Limit` | FLOAT64 | Guarantee amount limit (`castFloat64` of mds `BG_Limit`; currency not documented in the repo, presumably THB). |
| `Renewal` | STRING | Pass-through of mds `Renewal`, cleaned with `cleanString` (empty string becomes NULL). Renewal status/remark text; code values not documented in the repo. |
| `Remarks` | STRING | Pass-through of mds `Remarks`, cleaned with `cleanString` (empty string becomes NULL). Free-text remark. |
| `Address` | STRING | Pass-through of mds `Address`, cleaned with `cleanString` (empty string becomes NULL). Address text of the customer/guarantee (personal data; not shown here). |
| `PhoneNumber` | STRING | Pass-through of mds `PhoneNumber`, cleaned with `cleanString` (empty string becomes NULL). Phone number text (personal data). |
| `FAX` | STRING | Pass-through of mds `FAX`, cleaned with `cleanString` (empty string becomes NULL). Fax number text. |
| `MdsId` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. The live column name is `MdsId` (BigQuery column names are case-insensitive; the SQL aliases it `MdsID`). |

# How it is built

- Definition: `definitions/dimension/dim_guarantee.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `GuaranteeSK`.
- Storage options: `{"clusterBy": ["GuaranteeSK"]}`.
- Reads: `mds_dataset.mds_data_guarantee_document_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).
- Approximate size (BigQuery metadata, 2026-10-31): 355 rows, 181.1 KB.

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
