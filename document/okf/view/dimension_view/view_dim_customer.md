---
type: BigQuery View
title: "view_dim_customer"
description: "One row = one customer (CustomerSK) of a company, with group SK, address names, MDS nickname and key-account info."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_view&t=view_dim_customer&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_view
table_id: view_dim_customer
tags: ["view", "dimension_view", "mds"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/dimension_view/view_dim_customer.sqlx"
    title: "Dataform definition (view/dimension_view/view_dim_customer.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Enriched customer view over [dim_customer](/dimension/dim_customer.md). It adds `GroupCustomerSK` (from [dim_group_customer](/dimension/dim_group_customer.md)), the invoice address names (SubDistrict/District/Province/Region from the address dims), the MDS nickname (`NicknameCustomer`, `FlagMDSNickName`) and MDS key-account code/name. Used by [view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md) and [dim_customer_report_info](/dimension/dim_customer_report_info.md).

# Grain and key

One row per dim_customer row (CustomerSK; natural key companyID + debcode); all joins are LEFT. Duplicates can only arise if an MDS nickname or key-account table holds several active rows for one customer code.

# Schema

| Column | Type | Description |
|---|---|---|
| `GroupCustomerSK` | INT64 | SK of the customer group in dim_group_customer; NULL when the lookup fails. A NULL debgroup normally resolves to a self-group keyed by debcode, so this SK does not indicate whether a business group was assigned. |
| `CustomerSK` | INT64 | Stable SK of the customer in dim_customer. |
| `InvoiceProvinceSK` | INT64 | SK of the invoice-address province in `dim_provinces` (pass-through from dim_customer). |
| `InvoiceDistrictSK` | INT64 | SK of the invoice-address district in `dim_districts` (pass-through). |
| `InvoiceSubDistrictSK` | INT64 | SK of the invoice-address sub-district in `dim_sub_districts` (pass-through). |
| `CompanySK` | INT64 | SK of the company in dim_company. |
| `companyID` | STRING | MAC5 company code. |
| `debcode` | STRING | Customer (debtor) code. |
| `debdate` | DATETIME | Date the customer record was created. |
| `customer_code` | STRING | CIS360 customer code (`C` + 7 digits), matched to `match_customer.customer_allkon` to link MAC5 customers. |
| `prefix_id` | INT64 | Name prefix (title) of the customer (`prefix.id`). |
| `debnamet` | STRING | Customer name in Thai. |
| `first_name` | STRING | First name of the customer (individual). |
| `last_name` | STRING | Last name of the customer (individual). |
| `debtaxclass` | FLOAT64 | VAT rate applied to the customer in percent (7 or 0). |
| `full_name` | STRING | Full display name of the customer (person or company). |
| `customer_status_name` | STRING | Customer status name in Thai. |
| `debsalesp` | STRING | Salesperson code assigned to the customer (joins `per.percode`). |
| `debxxxx` | STRING | Secondary salesperson (employee) code of the customer. |
| `debgrade` | STRING | Customer grade code. |
| `nature_business_code` | STRING | Nature of business code (e.g. `WHOLESALE_BUSINESS`, `FINANCIAL_BUSINESS`, `LOGISTICS_BUSINESS`, `HRR`). |
| `nature_business_name` | STRING | Nature of business name in Thai. |
| `nature_business_name_en` | STRING | Nature of business name in English. |
| `customer_type_name` | STRING | Customer type name in Thai. |
| `customer_type_name_en` | STRING | Customer type name in English. |
| `debbranch` | STRING | Tax branch number of the customer (`00000` = head office). |
| `deblimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debgroup` | STRING | Customer group code (e.g. HP, TW, BT, GB, MH, DOHOME); drives channel matching in the sale-rep rules. |
| `DEBcreditTerm` | INT64 | Credit term in days. |
| `debmemo` | STRING | Free-text memo on the customer. |
| `Customer_CM_Grade` | STRING | Credit-management grade placeholder in dim_customer; written as NULL by dim_customer (`CAST(NULL AS STRING)`). Real grades are in [dim_customer_grade](/dimension/dim_customer_grade.md) - see view_dim_customer_credit_management. |
| `Total_contact_time_Year` | INT64 | Years since `debdate` (`DATE_DIFF(today, debdate, YEAR)`), computed when dim_customer is built. |
| `SubDistrict` | STRING | Thai sub-district name of the invoice address (`dim_sub_districts.name_th`). |
| `District` | STRING | Thai district name of the invoice address (`dim_districts.name_th`). |
| `Province` | STRING | Thai province name of the invoice address (`dim_provinces.name_th`). |
| `Region` | STRING | Geography/region name of the province (`dim_geographies.name`). |
| `NicknameCustomer` | STRING | MDS customer nickname if one exists, else `debnamet`. |
| `FlagMDSNickName` | BOOL | TRUE when NicknameCustomer comes from the MDS nickname master. |
| `KeyAccountCode` | STRING | Key-account group code from the MDS key-account master (joined by companyid + customercode); NULL if not a key account. |
| `KeyAccountName` | STRING | Key-account group name from the MDS key-account group master. |

# How it is built

- Definition: `definitions/view/dimension_view/view_dim_customer.sqlx` (`type: "view"`, tags `view`).
- Reads: `mds_dataset.mds_data_customernickname_master` (master data loaded outside this repo), `mds_dataset.mds_data_keyaccount_master` (master data loaded outside this repo), `mds_dataset.mds_data_keyaccount_group_master` (master data loaded outside this repo), [dimension_table.dim_customer](/dimension/dim_customer.md), [dimension_table.dim_group_customer](/dimension/dim_group_customer.md), `dimension_table.dim_sub_districts`, `dimension_table.dim_districts`, `dimension_table.dim_provinces`, `dimension_table.dim_geographies`.
- Build: A plain BigQuery view (`type: "view"`, tag `view`): no storage, evaluated at query time over the current content of its base tables, so it is as fresh as they are. The `view` tag is not part of the nightly run; it is deployed with tag `view` after the base dimensions exist. Reads dim_customer, dim_group_customer, the address dims, and three mds tables (nickname, key account, key account group; only `is_active = TRUE`). Master data in mds_dataset is loaded outside this repo.

# Examples

Customers of a key account with their region:

```sql
SELECT CustomerSK, debcode, NicknameCustomer, Province, Region
FROM `databuffet-nonprd.dimension_view.view_dim_customer`
WHERE companyID = 'ag01' AND KeyAccountCode IS NOT NULL
```

Customers per region and group-less count:

```sql
SELECT Region, COUNT(*) AS customers, COUNTIF(debgroup IS NULL) AS no_group
FROM `databuffet-nonprd.dimension_view.view_dim_customer`
GROUP BY Region
```
