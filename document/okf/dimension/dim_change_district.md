---
type: BigQuery Table
title: "dim_change_district"
description: "One row = one customer-to-new-section reassignment (customer, old section, new section, validity period) per company, from the MDS change-section master."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_change_district&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_change_district
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_change_district.sqlx"
    title: "Dataform definition (dimension/dim_change_district.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Records customers whose sales section (district) is changed for a period, so reports can attribute their sales to the new section instead of the one on the document. It is LEFT JOINed on `customerCode` (after `TRIM`) + `CompanySK` + `mix_date BETWEEN startDate AND endDate`, and `newSectionID` is then resolved to a Change-Section SK. Source is mds `mds_data_change_section_master`.

Read by: [fact_transcation](/fact/fact_transcation.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one active mds change-section record (customer + period): there is no surrogate key and no `uniqueKey`; `MdsID` identifies the source row. A customer may have several rows with different periods.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID; NULL if no match. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `customerCode` | STRING | Customer code (debtor code) being moved, `cleanString` of mds `customerCode`; the fact build joins it after `TRIM`, matching the mil customer code (`milCus`). |
| `CustomerName` | STRING | Customer name as typed in MDS (`cleanString` of `CustomerName`); descriptive only. |
| `province` | STRING | Province text as typed in MDS (`cleanString` of `province`). |
| `oldSectionID` | STRING | Section code the customer belonged to before the change (mds `oldSectionID`); informational, not used by the fact join. |
| `newSectionID` | STRING | Section code the customer's sales are re-assigned to (mds `newSectionID`); matched to `SectionID` in the section dimension by fact_transcation. |
| `startDate` | DATE | First date the reassignment applies (mds `startDate`, DATE passed through unchanged). |
| `endDate` | DATE | Last date the reassignment applies (mds `endDate`, DATE passed through unchanged). |
| `MdsID` | STRING | `id` of the source row in `mds_dataset.mds_data_change_section_master`, cleaned with `cleanString`; trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_change_district.sqlx` (`type: "table"`, tag `dimension_daily`).
- Storage options: `{"clusterBy": ["companyID", "customerCode"]}`.
- Reads: `mds_dataset.mds_data_change_section_master` (master data loaded outside this repo; only rows with `is_active = TRUE`), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`); runs after dim_company.

# Examples

Section change rows active today.

```sql
SELECT companyID, TRIM(customerCode) AS customerCode, oldSectionID, newSectionID, startDate, endDate
FROM `databuffet-nonprd.dimension_table.dim_change_district`
WHERE CURRENT_DATE('Asia/Bangkok') BETWEEN startDate AND endDate;
```

Customers with overlapping change periods.

```sql
SELECT a.companyID, a.customerCode, a.MdsID, b.MdsID AS other_MdsID
FROM `databuffet-nonprd.dimension_table.dim_change_district` a
JOIN `databuffet-nonprd.dimension_table.dim_change_district` b
  ON a.CompanySK = b.CompanySK AND TRIM(a.customerCode) = TRIM(b.customerCode)
 AND a.MdsID < b.MdsID AND a.startDate <= b.endDate AND b.startDate <= a.endDate;
```
