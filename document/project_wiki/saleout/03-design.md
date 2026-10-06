# 03 · Design — fact, grain, SK, การผูกตาราง

> **LLM context**: ทำไมตารางของสาย Sales Out หน้าตาแบบนี้ · fact/dim มีอะไร grain คืออะไร
> SK สร้างแบบไหน และ join กันยังไง · ข้อที่ห้ามทำ (Section, SK ข้ามวัน, RegionSK ผิดชุด)
> · แหล่ง: `design_saleout_de.xlsx` (D1–D33, L1–L12, Q1–Q20, นอกรีโป), รีวิว 2026-09-08,
> session "สรุปโปรแจก saleout" 2026-09-24 · ชื่อตารางยืนยันกับ `upstream/dev` ในบท 05

## 1. จาก 113 measure เหลือ 12 → 6 fact

**หลักตัดสินว่าอะไรเป็น fact:** "ถ้าไม่มีตารางนี้ ตอบคำถามไม่ได้เลย"
`MTD QTD YTD LM LY %Change %Achieve %Variance Diff` = มุมมองของ measure เดิม → ทำใน Power BI

| fact (design) | ตารางจริง | หมายเหตุ |
|---|---|---|
| ขายออก | `fact_saleout_mdt` | ทุกห้าง |
| ขายเข้า | `fact_transcation` (มีอยู่แล้ว) → `view_fact_salein_mdt` | |
| สต็อก | `fact_stock_mdt` (รายวัน) + `fact_stock_mdt_monthly` (snapshot สิ้นเดือน) | BT + TW · รีวิวสั่งให้มี snapshot เป็นตารางจริง |
| เป้าขายออก | `fact_target_saleout_mdt` ← `dim_target_saleout_mdt` | ⚠️ รีวิวเตือนว่า master/control เป็น dim ไม่ใช่ fact |
| เป้าขายเข้า | ❓ | |
| ยอดตลาด | ❓ ยังไม่มีไฟล์ `MarketShare.xlsx` | นิยามกำกวม |

ไม่เป็น fact: Sales KPI (คำนวณได้) · Working Day (`dim_calendar`)

## 2. Grain ของ `fact_saleout_mdt`

**1 แถว = 1 สินค้า × 1 สาขา × 1 ห้าง × 1 วันขาย × ชนิดเอกสาร** (ตรงกับ key ของ curated)

| ส่วนของ grain | ทำไมต้องมี |
|---|---|
| ~~ช่องทางจำหน่าย~~ | **design เดิมล้าสมัย** · ของจริง (2026-10-06): BT ใช้ `distribution_channel` แค่ตอน diff ยอด MTD (ต้อง diff ทีละช่องทาง 82/1,030 กลุ่มมี 2 ช่องทาง) แล้ว**รวมทิ้ง** · fact ไม่มีช่องทาง (บท 05 ข้อ 5) |
| ชนิดเอกสาร `doc_type` (SALE/RETURN) | รีวิว 2026-09-08 สั่งเปลี่ยนจาก `is_return BOOL` · ไม่งั้นขาย + คืนในคีย์เดียวกันหักกันเหลือ 0 แล้วถูกตัดทิ้ง (เกิดจริงกับ DH 5 คีย์) |
| ❌ PC | ไม่มีต้นทางไหนส่งรหัส PC → ปันส่วนใน view (ข้อ 5) |
| ❌ Section | **เป็นของฝั่ง Sales In** ห้ามแตกยอด/เป้าขายออกตาม Section |
| ❌ เลขใบขาย | มีแค่ GB → ยุบเป็นรายวัน (ข้อขัดแย้งที่ยังเปิด: ยุบแล้วตอบเรื่องวันที่คืนสินค้าไม่ได้ ดูข้อ 7) |

## 3. Bus matrix — อะไรเชื่อมข้าม fact ได้

| dimension | conform | เชื่อมด้วย |
|---|---|---|
| วัน | ✅ | `dim_calendar` |
| สินค้า | ✅ 79–88% | บาร์โค้ด 885 / ไฟล์ mapping (บท 04) |
| ห้าง | ✅ | `store_code` |
| สาขา | ✅ 96% | `target_saleout.xlsx` → mds (บท 04) |
| Zone / TA | ✅ | ผ่านสาขา |
| ภาค / ผู้จัดการภาค / Director | ✅ | `store_code` + ช่วงวันที่ |
| กลุ่มสินค้า (Marketing group) | ✅ | ผ่านสินค้า · **ระดับที่เป้าตั้งไว้** |
| ช่องทาง / อายุสต็อก | ❌ | มีแค่ BT → degenerate |
| PC | ❌ ในยอดขาย | มีในเป้าและใน `dim_pc` เท่านั้น |

## 4. SK — 2 แบบ ต้องรู้ว่าตัวไหนแบบไหน

**SK (Surrogate Key)** = เลขประจำแถวที่คลังตั้งเอง ไม่ได้มาจากห้าง · รวมรหัสหลายรูปแบบให้เป็นเลขเดียว
(HP `S015`, GB `GH-101`, BT ชื่อสาขาไทย → `BranchMdtSK`) · หาไม่เจอ → **-1** ("ไม่ระบุ") ยอดไม่หาย

| แบบ | วิธีสร้าง | เลขนิ่งไหม | SK ในสาย MDT |
|---|---|---|---|
| ROW_NUMBER (rebuild ทุกคืน) | เรียงตามรหัสแล้วนับใหม่ | ❌ **เปลี่ยนได้ทุกคืน** | `BranchMdtSK` `ProductMdtSK` `ZoneMdtSK` `ZoneTaMdtSK` `PcSK` `TargetSaleoutMdtSK` · `ProductMktSK` `RegionSK` `RegionManagerSK` `DirectorSK` (dim_product_mkt / dim_region* / dim_director เป็น `type: table` ทั้งหมด) |
| MERGE (ต่อเลขจากค่าสูงสุด) | ของเดิมเก็บไว้ | ✅ นิ่งตลอดไป | `ProductSK` เท่านั้น (`dim_product_master` = operations MERGE) |

**กติกา**
- ใช้ SK แบบ ROW_NUMBER ได้เพราะ fact ทุกตัวของสาย MDT ก็ rebuild ทุกคืน (`type: "table"`) → เลขชุดเดียวกัน
- ❌ **ห้ามเก็บ SK ข้ามวัน** (export ไป Excel แล้วเอากลับมา join) → อ้างอิงข้ามวันใช้ `BranchCode`/`ProductCode`
- ⚠️ Power BI ต้อง refresh dim กับ fact **พร้อมกัน** ไม่งั้นเชื่อมผิดช่วงหนึ่ง (ต้องบอก BI)

**PK vs SK** — PK คือ*หน้าที่* (คอลัมน์ที่ระบุแถวไม่ซ้ำ) · SK คือ*ที่มา* (เลขที่คลังตั้ง) · SK มักถูกเลือกเป็น PK ของ dim
· validated มี PK เป็น natural key (เช่น `siteno + artno + sale_date`) ไม่มี SK · fact เก็บ SK ของ dim = FK
· PK ใน BigQuery เป็น `NOT ENFORCED` — **ไม่กันแถวซ้ำ** ตัวกันจริงคือ `QUALIFY ROW_NUMBER() … = 1`

## 5. แผนผังการผูก

```
                      mds (ข้อมูลหลักที่คนกรอก)
   ┌──────────────┬──────────┼───────────┬──────────────┐
   ▼              ▼          ▼           ▼              ▼
dim_zone_mdt  dim_zone_ta  dim_sales_   dim_product_   dim_target_
 ZoneMdtSK    ZoneTaMdtSK  branch_mdt   mdt            saleout_mdt
   └──────►───────┴──────► BranchMdtSK  ProductMdtSK   (เป้าแตกรายวัน)
                           +RegionSK    +ProductSK        │
                           +ZoneMdtSK   +ProductMktSK     │
                                 │           │            │
          ┌──────────────────────┼───────────┤            │
          ▼                      ▼           ▼            ▼
      dim_pc              fact_saleout_mdt  fact_stock  fact_target_
  (PC × สาขา × กลุ่ม)     fact_stock_mdt     _monthly    saleout_mdt
          │                      │
          └────────► view_fact_saleout_pc_mdt (ปันยอดลง PC)
```

**หลัก:** dim ลูกเก็บ SK ของ dim แม่ไว้ในตัว (`dim_sales_branch_mdt` มี `ZoneMdtSK` · `dim_product_mdt` มี
`ProductSK` + `ProductMktSK` · `dim_pc` มี `BranchMdtSK`) → fact join แค่ 2 dim ก็ได้ SK ครบ

### `fact_saleout_mdt` join อะไรด้วยอะไร
| SK | join กับ | เงื่อนไข |
|---|---|---|
| `branch_sk`, `zone_sk` | `dim_sales_branch_mdt` | `store_code` + `branch_code` (รหัสดิบของห้าง) |
| `product_mdt_sk`, `product_sk`, `product_mkt_sk` | `dim_product_mdt` | `LTRIM(product_code,'0') = ProductCode` (ไม่ใส่ store_code ได้เพราะ dim ยุบเหลือ 1 แถวต่อรหัส — HP/MH ใช้รหัสร่วมกัน) |
| `report_sk` | `dim_report` | `store_code` + กลุ่มสินค้า · ไม่เจอ → บรรทัด "Other" ของห้างนั้น |
| `region_sk`, `region_manager_sk` | `dim_region` / `dim_region_manager` | `store_code = RegionID` + **`sale_date` อยู่ในช่วง StartDate–EndDate** |
| `director_sk` | `dim_director` | `DirectorID` จาก dim_region + `sale_date` ในช่วง StartDate–EndDate |

- **เทียบยอดกับเป้า** ผ่าน `branch_sk` + `product_mkt_sk` → `MarketingGroupID` (เป้าตั้งระดับกลุ่มสินค้า)
- เป้า join สาขาด้วย `BranchCodeMdt` (รหัสภายใน เช่น `GB_BK1_001`) และกลุ่มด้วย `MarketingGroupID + SubMarketingID + SegmentID`
- **PC**: `view_fact_saleout_pc_mdt` ปันยอดให้ PC ที่ดูแล (สาขา × กลุ่มสินค้า) ที่ `IsPlaceholder = FALSE` — ปันส่วน ไม่ใช่วัด

### ⚠️ RegionSK มี 2 ชุด — ห้ามสลับ
| อยู่ที่ | มาจาก | ความหมาย |
|---|---|---|
| `dim_sales_branch_mdt.RegionSK` | `dim_region_last` | ภาค**ปัจจุบัน** |
| `fact_saleout_mdt.region_sk` | `dim_region` + วันขาย | ภาค**ณ วันที่ขาย** (BT: 3 ปี 2022–25 · 4 ปี 2026+) |

join ข้ามชุด = ภาคผิดโดยไม่มี error

## 6. กฎ design อื่น (จากรีวิว 2026-09-08)
- fact ต้องประกาศ `partitionBy` และ `clusterBy`
- view ต้องมี prefix `view_` เห็นชื่อแล้วรู้ว่าเป็น view
- ใส่ dim ลงเอกสาร design ด้วย ไม่ใช่มีแค่ fact/view
- **DE เป็นเจ้าของความรู้เรื่อง BigQuery** (คลังมีตารางอะไรเก็บอะไร)
- อย่าเชื่อ validated เดิมที่เขียนไว้เร็ว ๆ ตอนโปรเจกต์พัก — รีวิวใหม่ทั้งหมด
- เป้ารายวัน = เป้ารายเดือน ÷ จำนวนวันทั้งเดือน (ไม่ตัดวันหยุด เก็บทศนิยม)

## 7. คำถาม design ที่ยังเปิด
| # | คำถาม | ใครตัดสิน |
|---|---|---|
| D-1 | คืนสินค้าลงวันที่คืน หรือย้อนไปหักวันขายเดิม (GB รองรับทั้งสองทาง เพราะ `Reference_No_` ครบ) | BI |
| D-2 | ยุบ GB เป็นรายวันแล้วเสียเลขใบขาย 19,777 ใบ — ยอมไหม (ขัดกับ D-1) | DE + BI |
| D-3 | ห้างที่ไม่ส่งข้อมูลคืน ใช้ `doc_type` ค่าอะไร | DE |
| D-4 | `uniqueKey` ใน config ของ fact แบบ `table` ไม่มีผล (ตรงกับ grain แล้ว แต่ไม่ได้บังคับอะไร) — เก็บไว้เป็นเอกสาร หรือลบ | DE |
