# How-to: เพิ่มตาราง Curated

## ขั้นตอน

### 1. ระบุ dependency

ต้นทางคือตาราง validated (อ่านผ่าน `${ref(databuffet.VALIDATED_MAC5, "mih")}` —
Dataform จัด dependency ให้เอง) ส่วน `dependencies` ใน config ใส่แค่
`curated_schema_<source>`

### 2. สร้าง `definitions/curated/<source>/curated_<name>.sqlx`

```javascript
config {
    type: "incremental",
    schema: databuffet.CURATED_MAC5,
    dependencies: ["curated_schema_mac5"],
    tags: [databuffet.TAG_CURATED],
    uniqueKey: ["company_id", "mihType", "mihVnos"],
    bigquery: {
        partitionBy: "asatdate",
        clusterBy: ["company_id", "mihVnos", "mihType"],
    },
}
```

### 3. เขียน logic

- Rename คอลัมน์ validated (snake/lower) → **camelCase**
- Business logic ที่ทำในชั้นนี้: status lookup (join ar_s/ap_s), แปลง percent string,
  JSON parsing, dedup revision ล่าสุด
- Incremental window แบบ inline (มาตรฐานจริงของชั้นนี้คือ **1 วัน**):
  ```sql
  ${when(incremental(), `AND asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`)}
  ```

### 4. Logic ซับซ้อนหลัง load → post_operations

ถ้าต้อง reallocate/แก้ค่าเป็นกลุ่ม (เช่น split-sale ของ ag01 ใน `curated_mil`)
ใช้ block รูปแบบนี้:

```sql
post_operations {
  BEGIN
    CREATE TEMP TABLE new_data AS ( ...CTE คำนวณ... );
    DELETE FROM ${self()} WHERE <PK> IN (SELECT <PK> FROM new_data);
    INSERT INTO ${self()} SELECT * FROM new_data;
  END
}
```

### 5. ถ้า PK เป็นระดับบรรทัด → ต้องมี doc-grain purge (`pre_operations`)

MERGE บน `uniqueKey` ระดับบรรทัดจะ **ลบบรรทัดที่ต้นทางลบไปแล้วไม่ได้เลย** —
บรรทัดเก่าค้างในตารางตลอดไป (วัดจริงบน `mil` ฝั่ง validated: ค้าง 476 แถว / 9.2 ล้านบาท)

ถ้า `uniqueKey` ของตารางใหม่มี `listno`/`seq`/เลขบรรทัด ให้ทำแบบ `curated_mil`:

โครงจริงจาก `curated_mil.sqlx` (บรรทัด 15–98):

```sql
pre_operations {
  CREATE OR REPLACE TEMP TABLE new_data_curated_mil_base AS
  SELECT ...          -- ทั้ง SELECT ที่ clean แล้ว รวม window incremental
  ${ when(incremental(), `AND asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`) }
  ;

  ${ when(incremental(), `
  DELETE FROM ${self()} AS t
  WHERE EXISTS (
    SELECT 1 FROM new_data_curated_mil_base AS b
    WHERE b.company_id = t.company_id
      AND IFNULL(b.milType, '') = IFNULL(t.milType, '')
      AND IFNULL(b.milVnos, '') = IFNULL(t.milVnos, '')
  );`) }
}
```

แล้ว body เหลือแค่ `SELECT * FROM new_data_curated_mil_base` — MERGE จะเข้า branch INSERT

> ใช้ `EXISTS` + `IFNULL(...)` ทีละคอลัมน์ ไม่ใช่ tuple `IN` — เพื่อให้ NULL จับคู่ได้

กฎสำคัญ:
- **อ่าน raw ครั้งเดียว** — อย่าวน query ต้นทางซ้ำเพื่อเก็บ doc key
- `config` **ไม่ต้องเปลี่ยน** — `type`/`uniqueKey` เดิมทั้งหมด
- doc key = คีย์ระดับ**เอกสาร** (`company_id` + type + vnos) **ไม่ใส่** เลขบรรทัด
- ห้ามทำถ้า PK มีวันที่/ลูกค้าอยู่ด้วย (เคส `mie` — จะลบแถวที่ถูกต้องทิ้ง 67,946 แถว)
- `curated_mih` **ไม่ต้องทำ** — `uniqueKey` ของมันเป็นคีย์เอกสารอยู่แล้ว

รายละเอียด + ตัวเลขที่วัดได้: [project_wiki/validated/validated-layer.md](../project_wiki/validated/validated-layer.md)

## ตัวอย่างจริงที่ควรอ่านก่อนเขียน

- `curated/mac5/curated_mih.sqlx` — status lookup + UNION แยกบริษัท
- `curated/mac5/curated_mil.sqlx` — ซับซ้อนสุด: `pre_operations` doc-grain purge (§5)
  + `post_operations` split-sale ของ ag01
- `curated/mastersku/curated_product.sqlx` — JSON parsing + Thai/English color split
  (ตารางเดียวที่ใช้ `updatePartitionFilter` 7 วัน)

## Checklist

- [ ] `type: "incremental"` + `uniqueKey` มี `company_id` (mac5)
- [ ] partition `asatdate`, cluster ≤ 4 คอลัมน์
- [ ] อ่านต้นทางผ่าน `ref()` — ไม่ hardcode
- [ ] window `when(incremental(), ...)` Bangkok time
- [ ] คอลัมน์ output เป็น camelCase
- [ ] logic กลุ่ม/ซับซ้อนอยู่ใน post_operations ไม่ปนกับ SELECT หลัก
- [ ] ถ้า `uniqueKey` เป็นระดับบรรทัด → มี doc-grain purge ใน `pre_operations` (§5)
- [ ] comment สั้น 1 บรรทัด บอก "ทำไม" — รายละเอียดไปไว้ใน `document/` ([coding-standard §9](../coding-standards/sqlx-coding-standard.md))
