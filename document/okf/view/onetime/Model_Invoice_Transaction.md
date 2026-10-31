---
type: BigQuery View
title: "Model_Invoice_Transaction"
description: "Sales rows of CompanySK 4 for 2024-2026 enriched with names; retained product barcode versions can repeat each source row and its measures."
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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

A denormalised, name-resolved sales transaction model meant to be loaded straight into a BI semantic model (the `onetime` dataset holds data marts and Power BI models). It takes [view_fact_transcation](/view/fact_view/view_fact_transcation.md), replaces all SKs with their IDs and names (channel, payment, document type, sales rep, section, region, director, product, marketing group, customer, province/district, report line) and renames measures to readable names (`NetSalesExcVat`, `Quantity`, ...). The org columns use the LATEST structure (`*_last` dims and `*SKLast` columns). Product enrichment can repeat measures.

No other object in this repo reads it; it is meant to be queried directly (BI tools or ad-hoc SQL).

# Grain and key

Starts from rows of `view_fact_transcation` restricted to `milYear IN (2024, 2025, 2026)`, `milvnos IS NOT NULL` (drops the calendar filler rows) and `CompanySK = 4` (hard-coded; which company that is is not documented in the SQL). Most dimension joins use SK + CompanySK, but the product join uses LOWER(milStk) = LOWER(ProductCode) + CompanySK, not ProductSK. It emits every retained barcode version, so one eligible 100-baht source row can become two model rows totalling 200. There is no deduplication of that product expansion.

# Schema

| Column | Type | Description |
|---|---|---|
| `InvoiceDate` | DATE | Bill date (`view_fact_transcation.mix_date`). |
| `InvoiceYear` | INT64 | Year of the bill date (`milYear`). |
| `InvoiceMonth` | INT64 | Month of the bill date (`milMonth`). |
| `InvoiceDay` | INT64 | Day of the bill date (`milDay`). |
| `InvoiceNo` | STRING | Document number (`milVnos`). |
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
| `Job` | STRING | Job code of the line (`milJob`). |
| `SalesRepID` | STRING | Employee id of the sales rep chosen under the LATEST structure (`dim_sale_representative_last.EmployeeID` via `SaleRepSKLast`). |
| `SalesRepNameSurname` | STRING | Concatenated first name and surname of that sales rep. |
| `DepartmentCode` | STRING | Department code written on the line (`milDep`), the key used for channel lookup. |
| `TeamID` | STRING | Department/team id of the sales rep in the latest structure (`dim_sale_representative_last.DepartmentID`). |
| `TeamName` | STRING | Department/team name (`dim_department_last.DepartmentName`). |
| `SectionID` | STRING | Section id under the latest structure, using `ChangeSectionSKLast` (so district/PS changes are applied). |
| `SectionName` | STRING | Section name (`dim_section_last`). |
| `SectionManagerNameSurname` | STRING | Concatenated name of the section manager under the latest structure (personal data). |
| `RegionID` | STRING | Region id under the latest structure (`RegionSKLast`). |
| `RegionName` | STRING | Region name (`dim_region_last`). |
| `RegionManagerNameSurname` | STRING | Concatenated name of the region manager under the latest structure (personal data). |
| `DirectorID` | STRING | Director id under the latest structure (`DirectorSKLast`). |
| `DirectorName` | STRING | Director name/group label (`dim_director_last.DirectorName`). |
| `DirectorSalesNameSurname` | STRING | Name of the director of sales (`dim_director_last.DirectorOfSalesName`, personal data). |
| `FlagSaleKPIExclude` | STRING | `view_fact_transcation.FlagSaleExc`: `Yes` = line excluded from the sales KPI. |
| `FlagSalesFiananceExclude` | STRING | `view_fact_transcation.FlagAccExc`: `Yes` = line excluded from finance sales (column name keeps the original typo `Fianance`). |
| `SCGSalesType` | STRING | `FlagSCG`: `ซื้อตรง` (direct) or `ซื้อผ่านร้าน` (through a shop) for SCG `CRC` documents, else NULL. |
| `Product` | STRING | MAC5 product code (`milstk`). |
| `ProductName` | STRING | MAC5 product description (`dim_product_master.ProductMac5Description`). |
| `MarketingGroupID` | STRING | Marketing group id from `dim_product_mkt` via `ProductMktSK` (not `NewProductMktSK`). |
| `MarketingGroupName` | STRING | Marketing group name. |
| `SubMarketingID` | STRING | Sub-marketing group id. |
| `SubMarketingName` | STRING | Sub-marketing group name. |
| `SegmentID` | STRING | Segment id. |
| `SegmentName` | STRING | Segment name. |
| `NetSalesExcVat` | FLOAT64 | `milsum`: net sales of the line excluding VAT. |
| `NetSalesIncVat` | FLOAT64 | `milsum_incvat`: net sales including VAT. |
| `Quantity` | FLOAT64 | `milQuan`: quantity sold (after split-sale for ag01). |
| `DiscountAmountExcVat` | FLOAT64 | `milDisca`: discount amount excluding VAT. |
| `DiscountAmountIncVat` | FLOAT64 | `mildisca_incvat`: discount including VAT. |
| `GrossAmountExcVat` | FLOAT64 | `milCog`: gross amount excluding VAT. |
| `GrossAmountIncVat` | FLOAT64 | `milcog_incvat`: gross amount including VAT. |
| `ProductCostPercent` | FLOAT64 | `ProductPercent`: cost percentage as a fraction from the cost-% rule; NULL when no rule. |
| `DepositExcVat` | FLOAT64 | Deposit/extra amount allocated to the line excluding VAT. |
| `DepositIncVat` | FLOAT64 | Deposit/extra amount allocated to the line including VAT. |
| `CustomerID` | STRING | Customer code (`milcus`). |
| `CustomerName` | STRING | Customer Thai name from `view_dim_customer.debnamet`. |
| `SubDistrict` | STRING | Sub-district name of the customer (`view_dim_customer.SubDistrict`). |
| `District` | STRING | District name of the customer. |
| `Province` | STRING | Province name of the customer. |
| `ReportID` | STRING | Report line id from `dim_report` (via `ReportSK`). |
| `ReportName1` | STRING | Report name level 1. |
| `ReportName2` | STRING | Report name level 2. |
| `TargetBySaleDayofworkSK` | INT64 | SK linking the line to the day-of-work target (`dim_target_product_group_by_sale_dayofwork`); join to `Model_Target_DayOfWork.TargetBySaleDayofworkSK` (regenerated daily). |

# How it is built

- Definition: `definitions/view/onetime/Model_Invoice_Transaction.sqlx` (`type: "view"`, tags `view`).
- Reads: [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_section_manager_last](/dimension/dim_section_manager_last.md), [dimension_table.dim_region_manager_last](/dimension/dim_region_manager_last.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_payment](/dimension/dim_payment.md), [dimension_table.dim_doctype](/dimension/dim_doctype.md), [dimension_table.dim_channel](/dimension/dim_channel.md), [dimension_table.dim_channel_cost](/dimension/dim_channel_cost.md), [dimension_table.dim_report](/dimension/dim_report.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; depends on `view_fact_transcation` (so on `fact_transcation`, tag `fact_daily`) and the `*_last` dims, `dim_channel`, `dim_payment`, `dim_doctype`, `dim_invoice`, `dim_product_master`, `dim_product_mkt`, `view_dim_customer`, `dim_report`, all rebuilt first.

# Examples

Monthly net sales by sales-channel group before product enrichment, with the model's company/year scope and sales-KPI filter.

```sql
SELECT FORMAT_DATE('%Y-%m', s.mix_date) AS month, ch.ChannelGroup AS ChannelSaleGroup,
       SUM(s.milSum) AS net_sales_exc_vat, SUM(s.milQuan) AS qty
FROM `databuffet-nonprd.fact_view.view_fact_transcation` AS s
LEFT JOIN `databuffet-nonprd.dimension_table.dim_channel` AS ch
  ON s.ChannelSK = ch.ChannelSK AND s.CompanySK = ch.CompanySK
WHERE s.CompanySK = 4 AND s.milYear IN (2024, 2025, 2026)
  AND s.milVnos IS NOT NULL AND s.FlagSaleExc = 'No'
GROUP BY month, ch.ChannelGroup
ORDER BY month, net_sales_exc_vat DESC
```

Net sales by latest region and marketing group for 2025 before product enrichment; same-run dimension joins use their matching SKs.

```sql
SELECT r.RegionID, r.RegionName, m.MarketingGroup AS MarketingGroupName,
       SUM(s.milSum) AS net_sales_exc_vat
FROM `databuffet-nonprd.fact_view.view_fact_transcation` AS s
LEFT JOIN `databuffet-nonprd.dimension_table.dim_region_last` AS r
  ON s.RegionSKLast = r.RegionSK AND s.CompanySK = r.CompanySK
LEFT JOIN `databuffet-nonprd.dimension_table.dim_product_mkt` AS m
  ON s.ProductMktSK = m.ProductMktSK AND s.CompanySK = m.CompanySK
WHERE s.CompanySK = 4 AND s.milYear = 2025
  AND s.milVnos IS NOT NULL AND s.FlagSaleExc = 'No'
GROUP BY r.RegionID, r.RegionName, m.MarketingGroup
ORDER BY net_sales_exc_vat DESC
```
