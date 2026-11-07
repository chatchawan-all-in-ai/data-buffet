---
type: BigQuery Table
title: "dim_customer_grade"
description: "One row = one customer per company per year with payment, collection-speed, bounced-cheque and relationship scores and the resulting credit grade."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_customer_grade&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_customer_grade
tags: ["dimension", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_customer_grade.sqlx"
    title: "Dataform definition (dimension/dim_customer_grade.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T23:20:34+07:00" }
status: draft
---

# What it is

Customer credit-management scorecard. For each customer and year it totals receipts, measures how late the customer pays (against invoice date and against due date), computes `CountCancelCheque` (defined in Schema below) and relationship length, looks each measure up in the MDS-driven score band dims, adds a fixed credibility score of 20, converts the sum to a percent of 80, and maps that percent to a grade (labels held in [dim_grade](/dimension/dim_grade.md)). Two parallel results exist: an invoice-date grade and a due-date grade. The group-level equivalent is [dim_group_customer_grade](/dimension/dim_group_customer_grade.md). Referenced score-band and grade dimensions now retain SKs for unchanged natural keys. Only current-year rows are recomputed; older scorecard rows retain their stored score attributes.

Read by: [view_dim_customer_credit_management](/view/dimension_view/view_dim_customer_credit_management.md).

# Grain and key

One row = one customer in one year: key (`CompanySK`, `CustomerCode`, `Year`). `CustomerGradeSK` is a stable surrogate key (existing rows keep it; new rows get `max_sk + ROW_NUMBER()` ordered by `CompanySK`, `Year`, `debcode`). A customer gets rows only for years >= the year of its first-contact date.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerGradeSK` | INT64 | Stable surrogate key of the (customer, year) grade row; assigned once via `max_sk + ROW_NUMBER()` and kept on later runs. |
| `CustomerSK` | INT64 | Customer SK from [dim_customer](/dimension/dim_customer.md) (the customer the grade belongs to). |
| `PaymentReceiveSK` | INT64 | SK of the payment-volume score band from [dim_payment_receive_score](/dimension/dim_payment_receive_score.md): the band where `ROUND(SumPaymentReceive)` falls between `PaymentReceivedMin` and `PaymentReceivedMax` and the as-at date is within the band's StartDate-EndDate. NULL if no band matches. Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `InvAvgCollectSK` | INT64 | SK of the collection-speed score band from [dim_avg_collection_score](/dimension/dim_avg_collection_score.md) for the invoice-date based average (`InvoiceDateAvgReceiveAgeDay` within the band's day min/max, valid on the as-at date). Role-played use of the avg-collection dim. Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `DueAvgCollectSK` | INT64 | Same as `InvAvgCollectSK` but for the due-date based average (`DueDateAvgReceiveAgeDay`). Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `BounceChequeSK` | INT64 | SK of the bounced-cheque score band from [dim_bounce_cheque_score](/dimension/dim_bounce_cheque_score.md) matching `CountCancelCheque` (band min/max, valid on the as-at date). Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `ContactSK` | INT64 | SK of the relationship-length score band from [dim_contact_score](/dimension/dim_contact_score.md) matching the rounded years since first contact (`CalculateFirstContact`), valid on the as-at date. Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `InvoiceGradeSK` | INT64 | SK of the grade row in [dim_grade](/dimension/dim_grade.md) matching `InvoiceCalPercent` (company grade bands by `Percentmin`..`Percentmax`, no date condition). Role-played use of dim_grade. Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `DueGradeSK` | INT64 | SK of the grade row in [dim_grade](/dimension/dim_grade.md) matching `DueCalPercent` (same join as `InvoiceGradeSK`). Valid only for rows whose `Year` is the year of yesterday's date at the last run; rows of earlier years keep the SK of their last computation. |
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID (via [dim_customer](/dimension/dim_customer.md)); NULL if no match. |
| `CompanyID` | STRING | MAC5 company code. |
| `Year` | INT64 | Calendar year the grade refers to (INT64). A run only computes the year of yesterday's date; earlier years keep the values from the last run in that year. |
| `CustomerCode` | STRING | MAC5 debtor code (`debcode`); with `CompanySK` and `Year` the natural key. |
| `CustomerName` | STRING | Customer name in Thai. |
| `CustomerLimit` | FLOAT64 | Credit limit of the customer in baht. |
| `CustomerCreditTerm` | INT64 | Credit term in days. |
| `CustomerMemo` | STRING | Free-text memo on the customer. |
| `SumPaymentReceive` | FLOAT64 | Total received (RS receipts, cheque-extract dates applied, rounded to 2 decimals) in `Year`; 0 when none. For BS/AS receipts, the amount is the linked bill's `mihnetsum`. RS receipts with header status 7 are included through 2022; other cancelled or not-received statuses are excluded. |
| `InvoiceDateAvgReceiveAgeDay` | FLOAT64 | Average days (rounded up) between invoice date and receipt date for receipts in `Year`, counting only late-positive differences; 0 when none. |
| `DueDateAvgReceiveAgeDay` | FLOAT64 | Average days (rounded up) between the computed due date (`invoice date + credit term`) and receipt date, counting only positive differences (paid late); 0 when none. |
| `CountCancelCheque` | INT64 | Number of distinct general-ledger account codes (`chqacode`) among cheque rows with `chqstatus = 2` (cancelled/bounced) dated in `Year`; rows with the same `chqacode` count once; 0 when none. |
| `CalculateFirstContact` | FLOAT64 | Years (days / 365.0) from the first-contact date to the day before the run. |
| `Credibility` | INT64 | Fixed credibility score of 20 for every row (hard-coded `20 as credibility_score`). |
| `FirstContactDate` | DATETIME | First-contact date: `debdate`, else the earliest MAC5 invoice (`mih`) date, else `debeditdt` (deb last-edit date). DATETIME. |
| `InvoiceCalPercent` | FLOAT64 | Overall score percent on the invoice-date basis: `(payment score + invoice avg-collection score + bounce score + contact score + 20 credibility) / 80 * 100`. |
| `InvoiceGrade` | STRING | Grade label looked up in [dim_grade](/dimension/dim_grade.md) for `InvoiceCalPercent`. |
| `DueCalPercent` | FLOAT64 | Overall score percent on the due-date basis: `(payment score + due avg-collection score + bounce score + contact score + 20 credibility) / 80 * 100`. |
| `DueGrade` | STRING | Grade label looked up in [dim_grade](/dimension/dim_grade.md) for `DueCalPercent`. |
| `asatdate` | DATE | Date the row was last computed (`CURRENT_DATE('Asia/Bangkok') - 1`). |

# How it is built

- Definition: `definitions/dimension/dim_customer_grade.sqlx` (`type: "operations"`, tag `dimension_daily`); the operation owns this table.
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md) (only the `Year` of yesterday's date), [validated_mac5.chq](/validated/validated_mac5/chq.md), [validated_mac5.cql](/validated/validated_mac5/cql.md), [validated_mac5.mie](/validated/validated_mac5/mie.md), [validated_mac5.mir](/validated/validated_mac5/mir.md), [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [dimension_table.dim_status_not_receive](/dimension/dim_status_not_receive.md), [dimension_table.dim_customer](/dimension/dim_customer.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [validated_mac5.mih](/validated/validated_mac5/mih.md), [dimension_table.dim_payment_receive_score](/dimension/dim_payment_receive_score.md), [dimension_table.dim_avg_collection_score](/dimension/dim_avg_collection_score.md), [dimension_table.dim_bounce_cheque_score](/dimension/dim_bounce_cheque_score.md), [dimension_table.dim_contact_score](/dimension/dim_contact_score.md), [dimension_table.dim_grade](/dimension/dim_grade.md).
- MERGE with stable SK in a `type: "operations"` file, tag `dimension_daily`, matching on `CustomerGradeSK` (existing `Year` + `CustomerCode` + `CompanySK`); updates all attribute columns, inserts new rows, no delete. Only the current year (year of yesterday) is recomputed each run; earlier years are not updated. Runs after `dim_customer`, `dim_aging`, `dim_status_not_receive`, `dim_calendar`, `dim_grade` and the four score dims (declared dependencies).

# Examples

Latest-year grades for one company, worst invoice-date percent first.

```sql
SELECT CustomerCode, CustomerSK, Year, SumPaymentReceive, InvoiceCalPercent, InvoiceGrade, DueGrade
FROM `databuffet-nonprd.dimension_table.dim_customer_grade`
WHERE CompanyID = 'ag01' AND Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
ORDER BY InvoiceCalPercent
LIMIT 50;
```

Distribution of grades by company for the current year.

```sql
SELECT CompanyID, InvoiceGrade, COUNT(*) AS customers
FROM `databuffet-nonprd.dimension_table.dim_customer_grade`
WHERE Year = EXTRACT(YEAR FROM CURRENT_DATE('Asia/Bangkok'))
GROUP BY CompanyID, InvoiceGrade
ORDER BY CompanyID, InvoiceGrade;
```
