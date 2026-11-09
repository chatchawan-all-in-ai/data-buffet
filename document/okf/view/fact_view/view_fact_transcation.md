---
type: BigQuery View
title: "view_fact_transcation"
description: "One row = one sales document line (IS/AS/BS/QS) per company with all org, product, customer, channel and flag SKs, plus one zero-valued row per company and date without any line."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_view&t=view_fact_transcation&page=table"
project_id: databuffet-nonprd
dataset_id: fact_view
table_id: view_fact_transcation
tags: ["view", "fact_view"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/view/fact_view/view_fact_transcation.sqlx"
    title: "Dataform definition (view/fact_view/view_fact_transcation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/view/view-layer.md"
    title: "Data Mart wiki (document/project_wiki/view/view-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-08T22:57:16+07:00" }
status: draft
---

# What it is

The main sales (sell-in) transaction view. It starts from the physical table [fact_transcation](/fact/fact_transcation.md), keeps one row per document line by choosing one sale-rep match, adds the latest-structure (`*Last`) org assignments, the invoice/aging/order/quotation links, the customer-report link, sales-KPI and accounting exclusion flags, the SCG purchase type and the product cost percent, and finally gap-fills the calendar so every date of every company has at least one row.

Read by: [Model_Invoice_Transaction](/view/onetime/Model_Invoice_Transaction.md), [export_view_fact_transcation](/view/pub_sub/export_view_fact_transcation.md) and [view_fact_salein_director_mdt](/view/fact_view/view_fact_salein_director_mdt.md).

# Grain and key

One row = one sales document line (IS/AS/BS/QS): intended key `CompanySK`, `milType`, `milVnos`, `milCus`, `LOWER(milStk)`, `milPer`, `milListno`. The `raw_table` step keeps one sale-rep/report match per key with `QUALIFY ROW_NUMBER() OVER (PARTITION BY ... ORDER BY seq_condition, dim_report.Segment, (CASE WHEN DepartmentID IS NULL THEN 1 ELSE 0 END) DESC, CompanySK DESC, DepartmentID DESC, EmployeeID DESC, DepCode DESC, CostChannelID DESC, ProvinceID DESC) = 1`; the later LEFT JOINs to `dim_product_master` (`t4`), `dim_rebate` (customer, sales, product, department and text-split aliases), `fact_invoice` (`t2`), `view_dim_aging`, `fact_order` (`t3`), linked `view_dim_invoice` (`t6`) and `dim_customer_report_info` (`cri`) are not guarded and can add rows, so uniqueness of the key is not guaranteed. In particular, `t6` groups by `CompanySK`, `mihType`, `mihVnos` but joins only on company and `milLinkVcno = mihVnos`, without matching document type; several types sharing a linked number can match and yield different `FlagSaleExc` values that survive the final DISTINCT. In addition, a calendar spine (`dim_calendar` x `dim_company`, from the start of the year 4 years ago up to yesterday, Asia/Bangkok) is LEFT JOINed, so dates without sales appear as one row with `milVnos` NULL, all measures 0 and `mix_date` = the calendar date; the `select distinct` at the end collapses identical rows.

# Schema

| Column | Type | Description |
|---|---|---|
| `FactInvoiceSK` | INT64 | Row key of [fact_invoice](/fact/fact_invoice.md#grain-and-key), matched on year, month, day, type, document no, customer, `milLinkVcno` and product (case-insensitive) and company; NULL when the line has no invoice row. |
| `InvoiceSK` | INT64 | SK of `dim_invoice` carried through `fact_invoice`; stable (MERGE dim). NULL for lines without an invoice row. |
| `AgingSK` | INT64 | SK of `dim_aging` via `view_dim_aging` (company + document number = `cfsVnosID`); regenerated daily; NULL when no aging row. |
| `AgingRangSK` | INT64 | SK of the aging bucket (`dim_aging_rang`) from `view_dim_aging`; NULL for companies without ranges. |
| `OrderSK` | INT64 | SK of `dim_order`: `COALESCE(fact_invoice.OrderSK, fact_order.OrderSK)` (invoice's order first). |
| `FactOrderSK` | INT64 | `COALESCE(fact_invoice.FactOrderSK, fact_order.FactOrderSK)`. |
| `QuotationSK` | INT64 | `COALESCE(fact_invoice.QuotationSK, fact_order.QuotationSK)`, link to `dim_quotation`. |
| `FactQuotationSK` | INT64 | `COALESCE(fact_invoice.FactQuotationSK, fact_order.FactQuotationSK)`. |
| `CustomerReportInfoSK` | INT64 | SK of `dim_customer_report_info` for the customer-report name on the invoice (whitespace-insensitive match); `-1` (reserved row) when the line has an invoice but the name is not found; NULL when there is no invoice. |
| `FlagSaleExc` | STRING | `Yes` when the line is flagged for exclusion from sales KPI: document cancelled or status 32/33 (`fn_flag_exc`), no linked order (`RefOrder` empty or doc no `0001`/`PRE...`), or matched by a rebate rule (customer, sales, product, text-split) with `salesExc = 'Yes'`; otherwise `No`; NULL on calendar rows. |
| `FlagAccExc` | STRING | `Yes` when the line is flagged for exclusion from finance/accounting sales: cancelled or status 32/33, or matched by a rebate rule with `accExc = 'Yes'`; otherwise `No`; NULL on calendar rows. |
| `Project` | STRING | Project / site name cut from the free-text invoice note `mihdesc` (`#`-separated): the first segment containing `โครงการ` (a leading `คุณ` directly before `โครงการ` is removed); if none, the first segment before `#` (leading `#` skipped); NULL when the note is empty. Often a delivery instruction (`ลงร้าน`, `ส่งต่อ`) or a branch name on non-project bills. NULL on calendar rows. |
| `IsProject` | STRING | `Yes` when `mihdesc` contains `โครงการ` (always equals "`Project` contains `โครงการ`"); otherwise `No`. Under 0.2% of `Yes` bills are not projects (location notes such as `ตรงข้ามโครงการ…`). NULL on calendar rows. |
| `FlagMappingInvoice` | STRING | NULL for companies other than ag01/ab01. For ag01/ab01: evaluated in order: `Yes` when `onetime.mapping_invoice.FlagMustUser` is true; NULL when the bill month is outside 202401–202601; `Yes` when the bill month is within 202401–202601 (so the later section-id and `No` branches are never reached). Drives which org SKs are used. |
| `ReportSK` | INT64 | SK of the `dim_report` line (by region, and marketing group where a region has several lines); NULL when no line matches. |
| `SaleRepSKLast` | INT64 | SK of `dim_sale_representative_last` chosen for the line using the LATEST sale-rep snapshot (matching employee id, channel/dep, customer flag, province, order window by `seq_condition`); historical bills are re-assigned to the latest structure. |
| `DepartmentSKLast` | INT64 | Department SK under the latest structure; NULL when `FlagMappingInvoice = 'Yes'`. |
| `RegionSKLast` | INT64 | Region SK under the latest structure (from the sale-rep's section, or the mapped section when `FlagMappingInvoice = 'Yes'`). |
| `RegionManagerSKLast` | INT64 | Region-manager SK under the latest structure. |
| `SectionSKLast` | INT64 | Section SK under the latest structure. |
| `SectionManagerSKLast` | INT64 | Section-manager SK under the latest structure. |
| `DirectorSKLast` | INT64 | Director SK under the latest structure. |
| `ChangeSectionSKLast` | INT64 | Section SK under the latest structure, evaluated in order: (1) mapped director `dir_map.DirectorName` is Agent and the alphabetic-only parts of `trans.SectionID` and `chg_dis_map.newSectionID` match: use `change_sec_map_sk.SectionSK`; (2) mapped director starts with PS and `trans.SectionID` is PS1-4: use the flag/fallback rules below, before testing the PS prefix match; (3) mapped director starts with PS and the first three characters of those section IDs match: use `change_sec_map_sk.SectionSK`; (4) all remaining rows use the same flag/fallback rules. Director and section comparisons are case-insensitive. Flag/fallback rules: when `FlagMappingInvoice` is NULL, `sale_sk.ChangeSectionFlag = 'Yes'` uses `COALESCE(change_sec_sk.SectionSK, dummy_sec_last.SectionSK)` (dummy `Dummy999990`), otherwise `sec_sk.SectionSK`; when `FlagMappingInvoice = 'Yes'`, use `sec_map_sk.SectionSK`; any other flag value returns NULL. Both `change_sec_map_sk` and `sec_map_sk` match the latest section by `trans.SectionMappingID` + company. |
| `ChangeSectionSK` | INT64 | Section SK at the bill date after the same change-section rules (district change, PS1-4 split, Dummy999990 placeholder). |
| `ChangeSectionManagerSK` | INT64 | Section-manager SK at the bill date after the change-section rules. |
| `ChangeRegionSK` | INT64 | Region SK at the bill date after the change-section rules. |
| `ChangeRegionManagerSK` | INT64 | Region-manager SK at the bill date after the change-section rules. |
| `ChangeDirectorSK` | INT64 | Director SK at the bill date after the change-section rules (placeholder `Non Director` row when applicable). |
| `PumpSK` | INT64 | SK of `dim_pump_information` matched on product, `FlagNewProductMKT`, region id and company. |
| `companyID` | STRING | MAC5 company code from `dim_company`; NULL on the zero-filled calendar rows. |
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
| `mihvatno` | STRING | Tax invoice number of the document. |
| `mihdesc` | STRING | Free-text document description. |
| `mihmemo` | STRING | Free-text document memo with an optional tag enclosed in `฿` signs. |
| `memoextract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `mihmemonew` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `QuotationID` | INT64 | Quotation id (`curated_tbook_quotation.id`) reached through the linked PS (order) document: `milLinkvcno -> PS mihVnos -> mihref1 = quotation running`. |
| `QuotationCode` | STRING | Quotation running number (`curated_tbook_quotation.running`) found the same way. |
| `milType` | STRING | Document type code (`IS` = invoice, `AS` = debit note, `BS` = credit note, `QS` = sales quotation). |
| `milVnos` | STRING | Document number of the line, matching `mihvnos` of the header. |
| `milCus` | STRING | Customer code (supplier code on purchase documents), matching `deb.debcode`. |
| `milStk` | STRING | Product (stock) code of the line, matching `stk.stkcode`. |
| `milJob` | STRING | Job code of the line (sales job or project category such as `TT`, `SHOP`, or a project number). |
| `milDep` | STRING | Department code of the line, used as the sales channel code. |
| `milPer` | STRING | Salesperson code of the line, replaced by the second salesperson's code on the second ag01 split-sale row. |
| `milPer_raw` | STRING | Original salesperson code before the split-sale override. |
| `milDoc` | STRING | Document print-form code of the line from the MAC5 `doc` master. |
| `milMec` | STRING | Memo-card code of the line, matching `mec.meccode`. |
| `milSto` | STRING | Warehouse (store) code the line is issued from, matching `sto` store codes. |
| `milStomt` | STRING | Destination warehouse code for transfer lines. |
| `milListno` | INT64 | Line number within the document. |
| `milQuan_raw` | FLOAT64 | Full line quantity before split-sale allocation, with negative values for BS credit notes. |
| `milAdisc_raw` | FLOAT64 | Full allocated header discount before split-sale allocation, with negative values for BS credit notes. |
| `milCog_raw` | FLOAT64 | Full gross line amount before discounts excluding VAT and before split-sale allocation, with negative values for BS credit notes. |
| `milDisca_raw` | FLOAT64 | Full line discount amount excluding VAT before split-sale allocation, with negative values for BS credit notes. |
| `milVat_raw` | FLOAT64 | Full line VAT amount before split-sale allocation, with negative values for BS credit notes. |
| `milSum_raw` | FLOAT64 | Full net line amount excluding VAT after line and allocated header discounts and before split-sale allocation, with negative values for BS credit notes. |
| `milCut` | INT64 | Flag: line deducts stock (-1 = yes). |
| `milStype` | INT64 | Line item type (1 = item, 2 = serial-tracked item, 3 = service). |
| `milUname` | STRING | Unit name of the line (e.g. `SET`, `ชุด`, `Pcs.`). |
| `milDesc` | STRING | Free-text line description. |
| `milVcol1` | STRING | User-defined text column 1 of the line. |
| `milVcol2` | STRING | User-defined text column 2 of the line. |
| `milVcol3` | STRING | User-defined text column 3 of the line. |
| `milVcol4` | STRING | User-defined text column 4 of the line. |
| `milCurc` | INT64 | Currency code (0 = Thai baht). |
| `milPqm` | INT64 | Price-quantity mode of the line. |
| `milPmfrom` | INT64 | Start of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milPmto` | INT64 | End of the line-number range the line belongs to (equals `millistno` for ordinary lines). |
| `milTag` | INT64 | Tag marker of the line. |
| `milLinkvcno` | STRING | Number of the source document this line was created from (e.g. the sales order of an invoice line). |
| `milLinkvcdate` | DATETIME | Date of the linked source document. |
| `milLinkvctype` | STRING | Document type of the linked source document (e.g. `PS`, `PP`). |
| `milLinkvcdeposit` | STRING | Deposit amount and VAT deducted from the linked document, stored as `amount/VAT` text. |
| `milLinkvcid` | INT64 | Internal ID of the linked source-document line. |
| `milClearum` | INT64 | Flag: outstanding quantity of the line cleared (0 = still open). |
| `milExpdate` | DATETIME | Expiry date of the line item. |
| `milNotes` | STRING | Free-text line notes. |
| `milNotkl` | INT64 | Flag indicating that the line is excluded from stock reservation. |
| `milDelvdt` | DATETIME | Requested delivery date of the line. |
| `milDatesp` | DATETIME | Special date of the line. |
| `milNumcsp` | FLOAT64 | Special numeric field of the line. |
| `milNumisp` | INT64 | Special integer field of the line. |
| `milUsequanp` | INT64 | Flag indicating use of the secondary-unit quantity (1 = yes). |
| `milVcol5` | STRING | User-defined text column 5 of the line. |
| `milFitem` | INT64 | Free-item flag of the line. |
| `asatdate` | DATE | Load date (ASATDATE) of the source `curated_mil` row; not a business date. |
| `percent_sale` | STRING | Split-sale share of this line as text (e.g. `60.00%`); `100.00%` when the line is not split (only ag01 splits lines between two sales people). |
| `stkGroup` | STRING | Stock group code (joins `stg.stgcode`). |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`). |
| `ProductPercent` | FLOAT64 | Cost percentage as a fraction (`dim_cost_stk.Percent/100`, or the group percent), rounded to 4 decimals; NULL when no cost rule. |
| `FlagProductPercent` | STRING | Source of ProductPercent: `% Stk` (product rule) or `% Group` (group rule); NULL if none. |
| `FlagSCG` | STRING | SCG sales type via `fn_flag_scg`: for document numbers starting `CRC`, `ซื้อตรง` (direct purchase) or `ซื้อผ่านร้าน` (through a shop) depending on whether the customer is in the SCG customer list; NULL otherwise. |
| `CompanySK` | INT64 | SK of `dim_company`; filled from the calendar on zero-filled rows. |
| `mix_date` | DATE | Bill date (`milYear/milMonth/milDay`). On the zero-filled calendar rows of `view_fact_transcation` it is the calendar date. |
| `milDay` | INT64 | Day of the bill date. |
| `milMonth` | INT64 | Month of the bill date. |
| `milYear` | INT64 | Year of the bill date. |
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milQuanp2` | FLOAT64 | Quantity in the secondary unit; zero on calendar rows without a transaction. |
| `milAdisc` | FLOAT64 | Allocated header discount deducted from the line amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milCog` | FLOAT64 | Gross line amount before discounts excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milConv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion); zero on calendar rows without a transaction. |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milDisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milVat` | FLOAT64 | Line VAT amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milSum` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows; zero on calendar rows without a transaction. |
| `milExchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents); zero on calendar rows without a transaction. |
| `milAcost` | FLOAT64 | Average cost of the line; zero on calendar rows without a transaction. |
| `milCost` | FLOAT64 | Cost amount of the line; zero on calendar rows without a transaction. |
| `milUcost` | FLOAT64 | Unit cost of the line; zero on calendar rows without a transaction. |
| `milUprice` | FLOAT64 | Unit price of the line, excluding VAT; zero on calendar rows without a transaction. |
| `Vat` | FLOAT64 | Allocated VAT passed through from `fact_transcation`; calculation and window keys are defined in [Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md#schema); 0 on calendar rows without a transaction. |
| `milsum_incvat` | FLOAT64 | Net amount including VAT: `milSum + Vat`; 0 on calendar rows without a transaction. |
| `mildisca_incvat` | FLOAT64 | Discount amount including VAT: `milDisca * stkVat` when the document carries VAT (`mihVatsum <> 0`), else `milDisca`; 0 on calendar rows without a transaction. |
| `milcog_incvat` | FLOAT64 | Gross amount including VAT: `milCog * stkVat` when the document carries VAT, else `milCog`; 0 on calendar rows without a transaction. |
| `DepositExcVat` | FLOAT64 | Deposit amount excluding VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero; zero on calendar rows without a transaction. |
| `DepositIncVat` | FLOAT64 | Deposit amount including VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero; zero on calendar rows without a transaction. |
| `DepositVat` | FLOAT64 | Deposit VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero; zero on calendar rows without a transaction. |

# How it is built

- Definition: `definitions/view/fact_view/view_fact_transcation.sqlx` (`type: "view"`, tags `view`).
- Reads: [dimension_table.dim_calendar](/dimension/dim_calendar.md), [dimension_table.dim_company](/dimension/dim_company.md), [dimension_table.dim_rebate](/dimension/dim_rebate.md), [dimension_table.dim_report](/dimension/dim_report.md), [fact_table.fact_transcation](/fact/fact_transcation.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), `onetime.mapping_invoice`, [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_pump_information](/dimension/dim_pump_information.md), `function_dataset.fn_flag_scg` (UDF), [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_channel](/dimension/dim_channel.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [dimension_table.dim_section_last](/dimension/dim_section_last.md), [dimension_table.dim_director_last](/dimension/dim_director_last.md), [dimension_table.dim_change_district](/dimension/dim_change_district.md), [dimension_table.dim_cost_stk](/dimension/dim_cost_stk.md), [dimension_table.dim_cost_group](/dimension/dim_cost_group.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_region_last](/dimension/dim_region_last.md), [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), `function_dataset.fn_flag_exc` (UDF), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [fact_table.fact_invoice](/fact/fact_invoice.md), [dimension_view.view_dim_aging](/view/dimension_view/view_dim_aging.md), [fact_table.fact_order](/fact/fact_order.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md).

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
