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
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

The main sales-transaction fact of the warehouse: every invoice-type bill line (IS invoice, AS, BS credit/return, QS) from MAC5, produced from `onetime.Transaction_Data_Mart` and joined to about 20 dimensions: product, payment, channel, customer address, marketing group (with an MDS re-map), the sale-representative chain (SaleRep -> Department -> Region -> RegionManager -> Section -> SectionManager -> Director, with 'Change*' current-organisation versions) and sales targets. It answers sales, discount, cost and VAT by product, customer, salesperson and organisation. The table name keeps the load-bearing typo `fact_transcation`. Consumers: `view_fact_transcation` (the BI-facing view that filters the expected duplicates), `view_fact_salein_mdt`, [dim_pump_information](/dimension/dim_pump_information.md) and [rls_customer360](/process/rls_customer360.md).

Used by / context: used by [dimension_table.dim_pump_information](/dimension/dim_pump_information.md), [process_dataset.rls_customer360](/process/rls_customer360.md), [fact_view.view_fact_salein_mdt](/view/fact_view/view_fact_salein_mdt.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row per bill line, but the upsert key is only (`milVnos`, `milType`, `CompanySK`), i.e. a bill document; all lines of a re-processed bill are deleted and re-inserted. There are expected per-line duplicates: `curated_mil` splits ag01 lines into two rows by salesperson share (`percent_sale`) and the sale-rep match can leave more than one candidate per line, so the same line can appear several times; `view_fact_transcation` filters them. Window: rows with `mix_date >= start of year, 4 years ago`.

# Schema

| Column | Type | Description |
|---|---|---|
| `CompanySK` | INT64 | Surrogate key of [dim_company](/dimension/dim_company.md), carried from Transaction_Data_Mart; part of the upsert key. |
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
| `RegionSK` | INT64 | Surrogate key of [dim_region](/dimension/dim_region.md) from the sales-org chain; when FlagMappingInvoice is 'Yes' it is replaced by the mapping-invoice section's region, 'No' gives NULL. |
| `RegionManagerSK` | INT64 | Surrogate key of dim_region_manager from the chain; same FlagMappingInvoice override as RegionSK. |
| `SectionSK` | INT64 | Surrogate key of dim_section from the chain; replaced by the mapping section when FlagMappingInvoice = 'Yes', NULL when 'No'. |
| `SectionManagerSK` | INT64 | Surrogate key of dim_section_manager; same override rule as SectionSK. |
| `DirectorSK` | INT64 | Surrogate key of [dim_director](/dimension/dim_director.md); same override rule as RegionSK. |
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
| `mihvatno` | STRING | VAT document number from the invoice header (`curated_mih.mihvatno`), via Transaction_Data_Mart. |
| `mihdesc` | STRING | Header description text (`curated_mih.mihdesc`). |
| `mihmemo` | STRING | Header memo text (`curated_mih.mihmemo`). |
| `memoextract` | STRING | Payment code extracted from the memo (`curated_mih.memoextract`); join key to dim_payment.CodeMemo. |
| `mihmemonew` | STRING | New-style header memo (`curated_mih.mihmemonew`). Meaning not documented in the repo. |
| `mihCancel` | INT64 | Header cancel flag (`curated_mih.mihCancel`; 0 = not cancelled in other facts). |
| `mihStatus` | INT64 | Header status code (`curated_mih.mihStatus`). |
| `QuotationID` | INT64 | Id of the quotation linked to the order behind the bill (via milLinkvcno to a PS header), from Transaction_Data_Mart. |
| `QuotationCode` | STRING | Quotation running number of that quotation. |
| `milDay` | INT64 | Pass-through of `curated_mil.milDay` via `onetime.Transaction_Data_Mart`; day of the bill date. |
| `milMonth` | INT64 | Pass-through of `curated_mil.milMonth` via `onetime.Transaction_Data_Mart`; month of the bill date. |
| `milYear` | INT64 | Pass-through of `curated_mil.milYear` via `onetime.Transaction_Data_Mart`; year of the bill date. |
| `milType` | STRING | Bill document type: IS, AS, BS or QS (Transaction_Data_Mart filters `mihtype IN ('IS','AS','BS','QS')`); BS is treated as a credit (negative VAT sign). |
| `milVnos` | STRING | Bill document number; part of the upsert key with milType and CompanySK. |
| `milCus` | STRING | Customer code (joins `dim_customer.debcode`). |
| `milStk` | STRING | Product code of the line. |
| `milJob` | STRING | Pass-through of `curated_mil.milJob` via `onetime.Transaction_Data_Mart`; job code used by some MDS marketing re-map rules. |
| `milDep` | STRING | Pass-through of `curated_mil.milDep` via `onetime.Transaction_Data_Mart`; department code; join key to view_dim_channel.DepCode and the DepCode sale-rep rules. |
| `milPer` | STRING | Pass-through of `curated_mil.milPer` via `onetime.Transaction_Data_Mart`; salesperson (employee) code; after the split-sale logic of curated_mil, for ag01 this is the share-owning salesperson. |
| `milPer_raw` | STRING | Pass-through of `curated_mil.milPer_raw` via `onetime.Transaction_Data_Mart`; salesperson before the split-sale row duplication. |
| `milDoc` | STRING | Pass-through of `curated_mil.milDoc` via `onetime.Transaction_Data_Mart`; document code Meaning not documented in the repo.. |
| `milMec` | STRING | Pass-through of `curated_mil.milMec` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milSto` | STRING | Pass-through of `curated_mil.milSto` via `onetime.Transaction_Data_Mart`; store/warehouse code. |
| `milStomt` | STRING | Pass-through of `curated_mil.milStomt` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milListno` | INT64 | Pass-through of `curated_mil.milListno` via `onetime.Transaction_Data_Mart`; line number within the bill. |
| `milQuan` | FLOAT64 | Pass-through of `curated_mil.milQuan` via `onetime.Transaction_Data_Mart`; quantity after split-sale allocation for ag01. |
| `milQuan_raw` | FLOAT64 | Pass-through of `curated_mil.milQuan_raw` via `onetime.Transaction_Data_Mart`; quantity before split-sale allocation. |
| `milQuanp2` | FLOAT64 | Pass-through of `curated_mil.milQuanp2` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milAdisc` | FLOAT64 | Pass-through of `curated_mil.milAdisc` via `onetime.Transaction_Data_Mart`; discount amount, after split-sale allocation. |
| `milAdisc_raw` | FLOAT64 | Pass-through of `curated_mil.milAdisc_raw` via `onetime.Transaction_Data_Mart`; before split-sale allocation. |
| `milCog` | FLOAT64 | Pass-through of `curated_mil.milCog` via `onetime.Transaction_Data_Mart`; gross line amount excluding VAT, after split-sale allocation. |
| `milCog_raw` | FLOAT64 | Pass-through of `curated_mil.milCog_raw` via `onetime.Transaction_Data_Mart`; full gross line amount excluding VAT before split-sale allocation. |
| `milConv` | FLOAT64 | Pass-through of `curated_mil.milConv` via `onetime.Transaction_Data_Mart`; conversion factor (inferred from the name). |
| `milDisca` | FLOAT64 | Pass-through of `curated_mil.milDisca` via `onetime.Transaction_Data_Mart`; discount amount, after split-sale allocation. |
| `milDisca_raw` | FLOAT64 | Pass-through of `curated_mil.milDisca_raw` via `onetime.Transaction_Data_Mart`; before split-sale allocation. |
| `milDisct` | STRING | Pass-through of `curated_mil.milDisct` via `onetime.Transaction_Data_Mart`; discount text/code (inferred). |
| `milVat` | FLOAT64 | Pass-through of `curated_mil.milVat` via `onetime.Transaction_Data_Mart`; VAT, after split-sale allocation. |
| `milVat_raw` | FLOAT64 | Pass-through of `curated_mil.milVat_raw` via `onetime.Transaction_Data_Mart`; before split-sale allocation. |
| `milSum` | FLOAT64 | Pass-through of `curated_mil.milSum` via `onetime.Transaction_Data_Mart`; net line amount excluding VAT in THB, after split-sale allocation. |
| `milSum_raw` | FLOAT64 | Pass-through of `curated_mil.milSum_raw` via `onetime.Transaction_Data_Mart`; before split-sale allocation. |
| `milCut` | INT64 | Pass-through of `curated_mil.milCut` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milStype` | INT64 | Pass-through of `curated_mil.milStype` via `onetime.Transaction_Data_Mart`; line type: 1 Item, 2 Serial, 3 Service as used in the store facts. |
| `milUname` | STRING | Pass-through of `curated_mil.milUname` via `onetime.Transaction_Data_Mart`; unit name (inferred). |
| `milDesc` | STRING | Pass-through of `curated_mil.milDesc` via `onetime.Transaction_Data_Mart`; line description. |
| `milVcol1` | STRING | Pass-through of `curated_mil.milVcol1` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milVcol2` | STRING | Pass-through of `curated_mil.milVcol2` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milVcol3` | STRING | Pass-through of `curated_mil.milVcol3` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milVcol4` | STRING | Pass-through of `curated_mil.milVcol4` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milCurc` | INT64 | Pass-through of `curated_mil.milCurc` via `onetime.Transaction_Data_Mart`; currency code (inferred). |
| `milExchg` | FLOAT64 | Pass-through of `curated_mil.milExchg` via `onetime.Transaction_Data_Mart`; exchange rate (inferred). |
| `milAcost` | FLOAT64 | Pass-through of `curated_mil.milAcost` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milPqm` | INT64 | Pass-through of `curated_mil.milPqm` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milPmfrom` | INT64 | Pass-through of `curated_mil.milPmfrom` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milPmto` | INT64 | Pass-through of `curated_mil.milPmto` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milTag` | INT64 | Pass-through of `curated_mil.milTag` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milLinkvcno` | STRING | Pass-through of `curated_mil.milLinkvcno` via `onetime.Transaction_Data_Mart`; number of the linked document (the originating order, used to find QuotationID). |
| `milLinkvcdate` | DATETIME | Pass-through of `curated_mil.milLinkvcdate` via `onetime.Transaction_Data_Mart`; date of the linked document (inferred). |
| `milLinkvctype` | STRING | Pass-through of `curated_mil.milLinkvctype` via `onetime.Transaction_Data_Mart`; type of the linked document (inferred). |
| `milLinkvcdeposit` | STRING | Pass-through of `curated_mil.milLinkvcdeposit` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milLinkvcid` | INT64 | Pass-through of `curated_mil.milLinkvcid` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milClearum` | INT64 | Pass-through of `curated_mil.milClearum` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milExpdate` | DATETIME | Pass-through of `curated_mil.milExpdate` via `onetime.Transaction_Data_Mart`; expiry date (inferred). |
| `milNotes` | STRING | Pass-through of `curated_mil.milNotes` via `onetime.Transaction_Data_Mart`; line notes. |
| `milNotkl` | INT64 | Pass-through of `curated_mil.milNotkl` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milDelvdt` | DATETIME | Pass-through of `curated_mil.milDelvdt` via `onetime.Transaction_Data_Mart`; delivery date (inferred). |
| `milDatesp` | DATETIME | Pass-through of `curated_mil.milDatesp` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milNumcsp` | FLOAT64 | Pass-through of `curated_mil.milNumcsp` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milNumisp` | INT64 | Pass-through of `curated_mil.milNumisp` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milCost` | FLOAT64 | Pass-through of `curated_mil.milCost` via `onetime.Transaction_Data_Mart`; cost (inferred). |
| `milUcost` | FLOAT64 | Pass-through of `curated_mil.milUcost` via `onetime.Transaction_Data_Mart`; unit cost (inferred). |
| `milUprice` | FLOAT64 | Pass-through of `curated_mil.milUprice` via `onetime.Transaction_Data_Mart`; unit price (inferred). |
| `milUsequanp` | INT64 | Pass-through of `curated_mil.milUsequanp` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milVcol5` | STRING | Pass-through of `curated_mil.milVcol5` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `milFitem` | INT64 | Pass-through of `curated_mil.milFitem` via `onetime.Transaction_Data_Mart`; Meaning not documented in the repo.. |
| `asatdate` | DATE | Snapshot/extract date of the source line (`curated_mil.asatdate`). |
| `percent_sale` | STRING | Salesperson share of the line, a percent STRING such as '100.00%' (curated_mil split-sale: ag01 lines can be split into two rows with per_sale1/per_sale2). |
| `stkGroup` | STRING | Product group code from the stock master (`stk.stkgroup`) via Transaction_Data_Mart. |
| `Vat` | FLOAT64 | VAT amount allocated to the line: `milSum / over_milsum * mihVatsum` (sign flipped for BS), where over_milsum is the bill total; 0 when the bill total is 0. |
| `milsum_incvat` | FLOAT64 | `milSum + Vat`, line amount including VAT. |
| `mildisca_incvat` | FLOAT64 | `milDisca * stkVat` (stock VAT multiplier) when the bill has VAT, otherwise milDisca. |
| `milcog_incvat` | FLOAT64 | `milCog * stkVat` when the bill has VAT, otherwise milCog. |
| `Barcode` | STRING | Product barcode (`stk.stkcode885`) from Transaction_Data_Mart. |
| `DepositExcVat` | FLOAT64 | Share of the bill's deposit/extra sum (`mihExtrasum`) allocated to the line by `milSum / bill total`, excluding VAT. |
| `DepositIncVat` | FLOAT64 | Allocated deposit including its VAT (`mihExtrasum + mihExtravat` shares). |
| `DepositVat` | FLOAT64 | Allocated VAT of the deposit (`mihExtravat` share). |

# How it is built

- Definition: `definitions/fact/fact_transcation.sqlx` (`type: "operations"`, tags `fact_daily`); the operation owns this table.
- Reads: [dimension_table.dim_department](/dimension/dim_department.md), [dimension_table.dim_section](/dimension/dim_section.md), [dimension_table.dim_section_manager](/dimension/dim_section_manager.md), [dimension_table.dim_region](/dimension/dim_region.md), [dimension_table.dim_region_manager](/dimension/dim_region_manager.md), [dimension_table.dim_director](/dimension/dim_director.md), [dimension_table.dim_cost_stk](/dimension/dim_cost_stk.md), [dimension_table.dim_cost_group](/dimension/dim_cost_group.md), [dimension_table.dim_change_district](/dimension/dim_change_district.md), `mds_dataset.mds_data_change_marketinggroup_master` (master data loaded outside this repo), [dimension_table.dim_product_mkt](/dimension/dim_product_mkt.md), [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [onetime.Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md), [dimension_table.dim_payment](/dimension/dim_payment.md), [dimension_view.view_dim_channel](/view/dimension_view/view_dim_channel.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), `onetime.mapping_invoice`, [dimension_table.dim_channel_cost](/dimension/dim_channel_cost.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [dimension_table.dim_target_product_group_by_sale_dayofwork](/dimension/dim_target_product_group_by_sale_dayofwork.md), [dimension_table.dim_customer](/dimension/dim_customer.md).
- Refresh: `type: "operations"`, tag `fact_daily`: builds `temp_fact_transcation` from the whole 4-year window, then DELETE target rows whose (milVnos, milType, CompanySK) exist in the temp, INSERT the temp, then a retention DELETE of `mix_date` older than the 4-year start-of-year boundary (TEMP -> DELETE -> INSERT upsert, no MERGE). The target table pre-exists (Dataform does not create it) and `INSERT ... SELECT *` is positional. Runs after the dimensions and views listed in dependencies (Transaction_Data_Mart, view_dim_channel, view_deb_address_data, view_dim_invoice and ~18 dims).
- Approximate size (BigQuery metadata, 2026-10-31): 2,721,231 rows, 2.6 GB.

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
