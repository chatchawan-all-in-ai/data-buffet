# Source Systems

> **LLM context**: **5 raw sources** ลงเป็น AVRO ที่ `gs://file-raw-data/<gcs_folder>/<table>/`
> บวกกับ BigQuery dataset ที่ถูกโหลดจากภายนอกอีกตัว (`mds_dataset`)
> ตรวจกับโค้ดจริง 2026-09-15

| Source | Raw dataset | Validated | Curated | สถานะ |
|---|---|---|---|---|
| MAC5 (5 บริษัท) | `raw_mac5_{ag01,aa05,ab01,ac02,ak02}` | `validated_mac5` — **87 ไฟล์** | `curated_mac5` — 3 ตาราง | ใช้งานเต็ม |
| MASTERSKU | `raw_mastersku` | `validated_mastersku` — 12 ไฟล์ | `curated_mastersku` — 2 ตาราง | ใช้งานเต็ม |
| CIS360 | `raw_cis360` | `validated_cis360` — 25 ไฟล์ | `curated_cis360` — **schema เปล่า** | ใช้งาน (ยังไม่มี curated) |
| SALEOUT_MDT | `raw_saleout_mdt` | `validated_saleout_mdt` — 12 ไฟล์ | `curated_saleout_mdt` — 2 ตาราง | ใช้งานเต็ม (ชุดใหม่ 2026-09) |
| ALLKONS_COMMISSION | `raw_allkons_commission` | **ไม่มีแล้ว** | — | ⚠️ **หยุดอยู่ชั้น initial** |
| mds_dataset | — (โหลดจากภายนอก) | — | — | เป็น master ของ 45 dims |

## MAC5 — POS / ERP / Ledger (แหล่งหลัก)

- ERP ไทย ตารางใช้รหัส 3 ตัวอักษร (`mih` = หัวใบกำกับ, `mil` = บรรทัดใบกำกับ,
  `deb` = ลูกหนี้/ลูกค้า, `stk` = สินค้า, `per` = พนักงาน, `ap_s`/`ar_s` = สถานะ AP/AR,
  `cps` = งานค้าง, `sto` = คลัง/สาขา, ...)
- **5 บริษัท** แต่ละบริษัทมี raw dataset และโฟลเดอร์ GCS ของตัวเอง:
  `ag01` (ตัวหลัก **87 external tables**), `aa05`, `ab01`, `ac02`, `ak02` (บริษัทละ 14)
- 14 ตาราง validated `UNION ALL` ทั้ง 5 บริษัทพร้อมคอลัมน์ `company_id` ที่ใส่เป็น literal:
  `ap_s, ar_s, cfs, chq, cql, deb, dep, mie, mih, mil, mir, per, stg, stk`
- GCS prefix พิเศษ: `mac5_report` (stg_report, stgacc), `mac5_gps`
  (tdelivery, ttrip, ttrip_document)
- ของเฉพาะ `ag01`: สัดส่วน split-sale (`mih2`), กลับเครื่องหมายเมื่อ `mihtype='BS'`
  (คอลัมน์คู่ `*_raw`), แกะ memo ภาษาไทย
- **doc-grain purge** บน `mih`/`mil`/`mir` (2026-09-10) — PK ระดับบรรทัดลบแถวที่ต้นทาง
  ลบไม่ได้ ดู [validated-layer.md](../validated/validated-layer.md)

## MASTERSKU — Product master

- 12 ไฟล์: `product` (PK `prd_id`), `product_detail`, `brand`, `category`, `unit`,
  `vendor`, `product_group`, `product_group_cost_group`, `product_category`,
  `product_status`, `product_admin_status` + schema bootstrap
- JSON ซ้อนใน `product_detail` (`prdDiminsionData.$.dimFeild`,
  `pd_spacific_fields.$.SpeciFeild`) เก็บขนาด/สีพร้อม label ภาษาไทย
  (`ขนาด`, `สี`) — แกะใน `curated_product`
  (`prdDiminsionData` เป็น **load-bearing typo** ของต้นทาง ห้ามแก้)

## CIS360 — ข้อมูลอ้างอิงลูกค้า

- 25 ไฟล์ ทั้งหมด incremental PK `id`: ตัวหลัก (`customer_profile`,
  `customer_address`, `juristic_profile`), ตาราง lookup (province/district/sub_district/
  zipcode/country, customer_status/type, juristic_type, nature_business,
  organize_type, role_business, category, prefix) และตารางเชื่อม
  (`customer_profile_*`, `customer_to_*`)
- consumer หลักคือ `dim_customer`

## SALEOUT_MDT — sell-out modern trade

**ชุดนี้โตขึ้นมากใน 2026-09** — จากเดิมที่มีแค่ validated ตอนนี้มีครบทั้งสาย

- **Validated (12 ไฟล์)** แยกโฟลเดอร์ตามห้าง: `BT` (บุญถาวร — 7 ตาราง:
  sales_by_branch, stock_by_branch, stock_aging, turnover, ...), `GB` (`saleout_gb`),
  `HP` (`saleout_hp`), `TW` (`report_sale_subscription`), `LASTYEAR`
  (`saleout_lastyear` — ไฟล์ Excel ย้อนหลังก่อนมี feed) + `validated_schema_saleout`
- **Curated (2)**: `curated_saleout_mdt` (รวม 5 แหล่งเป็น grain เดียว) และ
  `curated_stock_mdt` — ดู [curated-layer.md](../curated/curated-layer.md)
- **Dimension (6)**: `dim_zone_mdt`, `dim_zone_manager_mdt`, `dim_sales_branch_mdt`,
  `dim_product_mdt`, `dim_pc`, `dim_target_saleout_mdt` — ทั้ง 6 อ่าน `mds_dataset`
  ผ่าน const ใน `js {}` ไม่ใช่ `name:` (สำคัญตอนนับ mds dims)
- **Fact (3)**: `fact_saleout_mdt`, `fact_stock_mdt`, `fact_stock_mdt_monthly`
- **View (1)**: `view_fact_salein_mdt`
- ข้อควรรู้: แต่ละห้างส่งข้อมูลคนละรูปแบบ — BT ส่งเป็นช่วงวันต้องเฉลี่ยเอง
  (`date_is_estimated`), GB ใช้บาร์โค้ด 13 หลักเป็นรหัสสินค้า, TW ส่ง `branch_code`
  เป็นสตริงเต็ม `60001-CRC Thai Watsadu ...`

## ALLKONS_COMMISSION — ค่าคอมมิชชั่น (⚠️ หยุดไว้)

- เพิ่มเข้ามา 2026-08-18 · GCS prefix `allkons_commission/` โฟลเดอร์ละตาราง
  Hive-partitioned ด้วย `ASATDATE=`
- **7 raw external tables** ยังถูกสร้างอยู่: `mac5_transactions` (ตัวใหญ่),
  `mac5_sales_areas`, `mac5_sales_channels`, `sales_channels`, `sales_positions`,
  `marketing_condition_version_details`, `target_commission_monthly_carries`
- ⚠️ **ชั้น validated ถูกลบทิ้งแล้ว** ใน commit `74a10e0 "pause process data layer of
  commission"` — `definitions/validated/allkons_commission/` ไม่มีอยู่แล้ว
  dataset `validated_allkons_commission` ยังค้างใน BigQuery พร้อมข้อมูลเก่าที่ไม่มี
  ใครเติม · **ไม่มีอะไร downstream ใช้**
- ถ้าจะรื้อฟื้น: ทุกตารางคีย์ด้วย `id` (ยืนยันว่า unique ต่อ snapshot) ใช้ validated
  pattern มาตรฐานได้เลย · `mac5_sales_areas` / `mac5_sales_channels` มีคอลัมน์ชื่อ
  `desc` (reserved word) ต้องครอบ backtick เสมอ

## mds_dataset — Master Data Service (ภายนอก)

- **ไม่ได้สร้างโดย repo นี้** ตารางชื่อ `mds_data_<entity>_master`
- คอลัมน์มาตรฐานทุกตาราง: `id` (row id → เก็บใน dim เป็น `MdsID`),
  `is_active` (soft-delete flag), `updated_at`
- เป็นต้นทางของ **45 dims** (43 full rebuild + 2 MERGE legacy)
- dim แบบ full rebuild อ่านเฉพาะ `is_active = TRUE` ทั้งตารางทุกคืน soft delete และ
  overwrite import จึงหายเองอัตโนมัติ · dim แบบ MERGE (2 ตัว) ต้องมี tombstone DELETE
  ปิดท้าย ดู [dimension/mds-delete-pattern.md](../dimension/mds-delete-pattern.md)
