---
type: BigQuery View
title: "Model_Invoice_Transaction"
description: "One row = one view_fact_transcation line of CompanySK 4 for 2024-2026 with IDs and names; a line repeats once per matching dim_product_master row."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=onetime&t=Model_Invoice_Transaction&page=table"
project_id: databuffet-nonprd
dataset_id: onetime
table_id: Model_Invoice_Transaction
tags: ["view", "onetime"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/onetime/Model_Invoice_Transaction.sqlx"
    title: "Dataform definition (view/onetime/Model_Invoice_Transaction.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T00:00:00+07:00" }
status: draft
---

# What it is

A denormalised, name-resolved sales transaction model. It takes [view_fact_transcation](/view/fact_view/view_fact_transcation.md), replaces all SKs with their IDs and names (channel, payment, document type, sales rep, section, region, director, product, marketing group, customer, province/district, report line) and renames measures to readable names (`NetSalesExcVat`, `Quantity`, ...). The org columns use the LATEST structure (`*_last` dims and `*SKLast` columns).

# Grain and key

One row = one `view_fact_transcation` line restricted to `milYear IN (2024, 2025, 2026)`, `milvnos IS NOT NULL` (drops the calendar filler rows) and `CompanySK = 4` (hard-coded): intended key is that of `view_fact_transcation` (`milVnos`, `milType`, `CompanySK`, plus line columns), not unique here. Most dimension joins use SK + `CompanySK`; the product join uses `LOWER(milStk) = LOWER(ProductCode)` + `CompanySK` (not `ProductSK`) against `dim_product_master`, so a line is repeated once per matching `dim_product_master` row and its measures repeat with it. There is no deduplication.

# Schema

| Column | Type | Description |
|---|---|---|
| `InvoiceDate` | DATE | Bill date (`view_fact_transcation.mix_date`). |
| `InvoiceYear` | INT64 | Year of the bill date (`milYear`). |
| `InvoiceMonth` | INT64 | Month of the bill date. |
| `InvoiceDay` | INT64 | Day of the bill date (`milDay`). |
| `InvoiceNo` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `InvoiceType` | STRING | Document type code from `dim_doctype.Code` (join on `milType` + company), e.g. IS/AS/BS. |
| `InvoiceTypeName` | STRING | English description of the document type (`dim_doctype.DescriptionEN`). |
| `InvoiceStatusID` | INT64 | Status code of the invoice header (`dim_invoice.mihStatus`, join on InvoiceSK). |
| `InvoiceStatusName` | STRING | Status text of the invoice header (`dim_invoice.StatusDesc`). |
| `InvoiceCancel` | STRING | `Yes` when `dim_invoice.mihCancel = -1`, else `No`. |
| `PaymentID` | STRING | Payment method id from `dim_payment` (join on PaymentSK). |
| `PaymentName` | STRING | Payment method name from `dim_payment`. |
| `PaymentType` | STRING | Payment type from `dim_payment`. |
| `ChannelCostID` | STRING | Cost-channel id from `dim_channel` (via ChannelSK). |
| `ChannelCostName` | STRING | Cost-channel name from `dim_channel`. |
| `ChannelSaleID` | STRING | Sales-channel id (`dim_channel.ChannelID`). |
| `ChannelSaleName` | STRING | Sales-channel name (`dim_channel.ChannelName`). |
| `ChannelSaleGroup` | STRING | Sales-channel group (`dim_channel.ChannelGroup`). |
| `ChannelSaleSubGroup1` | STRING | Sales-channel sub group 1 (`ChannelSubGroupName1`). |
| `ChannelSaleSubGroup2` | STRING | Sales-channel sub group 2 (`ChannelSubGroupName2`). |
| `ChannelFinanceID` | STRING | Finance-channel id (`dim_channel.ChannelIDFinance`). |
| `ChannelFinanceName` | STRING | Finance-channel name (`ChannelNameFinance`). |
| `ChannelFinanceGroup` | STRING | Finance-channel group (`ChannelGroupFinance`). |
| `ChannelFinanceSubGroup1` | STRING | Finance-channel sub group 1. |
| `ChannelFinanceSubGroup2` | STRING | Finance-channel sub group 2. |
| `ChannelFinanceSubGroup3` | STRING | Finance-channel sub group 3. |
| `ChannelD01Site` | STRING | Cost-centre dimension level 1 (site) from `dim_channel.ChannelDSite01`. |
| `ChannelD02Department` | STRING | Cost-centre dimension level 2 (department) from `ChannelDDepartment02`. |
| `ChannelD03Division` | STRING | Cost-centre dimension level 3 (division) from `ChannelDDivision03`. |
| `ChannelD04SubDivision` | STRING | Cost-centre dimension level 4 (sub division) from `ChannelDSubDivision04`. |
| `Job` | STRING | Job code of the line (sales job or project category such as `TT`, `SHOP`, or a project number). |
| `SalesRepID` | STRING | Employee id of the sales rep chosen under the LATEST structure (`dim_sale_representative_last.EmployeeID` via `SaleRepSKLast`). |
| `SalesRepNameSurname` | STRING | Concatenated first name and surname of that sales rep. |
| `DepartmentCode` | STRING | Department code of the line, used as the sales channel code. |
| `TeamID` | STRING | Department/team id of the sales rep in the latest structure (`dim_sale_representative_last.DepartmentID`). |
| `TeamName` | STRING | Department/team name (`dim_department_last.DepartmentName`). |
| `SectionID` | STRING | Section id under the latest structure, using `ChangeSectionSKLast` (so district/PS changes are applied). |
| `SectionName` | STRING | Section name (`dim_section_last`). |
| `SectionManagerNameSurname` | STRING | Concatenated name of the section manager under the latest structure. |
| `RegionID` | STRING | Region id under the latest structure (`RegionSKLast`). |
| `RegionName` | STRING | Region name (`dim_region_last`). |
| `RegionManagerNameSurname` | STRING | Concatenated name of the region manager under the latest structure. |
| `DirectorID` | STRING | Director id under the latest structure (`DirectorSKLast`). |
| `DirectorName` | STRING | Director name/group label (`dim_director_last.DirectorName`). |
| `DirectorSalesNameSurname` | STRING | Name of the director of sales (`dim_director_last.DirectorOfSalesName`). |
| `FlagSaleKPIExclude` | STRING | `view_fact_transcation.FlagSaleExc`: `Yes` = line excluded from the sales KPI. |
| `FlagSalesFiananceExclude` | STRING | `view_fact_transcation.FlagAccExc`: `Yes` = line excluded from finance sales (column name keeps the original typo `Fianance`). |
| `SCGSalesType` | STRING | `FlagSCG`: `ซื้อตรง` (direct) or `ซื้อผ่านร้าน` (through a shop) for SCG `CRC` documents, else NULL. |
| `Product` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `ProductName` | STRING | MAC5 product description (`dim_product_master.ProductMac5Description`). |
| `MarketingGroupID` | STRING | Marketing group id from `dim_product_mkt` via `ProductMktSK` (not `NewProductMktSK`). |
| `MarketingGroupName` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing group id. |
| `SubMarketingName` | STRING | Sub-marketing group name. |
| `SegmentID` | STRING | Segment id. |
| `SegmentName` | STRING | Segment name. |
| `NetSalesExcVat` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `NetSalesIncVat` | FLOAT64 | `milsum_incvat`: net sales including VAT. |
| `Quantity` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `DiscountAmountExcVat` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `DiscountAmountIncVat` | FLOAT64 | `mildisca_incvat`: discount including VAT. |
| `GrossAmountExcVat` | FLOAT64 | Gross line amount before discounts excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `GrossAmountIncVat` | FLOAT64 | `milcog_incvat`: gross amount including VAT. |
| `ProductCostPercent` | FLOAT64 | `ProductPercent`: cost percentage as a fraction from the cost-% rule; NULL when no rule. |
| `DepositExcVat` | FLOAT64 | Deposit amount excluding VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero. |
| `DepositIncVat` | FLOAT64 | Deposit amount including VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero. |
| `CustomerID` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `CustomerName` | STRING | Customer Thai name from `view_dim_customer.debnamet`. |
| `SubDistrict` | STRING | Sub-district name of the customer (`view_dim_customer.SubDistrict`). |
| `District` | STRING | District name of the customer. |
| `Province` | STRING | Province name of the customer. |
| `ReportID` | STRING | Report line id from `dim_report` (via `ReportSK`). |
| `ReportName1` | STRING | Report name level 1. |
| `ReportName2` | STRING | Report name level 2. |
| `TargetBySaleDayofworkSK` | INT64 | SK linking the line to the day-of-work target (`dim_target_product_group_by_sale_dayofwork`); join to `Model_Target_DayOfWork.TargetBySaleDayofworkSK`. |

# How it is built

- Definition: `definitions/view/onetime/Model_Invoice_Transaction.sqlx` (`type: "view"`, tags `view`).
- Reads: [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_payment](/dimension/dim_payment.md), [dimension_table.dim_doctype](/dimension/dim_doctype.md), [dimension_table.dim_channel](/dimension/dim_channel.md), [dimension_table.dim_channel_cost](/dimension/dim_channel_cost.md), [dimension_table.dim_report](/dimension/dim_report.md).

# Examples

Monthly net sales by sales-channel group, excluding lines flagged out of the sales KPI.

```sql
SELECT FORMAT_DATE('%Y-%m', InvoiceDate) AS month, ChannelSaleGroup,
       SUM(NetSalesExcVat) AS net_sales_exc_vat, SUM(Quantity) AS qty
FROM `databuffet-nonprd.onetime.Model_Invoice_Transaction`
WHERE FlagSaleKPIExclude = 'No'
GROUP BY month, ChannelSaleGroup
ORDER BY month, net_sales_exc_vat DESC
```

Net sales by region and marketing group for 2025.

```sql
SELECT RegionID, RegionName, MarketingGroupName, SUM(NetSalesExcVat) AS net_sales_exc_vat
FROM `databuffet-nonprd.onetime.Model_Invoice_Transaction`
WHERE InvoiceYear = 2025 AND FlagSaleKPIExclude = 'No'
GROUP BY RegionID, RegionName, MarketingGroupName
ORDER BY net_sales_exc_vat DESC
```
