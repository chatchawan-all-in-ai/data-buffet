---
type: BigQuery Table
title: "dim_customer"
description: "One row = one MAC5 customer (debtor) per company, enriched with CIS360 customer-360 attributes (ag01 only) and parsed invoice-address SKs."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_customer&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_customer
tags: ["dimension", "mac5", "cis360", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_customer.sqlx"
    title: "Dataform definition (dimension/dim_customer.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Customer master dimension for the data mart. It starts from MAC5 `deb` (the debtor master, all five companies), adds the matching CIS360 customer profile (status, nature of business, customer type, names) through the `match_customer` mapping, and attaches province/district/sub-district SKs from the AI-parsed address view [view_deb_address_data](/view/process_dataset/view_deb_address_data.md). The CIS360 profile is matched only for ag01 customers; for the other companies the CIS360 columns are NULL. It is the source of `CustomerSK` for the fact tables and is exposed via [view_dim_customer](/view/dimension_view/view_dim_customer.md).

Read by: [fact_backlog_store](/fact/fact_backlog_store.md), [fact_chq](/fact/fact_chq.md), [fact_invoice](/fact/fact_invoice.md), [fact_invoice_store](/fact/fact_invoice_store.md), [fact_mir_rs](/fact/fact_mir_rs.md), [fact_mir_vs](/fact/fact_mir_vs.md), [fact_order](/fact/fact_order.md), [fact_order_store](/fact/fact_order_store.md), [fact_quotation](/fact/fact_quotation.md), [fact_transcation](/fact/fact_transcation.md), [dim_aging](/dimension/dim_aging.md), [dim_customer_grade](/dimension/dim_customer_grade.md), [dim_group_customer](/dimension/dim_group_customer.md), [dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [view_dim_customer](/view/dimension_view/view_dim_customer.md), [view_dim_customer_credit_management](/view/dimension_view/view_dim_customer_credit_management.md), [view_dim_guarantee](/view/dimension_view/view_dim_guarantee.md), [view_fact_salein_mdt](/view/fact_view/view_fact_salein_mdt.md), [GroupCustomerSK_CustomerSK](/view/bridge_dataset/GroupCustomerSK_CustomerSK.md).

# Grain and key

One row = one customer of a company: key (`CompanySK`, `debcode`) (QUALIFY keeps one row per `companyID` + `debcode`). `CustomerSK` is a stable surrogate key: existing (`debcode`, `CompanySK`) pairs keep their SK, new customers get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `debcode`. No sentinel row is created in this file.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerSK` | INT64 | Stable surrogate key (MERGE with `max_sk`); never regenerated. |
| `InvoiceProvinceSK` | INT64 | Province SK of the customer's invoice address, from `process_dataset.view_deb_address_data` (AI-parsed from `deb` addresses), joined on `debcode` + company. NULL when the address is not parsed. |
| `InvoiceDistrictSK` | INT64 | District SK of the invoice address from `view_deb_address_data` (same join). |
| `InvoiceSubDistrictSK` | INT64 | Sub-district SK of the invoice address from `view_deb_address_data` (same join). |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | MAC5 company code (ag01/aa05/ab01/ac02/ak02) from `dim_company.companyID`. |
| `debcode` | STRING | Customer (debtor) code. |
| `debdate` | DATETIME | Date the customer record was created. |
| `customer_code` | STRING | CIS360 customer code (`C` + 7 digits), matched to `match_customer.customer_allkon` to link MAC5 customers; ag01 customers only, NULL for other companies or when there is no match. |
| `prefix_id` | INT64 | Name prefix (title) of the customer (`prefix.id`); from the CIS360 profile (ag01 only). |
| `debnamet` | STRING | Customer name in Thai. |
| `first_name` | STRING | First name of the customer (individual); from the CIS360 profile (ag01 only). |
| `last_name` | STRING | Last name of the customer (individual); from the CIS360 profile (ag01 only). |
| `debtaxclass` | FLOAT64 | VAT rate applied to the customer in percent (7 or 0). |
| `full_name` | STRING | Full display name of the customer (person or company); from the CIS360 profile (ag01 only). |
| `customer_status_name` | STRING | Customer status name in Thai; from the CIS360 profile (ag01 only). |
| `debsalesp` | STRING | Salesperson code assigned to the customer (joins `per.percode`). |
| `debxxxx` | STRING | Secondary salesperson (employee) code of the customer. |
| `debgrade` | STRING | Customer grade code. |
| `nature_business_code` | STRING | Nature of business code (e.g. `WHOLESALE_BUSINESS`, `FINANCIAL_BUSINESS`, `LOGISTICS_BUSINESS`, `HRR`) (CIS360, ag01 only). |
| `nature_business_name` | STRING | Nature of business name in Thai (CIS360, ag01 only). |
| `nature_business_name_en` | STRING | Nature of business name in English (CIS360, ag01 only). |
| `customer_type_name` | STRING | Customer type name in Thai (CIS360, ag01 only). |
| `customer_type_name_en` | STRING | Customer type name in English (CIS360, ag01 only). |
| `debbranch` | STRING | Tax branch number of the customer (`00000` = head office). |
| `deblimit` | FLOAT64 | Credit limit of the customer in baht. |
| `debgroup` | STRING | Customer group code (e.g. HP, TW, BT, GB, MH, DOHOME); drives channel matching in the sale-rep rules. |
| `DEBcreditTerm` | INT64 | Credit term in days. |
| `debmemo` | STRING | Free-text memo on the customer. |
| `Customer_CM_Grade` | STRING | Always NULL here (`CAST(NULL AS STRING)` placeholder); credit-management grade lives in [dim_customer_grade](/dimension/dim_customer_grade.md). |
| `Total_contact_time_Year` | INT64 | Whole years between `debdate` and today (`DATE_DIFF(CURRENT_DATE('Asia/Bangkok'), debdate, YEAR)`), recomputed every run. |

# How it is built

- Definition: `definitions/dimension/dim_customer.sqlx` (`type: "operations"`, tag `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.match_customer](/validated/validated_mac5/match_customer.md), [validated_cis360.customer_profile](/validated/validated_cis360/customer_profile.md), [validated_cis360.customer_status](/validated/validated_cis360/customer_status.md), [validated_cis360.customer_profile_nature_business](/validated/validated_cis360/customer_profile_nature_business.md), [validated_cis360.nature_business](/validated/validated_cis360/nature_business.md), [validated_cis360.customer_type](/validated/validated_cis360/customer_type.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_company](/dimension/dim_company.md).
- MERGE with stable SK (matches on `debcode` + `CompanySK`; updates all attribute columns, inserts new customers; no delete) inside a `type: "operations"` file, tag `dimension_daily`; the target table pre-exists in BigQuery. Reads the whole `deb` table each run (no date window). Runs after `dim_company` and the process action `deb_address_data` (declared in `dependencies[]`, which feeds `view_deb_address_data`).

# Examples

Customers per company that have a matched CIS360 profile.

```sql
SELECT companyID, COUNT(*) AS customers, COUNTIF(customer_code IS NOT NULL) AS with_cis360
FROM `databuffet-nonprd.dimension_table.dim_customer`
GROUP BY companyID
ORDER BY companyID;
```

CustomerSK for a debtor code in one company (join pattern used by facts).

```sql
SELECT CustomerSK, debcode, deblimit, DEBcreditTerm, debgrade
FROM `databuffet-nonprd.dimension_table.dim_customer`
WHERE companyID = 'ag01' AND debcode = '111000001';
```
