# How-to: เพิ่มตาราง Validated

## ก่อนเริ่ม ตัดสินใจ 2 อย่าง

1. **Load pattern** — ดูลักษณะข้อมูล:
   - **Incremental**: transactional, ข้อมูลใหม่มาทุกวันตาม `ASATDATE` (เช่น mih, mil)
   - **Full** (`type: "table"`): reference/master ขนาดเล็ก rebuild ทั้งก้อนได้ (เช่น ap_s, grp)
2. **Primary key** — คอลัมน์อะไรระบุ row ได้ 1 เดียว (ใช้ dedup + uniqueKey)

## ขั้นตอน

### 1. ตรวจ external table ใน initial

ตาราง raw ต้องมีใน `definitions/initial/<source>/create_all_table_raw_<source>.sqlx`
ถ้ายังไม่มี ให้เพิ่ม (เลือก section INCREMENT = hive-partitioned หรือ FULL = glob ตรง)
แล้วรัน **เฉพาะ action `create_all_table_raw_<source>` ตัวเดียว โดยไม่ติ๊ก "include dependencies"**

> ⚠️ **ห้ามรัน tag `initial` ทั้ง tag** — tag นี้รวมไฟล์ `drop_all_tables_validated_<source>`
> ด้วย จึง **ลบตาราง validated** ของ cis360, mastersku, master_sku, saleout_mdt,
> allkons_commission และ d365 (ขอบเขตดู [initial file map](../project_wiki/initial/initial-layer.md#file-map) · ข้อมูลหายจนกว่าจะรันสร้างใหม่)
> และถ้าติ๊ก "include dependencies" ตอนรัน `create_all_table_raw_<source>` จะดึงไฟล์ drop
> ของ source นั้นมารันด้วย (ของ mac5 คือ drop ใน tag `re-initial` ซึ่งลบทั้ง validated และ curated ของ MAC5)

### 2. สร้างไฟล์ `definitions/validated/<source>/<table>.sqlx`

**ชื่อไฟล์ = ชื่อตาราง raw** (js block ใช้ `name()` อ้างกลับ)
copy จากไฟล์อ้างอิงที่ใกล้เคียง:
- single-source incremental → `validated/cis360/customer_profile.sqlx`
- multi-company (mac5) → `validated/mac5/mih.sqlx`
- full-load → `validated/mac5/grp.sqlx`

### 3. แก้จุดเหล่านี้

```javascript
config {
    type: "incremental",                      // หรือ "table" สำหรับ full
    schema: databuffet.VALIDATED_<SOURCE>,
    dependencies: ["validated_schema_<source>", "create_all_table_raw_<source>"],
    tags: [databuffet.TAG_VALIDATED, databuffet.TAG_VALIDATED_INCREMENTAL],  // หรือ _FULL
    uniqueKey: ["id"],                        // PK ที่ตัดสินใจไว้
    bigquery: { partitionBy: "asatdate", clusterBy: ["id"] },  // full-load มักไม่ partition
}
```

- ใน js: `pk_key = [...]` **ให้ตรงกับ `uniqueKey`** (นิยาม 2 ที่เสมอ)
- ถ้าตารางใหม่เป็น **เอกสารหลายบรรทัด** (PK ลงท้ายด้วย `listno`/`seq`) ให้พิจารณาเพิ่ม
  TEMP table + DELETE ราย document ใน `pre_operations` (config ไม่เปลี่ยน) — MERGE
  เฉย ๆ ลบบรรทัดที่ต้นทางลบไปไม่ได้ ดูวิธีและเงื่อนไขที่
  `document/project_wiki/validated/validated-layer.md` (ใช้อยู่ใน `mih`/`mil`/`mir`)
  **แต่ต้องเช็กก่อนว่า batch รายวันส่งบรรทัดมาครบทั้งใบ**
- SELECT: cast ทุกคอลัมน์ด้วย helper (`cleanString` / `castInt64` /
  `parseFlexibleDatetime` / `parseAsatDate()` สำหรับ `asatdate`)
- incremental window (เฉพาะ incremental):
  ```sql
  ${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY))`) }
  ```
- ปิดท้ายด้วย `${partition_statement}` (QUALIFY dedup)

### 4. กรณี multi-company (mac5)

- UNION ALL ครบ 5 บริษัท ใส่ literal `company_id` เป็นคอลัมน์แรก
- `company_id` นำหน้า `uniqueKey`/`clusterBy`
- dependencies เพิ่ม `create_all_table_raw_mac5_{aa05,ab01,ac02,ak02}`
- บริษัทอื่นนอกจาก ag01 ที่ไม่มี `ModDate`: `CAST(NULL AS DATETIME) AS moddate`

### 5. ตรวจและรัน

ตรวจ compile/SQL ตาม [README — Common Commands](../../README.md#common-commands)
แล้วเลือก action `validated_<source>.<table>` ตาม [คู่มือรันงาน](run-and-debug.md#รันด้วย-tag)

## Checklist

- [ ] ชื่อไฟล์ = ชื่อตาราง raw
- [ ] `uniqueKey` == `pk_key`
- [ ] ทุกคอลัมน์ผ่าน helper ไม่มี cast ดิบ
- [ ] `asatdate` มาจาก `parseAsatDate()`
- [ ] tag ตรงกับ load pattern
- [ ] QUALIFY dedup อยู่ท้าย SELECT
- [ ] post_operations PK ครอบด้วย `when(!incremental(), ...)`
- [ ] comment สั้น 1 บรรทัด บอก "ทำไม" — รายละเอียดไปไว้ใน `document/` ([coding-standard §9](../coding-standards/sqlx-coding-standard.md))
