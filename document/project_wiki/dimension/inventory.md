# Dimension Inventory

> **LLM context**: SK = surrogate key column; NK = natural/business key · dim ส่วนใหญ่
> ถือ FK `CompanySK` จาก `dim_company` · ตรวจกับโค้ดจริง 2026-10-18 (71 ไฟล์) ·
> ยอดไฟล์ล่าสุดดูที่ [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview)
>
> | กลุ่ม | จำนวน | ลักษณะ |
> |---|---:|---|
> | (a) mds **full daily rebuild** | **43** | SK ออกใหม่ทุกวัน — ห้ามเก็บข้ามวัน (42 ในตาราง (a) + `dim_change_district` ที่อยู่ในตาราง (c)) |
> | (a2) mds MERGE legacy | 2 | `dim_company`, `dim_aging_rang` — SK เสถียรตลอดกาล |
> | (b) lake MERGE (validated/curated) | 10 | SK เสถียร ไม่มี mds tombstone |
> | (b2) mds + invoice MERGE | 1 | `dim_customer_report_info` (2026-10-28) — SK เสถียร ไม่มี delete ห้าม full rebuild |
> | (c) full rebuild อื่น | 12 | `_last` snapshots, target, store, pump, `dim_product_series` (hard-code) |
> | (e) operations อื่น | 3 | `dim_calendar`, `dim_aging`, `update_sk_sale_rep_group` |
>
> วิธีนับที่เชื่อถือได้: จับ `mds_data_\w+` **ทั้งไฟล์** ไม่ใช่แค่ `name: "..."` — dim ชุด
> MDT อ้าง mds ผ่าน const ใน `js {}` (`${databuffet.MDS_DATASET}.mds_data_...`)
> ถ้าจับแค่ `name:` จะนับขาดไป 7 ตัว · `dim_product_series` มีคำว่า `mds_dataset` แค่ใน comment
> (ไม่ได้อ่าน mds) อย่านับเป็น mds dim

## Group (a) — mds dims (44 แถวในตาราง: 42 full rebuild + 2 MERGE legacy)

> ตั้งแต่ 2026-07-20 ทุก dim ในตารางนี้เป็น **full rebuild รายวัน**
> ([full-rebuild-pattern.md](full-rebuild-pattern.md)) — natural key เป็นตัวกำหนดลำดับ
> `ROW_NUMBER()` — **ยกเว้น `dim_company` กับ `dim_aging_rang`** ที่ยังใช้ MERGE +
> tombstone และ SK เสถียร · `dim_customer_report_info` อ่าน mds ด้วยแต่ย้ายไป [Group (b2)](#group-b2--mds--invoice-merge-1) แล้ว (2026-10-28)

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
| dim_customer_segment | CustomerSegmentSK | CompanyID, Segment3 (MDS rows) | mds_data_customer_segment_master · [Member and fallback rules](../view/view-layer.md#customer-report-info--customer-segment-2026-10-01) |
| dim_weight_score | WeightSK | CompanyID, Typeeng, Typethai, StartDate, EndDate | mds_data_custgrade_weight_score_master |
| dim_zone_mdt | ZoneMdtSK | zone_id | mds_data_mdt_sales_zone_master |
| dim_zone_ta_mdt | ZoneTaMdtSK | zone_id, ZoneTAEmployeeID (+ แถว Unknown) · deps `dim_zone_mdt` · แทน `dim_zone_manager_mdt` ที่ถูกลบ (`b198e24`; ตารางเก่ายังค้างใน BigQuery) | mds_data_mdt_sales_zone_ta_master |
| dim_sales_branch_mdt | BranchMdtSK | store_code, branch_code · deps `dim_zone_mdt`, `dim_zone_ta_mdt`, `dim_region_last`, `dim_section_last` | mds_data_mdt_sales_branch_master |
| dim_product_mdt | ProductMdtSK | product_mdt_code (CAST INT64) | mds_data_mdt_product_master |
| dim_pc | PcSK | รหัส PC ประจำสาขา | mds_data_mdt_sales_pc_master |
| dim_target_saleout_mdt | TargetSaleoutMdtSK | เป้ารายเดือน กระจายเป็นรายวัน · partition `TargetDate` | mds_data_mdt_sales_target_by_product_master |
| dim_target_series_mdt | TargetSeriesMdtSK | TargetDate, BranchCodeMdt, SeriesCode · เป้ารายเดือนตาม series กระจายเป็นรายวัน · partition `TargetDate` · deps `dim_sales_branch_mdt`, `dim_product_series` (รหัสที่ไม่มีลง `OTHERS`) | mds_data_mdt_sales_target_by_series |

Build dependency rules: [full-rebuild properties](full-rebuild-pattern.md#properties).

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
| dim_product_master | ProductSK (MERGE ON ProductCode + CompanySK) | validated_mac5 stk/stg, validated_mastersku product/product_detail · **+ 7 dummy ag01 `*OTHERS`** (สินค้าที่ไม่มีรหัส MDT เช่น `OTHERS099OTHERS`) ต่อท้าย `stk` ใน CTE — โครงคอลัมน์จาก `stk` เอง (`REPLACE` 3 คอลัมน์ ที่เหลือ NULL) เพิ่มรหัสใหม่ = เติมใน `UNNEST([...])` (2026-10-12) | dim_company, dim_product_mkt, dim_rebate, dim_stk_mkt |
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

## Group (c) — full rebuild `type: "table"` ที่ไม่ได้อ่าน mds (12) + `dim_change_district`

| File | SK | Notes |
|---|---|---|
| dim_change_district | *(none; CompanySK FK)* | **อ่าน mds** (นับใน (a)): Plain SELECT from mds_data_change_section_master, `WHERE is_active = true` |
| dim_product_series | SeriesSK · NK = SeriesCode | **hard-code 2 แถว** ด้วย `UNNEST` (`100001` TITAN, `999999` OTHERS) จากไฟล์ Excel ของ BI (2026-10-02) — รอย้ายไป `mds_dataset` เมื่อ BI โหลดเข้า · ไม่มีแถว `-1` · consumer: `dim_target_series_mdt`, view `onetime.Product_Attribute` · ดู [special-cases](special-cases.md) |
| dim_department_last / dim_director_last / dim_region_last / dim_region_manager_last / dim_section_last / dim_section_manager_last / dim_sale_representative_last | `<X>SK` via ROW_NUMBER | Latest SCD row per entity; NULL FK SKs backfilled by `update_sk_sale_rep_group` |
| dim_target_product_group_by_sale | TargetBySaleSK | Multi-CTE join of target/rate/report/product-mkt dims + `_last` family |
| dim_target_product_group_by_sale_dayofwork | TargetBySaleDayofworkSK | joins dim_calendar (working-day expansion); daily full rebuild, self-heals |
| dim_store | StoreSK · **NK = company_id + stoCode** | คลัง/สาขาจาก `validated_mac5.sto` (601 แถว ag01) · `StoreGroup` (`stogroup`) เป็นชั้นที่ใช้สไลซ์ — KK ขอนแก่น, LP ลำพูน, HY หาดใหญ่, UB อุบลราชธานี, PK ภูเก็ต · `ReportStore` (เพิ่ม 2026-09-03) = `stogroup` ที่ไม่อยู่ใน `kk/pk/lp/ub/hy` ยุบเป็น `'KTB'` ถังเดียว ไว้สไลซ์รายงาน · `UNION ALL` แถว Unknown `StoreSK = -1` (`StoreNameE = 'Unknown'`, **`ReportStore = 'KTB'`** ตั้งแต่ 2026-09-25 — เดิม `'Unknown'`) รับรหัสที่ไม่มีใน `sto` (pattern เดียวกับ `dim_stk_mkt`) · consumer: `fact_order_store` / `fact_invoice_store` / `fact_backlog_store` ต่อด้วย `milSto` / `cpsSto` (เพิ่ม 2026-09-01) |
| dim_pump_information | PumpSK · **NK = CompanySK + milstk + RegionID + FlagNewProductMKT** | **อ่านจาก `fact_transcation`** (ไม่ใช่ mds) → `PumpSegment`; PS1 + FlagNewProductMKT → `dim_product_mkt.Segment`, นอกนั้น → `view_dim_product_master.PumpSegment` (เพิ่ม 2026-08-26) · consumer: `view_fact_transcation` join กลับด้วย NK 4 ตัว (ไม่ persist PumpSK) · **`CompanySK` จำเป็น — `milstk` unique แค่ภายในบริษัท** |

## Group (e) — other operations (3)

| File | What it does |
|---|---|
| dim_calendar | Date spine via `GENERATE_DATE_ARRAY` (next-year start → current+2 Dec-31), joins dim_holiday, weekend/holiday/long-weekend flags; TEMP → DELETE-by-Date → INSERT. **Tag `dimension_yearly`** · ธงรายวัน `LatestDateFilter` อยู่ที่ `dimension_view.view_dim_calendar` (ไม่ได้อยู่ในตารางนี้) |
| dim_aging | ~500-line AR aging engine over chq/cql/mir/mie/ar_s/cfs + curated mih/mil + dim_aging_history + view_dim_aging + fact_mir_vs + onetime.cfsinvclose2024 |
| update_sk_sale_rep_group | UPDATE-only: backfills FK SKs (RegionManagerSK, DirectorSK, SectionSK, ...) across the 7 `_last` tables via temp_data |
