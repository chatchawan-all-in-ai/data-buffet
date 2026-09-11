# Curated Layer — `definitions/curated/`

> **LLM context**: 10 files — 4 are schema-bootstrap `operations` (one per source),
> 6 are real transformations. Dataset per source: `curated_mac5`, `curated_mastersku`,
> `curated_cis360`, `curated_saleout_mdt`. Most tag with `databuffet.TAG_CURATED` only;
> `curated_saleout_mdt` also uses `TAG_CURATED_INCREMENTAL` (first user of that tag,
> 2026-09-07). `curated_full` still unused.

## Inventory

| File | Target | Type | uniqueKey | Partition / Cluster | Notes |
|---|---|---|---|---|---|
| `mac5/curated_schema_mac5.sqlx` | schema `curated_mac5` | operations | — | — | `CREATE SCHEMA IF NOT EXISTS` |
| `mac5/curated_mih.sqlx` | `curated_mac5.curated_mih` | incremental | `company_id, mihType, mihVnos` | `asatdate` / `company_id, mihVnos, mihType` | Invoice headers + status lookup |
| `mac5/curated_mil.sqlx` | `curated_mac5.curated_mil` | incremental | `company_id, milType, milVnos, milListno` | `asatdate` / `company_id, milVnos, milType` | Invoice lines + **post_operations split-sale**; 68 คอลัมน์ รวม `_raw` 7 ตัว; **doc-grain purge ทั้ง pre + post (2026-09-10)** |
| `mac5/curated_tbook_quotation.sqlx` | `curated_mac5.curated_tbook_quotation` | incremental | `company_id, running` | (partition commented out) | Latest quotation revision (`ORDER BY rev DESC`) |
| `mastersku/curated_schema_mastersku.sqlx` | schema `curated_mastersku` | operations | — | — | |
| `mastersku/curated_product.sqlx` | `curated_mastersku.curated_product` | incremental | `prdSku` | `asatdate` / `prdSku, prdUniversalBarcode, prdVendorId, prdBrandId` | Only file using `updatePartitionFilter` (7-day) |
| `mastersku/product_for_aisearch.sqlx` | `curated_mastersku.product_for_aisearch` | operations | — | — | AI-search feed, STRUCT column, DELETE+INSERT by run_date |
| `cis360/curated_schema_cis360.sqlx` | schema `curated_cis360` | operations | — | — | Schema only, no tables yet |
| `saleout_mdt/curated_schema_saleout.sqlx` | schema `curated_saleout_mdt` | operations | — | — | เพิ่ม 2026-09-07 |
| `saleout_mdt/curated_saleout_mdt.sqlx` | `curated_saleout_mdt.curated_saleout_mdt` | incremental | `sale_date, store_code, branch_code, product_code` | `sale_date` / `store_code, branch_code, product_code` | **ชั้นที่ทำให้ทุกห้างหน้าตาเหมือนกัน** — เพิ่มห้างใหม่ = เพิ่ม UNION ALL block ไม่ต้องแตะ fact/view · ตอนนี้มี HomePro + Megahome + บุญถาวร · ตัวกรอง incremental อยู่ใน CTE เพื่อตัดพาร์ทิชันของ validated — **ยกเว้นบล็อก BT ที่ห้ามกรอง** (ดูหัวข้อ MTD differencing) |

## Incremental window — IMPORTANT

MAC5 curated tables use an inline **1-day** window, not `updatePartitionFilter`:

```sql
${when(incremental(), `AND asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`)}
```

Only `curated_product` uses `updatePartitionFilter: "asatdate >= CURRENT_DATE('Asia/Bangkok')-7"`.

## Business logic per table

### `curated_mih` — Master Invoice Headers

> No doc-grain purge needed: `uniqueKey` = `company_id, mihType, mihVnos` **is** the
> document key, so the MERGE already replaces the whole document. Verified 2026-09-10:
> 3,903,023 rows / 3,903,023 documents, **0 stale rows**.

- Renames ~90 snake_case columns from `validated_mac5.mih` to camelCase.
- Status description lookup: sales types (`QS,PS,IS,AS,BS,VS,RS`) → `ar_s.ar_snamet`;
  purchase types (`QP,PP,IP,AP,BP,VP,RP`) → `ap_s.ap_snamet` → `mihstatus_desc`.
- Split-sale percentages from `mih2` (percent strings parsed with
  `REGEXP_REPLACE(..., r'[^0-9.%]', '')`), applied **only to company `ag01`**;
  other companies pass through with defaults (`100.00%` / `0.00%`) via `UNION ALL`.

### `curated_mil` — Master Invoice Lines (most complex)
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
   ดู `document/project_wiki/validated/validated-layer.md` สำหรับต้นทางของ pattern นี้
2. `post_operations { BEGIN ... END }` recomputes **ag01 rows only** with split-sale
   allocation:
   - `filter_mih2`: parse split percentages, cap at 100.
   - `includ_mil`: `CROSS JOIN (SELECT 1 UNION ALL SELECT 2) AS split_sale` **doubles**
     each split line, multiplying `milQuan, milAdisc, milCog, milDisca, milVat, milSum`
     by `per_sale1/100` or `per_sale2/100` (two-salesperson revenue split).
   - `exclude_mil`: non-split lines at 100%.
   - Then `DELETE` from `self()` + `INSERT` from the temp table (manual upsert layered
     on Dataform's incremental merge). **This temp has NO incremental window** — it
     reads every ag01 row of `validated_mac5.mil`, so ag01 is fully rebuilt every run
     (that is where most of this file's cost sits).
   - The DELETE is **doc grain** since 2026-09-10 (`company_id + milType + milVnos`,
     `milListno` dropped). At PK grain a line deleted at source survived the rebuild
     because its PK was no longer in the temp; at doc grain the whole ag01 document is
     replaced, clearing all 387 stale ag01 rows in one run.

### `curated_saleout_mdt` — ทำให้ 6 ห้างหน้าตาเหมือนกัน

14 คอลัมน์คงที่ · เพิ่มห้าง = เพิ่ม CTE + `UNION ALL` ไม่ต้องแตะ `fact_saleout_mdt` เลย
ลำดับคอลัมน์ของทุกบล็อกต้องตรงกันเป๊ะ เพราะ `UNION ALL` จับตามตำแหน่ง ไม่ใช่ชื่อ

| ห้าง | บล็อก | รูปแบบต้นทาง | แถว | ยอด |
|---|---|---|---:|---:|
| HomePro + Megahome | `hp` | ยอดของวัน ใช้ได้ตรง ๆ | 24,790 | 167,978,976 |
| บุญถาวร | `bt_feed_gap` → `bt_daily` → `bt` | ยอดสะสม MTD ต้องหาส่วนต่าง | 1,343 | 15,555,025 |

#### MTD differencing (บุญถาวร) — รูปแบบใหม่ 2026-09-11

ต้นทางส่ง **ยอดสะสมตั้งแต่ต้นเดือน** มาใหม่ทุกวัน การขาย 1 ครั้งถูกส่งซ้ำจนสิ้นเดือน
(วัด: 12,756 แถว มีการขายจริง 1,370) `SUM` ตรง ๆ จะได้ 156.2 ล้าน แทนที่จะเป็น 15.6 ล้าน

```sql
net_inc_tax_mtd - IFNULL(LAG(net_inc_tax_mtd) OVER w, 0) AS sale_amount
WINDOW w AS (
  PARTITION BY branch, article_id, distribution_channel, DATE_TRUNC(end_date, MONTH)
  ORDER BY end_date
)
```

ข้อบังคับ 3 ข้อ — พลาดข้อใดข้อหนึ่งยอดเพี้ยนแบบเงียบ ๆ

1. **ห้ามใส่ `when(incremental(), ...)` ในบล็อกนี้** — `LAG` ต้องเห็นแถวของวันก่อนหน้า
   ถ้าอ่านแค่ 1 วัน แถวแรกจะไม่มี `LAG` แล้วยอดสะสมทั้งเดือนถูกนับเป็นยอดวันเดียว
   ต้นทาง 0.3 MB จึงอ่านทั้งก้อนทุกคืน · ถ้าโตเกินหลักล้านแถว ให้ย้อน **2 เดือนปฏิทิน**
   (เดือนเต็ม ไม่ใช่ N วัน เพราะการรีเซ็ตผูกกับต้นเดือน)
2. **`distribution_channel` ต้องอยู่ใน `PARTITION BY`** ไม่งั้นยอด Showroom กับ Anyhome
   ไปลบกันเอง
3. **`DATE_TRUNC(end_date, MONTH)` ต้องอยู่ใน `PARTITION BY`** ไม่งั้นเดือนใหม่ไปลบกับเดือนเก่า

`days_covered` วัดจาก **ช่วงห่างของ snapshot ที่ห้างส่งมาจริง** ไม่ใช่ช่วงห่างในกลุ่มสินค้า
เพราะสินค้าโผล่ในไฟล์ครั้งแรกก็ตอนที่มันขายแล้ว (MTD = 0 ไม่ถูกส่งมา)
วัดได้: ห่าง 1 วัน 149 ครั้ง · 2 วัน 11 ครั้ง · 3 วัน 1 ครั้ง · 10 วัน 1 ครั้ง (ไฟล์แรก ก.พ.)
· 18 วัน 1 ครั้ง (ไฟล์แรก มี.ค.) → `date_is_estimated = TRUE` 339 แถว / 4,275,921 บาท (27%)

ช่องทางถูกยุบรวมเพราะเกรนของ curated ไม่มีช่องทาง — 27 จาก 1,343 กลุ่มมี 2 ช่องทาง
คิดเป็นเงิน 395,197 ยอดรวมไม่เปลี่ยน

### `curated_product` — Product catalog
- Dedup per `prdSku` by `prdUpdatedDate DESC`.
- `post_operations` UPDATE parses JSON from `product_detail`:
  `JSON_QUERY_ARRAY(prdDiminsionData, '$.dimFeild')` and `'$.SpeciFeild'` —
  matches labels `'ขนาด'/'size'` and `'สี'/'color'`.
- Thai/English color split via Thai character range regex `r'[ก-๙]'` →
  `prdColorTH` / `prdColorEN`.

### `product_for_aisearch` — AI search feed
- `type: operations`: TEMP TABLE → `DELETE WHERE asatdate = run_date` → `INSERT`.
- Builds one `STRUCT` column `structData` joining product_detail, brand, category,
  vendor, and `unit` **five times** (width/length/height/net-weight/gross-weight).
- `product_status = 'Approve'` when `prdIsActive AND prdIsUse AND pd_is_system`.

## Rules when adding a curated table

1. Depend on the source's `curated_schema_<source>` action (not on validated tables
   directly — those are picked up via `${ref()}`).
2. `type: "incremental"` + `uniqueKey` including `company_id` for MAC5.
3. Partition by `asatdate`, cluster on ≤4 filter columns.
4. Inline `when(incremental(), ...)` Bangkok-time window.
5. Complex reallocation (split, re-derivation) goes in `post_operations { BEGIN...END }`
6. ถ้าต้นทางส่ง **ยอดสะสม** (MTD / running total) ห้ามใช้หน้าต่าง incremental รายวัน —
   ฟังก์ชัน `LAG` ต้องมองเห็นประวัติ อ่านทั้งก้อนหรือย้อนเป็นเดือนเต็ม
   (ตัวอย่าง: บล็อก `bt` ใน `curated_saleout_mdt`)
   as DELETE+INSERT on `self()`.
