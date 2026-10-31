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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Customer master dimension for the data mart. It starts from MAC5 `deb` (the debtor master, all five companies), adds the matching CIS360 customer profile (status, nature of business, customer type, names) through the `match_customer` mapping, and attaches province/district/sub-district SKs from the AI-parsed address view [view_deb_address_data](/view/process_dataset/view_deb_address_data.md). It is the source of `CustomerSK` for the fact tables ([fact_order](/fact/fact_order.md), [fact_invoice](/fact/fact_invoice.md), [fact_mir_vs](/fact/fact_mir_vs.md), [fact_transcation](/fact/fact_transcation.md), [fact_quotation](/fact/fact_quotation.md) and others), for [dim_aging](/dimension/dim_aging.md), the grade dims ([dim_customer_grade](/dimension/dim_customer_grade.md)) and [dim_group_customer](/dimension/dim_group_customer.md), and is exposed via [view_dim_customer](/view/dimension_view/view_dim_customer.md).

Used by: [fact_table.fact_backlog_store](/fact/fact_backlog_store.md), [fact_table.fact_chq](/fact/fact_chq.md), [fact_table.fact_invoice](/fact/fact_invoice.md), [fact_table.fact_invoice_store](/fact/fact_invoice_store.md), [fact_table.fact_mir_rs](/fact/fact_mir_rs.md), [fact_table.fact_mir_vs](/fact/fact_mir_vs.md), [fact_table.fact_order](/fact/fact_order.md), [fact_table.fact_order_store](/fact/fact_order_store.md), [bridge_dataset.GroupCustomerSK_CustomerSK](/view/bridge_dataset/GroupCustomerSK_CustomerSK.md), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), [dimension_view.view_dim_customer_credit_management](/view/dimension_view/view_dim_customer_credit_management.md), [dimension_view.view_dim_guarantee](/view/dimension_view/view_dim_guarantee.md), [fact_view.view_fact_salein_mdt](/view/fact_view/view_fact_salein_mdt.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer](/dimension/dim_group_customer.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md), [fact_table.fact_quotation](/fact/fact_quotation.md), [fact_table.fact_transcation](/fact/fact_transcation.md).

# Grain and key

One row per (`CompanySK`, `debcode`) (QUALIFY keeps one row per `companyID` + `debcode`). `CustomerSK` is a stable surrogate key: existing (`debcode`, `CompanySK`) pairs keep their SK, new customers get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `debcode`. No sentinel row is created in this file.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerSK` | INT64 | Stable surrogate key (MERGE with `max_sk`); never regenerated. |
| `InvoiceProvinceSK` | INT64 | Province SK of the customer's invoice address, from `process_dataset.view_deb_address_data` (AI-parsed from `deb` addresses), joined on `debcode` + company. NULL when the address is not parsed. |
| `InvoiceDistrictSK` | INT64 | District SK of the invoice address from `view_deb_address_data` (same join). |
| `InvoiceSubDistrictSK` | INT64 | Sub-district SK of the invoice address from `view_deb_address_data` (same join). |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), joined on `deb.company_id`. |
| `companyID` | STRING | MAC5 company code (ag01/aa05/ab01/ac02/ak02) from `dim_company.companyID`. |
| `debcode` | STRING | MAC5 debtor/customer code (`deb.debcode`); natural key with company. Matches `mihCus` on invoices. |
| `debdate` | DATETIME | Date field `deb.debdate` of the MAC5 debtor master (DATETIME); used to compute `Total_contact_time_Year`. Likely the customer creation/registration date, inferred from how it is used. |
| `customer_code` | STRING | CIS360 customer code (`customer_profile.customer_code`) matched to this debtor through `match_customer`. NULL for non-ag01 companies and unmatched debtors. |
| `prefix_id` | INT64 | CIS360 name-prefix id (`customer_profile.prefix_id`); NULL if unmatched. |
| `debnamet` | STRING | Customer Thai name from MAC5 `deb.debnamet`. |
| `first_name` | STRING | First name from the CIS360 customer profile (NULL if unmatched). |
| `last_name` | STRING | Last name from the CIS360 customer profile (NULL if unmatched). |
| `debtaxclass` | FLOAT64 | MAC5 `deb.debtaxclass` pass-through. Meaning not documented in the repo. |
| `full_name` | STRING | Full name from the CIS360 customer profile (NULL if unmatched). |
| `customer_status_name` | STRING | CIS360 customer status name (`customer_status.customer_status_name`, joined by `customer_status_id`). |
| `debsalesp` | STRING | Salesperson/employee code assigned to the customer in MAC5 (`deb.debsalesp`); used to look up the sale representative in the TA logic of the views. |
| `debxxxx` | STRING | MAC5 `deb.debxxxx` pass-through. Meaning not documented in the repo. |
| `debgrade` | STRING | MAC5 `deb.debgrade` customer grade code (pass-through). |
| `nature_business_code` | STRING | CIS360 nature-of-business code (via `customer_profile_nature_business` and `nature_business`). |
| `nature_business_name` | STRING | CIS360 nature-of-business name (Thai). |
| `nature_business_name_en` | STRING | CIS360 nature-of-business name (English). |
| `customer_type_name` | STRING | CIS360 customer type name (Thai), from `customer_type` by `customer_type_id`. |
| `customer_type_name_en` | STRING | CIS360 customer type name (English). |
| `debbranch` | STRING | MAC5 `deb.debbranch` pass-through, likely the tax branch code (inferred from the name). |
| `deblimit` | FLOAT64 | Customer credit limit from MAC5 `deb.deblimit`. |
| `debgroup` | STRING | MAC5 customer group code (`deb.debgroup`); basis of [dim_group_customer](/dimension/dim_group_customer.md) (NULL falls back to `debcode` there). |
| `DEBcreditTerm` | INT64 | Credit term in days from MAC5 `deb.DEBcreditTerm`. |
| `debmemo` | STRING | Free-text memo on the debtor (`deb.debmemo`). |
| `Customer_CM_Grade` | STRING | Always NULL here (`CAST(NULL AS STRING)` placeholder); credit-management grade lives in [dim_customer_grade](/dimension/dim_customer_grade.md). |
| `Total_contact_time_Year` | INT64 | Whole years between `debdate` and today (`DATE_DIFF(CURRENT_DATE('Asia/Bangkok'), debdate, YEAR)`), recomputed every run. |

# How it is built

- Definition: `definitions/dimension/dim_customer.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [validated_mac5.match_customer](/validated/validated_mac5/match_customer.md), [validated_cis360.customer_profile](/validated/validated_cis360/customer_profile.md), [validated_cis360.customer_status](/validated/validated_cis360/customer_status.md), [validated_cis360.customer_profile_nature_business](/validated/validated_cis360/customer_profile_nature_business.md), [validated_cis360.nature_business](/validated/validated_cis360/nature_business.md), [validated_cis360.customer_type](/validated/validated_cis360/customer_type.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_company](/dimension/dim_company.md).
- Refresh: MERGE with stable SK (matches on `debcode` + `CompanySK`; updates all attribute columns, inserts new customers; no delete) inside a `type: "operations"` file, tag `dimension_daily`. Reads the whole `deb` table each run (no date window). Runs after `dim_company` and the process action `deb_address_data` (declared in `dependencies[]`, which feeds `view_deb_address_data`). The target table pre-exists in BigQuery.
- Approximate size (BigQuery metadata, 2026-10-31): 98,325 rows, 17.5 MB.

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
