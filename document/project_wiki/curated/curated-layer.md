# Curated Layer — `definitions/curated/`

> **LLM context**: **11 ไฟล์** — 4 เป็น schema-bootstrap `operations` (source ละตัว),
> 7 เป็น transformation จริง · dataset ต่อ source: `curated_mac5`, `curated_mastersku`,
> `curated_saleout_mdt` (`curated_cis360` สร้าง schema ไว้แล้วแต่ยังไม่มีตาราง)
> ตรวจกับโค้ดจริง 2026-09-15

## Inventory (11)

| File | Target | Type | uniqueKey | Partition / Cluster | Tags |
|---|---|---|---|---|---|
| `mac5/curated_schema_mac5.sqlx` | schema `curated_mac5` | operations | — | — | `curated` |
| `mac5/curated_mih.sqlx` | `curated_mac5.curated_mih` | incremental | `company_id, mihType, mihVnos` | `asatdate` / `company_id, mihVnos, mihType` | `curated` |
| `mac5/curated_mil.sqlx` | `curated_mac5.curated_mil` | incremental | `company_id, milType, milVnos, milListno` | `asatdate` / `company_id, milVnos, milType` | `curated` |
| `mac5/curated_tbook_quotation.sqlx` | `curated_mac5.curated_tbook_quotation` | incremental | `company_id, running` | (partition comment ไว้) | `curated` |
| `mastersku/curated_schema_mastersku.sqlx` | schema `curated_mastersku` | operations | — | — | `curated` |
| `mastersku/curated_product.sqlx` | `curated_mastersku.curated_product` | incremental | `prdSku` | `asatdate` / `prdSku, prdUniversalBarcode, prdVendorId, prdBrandId` | `curated` |
| `mastersku/product_for_aisearch.sqlx` | `curated_mastersku.product_for_aisearch` | operations | — | — | `curated` |
| `cis360/curated_schema_cis360.sqlx` | schema `curated_cis360` | operations | — | — | `curated` |
| `saleout_mdt/curated_schema_saleout.sqlx` | schema `curated_saleout_mdt` | operations | — | — | `curated` |
| `saleout_mdt/curated_saleout_mdt.sqlx` | `curated_saleout_mdt.curated_saleout_mdt` | incremental | `sale_date, store_code, branch_code, product_code, doc_type` | `sale_date` / `store_code, branch_code, product_code` | `curated`, **`curated_incremental`** |
| `saleout_mdt/curated_stock_mdt.sqlx` | `curated_saleout_mdt.curated_stock_mdt` | **table** | — | `stock_date` / `store_code, branch_code, product_code` | `curated`, **`curated_full`** |

> tag `curated_incremental` / `curated_full` **เริ่มถูกใช้จริงแล้ว** ตั้งแต่ชุด SALEOUT_MDT
> (ก่อนหน้านี้ประกาศไว้เฉย ๆ ทั้งชั้นใช้แค่ `curated`)

## Incremental window — สำคัญ

ตาราง curated ฝั่ง MAC5 ใช้ window **1 วัน** แบบ inline ไม่ใช่ `updatePartitionFilter`:

```sql
${when(incremental(), `AND asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`)}
```

มีแค่ `curated_product` ที่ใช้ `updatePartitionFilter: "asatdate >= CURRENT_DATE('Asia/Bangkok')-7"`

ฝั่ง SALEOUT_MDT `curated_saleout_mdt` กรอง `asatdate` **ที่ต้นทาง** (ในแต่ละ CTE)
ไม่ใช่ข้างนอก — เพราะ validated partition ด้วย `asatdate` ถ้าวางเงื่อนไขไว้ชั้นนอก
BigQuery จะไม่ตัดพาร์ทิชันให้

## Business logic ต่อตาราง

### `curated_mih` — หัวเอกสาร

> ไม่ต้องทำ doc-grain purge: `uniqueKey` = `company_id, mihType, mihVnos` **คือ**
> document key อยู่แล้ว MERGE จึงแทนที่ทั้งเอกสาร · ยืนยัน 2026-09-10:
> 3,903,023 แถว / 3,903,023 เอกสาร **0 แถวค้าง**

- เปลี่ยนชื่อ ~90 คอลัมน์จาก snake_case ของ `validated_mac5.mih` เป็น camelCase
- lookup คำอธิบายสถานะ: ประเภทขาย (`QS,PS,IS,AS,BS,VS,RS`) → `ar_s.ar_snamet` ·
  ประเภทซื้อ (`QP,PP,IP,AP,BP,VP,RP`) → `ap_s.ap_snamet` → `mihstatus_desc`
- สัดส่วน split-sale จาก `mih2` (แปลงสตริงเปอร์เซ็นต์ด้วย
  `REGEXP_REPLACE(..., r'[^0-9.%]', '')`) ใช้**เฉพาะบริษัท `ag01`** บริษัทอื่นผ่านไป
  ด้วยค่า default (`100.00%` / `0.00%`) ผ่าน `UNION ALL`

### `curated_mil` — บรรทัดเอกสาร (ซับซ้อนที่สุด)

0. **คอลัมน์ `_raw` (เพิ่ม 2026-08-26)**: `milPer_raw` + `milQuan_raw`, `milAdisc_raw`,
   `milCog_raw`, `milDisca_raw`, `milVat_raw`, `milSum_raw` เก็บค่า**ก่อน**หาร split-sale
   ไว้คู่กับคอลัมน์ปกติที่ถูกหารแล้ว — ใช้ตอนต้องการยอดเต็มของบรรทัดนั้น
1. `pre_operations` (เพิ่ม 2026-09-10): `CREATE OR REPLACE TEMP TABLE
   new_data_curated_mil_base` = flat rename ของ `validated_mac5.mil` (window 1 วัน,
   `percent_sale = '100.00%'` hardcode) แล้ว `DELETE` **เอกสารทั้งใบ** ที่อยู่ใน temp ออก
   จากตารางจริงด้วย `company_id + milType + milVnos` (ไม่มี `milListno`) ครอบด้วย
   `when(incremental())` — body เหลือ `SELECT * FROM new_data_curated_mil_base` เท่านั้น
   จึงอ่าน validated รอบเดียวและ MERGE ตกเข้าเงื่อนไข insert
   **เหตุผล**: PK เป็นระดับบรรทัด บรรทัดที่ต้นทางลบไปจะค้างอยู่และถูกนับซ้ำ วัดบน nonprd
   2026-09-10 ได้ **477 แถว / 9.25 ล้านบาท** (ag01 387, ac02 42, ab01 31, ak02 10,
   aa05 7) ตรงกับ `validated_mac5.mil` ที่วัดได้ 476 แถว / 9.25 ล้านบาท
   ดู [validated-layer.md](../validated/validated-layer.md) สำหรับต้นทางของ pattern นี้
2. `post_operations { BEGIN ... END }` คำนวณ **เฉพาะแถว ag01** ใหม่พร้อมแบ่ง split-sale:
   - `filter_mih2`: แปลงเปอร์เซ็นต์ cap ที่ 100
   - `includ_mil`: `CROSS JOIN (SELECT 1 UNION ALL SELECT 2) AS split_sale` **แตกบรรทัด
     เป็นสองเท่า** คูณ `milQuan, milAdisc, milCog, milDisca, milVat, milSum` ด้วย
     `per_sale1/100` หรือ `per_sale2/100` (แบ่งยอดให้พนักงานขายสองคน)
   - `exclude_mil`: บรรทัดที่ไม่แบ่ง คงที่ 100%
   - แล้ว `DELETE` จาก `self()` + `INSERT` จาก temp (upsert มือซ้อนบน incremental merge
     ของ Dataform) · **temp นี้ไม่มี incremental window** — อ่านแถว ag01 ของ
     `validated_mac5.mil` ทั้งหมด ดังนั้น ag01 ถูกปั้นใหม่ทุกรอบ (ค่าใช้จ่ายส่วนใหญ่
     ของไฟล์นี้อยู่ตรงนี้)
   - DELETE เป็น **doc grain** ตั้งแต่ 2026-09-10 (`company_id + milType + milVnos`
     ตัด `milListno` ออก) · ที่ PK grain บรรทัดที่ต้นทางลบไปจะรอดจากการ rebuild เพราะ
     PK ไม่อยู่ใน temp แล้ว · ที่ doc grain เอกสาร ag01 ทั้งใบถูกแทนที่ ล้าง 387 แถวค้าง
     ของ ag01 ได้ในรอบเดียว

### `curated_saleout_mdt` — sell-out modern trade รวมทุกห้าง

รวม 5 แหล่งเป็น grain เดียว `(sale_date, store_code, branch_code, product_code, doc_type)`
ผ่าน `UNION ALL` โดยแต่ละห้างส่งข้อมูลคนละแบบ:

| CTE | ต้นทาง | ลักษณะเฉพาะ |
|---|---|---|
| `hp` | `saleout_hp` | `store_code` = `HP` หรือ `MH` · `NULL` = ไม่ใช่สาขาขายปลีก (CS01/EX99) · `vdartno` เป็นบาร์โค้ด GS1 ใช้จับ `dim_product_master.Barcode` |
| `bt_feed_gap` → `bt_daily` → `bt` | `sale_by_branch_detail` | บุญถาวรส่งเป็นช่วงวัน ต้องเฉลี่ยลงรายวันเอง · `days_covered > 1` ⇒ `date_is_estimated = TRUE` · `branch_code` เป็น**ชื่อไทย** จับคู่ dim ได้ 16/16 · ไม่ส่งบาร์โค้ด |
| `gb` | `saleout_gb` | Global House ใช้บาร์โค้ด 13 หลักเป็นรหัสสินค้าอยู่แล้ว · ส่ง `SALE`/`RETURN` มาเอง · มี `bill_no` ห้างเดียว |
| `tw_dedup` → `tw` | `report_sale_subscription` | ไทวัสดุ · `branch_code` เป็นสตริงเต็ม `60001-CRC Thai Watsadu ...` · ส่งบาร์โค้ดแยกคอลัมน์ · วันขายมาจากต้นทางไม่ได้เดา |
| `lastyear` | `saleout_lastyear` | ไฟล์ Excel ย้อนหลังก่อนที่ TW จะส่ง feed · ไม่มีบาร์โค้ด ไม่มีเลขบิล |

คอลัมน์ธง 3 ตัวที่ทุก CTE ต้องเติม: `doc_type_source` (`DERIVED` = เราอนุมานเอง),
`days_covered`, `date_is_estimated` — ใช้แยกยอดที่เชื่อวันได้กับยอดที่เฉลี่ยมา

### `curated_stock_mdt` — สต็อกคงเหลือรายสาขา

`type: "table"` ปั้นใหม่ทั้งก้อนทุกวัน (tag `curated_full`) partition `stock_date`

- `bt` จาก `stock_by_branch`: วันสต็อกอยู่ที่ `end_date` · 163 จาก 167 วันส่งมาครั้งเดียว
  อีก 4 วันส่งซ้ำ 2 ไฟล์ จึงเลือกไฟล์ล่าสุดต่อ (สาขา, สินค้า, วันสต็อก)
- `onhand_amt` ของ BT เป็น **ต้นทุน ไม่ใช่ราคาขาย** · BT ไม่ส่ง `onorder_qty`
- อีกแหล่งมาจาก `report_sale_subscription` (ไทวัสดุ)

### `curated_product` — แคตตาล็อกสินค้า

- dedup ต่อ `prdSku` ด้วย `prdUpdatedDate DESC`
- `post_operations` UPDATE แกะ JSON จาก `product_detail`:
  `JSON_QUERY_ARRAY(prdDiminsionData, '$.dimFeild')` และ `'$.SpeciFeild'` —
  จับ label `'ขนาด'/'size'` และ `'สี'/'color'`
  (`prdDiminsionData` เป็น **load-bearing typo** ของต้นทาง ห้ามแก้)
- แยกสีไทย/อังกฤษด้วยช่วงอักขระไทย `r'[ก-๙]'` → `prdColorTH` / `prdColorEN`

### `product_for_aisearch` — feed สำหรับ AI search

- `type: operations`: TEMP TABLE → `DELETE WHERE asatdate = run_date` → `INSERT`
- สร้างคอลัมน์ `STRUCT` ชื่อ `structData` join `product_detail`, `brand`, `category`,
  `vendor` และ `unit` **ห้าครั้ง** (กว้าง/ยาว/สูง/น้ำหนักสุทธิ/น้ำหนักรวม)
- `product_status = 'Approve'` เมื่อ `prdIsActive AND prdIsUse AND pd_is_system`

## กฎเวลาเพิ่มตาราง curated

1. ขึ้นกับ `curated_schema_<source>` ของ source นั้น (ไม่ต้องขึ้นกับตาราง validated ตรง ๆ
   เพราะดึงผ่าน `${ref()}` อยู่แล้ว)
2. `type: "incremental"` + `uniqueKey` ที่มี `company_id` สำหรับ MAC5
3. partition ด้วย `asatdate` (หรือคอลัมน์วันที่เชิงธุรกิจอย่าง `sale_date`/`stock_date`
   ถ้าเป็นชุดที่ปั้นใหม่ทั้งก้อน) · cluster ไม่เกิน 4 คอลัมน์ที่ใช้กรองจริง
4. window แบบ inline `when(incremental(), ...)` เวลาไทย · **วางเงื่อนไข `asatdate`
   ไว้ใน CTE ต้นทาง ไม่ใช่ชั้นนอก** ไม่งั้นไม่ตัดพาร์ทิชัน
5. ถ้า PK เป็นระดับบรรทัด ให้ทำ **doc-grain purge** ใน `pre_operations` ตามแบบ
   `curated_mil` — ไม่งั้นบรรทัดที่ต้นทางลบจะค้าง
6. การจัดสรรยอดซับซ้อน (split, คำนวณใหม่) ไปอยู่ใน `post_operations { BEGIN...END }`
   เป็น DELETE+INSERT บน `self()`
