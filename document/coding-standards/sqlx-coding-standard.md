# SQLX Coding Standard

มาตรฐานการเขียนไฟล์ `.sqlx` ของโปรเจกต์ — ยึดตามโค้ดจริงที่ใช้อยู่ (สแกน 2026-07-10)

## 1. โครงไฟล์

ทุกไฟล์เรียงเป็น 4 ส่วน:

```sqlx
config { ... }        -- metadata: type, schema, tags, dependencies, bigquery
js { ... }            -- ตัวแปร: table ref, pk_key, statement ที่ generate
<SQL body>            -- SELECT หรือ BEGIN...END
pre_operations {}     -- (validated) มักว่าง
post_operations { }   -- PK constraint / business UPDATE
```

## 2. config block

```javascript
config {
    type: "incremental",                    // "table" | "incremental" | "operations"
    schema: databuffet.VALIDATED_MAC5,      // ผ่าน databuffet.* เท่านั้น
    dependencies: ["validated_schema_mac5", "create_all_table_raw_mac5"],
    tags: [databuffet.TAG_VALIDATED, databuffet.TAG_VALIDATED_INCREMENTAL],
    uniqueKey: ["company_id", "mihtype", "mihvnos"],
    bigquery: {
        partitionBy: "asatdate",
        clusterBy: ["company_id", "mihvnos"],   // ≤ 4 คอลัมน์
    },
}
```

กติกา:
- `schema` และ `tags` ต้องอ้าง `databuffet.*` — **ห้าม string literal**
- เลือก `type` ตาม layer:
  - validated: `incremental` (transactional) หรือ `table` (full-load reference)
  - curated: `incremental`
  - dimension stable-key sync: `operations` with a complete source snapshot
  - fact: `table` หรือ `operations`
- `dependencies` ใช้กับ action ที่อ้างด้วย string interpolation (dim, schema bootstrap)
  ส่วนตารางที่อ่านผ่าน `${ref(...)}` Dataform จัด dependency ให้เอง — ไม่ต้องใส่ซ้ำ

## 3. การอ้างอิงตาราง/วิว — เลือก 1 ใน 2 แบบตาม "ใครสร้างตารางนั้น"

**กฎ**: ตารางที่ Dataform สร้างในชั้น validated/curated ใช้ `${ref()}`
ที่เหลือทั้งหมดประกาศ object + Ref string ใน `js {}` — **ห้าม inline**
`` `${databuffet.DATABASE}.${databuffet.XXX}.tbl` `` ใน SQL body และห้าม hardcode
`databuffet-nonprd` หรือชื่อ dataset ตรง ๆ

| แหล่งข้อมูล | รูปแบบ | `dependencies[]` |
|---|---|---|
| `validated_*`, `curated_*` | `${ref(databuffet.VALIDATED_MAC5, "deb")}` | **ห้ามใส่** — Dataform ผูกให้เอง |
| `dimension_table`, `fact_table`, view อื่น, `process_dataset`, `mds_dataset`, `onetime` base, `function_dataset`, external | js-block `<Pascal>TableRef` | ใส่ (เฉพาะที่เป็น action ใน repo) |

### 3.1 `${ref()}` — validated / curated

```sql
FROM ${ref(databuffet.CURATED_MAC5, "curated_mih")} AS mih
LEFT JOIN ${ref(databuffet.VALIDATED_MAC5, "deb")} AS deb ON ...
```

- 2 อาร์กิวเมนต์เสมอ: `ref(<schema constant>, "<table>")`
- **ไม่ต้องครอบ backtick** — `ref()` คืน FQN ที่ quote มาให้แล้ว
- ชื่อที่อ้างผ่าน `ref()` **ห้ามใส่ซ้ำใน `dependencies[]`** (§10)

### 3.2 js block — ที่เหลือทั้งหมด

```javascript
js {
    const DimCompanyTable = {
        database: databuffet.DATABASE,
        schema: databuffet.DIMENSION_TABLE,
        name: "dim_company",
    };
    const DimCompanyTableRef = `${DimCompanyTable.database}.${DimCompanyTable.schema}.${DimCompanyTable.name}`;
}
```

```sql
FROM `${DimCompanyTableRef}`
```

- ชื่อ: `<PascalCase>Table` + `<PascalCase>TableRef` — PascalCase แปลงจากชื่อตาราง
  (`dim_company` → `DimCompany`, `mds_data_keyaccount_master` → `MdsDataKeyaccountMaster`)
- ต้องครอบ backtick: `` `${XxxTableRef}` ``
- ตารางเป้าหมายของไฟล์ใช้ `name: name()` (ชื่อไฟล์ = ชื่อตาราง)
- ประกาศเรียงตามลำดับที่ถูกใช้ครั้งแรกใน SQL และ**ประกาศเฉพาะตัวที่ใช้จริง**
  (ไม่มี declared-but-unused); ถ้าไฟล์นั้นอ้างแต่ validated/curated ก็**ไม่ต้องมี js block**
- validated: ประกาศ `pk_key` ใน js ให้ตรงกับ `uniqueKey` ใน config เสมอ (นิยามซ้ำ 2 ที่)
- validated ที่เป็นเอกสารหลายบรรทัด (`mih`/`mil`/`mir`): เพิ่ม `doc_key` + `temp_table`
  ใน js แล้วสร้าง TEMP table + DELETE ราย document ใน `pre_operations` — config
  (`type`, `uniqueKey`) ไม่เปลี่ยน ดู `document/project_wiki/validated/validated-layer.md`

> ทำไม dim/fact ไม่ใช้ `ref()`: MERGE dims และ `fact_transcation` เป็น
> `type: "operations"` ที่ target มีอยู่ก่อนใน BigQuery — Dataform ไม่ได้เป็นเจ้าของ
> target จึง `ref()` ไม่ได้ ส่วน dimension operation actions ก็ใช้ js-block กับ target
> ที่มีอยู่ก่อนใน BigQuery
>
> กฎนี้ใช้กับทุก view ใน `definitions/view/` — ดู [View Layer](../project_wiki/view/view-layer.md#pattern)

### 3.3 Backslash ใน SQL body — เขียนตรง ๆ ตัวเดียว

**Dataform ส่ง backslash ใน SQL body ของ `.sqlx` ไปยัง BigQuery ตรง ๆ ไม่ unescape**
เขียนยังไงได้อย่างนั้น — regex เขียนเหมือนที่จะเขียนใน BigQuery console เป๊ะ

```sql
-- ถูก: เขียนตัวเดียวเหมือน SQL ปกติ
REGEXP_EXTRACT(pernamet, r'\(([^)]*)\)')
STRING_AGG(item, '\n')

-- ผิด: \\ จะหลุดไปถึง BigQuery ทั้งคู่
REGEXP_EXTRACT(pernamet, r'\\(([^)]*)\\)')   -- BigQuery อ่านว่า backslash + วงเล็บเปิด
```

| เขียนใน `.sqlx` | SQL ที่ออกจริง | ผล |
|---|---|---|
| `\n` `\(` `\d` `\s` `\+` `\1` | เหมือนเดิมทุกตัว | ✅ ที่ต้องการ |
| `\\n` `\\(` `\\d` | เหมือนเดิมทุกตัว (ยังคู่) | ⛔ regex พัง / เพี้ยนเงียบ |

#### ⚠️ ข้อยกเว้น — ใน `--` comment ต้อง double

Dataform escape backslash ให้อัตโนมัติ**เฉพาะในโค้ด SQL** แต่**ไม่ทำใน `--` comment**
comment จึงถูกประมวลผลเป็น JS template literal ตรง ๆ

```sql
--   SPLIT(REGEXP_REPLACE(ProductCode, r'/([PU])', r'|\\1'), '|')   -- ✅ ใน comment ต้อง \\1
    ARRAY_REVERSE(SPLIT(REGEXP_REPLACE(ProductCode, r'/([PU])', r'|\1'), '|'))  -- ✅ ในโค้ดใช้ \1
```

| ใน `--` comment | ผล |
|---|---|
| `\1`–`\9`, `\0` | ⛔ **compile error** *"Octal escape sequences are not allowed in template strings"* |
| `\n` `\t` `\r` | ⚠️ กลายเป็นขึ้นบรรทัดใหม่/tab จริง — **comment ขาดกลางคัน ส่วนที่เหลือกลายเป็นโค้ด** |
| `\(` `\d` `\s` | backslash หายเงียบ (ไม่อันตรายเพราะเป็น comment แต่อ่านแล้วสับสน) |
| `\\1` `\\n` | ✅ ได้ `\1` `\n` ตามต้องการ |

**สรุป: โค้ดเขียนตัวเดียว / comment เขียนสองตัว**
ที่ใช้อยู่จริง: [view_dim_product_master.sqlx:45](../../definitions/view/dimension_view/view_dim_product_master.sqlx)
เป็น comment เดียวในทั้งโปรเจกต์ที่มี backslash (สแกนยืนยัน 2026-08-10)

> ⚠️ **ข้อยกเว้น — ไฟล์ `.js` จริงใน `includes/`**
> `includes/controller/function-data.js` เป็น JavaScript จริง string ในนั้นเป็น template
> literal จริง ๆ → **ต้อง double** เช่น ``pattern = `r'[\\n\\r\\t]'` `` ซึ่ง**ถูกแล้ว**
> กฎ "เขียนตัวเดียว" ใช้กับ **SQL body ของ `.sqlx` เท่านั้น** ไม่ใช้กับ `.js`

> **ยืนยันก่อน deploy เสมอ**: เปิด panel **Compiled queries** ใน Dataform UI แล้วดูว่า
> backslash ที่ออกมาเป็นแบบที่ต้องการจริง — เร็วกว่าและชัวร์กว่าการเดาจากเอกสาร

> **ห้าม copy `.sqlx` ไปวางใน BigQuery console และห้าม copy จาก console กลับเข้า `.sqlx`
> โดยไม่ตรวจ** — deploy ผ่าน Dataform เท่านั้น

#### ประวัติ (สำคัญ — เอกสารฉบับก่อนบอกกลับด้าน)

| วันที่ | เกิดอะไร |
|---|---|
| 2026-07-27 | §3.3 ฉบับแรกสรุปว่า Dataform คอมไพล์ body เป็น JS template literal จึงต้อง double → commit `3c02e61` ไล่ double 3 view file + `67e779e` double ทั้ง `create_all_function.sqlx` (335 จุด) |
| 2026-08-07 | UDF ถูก deploy เข้า BigQuery → `EXTRACT_CHQ_DATA` พัง `Cannot parse regular expression: missing )` |
| 2026-08-10 | ตรวจ **Compiled queries panel ของจริง** → `\\` ออกมาเป็น `\\` ไม่ถูกกิน **ข้อสรุปเดิมผิด** ย้อน `create_all_function.sqlx` (351 จุด) และ 3 view file กลับเป็น backslash ตัวเดียว |

**บทเรียน**: อย่าสรุปพฤติกรรม compiler จากการอนุมาน — เปิด Compiled queries panel ดูของจริง

## 4. การ cast / ทำความสะอาดข้อมูล

ใช้ helper จาก `function-data.js` เท่านั้น:

```sql
${databuffet.functionData.cleanString("t1.CompanyID")} AS CompanyID,
${databuffet.functionData.castInt64("t1.StatusID")}    AS StatusID,
${databuffet.functionData.castFloat64("t1.weight")}    AS weight,
${databuffet.functionData.parseFlexibleDatetime("create_date")} AS create_date,
${databuffet.functionData.parseAsatDate()}             AS asatdate,
```

- string ทุกคอลัมน์ → `cleanString` (หรือ `cleanCode` ถ้ามี control character)
- **ยกเว้น** คอลัมน์ string ที่อยู่ใน `uniqueKey` ของตาราง incremental ห้ามเป็น NULL →
  `IFNULL(cleanString(...), '')` เพราะ MERGE เทียบ key ด้วย `=` และ `NULL = NULL` ไม่จริง
  แถวนั้นจะถูก INSERT ซ้ำทุกรอบ (เคส `mie.miecus` 2026-10-12)
- ใน JOIN condition ก็ต้องใช้ `cleanString` ฝั่งต้นทางให้ตรงกับค่าที่เก็บ
- datetime จาก raw → `parseFlexibleDatetime` (SAFE, พังเป็น NULL)
- datetime จาก raw ที่เป็น UTC (`master_sku`, DERP journal headers/entries) → `parseFlexibleUtcDatetime` (SAFE; รับทั้งมีและไม่มี offset `+00:00` แล้วแปลงเป็น DATETIME เวลา `Asia/Bangkok`)
- date string `YYYY-MM-DD` หรือ `YYYY/MM/DD` → `parseFlexibleDate` (NULL คง NULL; รูปแบบอื่น fail ทั้ง run โดยตั้งใจ) — `parseDateDash`/`parseDateSlash` ถูกลบแล้ว (2026-10-28)
- `castInt64/castFloat64` ไม่ SAFE — ตั้งใจให้ fail เมื่อ schema เพี้ยน

## 5. วันที่และ timezone

- `CURRENT_DATE('Asia/Bangkok')` เสมอ — ห้าม `CURRENT_DATE()` เปล่า
- Incremental window ของ validated กรองบน **string** `ASATDATE`:
  ```sql
  ${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY))`) }
  ```
- Dimension sync uses a complete active-source snapshot rather than an `updated_at` window.

## 6. Deduplication

```sql
QUALIFY ROW_NUMBER() OVER(
    PARTITION BY ${pk_key}
    ORDER BY asatdate DESC          -- หรือคอลัมน์ business ที่เหมาะสม
) = 1
```

## 7. Primary key (validated)

post_operations มาตรฐาน — retry loop 10 ครั้ง, รันเฉพาะ full build:

```sql
post_operations { ${ when(!incremental(), post_operations_statement) } }
-- statement = BEGIN ... WHILE retry < 10 ...
--   ALTER TABLE ${self()} DROP PRIMARY KEY IF EXISTS;
--   ALTER TABLE ${self()} ADD PRIMARY KEY (${pk_key}) NOT ENFORCED;
-- ... END
```

PK เป็น `NOT ENFORCED` — เป็น hint ให้ optimizer ไม่ใช่ constraint จริง

## 8. Dimension SK synchronization

การเลือกคีย์ การใช้ source ที่ครบ การตรวจ assertions การจัดสรรคีย์ และ MERGE ทั้งสามส่วน
ให้ทำตาม [stable-key synchronization contract](../project_wiki/dimension/merge-sk-pattern.md)
ส่วน [inventory](../project_wiki/dimension/inventory.md) ระบุขอบเขตและตารางที่ยังพักไว้
และ OKF card ของแต่ละตารางระบุ grain กับ key

ห้ามเลือกรายการด้วยลำดับ SK เช่น `MIN`/`MAX`, `ORDER BY` หรือ `QUALIFY` บน SK ของ dimension
หรือ fact ให้เรียงด้วยคอลัมน์ธุรกิจที่ `ROW_NUMBER()` เดิมใช้แทน เพราะ SK คงที่จัดสรรด้วย
`MAX + n` สำหรับแถวใหม่ จึงไม่สื่อถึงลำดับธุรกิจ

### Fact row surrogate keys

fact ทั้ง 11 ตารางที่มี row-level SK ใช้คีย์แถวแบบคงที่ ได้แก่ `fact_order`,
`fact_quotation`, `fact_invoice`, `fact_delivery`, `fact_transaction_delivery`,
`fact_mir_vs`, `fact_chq`, `fact_mir_rs`, `fact_order_store`, `fact_invoice_store`
และ `fact_backlog_store` โดยคำนวณแต่ละคีย์ด้วย
`FARM_FINGERPRINT(TO_JSON_STRING(STRUCT(<typed business key fields>, occ)))`
สร้าง `occ` ด้วย `ROW_NUMBER()` ที่แบ่งตาม natural business grain ของ fact
และเรียงด้วย `TO_JSON_STRING` ของ output ทุกคอลัมน์ที่เปิดเผย ยกเว้น row SK ของ fact นั้น
ให้รวม FK SK, business date, วันที่รัน เช่น `asatdate` และ output ทุกคอลัมน์
สร้าง public row ก่อนจัดอันดับ เพื่อให้ค่าที่คำนวณและ candidates จาก join ใช้กติกาเดียวกัน
แถวที่ค่า output เหมือนกันทั้งหมดถือเป็น tie
ห้ามใช้ internal grain fields ที่ไม่แสดงใน output มาเรียง เช่น natural key ของ cheque ใน
`fact_mir_rs` และ source company ใน `fact_delivery`
ให้คง output columns, field types, จำนวนแถว, ค่า non-key และ materialization config

`assignedOccurrences` ใน `includes/fact_occurrence.js` หา ordinal ที่ `fact_order` จัดให้
สำหรับ `fact_invoice` โดยจับคู่ hash ที่บันทึกไว้กับ ordinal ตั้งแต่ 1 ถึงจำนวนแถวใน grain
ให้สร้าง typed `STRUCT` เหมือนฝั่งสร้างทุกประการ รวมชื่อ field และ normalization
ห้ามจัดอันดับแถว order ที่บันทึกไว้อีกครั้ง
ordinal เป็นค่าภายในและไม่ส่งออกใน public output
join ของ delivery และ receipt ใช้ FK SK ใน output ordering ได้โดยตรง ไม่ต้องกู้ ordinal ต้นทาง

คง base SELECT ของ `fact_order` ไว้ เพราะการเปลี่ยนลำดับ aggregation เปลี่ยนผล `FLOAT`
และสร้าง stable key ใน `post_operations`
`fact_invoice` เลือกแถว order ที่เชื่อมกันด้วย `occ DESC`
คงการเลือก latest-billing candidate เดิมใน `fact_mir_vs` รวมถึงการเลือกใดก็ได้เมื่อวันที่ล่าสุดเสมอกัน
และห้ามเพิ่ม tie-breaker ใหม่
`fact_mir_vs` hash `(company_id, mirtype, mirvnos, mirlistno, mirbinvno, occ)`
โดย occurrence partition ใช้ business fields ห้าตัวแรก
`fact_mir_rs` hash receipt natural key กับ cheque natural key ใน typed `STRUCT` เดียวพร้อม `occ`
เพื่อให้แถวที่มี cheque อย่างเดียวได้คีย์ต่างกันด้วย

ไม่มี legacy key map: row-level fact SK เปลี่ยนครั้งเดียวตอน rollout แล้วคงเดิมในการ rebuild
`fact_transcation` และ fact ของ MDT ทั้งหกไม่มี row-level SK
เก็บหลักฐาน live comparison ไว้นอก repository

## 9. คอมเมนต์

- คอมเมนต์ไทยหรืออังกฤษได้ ให้อธิบาย "ทำไม" ไม่ใช่ "ทำอะไร"
- **สั้น ย่อ เข้าใจง่าย** (ผู้ใช้กำหนด 2026-09-28) — ปกติ 1 บรรทัดต่อจุด ห้ามเขียนยาวหลายบรรทัด
  รายละเอียด/ที่มา/ตัวอย่าง ให้ไปอยู่ใน `document/` แทน
  ```sql
  -- ✅ ข้อมูลเข้า day -1 · เสาร์ทีมดูรายงานหยุด → สะสมย้อนถึงวันทำงานล่าสุด
  -- ⛔ comment 5–6 บรรทัดอธิบายกฎ ตัวอย่าง และข้อจำกัดทั้งหมด
  ```
- โค้ดที่เลิกใช้: โปรเจกต์นิยม comment ไว้ (เช่น SK ใน dim_doctype) —
  ถ้าตั้งใจปิดถาวรให้เขียนเหตุผลกำกับ

## 10. สิ่งที่ห้ามทำ

| ห้าม | เพราะ |
|---|---|
| hardcode ชื่อ dataset/project | ต้องผ่าน `databuffet.*` เพื่อย้าย environment ได้ |
| inline `` `${databuffet.DATABASE}.${databuffet.X}.tbl` `` ใน SQL body | ต้องประกาศ object + `XxxTableRef` ใน `js {}` แล้วอ้าง `` `${XxxTableRef}` `` (§3.2) |
| ใช้ js-block Ref กับ `validated_*` / `curated_*` | ต้องใช้ `${ref(...)}` เพื่อให้ Dataform ผูก dependency ให้ (§3.1) |
| escape backslash ผิดบริบท | ใช้กฎ SQL body, `--` comment และไฟล์ `.js` ตาม [§3.3](#33-backslash-ใน-sql-body--เขียนตรง-ๆ-ตัวเดียว) |
| เปลี่ยน SK ของ dimension ที่ downstream persist ไว้โดยไม่ sync ตาม natural key | fact/dim อื่นอาจชี้ไปยัง key ที่ไม่มีอยู่หรือผิดแถว |
| recreate a stable dimension from a fresh SELECT | assigning keys again can break downstream references |
| `CURRENT_DATE()` ไม่ระบุ timezone | เที่ยงคืน UTC ≠ เที่ยงคืนไทย ข้อมูลคลาดวัน |
| เลือกแถวด้วย `MIN`/`MAX`, `ORDER BY` หรือ `QUALIFY` บน dimension หรือ fact SK | SK ใหม่จัดสรรด้วย `MAX + n` จึงไม่บอกลำดับธุรกิจ ให้ใช้ business columns ที่ `ROW_NUMBER()` เดิมใช้ |
| แก้คำผิด `fact_transcation`, `CDC_DATESET`, `prdDiminsionData` | เป็น identifier จริงใน BigQuery |
| ใส่ dependency ของตารางที่อ่านผ่าน `ref()` ซ้ำ | graph ซ้ำซ้อน สับสน |
| use a partial source with delete-by-source in a stable dimension | active rows outside the source window would be removed |
