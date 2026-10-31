---
type: BigQuery View
title: "view_dim_guarantee"
description: "One row = one bank guarantee (GuaranteeSK) per company, customer and bank, linked to its CustomerSK."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_guarantee&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_guarantee
tags: ["view", "dimension_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_guarantee.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_guarantee.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Customer guarantee view: [dim_guarantee](/dimension/dim_guarantee.md) (bank guarantee documents from MDS) with the customer's `CustomerSK` from [dim_customer](/dimension/dim_customer.md), matched on customer code and CompanySK. Rows whose customer cannot be matched are dropped. Used for credit-control reports on guarantee limits and expiry; nothing else in the repo reads it.

# Grain and key

One row per GuaranteeSK (grain of dim_guarantee: companyID + CustomerCode + BankName). INNER-style filter `CustomerSK IS NOT NULL` removes unmatched customers.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerSK` | INT64 | Stable SK of the customer in dim_customer, matched on CustomerCode = debcode and CompanySK; never NULL in this view. |
| `GuaranteeSK` | INT64 | SK of the guarantee row in dim_guarantee (ROW_NUMBER over companyID, CustomerCode, BankName; regenerated daily). |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `CompanyID` | STRING | MAC5 company code (cleaned). |
| `Region` | STRING | Sales region text from the MDS guarantee document master (pass-through). |
| `CustomerCode` | STRING | Customer code (debcode) the guarantee belongs to. |
| `CustomeName` | STRING | Customer name from the MDS guarantee master (dim_guarantee `CustomerName`); the deployed view spells the column `CustomeName`. |
| `ExpiryDate` | DATE | Expiry date of the guarantee. |
| `BankName` | STRING | Issuing bank name. |
| `BG_Limit` | STRING | Bank guarantee limit (STRING as stored in MDS). |
| `Renewal` | STRING | Renewal text from MDS (pass-through; values not documented). |
| `Remarks` | STRING | Free-text remarks from MDS. |
| `Address` | STRING | Address text from MDS guarantee master. |
| `PhoneNumber` | STRING | Phone number text from MDS (personal contact data). |
| `FAX` | STRING | Fax number text from MDS. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_guarantee.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_guarantee](/dimension/dim_guarantee.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_guarantee (full rebuild from mds, tag `dimension_daily`) and dim_customer.

# Examples

Guarantees expiring in the next 90 days:

```sql
SELECT CustomerSK, BankName, BG_Limit, ExpiryDate
FROM `databuffet-nonprd.dimension_view.view_dim_guarantee`
WHERE ExpiryDate BETWEEN CURRENT_DATE('Asia/Bangkok') AND DATE_ADD(CURRENT_DATE('Asia/Bangkok'), INTERVAL 90 DAY)
ORDER BY ExpiryDate
```

Guarantees per bank:

```sql
SELECT BankName, COUNT(*) AS guarantees
FROM `databuffet-nonprd.dimension_view.view_dim_guarantee`
GROUP BY BankName
```
