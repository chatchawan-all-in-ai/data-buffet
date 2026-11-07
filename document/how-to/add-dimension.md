# How-to: เพิ่ม dimension ที่มี surrogate key

ใช้ stable-key sync สำหรับ dimension ใหม่ที่มี surrogate key โดยอ่าน source ให้ครบและ
เก็บ SK เดิมตาม natural key ดูกติกาเต็มใน
[stable dimension SK synchronization](../project_wiki/dimension/merge-sk-pattern.md)
และตรวจ key/source เดิมใน [dimension inventory](../project_wiki/dimension/inventory.md)

## ขั้นตอน

### 1. กำหนด natural key และ grain

กำหนด key ตาม [grain-preservation contract](../project_wiki/dimension/merge-sk-pattern.md#key-and-synchronization-rules)
และระบุ grain/key ของตารางใน OKF card ก่อนเริ่ม implementation

ถ้า key ยังแยกแถวซ้ำไม่ได้ ให้หยุด dimension นั้นไว้และบันทึกตัวอย่างแถวที่ชนกัน
อย่าลบหรือรวมข้อมูลซ้ำเพื่อทำให้ assertion ผ่าน

### 2. เริ่มจาก action dimension ที่ใช้ stable sync

ใช้ `definitions/dimension/dim_waterpac.sqlx` เป็นโครงสร้างตั้งต้น แล้วแก้เฉพาะส่วน
ที่ประกาศ table references, key, columns และ source query ให้ตรงกับ dimension ใหม่

- `config` ใช้ `type: "operations"`, `hasOutput: true`, `schema: databuffet.DIMENSION_TABLE`,
  `dependencies` และ tag ของ dimension ที่ใช้อยู่
- ประกาศ target เป็น `<Name>Table` และ `<Name>TableRef` ใน `js {}`
- สร้าง complete source snapshot จาก SELECT/CTE เดิม และคง source joins, UNION,
  `QUALIFY`, fallback, sentinel `-1`, formulas และคอลัมน์เดิมไว้
- สำหรับ MDS ให้คงเงื่อนไข `is_active = TRUE`; source snapshot ต้องครอบคลุมทุกแถวที่
  ควรอยู่ใน dimension ไม่ใช้ `updated_at` window
- ใช้ nullable-safe `IS NOT DISTINCT FROM` สำหรับ lookup natural key เพื่อหา SK เดิม
  หลังคง SK เดิมหรือจ่าย SK ใหม่แล้ว ให้ MERGE ด้วย `ON T.<SK> = S.<SK>`
- ตรวจ source/target natural key ให้ unique และ target SK ให้ non-NULL และ unique
- คง SK เดิมเมื่อ natural key ตรงกัน; จัดสรร `MAX(SK) + ROW_NUMBER()` เฉพาะแถวใหม่
- ใช้สามกรณีใน sync เดียว: update เฉพาะ attributes, insert แถวใหม่พร้อม SK, และ delete
  target ที่ไม่อยู่ใน complete source
- ห้าม update SK หรือตัว natural key

ตาราง `operations` ต้องมีอยู่ใน BigQuery ก่อน action ทำงาน; ตรวจสภาพแวดล้อมและวิธี
เตรียมตารางตาม deployment guide ของทีม

### 3. รักษา behavior เฉพาะ

- ทำ source calculations และ filters เดิมให้เหมือนเดิมทุกประการ
- ห้ามแก้ process หรือ fact logic เพื่อรองรับ dimension
- ไม่ใช้ stable sync ถ้า source grain ยังไม่ระบุหรือ key ซ้ำโดยไม่มี discriminator ที่
  คงที่; ดูข้อยกเว้นใน [special cases](../project_wiki/dimension/special-cases.md)
- dimension ที่ไม่มี SK เช่น `dim_doctype` ให้คงเป็น active-source SELECT ตาม pattern
  ของไฟล์นั้น ไม่ต้องเพิ่มตัวแทน SK

### 4. เอกสารและตรวจสอบ

- เพิ่ม natural key และ source ใน [dimension inventory](../project_wiki/dimension/inventory.md)
- อัปเดต OKF card ใน `document/okf/` ให้สะท้อน grain, columns, key และ source
- คอมไพล์ Dataform และใช้ BigQuery `--dry_run` กับ query ที่รองรับการตรวจแบบ dry run
- ตรวจ schema และผลจำลอง source sync เทียบกับตารางปัจจุบันแบบอ่านอย่างเดียว
