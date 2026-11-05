---
type: BigQuery Table
title: "dim_group_customer_grade"
description: "One row = one customer group per company per year with payment, collection-speed, bounced-cheque and relationship scores and the resulting credit grade."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_group_customer_grade&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_group_customer_grade
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_group_customer_grade.sqlx"
    title: "Dataform definition (dimension/dim_group_customer_grade.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

Group-level version of [dim_customer_grade](/dimension/dim_customer_grade.md): receipts, late-payment averages, cancelled cheques and first-contact date are aggregated over every customer of a `debgroup` (from [dim_group_customer](/dimension/dim_group_customer.md)) instead of one customer, then scored against the same MDS score bands and mapped to a grade through [dim_grade](/dimension/dim_grade.md). Two results are given: invoice-date basis and due-date basis.

# Grain and key

One row = one customer group per company per year: key (`CompanySK`, `CustomerGroup`, `Year`). `GroupCustomerGradeSK` is a stable surrogate key (existing rows keep it; new rows get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `Year`, `debgroup`). A group gets rows only for years >= the year of its first-contact date.

# Schema

| Column | Type | Description |
|---|---|---|
| `GroupCustomerGradeSK` | INT64 | Stable surrogate key of the (customer group, year) grade row; assigned once via `max_sk + ROW_NUMBER()` and kept on later runs. |
| `GroupCustomerSK` | INT64 | Group SK from [dim_group_customer](/dimension/dim_group_customer.md). |
| `PaymentReceiveSK` | INT64 | SK of the payment-volume score band from [dim_payment_receive_score](/dimension/dim_payment_receive_score.md): the band where `ROUND(SumPaymentReceive)` falls between `PaymentReceivedMin` and `PaymentReceivedMax` and the as-at date is within the band's StartDate-EndDate. NULL if no band matches. Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `InvAvgCollectSK` | INT64 | SK of the collection-speed score band from [dim_avg_collection_score](/dimension/dim_avg_collection_score.md) for the invoice-date based average (`InvoiceDateAvgReceiveAgeDay` within the band's day min/max, valid on the as-at date). Role-played use of the avg-collection dim. Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `DueAvgCollectSK` | INT64 | Same as `InvAvgCollectSK` but for the due-date based average (`DueDateAvgReceiveAgeDay`). Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `BounceChequeSK` | INT64 | SK of the bounced-cheque score band from [dim_bounce_cheque_score](/dimension/dim_bounce_cheque_score.md) matching `CountCancelCheque` (band min/max, valid on the as-at date). Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `ContactSK` | INT64 | SK of the relationship-length score band from [dim_contact_score](/dimension/dim_contact_score.md) matching the rounded years since first contact (`CalculateFirstContact`), valid on the as-at date. Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `InvoiceGradeSK` | INT64 | SK of the grade row in [dim_grade](/dimension/dim_grade.md) matching `InvoiceCalPercent` (company grade bands by `Percentmin`..`Percentmax`). Role-played use of dim_grade. Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `DueGradeSK` | INT64 | SK of the grade row in [dim_grade](/dimension/dim_grade.md) matching `DueCalPercent`. Refers to the dim row of the run that computed it, so it matches the current dim only for rows where `Year` = year of yesterday. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md), carried over from `dim_customer.CompanySK`; NULL if no match. |
| `CompanyID` | STRING | MAC5 company code. |
| `Year` | INT64 | Calendar year the grade refers to (INT64). A run only computes the year of yesterday's date; earlier years keep the values from the last run in that year. |
| `CustomerGroup` | STRING | Customer group code (`debgroup`, or the customer's own `debcode` when no group); with `CompanySK` and `Year` the natural key. |
| `SumPaymentReceive` | FLOAT64 | Total received by all customers of the group in `Year` (RS receipts, cheque-extract dates applied, rounded to 2 decimals); 0 when none. |
| `InvoiceDateAvgReceiveAgeDay` | FLOAT64 | Average days (rounded up) between invoice date and receipt date for receipts in `Year`, counting only late-positive differences; 0 when none. |
| `DueDateAvgReceiveAgeDay` | FLOAT64 | Average days (rounded up) between the computed due date (`invoice date + credit term`) and receipt date, counting only positive differences (paid late); 0 when none. |
| `CountCancelCheque` | INT64 | Number of distinct cheques with `chqstatus = 2` dated in `Year` across all customers of the group; 0 when none. |
| `CalculateFirstContact` | FLOAT64 | Years (days / 365.0) from the group's first-contact date to the day before the run. |
| `Credibility` | INT64 | Fixed credibility score of 20 for every row (hard-coded `20 as credibility_score`). |
| `FirstContactDate` | DATETIME | First-contact date of the group: earliest `debdate` of its customers, else the earliest MAC5 invoice (`mih`) date of any customer in the group, else `debeditdt`. DATETIME. |
| `InvoiceCalPercent` | FLOAT64 | Overall score percent on the invoice-date basis: `(payment score + invoice avg-collection score + bounce score + contact score + 20 credibility) / 80 * 100`. |
| `InvoiceGrade` | STRING | Grade label looked up in [dim_grade](/dimension/dim_grade.md) for `InvoiceCalPercent`. |
| `DueCalPercent` | FLOAT64 | Overall score percent on the due-date basis: `(payment score + due avg-collection score + bounce score + contact score + 20 credibility) / 80 * 100`. |
| `DueGrade` | STRING | Grade label looked up in [dim_grade](/dimension/dim_grade.md) for `DueCalPercent`. |
| `asatdate` | DATE | Date the row was last computed (`CURRENT_DATE('Asia/Bangkok') - 1`). |

# How it is built

- Definition: `definitions/dimension/dim_group_customer_grade.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [dimension_table.dim_group_customer](/dimension/dim_group_customer.md), [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_status_not_receive](/dimension/dim_status_not_receive.md), [validated_mac5.mih](/validated/validated_mac5/mih.md), [dimension_table.dim_payment_receive_score](/dimension/dim_payment_receive_score.md), [dimension_table.dim_avg_collection_score](/dimension/dim_avg_collection_score.md), [dimension_table.dim_bounce_cheque_score](/dimension/dim_bounce_cheque_score.md), [dimension_table.dim_contact_score](/dimension/dim_contact_score.md), [dimension_table.dim_grade](/dimension/dim_grade.md).
- Refresh: MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `GroupCustomerGradeSK` (existing `Year` + `CustomerGroup` + `CompanySK`); updates all attribute columns, inserts new rows, no delete. Only the current year (year of yesterday) is recomputed each run. Runs after `dim_customer`, `dim_group_customer`, `dim_calendar`, `dim_status_not_receive`, `dim_grade` and the four score dims.

# Examples

Current-year group grades for one company, best first.

```sql
SELECT CustomerGroup, GroupCustomerSK, SumPaymentReceive, InvoiceCalPercent, InvoiceGrade, DueGrade
FROM `databuffet-nonprd.dimension_table.dim_group_customer_grade`
WHERE CompanyID = 'ag01' AND Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
ORDER BY InvoiceCalPercent DESC
LIMIT 50;
```

Group grade and grades of its member customers.

```sql
SELECT g.CustomerGroup, g.InvoiceGrade AS group_grade, c.CustomerCode, c.InvoiceGrade AS customer_grade
FROM `databuffet-nonprd.dimension_table.dim_group_customer_grade` AS g
JOIN `databuffet-nonprd.dimension_table.dim_customer` AS cu
  ON cu.CompanySK = g.CompanySK AND IFNULL(cu.debgroup, cu.debcode) = g.CustomerGroup
JOIN `databuffet-nonprd.dimension_table.dim_customer_grade` AS c
  ON c.CustomerSK = cu.CustomerSK AND c.Year = g.Year
WHERE g.Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
LIMIT 50;
```
