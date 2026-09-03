# Dimension Inventory — all 61 files

> **LLM context**: SK = surrogate key column; NK = natural/business key. Most dims
> carry `CompanySK` FK from `dim_company`.
> Groups since 2026-07-20: (a) mds **full daily rebuild** (34 — SKs regenerate daily),
> (a2) mds MERGE legacy (2), (b) lake MERGE (10), (c) other full rebuild (12), (e) other (3).

## Group (a) — mds dims (36 total: 34 full rebuild + 2 MERGE legacy)

> Since 2026-07-20 every dim in this table is a **daily full rebuild**
> ([full-rebuild-pattern.md](full-rebuild-pattern.md)) — natural key drives the
> `ROW_NUMBER()` ordering — **except `dim_company` and `dim_aging_rang`** which keep
> the MERGE + tombstone pattern and stable SKs.

| File | SK | Natural key | mds source table |
|---|---|---|---|
| dim_company | CompanySK | CompanyID, CompanyCode | mds_data_company_master |
| dim_aging_rang | AgingRangSK | companyID, AgingDayMin, AgingDayMax | mds_data_aging_rang_master |
| dim_avg_collection_score | AvgCollectSK | companyID, AvgCollectiondayMin/Max, StartDate, EndDate | mds_data_custgrade_score_master |
| dim_bounce_cheque_score | BounceChequeSK | companyID, BouncedChequeMin/Max, StartDate, EndDate | mds_data_custgrade_cheque_score_master |
| dim_channel | ChannelSK | companyID, DepCode | mds_data_channel_master |
| dim_channel_cost | ChannelCostSK | companyID, ChannelCostID | mds_data_channel_cost_master |
| dim_channel_finance | ChannelFinanceSK | companyID, ChannelIDFinance | mds_data_channel_finance_master |
| dim_channel_sales | ChannelSaleSK | companyID, ChannelID | mds_data_channel_sales_master |
| dim_collection_status | CollectSK | CompanyID, CustomerID, Month, Year | mds_data_collection_status_master |
| dim_contact_score | ContactSK | companyID, ContactYearMin/Max, StartDate, EndDate | mds_data_custgrade_contact_score_master |
| dim_cost_group | CostGroupSK | companyID, ChannelCostID, GAccID, StartDate, EndDate | mds_data_standard_cost_by_product_group_master |
| dim_cost_stk | CostStkSK | companyID, ChannelCostID, GaccID, MilStk, StartDate, EndDate | mds_data_standard_cost_by_product_id_master |
| dim_department | DepartmentSK | companyID, DepartmentID, RegionID, SectionID, StartDate, EndDate | mds_data_sales_department_master |
| dim_director | DirectorSK | companyID, DirectorID, StartDate, EndDate | mds_data_sales_director_master |
| dim_doctype | *(SK commented out)* | companyID, Code — MERGE ON natural key | mds_data_document_type_master |
| dim_grade | GradeSK | companyID, Percentmin, Percentmax, StartDate, EndDate | mds_data_custgrade_master |
| dim_guarantee | GuaranteeSK | CompanyID, CustomerCode | mds_data_guarantee_document_master |
| dim_holiday | *(SK commented out)* | HolidayDate — MERGE ON natural key | mds_data_holiday_master |
| dim_payment | PaymentSK | companyID, CodeMemo | mds_data_payment_master |
| dim_payment_receive_score | PaymentReceiveSK | companyID, PaymentReceivedMin/Max, StartDate, EndDate | mds_data_custgrade_payment_receive_score_master |
| dim_product_master_fc | ProductMasterFcSK | companyID, ProductIDOldMac5 | mds_data_product_finance_master |
| dim_product_mkt | ProductMktSK | CompanyID, MarketingGroupID, SubMarketingID, SegmentID, TypeMarketingID | mds_data_product_marketing_name_master |
| dim_product_mkt_director | ProductMktDirectorSK | CompanyID, TypeMarketingID | mds_data_product_marketing_director_master |
| dim_rate_target | RateTargetSK | companyID, TargetID, TargetDepartmentID, ProductGroupID, Month, Year | mds_data_target_rate_master |
| dim_rebate | RebateSK | companyID, rebate, status | mds_data_sales_kpi_condition_master (uses `databuffet.MDS_DATASET`) |
| dim_region | RegionSK | companyID, RegionID, SubRegionID, StartDate, EndDate | mds_data_sales_region_master |
| dim_region_manager | RegionManagerSK | companyID, RegionID, SubRegionID, StartDate, EndDate | mds_data_sales_region_manager_master |
| dim_report | ReportSK | companyID, ReportID, MarketingGroupID, RegionID | mds_data_sales_report_group_master |
| dim_sale_representative | SaleRepSK | companyID, DepartmentID, EmployeeID, DepCode, CostChannelID, ProvinceID, StartDate, EndDate | mds_data_sales_representative_master + block 2: validated_mac5.per |
| dim_section | SectionSK | companyID, SectionID, StartDate, EndDate | mds_data_sales_section_master |
| dim_section_manager | SectionManagerSK | companyID, SectionID, StartDate, EndDate | mds_data_sales_section_manager_master |
| dim_status_not_receive | NotReceiveSK | CompanyID, StatusID | mds_data_payment_status_not_receive_master |
| dim_stk_mkt | StkMktSK | companyID, StkCode | mds_data_product_market_group_by_product_id_master + validated_mac5.stk (placeholders) |
| dim_target_product_group | TargetProductGroupSK | companyID, Year, Month, MarketingGroupID, SubMarketingID, SegmentID, ChannelTargetGroup, TargetID | mds_data_sales_target_by_product_group_master |
| dim_waterpac | WaterPacSK | CompanyID, WaterPacCode | mds_data_waterpac_master |
| dim_weight_score | WeightSK | CompanyID, Typeeng, Typethai, StartDate, EndDate | mds_data_custgrade_weight_score_master |

All depend on `dim_company` except `dim_company` (deps `[]`) and `dim_holiday` (no deps).

## Group (b) — MERGE from lake tables (10)

| File | SK | Sources | Deps |
|---|---|---|---|
| dim_customer | CustomerSK | validated_mac5 (match_customer, deb), validated_cis360 (customer_profile/status/type/nature_business), view_deb_address_data | dim_company |
| dim_invoice | InvoiceSK | curated_mih, ar_s/ap_s, curated_mil, per | dim_company, dim_order |
| ↳ 2026-09-03 | เพิ่ม `pernamet` (จาก `validated_mac5.per` join `mihPer` = `percode`) + `mihDesc` (จาก `curated_mih` ที่อ่านอยู่แล้ว) | ต้องสร้างตารางใหม่ก่อน (สคริปต์ `rebuild_dim_order_invoice.sql` — backup → `CREATE OR REPLACE` → verify, `InvoiceSK` คงเดิมทุกแถว) · `per` คีย์ `(company_id, percode)` unique 1,791 และ `curated_mih` คีย์ `(company_id, mihType, mihVnos)` → ไม่ fan out (1,657,238 เข้า = ออก) · เติมได้ `pernamet` 99.51% / `mihDesc` 99.30% | `view_dim_invoice` ทำ `inv.*` จึงได้ 2 คอลัมน์นี้อัตโนมัติ |
| dim_order | OrderSK | curated_mih, ar_s, curated_mil, per | dim_company |
| ↳ 2026-09-03 | เพิ่ม `pernamet` (ชื่อพนักงานขาย จาก `validated_mac5.per` join `mihPer` = `percode`) — ย้ายมาจาก `fact_order_store` เพื่อให้ซ่อน fact ได้ทั้งใบ | สร้างตารางใหม่ก่อน (สคริปต์ `rebuild_dim_order_invoice.sql` — backup → `CREATE OR REPLACE` → verify, `OrderSK` คงเดิมทุกแถว) · เติมได้ 1,369,665/1,374,663 = 99.64% | consumer: `fact_order_store` (Power BI ใช้ `dim_order[pernamet]` แทน) |
| ↳ 2026-09-01 | เพิ่ม 8 คอลัมน์ (ไม่แตะ logic/เงื่อนไข/SK): `mihDesc` `mihKeydate` `mihDelvdate` `mihClearum` `mihExtrasum` `mihPer` `mihBl` จาก `curated_mih` ที่อ่านอยู่แล้ว + `StatusColorBg` (`ar_scolb`) จาก `ar_s` ที่ join อยู่แล้ว | ต้อง `ALTER TABLE ... ADD COLUMN` บน BigQuery ก่อน (type `operations`, ตาราง pre-exist) · `view_dim_order` ทำ `SELECT ord.*` จึงได้ 8 คอลัมน์นี้ไปด้วยอัตโนมัติ · 49,719 แถวที่เก่ากว่า window 4 ปีจะเป็น NULL ถาวร | consumer: `fact_order_store`, `fact_invoice_store`, `fact_backlog_store` |
| dim_delivery | DeliverySK | curated_mil, ttrip/ttrip_document/tdelivery, deb, curated_mih | dim_company |
| dim_project | ProjectSK | validated_mac5.tbook_profilecomp | dim_company |
| dim_quotation | QuotationSK | curated_tbook_quotation, tbook_quodetail, curated_mih/mil | dim_company, dim_project |
| dim_product_master | ProductSK (MERGE ON ProductCode + CompanySK) | validated_mac5 stk/stg, validated_mastersku product/product_detail | dim_company, dim_product_mkt, dim_rebate, dim_stk_mkt |
| dim_customer_grade | CustomerGradeSK | chq, cql, mie, mir, deb, mih, curated_mih | dim_customer, dim_aging, dim_calendar, dim_status_not_receive + 5 score dims |
| dim_group_customer | GroupCustomerSK | dim_customer | dim_customer |
| dim_group_customer_grade | GroupCustomerGradeSK | deb, chq, cql, mie, mir, mih, curated_mih | dim_calendar, dim_customer, dim_group_customer + score dims |

## Group (c) — full rebuild `type: "table"` (12)

| File | SK | Notes |
|---|---|---|
| dim_change_district | *(none; CompanySK FK)* | Plain SELECT from mds_data_change_section_master, `WHERE is_active = true` |
| dim_department_last / dim_director_last / dim_region_last / dim_region_manager_last / dim_section_last / dim_section_manager_last / dim_sale_representative_last | `<X>SK` via ROW_NUMBER | Latest SCD row per entity; NULL FK SKs backfilled by `update_sk_sale_rep_group` |
| dim_target_product_group_by_sale | TargetBySaleSK | Multi-CTE join of target/rate/report/product-mkt dims + `_last` family |
| dim_target_product_group_by_sale_dayofwork | TargetBySaleDayofworkSK | joins dim_calendar (working-day expansion); daily full rebuild, self-heals |
| dim_store | StoreSK · **NK = company_id + stoCode** | คลัง/สาขาจาก `validated_mac5.sto` (601 แถว ag01) · `StoreGroup` (`stogroup`) เป็นชั้นที่ใช้สไลซ์ — KK ขอนแก่น, LP ลำพูน, HY หาดใหญ่, UB อุบลราชธานี, PK ภูเก็ต · `UNION ALL` แถว Unknown `StoreSK = -1` รับรหัสที่ไม่มีใน `sto` (pattern เดียวกับ `dim_stk_mkt`) · consumer: `fact_order_store` / `fact_invoice_store` / `fact_backlog_store` ต่อด้วย `milSto` / `cpsSto` (เพิ่ม 2026-09-01) |
| dim_pump_information | PumpSK · **NK = CompanySK + milstk + RegionID + FlagNewProductMKT** | **อ่านจาก `fact_transcation`** (ไม่ใช่ mds) → `PumpSegment`; PS1 + FlagNewProductMKT → `dim_product_mkt.Segment`, นอกนั้น → `view_dim_product_master.PumpSegment` (เพิ่ม 2026-08-26) · consumer: `view_fact_transcation` join กลับด้วย NK 4 ตัว (ไม่ persist PumpSK) · **`CompanySK` จำเป็น — `milstk` unique แค่ภายในบริษัท** |

## Group (e) — other operations (3)

| File | What it does |
|---|---|
| dim_calendar | Date spine via `GENERATE_DATE_ARRAY` (next-year start → current+2 Dec-31), joins dim_holiday, weekend/holiday/long-weekend flags; TEMP → DELETE-by-Date → INSERT. **Tag `dimension_yearly`** |
| dim_aging | ~500-line AR aging engine over chq/cql/mir/mie/ar_s/cfs + curated mih/mil + dim_aging_history + view_dim_aging + fact_mir_vs + onetime.cfsinvclose2024 |
| update_sk_sale_rep_group | UPDATE-only: backfills FK SKs (RegionManagerSK, DirectorSK, SectionSK, ...) across the 7 `_last` tables via temp_data |
