# Dimension

Star-schema dimensions in `dimension_table` (surrogate keys, mds and lake sourced).

# Tables

* [dim_aging](dim_aging.md) - One row = one AR document (tax invoice IS, credit note BS or debit note AS) per company with its payment, credit/debit-note adjustments, outstanding balance, completion flag and invoice-group flag.
* [dim_aging_history](dim_aging_history.md) - One row = one AR document in a non-completed group, captured under the prior-day asatdate label; kept for the latest label and month-ends.
* [dim_aging_rang](dim_aging_rang.md) - One row = one aging bucket (min and max days past due, with its report label) defined per company in MDS master data.
* [dim_avg_collection_score](dim_avg_collection_score.md) - One row = one score band (min/max average collection days, validity period) per company, used to score a customer's average receipt age.
* [dim_bounce_cheque_score](dim_bounce_cheque_score.md) - Score bands for the customer-grade CountCancelCheque metric; see the card for grain and bounds.
* [dim_calendar](dim_calendar.md) - One row = one calendar date with day/week/month/quarter/year labels and weekend, holiday and long-weekend flags.
* [dim_change_district](dim_change_district.md) - One row = one customer-to-new-section reassignment (customer, old section, new section, validity period) per company, from the MDS change-section master.
* [dim_channel](dim_channel.md) - One row = one department code (DepCode) per company with its sales, cost and finance channel classification, from the MDS channel master.
* [dim_channel_cost](dim_channel_cost.md) - One row = one cost channel (code and name) per company, from the MDS cost-channel master.
* [dim_channel_finance](dim_channel_finance.md) - One row = one finance channel (code and name) per company, from the MDS finance-channel master.
* [dim_channel_sales](dim_channel_sales.md) - One row = one sales channel (code and name) per company, from the MDS sales-channel master.
* [dim_collection_status](dim_collection_status.md) - One row = one collection follow-up record (company, year, month, customer) with the action, justification and responsible person, from the MDS collection-status master.
* [dim_company](dim_company.md) - One row = one MAC5 company (ag01, aa05, ab01, ac02, ak02) with its code, Thai and English names and a stable surrogate key.
* [dim_contact_score](dim_contact_score.md) - One row = one score band (min/max years since first contact, validity period) per company, used to score customer relationship length.
* [dim_cost_group](dim_cost_group.md) - One row = one standard-cost percentage for a product group (GAccID) in a cost channel for a validity period, per company.
* [dim_cost_stk](dim_cost_stk.md) - One row = one product-level (MilStk) standard-cost percentage in a cost channel for a validity period, per company.
* [dim_customer](dim_customer.md) - One row = one MAC5 customer (debtor) per company, enriched with CIS360 customer-360 attributes (ag01 only) and parsed invoice-address SKs.
* [dim_customer_grade](dim_customer_grade.md) - One row = one customer per company per year with payment, collection-speed, bounced-cheque and relationship scores and the resulting credit grade.
* [dim_customer_report_info](dim_customer_report_info.md) - One row = one customer report name (shop/account name as shown on reports, whitespace-insensitive) per company, with segment, TA (team-area) chain, sale rep, address and online-shop attributes.
* [dim_customer_segment](dim_customer_segment.md) - One row = one customer segment code (Segment1/2/3 with Thai and English descriptions) per company, plus a reserved -1 'Non-Segment' row.
* [dim_delivery](dim_delivery.md) - One row = one invoice document on a delivery trip (MAC5 IS document) per company with trip, vehicle, item quantity and preparation/release/receipt status counts.
* [dim_department](dim_department.md) - One row = one sales department (company, region, section, department id) with its validity period, from the MDS sales-department master.
* [dim_department_last](dim_department_last.md) - One row = the latest-period row of each department per company, taken from dim_department, with placeholder FK columns for section, region and director.
* [dim_director](dim_director.md) - One row = one sales director (company, DirectorID) with the director of sales and a validity period, from the MDS sales-director master.
* [dim_director_last](dim_director_last.md) - One row = the latest-period row of each director per company, taken from dim_director.
* [dim_doctype](dim_doctype.md) - One row = one document-type code (AccountCategory + Code) per company with English and Thai descriptions, from the MDS document-type master.
* [dim_grade](dim_grade.md) - One row = one grade band (min/max score percentage, grade label, validity period) per company, used to turn a customer's total score into a grade.
* [dim_group_customer](dim_group_customer.md) - One row = one customer group (`debgroup`) per company, used to group customers that belong to the same account group.
* [dim_group_customer_grade](dim_group_customer_grade.md) - One row = one customer group per company per year with payment, collection-speed, bounced-cheque and relationship scores and the resulting credit grade.
* [dim_guarantee](dim_guarantee.md) - One row = one bank guarantee (BG) document for a customer at a bank (company, customer code, bank name), with its limit and expiry date, from the MDS guarantee master.
* [dim_holiday](dim_holiday.md) - One row = one public holiday date with Thai and English names and a long-weekend flag, from the MDS holiday master.
* [dim_invoice](dim_invoice.md) - One row = one sales document per distinct linked order number (NULL when unlinked), company, customer and date, with sales-split percentages.
* [dim_order](dim_order.md) - One row = one MAC5 sales order (document type PS) per company with header attributes, status text and a derived fulfilment status (On Order / In Process / Complete).
* [dim_payment](dim_payment.md) - One row = one payment memo code (CodeMemo) per company with its payment id, name, method (EN/TH) and type, from the MDS payment master.
* [dim_payment_receive_score](dim_payment_receive_score.md) - One row = one score band (min/max total payment received, validity period) per company, used to score a customer's yearly payment volume.
* [dim_pc](dim_pc.md) - One row = one promoter/PC (product consultant) assignment (employee, MDT branch, marketing group, period) from the MDS PC master, plus a reserved -1 'unknown' row.
* [dim_product_master](dim_product_master.md) - One row = one MAC5 stock item (product code) per company and barcode, enriched with MAC5 stock-group, MASTERSKU product master data and marketing-group SKs.
* [dim_product_master_fc](dim_product_master_fc.md) - One row = one product/variant (by barcode) per company from the MDS finance product master, with MAC5 and D365 codes, variant attributes, dimensions and product hierarchy.
* [dim_product_mdt](dim_product_mdt.md) - One row = one MDT (modern trade saleout) product code with its link to the MAC5 product SK and marketing-group SK, plus placeholder rows for unmapped codes and a -1 unknown row.
* [dim_product_mkt](dim_product_mkt.md) - One row = one marketing classification (type, marketing group, sub-marketing, segment) per company, from the MDS marketing-name master.
* [dim_product_mkt_director](dim_product_mkt_director.md) - One row = one active MDS marketing-director assignment record, with company, marketing type and validity interval; several records can share a company and type.
* [dim_product_series](dim_product_series.md) - One row = one MDT product series (SeriesCode and SeriesName), from the MDS product-series master.
* [dim_project](dim_project.md) - One row = one customer project profile (project code) per company from the MAC5 quotation-book company/project profiles.
* [dim_pump_information](dim_pump_information.md) - One row = one distinct combination of company, product code (milstk), RegionID and FlagNewProductMKT seen in fact_transcation, with the pump segment resolved for it.
* [dim_quotation](dim_quotation.md) - One row = one MAC5 quotation (book quotation, identified by its running number) per company with date, project link, customer code, terms and a derived order-fulfilment status.
* [dim_rate_target](dim_rate_target.md) - One row = one target-share rule: the percent of a target (TargetID, optionally by product group and month) assigned to one employee in one department of a company, from the MDS target rate master.
* [dim_rebate](dim_rebate.md) - One row = one rebate or sales-KPI exclusion rule of a company: a code (rebate) of a given status type (customer, sales, product, dep, textsplit) with its sales and accounting exclusion flags, from the MDS KPI condition master.
* [dim_region](dim_region.md) - One row = one sales region or sub-region (RegionID, SubRegionID) of one company over one StartDate to EndDate validity interval, from the MDS region master.
* [dim_region_last](dim_region_last.md) - One row = one region or sub-region code (companyID, RegionID, SubRegionID) of a company, keeping only its latest validity interval from dim_region.
* [dim_region_manager](dim_region_manager.md) - One row = one region manager assignment for a region or sub-region of one company over one StartDate to EndDate interval, from the MDS region manager master.
* [dim_region_manager_last](dim_region_manager_last.md) - One row = one region or sub-region code (companyID, RegionID, SubRegionID) with its latest region manager interval from dim_region_manager.
* [dim_report](dim_report.md) - One row = one report-group mapping of a company: a ReportID tied to a RegionID and optionally a MarketingGroupID, with two display names, from the MDS report group master.
* [dim_sale_representative](dim_sale_representative.md) - One row = one sales-representative rule row: an employee in a department (with optional DepCode, CostChannelID, ProvinceID, CustomerFlag and order window) over a StartDate to EndDate interval from the MDS representative master, plus one catch-all row per employee from the MAC5 personnel ledger.
* [dim_sale_representative_last](dim_sale_representative_last.md) - One row = one sales-representative rule (latest interval per company, department, employee, DepCode, CostChannelID, ProvinceID and order window), collapsed to a single normal row per employee when one exists, plus one ledger row per employee with no department.
* [dim_sales_branch_mdt](dim_sales_branch_mdt.md) - One row = one MDT (modern-trade) retail branch identified by store chain (StoreCode) and branch number (BranchCode), with its region, section and zone keys, plus waiting rows for branches that appear in the saleout feeds but not yet in the master and a reserved -1 row.
* [dim_section](dim_section.md) - One row = one sales section (SectionID) of one company over one StartDate to EndDate validity interval, from the MDS section master.
* [dim_section_last](dim_section_last.md) - One row = one section code (companyID, SectionID) with its latest validity interval from dim_section, plus hierarchy keys up to manager, region and director.
* [dim_section_manager](dim_section_manager.md) - One row = one section manager assignment for one section of one company over one StartDate to EndDate interval, from the MDS section manager master.
* [dim_section_manager_last](dim_section_manager_last.md) - One row = one section code (companyID, SectionID) with its latest section manager interval from dim_section_manager.
* [dim_status_not_receive](dim_status_not_receive.md) - One row = one invoice status code (StatusID) of a company that counts as paid-without-receipt, with Thai and English names, from the MDS payment status master.
* [dim_stk_mkt](dim_stk_mkt.md) - One row = one MAC5 stock code of a company with its marketing group, sub group and segment, from the MDS product market group master, plus placeholder rows for stock codes MDS does not know yet.
* [dim_store](dim_store.md) - One row = one warehouse or branch store (StoreCode) of a company from the MAC5 stock-location master, plus a reserved -1 row for unknown stores.
* [dim_target_product_group](dim_target_product_group.md) - One row = one company-level sales target (Amt and Qty) for a year and month by marketing group, sub group, segment, channel target group and TargetID, from the MDS target by product group master.
* [dim_target_product_group_by_sale](dim_target_product_group_by_sale.md) - One row = one company-level product-group target (TargetProductGroupSK) allocated to one employee and department through a rate rule (RateTargetSK), with the allocated amount and quantity (CalAmt, CalQty) and the latest-snapshot org keys of that employee.
* [dim_target_product_group_by_sale_dayofwork](dim_target_product_group_by_sale_dayofwork.md) - One row = one allocated target row of dim_target_product_group_by_sale spread onto one calendar date (Amt_New and Qty_New for that date, zero on holidays), with the org-hierarchy SKs valid on that date.
* [dim_target_saleout_mdt](dim_target_saleout_mdt.md) - One row = the daily sales target (Amt, Qty) of one MDT branch for one marketing group, sub group and segment on one date, derived by splitting the monthly MDS target evenly over the days of the month, plus a reserved -1 row.
* [dim_target_series_mdt](dim_target_series_mdt.md) - One row = the daily sales target (Amt, Qty) of one MDT branch for one product series on one date, derived by splitting the monthly MDS series target evenly over the days of the month, plus a reserved -1 row.
* [dim_waterpac](dim_waterpac.md) - One row = one WaterPac (pump variant) code of a company with its name and brand, from the MDS WaterPac master.
* [dim_weight_score](dim_weight_score.md) - One row = one MDS weight-score lookup entry (score type with its weight) of a company over one StartDate to EndDate interval, from the MDS weight-score master.
* [dim_zone_mdt](dim_zone_mdt.md) - One row = one MDT sales zone (ZoneCode) with its name and validity dates, from the MDS MDT zone master, plus a reserved -1 NotZone row.
* [dim_zone_ta_mdt](dim_zone_ta_mdt.md) - One row = one zone manager (TA) assignment for an MDT zone over one StartDate to EndDate interval, from the MDS zone manager master, plus a reserved -1 row.
