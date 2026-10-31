---
type: BigQuery View
title: "view_fact_transcation"
description: "One row = one sales document line (IS/AS/BS/QS) per company with all org, product, customer, channel and flag SKs, plus one zero-valued row per company and date without any line."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_transcation&page=table"
tags: ["view", "fact_view", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_transcation.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_transcation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The main BI-facing sales (sell-in) transaction view. It starts from the physical table [fact_transcation](/fact/fact_transcation.md), keeps one row per document line by choosing one sale-rep match, adds the latest-structure (`*Last`) org assignments, the invoice/aging/order/quotation links, the customer-report link, sales-KPI and accounting exclusion flags, the SCG purchase type and the product cost percent, and finally gap-fills the calendar so every date of every company has at least one row. Customer-, invoice- and aging-level models ([Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [view_fact_salein_director_mdt](/view/fact_view/view_fact_salein_director_mdt.md)) read from it.

Used by [fact_view.view_fact_salein_director_mdt](/view/fact_view/view_fact_salein_director_mdt.md), [onetime.Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md).

# Grain and key

One row per sales line: (CompanySK, milType, milVnos, milCus, LOWER(milStk), milPer, milListno), enforced by `QUALIFY ROW_NUMBER() OVER (PARTITION BY ... ORDER BY seq_condition, dim_report.Segment, SaleRepSK DESC) = 1` in the `raw_table` step; this is what removes the per-line duplicates of `fact_transcation` created by the sale-rep and report joins. In addition, a calendar spine (`dim_calendar` x `dim_company`, from the start of the year 4 years ago up to yesterday, Asia/Bangkok) is LEFT JOINed, so dates without sales appear as one row with `milVnos` NULL, all measures 0 and `mix_date` = the calendar date; the `select distinct` at the end collapses identical rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactInvoiceSK` | INT64 | SK of `fact_invoice` matched on year, month, day, type, document no, customer, `milLinkVcno` and product (case-insensitive) and company; NULL when the line has no invoice row. Regenerated daily. |
| `InvoiceSK` | INT64 | SK of `dim_invoice` carried through `fact_invoice`; stable (MERGE dim). NULL for lines without an invoice row. |
| `AgingSK` | INT64 | SK of `dim_aging` via `view_dim_aging` (company + document number = `cfsVnosID`); regenerated daily; NULL when no aging row. |
| `AgingRangSK` | INT64 | SK of the aging bucket (`dim_aging_rang`) from `view_dim_aging`; NULL for companies without ranges. |
| `OrderSK` | INT64 | SK of `dim_order`: `COALESCE(fact_invoice.OrderSK, fact_order.OrderSK)` (invoice's order first). |
| `FactOrderSK` | INT64 | `COALESCE(fact_invoice.FactOrderSK, fact_order.FactOrderSK)`. |
| `QuotationSK` | INT64 | `COALESCE(fact_invoice.QuotationSK, fact_order.QuotationSK)`, link to `dim_quotation`. |
| `FactQuotationSK` | INT64 | `COALESCE(fact_invoice.FactQuotationSK, fact_order.FactQuotationSK)`. |
| `CustomerReportInfoSK` | INT64 | SK of `dim_customer_report_info` for the customer-report name on the invoice (whitespace-insensitive match); `-1` (reserved row) when the line has an invoice but the name is not found; NULL when there is no invoice. |
| `FlagSaleExc` | STRING | `Yes` when the line is flagged for exclusion from sales KPI: document cancelled or status 32/33 (`fn_flag_exc`), no linked order (`RefOrder` empty or doc no `0001`/`PRE...`), or matched by a rebate rule (customer, sales, product, text-split, dep) with `salesExc = 'Yes'`; otherwise `No`. |
| `FlagAccExc` | STRING | `Yes` when the line is flagged for exclusion from finance/accounting sales: cancelled or status 32/33, or matched by a rebate rule with `accExc = 'Yes'`; otherwise `No`. |
| `FlagMappingInvoice` | STRING | NULL for companies other than ag01/ab01. For ag01/ab01: `Yes` when the bill is re-mapped to a section through `onetime.mapping_invoice` (`FlagMustUser`, or a section id exists, or month between 202401 and 202601), `No` otherwise; NULL again outside that month window. Drives which org SKs are used. |
| `ReportSK` | INT64 | SK of the `dim_report` line (by region, and marketing group where a region has several lines); NULL when no line matches. |
| `SaleRepSKLast` | INT64 | SK of `dim_sale_representative_last` chosen for the line using the LATEST sale-rep snapshot (matching employee id, channel/dep, customer flag, province, order window by `seq_condition`); historical bills are re-assigned to the latest structure. |
| `DepartmentSKLast` | INT64 | Department SK under the latest structure; NULL when `FlagMappingInvoice = 'Yes'`. |
| `RegionSKLast` | INT64 | Region SK under the latest structure (from the sale-rep's section, or the mapped section when `FlagMappingInvoice = 'Yes'`). |
| `RegionManagerSKLast` | INT64 | Region-manager SK under the latest structure. |
| `SectionSKLast` | INT64 | Section SK under the latest structure. |
| `SectionManagerSKLast` | INT64 | Section-manager SK under the latest structure. |
| `DirectorSKLast` | INT64 | Director SK under the latest structure. |
| `ChangeSectionSKLast` | INT64 | Section SK after the change-section rules under the latest structure: Agent/PS customers moved to the new section from `dim_change_district` or a `Dummy999990` section when `ChangeSectionFlag = 'Yes'`; otherwise the same as `SectionSKLast`. |
| `ChangeSectionSK` | INT64 | Section SK at the bill date after the same change-section rules (district change, PS1-4 split, Dummy999990 placeholder). |
| `ChangeSectionManagerSK` | INT64 | Section-manager SK at the bill date after the change-section rules. |
| `ChangeRegionSK` | INT64 | Region SK at the bill date after the change-section rules. |
| `ChangeRegionManagerSK` | INT64 | Region-manager SK at the bill date after the change-section rules. |
| `ChangeDirectorSK` | INT64 | Director SK at the bill date after the change-section rules (placeholder `Non Director` row when applicable). |
| `PumpSK` | INT64 | SK of `dim_pump_information` matched on product, `FlagNewProductMKT`, region id and company. |
| `companyID` | STRING | Company code (ag01/aa05/ab01/ac02/ak02) from `dim_company`. |
| `InvoiceProvinceSK` | INT64 | Province SK of the invoiced customer's address (`view_deb_address_data`). |
| `InvoiceDistrictSK` | INT64 | District SK of the invoiced customer's address. |
| `InvoiceSubDistrictSK` | INT64 | Sub-district SK of the invoiced customer's address. |
| `StkMktSK` | INT64 | SK of `dim_stk_mkt` (product -> marketing group mapping). |
| `FlagNewProductMKT` | BOOL | TRUE when an mds mapping gives a `NewProductMktSK` for the product, else FALSE. |
| `NewProductMktSK` | INT64 | `COALESCE(mds NewProductMktSK, ProductMktSK)`: the marketing product-group SK to report on. |
| `ProductMktSK` | INT64 | SK of `dim_product_mkt` from the product's stk-marketing mapping. |
| `TargetBySaleDayofworkSK` | INT64 | SK of `dim_target_product_group_by_sale_dayofwork` matching day, department, marketing group/sub/segment and company (target link). |
| `TargetProductGroupSK` | INT64 | SK of `dim_target_product_group` from the same match. |
| `RateTargetSK` | INT64 | SK of `dim_rate_target` from the same match. |
| `CustomerSK` | INT64 | SK of `dim_customer` (stable MERGE dim). |
| `SaleRepSK` | INT64 | SK of `dim_sale_representative` valid at the bill date (as-of structure). |
| `DepartmentSK` | INT64 | SK of `dim_department` as of the bill date. |
| `RegionSK` | INT64 | SK of `dim_region` as of the bill date (mapping-invoice adjusted). |
| `RegionManagerSK` | INT64 | SK of `dim_region_manager` as of the bill date. |
| `SectionSK` | INT64 | SK of `dim_section` as of the bill date. |
| `SectionManagerSK` | INT64 | SK of `dim_section_manager` as of the bill date. |
| `DirectorSK` | INT64 | SK of `dim_director` as of the bill date. |
| `CostStkSk` | INT64 | SK of `dim_cost_stk` (product cost % rule) matched on product and cost channel; NULL if none. |
| `CostGroupSK` | INT64 | SK of `dim_cost_group` (cost % by product group) matched on group and cost channel. |
| `ChannelSK` | INT64 | SK of `dim_channel`/`view_dim_channel` from the line's department code (`milDep`). |
| `ChannelFinanceSK` | INT64 | Finance-channel SK of the same channel row. |
| `ChannelSaleSK` | INT64 | Sales-channel SK of the same channel row. |
| `ChannelCostSK` | INT64 | Cost-channel SK of the same channel row. |
| `ChannelCostID` | STRING | Cost-channel id of the channel row; `COST99999` rows are re-resolved in `fact_transcation`. |
| `PaymentSK` | INT64 | SK of `dim_payment` matched on `memoextract` + company. |
| `ProductSK` | INT64 | SK of `dim_product_master` (stable MERGE dim). |
| `OrderProvinceSK` | INT64 | Province SK of the customer's address (`view_deb_address_data`, AI-parsed from the debtor address), used for order-based rules. |
| `OrderDistrictSK` | INT64 | District SK of the customer's address. |
| `OrderSubDistrictSK` | INT64 | Sub-district SK of the customer's address. |
| `DummyChannel` | STRING | Channel code used instead of `milPer` for sale-rep matching when the channel defines one (`not calculated` values become NULL; also NULL for special ab01 employees). |
| `mihvatno` | STRING | VAT tax-invoice number of the document header (`curated_mih.mihvatno`). |
| `mihdesc` | STRING | Header description text of the document (`curated_mih.mihdesc`). |
| `mihmemo` | STRING | Header memo text (`curated_mih.mihmemo`). |
| `memoextract` | STRING | Payment code extracted from the memo; joins to `dim_payment.CodeMemo` to give `PaymentSK` (`curated_mih.memoextract`). |
| `mihmemonew` | STRING | Cleaned/new-format header memo (`curated_mih.mihmemonew`). |
| `QuotationID` | INT64 | Quotation id (`curated_tbook_quotation.id`) reached through the linked PS (order) document: `milLinkvcno -> PS mihVnos -> mihref1 = quotation running`. |
| `QuotationCode` | STRING | Quotation running number (`curated_tbook_quotation.running`) found the same way. |
| `milType` | STRING | MAC5 document type: `IS` invoice, `AS` debit note, `BS` credit note, `QS` is also included by the source filter `mihtype IN ('IS','AS','BS','QS')` (its meaning is not documented in the repo). |
| `milVnos` | STRING | Document number (`milVnos`); with `milType`, `milCus` and `milListno` it identifies the line. NULL on the zero-filled calendar rows of `view_fact_transcation`. |
| `milCus` | STRING | Customer code on the document; matches `dim_customer.debcode` / `validated_mac5.deb.debcode`. |
| `milStk` | STRING | MAC5 product (stock) code; matched case-insensitively to `dim_product_master.ProductCode` and `dim_stk_mkt.StkCode`. |
| `milJob` | STRING | Job code of the line (MAC5 `milJob`). |
| `milDep` | STRING | Department code of the line (MAC5 `milDep`); joins to `view_dim_channel.DepCode` (`ChannelSK`) and is used by the sale-rep matching rules. |
| `milPer` | STRING | Sales-person code of the line (employee id, matched to `dim_sale_representative`). For ag01 split-sale lines it is the share-owner. |
| `milPer_raw` | STRING | Sales-person code before the split-sale rewrite (`curated_mil.milPer_raw`). |
| `milDoc` | STRING | Pass-through of MAC5 `mil.milDoc`; meaning not documented in the repo |
| `milMec` | STRING | Pass-through of MAC5 `mil.milMec`; meaning not documented in the repo |
| `milSto` | STRING | Pass-through of MAC5 `mil.milSto`; meaning not documented in the repo |
| `milStomt` | STRING | Pass-through of MAC5 `mil.milStomt`; meaning not documented in the repo |
| `milListno` | INT64 | Line number inside the document. |
| `milQuan_raw` | FLOAT64 | Quantity before the split-sale division (full line quantity). |
| `milAdisc_raw` | FLOAT64 | `milAdisc` before the split-sale division. |
| `milCog_raw` | FLOAT64 | `milCog` before the split-sale division. |
| `milDisca_raw` | FLOAT64 | Discount amount before the split-sale division. |
| `milVat_raw` | FLOAT64 | `milVat` before the split-sale division. |
| `milSum_raw` | FLOAT64 | Line amount excluding VAT before the split-sale division. |
| `milCut` | INT64 | Boolean-like flag of the line (only -1/0 values, not a delivered quantity). |
| `milStype` | INT64 | Line type code (`milstype`); code list not documented in the repo. |
| `milUname` | STRING | Unit-of-measure name of the line (`milUname`, inferred from the name). |
| `milDesc` | STRING | Line description text. |
| `milVcol1` | STRING | Pass-through of MAC5 `mil.milVcol1`; meaning not documented in the repo |
| `milVcol2` | STRING | Pass-through of MAC5 `mil.milVcol2`; meaning not documented in the repo |
| `milVcol3` | STRING | Pass-through of MAC5 `mil.milVcol3`; meaning not documented in the repo |
| `milVcol4` | STRING | Pass-through of MAC5 `mil.milVcol4`; meaning not documented in the repo |
| `milCurc` | INT64 | Currency code of the line. |
| `milPqm` | INT64 | Pass-through of MAC5 `mil.milPqm`; meaning not documented in the repo |
| `milPmfrom` | INT64 | Pass-through of MAC5 `mil.milPmfrom`; meaning not documented in the repo |
| `milPmto` | INT64 | Pass-through of MAC5 `mil.milPmto`; meaning not documented in the repo |
| `milTag` | INT64 | Pass-through of MAC5 `mil.milTag`; meaning not documented in the repo |
| `milLinkvcno` | STRING | Number of the linked document (e.g. the order PS document for an invoice, or the invoice for a note); used to find orders/quotations and by `fn_flag_scg`. |
| `milLinkvcdate` | DATETIME | Date of the linked document. |
| `milLinkvctype` | STRING | Type of the linked document. |
| `milLinkvcdeposit` | STRING | Pass-through of MAC5 `mil.milLinkvcdeposit`; meaning not documented in the repo |
| `milLinkvcid` | INT64 | Pass-through of MAC5 `mil.milLinkvcid`; meaning not documented in the repo |
| `milClearum` | INT64 | Pass-through of MAC5 `mil.milClearum`; meaning not documented in the repo |
| `milExpdate` | DATETIME | Expiry date on the line (inferred from the name). |
| `milNotes` | STRING | Line notes. |
| `milNotkl` | INT64 | Pass-through of MAC5 `mil.milNotkl`; meaning not documented in the repo |
| `milDelvdt` | DATETIME | Delivery date of the line (inferred from the name). |
| `milDatesp` | DATETIME | Pass-through of MAC5 `mil.milDatesp`; meaning not documented in the repo |
| `milNumcsp` | FLOAT64 | Pass-through of MAC5 `mil.milNumcsp`; meaning not documented in the repo |
| `milNumisp` | INT64 | Pass-through of MAC5 `mil.milNumisp`; meaning not documented in the repo |
| `milUsequanp` | INT64 | Pass-through of MAC5 `mil.milUsequanp`; meaning not documented in the repo |
| `milVcol5` | STRING | Pass-through of MAC5 `mil.milVcol5`; meaning not documented in the repo |
| `milFitem` | INT64 | Pass-through of MAC5 `mil.milFitem`; meaning not documented in the repo |
| `asatdate` | DATE | Load date (ASATDATE) of the source `curated_mil` row; not a business date. |
| `percent_sale` | STRING | Split-sale share of this line as text (e.g. `60.00%`); `100.00%` when the line is not split (only ag01 splits lines between two sales people). |
| `stkGroup` | STRING | MAC5 stock group of the product (`validated_mac5.stk.stkgroup`). |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`). |
| `ProductPercent` | FLOAT64 | Cost percentage as a fraction (`dim_cost_stk.Percent/100`, or the group percent), rounded to 4 decimals; NULL when no cost rule. |
| `FlagProductPercent` | STRING | Source of ProductPercent: `% Stk` (product rule) or `% Group` (group rule); NULL if none. |
| `FlagSCG` | STRING | SCG sales type via `fn_flag_scg`: for document numbers starting `CRC`, `ซื้อตรง` (direct purchase) or `ซื้อผ่านร้าน` (through a shop) depending on whether the customer is in the SCG customer list; NULL otherwise. |
| `CompanySK` | INT64 | SK of `dim_company`; filled from the calendar on zero-filled rows. |
| `mix_date` | DATE | Bill date (`milYear/milMonth/milDay`). On the zero-filled calendar rows of `view_fact_transcation` it is the calendar date. |
| `milDay` | INT64 | Day of the bill date. |
| `milMonth` | INT64 | Month of the bill date. |
| `milYear` | INT64 | Year of the bill date. |
| `milQuan` | FLOAT64 | Quantity of the line (after split-sale division). 0 on zero-filled calendar rows. |
| `milQuanp2` | FLOAT64 | Pass-through of MAC5 `mil.milQuanp2`; meaning not documented in the repo |
| `milAdisc` | FLOAT64 | Additional/line discount amount from MAC5 (`milAdisc`, after split-sale); not documented further in the repo. |
| `milCog` | FLOAT64 | Gross line amount excluding VAT (`milCog`; surfaced as `GrossAmountExcVat` in `Model_Invoice_Transaction`). |
| `milConv` | FLOAT64 | Unit conversion factor of the line (inferred from the name). |
| `milDisca` | FLOAT64 | Discount amount of the line excluding VAT (`DiscountAmountExcVat` in `Model_Invoice_Transaction`). |
| `milDisct` | STRING | Discount text/expression of the line as entered in MAC5 (inferred from the name). |
| `milVat` | FLOAT64 | VAT figure carried on the MAC5 line (`milVat`); the allocated document VAT is the separate `Vat` column. |
| `milSum` | FLOAT64 | Net line amount excluding VAT (`NetSalesExcVat`). |
| `milExchg` | FLOAT64 | Exchange rate of the line. |
| `milAcost` | FLOAT64 | Pass-through of MAC5 `mil.milAcost`; meaning not documented in the repo |
| `milCost` | FLOAT64 | Cost amount of the line (MAC5 `milCost`, inferred from the name). |
| `milUcost` | FLOAT64 | Unit cost (inferred from the name). |
| `milUprice` | FLOAT64 | Unit price (inferred from the name). |
| `Vat` | FLOAT64 | VAT of the document allocated to the line: `milSum / SUM(milSum over document) * mihVatsum` (sign flipped for `BS` credit notes); 0 when the document total is 0. |
| `milsum_incvat` | FLOAT64 | Net amount including VAT: `milSum + Vat`. |
| `mildisca_incvat` | FLOAT64 | Discount amount including VAT: `milDisca * stkVat` when the document carries VAT (`mihVatsum <> 0`), else `milDisca`. |
| `milcog_incvat` | FLOAT64 | Gross amount including VAT: `milCog * stkVat` when the document carries VAT, else `milCog`. |
| `DepositExcVat` | FLOAT64 | Share of the document's extra/deposit amount (`mihExtrasum`) allocated to this line by `milSum` weight, excluding VAT. |
| `DepositIncVat` | FLOAT64 | Allocated deposit including VAT (`mihExtrasum` + `mihExtravat` shares). |
| `DepositVat` | FLOAT64 | VAT part of the allocated deposit. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_transcation.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_rebate](/dimension/dim_rebate.md), [dimension_table.dim_report](/dimension/dim_report.md), [fact_table.fact_transcation](/fact/fact_transcation.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), `onetime.mapping_invoice`, [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_pump_information](/dimension/dim_pump_information.md), `function_dataset.fn_flag_scg` (UDF), [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_channel](/dimension/dim_channel.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_change_district](/dimension/dim_change_district.md), [dimension_table.dim_cost_stk](/dimension/dim_cost_stk.md), [dimension_table.dim_cost_group](/dimension/dim_cost_group.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), `function_dataset.fn_flag_exc` (UDF), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [fact_table.fact_invoice](/fact/fact_invoice.md), [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md), [fact_table.fact_order](/fact/fact_order.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md).
- Logical view (`type: "view"`, tag `view`): `CREATE OR REPLACE VIEW`, no data is stored, so every query reads the current content of the base tables. It is (re)deployed by running tag `view`; its base `fact_transcation` (tag `fact_daily`) is rebuilt first after all org/product/customer dims (`dimension_daily`). It reads the `*_last` dims for the latest org structure, `fact_invoice`, `fact_order`, `view_dim_aging`, `view_dim_invoice`, `dim_rebate`, `dim_customer_report_info`, `onetime.mapping_invoice` and UDFs `fn_flag_exc` / `fn_flag_scg`.

# Examples

Net sales excluding VAT per company and month, KPI-eligible lines only (calendar rows contribute 0).

```sql
SELECT companyID, DATE_TRUNC(mix_date, MONTH) AS month, SUM(milSum) AS net_sales_exc_vat, SUM(milsum_incvat) AS net_sales_inc_vat
FROM `databuffet-nonprd.fact_view.view_fact_transcation`
WHERE FlagSaleExc = 'No' OR FlagSaleExc IS NULL
GROUP BY companyID, month
ORDER BY companyID, month
```

Lines of one document.

```sql
SELECT milType, milVnos, milListno, milStk, milQuan, milSum, FlagSaleExc, FlagAccExc
FROM `databuffet-nonprd.fact_view.view_fact_transcation`
WHERE companyID = 'ag01' AND milVnos = '<document no>' AND mix_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 YEAR)
ORDER BY milListno
```
