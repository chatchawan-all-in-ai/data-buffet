# Curated Layer — `definitions/curated/`

> **LLM context**: 8 files — 3 are schema-bootstrap `operations` (one per source),
> 5 are real transformations. Dataset per source: `curated_mac5`, `curated_mastersku`,
> `curated_cis360`. All tag with `databuffet.TAG_CURATED` only (the
> `curated_incremental`/`curated_full` tags exist in variables.json but are **not used**).

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
   as DELETE+INSERT on `self()`.
