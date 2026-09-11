# Dimension Inventory — all 67 files

> **LLM context**: SK = surrogate key column; NK = natural/business key. Most dims
> carry `CompanySK` FK from `dim_company`.
> Groups since 2026-07-20: (a) mds **full daily rebuild** (34 — SKs regenerate daily),
> (a2) mds MERGE legacy (2), (b) lake MERGE (10), (c) other full rebuild (12), (e) other (3).

## Group (a) — mds dims (36 total: 34 full rebuild + 2 MERGE legacy)

> Since 2026-07-20 every dim in this table is a **daily full rebuild**
> ([full-rebuild-pattern.md](full-rebuild-pattern.md)) — natural key drives the
> `ROW_NUMBER()` ordering — **except `dim_company` and `dim_aging_rang`** which keep
> the MERGE + tombstone pattern and stable SKs.
>
> **นับแล้ว 2026-09-11**: ไฟล์จริงใน `definitions/dimension/` = 67 · ตารางในหน้านี้
> ครอบ 60 ไฟล์ · 7 ไฟล์ตระกูล `_last` (`dim_director_last`, `dim_region_last`,
> `dim_region_manager_last`, `dim_sale_representative_last`, `dim_section_last`,
> `dim_section_manager_last`) อยู่ใน [special-cases.md](special-cases.md) แทน

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
| dim_order | OrderSK | curated_mih, ar_s, curated_mil, per | dim_company · join PS↔IS ด้วย `lower(milstk)` สองฝั่ง (2026-09-03) — จับได้เพิ่ม 412 คีย์ ดู `known-issues.md` |
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
| dim_store | StoreSK · **NK = company_id + stoCode** | คลัง/สาขาจาก `validated_mac5.sto` (601 แถว ag01) · `StoreGroup` (`stogroup`) เป็นชั้นที่ใช้สไลซ์ — KK ขอนแก่น, LP ลำพูน, HY หาดใหญ่, UB อุบลราชธานี, PK ภูเก็ต · `ReportStore` (เพิ่ม 2026-09-03) = `stogroup` ที่ไม่อยู่ใน `kk/pk/lp/ub/hy` ยุบเป็น `'KTB'` ถังเดียว ไว้สไลซ์รายงาน · `UNION ALL` แถว Unknown `StoreSK = -1` (`ReportStore = 'Unknown'`) รับรหัสที่ไม่มีใน `sto` (pattern เดียวกับ `dim_stk_mkt`) · consumer: `fact_order_store` / `fact_invoice_store` / `fact_backlog_store` ต่อด้วย `milSto` / `cpsSto` (เพิ่ม 2026-09-01) |
| dim_pump_information | PumpSK · **NK = CompanySK + milstk + RegionID + FlagNewProductMKT** | **อ่านจาก `fact_transcation`** (ไม่ใช่ mds) → `PumpSegment`; PS1 + FlagNewProductMKT → `dim_product_mkt.Segment`, นอกนั้น → `view_dim_product_master.PumpSegment` (เพิ่ม 2026-08-26) · consumer: `view_fact_transcation` join กลับด้วย NK 4 ตัว (ไม่ persist PumpSK) · **`CompanySK` จำเป็น — `milstk` unique แค่ภายในบริษัท** |

| dim_sales_branch_mdt | BranchMdtSK · **NK = StoreCode + BranchCode** | สาขาของ 6 ห้าง 494 แถว + `-1` · ต้นทาง `mds_dataset.mds_data_sales_branch_master` · ⚠️ **เพิ่ม `RegionSK` 2026-09-11** — เดิม `region_id` เก็บเป็นรหัสเปล่า ๆ ไม่มี SK · ดึงจาก `dim_region` (`companyID = 'ag01'`) พร้อม `RegionName`/`SubRegionID` · `dim_region` แบ่งตามช่วงเวลา **รหัสละ 2 แถว** (HP: SK 21 = 2022-01-01→2025-12-31 · SK 22 = 2026-01-01→2066-12-31) ต้องกรองช่วงที่ครอบวันนี้ ไม่งั้นสาขาบวม 2 เท่า · ตารางนี้ rebuild ทุกคืน `RegionSK` จึงขยับเองเมื่อข้ามช่วง · **ติดครบ 6 ห้าง ไม่มีสาขาไหนเป็น `-1`** (BT 4 BOONTHAVORN · DH 6 DOHOME · GB 20 GLOBALHOUSE · HP 22 HOME PRO · MH 28 MEGA HOME · TW 54 THAIWATSADU) — เดิม `GH` ไม่ติดทั้ง 100 สาขาเพราะ `dim_region` ใช้ `GB` แต่ branch master ใช้ `GH` · **แก้ที่ต้นทางแล้ว 2026-09-11: mds เปลี่ยน `region_id` และ `branch_code` ของโกลบอลเฮ้าส์เป็น `GB`** (ไม่ใส่การแปลงในโค้ด) · **เพิ่ม `ZoneManagerMdtSK` 2026-09-11** — join `dim_zone_manager_mdt` ด้วย `ZoneCode` แบบเดียวกับ `dim_zone_mdt` (ผู้ใช้ยืนยันว่าเกรนเท่ากัน 1 แถว = 1 โซน จึงไม่ทำให้สาขาบวม) · ต้นทางยังว่าง 0 แถว SK จึงเป็น `-1` ทั้ง 494 สาขา แต่จะเข้าที่เองคืนที่ mds กรอกข้อมูล ไม่ต้องกลับมาแก้โค้ด · CTE `zone_manager_current` ปิดท้ายด้วย `QUALIFY ROW_NUMBER() OVER(PARTITION BY ZoneCode ...) = 1` เป็นตัวกันเผื่อวันหน้าโซนหนึ่งมีผู้จัดการหลายคน · **ไม่เก็บ `MdsID` และคอลัมน์ audit** (ผู้ใช้ตัดสิน 2026-09-11) เหลือ 15 คอลัมน์ · **สูตรเช็ค `COUNT(dim) - 1 = COUNT(mds WHERE is_active)` → 494 = 494** · `StoreCode` = `region_id` (HP MH TW GH BT DH) · **`BranchCode` = `store_id` ใช้ค่าดิบ ห้ามตัดแปลง** — แต่ละห้างเขียนคนละแบบ (HP `S015` · GH `GH-101` · BT ชื่อสาขา · TW `60001-CRC Thai Watsadu Limited (Head Office)`) การตัดหลัง `-` ทำให้ TW/GH ไม่ติดเลย · วัด 2026-09-09 join กับ raw ได้ 350/359 = **97.5%** (ไม่ติด: MH `M888` + TW 8 สาขา) · `BranchCode` (`HP_BK1_001`) เป็นรหัสภายใน ใช้เชื่อม PC และเป้า · เก็บ `ZoneMdtSK` ไว้ในตัว fact จึงไม่ join `dim_zone_mdt` · จังหวัดยังไม่มีใน mds (Q31) · ⚠️ ต้องเปลี่ยนเป็น MERGE ก่อนที่ fact จะเป็น incremental (เขียนจริง 2026-09-09) |
| dim_zone_mdt | ZoneMdtSK · **NK = ZoneCode** | โซนขายของ MDT 15 แถว + `-1` · ต้นทาง `mds_dataset.mds_data_sales_zone_master` **ตารางเดียว ไม่ join ใคร** · เก็บคอลัมน์กำกับการแก้ไขครบ (`IsActive/Version/CreatedAt/CreatedBy/UpdatedAt/UpdatedBy`) ต่างจาก dim mds อื่นที่เก็บแค่ `MdsID` — จงใจตามที่ตกลง 2026-09-11 ว่าเก็บทุกคอลัมน์ของ MDS ห้ามตัด · **fact ไม่ join ตารางนี้** อ่าน `ZoneMdtSK` จาก `dim_sales_branch_mdt` · ตั้งชื่อ `_mdt` เพื่อไม่ให้กำกวมกับ `dim_region`/`dim_section` ของ MAC5 · ⚠️ ต้องเปลี่ยนเป็น MERGE ก่อนที่ fact จะเป็น incremental (เขียนจริง 2026-09-09 · **แยกผู้จัดการโซนออกเป็น dim ของตัวเอง 2026-09-11**) |
| dim_zone_manager_mdt | ZoneManagerMdtSK · **NK = ZoneCode + EmployeeID** | ผู้จัดการโซนของ MDT **16 แถว = 15 โซน + `-1`** · ต้นทาง `mds_dataset.mds_data_sales_zone_manager_master` · ⚠️ **ขับตารางจาก `dim_zone_mdt` ไม่ใช่จากตารางผู้จัดการ (2026-09-11)** เพราะต้นทางผู้จัดการยังว่าง 0 แถว — ถ้าขับจากต้นทาง ตารางนี้จะมีแต่แถว `-1` และ `dim_sales_branch_mdt` จะได้ `ZoneManagerMdtSK = -1` ทั้ง 494 สาขา · ขับจากโซนแทนจึงได้โครงครบ 15 โซนตั้งแต่วันนี้ ชื่อผู้จัดการเติมเข้ามาเองคืนที่ mds นำเข้า · `ZoneCode`/`ZoneName` เอาจาก `dim_zone_mdt` (ที่มาที่เดียว) · ⚠️ ผลข้างเคียง: นับแถวเทียบกับ mds ตรง ๆ ไม่ได้แล้ว (เท่ากับจำนวนโซน ไม่ใช่จำนวนแถวต้นทาง) · **แยกออกจาก `dim_zone_mdt` เมื่อ 2026-09-11 ตามรีวิว** — เดิมถูก LEFT JOIN เข้าไปแปะ 4 คอลัมน์ ซึ่งยุบ 2 ตาราง MDS เป็น dim เดียว (ตามรอยกลับต้นทางยาก) และถ้า 1 โซนมีผู้จัดการหลายคนจะทำให้แถวโซนบวมแล้ว `ZoneMdtSK` ที่ปั้นด้วย `ROW_NUMBER` ซ้ำ · ⚠️ **ต้นทางว่าง 0 แถว (2026-09-11)** ตารางจึงมีแต่แถว `-1` — Excel ชีท Zone มีชื่อผู้จัดการครบ 15 โซน ต้องแจ้งคนดูแล mds ให้นำเข้า (โซน `CEN` ไม่มี `employee_id` ในต้นฉบับ) · เกรน = **การมอบหมาย (โซน × ผู้จัดการ)** ไม่ใช่ตัวคน รองรับทั้ง 1 โซนหลายคน และ 1 คนหลายโซน · เก็บคอลัมน์กำกับการแก้ไขครบเช่นกัน · เก็บ `ZoneMdtSK` ไว้ในตัว (แนวเดียวกับ `dim_sales_branch_mdt`) · **`dim_sales_branch_mdt` เก็บ `ZoneManagerMdtSK` ไว้ในตัวแล้ว (2026-09-11)** join ด้วย `ZoneCode` แบบเดียวกับ `dim_zone_mdt` · ⚠️ ต้องเปลี่ยนเป็น MERGE ก่อนที่ consumer จะเก็บ SK นี้ข้ามวัน |
| dim_product_mdt | ProductMdtSK · **NK = ProductCode** (คอลัมน์เดียว ไม่ต้องมีรหัสห้าง) | สินค้าที่ขายผ่าน MDT 2,348 แถว + `-1` · ต้นทาง `mds_dataset.mds_data_product_master_mdt` · **วัด 2026-09-09: `product_mdt_code` ไม่ซ้ำเลยทั้ง 2,348 แถว การไม่สนห้างให้ผลเท่ากับจับคู่แยกห้าง โดยไม่จับผิดเพิ่มแม้แถวเดียว** — ใส่ห้างในคีย์ทำให้ MH ได้แค่ 2.8% (6/214) เพราะ HP/MH ใช้ `ARTNO` ชุดเดียวกันแต่ mds ลงทะเบียนไว้ใต้ห้างเดียว · ครอบคลุม HP 317 · MH 196 · TW 341 · GH 164 · BT 172 = **1,190/1,287 = 92.5%** · **ฝั่ง fact ต้อง `LTRIM(product_code,'0')` ก่อน join** — TW ส่งรหัสพร้อม 0 นำหน้าทุกตัว ไม่ตัดแล้วได้ 0/383 · `ProductCode` แปลงผ่าน INT64 เพราะต้นทางเป็น FLOAT (ห้าม CAST FLOAT→STRING ตรง ๆ) · เก็บ `ProductSK` + `ProductMktSK` ไว้ในตัว fact จึงไม่ join `dim_product_master`/`dim_product_mkt` — `ProductMktSK` เป็นทางเดียวที่โยงยอดขายเข้ากลุ่มสินค้าของเป้า · `commpy` = `ag01` ทุกแถว กรอง `dim_product_master` ด้วย companyID เดียวกันกัน fan-out · ⚠️ ต้นทางหาย 130 แถว (Excel 2,478 → mds 2,348) และ `product_mac5_code` หลุด 27/961 · **แถวใหม่ห้ามเพิ่มอัตโนมัติ** ต้องมีคนกรอกผ่าน form · ⚠️ ต้องเปลี่ยนเป็น MERGE ก่อนที่ fact จะเป็น incremental (เขียนจริง 2026-09-09) |
| dim_pc | PcSK · **NK = EmployeeID + BranchCodeMdt + MarketingGroupID** | PC ของ MDT **579 แถว = 578 แถวของ MDS + `-1`** · ⚠️ **เขียนใหม่ 2026-09-11 — กติกาคือ dim ต้องตรงกับ MDS แถวต่อแถว** เก็บทุกคอลัมน์ ไม่กรองแถวใดออก เพื่อเช็คได้ว่า MDS กับ dim ตรงกันไหม แล้วค่อยเลือกทีหลังว่าจะหยิบคอลัมน์ไหนไปใช้ · **สูตรเช็ค: `COUNT(dim_pc) - 1 = COUNT(mds WHERE is_active)` → 578 = 578** · ในนั้น = 531 การมอบหมายจริง (**527 คน**) + **47 แถวปลอม** · เดิม 1 แถว = 1 คน (527 แถว ยุบซ้ำต่อคน + กรองแถวปลอม + ตัด `branch_code` ทิ้ง) → ใหม่ **1 แถว = 1 แถวของ MDS** เกรนคือการมอบหมาย (คน × สาขา × กลุ่มสินค้า) เพราะเก็บ `branch_code`/`marketinggroupid` ไว้แล้วยุบซ้ำต่อคนไม่ได้ (4 คนดูแล 2 สาขา) · ⚠️ **`PcSK` ไม่ใช่รหัสประจำตัวคนอีกแล้ว** เป็นรหัสของการมอบหมาย · จำนวนคนต้องใช้ `COUNT(DISTINCT EmployeeID)` ไม่ใช่ `COUNT(*)` · เก็บ `BranchMdtSK` ไว้ในตัว (join ด้วย `BranchCodeMdt` — จับไม่ได้ 1 แถว) · เก็บคอลัมน์กำกับการแก้ไขครบ (`IsActive/Version/CreatedAt/CreatedBy/UpdatedAt/UpdatedBy`) ต่างจาก dim mds อื่นที่เก็บแค่ `MdsID` — จงใจตามที่ตกลง · **47 แถวปลอมติดธง `IsPlaceholder = TRUE` ไว้ ไม่กรองออก** เพราะต้องตรงกับ MDS — **ใครเอาไปใช้ต้องใส่ `AND IsPlaceholder = FALSE` เอง** ไม่งั้นจะได้พนักงาน 1 คนที่ดูเหมือนดูแล 47 สาขาทั่วประเทศ (`employee_id = 'Dummy_NotPC'` / ชื่อ `'Not PC'`; รูปแบบเก่าคือ `employee_id` ว่าง + ชื่อ `'ไม่มี PC'` — เช็คไว้ทั้งสองแบบ) · ยุบซ้ำที่ระดับการมอบหมาย `ORDER BY updated_at DESC, id` · ⚠️ `employee_type` กลายเป็น NULL ทั้งหมด (เดิม `'พันธมิตร'`) · ⚠️ `start_date`/`end_date` เป็นค่าตัวแทน `2022-01-01`/`2066-12-31` ทั้ง 578 แถว กติกา "PC ที่ออกแล้วไม่ได้เครดิตยอด" จึงบังคับไม่ได้ · **ไม่มี fact ไหน join และ join กับการขายไม่ได้** — ไฟล์ขายของทั้ง 5 ห้างไม่มีคอลัมน์คนขาย จึงรู้ได้แค่ว่าใครดูแลสาขา ไม่ใช่ใครขายบิล · ถ้าอนุมานจาก (สาขา, กลุ่มสินค้า) ระบุตัวได้ **55.5% ของยอดเงิน** ที่เหลือ 22% สาขาไม่มี PC · 19.6% มี PC 2-3 คน · ⚠️ **`view_fact_saleout_pc_mdt` ยังไม่ได้แก้ตามเกรนใหม่** — มันอ่าน mds ดิบแล้ว `JOIN dim_pc ON EmployeeID` จะได้ 2 แถวสำหรับ 4 คนนั้น ทำให้ `PcCountInCell` เพิ่มเท่าตัว · ทางแก้: ให้ view อ่าน `dim_pc` ตรง ๆ แล้วเลิกอ่าน mds · ⚠️ ต้องเปลี่ยนเป็น MERGE ก่อนที่จะมี fact เก็บ `PcSK` |
| dim_target_saleout_mdt | TargetSaleoutMdtSK · **NK = TargetDate + BranchCodeMdt + MarketingGroupID** | เป้าขายออกของ MDT **ราว 514,000 แถว** + `-1` · ต้นทาง `mds_dataset.mds_data_sales_target_by_mdt_master` 16,903 แถว ครอบ 2024-01 ถึง 2026-12 (36 เดือน · เดือนละ 92-117 ล้านบาท) · **เป็น dim ไม่ใช่ fact** ตามเกณฑ์ "ข้อมูลที่คนกำหนดล่วงหน้า = dim" และตรง convention ของรีโปที่ target ทั้ง 6 ตารางอยู่ในชั้น dim · ต้นทางรายเดือน **กระจายเป็นรายวัน** ด้วย `GENERATE_DATE_ARRAY` · `Amt` = `value ÷ DaysInMonth` ไม่ตัดวันหยุด ไม่ปัดทศนิยม · **`Amt` เป็นยอดต่อวันตัวเดียวที่ SUM ได้** ห้ามเก็บยอดรายเดือนไว้ในแถวรายวัน ถ้าต้องการยอดเดือนใช้ `Amt × DaysInMonth` · ตรวจ: `SUM(Amt)` ของเดือน = `value` ของเดือนนั้น · `partitionBy: TargetDate` · `MarketingGroupID` มีแค่ 2 ค่า (001 PE · 005 DOOR & WINDOW) เก็บเป็น degenerate ไม่ทำ dim แยก — ยอดขายจริงโยงเข้ากลุ่มผ่าน `dim_product_mdt.ProductMktSK` → `dim_product_mkt` · `StoreCode` เอาจาก `dim_sales_branch_mdt` (join `BranchCodeMdt` ติดครบ 386/386) · เป้าไม่แบ่งลง PC และไม่แบ่งลง Section · ⚠️ ต้องเปลี่ยนเป็น MERGE ก่อนที่จะมี fact เก็บ SK นี้ (เขียนจริง 2026-09-09) |

## Group (e) — other operations (3)

| File | What it does |
|---|---|
| dim_calendar | Date spine via `GENERATE_DATE_ARRAY` (next-year start → current+2 Dec-31), joins dim_holiday, weekend/holiday/long-weekend flags; TEMP → DELETE-by-Date → INSERT. **Tag `dimension_yearly`** |
| dim_aging | ~500-line AR aging engine over chq/cql/mir/mie/ar_s/cfs + curated mih/mil + dim_aging_history + view_dim_aging + fact_mir_vs + onetime.cfsinvclose2024 |
| update_sk_sale_rep_group | UPDATE-only: backfills FK SKs (RegionManagerSK, DirectorSK, SectionSK, ...) across the 7 `_last` tables via temp_data |
