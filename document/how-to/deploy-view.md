# How-to: Deploy View ขึ้น BigQuery (ด้วยมือ)

> ตรวจกับสภาพจริงเมื่อ 2026-09-15 · คู่กับ [add-view.md](add-view.md) และ
> [project_wiki/view/view-layer.md](../project_wiki/view/view-layer.md)

## ทำไมต้องทำมือ

tag `view` **ยังไม่อยู่ในตารางเวลาของ Dataform** และเจ้าของงานเลือกแก้ view ตรง ๆ
บน BigQuery console แทนการรัน Dataform (กันไม่ให้ Dataform `CREATE OR REPLACE` ทับ
งานที่แก้ค้างไว้บน console)

ผลที่ตามมาคือกฎข้อเดียวที่ต้องจำ:

> **commit ≠ deploy** — `.sqlx` ที่ merge เข้า `dev` แล้ว อาจไม่เคยขึ้น BigQuery เลย
> และไม่มีอะไรเตือน

วัดจริง 2026-09-15: view 5 ตัวที่ commit ไปแล้วค้างไม่ได้ deploy **นานสุด 5 เดือน**
(`Model_Invoice_Transaction` แก้ในรepo 16/04 · BigQuery ยังเป็นของเดิมจนถึง 15/09)
รายการเต็ม: [view-layer.md](../project_wiki/view/view-layer.md) หัวข้อ "drift = 0"

## ขั้นตอน

### 1. แก้ `.sqlx` แล้ว commit ตามปกติ

ตามกฎใน [add-view.md](add-view.md) — `${ref()}` สำหรับ validated/curated,
js-block `TableRef` สำหรับที่เหลือ

### 2. Render SQL ให้เป็นแบบที่ BigQuery กิน

ต้องขยาย placeholder ทั้งหมดเองก่อน (Dataform ทำให้ตอน compile แต่เราไม่ได้รัน):

| ในไฟล์ | ขยายเป็น |
|---|---|
| `${ref(databuffet.CURATED_MAC5, "curated_mih")}` | `` `databuffet-nonprd.curated_mac5.curated_mih` `` |
| `` `${DimCompanyTableRef}` `` | `` `databuffet-nonprd.dimension_table.dim_company` `` |
| `${databuffet.DATABASE}` / `${databuffet.<KEY>}` | ค่าจาก `includes/controller/variables.json` |
| `${databuffet.functionData.cleanString("x")}` | `NULLIF(CAST(TRIM(x) AS STRING), '')` |

ทางลัดที่ใช้ได้จริง: รัน drift scan (ขั้นที่ 4) **ก่อน** deploy — `scan.py` render
ไฟล์ด้วยวิธีเดียวกับ Dataform แล้วเขียน unified diff ลง `<scratchpad>/diffs/`
ฝั่ง repo ในไฟล์ diff นั้นคือ SQL ที่ render เสร็จแล้ว copy ไปใช้ได้เลย

> ⚠️ ยังไม่มีคำสั่ง "render อย่างเดียว" ใน `scan.py` (ไม่มี flag `--render`) —
> ถ้าต้องทำบ่อย ควรเพิ่ม flag นี้เข้าไปในสคริปต์

### 3. `CREATE OR REPLACE VIEW` บน BigQuery console

```sql
CREATE OR REPLACE VIEW `databuffet-nonprd.<dataset>.<view_name>` AS
<SQL ที่ render แล้ว>
```

- `<dataset>` เอาจาก `config.schema` ของไฟล์ **ไม่ใช่ชื่อโฟลเดอร์** — สองอย่างนี้
  ไม่จำเป็นต้องตรงกัน (ดูตารางใน [add-view.md](add-view.md) §1)
- ถ้าแก้ view ที่มี view อื่นอ่านต่อ (เช่น `view_fact_transcation` →
  `Model_Invoice_Transaction`) ให้ deploy **ตัวล่างสุดก่อน** แล้วไล่ขึ้น
- แก้ชุดไหนต้องทำให้ครบชุด — เช่นรอบ `LOWER(milStk)` มี view 3 ตัวต้องแก้พร้อมกัน
  (`onetime.Transaction_Data_Mart`, `onetime.Model_Invoice_Transaction`,
  `fact_view.view_fact_transcation`) แก้ไม่ครบ = ตัวเลขสองฝั่งไม่ตรงกัน

### 4. ยืนยันด้วย drift scan — **ขั้นนี้ห้ามข้าม**

```bash
python .claude/skills/bq-drift-scan/scripts/scan.py --scratchpad <scratchpad>
```

ต้องได้ `identical` สำหรับ view ที่เพิ่ง deploy · ถ้ายังขึ้น different แปลว่า
render ไม่ตรง หรือ paste ไม่ครบ · รายละเอียดการ dump/จำแนก:
skill [`bq-drift-scan`](../../.claude/skills/bq-drift-scan/SKILL.md)

เกณฑ์ที่ถือว่าจบ (baseline 2026-09-15): **40 object · identical 40 · different 0**
(`extra in BigQuery 1` = `onetime.PowerBI_Data_Buffet_Transaction` ที่เลิกใช้แล้ว
ตั้งใจปล่อยไว้ ไม่ถือเป็น drift)

## กรณีกลับทาง — มีคนแก้ view บน console

BigQuery เป็น source of truth ของ SQL ใน view **ห้ามเขียนทับจาก repo โดยไม่ถาม** —
ให้ pull กลับเข้า repo แทน:

```bash
python .claude/skills/bq-drift-scan/scripts/pull.py --scratchpad <scratchpad> --view <name>          # dry run
python .claude/skills/bq-drift-scan/scripts/pull.py --scratchpad <scratchpad> --view <name> --apply
```

`pull.py` คง `config {}` เดิม เอา SQL body จาก BigQuery มาตรง ๆ แล้วแปลง path กลับ
เป็น `${ref()}` / js-block `TableRef` ให้อัตโนมัติ พร้อมเติม `dependencies[]` ที่ขาด

## Checklist

- [ ] commit `.sqlx` แล้ว
- [ ] render placeholder ครบทุกตัว (ไม่มี `${...}` หลงเหลือใน SQL ที่ paste)
- [ ] `CREATE OR REPLACE VIEW` ชี้ dataset ตาม `config.schema` (ไม่ใช่ชื่อโฟลเดอร์)
- [ ] deploy ครบทั้งชุดที่เกี่ยวข้อง เรียงจาก view ล่างสุดขึ้นบน
- [ ] `bq-drift-scan` ขึ้น `identical` แล้ว
- [ ] ถ้าเป็น pattern ใหม่ → บันทึกใน [view-layer.md](../project_wiki/view/view-layer.md)
