# Dimension Inventory

> **LLM context**: SK = surrogate key; NK = natural/business key. This inventory owns
> the conversion scope. The common synchronization contract is in
> [merge-sk-pattern.md](merge-sk-pattern.md); table-specific details are in each OKF card.
>
> | Pattern | Behavior |
> |---|---|
> | Stable-SK three-clause sync | Complete active-source snapshot; match/update, insert, and delete absent rows; company retains its legacy identity lookup |
> | Distinct behavior | `dim_order`, `dim_customer_report_info` |
> | Unchanged | Existing actions, including the held dimensions below |
>
> Held conversions: `dim_aging`, `dim_product_master`, `dim_stk_mkt`, and
> `dim_target_saleout_mdt` retain their original key-generation behavior and OKF cards.
> The only SQLX exception is `dim_target_saleout_mdt`'s ProductMkt lookup ordering,
> which uses the business-field order from before stable allocation in `dim_product_mkt`.
> `dim_target_product_group_by_sale` and `dim_target_product_group_by_sale_dayofwork`
> are also held; their rebuild and key contracts are owned by their OKF cards below.
>
> Key selection follows the [grain-preservation contract](merge-sk-pattern.md#key-and-synchronization-rules).
> Exact table grains and keys are owned by their OKF cards.

## Group (a) — MDS-sourced dimensions (44)

> Except for the held conversions listed above, dimensions with SKs in this group use
> the common stable-SK sync, including
> `dim_aging_rang`; `dim_company` retains its legacy MdsId-first identity lookup with
> a CompanyID/CompanyCode fallback and deletes rows absent from the complete active source.
> The retained row grain defines other SK identities. `dim_doctype`
> and `dim_holiday` have no SK. `dim_customer_report_info` remains in the distinct-behavior
> section because it retains rows absent from its source.

| File | SK | Natural key | mds source table |
|---|---|---|---|
| dim_company | CompanySK | Legacy MdsId-first lookup; CompanyID, CompanyCode fallback | mds_data_company_master |
| dim_aging_rang | AgingRangSK | companyID, AgingDayMin, AgingDayMax | mds_data_aging_rang_master |
| dim_avg_collection_score | AvgCollectSK | companyID, AvgCollectiondayMin, AvgCollectiondayMax, StartDate, EndDate | mds_data_custgrade_score_master |
| dim_bounce_cheque_score | BounceChequeSK | companyID, BouncedChequeMin, BouncedChequeMax, StartDate, EndDate | mds_data_custgrade_cheque_score_master |
| dim_channel | ChannelSK | companyID, DepCode | mds_data_channel_master |
| dim_channel_cost | ChannelCostSK | companyID, ChannelCostID | mds_data_channel_cost_master |
| dim_channel_finance | ChannelFinanceSK | companyID, ChannelIDFinance | mds_data_channel_finance_master |
| dim_channel_sales | ChannelSaleSK | companyID, ChannelID | mds_data_channel_sales_master |
| dim_collection_status | CollectSK | CompanyID, CustomerID, Month, Year | mds_data_collection_status_master |
| dim_contact_score | ContactSK | companyID, ContactYearMin, ContactYearMax, StartDate, EndDate | mds_data_custgrade_contact_score_master |
| dim_cost_group | CostGroupSK | companyID, GAccID, ChannelCostID, StartDate, EndDate | mds_data_standard_cost_by_product_group_master |
| dim_cost_stk | CostStkSK | companyID, MilStk, GaccID, ChannelCostID, StartDate, EndDate | mds_data_standard_cost_by_product_id_master |
| dim_department | DepartmentSK | companyID, RegionID, SectionID, DepartmentID, StartDate, EndDate | mds_data_sales_department_master |
| dim_director | DirectorSK | companyID, DirectorID, StartDate, EndDate | mds_data_sales_director_master |
| dim_doctype | *(no SK)* | companyID, Code — active-source SELECT | mds_data_document_type_master |
| dim_grade | GradeSK | companyID, Percentmin, Percentmax, StartDate, EndDate | mds_data_custgrade_master |
| dim_guarantee | GuaranteeSK | CompanyID, CustomerCode, BankName | mds_data_guarantee_document_master |
| dim_holiday | *(no SK)* | HolidayDate — active-source SELECT | mds_data_holiday_master |
| dim_payment | PaymentSK | companyID, CodeMemo | mds_data_payment_master |
| dim_payment_receive_score | PaymentReceiveSK | companyID, PaymentReceivedMin, PaymentReceivedMax, StartDate, EndDate | mds_data_custgrade_payment_receive_score_master |
| dim_product_master_fc | ProductMasterFcSK | companyID, Barcode | mds_data_product_finance_master |
| dim_product_mkt | ProductMktSK | CompanyID, TypeMarketingID, MarketingGroupID, SubMarketingID, SegmentID | mds_data_product_marketing_name_master |
| dim_product_mkt_director | ProductMktDirectorSK | CompanyID, TypeMarketingID, StartDate, EndDate | mds_data_product_marketing_director_master |
| dim_rate_target | RateTargetSK | companyID, Year, Month, StartDate, EndDate, ProductGroupID, TargetID, TargetDepartmentID, DepartmentID, EmployeeID | mds_data_target_rate_master |
| dim_rebate | RebateSK | companyID, rebate, status | mds_data_sales_kpi_condition_master (uses `databuffet.MDS_DATASET`) |
| dim_region | RegionSK | companyID, RegionID, SubRegionID, StartDate, EndDate | mds_data_sales_region_master |
| dim_region_manager | RegionManagerSK | companyID, RegionID, SubRegionID, StartDate, EndDate | mds_data_sales_region_manager_master |
| dim_report | ReportSK | companyID, ReportID, RegionID, MarketingGroupID | mds_data_sales_report_group_master |
| dim_sale_representative | SaleRepSK | companyID, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, StartDate, EndDate, OrderStartDate, OrderEndDate, CustomerFlag | mds_data_sales_representative_master + block 2: validated_mac5.per |
| dim_section | SectionSK | companyID, SectionID, StartDate, EndDate | mds_data_sales_section_master |
| dim_section_manager | SectionManagerSK | companyID, SectionID, StartDate, EndDate | mds_data_sales_section_manager_master |
| dim_status_not_receive | NotReceiveSK | CompanyID, StatusID | mds_data_payment_status_not_receive_master |
| dim_stk_mkt | StkMktSK (regenerated) | Held; see [table grain](../../okf/dimension/dim_stk_mkt.md#grain-and-key) | mds_data_product_market_group_by_product_id_master + validated_mac5.stk (placeholders) |
| dim_target_product_group | TargetProductGroupSK | companyID, Year, Month, MarketingGroupID, SubMarketingID, SegmentID, ChannelTargetGroup, TargetID | mds_data_sales_target_by_product_group_master |
| dim_waterpac | WaterPacSK | CompanyID, WaterPacCode | mds_data_waterpac_master |
| dim_customer_segment | CustomerSegmentSK | CompanyID, Segment3 | mds_data_customer_segment_master · [Member and fallback rules](../view/view-layer.md#customer-report-info--customer-segment-2026-10-01) |
| dim_weight_score | WeightSK | CompanyID, Typeeng, Typethai, StartDate, EndDate | mds_data_custgrade_weight_score_master |
| dim_zone_mdt | ZoneMdtSK | ZoneCode | mds_data_mdt_sales_zone_master |
| dim_zone_ta_mdt | ZoneTaMdtSK | ZoneCode, EmployeeID, StartDate, EndDate | mds_data_mdt_sales_zone_ta_master |
| dim_sales_branch_mdt | BranchMdtSK | StoreCode, BranchCode, StartDate, EndDate | mds_data_mdt_sales_branch_master |
| dim_product_mdt | ProductMdtSK | ProductCode | mds_data_mdt_product_master |
| dim_pc | PcSK | EmployeeID, BranchCodeMdt, MarketingGroupID, StartDate, EndDate | mds_data_mdt_sales_pc_master |
| dim_target_saleout_mdt | TargetSaleoutMdtSK (regenerated; reserved -1) | Held; see [table grain](../../okf/dimension/dim_target_saleout_mdt.md#grain-and-key) | mds_data_mdt_sales_target_by_product_master |
| dim_target_series_mdt | TargetSeriesMdtSK | TargetDate, BranchCodeMdt, SeriesCode | mds_data_mdt_sales_target_by_series |

Build dependencies: follow the complete source and dependency order recorded for each
action; see [stable dimension sync](merge-sk-pattern.md) and the project DAG.
## Group (b) — MERGE from lake tables (10)

| File | SK | Sources | Deps |
|---|---|---|---|
| dim_customer | CustomerSK | validated_mac5 (match_customer, deb), validated_cis360 (customer_profile/status/type/nature_business), view_deb_address_data | dim_company |
| dim_invoice | InvoiceSK | curated_mih, ar_s/ap_s, curated_mil, per | dim_company, dim_order |
| ↳ 2026-09-03 | เพิ่ม `pernamet` (จาก `validated_mac5.per` join `mihPer` = `percode`) + `mihDesc` (จาก `curated_mih` ที่อ่านอยู่แล้ว) | ต้องสร้างตารางใหม่ก่อน (สคริปต์ `rebuild_dim_order_invoice.sql` — backup → `CREATE OR REPLACE` → verify, `InvoiceSK` คงเดิมทุกแถว) · `per` คีย์ `(company_id, percode)` unique 1,791 และ `curated_mih` คีย์ `(company_id, mihType, mihVnos)` → ไม่ fan out (1,657,238 เข้า = ออก) · เติมได้ `pernamet` 99.51% / `mihDesc` 99.30% | `view_dim_invoice` ทำ `inv.*` จึงได้ 2 คอลัมน์นี้อัตโนมัติ |
| dim_order | OrderSK | curated_mih, ar_s, curated_mil, per | dim_company · join PS↔IS ด้วย `lower(milstk)` สองฝั่ง (2026-09-03) — จับได้เพิ่ม 412 คีย์ ดู `known-issues.md` |
| ↳ 2026-09-24 | `OrderStatus` คำนวณจาก mil ครบ window 4 ปี (ถอด `asatdate >= current_date - 1`) + เขียนใน `UPDATE SET` ทุกคืน (เดิมเขียนแค่ INSERT) | ไม่ต้อง ALTER/backfill — รันคืนแรกซ่อมเอง: `On Order` ค้าง 56,755 ใบ · `NULL` 377,982 ใบ · +~0.79 GB/วัน · เทียบยอดเงินด้วย `ROUND(milSum, 2)` กัน float สลับสถานะ (4,087 ใบ) | ดู `known-issues.md` 2026-09-24 |
| ↳ 2026-09-03 | เพิ่ม `pernamet` (ชื่อพนักงานขาย จาก `validated_mac5.per` join `mihPer` = `percode`) — ย้ายมาจาก `fact_order_store` เพื่อให้ซ่อน fact ได้ทั้งใบ | สร้างตารางใหม่ก่อน (สคริปต์ `rebuild_dim_order_invoice.sql` — backup → `CREATE OR REPLACE` → verify, `OrderSK` คงเดิมทุกแถว) · เติมได้ 1,369,665/1,374,663 = 99.64% | consumer: `fact_order_store` (Power BI ใช้ `dim_order[pernamet]` แทน) |
| ↳ 2026-09-01 | เพิ่ม 8 คอลัมน์ (ไม่แตะ logic/เงื่อนไข/SK): `mihDesc` `mihKeydate` `mihDelvdate` `mihClearum` `mihExtrasum` `mihPer` `mihBl` จาก `curated_mih` ที่อ่านอยู่แล้ว + `StatusColorBg` (`ar_scolb`) จาก `ar_s` ที่ join อยู่แล้ว | ต้อง `ALTER TABLE ... ADD COLUMN` บน BigQuery ก่อน (type `operations`, ตาราง pre-exist) · `view_dim_order` ทำ `SELECT ord.*` จึงได้ 8 คอลัมน์นี้ไปด้วยอัตโนมัติ · 49,719 แถวที่เก่ากว่า window 4 ปีจะเป็น NULL ถาวร | consumer: `fact_order_store`, `fact_invoice_store`, `fact_backlog_store` |
| dim_delivery | DeliverySK | curated_mil, ttrip/ttrip_document/tdelivery, deb, curated_mih | dim_company |
| dim_project | ProjectSK | validated_mac5.tbook_profilecomp | dim_company |
| dim_quotation | QuotationSK | curated_tbook_quotation, tbook_quodetail, curated_mih/mil | dim_company, dim_project |
| dim_product_master | ProductSK · NK = CompanySK + ProductCode + Barcode | Held; original no-delete MERGE. See [table contract](../../okf/dimension/dim_product_master.md#how-it-is-built). Source: validated_mac5 stk/stg and validated_mastersku product/product_detail · includes 8 dummy ag01 codes (7 `*OTHERS` plus `WAITING999`) | dim_company, dim_product_mkt, dim_rebate, dim_stk_mkt |
| dim_customer_grade | CustomerGradeSK | chq, cql, mie, mir, deb, mih, curated_mih | dim_customer, dim_aging, dim_calendar, dim_status_not_receive + 5 score dims |
| dim_group_customer | GroupCustomerSK | dim_customer | dim_customer |
| dim_group_customer_grade | GroupCustomerGradeSK | deb, chq, cql, mie, mir, mih, curated_mih | dim_calendar, dim_customer, dim_group_customer + score dims |

## Group (b2) — mds + invoice MERGE (1)

| File | SK | Natural key | Sources |
|---|---|---|---|
| dim_customer_report_info | CustomerReportInfoSK (MERGE ON `CompanyID` + `CustomerReportKey`, ใหม่ = `max_sk + ROW_NUMBER()`) | CompanyID, CustomerReportKey (ชื่อร้านตัด whitespace ทั้งหมด — เก็บเป็นคอลัมน์ตั้งแต่ 2026-10-28) | mds_data_customer_report_master + ทุกชื่อใน view_dim_invoice · [Customer Report Info: sources, grain, segment/TA rules and relationships](../view/view-layer.md#customer-report-info--customer-segment-2026-10-01) |

`type: "operations"` (ตารางต้องมีอยู่แล้ว) · ชื่อเดิมคง SK และอัปเดตทุกคอลัมน์อื่นทุกคืน · ชื่อที่หายจาก source (MDS inactive
และไม่มี invoice) **ไม่ลบ** · แถวสงวน -1 อยู่นอก MERGE (`INSERT ... WHERE NOT EXISTS`) · **ห้าม full rebuild** — SK จะเปลี่ยน
([known-issues 2026-10-28](../../operations/known-issues.md))

## Group (c) — Other dimension outputs (12) + `dim_change_district`

> Except for the held daily rebuilds listed below, SK dimensions in this group use the common stable-SK sync. Their existing latest-row,
> target, store, pump, and union/fallback source logic remains part of the complete source.

| File | SK | Notes |
|---|---|---|
| dim_change_district | *(none; CompanySK FK)* | **อ่าน mds** (นับใน (a)): Plain SELECT from mds_data_change_section_master, `WHERE is_active = true` |
| dim_product_series | SeriesSK · NK = SeriesCode | Active rows from `mds_data_product_series_master`; stable SK sync retains SeriesCode as the key · consumer: `dim_target_series_mdt`, view `onetime.Product_Attribute` · see [special-cases](special-cases.md) |
| dim_department_last / dim_director_last / dim_region_last / dim_region_manager_last / dim_section_last / dim_section_manager_last / dim_sale_representative_last | established `<X>SK` | Stable SK sync on the retained latest-period natural key, including validity dates; NULL FK SKs are backfilled by `update_sk_sale_rep_group` |
| dim_target_product_group_by_sale | TargetBySaleSK | Held because the stable-SK existing-row lookup exceeded BigQuery's on-demand CPU limit; see the [table contract](../../okf/dimension/dim_target_product_group_by_sale.md#grain-and-key) |
| dim_target_product_group_by_sale_dayofwork | TargetBySaleDayofworkSK | Held; original daily full-rebuild behavior remains |
| dim_store | StoreSK · **NK = companyID + StoreCode** | คลัง/สาขาจาก `validated_mac5.sto` (601 แถว ag01) · `StoreGroup` (`stogroup`) เป็นชั้นที่ใช้สไลซ์ — KK ขอนแก่น, LP ลำพูน, HY หาดใหญ่, UB อุบลราชธานี, PK ภูเก็ต · `ReportStore` (เพิ่ม 2026-09-03) = `stogroup` ที่ไม่อยู่ใน `kk/pk/lp/ub/hy` ยุบเป็น `'KTB'` ถังเดียว ไว้สไลซ์รายงาน · `UNION ALL` แถว Unknown `StoreSK = -1` (`StoreNameE = 'Unknown'`, **`ReportStore = 'KTB'`** ตั้งแต่ 2026-09-25 — เดิม `'Unknown'`) รับรหัสที่ไม่มีใน `sto` (pattern เดียวกับ `dim_stk_mkt`) · consumer: `fact_order_store` / `fact_invoice_store` / `fact_backlog_store` ต่อด้วย `milSto` / `cpsSto` (เพิ่ม 2026-09-01) |
| dim_pump_information | PumpSK · **NK = CompanyID + milstk + RegionID + FlagNewProductMKT + PumpSegment** | **อ่านจาก `fact_transcation`** (ไม่ใช่ mds) → `PumpSegment`; PS1 + FlagNewProductMKT → `dim_product_mkt.Segment`, นอกนั้น → `view_dim_product_master.PumpSegment` (เพิ่ม 2026-08-26) · consumer: `view_fact_transcation` join กลับด้วย NK 4 ตัว (ไม่ persist PumpSK) · **`CompanySK` จำเป็น — `milstk` unique แค่ภายในบริษัท** |

## Group (d) — D-ERP price dimensions (3)

| File | SK | Natural key | Source |
|---|---|---|---|
| dim_price | PriceSK | NdSdPriceID | validated_derp.crm_nd_sd_price |
| dim_price_tier | PriceTierSK | NdSdPriceID, TierCode | validated_derp.crm_nd_sd_price; depends on dim_price |
| dim_price_channel | PriceChannelSK | MasterSalesChannelID | validated_derp.sales_channel_master_sales_channel; depends on dim_company |

These dimensions use the common [stable-SK sync](merge-sk-pattern.md). Table-specific mapping and hierarchy contracts are owned by the [dim_price](../../okf/dimension/dim_price.md), [dim_price_tier](../../okf/dimension/dim_price_tier.md) and [dim_price_channel](../../okf/dimension/dim_price_channel.md) cards.

## Group (e) — Other operations and distinct dimension behavior

| File | What it does |
|---|---|
| dim_calendar | Date spine via `GENERATE_DATE_ARRAY` (next-year start → current+2 Dec-31), joins dim_holiday, weekend/holiday/long-weekend flags; TEMP → DELETE-by-Date → INSERT. **Tag `dimension_yearly`** · ธงรายวัน `LatestDateFilter` อยู่ที่ `dimension_view.view_dim_calendar` (ไม่ได้อยู่ในตารางนี้) |
| dim_aging | AR aging engine over chq/cql/mir/mie/ar_s/cfs + curated mih/mil + dim_aging_history + view_dim_aging + fact_mir_vs + onetime.cfsinvclose2024; held; original daily rebuild and history writer remain. See [table contract](../../okf/dimension/dim_aging.md#how-it-is-built) |
| update_sk_sale_rep_group | UPDATE-only: backfills FK SKs (RegionManagerSK, DirectorSK, SectionSK, ...) across the 7 `_last` tables via temp_data |
