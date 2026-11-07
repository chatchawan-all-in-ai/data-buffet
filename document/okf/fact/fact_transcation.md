---
type: BigQuery Table
title: "fact_transcation"
description: "One row = one bill line (IS/AS/BS/QS document line, milListno) per company, enriched with product, customer, channel, sales-organisation and marketing SKs, for the last four years."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=fact_table&t=fact_transcation&page=table"
project_id: databuffet-nonprd
dataset_id: fact_table
table_id: fact_transcation
tags: ["fact", "mds", "mac5", "fact_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/fact/fact_transcation.sqlx"
    title: "Dataform definition (fact/fact_transcation.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/fact/fact-layer.md"
    title: "Data Mart wiki (document/project_wiki/fact/fact-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T22:44:47+07:00" }
status: draft
---

# What it is

The main sales-transaction fact of the warehouse: every invoice-type bill line (IS invoice, AS, BS credit/return, QS) from MAC5, produced from `onetime.Transaction_Data_Mart` and joined to about 20 dimensions: product, payment, channel, customer address, marketing group (with an MDS re-map), the sale-representative chain (SaleRep -> Department -> Region -> RegionManager -> Section -> SectionManager -> Director, with 'Change*' current-organisation versions) and sales targets. It answers sales, discount, cost and VAT by product, customer, salesperson and organisation. The table name keeps the load-bearing typo `fact_transcation`.

Read by: [dim_pump_information](/dimension/dim_pump_information.md), [rls_customer360](/process/rls_customer360.md), [view_fact_salein_mdt](/view/fact_view/view_fact_salein_mdt.md), [view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row = one bill line (`milListno`) of one IS/AS/BS/QS document per customer, product and salesperson (`milPer`), per company: no unique key is declared; the upsert key is (`milVnos`, `milType`, `CompanySK`), i.e. a bill document, and all lines of a re-processed bill are deleted and re-inserted. The line is de-duplicated with `QUALIFY ROW_NUMBER() OVER(PARTITION BY CompanySK, milType, milVnos, milCus, LOWER(milStk), milPer, milListno ORDER BY seq_condition, (CASE WHEN MdsID IS NULL THEN 1 ELSE 0 END) DESC, companyID DESC, DepartmentID DESC, EmployeeID DESC, DepCode DESC, CostChannelID DESC, ProvinceID DESC, StartDate DESC, EndDate DESC) = 1`, keeping one sale-rep candidate per line; `curated_mil` splits ag01 lines into two rows by salesperson share (`percent_sale`) with different `milPer`, which stay separate rows. The final enrichment joins (address, marketing group, target) can still repeat a line, and `view_fact_transcation` re-applies a QUALIFY on the same partition. Window: rows with `mix_date >= start of year, 4 years ago`.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Surrogate key of the company, from [dim_company](/dimension/dim_company.md) joined on CompanyID in Transaction_Data_Mart; NULL if no match; part of the upsert key. |
| `companyID` | STRING | MAC5 company code (ag01, aa05, ab01, ac02, ak02). |
| `InvoiceProvinceSK` | INT64 | Province SK of the customer's address from `view_deb_address_data` (AI-parsed address, joined on milCus + company). |
| `InvoiceDistrictSK` | INT64 | District SK of the customer's address from view_deb_address_data. |
| `InvoiceSubDistrictSK` | INT64 | Sub-district SK of the customer's address from view_deb_address_data. |
| `StkMktSK` | INT64 | Surrogate key of `dim_stk_mkt` (marketing hierarchy of the product code, case-insensitive on milStk + CompanySK). |
| `FlagNewProductMKT` | BOOL | TRUE when a row of the MDS marketing-group re-map (`mds_data_change_marketinggroup_master`) matched this line, else FALSE. |
| `NewProductMktSK` | INT64 | Marketing-group SK after the MDS re-map: the re-mapped ProductMktSK when matched, otherwise the same as `ProductMktSK`. |
| `ProductMktSK` | INT64 | Surrogate key of [dim_product_mkt](/dimension/dim_product_mkt.md) via dim_stk_mkt (marketing group + sub group + segment + company), before any MDS re-map. |
| `TargetBySaleDayofworkSK` | INT64 | Key of `dim_target_product_group_by_sale_dayofwork` for the line's date, department and marketing group/sub/segment; NULL when no target row. |
| `TargetProductGroupSK` | INT64 | Target product-group SK from the same dim_target_product_group_by_sale_dayofwork row. |
| `RateTargetSK` | INT64 | Rate-target SK from the same dim_target_product_group_by_sale_dayofwork row. |
| `CustomerSK` | INT64 | Surrogate key of [dim_customer](/dimension/dim_customer.md) (`milCus = debcode`, CompanySK). |
| `SaleRepSK` | INT64 | Surrogate key of [dim_sale_representative](/dimension/dim_sale_representative.md) chosen per line: employee match on milPer (or DummyChannel) + date window + DepCode/customer/channel rules, best `seq_condition` kept (business-flags.md). |
| `DepartmentSK` | INT64 | Surrogate key of `dim_department` reached from the chosen sale rep (hierarchy chain). |
| `RegionSK` | INT64 | Surrogate key of [dim_region](/dimension/dim_region.md) from the sales-org chain of the chosen sale rep, unless the invoice-mapping rule applies. Mapping rule (shared by RegionSK, RegionManagerSK, SectionSK, SectionManagerSK and DirectorSK): for company ag01/ab01, when `onetime.mapping_invoice` has `FlagMustUser = TRUE` for the line (`milPer`, `milVnos`, company) or `mix_date` is in 202401-202601, the value is taken from the chain of the section in the mapping row (NULL when there is no mapping row or it has no section); for other companies, and for ag01/ab01 outside 202401-202601 without `FlagMustUser`, the sale-rep chain value is used. |
| `RegionManagerSK` | INT64 | Surrogate key of dim_region_manager from the chain; same mapping rule as RegionSK. |
| `SectionSK` | INT64 | Surrogate key of dim_section from the chain; same mapping rule as RegionSK. |
| `SectionManagerSK` | INT64 | Surrogate key of dim_section_manager from the chain; same mapping rule as RegionSK. |
| `DirectorSK` | INT64 | Surrogate key of [dim_director](/dimension/dim_director.md) from the chain; same mapping rule as RegionSK. |
| `CostStkSk` | INT64 | Surrogate key of dim_cost_stk. |
| `CostGroupSK` | INT64 | Surrogate key of dim_cost_group for the cost channel. |
| `ChangeSectionSK` | INT64 | Section SK under the 'change' (current organisation) chain via dim_change_district; used by view_fact_transcation for the `*Last` columns (passes through raw here). |
| `ChangeSectionManagerSK` | INT64 | Section-manager SK under the 'change' chain (raw pass-through, not subject to the mapping CASE). |
| `ChangeRegionSK` | INT64 | Region SK under the 'change' chain (raw pass-through). |
| `ChangeRegionManagerSK` | INT64 | Region-manager SK under the 'change' chain (raw pass-through). |
| `ChangeDirectorSK` | INT64 | Director SK under the 'change' chain (raw pass-through). |
| `ChannelSK` | INT64 | Channel SK from `view_dim_channel` matched on `milDep` (NULL milDep treated as 'N/A') + CompanySK. |
| `ChannelFinanceSK` | INT64 | Finance-channel SK from view_dim_channel. |
| `ChannelSaleSK` | INT64 | Sale-channel SK from view_dim_channel. |
| `ChannelCostSK` | INT64 | Cost-channel SK from view_dim_channel (re-derived for COST99999 lines via dim_channel_cost). |
| `ChannelCostID` | STRING | Cost channel code from view_dim_channel; the special value 'COST99999' routes the line to the part-2 re-derivation. |
| `PaymentSK` | INT64 | Surrogate key of dim_payment, matched on `memoextract = CodeMemo` + CompanySK. |
| `ProductSK` | INT64 | Surrogate key of [dim_product_master](/dimension/dim_product_master.md) (case-insensitive milStk + CompanySK). |
| `OrderProvinceSK` | INT64 | Province SK of the customer address (order side) from view_deb_address_data, carried from Transaction_Data_Mart. |
| `OrderDistrictSK` | INT64 | District SK (order side), same source. |
| `OrderSubDistrictSK` | INT64 | Sub-district SK (order side), same source. |
| `mix_date` | DATE | Business date of the line: PARSE_DATE of milYear, milMonth, milDay (Asia/Bangkok). Partition column; drives the 4-year retention. |
| `DummyChannel` | STRING | Dummy channel/employee code from view_dim_channel used instead of milPer in the sale-rep match; NULL when 'not calculated' or when the employee is a special ab01 rep. |
| `mihvatno` | STRING | Tax invoice number of the document. |
| `mihdesc` | STRING | Free-text document description. |
| `mihmemo` | STRING | Free-text document memo with an optional tag enclosed in `฿` signs. |
| `memoextract` | STRING | Tag extracted from the document memo, defaulting to `฿00฿` and matched to `dim_payment.CodeMemo`. |
| `mihmemonew` | STRING | Document memo with the tag enclosed in `฿` signs removed, or NULL when no text remains. |
| `mihCancel` | INT64 | Cancellation flag (-1 = cancelled, 0 = active). |
| `mihStatus` | INT64 | Document status code; meaning in `ar_s` for sales types and `ap_s` for purchase types (e.g. 26 = approved sales order, 30 = VAT sale, 32 = cancelled tax invoice). |
| `QuotationID` | INT64 | Id of the quotation linked to the order behind the bill (via milLinkvcno to a PS header), from Transaction_Data_Mart. |
| `QuotationCode` | STRING | Quotation running number of that quotation. |
| `milDay` | INT64 | Day part of the document date. |
| `milMonth` | INT64 | Month part of the document date. |
| `milYear` | INT64 | Year part of the document date (Gregorian). |
| `milType` | STRING | Document type code (QS = sales quotation, PS = sales order, IS = invoice, AS = debit note, BS = credit note, VS = billing statement, RS = receipt; purchase side QP, PP, IP, AP, BP, VP, RP); `BL` = billing document. |
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
| `milQuan` | FLOAT64 | Line quantity, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milQuan_raw` | FLOAT64 | Full line quantity before split-sale allocation, with negative values for BS credit notes. |
| `milQuanp2` | FLOAT64 | Quantity in the secondary unit. |
| `milAdisc` | FLOAT64 | Allocated header discount deducted from the line amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milAdisc_raw` | FLOAT64 | Full allocated header discount before split-sale allocation, with negative values for BS credit notes. |
| `milCog` | FLOAT64 | Gross line amount before discounts excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milCog_raw` | FLOAT64 | Full gross line amount before discounts excluding VAT and before split-sale allocation, with negative values for BS credit notes. |
| `milConv` | FLOAT64 | Unit conversion factor of the line (1 when no conversion). |
| `milDisca` | FLOAT64 | Line discount amount excluding VAT, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milDisca_raw` | FLOAT64 | Full line discount amount excluding VAT before split-sale allocation, with negative values for BS credit notes. |
| `milDisct` | STRING | Line discount as entered (a percentage such as `35`, or a formula text). |
| `milVat` | FLOAT64 | Line VAT amount, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
| `milVat_raw` | FLOAT64 | Full line VAT amount before split-sale allocation, with negative values for BS credit notes. |
| `milSum` | FLOAT64 | Net line amount excluding VAT after line and allocated header discounts, negative for BS credit notes and multiplied by the salesperson share for ag01 split-sale rows. |
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
| `milExchg` | FLOAT64 | Exchange rate to Thai baht (1 for baht documents). |
| `milAcost` | FLOAT64 | Average cost of the line. |
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
| `milCost` | FLOAT64 | Cost amount of the line. |
| `milUcost` | FLOAT64 | Unit cost of the line. |
| `milUprice` | FLOAT64 | Unit price of the line, excluding VAT. |
| `milUsequanp` | INT64 | Flag indicating use of the secondary-unit quantity (1 = yes). |
| `milVcol5` | STRING | User-defined text column 5 of the line. |
| `milFitem` | INT64 | Free-item flag of the line. |
| `asatdate` | DATE | Snapshot/extract date of the source line (`curated_mil.asatdate`). |
| `percent_sale` | STRING | Salesperson share of the line, a percent STRING such as '100.00%' (curated_mil split-sale: ag01 lines can be split into two rows with per_sale1/per_sale2). |
| `stkGroup` | STRING | Stock group code (joins `stg.stgcode`). |
| `Vat` | FLOAT64 | Allocated VAT passed through from [Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md#schema), which defines the calculation and window keys. |
| `milsum_incvat` | FLOAT64 | `milSum + Vat`, line amount including VAT. |
| `mildisca_incvat` | FLOAT64 | `milDisca * stkVat` (stock VAT multiplier) when the bill has VAT, otherwise milDisca. |
| `milcog_incvat` | FLOAT64 | `milCog * stkVat` when the bill has VAT, otherwise milCog. |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`) from Transaction_Data_Mart. |
| `DepositExcVat` | FLOAT64 | Deposit amount excluding VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero. |
| `DepositIncVat` | FLOAT64 | Deposit amount including VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero. |
| `DepositVat` | FLOAT64 | Deposit VAT allocated to the line by its share of the document net amount, or zero when the document net amount is zero. |

# How it is built

- Definition: `definitions/fact/fact_transcation.sqlx` (`type: "operations"`, tags `fact_daily`); the operation owns this table.
- Reads: [dimension_table.dim_department](/dimension/dim_department.md), [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_cost_stk](/dimension/dim_cost_stk.md), [dimension_table.dim_cost_group](/dimension/dim_cost_group.md), [dimension_table.dim_change_district](/dimension/dim_change_district.md), `mds_dataset.mds_data_change_marketinggroup_master` (master data loaded outside this repo), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [onetime.Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_payment](/dimension/dim_payment.md), [dimension_view.view_dim_channel](/view/dimension_view/view_dim_channel.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), `onetime.mapping_invoice`, [dimension_table.dim_channel_cost](/dimension/dim_channel_cost.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: `type: "operations"`, tag `fact_daily`: builds `temp_fact_transcation` from the whole 4-year window, then DELETE target rows whose (milVnos, milType, CompanySK) exist in the temp, INSERT the temp, then a retention DELETE of `mix_date` older than the 4-year start-of-year boundary (TEMP -> DELETE -> INSERT upsert, no MERGE). The target table pre-exists (Dataform does not create it) and `INSERT ... SELECT *` is positional. Runs after the dimensions and views listed in dependencies (Transaction_Data_Mart, view_dim_channel, view_deb_address_data, view_dim_invoice and ~18 dims).

# Examples

Sales-KPI-eligible net sales by month and company, via the preferred view with its sales exclusion flag applied.
```sql
SELECT companyID, DATE_TRUNC(mix_date, MONTH) AS month, SUM(milSum) AS sales_ex_vat
FROM `databuffet-nonprd.fact_view.view_fact_transcation`
WHERE mix_date >= DATE '2026-01-01' AND FlagSaleExc = 'No'
GROUP BY companyID, month ORDER BY month;
```
One bill's lines directly in the fact (including duplicates).
```sql
SELECT milListno, milStk, milPer, percent_sale, milQuan, milSum, SaleRepSK
FROM `databuffet-nonprd.fact_table.fact_transcation`
WHERE milVnos = '<bill no>' AND milType = 'IS' AND companyID = 'ag01'
ORDER BY milListno;
```
