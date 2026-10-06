# 05 · Pipeline — โค้ดจริงแต่ละชั้นทำอะไร

> **LLM context**: แผนที่โค้ดสาย Sales Out MDT ทุกไฟล์ (initial → validated → curated → dim → fact → view)
> พร้อมวันตัด ค่าคงที่ และจุดที่ต้องแก้เป็นคู่ · ยืนยันกับ `upstream/dev` @ `fe7afdf` (2026-10-06)
> · เลขบรรทัดอ้างอิง ref นั้น อาจเลื่อนได้ · ❓ = ยังไม่ได้ยืนยัน

## 1. ลำดับการรัน (tag)

```
initial          drop_all_tables_validated_saleout_mdt ⚠️ → create_all_table_raw_saleout_mdt
validated        validated_schema_saleout → BT×7 · HP · GB · TW · DH · LASTYEAR · EOM×4
curated          curated_saleout_mdt · curated_stock_mdt → curated_saleout_monthly_mdt
dimension_daily  dim_zone_mdt → dim_zone_ta_mdt → dim_sales_branch_mdt → dim_pc · dim_target_saleout_mdt · dim_target_series_mdt
                 dim_product_mdt (← dim_product_master, dim_stk_mkt, dim_product_mkt)
fact_daily       fact_saleout_mdt · fact_saleout_monthly_mdt · fact_stock_mdt → fact_stock_mdt_monthly · fact_target_saleout_mdt · fact_target_series_mdt
view             view_fact_*_mdt (6 ตัว)
```

- dim/fact อ้างตารางด้วย string + `dependencies:` เกือบทั้งหมด ไม่ใช่ `ref()` → ลืมใส่ dependency = รันผิดลำดับเงียบ ๆ
- `dim_sales_branch_mdt` **อ่าน curated** (`ref`, :122) เพื่อเติมสาขาใหม่ → dim ต้องรันหลัง curated
- `curated_saleout_monthly_mdt` อ่าน `onetime.saleout_lastyear_monthly` แบบ hardcode (:34) ไม่ใช่ ref

### ⚠️ `drop_all_tables_validated_saleout_mdt`
เป็น dependency ของ `create_all_table_raw_saleout_mdt` และ `validated_schema_saleout`
→ รัน validated แบบ **"include dependencies"** จะลาก drop มาด้วย → ตาราง incremental เสียประวัติที่ GCS ไม่มีแล้ว
· ใช้ tag `initial` (บท 02) → รัน tag `initial` = validated saleout หาย · hook `guard-dangerous` บล็อกคำสั่งที่มีชื่อไฟล์นี้

## 2. Config

| key (`variables.json`) | ค่า |
|---|---|
| `RAW_SALEOUT_MDT` | `raw_saleout_mdt` |
| `VALIDATED_SALEOUT_MDT` | `validated_saleout_mdt` |
| `CURATED_SALEOUT_MDT` | `curated_saleout_mdt` |
| `GCS_SALEOUT_MDT` | `saleout_mdt` (โฟลเดอร์ใน `gs://file-raw-data`) |
| `BACKFILL_DAYS` | `1` (`workflow_settings.yaml`) — ช่วงย้อนของ validated/curated incremental |

## 3. Initial — `create_all_table_raw_saleout_mdt`
operations สร้าง external table AVRO (hive partition `ASATDATE`) ทุกห้าง: BT 7 sheet · `saleout_hp` · `saleout_gb`
· `report_sale_subscription` (TW) · `saleout_dh` · EOM 5 ตัว · `saleout_lastyear` เป็น **CSV**

## 4. Validated (`validated_saleout_mdt`)

| ไฟล์ | แบบ | คีย์ dedup | จุดสำคัญ |
|---|---|---|---|
| HP/`saleout_hp` | incremental | siteno, artno, sale_date (ASATDATE DESC, value DESC) | **แยก HP/MH ที่นี่** (:56-60): `M888`/`CS01`/`EX99` หรือขึ้นต้น `S` → HP · `M` → MH · อื่น → NULL |
| GB/`saleout_gb` | incremental | sale_no, sale_date, branch, product | 2 รูปแบบวัน (:17-22): ปี ≥ 2500 = พ.ศ. อ่าน d/m แล้ว −543 · ไม่งั้น ค.ศ. อ่าน m/d · ทิ้งแถวสรุป (Sale_Date NULL) |
| BT/`sale_by_branch_detail` | incremental | branch, article_id, distribution_channel, end_date | ค่า**สะสม MTD** · `Website` → `Web` |
| BT/อีก 4 ตาราง (mch3, sales_by_branch, turnover, turnover_brand) | incremental | vendor_id, branch (+mch3 / brand, class_stock) — **ไม่มี `end_date`** จึงกินข้อมูลตัวเอง (backlog 15) | **ไม่มีใครใช้ (ตั้งใจ)** โหลดทุกชีตเข้า raw ไว้เทียบยอด ใช้จริงแค่ชีต detail · `sales_by_branch` เป็นยอดรวมระดับสาขา ไม่มีรายสินค้า (`eom_bt` :16) |
| BT/`stock_by_branch`, `stock_aging` | table (full) | QUALIFY | ใช้ทำสต็อก |
| TW/`report_sale_subscription` | table (full) | **ไม่มี** | dedup ใน curated |
| DH/`saleout_dh` | **table (full)** | sale_date, branch, product, is_return | ดูข้อ 4.1 |
| LASTYEAR/`saleout_lastyear` | table | ไม่ dedup (ตั้งใจ) | partition `sale_date` |
| EOM/`eom_bt/gb/hp/tw` | table | month + branch + product (GB +doc_type · HP +store_code) | ยอดปิดเดือนที่ห้างส่ง (ข้อ 6) |

incremental ทุกตัวกรอง `ASATDATE >= วันนี้ − BACKFILL_DAYS` (string compare)

### 4.1 DH — ทำไมเป็น full load
- `ASATDATE` ของ DH = วันขายสุดท้ายในไฟล์ (1 ไฟล์ = 1 สาขา × 1 เดือน) → กรองแบบ incremental ได้ 0 แถว
- คอลัมน์: วันขาย `SALES_DATE` (`%Y-%m-%d`, :42) · สินค้า **`PRODUCT_CODE`** (:44) · คืน = `SALES_AMOUNT < 0`
- เก็บไฟล์ล่าสุดต่อ (`SOURCE_FOLDER`, เดือนขาย) ด้วย `FILE_MODIFIED` แล้ว **SUM** (ไม่ใช่ ROW_NUMBER) — DH อัปไฟล์ทับได้

## 5. Curated `curated_saleout_mdt` (หัวใจของสาย)

incremental · key `sale_date, store_code, branch_code, product_code, doc_type` · partition `sale_date`
· UNION ALL 6 ก้อน (:530-540): `hp` `bt` `gb` `tw` `dh` `lastyear`

| ก้อน | logic |
|---|---|
| **hp** (HP+MH) | กรอง `qty <> 0 OR value <> 0` · `doc_type` = RETURN ถ้า QTY < 0 |
| **bt** | `bt_feed_gap` หา `days_covered` (ระยะห่างระหว่าง snapshot) → `bt_daily` = `MTD − LAG(MTD)` ตาม (branch, article, channel, เดือน) **ไม่กรอง asatdate** (ต้องเห็นวันก่อน) → รวมช่องทาง · `date_is_estimated = days_covered > 1` (ฟีดขาดวัน ยอดไปกองวันถัดไป) |
| **gb** | เก็บ product_code ตัวเลขเท่านั้น (หรือ NULL) · **ตัดปั๊ม Hitachi 3 บาร์โค้ด** (:140) · ไฟล์ล่าสุดต่อบิล (DENSE_RANK) · `doc_type` จากต้นทาง |
| **tw** | วันขาย = `Last_Sold_Date >= 2026-05-13` (:186) · ล่าสุดต่อ (Store, SKU, วัน) · **เก็บเฉพาะวันที่มี ≥ 30 สาขา** (:204) · `LTRIM(SKU,'0')` |
| **dh** | อ่าน validated ทั้งหมด กรอง `sale_date >= 2026-08-01` (:265) — ก.ค. เป็นไฟล์ตัวอย่างที่ทีมอัปเอง |
| **lastyear** | ไฟล์ BI ใช้เมื่อ **ครบ 3 ข้อ**: ไม่มีฟีดวันนั้นของห้างนั้น (`feed_days`) · เดือนไม่อยู่ใน `partial_months` · `sale_date < feed_from` · DH: รหัส `^M[0-9]+$` เติม `_TG` |

### วันตัด `feed_start` (:453-458) — ⚠️ แก้คู่กับ CTE ของห้าง
| ห้าง | feed_from |
|---|---|
| HP · MH · GB | 2026-02-09 |
| BT | 2026-02-10 |
| TW | 2026-05-13 (คู่กับ :186) |
| DH | 2026-08-01 (คู่กับ :265) |

ห้างใหม่ = เพิ่มแถวที่นี่ **และ** กรองวันเดียวกันใน CTE ของห้าง ไม่งั้นยอดนับซ้ำ (BI + ฟีด)

- `lastyear_topup` (เครื่องคำนวณ :297-487 · CTE :460) ถูก comment ออกจาก UNION (:541-542) — คำนวณแต่ยังไม่ต่อท่อ
- `distribution_channel` ใช้แค่เป็น PARTITION ของ LAG (ต้อง diff ทีละช่องทาง ไม่งั้นยอดเพี้ยน) แล้วรวมทิ้ง → **grain จริงไม่มีช่องทาง** (ตั้งใจ · บท 03 แก้แล้ว)
- `lastyear_topup` = **รอเปิด** ไม่ใช่เลิกใช้ (เติมวันที่ฟีดไม่มี, `date_is_estimated = TRUE`) — ห้ามลบ

## 6. Monthly + EOM
- **EOM** = ยอดปิดเดือนที่ห้างส่งเอง · งวดอ่านจากเนื้อไฟล์ ไม่ใช่ ASATDATE · เก็บเวอร์ชันล่าสุดต่องวด
- `fact_saleout_monthly_mdt` มี `sales_channel` ใน uniqueKey แต่เป็นค่าคงที่ `'-'` → grain ยังไม่มีช่องทาง
- `curated_saleout_monthly_mdt` เลือก 1 แหล่งต่อ (เดือน × ห้าง) ตามลำดับ:
  1. `CHAIN_FILE` (EOM, เดือนที่ปิดแล้ว) → 2. `BI` (`onetime.saleout_lastyear_monthly`) → 3. `DAILY_ROLLUP` (จาก curated รายวัน)
  - คอลัมน์ `source_type` บอกว่ามาจากไหน · **เดือนปัจจุบันยังเป็นรายวัน** (grain ผสม)

## 7. Stock — `curated_stock_mdt`
| ห้าง | ต้นทาง | วันที่สต็อก | หมายเหตุ |
|---|---|---|---|
| BT | `stock_by_branch` | `end_date` | มี `ur_cost_amt` (ทุน) |
| TW | `report_sale_subscription` | `asatdate` | ทิ้งแถว `Stock_On_Hand` NULL |

## 8. Dimension (`dimension_table`, ทุกตัว `type: table`, SK = ROW_NUMBER, มีแถว -1)

| dim | ต้นทาง mds | จุดสำคัญ |
|---|---|---|
| `dim_zone_mdt` | `mds_data_sales_zone_master` | |
| `dim_zone_ta_mdt` | `mds_data_sales_zone_ta_master` | |
| `dim_sales_branch_mdt` | `mds_data_sales_branch_master` | RegionSK จาก **`dim_region_last`** (ag01) · Section แกะด้วย REGEXP (:98-108) · **`new_branch`**: สาขาที่เห็นใน curated แต่ไม่มีใน master → เพิ่มให้ ZoneName = `รอข้อมูล Master` |
| `dim_product_mdt` | `mds_data_product_master_mdt` | dedup ต่อ `CAST(product_mdt_code AS INT64)` · ProductSK จาก `dim_product_master` ผ่าน **รหัส mac5** · ProductMktSK fallback `dim_stk_mkt` ⋈ `dim_product_mkt` |
| `dim_pc` | `mds_data_sales_pc_master` | PC × สาขา × กลุ่ม · ล่าสุดตาม `updated_at` · `IsPlaceholder` = `Dummy_NotPC` / `ไม่มี PC` / `Not PC` |
| `dim_target_saleout_mdt` | `mds_data_sales_target_by_mdt_master` | แตกรายวัน `MonthAmt / DaysInMonth` · **GH_→GB_ (:96-98)** |
| `dim_target_series_mdt` | `mds_data_sales_target_by_series` (+ `dim_product_series`) | GH_→GB_ อีกที่ (:77-79) · series ไม่รู้จัก → `999999` OTHERS |

> ✅ **ยืนยันแล้ว: บาร์โค้ด 885 ไม่ได้ใช้ใน dim/fact/view เลย** — การจับสินค้าจริงอยู่ใน mds
> (`product_mdt_code` → `product_mac5_code`) · curated มีคอลัมน์ `barcode_match` แต่ไม่มีใคร join

## 9. Fact (`fact_table`, ทุกตัว `type: table` rebuild ทุกคืน)

### `fact_saleout_mdt` — partition `sale_date` · cluster `store_code, branch_sk, product_mdt_sk`
| join | เงื่อนไข |
|---|---|
| สาขา | `store_code = StoreCode AND branch_code = BranchCode` |
| สินค้า | `LTRIM(product_code,'0') = ProductCode` |
| report | `dim_report` ตรง (store, MG) → ไม่เจอใช้แถว MG NULL ของห้าง |
| ภาค / ผจก.ภาค | `store_code = RegionID` + `sale_date BETWEEN StartDate AND EndDate` |
| Director | `DirectorID` จาก dim_region (ผ่าน `rg`) + `sale_date BETWEEN StartDate AND EndDate` (:162-164) |

- SK ไม่เจอ → `IFNULL(…,-1)` · `product_mkt_sk` ไม่เจอ → MG `999` "Waiting Master" (ไม่ใช่ -1)
- **ตัด GB Segment `00221`, `00222`** (:166-170) = **ทดลองตัด** (2026-09-23) ไม่ใช่กฎถาวร · `00221` = HITACHI HOME PUMP 3 รุ่น 16.47 ลบ. · `00222` ยังไม่มีแถว GB · รอ BI ยืนยันแล้วย้ายไปเป็น master รายการตัดออก (store, segment) · ❓ ใครสั่ง
- คู่กับการตัดปั๊ม Hitachi ใน curated (:140) — **ตัดด้วยรหัสสินค้า 3 ตัว ไม่ใช่คำว่า 'HITACHI'** เพราะมีถังเก็บน้ำ DOS ที่ชื่อมีคำนี้ (พี่กุ้งแจ้งผ่านคุณวิสุทธิ์ 2026-10-05)

### ตัวอื่น
| fact | สรุป |
|---|---|
| `fact_saleout_monthly_mdt` | แบบเดียวกันบน monthly · ภาคใช้ `month_date` |
| `fact_stock_mdt` | curated_stock + dim สาขา/สินค้า (ไม่มี fallback 999) |
| `fact_stock_mdt_monthly` | ต่อ (ห้าง, เดือน) เอา**วันสุดท้ายที่ยอดรวมไม่เป็น 0** · `is_month_end` = เดือนก่อนเดือนนี้ |
| `fact_target_saleout_mdt` | เป้ารายวัน ระดับ MG/SubMkt/Segment + ภาค ณ วันเป้า |
| `fact_target_series_mdt` | เป้าราย series · **มีแต่เป้าจำนวนชิ้น** — `target_amt` = 0 ทุกแถว (42,216 แถว, วัด 2026-10-06) · `target_qty` รวม 3,834 |

## 10. View (`fact_view`)
| view | ทำอะไร |
|---|---|
| `view_fact_saleout_pc_mdt` | **ปันยอดให้ PC**: แตก `dim_pc` เป็นรายเดือน (ตัด -1 / placeholder) · `pc_in_slot` = จำนวน PC ใน (เดือน, สาขา, MG) · ยอด ÷ `pc_in_slot` · `fact_pc_not_count = 'Yes'` กันนับซ้ำ · ใช้ **monthly** fact |
| `view_fact_stock_nonmove_mdt` | สต็อกล่าสุด > 0 + วันขายล่าสุด → bucket 0-30/31-60/61-90/>90/ไม่เคยขาย |
| `view_fact_target_section_mdt` | เป้ารวม (วัน, ห้าง, MG) + จำนวนสาขา ⚠️ ชื่อมี section ทั้งที่ห้ามแตกตาม Section (บท 01 ข้อ 6.3) |
| `view_fact_target_product_group_mdt` | จาก `dim_target_product_group_by_sale_dayofwork` เฉพาะ `MDT` |
| `view_fact_salein_mdt` | ขายเข้า: `fact_transcation` กรองลูกค้าที่เป็น 6 ห้าง · จับสาขาด้วยชื่อ |
| `view_fact_salein_director_mdt` | `view_fact_transcation` DirectorID `00004` |

## 11. ค่าคงที่ใน SQL (ต้องรู้ก่อนแก้)
| ค่า | ที่ | แก้เมื่อ |
|---|---|---|
| `feed_start` 6 แถว | curated :453-458 | ห้างใหม่ / เปลี่ยนวันตัด (แก้คู่ CTE) |
| TW `2026-05-13` · DH `2026-08-01` | curated :186, :265 | คู่กับ feed_start |
| TW ≥ 30 สาขา | curated :204 | TW เปิด/ปิดสาขาเยอะ |
| Hitachi 3 บาร์โค้ด | curated :140 · `eom_gb` :20 | **แก้ 2 ที่** |
| GB Segment `00221/00222` | fact :169 | |
| GH_→GB_ | dim_target_saleout :96 · dim_target_series :77 | **ลบ 2 ที่** เมื่อ MDS แก้ |
| `2099-12-31` | view PC :41 | – |

## 12. ⚠️ กับดักของ Dataform workspace (จาก fork 3, 2026-10-06)
1. **workspace/BigQuery ล้ำหน้ารีโปได้แบบเงียบ ๆ** — `view_fact_saleout_pc_mdt` บน BigQuery มี `region_sk`, `region_manager_sk`, `director_sk`
   แต่ไฟล์ในรีโปไม่มี พอ deploy จากรีโป 3 คอลัมน์หาย (BI จับได้) · `dataform compile` กับ `--dry_run` **จับไม่ได้** เพราะ SQL ถูก
   → ก่อน deploy view ให้เทียบกับ `SELECT view_definition FROM <dataset>.INFORMATION_SCHEMA.VIEWS` หรือใช้ skill `bq-drift-scan`
   · ✅ dev มี 3 คอลัมน์นี้แล้ว (`view_fact_saleout_pc_mdt.sqlx` :67-69 ผ่าน commit `0e3a8f2`)
2. **Dataform workspace ตัด comment ทิ้งตอน commit** — ไฟล์ saleout ~10 ตัวบน dev ตรรกะตรงกับ local แต่ comment หาย
   (เช่น เหตุผลที่ `eom_gb` เป็น table, คำเตือน `is_return` ของ DH ห้ามคิดจากผลรวม) → **อ่านเหตุผลจาก local repo ไม่ใช่จาก dev**
   · เลขบรรทัดใน local กับ dev จึงต่างกันได้ 2–3 บรรทัด
3. `dependencies[]` ไม่ใช่ภาพ DAG จริง — อ้างตารางด้วยการต่อ string ที่ Dataform มองไม่เห็น → "Include dependents" ใน UI พลาดได้

## 13. ❓ ที่ยังเปิด
1. `drop_all_tables_validated_saleout_mdt` ใช้ tag `initial` (บท 02) — ควรตัดออกจาก dependency ของ validated ไหม
2. GB Segment `00221/00222` — ใครสั่ง และ BI ยืนยันเป็นกฎถาวรเมื่อไหร่
3. **ช่องว่าง 19% เม.ย.–ก.ค. 2026** (`saleout_lastyear` :32-33) — **ยังไม่รู้สาเหตุ** · อาจเป็นแค่การเทียบคนละฐานวัน
   (ไฟล์ BI ลงวันไม่ตรงวันขาย) แต่ยังไม่มีใครพิสูจน์ · ต้องหาสาเหตุก่อนจะเปิด `lastyear_topup`
