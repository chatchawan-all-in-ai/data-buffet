# Curated Layer — `definitions/curated/`

> **LLM context**: schema-bootstrap `operations` (source ละตัว) และ transformation ·
> dataset ต่อ source: `curated_mac5`, `curated_mastersku`,
> `curated_master_sku`, `curated_saleout_mdt` (`curated_cis360` สร้าง schema ไว้แล้วแต่ยังไม่มีตาราง)
> จำนวนไฟล์ปัจจุบันดู [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview)

## Inventory

| File | Target | Type | uniqueKey | Partition / Cluster | Tags |
|---|---|---|---|---|---|
| `mac5/curated_schema_mac5.sqlx` | schema `curated_mac5` | operations | — | — | `curated` |
| `mac5/curated_mih.sqlx` | `curated_mac5.curated_mih` | incremental | `company_id, mihType, mihVnos` | `asatdate` / `company_id, mihVnos, mihType` | `curated` |
| `mac5/curated_mil.sqlx` | `curated_mac5.curated_mil` | incremental | `company_id, milType, milVnos, milListno` | `asatdate` / `company_id, milVnos, milType` | `curated` |
| `mac5/curated_tbook_quotation.sqlx` | `curated_mac5.curated_tbook_quotation` | incremental | `company_id, running` | (partition comment ไว้) | `curated` |
| `mastersku/curated_schema_mastersku.sqlx` | schema `curated_mastersku` | operations | — | — | `curated` |
| `mastersku/curated_product.sqlx` | `curated_mastersku.curated_product` | incremental | `prdSku` | `asatdate` / `prdSku, prdUniversalBarcode, prdVendorId, prdBrandId` | `curated` |
| `mastersku/product_for_aisearch.sqlx` | `curated_mastersku.product_for_aisearch` | operations | — | — | `curated` |
| `master_sku/curated_schema_master_sku.sqlx` | schema `curated_master_sku` | operations | — | — | `curated` |
| `master_sku/product_for_aisearch_v3.sqlx` | `curated_master_sku.product_for_aisearch_v3` | operations | — | `asatdate` / `id` | `curated` |
| `master_sku/curated_products.sqlx` | `curated_master_sku.curated_products` | **table** | — | `asatdate` / `prdSku, prdUniversalBarcode, prdVendorId, prdBrandId` | `curated` |
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

### `product_for_aisearch_v3` — feed AI search จาก master_sku (shadow)

- **shadow table** ข้าง `product_for_aisearch` เดิม — ยังไม่มีผู้อ่าน ตัวเดิมยังอ่าน
  `mastersku` อยู่ (การสลับผู้อ่านเป็นงานแยก ยังไม่ตัดสินใจ)
- output เหมือนตัวเดิมทุกคอลัมน์ (`asatdate`, `id`, `structData` field ชื่อ/ชนิดเดิม)
  เพราะ AI search อ่านรูปแบบนี้ · partition `asatdate` / cluster `id`
- อ่าน `validated_master_sku` ตรง ๆ (ไม่มี curated_product คั่น) — `products` +
  `brands`, `categories`, `brand_vendors` (→ `vendors`, brand สำรอง) และ `common_codes` ×4
- `operations`: TEMP TABLE → `CREATE TABLE IF NOT EXISTS` (นอก transaction) →
  `BEGIN TRANSACTION` → `DELETE WHERE asatdate = run_date` → `INSERT` → `COMMIT TRANSACTION`
  · DELETE+INSERT เป็น atomic: ถ้า INSERT ล้มเหลว partition เดิมยังอยู่
- **Required deploy step**: Drop the draft-built `curated_master_sku.product_for_aisearch_v3` table before the first run so the new code performs a full load.
- **window**: `window_start = MAX(asatdate) - 1` ของ target เฉพาะ `asatdate < run_date`
  - target ไม่มี / ว่าง / มีแค่ partition วันนี้ → `window_start` NULL = **ส่งทั้ง catalog**
  - คืนที่รันพลาดไม่หาย (เริ่มจากรอบก่อนหน้าจริง ไม่ใช่ `run_date-1`) · รันซ้ำวันเดียวกันใช้ window เดิม
    และแทนที่เฉพาะ partition วันนี้ โดยเก็บ partition ก่อนหน้าไว้
  - ส่ง id เมื่อ `asatdate >= window_start` ของแถว `products` ที่เลือก หรือ lookup ที่ join กับแถวนั้น:
    `brands` (ทั้ง brand ตรงและ brand สำรองผ่าน `brand_vendors`), `brand_vendors`, `vendors`,
    `categories`, `common_codes` ทั้ง `sales_unit`, `package_unit`, `weight_unit`, `volume_unit`
    (เปลี่ยนชื่อ brand หรือหน่วยโดยไม่แก้สินค้าก็ส่งใหม่)
  - ส่งสินค้าที่หน่วยขายเป็น `ชิ้น` และท้ายชื่อเป็นคำใน `unit_vocab` ด้วย เมื่อแถวต้นทางของคำนั้น
    (`products` ที่มี variant `หน่วยขาย` หรือ `common_codes` ประเภทหน่วยทั้ง 5) มี `asatdate >= window_start`
- ตัด placeholder ที่ไม่มี `master_sku_code` · เลือก 1 แถวล่าสุดต่อ `master_sku_code`
  ด้วย `QUALIFY ROW_NUMBER() ... ORDER BY updated_at DESC` **ก่อน** join และกรอง window
  เพื่อไม่ให้ lookup ของแถวเก่าทำให้ส่งสินค้าซ้ำ SKU ที่ไม่ใช่แถวล่าสุด
- mapping ที่ต่างจากการ copy ตรง ๆ:

| field | มาจาก | เหตุผล |
|---|---|---|
| `product_shape` | `package_shape` | `pd_shape` เดิมคือรูปทรงบรรจุภัณฑ์ · `products.shape` ว่างทุกแถว |
| `product_dimensions_json` | `{"dimFeild":[{label,value}]}` จาก `specification_attributes` (ตัด `id`) | `specification_attributes` คือค่า variant = `prdDiminsionData` เดิม · label เป็นไทย (`ขนาด`, `สี`, `โมเดล`) |
| `special_specifications_json` | `'{"SpeciFeild":[]}'` คงที่ | master_sku ไม่มีข้อมูลแบบ `pd_spacific_fields` เดิม |
| หน่วย ×5 | `LOWER(common_codes.code)` (`IN` → `inch`) เฉพาะเมื่อมีค่า · น้ำหนัก = `COALESCE(weight_unit.code, volume_unit.code)` | ตัวเดิมส่งรหัสตัวเล็ก `mm/cm/m/inch/ft`, `kg/g`, `l/ml` · master_sku มีหน่วยเดียวต่อกลุ่ม (กว้าง/ยาว/สูง ใช้ `length_package_unit_id`, น้ำหนักทั้งสองใช้ `weight_unit_id` สำรองด้วย `volume_unit_id` สำหรับของเหลว: net +401 / gross +369 แถว) · **ไม่ใช้ `NULLIF(…, 0)`** กับค่าขนาด/น้ำหนัก เพราะตัวเดิมก็ส่ง `0` |
| `brand_name` | `COALESCE(brands[brand_id], brands[brand_vendors.brand_id])` | 52 สินค้าไม่มี `brand_id` |
| `product_tags_json` | `{"mypro_tag":[…]}` ไม่มี tag = `{"mypro_tag":[]}` | ตัวเดิมไม่เคยส่ง NULL |
| `product_model` | `COALESCE(model, variant 'โมเดล', variant 'รุ่นสินค้า')` (ค่าแรกที่ไม่ว่าง) | ~17k สินค้าเก็บ model ไว้ใน variant อย่างเดียว |
| `product_material` | `COALESCE(material, variant 'วัสดุ')` ตัด `โปรดระบุ` / `-` / `0` | ได้ค่าเพิ่ม 245 แถว ไม่มีแถวไหนแย่ลง |
| `product_description` | `detail` แต่เป็น NULL ถ้าเป็นแค่รหัส (`^[A-Za-z0-9#_./-]{4,40}$`) | ~6k แถวมีแค่รหัสสินค้า ไม่ใช่รายละเอียด |
| `product_status` | `Approve` เมื่อ `product_status = 'Active' AND sales_status = 'Active'` | ไม่มี `pd_is_system` แล้ว |
| `sales_unit` | `common_codes[uom_sales_id].name` · ถ้าเป็นค่า default `ชิ้น` ใช้หน่วยท้ายชื่อ `… (แผ่น)` (เฉพาะคำที่อยู่ใน `unit_vocab`) ก่อน variant `หน่วยขาย` ค่าแรกที่ไม่ว่างตามลำดับ array แล้วจึง `ชิ้น` | ค่าใน common_codes normalize แล้ว (`ชิ้น`, `ชุด`) · ตรงกับตัวเดิม 17.3% → 23.8% · `unit_vocab` = ค่า `หน่วยขาย` ที่ผ่าน `cleanString` และไม่ว่างจากทุก attribute ของทุกแถว `validated_master_sku.products` (รวมแถวซ้ำ SKU และค่า attribute ถัดไป) + ชื่อที่ไม่เป็น NULL จาก common_codes ประเภท `sales-unit`, `uom-general`, `uom-volume`, `uom-weight`, `uom-length` (กันคำที่ไม่ใช่หน่วย เช่น `Day Light`) |

- เทียบตัวเดิม (แถวล่าสุดต่อ id, 101,849 id ที่ตรงกัน, 2026-10-12): `structData` เหมือนกันทุก field = 0 id
  — ต่างเพราะ source เปลี่ยน (ชื่อสินค้า, หน่วยขาย, รายละเอียด, ตัวพิมพ์ brand) ดูก่อนสลับผู้อ่าน

### `curated_products` — แคตตาล็อกสินค้าจาก master_sku

- ตารางใหม่ข้าง `curated_mastersku.curated_product` เดิม (ไม่แตะของเดิม) · 50 คอลัมน์ชื่อ/ลำดับเดียวกับตัวเดิม
- `type: "table"` rebuild ทุกวัน (~101.9k แถว) — 1 แถวต่อ `master_sku_code` ไม่มีปัญหา sku ซ้ำแบบ MERGE
  ที่ใช้ `updatePartitionFilter` 7 วันของตัวเดิม · `asatdate` = `products.asatdate` ของแถวที่เลือก
- อ่าน `products` (ตัด placeholder ที่ไม่มี `master_sku_code`), `brand_vendors` (vendor, brand สำรอง),
  `common_codes` (หน่วยขาย, รูปแบบ barcode) · CTE `spec` เลือกค่า variant แรกที่ไม่ว่างตามลำดับ array
  ของสินค้าที่เลือก ส่วน `unit_vocab` ใช้ทุก attribute ของทุกแถวตามนิยามใน mapping `sales_unit` ด้านบน
- mapping ที่ไม่ตรงไปตรงมา:
  - `prdSaleUnite` ใช้กฎและนิยาม `unit_vocab` เดียวกับ mapping `sales_unit` ของ v3 ด้านบน
  - `prdSize` = variant `ขนาด`/`size` สำรองด้วย `d365_size` ที่ตัด 0 นำหน้า (`01000L` → `1000L`)
  - `prdColorTH` / `prdColorEN` แยกจาก variant `สี`/`color` ด้วยช่วงอักขระไทยเท่านั้น · **ไม่ใช้ fallback `color_descriptor_id`**
    (captain ตัดสิน 2026-10-12: ได้ค่ากลับมา 626 แถว แต่ ~165 แถวเป็นสีอื่นจริง)
  - `prdModel` = `COALESCE(model, variant 'โมเดล', variant 'รุ่นสินค้า')`
  - `prdBrandId` = id ชุดใหม่ของ master_sku (ไม่ใช่ id ของ `mastersku` เดิม) — ผู้อ่าน join `validated_master_sku.brands`
  - `prdUpdatedDate`: เมื่อ `updated_at < '2000-01-02'` ใช้
    `COALESCE(product_status_date, sales_status_date, updated_at)` แทนค่า placeholder
  - `prdPsId` = id คงที่ของ lookup เดิม `On`/`Off` ตาม `product_status`
  - `prdBarcodeFormat`: `EAN13` → `GTIN-13 / EAN-13` ให้ตรงชื่อเดิม
  - เวลาเป็นเวลาไทย (ตัวเดิมเป็น UTC)
  - คอลัมน์ที่ master_sku ไม่มี (`prdPasId`, `prdIdSource`, `prdRefMpId`, combo ฯลฯ) เป็น NULL

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
