# Source Systems

> **LLM context**: **7 raw sources** ลงที่ `gs://file-raw-data/<gcs_folder>/<table>/`
> (AVRO ทั้งหมด ยกเว้น `saleout_lastyear` ที่เป็น CSV)
> บวกกับ BigQuery dataset ที่ถูกโหลดจากภายนอกอีกตัว (`mds_dataset`)
> ตรวจกับโค้ดจริง 2026-10-18 · จำนวนไฟล์ต่อ source ดูที่
> [validated/source-inventory.md](../validated/source-inventory.md)

| Source | GCS folder | Raw dataset | Validated | Curated | สถานะ |
|---|---|---|---|---|---|
| MAC5 (5 บริษัท) | `mac5_*` | `raw_mac5_{ag01,aa05,ab01,ac02,ak02}` | `validated_mac5` | `curated_mac5` — 3 ตาราง | ใช้งานเต็ม |
| MASTERSKU | `mastersku` | `raw_mastersku` | `validated_mastersku` | `curated_mastersku` — 2 ตาราง | ใช้งานเต็ม |
| MASTER_SKU (3.0) | `master_sku` | `raw_master_sku` | `validated_master_sku` | `curated_master_sku` — 2 ตาราง | ใหม่ 2026-10-12 — ยังไม่มี dim/view อ่าน |
| CIS360 | `cis360` | `raw_cis360` | `validated_cis360` | `curated_cis360` — **schema เปล่า** | ใช้งาน (ยังไม่มี curated) |
| SALEOUT_MDT | `saleout_mdt` | `raw_saleout_mdt` | `validated_saleout_mdt` | `curated_saleout_mdt` — 3 ตาราง | ใช้งานเต็ม มีรอบรันของตัวเอง 08:55 |
| DERP | `derp_temp` | `raw_derp` | `validated_derp` | — | ใหม่ 2026-10-17 (crm/sales 2026-10-28) — ยังไม่มีใครอ่านต่อ |
| ALLKONS_COMMISSION | `allkons_commission` | `raw_allkons_commission` | **ไม่มีแล้ว** | — | ⚠️ **หยุดอยู่ชั้น initial** |
| mds_dataset | — | — (โหลดจากภายนอก) | — | — | เป็น master ของ dims ส่วนใหญ่ |

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
  (คอลัมน์คู่ `*_raw`)
- แกะ memo ภาษาไทยใน `mih` และ `chq` ทั้ง 5 บริษัท
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

**ชุดนี้โตขึ้นมากใน 2026-09/10** — จากเดิมที่มีแค่ validated ตอนนี้มีครบทั้งสาย
หน้านี้คือภาพรวมตั้งแต่ต้นจนจบ รายละเอียดแต่ละชั้นอยู่ในหน้าที่ลิงก์ไว้

```
GCS saleout_mdt/{bt,dh,gb,hp,tw,so_mdt_eom,lastyear}
  → raw_saleout_mdt (16 AVRO + saleout_lastyear CSV)
  → validated_saleout_mdt (BT, DH, EOM, GB, HP, LASTYEAR, TW)
  → curated_saleout_mdt ─┬→ fact_saleout_mdt ───────────┐
    curated_stock_mdt ───┼→ fact_stock_mdt → fact_stock_mdt_monthly
    curated_saleout_monthly_mdt → fact_saleout_monthly_mdt
  mds_dataset.mds_data_mdt_* → dim_zone_mdt → dim_zone_ta_mdt → dim_sales_branch_mdt
                               → dim_pc, dim_product_mdt, dim_target_saleout_mdt,
                                 dim_target_series_mdt (+ dim_product_series)
  dims → fact_target_saleout_mdt, fact_target_series_mdt
  facts/dims → views view_fact_*_mdt (fact_view)
```

- **Validated** แยกโฟลเดอร์ตามห้าง: `BT` (บุญถาวร — 7 ตาราง: sales_by_branch,
  stock_by_branch, stock_aging, turnover, ...), `DH` (`saleout_dh`), `EOM` (`eom_bt/gb/hp/tw`
  — ยอดปิดเดือนที่ห้างส่งมาเอง), `GB` (`saleout_gb`), `HP` (`saleout_hp`),
  `TW` (`report_sale_subscription`), `LASTYEAR` (`saleout_lastyear` — ไฟล์ Excel ย้อนหลัง
  ก่อนมี feed, raw เป็น CSV) + `validated_schema_saleout` · มีทั้ง incremental และ full
  (`DH`/`EOM` เก็บเฉพาะไฟล์ล่าสุดของแต่ละงวด) — ตารางต่อไฟล์ดู
  [source-inventory § SALEOUT_MDT](../validated/source-inventory.md#saleout_mdt-17--7-incremental--9-full--1-schema--by-retailer-subfolder)
- **Curated (3)**: `curated_saleout_mdt` (รวมทุกห้างเป็น grain เดียว, incremental),
  `curated_stock_mdt` (table) และ `curated_saleout_monthly_mdt` (table — เลือกจาก
  `eom_*`, `onetime.saleout_lastyear_monthly` หรือ `curated_saleout_mdt`
  แทน `onetime.saleout_monthly_mdt` ที่ปั้นมือ) · **เกรนผสม**: เดือนปัจจุบันเก็บวันที่ขายรายวัน
  เดือนที่ปิดแล้วใช้วันสิ้นเดือน · `fact_saleout_monthly_mdt` ส่งต่อ `month_date` ตามเดิม
  · รวมยอดรายเดือนด้วย `SUM` และ `GROUP BY DATE_TRUNC(month_date, MONTH)` พร้อม key ที่ต้องการ
  และกรองเดือนด้วย `DATE_TRUNC(month_date, MONTH)` ไม่ใช้ `month_date` เท่ากับวันสิ้นเดือน
  — tag `curated_full` / `curated_incremental` · ดู [curated-layer.md](../curated/curated-layer.md)
- **Dimension (7 + 1)**: `dim_zone_mdt`, `dim_zone_ta_mdt`, `dim_sales_branch_mdt`,
  `dim_product_mdt`, `dim_pc`, `dim_target_saleout_mdt`, `dim_target_series_mdt` — ทั้ง 7
  อ่าน `mds_dataset.mds_data_mdt_*` ผ่าน const ใน `js {}` ไม่ใช่ `name:` (สำคัญตอนนับ mds dims)
  · `dim_target_series_mdt` ใช้ `dim_product_series` ซึ่ง **hard-code 2 แถว** (ดู
  [known-issues](../../operations/known-issues.md)) · `dim_zone_manager_mdt` ถูกลบจาก repo แล้ว
  (ตารางยังค้างใน BigQuery) · รายละเอียดดู [dimension/inventory.md](../dimension/inventory.md)
- **Fact (6)**: `fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `fact_stock_mdt`,
  `fact_stock_mdt_monthly`, `fact_target_saleout_mdt`, `fact_target_series_mdt`
  — ดู [fact/fact-layer.md](../fact/fact-layer.md)
- **View**: `view_fact_salein_mdt`, `view_fact_salein_director_mdt`, `view_fact_saleout_pc_mdt`,
  `view_fact_stock_nonmove_mdt`, `view_fact_target_pc_mdt`, `view_fact_target_section_mdt`,
  `view_fact_target_product_group_mdt` (ชื่อลงท้าย `_mdt` แต่บางตัวอ่าน fact ฝั่ง MAC5 —
  ดู [generated lineage](../../diagrams/pipeline_lineage.md))
- **รอบรัน**: อยู่ใน `daily_process` 06:00 และรันซ้ำใน workflow `saleout_morning` 08:55
  (31 target ระบุชื่อทีละตัว ไม่ใช้ tag — **ตารางใหม่ต้องเพิ่มเข้ารายชื่อเองในหน้า Dataform**
  · จุดประสงค์ของรอบ 08:55 ไม่ได้บันทึกไว้ที่ไหน) — ดู
  [running-and-troubleshooting § Schedule](../operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd)
- ข้อควรรู้: แต่ละห้างส่งข้อมูลคนละรูปแบบ — BT ส่งเป็นช่วงวันต้องเฉลี่ยเอง
  (`date_is_estimated`), GB ใช้บาร์โค้ด 13 หลักเป็นรหัสสินค้า, TW ส่ง `branch_code`
  เป็นสตริงเต็ม `60001-CRC Thai Watsadu ...`

## DERP — inventory

- เดิมเรียก D365 / Dynamics 365 · เปลี่ยนชื่อใน repo เป็น DERP เมื่อ 2026-10-28 (โฟลเดอร์, ไฟล์,
  constant, dataset)
- เข้า repo ใน `7819bef` (2026-10-17) · dataset `raw_d365` / `validated_d365` ถูกสร้างด้วยมือ
  ไว้ก่อนแล้วเมื่อ 2026-10-16 (ปัจจุบันคือ `raw_derp` / `validated_derp`)
- GCS folder **`derp_temp/`** (constant `GCS_DERP`) — ชื่อฟังดูชั่วคราว อาจเปลี่ยน
- 56 ตาราง:
  - `inventory_movement_journal_headers`, `inventory_movement_journal_entries` — journal
    การเคลื่อนไหวสินค้า เป็น incremental feed (20260914–16 เป็น full load, ตั้งแต่ 20260917
    รายวัน) · เวลาใน raw เป็น UTC · ขอบเขตการ dedup ตอนเริ่มสร้างและรอบ incremental ดู
    [source-inventory § DERP](../validated/source-inventory.md#derp-57--56-incremental--1-schema)
  - `inventory_item_price` — snapshot ราคาเต็มทุกวัน (~175k แถว) · validated เป็น incremental
    ตั้งแต่ 2026-10-28 (แถวที่ต้นทางลบยังค้างอยู่)
  - 23 `crm_*` (ราคา ND/SD, ใบเสนอราคา, ใบสั่งขาย) + 5 `sales_*` (ช่องทางขาย, เขตการขาย,
    พนักงานขาย) — เพิ่ม 2026-10-28 · โฟลเดอร์เริ่มส่ง 2026-10-21/22/26 · incremental ทั้งหมด ·
    เวลาใน raw เป็นเวลาไทยอยู่แล้ว
  - 10 `crm_*` customer/business-unit tables added 2026-10-29: customer master,
    address, contact, contact channels, credit, segment, stores, customer data zone,
    data zone and business unit. First files use `ASATDATE=20261029`; future cadence
    is unconfirmed. See the source inventory for keys and schema differences.
  - 10 tables added 2026-11-08: seven combo-set/payment tables, two inventory formula
    tables and `sync_mac5_inventory_item_price`. Their first observed files use
    `ASATDATE=20261105`; no later date was present in the checked listing, so snapshot
    versus change-feed behavior and future cadence remain unconfirmed. They follow the
    existing incremental validated pattern; see the source inventory for keys.
  - 5 CRM tables added 2026-11-09: `crm_customer_bank_account`, `crm_customer_branch`,
    `crm_nd_sd_price_channel`, `crm_quotation_terr_cust` and `crm_quotation_terr_sale`.
    They use the existing incremental validated pattern; schema and keys are in the
    source inventory.
- ไฟล์ journal ของวัน `ASATDATE=D` ลงประมาณ **01:02 น. (เวลาไทย) ของวัน D+1** · รันใน `daily_process`
  06:00 (tag `validated`) ตั้งแต่ 2026-10-18 · ไม่อยู่ใน `saleout_morning`
- Downstream readers: see the [validated DERP table cards](../../okf/validated/validated_derp/index.md).
- เรื่องที่ยังเปิดอยู่: timezone ของ `inventory_item_price` ยังไม่ยืนยัน (จึงใช้
  `parseFlexibleDatetime`) · ไฟล์ AVRO ช่วง 2026-10 มีค่า default ผิดกฎใน 3 ฟิลด์ · ชื่อโฟลเดอร์
  `derp_temp` อาจเปลี่ยน
- ตารางต่อไฟล์: [source-inventory § DERP](../validated/source-inventory.md#derp-57--56-incremental--1-schema)

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
- เป็นต้นทางของ MDS dimensions — รายชื่อดู
  [dimension/inventory.md](../dimension/inventory.md)
- stable-key dimensions sync จาก complete source ที่ `is_active = TRUE`: matching keys
  update, new keys insert, inactive or missing rows delete. See
  [dimension/mds-delete-pattern.md](../dimension/mds-delete-pattern.md)
