# Known Issues & Gotchas

รวมจุดที่รู้แล้วว่า "เป็นแบบนี้โดยตั้งใจ" หรือ "ต้องระวัง" — อัปเดตล่าสุด 2026-10-28

## `dim_customer_report_info` SK เสถียรแล้ว — ห้าม full rebuild (2026-10-28)

เดิมเป็น `type: "table"` ที่ rebuild ทุกวันด้วย `ROW_NUMBER() OVER(ORDER BY CompanyID, CustomerReportKey)`
ชื่อใหม่ที่เรียงอยู่กลางทำให้ SK ของทุกชื่อหลังจากนั้นขยับ (41,593 แถว ณ วันเปลี่ยน) — เปลี่ยนเป็น
`type: "operations"` MERGE + `max_sk` แบบ `dim_customer`
([inventory (b2)](../project_wiki/dimension/inventory.md#group-b2--mds--invoice-merge-1))

- **ห้าม rebuild ตารางใหม่ตั้งแต่ต้น** (`CREATE OR REPLACE`, drop แล้วรันใหม่, กลับไปใช้ `type: "table"`) — SK จะเรียงใหม่ทั้งหมด
- ตารางต้องมีอยู่แล้วใน BigQuery พร้อมคอลัมน์ `CustomerReportKey` (เพิ่มครั้งเดียวด้วย `ALTER TABLE ... ADD COLUMN` แล้ว
  `UPDATE ... SET CustomerReportKey = REGEXP_REPLACE(CustomerReportName, r'\s', '')` ทุกแถวยกเว้น -1 ก่อนรันคืนแรก)
  · วัด 2026-10-28 (read-only): key จากชื่อในตารางตรงกับ key ที่ไฟล์ใหม่คำนวณ **41,592/41,592 แถว ต่าง 0** → คืนแรกไม่มีแถวใหม่ SK เท่าเดิมทุกแถว
- ชื่อที่หายจาก source (MDS inactive และไม่มี invoice ใน `view_dim_invoice`) **ค้างอยู่ในตารางพร้อม SK เดิม** — ตั้งใจ
  (ข้อมูลของแถวนั้นหยุดอัปเดต) · ถ้าชื่อกลับมาจะได้ SK เดิม
- คอลัมน์ใหม่ในอนาคตต้อง `ALTER TABLE ... ADD COLUMN` เองก่อน merge เหมือน dim MERGE ตัวอื่น

## CustomerFlag ใน mds sales representative (2026-09-15)

สมมติฐาน 3 ข้อที่กฎ CustomerFlag ตั้งอยู่ ถ้าข้อไหนพังต้องกลับมาแก้โค้ด

1. **แถว flag ต้องมีแถว DepCode ให้เกาะ** — user กรอกแถว CustomerFlag แยก โดยใช้
   companyID + EmployeeID + DepartmentID เดียวกับแถวกฎจริง และช่วงวันที่ซ้อนกัน
   `dim_sale_representative` จะยุบ flag เข้าไปในแถวที่มี DepCode
   **ถ้าหาแถวเกาะไม่ได้ แถว flag จะหายไปเงียบ ๆ ไม่มี error** เลือกทางนี้เพราะถ้าปล่อยให้
   แถว flag ล้วนเข้า dim มันจะไปยุบ `dim_sale_representative_last` ทั้งพนักงาน
   (`agg_normal` ไม่เช็ค CustomerFlag) ซึ่งวัดแล้วว่าย้าย fact `*Last` หลายร้อยแถว
   วิธีตรวจ: `SELECT` แถว mds ที่มี CustomerFlag แล้ว DepCode/Cost/Province ว่าง
   แล้วเทียบกับแถวที่โผล่ใน dim
2. **พนักงานคนเดียวในบริษัทเดียวกันห้ามมี 2 แถวที่รหัสภายใน DepCode ซ้อนกันแต่ต่าง DepartmentID และช่วงวันซ้อนกัน**
   (รวมกรณี `A|B` กับ `B` — ดูหัวข้อ DepCode หลายค่าด้านล่าง)
   — `seq_condition = 2.5` ให้สิทธิ์ทั้งแถว ไม่ได้ดูว่า transaction นั้นชนผ่าน customer list
   หรือชนผ่าน DepCode ถ้าเกิดกรณีนี้แถวที่มี flag จะชนะแม้ตอนที่ชนด้วย DepCode เฉย ๆ
   วัด 2026-09-15 ทั้ง mds ก่อนรองรับ list ใน DepCode: **0 คู่** ถ้าอยากกันจริงต้องย้าย priority ไปไว้ใน `ORDER BY`
   ของ `QUALIFY` แทน (ตัดสินใจไม่ทำเพราะยังไม่มีเคส)
3. **flag ใช้กับกิ่ง DepCode ล้วนเท่านั้น** — กิ่ง `seq_condition = 1`
   (DepCode + CostChannelID) ไม่ได้รับการ override จาก CustomerFlag ตาม spec ที่ตกลงกัน
   ("employeeid + depcode")

## DepCode หลายค่า `A|B` ใน mds sales representative (2026-10-17)

รูปแบบค่าและกฎ matching อยู่ที่ [DepCode รับหลายค่า](../project_wiki/fact/fact-layer.md#depcode-รับหลายค่า-ab-2026-10-17)
ส่วนการกรอกใน MDS เป็นงานของ user

- **อย่าให้รหัสซ้อนกัน** — พนักงานคนเดียวในบริษัทเดียวกันมีแถว `A|B` และแถว `B` (หรือ `A|B` สองแถว)
  ที่ช่วงวันซ้อนกันและผ่านเงื่อนไขอื่นของบิลเดียวกัน บรรทัด `B` จะชนทั้งสองแถว;
  `fact_transcation` เลือก `seq_condition` ต่ำสุดก่อน
  แล้วเลือก `SaleRepSK` มากกว่าเมื่อ priority เท่ากัน
  ซึ่งเปลี่ยนได้ทุกวันเพราะ SK ของ dim rebuild ใหม่ทุกวัน (พฤติกรรมเดียวกับมีแถว `A` ซ้ำสองแถวในปัจจุบัน)
  · `view_fact_transcation` เรียง `seq_condition`, `dim_report.Segment` แล้ว `SaleRepSK DESC`
  · การเลือก TA ใน `dim_customer_report_info` ใช้กฎเรียงของ
  [Customer Report Info](../project_wiki/view/view-layer.md#customer-report-info--customer-segment-2026-10-01)
- หลัง merge ต้อง deploy view `view_fact_transcation` และ rebuild `fact_transcation` /
  `dim_customer_report_info` ก่อน ค่าใหม่จึงมีผลกับข้อมูลจริง

## ยอดงวดเบิ้ลเพราะไฟล์ EOM ค้างในโฟลเดอร์ (เจอ+แก้ 2026-10-19)

DAG `pipline_saleout_mdt_eom` **รวมทุกไฟล์ในโฟลเดอร์เป็น AVRO ก้อนเดียว**
(`process_all_folders` — "all chunks are appended into the same Avro file")
รอบไหนไม่ได้รัน ไฟล์จะค้าง แล้วรอบถัดไปเก็บไปรวมกัน

ไฟล์ EOM แต่ละไฟล์คือ**ภาพรวมของทั้งงวด** ไม่ใช่ส่วนเพิ่มแบบฟีดรายวัน
2 ไฟล์จึงกลายเป็นทุกแถวซ้ำ 2 ครั้ง → ยอดงวดนั้นเบิ้ล

**เกิดจริง 2 ครั้งใน 2 สัปดาห์** — GB พาร์ทิชัน 20261015 · TW พาร์ทิชัน 20261018
(รอบวันที่ 17 ไม่ได้รัน ไฟล์ของ 17 กับ 18 เลย archive พร้อมกันตอน 05:17)
ยอด TW ก.ย. ขึ้นรายงาน BI เป็น 47.0M แทนที่จะเป็น 23.5M อยู่ 2 วัน

**⚠️ ทำไม `QUALIFY asat_raw = MAX(asat_raw)` ที่มีอยู่กันไม่ได้** — มันกันซ้ำ
*ข้ามพาร์ทิชัน* ถ้าไฟล์ซ้ำอยู่ใน AVRO ก้อนเดียวกัน (พาร์ทิชันเดียวกัน) มันรอดมาทั้งคู่

**⚠️ ทำไมต้องดักก่อน `GROUP BY`** — การยุบแถวกลบอาการสนิท จำนวนแถวที่ออกมา
**เท่าเดิมเป๊ะ** (TW ก.ย. 2,155 แถวทั้งตอนปกติและตอนเบิ้ล) มีแต่ยอดเงินที่คูณสอง
ถ้าดักที่ผลลัพธ์จะมองไม่เห็นอะไรเลย

**การ์ด `dup_guard` ในทั้ง 4 ไฟล์ eom** จึงนับแถวที่ซ้ำกันทั้งแถวใน CTE `latest`
แล้ว `ERROR()` ถ้าเจอ · วันปกติทั้ง 4 ห้างไม่มีแถวซ้ำเลยสักแถว จึงไม่เตือนผิด

**⚠️ ต้องอ้าง `dup_guard.ok` ใน `WHERE` ห้ามใช้ `CROSS JOIN` เฉย ๆ** — ถ้าไม่มีใคร
ใช้คอลัมน์นั้น BigQuery จะตัด join ทิ้งทั้งก้อน แล้ว `ERROR()` ไม่เคยถูกคำนวณ
การ์ดจะอยู่ในโค้ดแต่ไม่ทำงาน (เจอตอนทดสอบ ถ้าไม่ได้ลองกับข้อมูลเสียจริงจะไม่รู้)

**ยังไม่ได้แก้ที่ต้นเหตุ** — DAG ยังรวมไฟล์เหมือนเดิม และยังไม่รู้ว่าทำไมรอบ 17 ไม่รัน
ฝั่ง `pipline_saleout` รายวันไม่มีปัญหานี้ เพราะแต่ละไฟล์เก็บคนละวัน รวมกันแล้วไม่ซ้ำ

## คำสะกดผิดที่เป็น identifier จริง (ห้ามแก้)

| ที่ | คำ | หมายเหตุ |
|---|---|---|
| `definitions/fact/fact_transcation.sqlx` | `fact_transcation` | ชื่อไฟล์ + ตารางจริงใน BigQuery |
| `includes/controller/variables.json` | `CDC_DATESET` | คีย์ constant (ค่า `cdc_dataset` ถูกต้อง) |
| MASTERSKU JSON | `prdDiminsionData`, `SpeciFeild`, `dimFeild` | field จริงในข้อมูล |
| `FactOrderSk` vs `FactOrderSK` | casing ไม่คงที่ในไฟล์เดียวกัน | ใช้ตามที่ไฟล์นั้นใช้ |

## พฤติกรรมที่ตั้งใจ (อย่า "แก้")

- **mds dims 34 ตัวเป็น full daily rebuild** (ตัดสินใจ 2026-07-20 · เลข 34 คือจำนวน ณ วันนั้น ปัจจุบันมีมากกว่านั้น — ดู [inventory](../project_wiki/dimension/inventory.md)): แปลงจาก MERGE
  เป็น `type: "table"` ปั้นใหม่ทุกวันจาก `is_active = TRUE` — **SK ออกเลขใหม่ทุกวัน
  ห้าม persist SK พวกนี้ข้ามวัน** เหตุผล: mds มี overwrite import mode (ล้างแล้วลง
  ใหม่ id ใหม่หมด) ซึ่ง MERGE pattern รับมือไม่ครบ (zombie rows) ตรวจ consumer ครบ
  ทุกตัวแล้ว (repo + BQ + query history 90 วัน): ทุก consumer re-derive รายวัน
  ยกเว้นที่ยกเว้นไว้ ดู `project_wiki/dimension/full-rebuild-pattern.md`
  - **ยกเว้น 2 ตัวที่ยังเป็น MERGE + tombstone**: `dim_company` (CompanySK ฝังถาวรใน
    dims/facts ทั้งระบบ) และ `dim_aging_rang` (AgingRangSK freeze ใน dim_aging_history)
  - **เงื่อนไขปิดแล้ว (2026-07-20)**: `fact_mir_vs`/`fact_mir_rs` (+ `fact_chq`)
    ถูกย้ายเข้า repo เป็น `type: "table"` tag `fact_daily` (rebuild เต็มทุกคืน หลัง
    dims) — `dim_collection_status` rebuild ได้อย่างปลอดภัยแล้ว
- **Hard delete tombstone ใน mds MERGE dims** (ตัดสินใจ 2026-07-10 — ปัจจุบันเหลือ
  ใช้กับ dim_company + dim_aging_rang เท่านั้น): row ที่ mds `is_active = FALSE`
  ถูกลบจริงจาก dim โดยไม่เช็ก FK ปลายทาง; DELETE ไม่มี date filter (ตั้งใจ)
- **`dim_doctype` / `dim_holiday` ไม่มี SK** — โค้ด SK ถูก comment ไว้ MERGE ด้วย
  natural key แทน
- **`dim_stk_mkt` มี row 'Waiting Master'** (`MdsID = NULL`, MarketingGroupID='999') —
  placeholder สำหรับ stkcode ที่ยังไม่มี master ปลอดภัยจาก DELETE เพราะ
  `IN (subquery)` ไม่ match NULL
- **`curated_tbook_quotation`** — partition + incremental filter ถูก comment ไว้
  จึงทำงานเหมือน full rebuild แม้ประกาศ `type: "incremental"`
- **`mir.sqlx`** — `type: "incremental"` แต่ tag `validated_full` (จัดกลุ่ม operator)
- **saleout_mdt** — ไม่มี sub-tag และส่วนใหญ่ไม่ partition
- **View layer เข้า Dataform** (ตัดสินใจ + ทำ 2026-07-24): เดิม BigQuery views ถูก
  สร้าง/แก้ **นอก Dataform** ตรงใน console จึงไม่อยู่ใน repo และไม่มี lineage — ย้ายมา
  เป็น `type: "view"` ใต้ `definitions/view/` (แยก subfolder ตาม dataset ปลายทาง)
  แล้ว **32 ไฟล์** โดย **`config.schema` คงชี้ dataset เดิม** (`dimension_view`,
  `fact_view`, `onetime`, `process_dataset`, `bridge_dataset`) เพื่อไม่ให้
  Power BI/consumer พัง และแทน project literal `databuffet-nonprd` ด้วย
  `${databuffet.DATABASE}` (portable ข้าม env) — inventory เต็ม: `project_wiki/view/view-layer.md`
  - ไม่เอาเข้า Dataform: `temp_dim.*` 3 ตัว (test) + `peem_using` ทั้ง dataset 7 ตัว
    (`view_1..4_Product_DOS_CAT1*` + RLS trio `view_rls_data`/`sale`/`special` —
    เป็น **test copy ส่วนตัวของเจ้าของ** ของ RLS views ใน `process_dataset`)
  - เพิ่ม constant: `TAG_VIEW`=`view`, `BRIDGE`=`bridge_dataset` (ไม่มี `PEEM_USING`)
  - `dependencies[]` ใส่เฉพาะ action จริง (basename ที่ unique) — external/UDF/ตารางที่
    ไม่มี .sqlx (`dim_districts/provinces/geographies/sub_districts`, `dim_aging_history`,
    `mih_address_data`, `mds_*`) อ้างด้วย interpolation แต่ไม่ list เป็น dep
    (ตารางมีอยู่แล้ว)
    > แก้ 2026-08-11: ลิสต์นี้เคยมี `dim_product_rebate` (ชื่อผิด — ของจริงคือ
    > `dim_rebate` ซึ่ง**มี** .sqlx) และ `RLS_Customer360` (ตอนนี้ repo สร้างเองแล้วที่
    > `definitions/process/rls_customer360.sqlx` และเป็นตัวพิมพ์เล็ก) ทั้งคู่อยู่ใน
    > `dependencies[]` ของผู้ใช้เรียบร้อยแล้ว
  - ⚠️ ตอนบันทึกรายการนี้ยังไม่ได้ compile-verify — ตรวจในเครื่องได้ตาม [run/debug guide](../how-to/run-and-debug.md#ตรวจ-sql-โดยไม่มี-dataform-cli) และต้องเช็คตอนขึ้น service:
    (1) view ที่อ้าง view อื่น (chain เช่น `view_dim_aging`→`view_dim_channel`,
    `Model_Invoice_Transaction`→`view_fact_transcation`) resolve เรียงลำดับถูก
    (2) `fact_transcation.sqlx` อ่าน `onetime.Transaction_Data_Mart` และ
    `dimension_view.view_dim_channel` แต่ไม่ได้ประกาศ dep ฝั่ง fact (จงใจไม่แตะไฟล์
    pipeline เดิม) — pipeline ยังถูกเพราะ view เป็น logical + มีอยู่ก่อน; follow-up ควรเติม
    dep ฝั่ง fact ให้ DAG ครบ (3) ownership เปลี่ยนมือ — Dataform จะ `CREATE OR REPLACE`
    ทับทุกครั้งที่รัน ใครแก้ใน console จะโดนเขียนทับ
  - **Format การอ้างอิงตาราง = กฎ 2 ชั้น** (แก้ 2026-07-24 ตาม feedback 2 รอบ):
    (ก) `validated_*`/`curated_*` → `${ref(databuffet.<CONST>, "tbl")}` ไม่ครอบ backtick
    และ **ห้ามใส่ใน `dependencies[]`** (Dataform ผูกให้เอง — §10)
    (ข) ที่เหลือ (dim/fact, view อื่น, process, mds, onetime base, UDF, external) →
    js-block `<Pascal>Table`/`<Pascal>TableRef` อ้างด้วย `` `${XxxTableRef}` ``
    ห้าม inline `${databuffet.DATABASE}...` ใน body; view ที่อ่านแต่ validated/curated
    จะ**ไม่มี js block** เลย (ณ 2026-09-03 view ทั้ง 31 ตัวมี js block หมด ไม่มีตัวอย่างจริง)
    ประวัติ: รอบแรก generate เป็น inline (ผิด §3) → รอบสองแก้เป็น js-block ทั้งหมด
    (ยัง**ผิด** เพราะ validated/curated ต้องเป็น `ref()`) → รอบสามได้ตามนี้
    ยืนยันทุกรอบ: เนื้อ SQL ไม่เปลี่ยนเทียบกับ BigQuery
- **⚠️ ดึง view จาก BigQuery กลับเข้า `.sqlx` — backtick หาย** (เจอจริง 2026-08-10):
  `INFORMATION_SCHEMA.VIEWS.view_definition` คืน path ของตาราง **โดยตัด backtick ออก**
  เช่น `from databuffet-nonprd.dimension_table.dim_invoice as inv`
  **แก้ความเข้าใจผิด (2026-08-10)**: ตอนแรกบันทึกว่า "ไม่ใช่ SQL ที่ valid เพราะ project id
  มีขีดกลาง" — **ผิด** ทดสอบด้วย `bq query --dry_run` แล้ว GoogleSQL รับ project id
  ที่มีขีดกลางใน table path โดยไม่ต้อง backtick ได้ปกติ
  → **ยังต้องใส่ backtick กลับ** แต่เหตุผลคือ**ความสม่ำเสมอกับ convention ของ repo**
  ไม่ใช่เรื่อง valid/invalid (ทั้ง repo ใช้ `` `${XxxTableRef}` `` และมี 1 จุดที่หลุด —
  `fact_transcation.sqlx:768` — ซึ่งรันได้ แต่อ่านแล้วเหมือนบั๊กทุกครั้งที่มีคนรีวิว)
  (น่าสังเกต: การเรียก UDF ยังคง backtick ไว้ ตัดเฉพาะ path ของตาราง)
  **เวลาดึงกลับเข้า repo ต้องใส่ backtick ครอบ `` `${XxxTableRef}` `` เองทุกตัว**
  ส่วน `${ref(...)}` **ห้าม**ครอบ เพราะ Dataform ใส่ให้เองอยู่แล้ว
  **กับดักที่ 2 — backslash ใน comment (เจอ 2026-08-26 ตอน pull `view_dim_product_master`)**:
  ถ้าโค้ดที่ดึงกลับมามีบล็อกที่ถูก comment ไว้ด้วย `--` และข้างในมี backslash
  ต้อง **double เอง** — BigQuery คืนมาตัวเดียวเสมอ แต่ `\1` ใน `--` comment
  = octal escape → **ทั้ง action compile ไม่ผ่าน** (กฎอยู่ใน coding-standard §3.3)
  สคริปต์ `pull.py` **ไม่ได้ทำให้** — ต้องไล่เองหลัง pull ทุกครั้ง

  อีกเรื่อง: BigQuery **ตัด comment ที่ comment ทิ้งไว้ออก** ตอน save view ในคอนโซล
  (`view_rls_data` เสีย 88 บรรทัดของโค้ดเก่าที่ comment ไว้ — กู้จาก git history ได้)
  **บทเรียน**: สคริปต์เทียบ repo↔BQ ที่ normalize backtick ทิ้งก่อนเทียบ **มองไม่เห็นบั๊กนี้**
  ต้องเช็คแยกว่าทุก `${...TableRef}` มี backtick ครอบ
- **🔥 Backslash ใน SQL body — เขียนตัวเดียว (เอกสารเดิมบอกกลับด้าน แก้แล้ว 2026-08-10)**

  **ข้อเท็จจริง (ยืนยันจาก Compiled queries panel ของจริง 2026-08-10)**:
  Dataform ส่ง backslash ใน SQL body ของ `.sqlx` ไป BigQuery **ตรง ๆ ไม่ unescape**
  เขียน `\\` ก็ได้ `\\` เขียน `\` ก็ได้ `\` → **regex ต้องเขียนตัวเดียวเหมือน SQL ปกติ**
  (กฎอยู่ใน coding-standard §3.3 ที่แก้ใหม่แล้ว)

  **ลำดับเหตุการณ์**
  1. 2026-07-27 — สรุป (โดยการอนุมาน ไม่ได้เปิด compiled panel ดู) ว่า body เป็น JS
     template literal จึงต้อง double → commit `3c02e61` double 2 view file
     (`view_dim_product_master`, `view_aging_ri`) และ
     `67e779e` double ทั้ง `create_all_function.sqlx` (335 จุด)
  2. 2026-08-07 15:25 — deploy UDF เข้า BigQuery → `EXTRACT_CHQ_DATA` พัง
     `Cannot parse regular expression: missing )` เพราะ `\\(` ที่ไปถึง BigQuery
     ถูกอ่านเป็น "backslash + วงเล็บเปิด" วงเล็บไม่บาลานซ์
     **และ regex อีก 33 ตัวในฟังก์ชันเดียวกันผิดเงียบด้วย** (`\\d` = backslash+`d`
     ไม่ใช่ตัวเลข) — ไม่ใช่แค่ตัวที่ error ดัง
  3. 2026-08-10 — เปิด **Compiled queries panel** ดูของจริง พบว่า `\\` ออกมาเป็น `\\`
     → **ข้อสรุปของข้อ 1 ผิด** ย้อนกลับทั้งหมด: `create_all_function.sqlx` 351 จุด
     และ 3 view file (`git checkout 3c02e61^`) กลับเป็น backslash ตัวเดียว
  4. 2026-08-10 (ต่อ) — deploy `create_all_function` ผ่าน Dataform แล้ววัดของจริง:
     `EXTRACT_CHQ_DATA` 337 backslash / `clean_company_prefix` 14 → รวม 351 เท่ากับใน
     `.sqlx` เป๊ะ และ `REGEXP_CONTAINS(ddl, r'\\\\')` = **false** ทุก routine
     → **ยืนยัน pass-through 1:1 จากปลายทาง** ทดสอบเรียกใช้ผ่านทั้ง 3 เคส
  5. 2026-08-10 (ต่อ) — เจอ **ข้อยกเว้นจริง: `--` comment คนละกฎกับโค้ด**
     Dataform escape backslash ให้อัตโนมัติเฉพาะในโค้ด SQL **ไม่ทำใน `--` comment**
     comment จึงโดนประมวลผลเป็น JS template literal ตรง ๆ
     - โค้ด `r'|\1'` → compiled `r'|\1'` ✅ ผ่านตรง ๆ
     - comment `r'|\1'` → ⛔ *"Octal escape sequences are not allowed"*
     - comment `r'|\\1'` → compiled `r'|\1'` ✅
     นี่คือสาเหตุที่แท้จริงของ error ที่ commit `3c02e61` เจอเมื่อ 2026-07-27 —
     มาจาก **comment บรรทัดเดียว** แต่ตอนนั้นเหมาว่าทั้งไฟล์ต้อง double
     สแกนทั้ง `definitions/` แล้ว: มี **comment เดียว**ในโปรเจกต์ที่มี backslash คือ
     `view_dim_product_master.sqlx:45` → ใส่ `\\1` แล้ว
     **กฎสุดท้าย: โค้ดเขียน backslash ตัวเดียว / ใน `--` comment เขียนสองตัว**

  **ผลพลอยได้ — 4 ไฟล์ที่เคย flag ว่า "เสี่ยง" ไม่ใช่ปัญหา**
  `dim_sale_representative`, `dim_sale_representative_last`, `dim_quotation`,
  `deb_address_data` เขียน `\` ตัวเดียวอยู่แล้ว = **ถูกตามกฎที่แท้จริง** ไม่ต้องแก้
  (เดิม flag ไว้ว่าอาจ "เพี้ยนเงียบ" — เกิดจากกฎที่ผิด) ส่วน `\'` ใน validated/* ~35 ไฟล์
  ก็ไม่ใช่ปัญหาเช่นกัน เพราะอยู่ใน `${when(incremental(), ...)}` ซึ่งเป็น JS จริง

  **บทเรียน**
  - **อย่าอนุมานพฤติกรรม compiler — เปิด Compiled queries panel ดูของจริงก่อนเสมอ**
    การอนุมานผิดรอบเดียวลาม 4 commit และทำให้ UDF พังจริงบน production
  - **ห้าม copy `.sqlx` ไปวางใน BigQuery console** และ **ห้าม copy จาก console
    กลับเข้า `.sqlx` โดยไม่ตรวจ** — `67e779e` sync มาจาก console คือจุดที่รับ `\\` เข้ามา
  - ข้อยกเว้นที่ยังจริง: ไฟล์ `.js` ใน `includes/` เป็น JavaScript จริง **ต้อง double**
    (`function-data.js` → ``r'[\\n\\r\\t]'`` ถูกแล้ว) กฎ "ตัวเดียว" ใช้กับ `.sqlx` เท่านั้น
- **`create_all_function.sqlx` เคย drift จาก BigQuery** (sync แล้ว 2026-07-24): ไฟล์มี
  UDF แค่ 4 ตัว **ขาด `fn_order_type`** (ซึ่ง `view_dim_order` เรียกใช้อยู่) และ
  `fn_flag_scg` ประกาศพารามิเตอร์เป็น `milvnos`/`milcus` ขณะที่ของจริงคือ
  `mihvnos`/`mihcus` — สาเหตุน่าจะมาจากที่ action นี้ compile ไม่ผ่าน (octal `\1`)
  คนเลยไปแก้ UDF ตรงใน console แทน ตอนนี้ generate ใหม่จาก
  `function_dataset.INFORMATION_SCHEMA.ROUTINES` ครบ 5 ตัว ตรงกับ BigQuery แบบ
  byte-identical (verify ด้วยการจำลอง template-literal unescape แล้ว 5/5)
  **หลักการ: ไฟล์นี้ยึด BigQuery เป็นความจริง** — ถ้าจะแก้ UDF ให้แก้ที่ไฟล์แล้วรัน
  ไม่ใช่แก้ใน console
- ~~**ไฟล์เก่ายังมี inline reference (tech debt)**: `fact_transcation.sqlx` inline
  `${databuffet.DATABASE}.onetime.Transaction_Data_Mart`~~ **ปิดแล้ว 2026-08-20** —
  เขียนใหม่ทั้งไฟล์แล้ว ตอนนี้ทุก ref เป็น js-block Ref / `${ref()}` ครบ
  (ตรวจซ้ำ: `grep -c 'databuffet-nonprd' definitions/fact/fact_transcation.sqlx` = 0)
  และ `dependencies[]` อ้าง view ที่อ่านตรงแทนตารางเบื้องหลัง

## ข้อจำกัด environment

- การตรวจในเครื่อง, environment ที่ใช้ซ้ำ และข้อจำกัดการรัน: [run/debug guide](../how-to/run-and-debug.md)
- `bq` ต้องระบุ `--project_id=databuffet-nonprd` (default gcloud project เป็นตัวอื่น)
- INFORMATION_SCHEMA ระดับ region ถูก deny — ใช้ระดับ dataset
- การตั้ง `BACKFILL_DAYS` และผลต่อ workspace / schedule:
  [backfill procedure](../project_wiki/operations/running-and-troubleshooting.md#backfilling-more-than-one-day-backfill_days)
- **git ฝั่ง WSL กับฝั่ง Windows เห็น working tree ไม่ตรงกัน (CRLF)**: ฝั่ง Windows
  สะอาด แต่ `wsl git status` เห็นไฟล์เป็น modified นับสิบ เพราะ config line-ending
  คนละแบบ → Stop hook `doc-sync-check.sh` (อ่าน `git status` จาก WSL) จะเตือน
  doc-sync ทุกครั้งแม้ commit ครบแล้ว **เป็น false positive ไม่ใช่เอกสารขาด**

## เหตุการณ์ที่เคยเกิด

- **2026-05-23/24**: validated_mac5 datetime parse fail 2 วัน (รูปแบบ timestamp
  จาก raw เปลี่ยนชั่วคราว) — หายเองตั้งแต่ 05-25 ถ้าเกิดซ้ำให้ดู
  `parseFlexibleDatetime` ว่ารองรับ format ใหม่หรือยัง
- **2026-08-07/10**: `EXTRACT_CHQ_DATA` พังบน BigQuery
  (`Cannot parse regular expression: missing )`) จากการ deploy ด้วยการ paste
  ข้อความดิบเข้า console + กฎ backslash ในเอกสารที่สรุปผิดมาตั้งแต่ 07-27
  รายละเอียดเต็มอยู่ในหัวข้อ **พฤติกรรมที่ตั้งใจ** ด้านบน (bullet backslash)
- **แก้ 2026-08-17 — `CURRENT_DATE()` ไม่มี timezone** (`dim_customer`, `dim_project`)
  job รันเสร็จ ~06:07 น. ไทย = 23:07 UTC ของเมื่อวาน → `CURRENT_DATE()` คืนวันที่
  ย้อนหลัง 1 วัน**ทุกคืน** ทำให้ `projectDay` ต่ำไป 1 วันทุกแถวที่ `pjend` เป็น NULL
  และ `Total_contact_time_Year` ต่ำไป 1 ปีเฉพาะแถวที่ครบรอบวันนั้นพอดี
  แก้เป็น `CURRENT_DATE('Asia/Bangkok')` ทั้งหมดแล้ว ค่าถูกเองรอบรันถัดไป
  (dim rebuild ทุกคืน ไม่ต้อง backfill) ส่วน view มีผลทันทีที่ deploy
  **ตรวจซ้ำได้ด้วย**: `grep -rniE "current_date\(\)|current_datetime\(\)" definitions includes`
  ต้องได้ 0 บรรทัด (`CURRENT_TIMESTAMP()` 6 จุดใน `cdc_change_log`/`chq` ไม่ต้องแก้ —
  TIMESTAMP เป็นเวลาสัมบูรณ์)

- **2026-08-17 — `sale_by_branch_mch3` ไม่มี PRIMARY KEY มาตลอด** เพราะ `uniqueKey`
  และ `pk_key` เขียน `branch` ซ้ำ 2 ครั้ง (`["vendor_id","branch","mch3","branch"]`)
  → `ADD PRIMARY KEY` ผิด syntax แล้ว retry-loop ใน post_operation กลืน error
  จนครบ 10 รอบแบบเงียบ ๆ **ข้อมูลไม่เคยผิด** (`PARTITION BY a,b,c,b` ให้ผลเท่ากับ
  `a,b,c`) เสียแค่ PK ไม่ติด — ตัด `branch` ตัวซ้ำออกแล้ว PK จะติดตอน full refresh
  รอบถัดไป **บทเรียน**: retry-loop ที่ `EXCEPTION WHEN ERROR THEN retry` ปิดปาก
  error ถาวร ถ้าสงสัยให้เช็กของจริงด้วย
  `SELECT * FROM <dataset>.INFORMATION_SCHEMA.TABLE_CONSTRAINTS`

- **2026-08-25 — `dim_change_district` ไม่มี `schema:` ใน config มาตลอด**
  config เขียนแค่ `type: "table"` + `dependencies` + `tags` ไม่มี `schema` →
  Dataform ใช้ `defaultDataset` จาก `workflow_settings.yaml` (คือ `dataform`)
  ไม่ใช่ `dimension_table` ขณะที่ `fact_transcation` / `view_fact_transcation`
  อ้าง `${databuffet.DIMENSION_TABLE}.dim_change_district` เสมอ
  แก้แล้วใน `e0fe26c` — เพิ่ม `schema: databuffet.DIMENSION_TABLE` +
  `clusterBy: ["companyID","customerCode"]`
  ตรวจ 2026-08-26: dataset `dataform` **ว่างเปล่า** ไม่มีตารางตกค้าง
  **บทเรียน**: `schema:` ไม่ใช่ optional — ไฟล์ dim/fact ทุกไฟล์ต้องระบุ
  ตรวจซ้ำได้ด้วย `for f in definitions/dimension/*.sqlx; do grep -q "schema:" "$f" || echo "$f"; done`
  (ตอนนี้ได้ 0 บรรทัด)

- **2026-10-12 — `validated_mac5.mie` มีแถวซ้ำบน PK 98,474 แถว** (เจอตอน port query
  commission) พบ 3,339 PK ทุกตัวมี `miecus` NULL
  ซ้ำสูงสุด 219 ชุด ตั้งแต่ 2026-05-11 ทำให้ join `mie` ด้วยเลขเอกสารแตกแถว
  (order commission ของ ag01 ปี 2026 เกิน ~370,000 แถว) ตอนสแกน `mie_dummy` ไม่พบปัญหานี้
  สาเหตุและกฎป้องกันอยู่ที่ [coding-standard §4](../coding-standards/sqlx-coding-standard.md#4-การ-cast--ทำความสะอาดข้อมูล);
  ขอบเขตการแก้โค้ดอยู่ที่ [incremental string keys](../project_wiki/validated/validated-layer.md#null-in-a-uniquekey-column-2026-10-12).
  ปลายทางไม่กระทบ: ที่ใช้ `miecus` มีแค่ `fact_mir_vs`/`fact_mir_rs` (`mir.mircus = mie.miecus`)
  ซึ่งแถวลูกค้าว่างก็ join ไม่ติดทั้งก่อนและหลัง
  **ล้างข้อมูล `miecus` แล้ววันที่ 2026-10-12** เหลือ 4,155,993 แถว ซ้ำ 0;
  ตาราง downstream (`dim_aging`, `dim_customer_grade`, `dim_group_customer_grade`,
  `fact_mir_vs`, `fact_mir_rs`) rebuild ทุกคืน หายเอง
  ตรวจด้วย `COUNT(*) - COUNT(DISTINCT TO_JSON_STRING(STRUCT(<pk>)))`

### NULL-key cleanup (2026-10-12)

- **2026-10-12 — ไม่ได้เป็นแค่ latent: `mih2` กับ `cst` ซ้ำอยู่จริงแบบเดียวกับ `mie`**
  สแกน incremental ทั้ง 77 ตัวหลังแก้ `mie` แล้วพบว่า
  - ซ้ำอยู่ตอนนี้และเพิ่มขึ้นทุกคืน (A): `validated_mac5.mih2` ซ้ำ 134,332 แถว (963 PK สูงสุด 199 ชุด
    `mih2cus` NULL เพิ่มคืนละประมาณ 543 แถว ไม่มียอดเงินติดมา) กับ `validated_mac5.cst` ซ้ำ 3,152 แถว
    (32 PK ทั้งหมดเป็น `cststo` NULL ที่ `csttype = 'IS'` มี `cstquan` ส่วนเกินรวม 8,868 หน่วย ใน repo ไม่มีตารางไหนอ่าน `cst`)
  - มี key เป็น NULL แต่ยังไม่ซ้ำ (B): `mie.mievnos` 3 แถว, `cql.cqlbank` 3 แถว, `mih_dummy.mihvnos` 2 แถว
    ทั้งหมดมาจาก snapshot เก่า จะซ้ำเมื่อค่าว่างกลับมาใน raw
  - ยังไม่มี NULL แต่เสี่ยงสูงเพราะอ่าน source ทั้งก้อนทุกวัน (C1): `mie_dummy`, `mil_dummy`, `mih_dummy.mihcus`,
    `curated_mac5.curated_tbook_quotation.Running`

  ขอบเขตการแก้คีย์และพฤติกรรม consumer อยู่ที่
  [incremental string keys](../project_wiki/validated/validated-layer.md#null-in-a-uniquekey-column-2026-10-12).
  ตอนสแกนไม่พบ NULL ใน key ที่ไม่ใช่ string จึงไม่อยู่ในขอบเขตการแก้
  **ยังต้องล้างข้อมูลเก่าครั้งเดียวด้วยมือ** (guard hook บล็อก DML) สำหรับ `mih2`, `cst`, `mie`, `cql`, `mih_dummy`
  คือแปลง NULL เฉพาะคีย์ string ที่แก้เป็น `''` แล้วเหลือ 1 แถวต่อ PK (เก็บ asatdate ล่าสุด)
  **ยังไม่ได้ล้างตามบันทึกการสแกนนี้** ควรล้างหลัง deploy; การล้าง `mie.miecus` ด้านบนทำแล้ว
  แต่ `mie.mievnos` ยังเป็นงานค้างแยกต่างหาก
  ถ้าไม่ล้าง แถวเก่าที่เป็น NULL กับแถวใหม่ที่เป็น `''` จะไม่ match กัน (`mih2` จะได้แถว `''` เพิ่ม 543 แถวครั้งเดียว `cst` 8 แถว)
  ตารางที่อยู่เฉพาะ C1 (`mie_dummy`, `mil_dummy`, `curated_tbook_quotation`) ไม่ต้องล้างตามผลสแกนนี้;
  `mih_dummy` ยังต้องล้างคีย์ `mihvnos` ในกลุ่ม B
  ส่วนที่ยังไม่ได้แก้ (ตัดสินใจไว้แล้ว): latent อื่น ๆ (cis360, master_sku, mastersku, saleout_mdt, `cps`, `rcv`, `curated_mih`,
  `curated_saleout_mdt`), `curated_mil` ที่แบ่งบรรทัดเป็น 2 แถวตั้งใจแต่ key ไม่มีตัวแยก split, และ `curated_product`
  ที่ `updatePartitionFilter` 7 วันทำให้ซ้ำ

## การตัดสินใจเชิงออกแบบ

- **2026-10-28 — DERP: เพิ่ม raw + validated ของ 28 ตาราง crm/sales และเปลี่ยน `inventory_item_price` เป็น incremental**

  ตามโครงสร้าง GCS: โฟลเดอร์ที่มี partition `ASATDATE=YYYYMMDD` = incremental → ทั้ง 28 ตาราง
  (`crm_*` 23 + `sales_*` 5) เป็น incremental, key = `<table>_id` · คอลัมน์ยึดตามไฟล์ AVRO จริง
  ไม่ใช่ schema workbook (workbook เก่ากว่าไฟล์) · เวลาเป็นเวลาไทยอยู่แล้ว → `parseFlexibleDatetime`
  · คอลัมน์ `'YYYY-MM-DD 00:00:00'` 12 ตัวเก็บเป็น DATE · คอลัมน์ `'YYYY-MM-DD'` ล้วน 6 ตัวใช้
  `parseDateDash` เพราะ `parseFlexibleDatetime` คืน NULL
  · `inventory_item_price` เปลี่ยนจาก `type: "table"` อ่าน partition ล่าสุด เป็น incremental
  (key `inventory_item_price_id`) · **trade-off**: ยังไม่ purge แถวที่ถูกลบที่ต้นทาง (ทั้ง 29 ตาราง)
  แถวพวกนี้จะค้างใน validated · ตาราง `validated_derp.inventory_item_price` เดิมไม่มี partition —
  ต้องสร้างใหม่ครั้งแรก (full refresh ของ action นี้) ถึงจะได้ `partitionBy asatdate`

- **2026-10-28 — เปลี่ยนชื่อ D365 → DERP**

  source เดิมชื่อ D365 เปลี่ยนเป็น DERP ทั้งหมดใน repo: โฟลเดอร์ `definitions/initial/derp/`,
  `definitions/validated/derp/`, ชื่อไฟล์/action (`create_all_table_raw_derp`, `validated_schema_derp`),
  constant `RAW_DERP` / `VALIDATED_DERP` / `GCS_DERP` และ dataset `raw_derp` / `validated_derp`
  · โฟลเดอร์ GCS **ไม่เปลี่ยน** — `GCS_DERP` ยังเป็น `derp_temp` · ชื่อตาราง 3 ตัว (`inventory_*`) ไม่เปลี่ยน
  · คอลัมน์ `d365_*` ของ master_sku / mastersku / mds และคอลัมน์ที่ BI อ่าน (`prdD365Sku`,
  `ProductIDNewD365`) **ไม่ใช่ source นี้ — ห้ามเปลี่ยน**
  · ฝั่ง BigQuery ทำเสร็จแล้ว 2026-10-28: สร้าง `raw_derp` / `validated_derp` ใหม่ (รันทีละ action จาก
  compilation ของ nonprod `9f4fb18`: `create_all_table_raw_derp` → `validated_schema_derp` →
  `inventory_item_price`, `inventory_movement_journal_headers`, `inventory_movement_journal_entries`
  ไม่ได้รัน tag `initial`) · ตรวจเทียบกับตารางเดิมแล้ว: จำนวนแถวเท่ากัน (174,967 / 276,913 / 1,298,436),
  key ไม่ซ้ำ, แถวที่มีข้างเดียว 0, 43 partition ถึง 2026-10-27 · เจ้าของโปรเจกต์ลบ `raw_d365` /
  `validated_d365` แล้วในวันเดียวกัน · `daily_process` ตั้งแต่ 2026-10-29 เขียนลง `validated_derp`

- **2026-10-09 — Customer Report Info: สัญญาและลำดับ deploy**

  สัญญาข้อมูลและลำดับ deploy/Power BI refresh อยู่ที่
  [Customer Report Info + Customer Segment](../project_wiki/view/view-layer.md#customer-report-info--customer-segment-2026-10-01).

- **2026-10-02 — Customer Segment fallback**

  กฎ fallback และผลจำลองอยู่ที่
  [Customer Report Info + Customer Segment](../project_wiki/view/view-layer.md#customer-report-info--customer-segment-2026-10-01).

- **2026-10-02 — `CustomerReportName` ใช้ `mecdesc` เฉพาะบิล SCG**

  สูตรที่เลือก ลำดับ fallback คอลัมน์รายสาขาสำหรับ Power BI และผลกระทบหลัง rebuild อยู่ที่
  [Customer Report Info + Customer Segment](../project_wiki/view/view-layer.md#customer-report-info--customer-segment-2026-10-01).

- **2026-10-01 — Customer Report Info + Customer Segment: SK ลง view, Segment อยู่ใน dim**

  กฎ relationship, การเลือก Segment และข้อจำกัดอยู่ที่
  [Customer Report Info + Customer Segment](../project_wiki/view/view-layer.md#customer-report-info--customer-segment-2026-10-01).

- **2026-09-30 — `clean_company_prefix` ตัดคำลงท้ายซ้ำจนหมด + ตัด `จำกัด` หน้า `(สาขา…)`**

  **ปัญหา**: regex คำลงท้ายรันครั้งเดียว → `บริษัท โฮม สุขภัณฑ์ จำกัด (มหาชน)` ได้
  `โฮม สุขภัณฑ์ จำกัด` (ตัดแค่ `(มหาชน)`) และ `… จำกัด (สาขา…)` ไม่ถูกตัดเลย เพราะ `จำกัด`
  ไม่ได้อยู่ท้ายสุด · ชื่อใน `CustomerReportName` จึงไม่ตรงกับชื่อร้านที่ฝ่ายขายใช้

  **วิธี**: เพิ่ม step กลาง `(?:\s*(?:จำกัด|จก\.|\(มหาชน\)))+\s*(\([^()]*\))\s*$` → `' \1'`
  และให้ step คำลงท้ายเป็น `(?:…)+` (ซ้ำได้) · ทดสอบ body จากไฟล์จริงบน BigQuery 14 เคส ผ่าน

  **ผลกระทบที่วัดก่อน deploy** (`view_dim_invoice` เดิม vs inline สูตรใหม่ เทียบราย InvoiceSK):
  `CustomerReportName` เปลี่ยน ag01 **295 ชื่อ / 435,308 invoice** (ส่วนใหญ่สาขา ซีอาร์ซี ไทวัสดุ)
  + ac02 17 / ak02 3 / aa05 2 / ab01 1 ชื่อ · 2 ชื่อรวมเข้ากับชื่อที่มีอยู่แล้ว
  (`เนาวรัตน์พัฒนาการ`, `โฮมโปรดักส์ เซ็นเตอร์`) · consumer และกฎ relationship:
  [Customer Report Info + Customer Segment](../project_wiki/view/view-layer.md#customer-report-info--customer-segment-2026-10-01)
  — **Power BI ที่อ้างชื่อเดิมต้องปรับเอง**

  **ต้องทำหลัง deploy**: key ใน `mds_data_crc_shop_name_rename` 2 แถวจะไม่ match อีก
  (`ระยองภาคินทร์ จก.(SCG Dist)` 333 invoice, `แสงไพบูลย์เชียงราย จก.(เอสซีจี-บุญถาวร)` 194)
  ต้องแก้ `crc_shop_name` เป็นรูปใหม่ `ระยองภาคินทร์ (SCG Dist)` /
  `แสงไพบูลย์เชียงราย (เอสซีจี-บุญถาวร)` · อีก 4 แถวใน rename master match ไม่ได้อยู่แล้วก่อนแก้
  (key มีคำนำหน้า `บ.` ซึ่งฟังก์ชันตัดทิ้งเสมอ)

- **2026-09-24 — `dim_order.OrderStatus` คำนวณใหม่และ UPDATE ทุกคืน**

  **ปัญหา**: `OrderStatus` ถูกเขียนแค่ตอน INSERT (`UPDATE SET` ไม่มีคอลัมน์นี้) และคำนวณจาก
  `curated_mil` เฉพาะ `asatdate >= current_date - 1` → ใบที่ออก invoice ทีหลังวันสั่งค้าง
  `On Order` ตลอดไป (เช่น CRC69090169 สั่ง 09-03 invoice 6909001665 วันที่ 09-04 แต่ dim
  ยังเป็น On Order) และใบที่บรรทัด mil ไม่อยู่ใน window ตอน insert ได้ `NULL` ถาวร

  วัดบน nonprd 2026-09-24 (dim เทียบคำนวณใหม่): `On Order` ที่ควรเป็น Complete **53,012** /
  In Process **3,743** ใบ · `In Process` → Complete 995 · `NULL` → On Order **377,982** ใบ

  **วิธี**: ถอด `asatdate >= current_date - 1` ออกจาก CTE `mil` (คำนวณสถานะจาก mil ครบ
  window 4 ปี) + เพิ่ม `T.OrderStatus = S.OrderStatus` ใน `UPDATE SET` · SK/คีย์ไม่เปลี่ยน ·
  รันคืนแรกซ่อมย้อนหลังครบเอง (source ของ MERGE ครอบ PS ทั้ง 4 ปีอยู่แล้ว) — ไม่ต้อง backfill
  ค่าใช้จ่ายเพิ่ม ~0.79 GB/วัน (dry-run) ≈ ฿4.5/เดือน · ไม่ย้ายไป view เพราะ `curated_mil`
  สดรายวันเท่ากัน แต่ view จะคำนวณทุกครั้งที่ query · นิยามสถานะไม่เปลี่ยน
  (invoice ครบทั้ง qty และ sum = Complete)

  **รอบสอง (วันเดียวกัน) — เทียบยอดเงินด้วย `ROUND(..., 2)`**: หลังรันซ่อมเหลือ 3 ใบที่สลับสถานะ
  ทั้งที่ `curated_mil` เสร็จก่อน `dim_order` (ยืนยันจาก `JOBS_BY_PROJECT`: INSERT จบ 11:35:58 UTC,
  MERGE เริ่ม 11:36:02) — สาเหตุคือ `milSum` เป็น FLOAT64 และ `SUM()` ไม่รับประกันลำดับการบวก
  เช่น S68010080: IS 20,416.67×10 + 20,416.65×2 = 245,000.00 เท่ายอด PS แต่ได้ ±1e-11 สลับไปมา
  วัด: **13,794 บรรทัด** เท่ากันที่ 2 ตำแหน่งแต่ float ต่าง → **4,087 ใบ** ขึ้น In Process ผิด
  แก้ `cal_table` เป็น `ROUND(sec.milSum, 2) >= ROUND(main.milSum, 2)` · `dim_quotation`
  มี logic เดียวกัน (`sec.milSum >= main.total`) ยังไม่แก้

- **2026-09-23 — `fact_backlog_store` กรองบรรทัดให้ตรงกับ `fact_order_store`**

  **ปัญหา**: 3 ตาราง store ถูกใช้คู่กันใน Power BI แต่ `fact_backlog_store` รับบรรทัดจาก
  `cps` ตรง ๆ ขณะที่ `fact_order_store`/`fact_invoice_store` ตัด `milstype = 3` และ
  `LEFT(milstk,1) = 'บ'` ทิ้ง → backlog มีบรรทัดที่อีกสองตารางไม่มี เทียบระดับบรรทัดไม่ได้

  **วิธี**: เพิ่ม CTE `mil_line_scope` (`SELECT DISTINCT company_id, milVnos, milStk`
  จาก `curated_mil` ที่ `milType='PS'` + เงื่อนไขสองข้อข้างบน **ลอกมาคำต่อคำ**) แล้ว
  `INNER JOIN` บน (company_id, cpsVnosID, cpsStkID) — ใช้ `curated_mil` ไม่ใช่
  `EXISTS` ไปยัง fact อื่น เพราะรีโปนี้ไม่มี dependency fact→fact ที่ไหนเลย

  วัดบน nonprd 2026-09-23: 328,620 → **310,590 แถว** (ตัด 18,030 แถว, qty 4,419 = 3.3%)
  distinct SK = 310,590 เท่ากัน **ไม่มี fan-out**; ตัวเลขตรงกับการทดสอบด้วย
  `EXISTS` ไปยัง `fact_order_store` ทุกตัว

  **trade-off ที่ยอมรับ**: backlog ไม่ใช่ภาพงานค้างที่ครบอีกต่อไป — 18,029 แถวที่ตัดออก
  เป็นบรรทัดที่ `milstype = 3` ล้วน (มีอยู่จริงใน `mil` ไม่ใช่ขยะ) อีก 1 แถวไม่มีบรรทัดใน
  `mil` เลย ใครต้องการยอดค้างทั้งหมดต้องไปอ่าน `validated_mac5.cps` ตรง ๆ

  **ข้อเท็จจริงที่วัดไว้ตอนพิจารณา (กันวิเคราะห์ซ้ำ)**:
  - `mil.milcut` เป็นธง boolean มีแค่ **-1 กับ 0** ไม่ใช่จำนวนที่ส่งแล้ว →
    **คำนวณ backlog จาก `mil` ไม่ได้** ต้องใช้ `cps.cpsstkcut1` เท่านั้น
  - `cps.cpsstkreq` กับ `mil.milquan` เป็นเลขเดียวกันแทบ 100% (จับคู่ 433,428 คู่
    ต่างกัน **6 คู่**) → ของที่ `cps` มีอยู่คนเดียวคือ `cpsstkcut1`
  - `cps` เป็น snapshot รายวัน บรรทัดที่ปิดงานแล้วจะหายจาก snapshot ล่าสุด →
    **ห้ามเปลี่ยน `cps_latest` เป็น `QUALIFY ROW_NUMBER() PARTITION BY (company_id,
    cpsvnosid, cpsstkid)`** จะลากแถวที่ปิดแล้วกลับมา 2,033,785 แถว + ทิ้งแถวซ้ำใน
    snapshot เดียวกัน 38,255 แถว ทำให้ backlog พอง **5.1 เท่า** (qty 356,551 → 1,823,031).
    `QUALIFY asatdate = MAX(asatdate) OVER (PARTITION BY company_id)` เท่าของเดิมเป๊ะ
    (diff 0 ทั้งสองทาง, bytes เท่ากัน) แต่ **เลือกคงท่าเดิม `INNER JOIN MAX` ไว้**
  - `LEFT(cps.cpsStkID,1) not in ('บ')` ใน `WHERE` เป็น **no-op** — ไม่มีแถวขึ้นต้น `บ`
    ใน `cps` เลยสักแถว เก็บไว้เพื่อประกาศเจตนาให้ตรงกับอีกสองตาราง

  **เพิ่ม `milstk NOT LIKE 'TEST%'` ทั้ง 3 ตาราง store (วันเดียวกัน)**: เจอ backlog
  `BT69050113M` / `TEST-TANK` ที่ไม่มีฝั่ง order — สาเหตุคือ `fact_order_store` บน
  BigQuery ถูก build ตอน 16:35 จาก Dataform workspace ที่มีบรรทัด `TEST%` **ซึ่งไม่มีใน
  git** ส่วนอีกสองตารางไม่มี (ตรวจจาก query text ใน `JOBS_BY_PROJECT`) จึงใส่ให้ครบทั้ง
  `fact_order_store`, `fact_invoice_store`, `mil_line_scope` ใน `fact_backlog_store`
  ผลวัด: backlog −5 แถว, order/invoice 0 (order ตัวที่ deploy อยู่มีอยู่แล้ว, invoice ไม่มี
  สินค้า TEST) ต้นทาง `curated_mil` PS มี 2,100 บรรทัด `TEST%` ไม่มีตัวพิมพ์อื่น
  **บทเรียน**: ตัวกรองบรรทัดชุดนี้ลอกด้วยมือ 3 ที่ — รันจาก workspace ที่แก้ไม่ครบจะทำให้
  3 ตารางเพี้ยนกันเงียบ ๆ

  **ยังไม่ได้แก้**: `partitionBy` ของตารางนี้คือ `sDate` = วันที่ใบสั่ง **ไม่ใช่วันที่วัด
  backlog** และ rebuild ทับทุกคืน → ดู backlog ย้อนหลังไม่ได้ ถ้าต้องการกราฟรายวันต้อง
  เก็บทุก snapshot (`cps` มี `asatdate` ให้อยู่แล้ว)

- **2026-09-10 — `monitor_dataset.dataform_run_action.total_bytes` สูงเกินจริง 2 เท่า (ยังไม่แก้)**

  Dataform รันแต่ละ action เป็น **parent SCRIPT job 1 ตัว + child statement 8 ตัว**
  และ `total_bytes_billed` ของ parent **เท่ากับผลรวมของ child พอดี** (parent ครอบ child
  อยู่แล้ว) แต่ collector (Cloud Run `alert-dataform` — อยู่นอก repo นี้) เอามาบวกกัน
  ตัวเลขใน monitor จึงเป็น 2 เท่าของ bytes ที่ถูกคิดเงินจริง

  วัดจาก `region-us-central1.INFORMATION_SCHEMA.JOBS_BY_PROJECT` คืน 2026-09-09:

  | action | parent (จริง) | children | parent+children | ที่ monitor บันทึก |
  |---|---:|---:|---:|---:|
  | `mil` | 1,756 MB | 1,756 | 3,513 | 3,512 |
  | `mih` | 829 MB | 829 | 1,659 | 1,657 |
  | `mie` | 513 MB | 513 | 1,026 | 1,025 |
  | `mir` | 457 MB | 457 | 914 | 913 |
  | `mie_dummy` | 58 MB | 58 | 115 | 114 |

  **ผลกระทบ**: baseline "~117 GB/คืน" ในสกิล `check-runs` และทุกตัวเลข bytes/cost ที่
  อ้างจากตารางนี้ **ต้องหารสอง** (ของจริง ~58 GB/คืน) `duration_sec` กับ `status`
  ไม่ได้รับผลกระทบ
  **วิธีเลี่ยง**: ถ้าต้องการ bytes ที่คิดเงินจริง ให้ query
  `INFORMATION_SCHEMA.JOBS_BY_PROJECT` ที่ `parent_job_id IS NULL` (นับแค่ parent)
  — region-level view นี้ใช้ได้ ต่างจาก `INFORMATION_SCHEMA` ระดับ region อื่นที่ถูก deny

- **2026-09-10 — `mih`/`mil`/`mir` เพิ่ม TEMP table + DELETE ราย document ก่อน MERGE**

  **ปัญหา**: PK ของ `mil`/`mir` เป็นระดับ**บรรทัด** (`...listno`) แต่ Dataform
  incremental ทำได้แค่ upsert — บรรทัดที่ต้นทางลบทิ้งจะคาอยู่ใน validated ด้วย
  `asatdate` เก่าตลอดไป และถูกนับซ้ำ ไม่มี error ไม่มี NULL ไม่มีสัญญาณอะไรเลย
  (เหมือนเคส `AgingSK` ด้านล่าง)

  ตัวอย่างจริง `ag01/IS/6907004392`: `millistno` 1 (asatdate 2026-09-09) กับ
  `millistno` 2 (asatdate 2026-08-23) เป็น **สินค้า/จำนวน/ยอดเดียวกัน**
  (ECO-04/GR-2000L, 5 ตัว, 25,100) เพราะต้นทางเปลี่ยนเลข listno → ใบนี้ยอดกลายเป็น
  50,200

  วัดบน nonprd 2026-09-10:

  | ตาราง | แถว/เอกสาร | บรรทัดค้าง | ยอดที่นับซ้ำ | ผลของการเปลี่ยน |
  |---|---:|---:|---:|---|
  | `mil` | 3.12 | 476 | 9.2 ล้านบาท (`milsum`) | ล้าง 473 บรรทัด/รัน |
  | `mir` | 3.49 | 506 | 10.4 ล้านบาท (`mirsum`) | ล้าง 504 บรรทัด/รัน |
  | `mih` | 1.00 | 0 | — | **ไม่เปลี่ยนอะไร** (doc key = PK) ทำไว้ให้เข้าชุดกับ `mil` |

  **วิธี**: **config ไม่เปลี่ยนเลย** (`type: "incremental"` + `uniqueKey` เดิม) —
  `pre_operations` สร้าง `CREATE OR REPLACE TEMP TABLE new_data_<table>` จาก batch วันนี้
  (อ่าน raw รอบเดียว) แล้วยิง `DELETE` เอกสารทั้งใบที่อยู่ใน temp ครอบด้วย
  `when(incremental())` ส่วน body เหลือ `SELECT * FROM new_data_<table>` → MERGE ด้วย
  `uniqueKey` เดิม ซึ่งเข้าเงื่อนไข INSERT เพราะแถวเก่าถูกลบไปแล้ว
  รายละเอียดและข้อบังคับ: `document/project_wiki/validated/validated-layer.md`

  **`mie`/`mie_dummy` ไม่ทำด้วยตั้งใจ**: PK มี `mieday/miemonth/mieyear/miecus`
  ทำให้ `(mietype, mievnos)` เดียวมีได้หลายแถวโดยชอบธรรม ถ้าลบราย `(type, vnos)`
  จะ**ลบทิ้ง 67,946 แถวจาก 4,744 ใบ** ที่ batch ไม่ได้ส่งกลับมา (มากกว่า `mil`/`mir`
  ราว 140 เท่า) — ถ้าจะทำ ต้องหา doc key ที่ถูกต้องของ `mie` ก่อน

  **trade-off ที่ยอมรับ**: DELETE ลงก่อน MERGE → ถ้า MERGE พังหลัง DELETE เอกสารชุดนั้น
  จะหายจนรันรอบถัดไป (ทางกลับกันเกิดไม่ได้ เพราะ Dataform fail ทั้ง action เมื่อ
  `pre_operations` fail จึงไม่มีกรณี insert ซ้ำโดยไม่ได้ DELETE)

  **`curated_mil` ต้องแก้ตามด้วย (วันเดียวกัน)**: ถ้าล้างแค่ validated แต่ curated ยังลบ
  ด้วย PK ระดับบรรทัด จำนวนแถวต่อเอกสารจะไม่เท่ากันสองชั้น วัดได้ **477 แถว /
  9.25 ล้านบาท** (ag01 387, ac02 42, ab01 31, ak02 10, aa05 7) จึงเพิ่ม 2 จุด —
  `pre_operations` สร้าง `new_data_curated_mil_base` + DELETE เอกสารทั้งใบ (ครอบทุกบริษัท
  ตาม window 1 วัน ลบ 970,161 แถว ในนั้นเป็นแถวค้าง 474) และเปลี่ยน DELETE ใน
  `post_operations` จาก PK grain เป็น doc grain (ag01 ลบ 9,164,132 แถวแล้ว insert คืน
  ซึ่งเป็นพฤติกรรมเดิมอยู่แล้วเพราะ temp นั้นไม่มี window — แค่ทำให้แถวค้าง 387 ไม่รอด)
  **`curated_mih` ไม่ต้องแก้**: `uniqueKey` เป็น doc key อยู่แล้ว แถวค้าง 0

- **2026-08-11 — `view_dim_aging_history` derive `AgingSK`/`BillingSK` สดแทนที่จะเชื่อค่าที่เก็บไว้**

  **ปัญหา**: `dim_aging_history` เป็น snapshot สะสม (สิ้นเดือน + เมื่อวาน รวม 33
  snapshot / 1,023,308 แถว) แต่ `dim_aging.AgingSK` และ `fact_mir_vs.BillingSK`
  ปั้นด้วย `ROW_NUMBER()` ใหม่ทุกคืน → เลขที่ freeze ไว้ไปชี้คนละใบ
  **orphan = 0 ทุกตัว จึงไม่มี error ไม่มี NULL ไม่มีสัญญาณอะไรเลย**

  | SK | ต้นทาง | ชี้ผิดใบ |
  |---|---|---:|
  | `AgingSK` | `dim_aging` (`ROW_NUMBER`) | 993,491 / 1,023,308 = 97.1% |
  | `BillingSK` | `fact_mir_vs` (`ROW_NUMBER`) | 824,705 / 844,556 = 97.6% |

  อีก 4 SK ในตารางเดียวกันปลอดภัย (`CompanySK`/`CustomerSK`/`InvoiceSK`/`AgingRangSK`
  มาจาก dim ที่ใช้ MERGE + `max_sk` — ชี้ผิด 0)

  **ทางเลือกที่พิจารณา**: (A) เปลี่ยนชื่อเป็น `*_asat` (B) ตัดทิ้ง
  (C) ทำ SK ให้นิ่ง — ทั้ง MERGE และ `FARM_FINGERPRINT` (D) **derive ที่ view** ← เลือก

  **เหตุผลที่เลือก D**: `dim_aging_history` เก็บ natural key ไว้ครบอยู่แล้ว
  (`companyID` + `cfsVnosID` + `cfsTypeID`) จึง join กลับหาต้นทางได้เลย
  — ไม่ต้องแตะ `dim_aging` / `fact_mir_vs`, `ReceiveSK` ไม่ต้อง renumber,
  ไม่ต้อง `UPDATE` ย้อนหลัง 995,548 แถว, และค่าที่ได้**สดเสมอ**แทนที่จะนิ่งแต่เก่า

  **ผลที่วัดแล้ว** (เทียบกับ view ตัวจริง): แถวเท่าเดิม 1,023,308 · คอลัมน์ 48 ตัว
  ชื่อครบ · payload (`OutStanding`/`DayRange`/`flagComplete`/natural key) diff = 0 ·
  `AgingSK` ชี้ผิด 993,491 → **0** (NULL 767 = ใบที่ปิดไปแล้วหลุดจาก `dim_aging`) ·
  `BillingSK` ชี้ผิด 824,705 → **0** และ NULL ลดจาก 178,752 → 127,919
  (50,833 แถวที่ตอน snapshot ยังหา billing ไม่เจอ วันนี้เจอแล้ว)

  **ข้อแลก**: SK สะท้อนสภาพ *วันนี้* ไม่ใช่ ณ วันที่ snapshot (แต่ของเดิมก็ตอบไม่ได้
  อยู่แล้ว เพราะผิด 97%) · ลำดับคอลัมน์ขยับ — `AgingSK`/`BillingSK` ย้ายจากตำแหน่ง
  6/8 มา 5/6 ชื่อครบเหมือนเดิม BI ที่อ้างด้วยชื่อไม่กระทบ

  **จุดที่ต้องระวังถ้าจะแก้ไฟล์นี้อีก**: `QUALIFY` เปลี่ยนจาก `partition by asatdate,
  AgingSK` เป็น natural key (ตรวจแล้วไม่ซ้ำเลยสัก snapshot) — ต้องคงไว้ เพราะทั้ง
  `dim_aging` และ `fact_mir_vs` มีคีย์ซ้ำอย่างละ 1 คู่ ถ้าเอา `QUALIFY` ออกแถวจะบาน

- **2026-08-11 — `view_dim_aging` join `dim_aging_rang` ด้วย CompanySK จริง**

  **ปัญหา**: เงื่อนไข join เขียนเป็น `on raw.CompanySK = raw.CompanySK` (เทียบกับ
  ตัวเอง = TRUE เสมอ) → ทุกบริษัทไปหยิบช่วง aging ของ `ag01` มาใช้ พบตอนสแกน SK
  2026-08-11 และตรงกับ view บน BigQuery (ไม่ใช่ console drift)

  **ตัดสินใจ (ผู้ใช้สั่ง)**: แก้เป็น `raw.CompanySK = dim_aging_rang.CompanySK`
  แม้จะทำให้ข้อมูลบางส่วนกลายเป็น NULL — ถือว่า aging range เป็นของแต่ละบริษัท

  **ผลกระทบที่วัดแล้ว** (จำนวนแถวรวมเท่าเดิม 1,575,748 ไม่มีแถวหาย):

  | companyID | เสีย `AgingRangSK` | ในจำนวนนั้นโผล่ที่ `view_aging_ri` |
  |---|---:|---:|
  | `ak02` | 5,887 | 2,309 |
  | `aa05` | 2,434 | 124 |
  | `ac02` | 1,870 | 525 |
  | `ab01` | 98 | 33 |
  | **รวม** | **10,289** | **2,991** |

  `ag01` 1,564,616 แถวไม่กระทบ · snapshot เก่าใน `dim_aging_history` ไม่กระทบ
  (เก็บค่าที่คำนวณไว้แล้ว) แต่ snapshot รอบถัดไปจะเริ่มมี NULL

  **เงื่อนไขปิดเคส**: ให้ฝั่ง mds เพิ่ม aging range ให้ aa05/ab01/ac02/ak02 ใน
  `mds_data_aging_rang_master` (ตอนนี้มีแต่ `ag01` 8 ช่วง active + `companyID 999`
  อีก 3 แถว inactive) แล้ว 10,289 แถวจะกลับมาเอง ไม่ต้องแก้โค้ดอีก

- **2026-08-10 — `BACKFILL_DAYS` สำหรับ incremental window ของ validated/curated**

  **ปัญหา**: incremental window hardcode `CURRENT_DATE('Asia/Bangkok')-1` ทุกจุด
  พอ source พังหลายวัน (เช่น `mih` พัง 3 วัน) เก็บย้อนหลังไม่ได้ ต้อง full refresh
  ทั้งตารางอย่างเดียว

  **ที่เลือกทำ**: เปลี่ยนเป็น
  `DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY)`
  74 จุด / 52 ไฟล์ (validated mac5+cis360+mastersku และ curated) — ปรับ var
  ชั่วคราวแล้วรัน จากนั้นตั้งกลับ ขั้นตอนอยู่ใน
  [running-and-troubleshooting.md](../project_wiki/operations/running-and-troubleshooting.md)

  **ที่จงใจไม่แตะ** (ความหมายไม่ใช่หน้าต่างย้อนหลัง — อย่าเอาไปผูกกับ var นี้):
  - `cdc/cdc_change_log.sqlx` — ใช้ `=` เจาะ partition เดียว ไม่ใช่ช่วง
    ถ้าเปลี่ยนเป็นช่วงจะเปลี่ยนสิ่งที่ CDC เอาไปเทียบ
  - `dimension/dim_aging.sqlx` `run_date` — เป็นวันที่ของ snapshot
    `DELETE ... >= run_date` แต่ `INSERT` วันเดียว → ถอยวันจะลบมากกว่าที่เขียนกลับ
  - `view/fact_view/view_fact_transcation.sqlx` — เป็นขอบบนของช่วง 4 ปี

  **ข้อควรรู้**:
  - สถานะ config และ fallback ปัจจุบัน: ดู
    [databuffet.js — Key facts](../project_wiki/includes/databuffet-js.md#key-facts)
  - รูปแบบนี้ nest `${databuffet.BACKFILL_DAYS}` ไว้ข้างใน
    `${when(incremental(), ...)}` ซึ่งไม่เคยมีในโปรเจกต์มาก่อน —
    **ยืนยันแล้วว่า compile ผ่าน** (ดู Compiled queries ของ `mih` 2026-08-10
    ออกมาเป็น `INTERVAL 1 DAY`)
  - รันซ้ำวันที่เก็บไปแล้วปลอดภัย เพราะ `QUALIFY ROW_NUMBER() ... ORDER BY
    asatdate DESC` คัดเหลือ 1 แถวต่อ PK อยู่แล้ว

## หนี้ทางเทคนิค / งานค้าง

- **`dim_product_series` hard-code ไว้ในไฟล์ (เพิ่ม 2026-10-02, `e57d635`) — งานค้าง**:
  2 แถว (`100001` TITAN, `999999` OTHERS) พิมพ์ไว้ใน `UNNEST([...])` จากไฟล์ Excel ของ BI
  ไม่ได้อ่าน `mds_dataset` · comment ในไฟล์บอกว่าให้ย้ายไป mds เมื่อ BI โหลดเข้าไปแล้ว ·
  จนกว่าจะย้าย series ใหม่ = ต้องแก้ `.sqlx` เอง ถ้าไม่แก้ เป้าของ series ใหม่ใน
  `dim_target_series_mdt` จะตกไปที่ `OTHERS` เงียบ ๆ · consumer: `dim_target_series_mdt`,
  view `onetime.Product_Attribute` · ดู [special-cases](../project_wiki/dimension/special-cases.md)
- **ของใน BigQuery ที่ repo ไม่ได้สร้าง** (สแกน `databuffet-nonprd` 2026-10-18 เทียบกับ
  `dataform compile --json` — ตรวจซ้ำก่อนลบทุกครั้ง) แบ่งเป็น 3 กลุ่ม:

  | กลุ่ม | ของ | ทำอะไรได้ |
  |---|---|---|
  | **โค้ดใน repo อ่านอยู่ — ห้ามลบ** (Dataform สร้างกลับให้ไม่ได้) | `dimension_table.dim_aging_history` (`dim_aging`, `view_dim_aging_history`) · `dimension_table.dim_districts` / `dim_provinces` / `dim_sub_districts` / `dim_geographies` (view ที่อยู่ลูกค้า) · `onetime.cfsinvclose2024` (`dim_aging`) · `onetime.mapping_invoice` (`fact_transcation`, `view_fact_transcation`) · `onetime.saleout_lastyear_monthly` (`curated_saleout_monthly_mdt` แหล่ง BI) · `process_dataset.mih_address_data` (`view_mih_address_data`) | เก็บไว้ · ต้องติดไปตอน deploy prod ด้วย ([deploy-to-prod Step 9](deploy-to-prod.md)) |
  | **ไม่มีโค้ดใน repo อ่าน (orphan / ของเก่า)** | `dimension_table.dim_zone_manager_mdt` (ถูกแทนด้วย `dim_zone_ta_mdt` ใน `b198e24` ตารางยังค้าง) · `dimension_table.dim_target_channel`, `dim_target_sale` · `fact_table.dim_mir` · `onetime.saleout_monthly_mdt` (แทนด้วย `curated_saleout_monthly_mdt` 2026-10-05) · `onetime.saleout_monthly_aug2026` · `onetime.mapping_invoice_backup20260818` · view `onetime.PowerBI_Data_Buffet_Transaction` (ไฟล์ย้ายไป `backup/` แล้ว) · `onetime.Table_Model_Invoice_Transaction` / `Table_Model_Target_DayOfWork` (เจ้าของคือ scheduled query `table_for_ai_chatwith_data` ไม่ใช่ repo) · `validated_allkons_commission.*` (7 ตาราง ข้อมูลเก่า) | ถามฝั่ง BI ก่อน — Power BI อาจยังต่ออยู่ · ลบได้เมื่อยืนยันว่าไม่มีใครใช้ |
  | **backup / dataset ชั่วคราว** | `validated_mac5`: `cpp_backup20260901`, `cps_backup20260901`, `cps_dummy_backup20260901`, `cql/cst/mie/mih2/mih_dummy_backup_20261012`, `mie_backup_20261012b` · dataset `mds_dataset_bak_20261003`, `onetime_backup20260821`, `raw_mac5_backup`, `temp_dim`, `peem_using` | เจ้าของ backup ตัดสินใจ · ไม่ต้องยกไป prod |

  `raw_d365` / `validated_d365` (ปัจจุบันคือ `raw_derp` / `validated_derp`) เคยอยู่ในกลุ่มนี้ (สร้างมือ 2026-10-16) — ตั้งแต่ `7819bef`
  repo สร้างเองแล้ว

- **2026-08-26 — ล้าง literal `"mds_dataset"` ออกหมดแล้ว** เดิม 36 ไฟล์ใน
  `definitions/dimension/` เขียน `schema: "mds_dataset"` ตรง ๆ (ผิด hard rule ข้อ 3)
  ทั้งที่ constant `MDS_DATASET` มีอยู่ตั้งแต่ 2026-05-31 — เกิดจาก template ที่ใช้
  generate dim รอบใหญ่ (`694e996` "add process mds to dim - phase2") ยังเป็นตัวเก่า
  แก้เป็น `databuffet.MDS_DATASET` ทั้งหมดใน `b746f93` ค่าเหมือนเดิมเป๊ะ ผล compile ไม่เปลี่ยน
  ตอนนี้ `grep -rn '"mds_dataset"' definitions` ต้องได้ 0 บรรทัด
- **`dim_pump_information` (เพิ่ม 2026-08-26) เป็น dim ตัวเดียวที่อ่านจาก fact**
  `dependencies: ["fact_transcation", ...]` แต่ tag เป็น `dimension_daily` ส่วน
  `fact_transcation` เป็น `fact_daily` → **ถ้ารัน tag แยกกันโดยไม่ติ๊ก dependencies
  จะอ่าน fact ของเมื่อวาน** (คลาสเดียวกับ `dim_aging` ที่ขึ้นกับ `fact_mir_vs`)
  SK (`PumpSK`) ปั้นใหม่ทุกวันด้วย `ROW_NUMBER()` — ห้าม persist ข้ามวัน
  consumer เดียวคือ `view_fact_transcation` ซึ่ง join กลับด้วย natural key 4 ตัว
  `CompanySK` × `IFNULL(milStk,'')` × `FlagNewProductMKT` × `IFNULL(RegionID,'')`
  จึง re-derive สดทุก query — ไม่ได้เก็บ `PumpSK` ไว้
  **ประวัติ**: ตอนเพิ่มครั้งแรก (`b746f93`) key ไม่มีบริษัท ทำให้ซ้ำ 57 key เพราะ
  รหัส `milStk` เดียวกันมีอยู่ทั้งใน ag01 (ได้แบรนด์จริง) และ ac02 (ได้ `OTHERS`)
  — `milStk` unique แค่ภายในบริษัท แก้แล้วใน `91e120d` โดยเพิ่ม `CompanySK`/`CompanyID`
  เข้า `SELECT DISTINCT` และเพิ่ม `trans.CompanySK = pump.CompanySK` ในฝั่ง view
  ตรวจ 2026-08-26 หลัง rebuild: **ซ้ำ 0 key** (ทดสอบด้วยรูป `IFNULL()` ตรงตามที่ view
  join จริง) · 34,645 แถว · ถ้าถอด `CompanySK` ออกจาก key ตอนนี้จะซ้ำ 568 key
  **ข้อควรระวังถ้าเพิ่มคอลัมน์ในอนาคต**: `SELECT DISTINCT` ทำให้ทุกคอลัมน์ที่ใส่เข้าไป
  กลายเป็นส่วนหนึ่งของ key โดยปริยาย
- SK ที่ยังไม่รู้เจ้าของ (จาก FK scan 2026-07-09): `BillingSK` (หา dim ต้นทางไม่พบ),
  `DueAvgCollectSK`/`InvAvgCollectSK` (น่าจะ role-play ของ dim_avg_collection_score),
  `DueGradeSK`/`InvoiceGradeSK` (น่าจะ role-play ของ dim_grade)
- ไม่มี Dataform assertions เลย — ถ้าจะเพิ่ม data-quality checks ต้องเริ่มจากศูนย์
- ~~Slack run-monitor ยังไม่ deploy~~ **deploy แล้ว (ยืนยัน 2026-08-17)**:
  Cloud Run service `alert-dataform` (และ `alert-ms-team`) รันอยู่บน
  `databuffet-nonprd` เขียนผลลง `monitor_dataset.dataform_run_action`
  วันละครั้งเวลา 07:00 น. ไทย · partition `run_date` เก็บ 90 วัน ·
  ค่า `status` มีแค่ `SUCCESS`/`FAILED` — ใช้ skill `check-runs` ดูสรุป
- Tag ที่ประกาศแต่ไม่ใช้: `dimension_monthly`, `fact_monthly`, `fact_yearly`
  (`curated_full` / `curated_incremental` ใช้แล้วกับ curated ชุด SALEOUT_MDT ·
  `onetime` เป็นชื่อ dataset ไม่ใช่ tag)
- **`cps` เคยกอง snapshot ทุกวันโดยไม่ dedup — แก้แล้ว 2026-09-01** (`105870e add pk key`):
  เดิม `cps.sqlx` ประกาศ `uniqueKey: []` ทำให้ตารางมี **164,093,041 แถว** (ag01)
  กระจายบน 238 `asatdate` ทั้งที่ข้อมูลจริงวันละ ~482K แถว · แก้โดยใส่
  `uniqueKey: ["company_id","rowguid"]` เหลือ **3,429,587 แถว** (เล็กลง 48 เท่า)
  `rowguid` unique เป๊ะ NULL 0 · ผลพลอยได้: วันที่ job ขนซ้ำ (2026-08-20 ขน 5 เท่า,
  08-24 ขน 3 เท่า) ถูกยุบไปโดยโครงสร้าง ไม่ต้องตัดแถวซ้ำในชั้น fact อีก
- **ห้าม dedup `cps` ต่อ key แบบตารางอื่น** — `mih`/`mil`/`deb` ใช้
  `QUALIFY ROW_NUMBER() PARTITION BY pk ORDER BY asatdate DESC` ซึ่งถูกกับตารางที่แถว
  อยู่ถาวร แต่ **แถวใน `cps` หายไปเมื่อตัดของครบ** · วัด 2026-09-01: key ตลอด 238 วัน
  = 2,806,672 แต่วันล่าสุดมี 482,624 → dedup ต่อ key จะชุบชีวิตงานที่ปิดแล้ว 2.3 ล้านบรรทัด
  ต้องใช้ `WHERE asatdate = MAX(asatdate)` ต่อบริษัท (ทำไว้แล้วใน `fact_backlog_store`)
- **`dim_product_master` และ `dim_sale_representative` fan out เมื่อ join ด้วย natural key**
  (วัด 2026-09-01): `dim_product_master` มี `(CompanySK, ProductCode)` distinct 117,383
  จาก 117,419 แถว → **ซ้ำ 36 code** · `dim_sale_representative` มี
  `(CompanySK, EmployeeID)` distinct 1,796 จาก 2,339 แถว → **ซ้ำ 543 แถว** เพราะเป็น
  `UNION ALL` ของ mds block กับ ledger block · fact ที่ join ต้อง `QUALIFY ROW_NUMBER()`
  ก่อน (ทำไว้แล้วใน `fact_*_store` ทั้งสามตัว) ส่วนพนักงานขายเลี่ยงไปใช้
  `validated_mac5.per` ตรง ๆ ซึ่ง PK unique จริง
- **`ar_sColB` / `ar_sColF` เก็บสีเป็น integer แบบ BGR ไม่ใช่ RGB** (ยืนยัน 2026-09-01):
  MAC5 เป็นระบบสาย Delphi (`TColor` = `$00BBGGRR`) · `255` = แดง (ห้ามส่งสินค้า,
  ยกเลิก Order), `65280` = เขียว (อนุมัติ), `65535` = เหลือง (รออนุมัติ)
  แปลงด้วย `FORMAT("#%02X%02X%02X", MOD(c,256), MOD(DIV(c,256),256), MOD(DIV(c,65536),256))`
  ถ้าอ่านเป็น RGB ตรง ๆ สีจะสลับแดง↔น้ำเงินกับหน้าจอ MAC5
- **`is_store_*` ถูกถอดออกจาก `fact_invoice_store` แล้ว (2026-09-03)** — เดิมคัดลอก 6
  คอลัมน์ boolean มาจาก Query "ยอดจ่าย" ตรง ๆ ซึ่งเดาสาขาจาก prefix ของเลขที่เอกสาร
  (`p1`–`p5` SUBSTR) และมีจุดที่ทับกันเอง: เอกสารที่เลขขึ้นต้น `MEMO-H` ได้ทั้ง
  `is_store_ktb` และ `is_store_hy` เป็น TRUE พร้อมกัน เพราะ `'MEMO-H'` ไม่อยู่ใน
  exclusion list ของ `p5` (มีแค่ MEMO-K/P/L/U) · **เจ้าของงานสั่งเอาออกทั้งชุด**
  เมื่อ `dim_store` (จาก `validated_mac5.sto`) พร้อมใช้แล้ว — สไลซ์สาขาให้ใช้
  `StoreSK` → `dim_store[StoreGroup]` ซึ่งเป็น dimension จริง ไม่ใช่การเดาจาก prefix ·
  `KTB` = ธนาคารกรุงไทย ไม่ใช่คลัง จึงไม่เคยมีใน `sto` อยู่แล้ว
- **`curated_mil` ฝั่ง `IS` แตกบรรทัดตามสัดส่วนพนักงานขาย — ห้าม QUALIFY ทิ้ง**
  (วัด 2026-09-01): `curated_mil` มี 4,344,147 แถวเทียบกับ `validated_mac5.mil` 4,339,108
  → **เกิน 5,039 แถว** เพราะบรรทัดเดียวถูกแตกตาม `percent_sale` (70/30, 50/50)
  โดย `milPer_raw` เก็บพนักงานคนเดิมไว้ · `miltype = 'PS'` ไม่มีปัญหานี้ (3,012,477 = distinct PK)
  **ตัวเลขที่พิสูจน์**: `SUM(milQuan)` ของ curated ทั้งหมด = 22,209,217.12 เทียบกับ validated
  22,209,216.72 (ต่างกัน 0.40 = เศษปัดจากการหารสัดส่วน) แต่ถ้า `QUALIFY ROW_NUMBER() = 1`
  เหลือแถวเดียวจะได้ 22,199,705.31 → **qty หาย 9,512 และ `milSum` หาย 141 ล้าน**
  ดังนั้น `fact_invoice_store` ใช้ grain ที่รวม `milPer` และเก็บ `percent_sale` ไว้
  (การตัดสินใจของเจ้าของงาน 2026-09-01: "แตกยอดให้พนักงานขาย ไม่ต้องยุ่ง")
- **`milStk` เทียบแบบไม่สนตัวพิมพ์ใหญ่-เล็กแล้ว (2026-09-03)** — `fact_order` join
  `dim_product_master` เปลี่ยนเป็น `lower(mil.milstk) = lower(dim_product.ProductCode)`
  และ `fact_invoice` join `fact_order` ด้วย `LOWER(milStk)` ทั้งใน `ON` และใน
  `QUALIFY ... PARTITION BY` ส่วน `FactOrderSk` ก็ `order by lower(mil.milStk)` ตามไปด้วย
  **ตัวเลขที่วัดได้ 2026-09-03**: `(company_id, milStk)` ของ `milType = 'PS'` ทั้งหมด
  16,283 ตัว → match แบบเดิม 16,173 → `LOWER()` **ได้เพิ่มแค่ 17 ตัว** และยังไม่ match
  อีก 93 ตัว (93 ตัวนี้คนละสาเหตุ ไม่ใช่เรื่องตัวพิมพ์ — ยังไม่ได้สอบ)
  **ข้อควรระวังที่ต้องเช็คซ้ำเวลาเพิ่มสินค้า**: ถ้า `dim_product_master` มี `ProductCode`
  สองตัวที่ต่างกันแค่ตัวพิมพ์ในบริษัทเดียวกัน join นี้จะ fan-out เป็น 2 แถวที่ `ProductSK`
  ต่างกัน และ `group by 1,...,12` ใน `fact_order` (คอลัมน์ 1 คือ `ProductSK`) จะไม่ยุบให้
  → ยอด `milQuan`/`milSum` คูณสอง · วัดแล้ว **ยังไม่มีคู่ไหนชนกันเลย (0 กลุ่ม)** ตรวจด้วย
  `SELECT companyID, LOWER(ProductCode) AS k FROM dimension_table.dim_product_master GROUP BY 1,2 HAVING COUNT(DISTINCT ProductCode) > 1`
  · `FactOrderSK` เลื่อนค่าจากการเปลี่ยน `order by` — ไม่กระทบเพราะ `fact_order` เป็น
  full rebuild และ consumer ทั้งสอง (`fact_invoice`, `view_fact_transcation`) rebuild ตามทุกคืน
- **`dim_store.ReportStore` (2026-09-03)** — คอลัมน์ใหม่สำหรับสไลซ์รายงาน:
  `lower(ifnull(stogroup, ''))` ที่ไม่อยู่ใน `kk/pk/lp/ub/hy` ยุบเป็น `'KTB'` ถังเดียว
  ที่เหลือคืน `stogroup` ตัวเดิม (ไม่ lower) · **`stogroup` ที่เป็น NULL ก็ตกเป็น `'KTB'`**
  เพราะ `ifnull` แปลงเป็น `''` ก่อน — ไม่ใช่ NULL · แถว Unknown `StoreSK = -1` ได้
  `'KTB'` (**เปลี่ยน 2026-09-25** — เดิม `'Unknown'` ดูหัวข้อถัดไป) · เป็นตัวแทนของ
  `is_store_*` ที่ถอดออกไปตอน 2026-09-03
  **`'KTB'` ที่นี่คือถังรวม "ที่เหลือทั้งหมด" ไม่ได้หมายถึงคลังของธนาคารกรุงไทย** —
  ชื่อพ้องกับ `is_store_ktb` เดิมแต่ความหมายไม่เหมือนกัน อย่าอ่านว่าเป็นสาขา ·
  commit เดียวกันนี้ลบคอมเมนต์อธิบายใน `dim_store.sqlx` ทิ้ง (ถูก re-save ทับจาก
  Dataform web IDE) — **เจ้าของงานตัดสินใจไม่เอากลับ** คำอธิบายอยู่ที่ไฟล์นี้กับ
  `project_wiki/dimension/inventory.md` แทน
- **`dim_store` แถว `-1`: `ReportStore` `'Unknown'` → `'KTB'` (2026-09-25)** — ตามคำขอ
  รายงาน Warehouse Group (Power BI rename `ReportStore` เป็น `Warehouse Group Report`)
  ให้ Unknown ไปรวมกับ KTB · **คง default SK `-1` ไว้** เพราะเป็น pattern เดียวที่ repo ใช้
  (ปล่อย NULL จะขึ้น `(Blank)` ใน Power BI · ชี้ไปคลังจริงก็ไม่ได้ เพราะ KTB เป็นถังรวม
  ไม่ใช่คลังเดียว) · `StoreNameT`/`StoreNameE` ยังเป็น `ไม่ระบุคลัง`/`Unknown` · ไม่ต้อง
  rebuild fact เพราะ SK ไม่เปลี่ยน
  **วัด 2026-09-25 ยอดที่ย้ายเข้า KTB**: order 7,874 แถว / 24,801 ชิ้น · invoice 67 / 191 ·
  backlog 415 / 11 · **ต้นเหตุส่วนใหญ่คือรหัสคลังที่ไม่มีใน `validated_mac5.sto`** (ag01):
  `FGON` 6,213 แถว order · `milSto` NULL 1,228 (+ invoice 63) · `FGKTB` 184 ·
  `FGHY (B)`/`FGLP (B)`/`FGUB (B)`/`FGPK (B)` รวม 196 — **ดูจากชื่อน่าจะเป็นกลุ่ม HY/LP/UB/PK
  แต่ตอนนี้ตกไป KTB** แก้ได้ที่ต้นทางด้วยการเพิ่มรหัสเข้า master `sto` · `AS02` 15 แถวมีใน
  `sto` แต่เป็นของ ag01 ขณะที่แถว order เป็น ab01 · **ab01 ไม่มีคลังใน `dim_store` เลย**
  (`sto` ไม่มีแถว ab01)
- **`fact_transcation` dedup: เพิ่ม `CompanySK` เข้า `QUALIFY ... PARTITION BY` (2026-09-03)** —
  เดิม partition ด้วย 6 คีย์เอกสาร (`milType, milVnos, milCus, milStk, milPer, milListno`)
  **ไม่มี `CompanySK`** ขณะที่คีย์ upsert (`DELETE ... WHERE EXISTS`) คือ
  `(milVnos, milType, CompanySK)` และข้อมูลมี 5 บริษัท → ถ้าวันไหนเลขเอกสารซ้ำข้ามบริษัท
  แถวของบริษัทหนึ่งจะถูก `QUALIFY` ทิ้งเงียบ ๆ ทั้งที่ upsert มองว่าเป็นคนละแถว
  **วัด 2026-09-03 ก่อนแก้**: `onetime.Transaction_Data_Mart` ในหน้าต่าง 4 ปี 2,655,284 แถว
  → ยุบเป็น 2,655,222 กลุ่ม (6 คีย์) → **กลุ่มที่คร่อม `CompanySK` มากกว่า 1 = 0**
  ดังนั้นการเพิ่ม `CompanySK` **เป็น no-op บนข้อมูลวันนี้** ไม่ใช่การแก้บั๊กที่กำลังเกิด
  แต่เป็นการปิดช่องไว้ล่วงหน้าให้ partition ตรงกับคีย์ upsert · แก้ 2 จุด
  (`final_part1`, `final_part2`) — ต้องแก้คู่กันเสมอ เพราะสอง CTE นี้ใช้ dedup ชุดเดียวกัน
  ตรวจซ้ำได้ด้วย: group by 6 คีย์ แล้ว `HAVING COUNT(DISTINCT CompanySK) > 1`
- **ทำ `milStk` ให้ไม่สนตัวพิมพ์ทั่วทั้ง repo (2026-09-03, ต่อจาก commit b14a0d4)** —
  สแกน `milstk` ทั้ง repo เจอ 66 บรรทัดใน 20 ไฟล์ แล้วใส่ `LOWER()` **สองฝั่งเสมอ**
  ให้เฉพาะจุดที่พิสูจน์แล้วว่าไม่ทำให้แถวงอก · **เกณฑ์ที่ใช้**: ฝั่งขวาต้องไม่มีรหัส
  ที่ต่างกันแค่ตัวพิมพ์ในกลุ่มเดียวกัน (วัดด้วย `GROUP BY key, LOWER(code) HAVING COUNT(DISTINCT code) > 1`)
  **ผลวัด 2026-09-03**: `validated_mac5.stk` 0 · `dim_product_master` 0 · `dim_stk_mkt` 0 ·
  `dim_cost_stk` 0 · `dim_rebate` (product) 0 · `fact_transaction_delivery` 0 ·
  `mds_data_change_marketinggroup_master` 0 → **ใส่ได้** ·
  `fact_quotation` **6 กลุ่ม** · `validated_mac5.tbook_quodetail` **6 กลุ่ม** → **ห้ามใส่**
  **จำนวนที่ได้เพิ่มถ้าใส่**: `stk`/`dim_product_master` 36 รหัส (จาก 28,635) ·
  `dim_stk_mkt` 27 · `fact_quotation` 9 · `dim_cost_stk` 0
  **จุดที่เว้นไว้ (ห้ามใส่ทั้ง 3 กลุ่ม)**:
  1. `fact_order.sqlx` join `fact_quotation` (`mil.milStk = fact_quo.StkCode`) — `fact_quotation`
     มี `StkCode` ต่างกันแค่ตัวพิมพ์ 6 คู่ (ag01: `COM-01/SB-1000L` vs `com-01/sb-1000L`,
     `FBWPCG1500` vs `Fbwpcg1500`, `T01-PVC-40X2400X10-025` vs `T01-PVC-40x2400x10-025` ฯลฯ)
     ถ้าใส่ `LOWER()` join จะได้ 2 แถว → `milQuan`/`milSum` เฟ้อ · **ถ้าจะทำ ต้อง `QUALIFY` dedup
     ฝั่ง `fact_quo` ก่อน** แบบที่ `fact_invoice.sqlx` ทำกับ `fact_order`
  2. `dim_quotation.sqlx` join `main.stkcode = sec.milstk` — `tbook_quodetail` ชนกัน 6 กลุ่ม
     (ต้นทางของ `fact_quotation` จึงชนแบบเดียวกัน)
  3. `fact_transcation.sqlx` ที่เทียบกับ `mds.ProductID` (ทั้ง `=` และ `REGEXP_CONTAINS`) —
     pattern ทั้ง 22 ตัวเป็นเลขกับอักษรไทย (`บ-0025`, `บ-124|บ-125|...`) **ไม่มีอักษรละตินเลย**
     `LOWER()` จึงเป็น no-op (วัดแล้ว match 5 = 5 ทั้งก่อนและหลัง) — ไม่ต้องแตะ
  **`PARTITION BY` ของ dedup ที่เปลี่ยนเป็น `LOWER(milStk)`** (`fact_transcation` 2 จุด +
  `view_fact_transcation` 1 จุด) วัดก่อนแก้ว่า **ยุบแล้วไม่มีแถวหาย = 0 กลุ่ม** ทั้งบน
  `onetime.Transaction_Data_Mart` และ `fact_table.fact_transcation`
  **`ORDER BY` ใน `ROW_NUMBER()` ที่ใส่ `LOWER()`** (`FactInvoiceSK`, `FactTransDeliverySK`,
  `PumpSK`) **ไม่มีผลต่อการ match** เปลี่ยนแค่ลำดับเลข SK — ปลอดภัยเพราะทั้งสามเป็น
  full rebuild และ consumer ก็ rebuild ตามทุกคืน (ใส่เพื่อให้ตรงกับ `FactOrderSk` ที่ b14a0d4 ทำไว้)
  **⚠️ view 3 ตัวต้องไป `CREATE OR REPLACE VIEW` บน BigQuery เองด้วย** (เจ้าของงานเลือกไม่รัน
  Dataform เพื่อ deploy view): `onetime.Transaction_Data_Mart`,
  `onetime.Model_Invoice_Transaction`,
  `fact_view.view_fact_transcation` — ถ้าแก้ไม่ครบทั้ง 4 จะเกิด drift ระหว่าง repo กับ BigQuery
  (ตรวจด้วย skill `bq-drift-scan`)
  **บั๊กที่เจอระหว่างสแกน — ตกไปเพราะเลิกใช้**: `onetime.PowerBI_Data_Buffet_Transaction`
  join `stk` ด้วย `stkcode = milstk` **โดยไม่มีเงื่อนไข `company_id`** ขณะที่ `stkcode`
  ซ้ำข้ามบริษัทถึง 21,985 รหัส → fan-out ข้ามบริษัท (คนละเรื่องกับ case) ·
  ไฟล์ถูกย้ายไป `backup/view/onetime/` 2026-09-03 จึงไม่แก้
- **`onetime.PowerBI_Data_Buffet_Transaction` ย้ายไป `backup/` (2026-09-03)** —
  เจ้าของงานแจ้งว่าเลิกใช้แล้ว · view layer เหลือ **31 ไฟล์** (จาก 32) ·
  ผลข้างเคียง: บั๊ก join `stk` ที่ขาด `company_id` (fan-out ข้ามบริษัท 21,985 รหัส) ตกไป
  และ view ที่ต้อง `CREATE OR REPLACE VIEW` มือบน BigQuery ลดจาก 4 เหลือ **3** ตัว ·
  **หมายเหตุ**: การลบ `.sqlx` ไม่ได้ลบ view ใน BigQuery — `onetime.PowerBI_Data_Buffet_Transaction`
  ยังอยู่ แต่ไม่มีใครดูแลแล้ว ถ้าจะ drop ต้องสั่งเองบน console
  (`document/operations/deploy-to-prod.md` มีบรรทัด `DROP VIEW IF EXISTS` ของ prd อยู่แล้ว)
- **รอบสองของ `LOWER(milStk)` — 7 จุดที่รอบแรกเว้นไว้ (2026-09-03)** —
  เจ้าของงานสั่งให้ใส่เพิ่ม วัดผลกระทบทีละจุดก่อน:
  **จุดที่กระทบข้อมูลจริง — ใหญ่สุดในงานนี้ทั้งหมด**
  · `dim_order.sqlx` 2 จุด (`mil.milstk = main.milstk` ใน `EXISTS` ของ `sec_table`
    และ `main.milstk = sec.milstk` ใน `cal_table`) — สองฝั่งเป็น **เอกสารต่างใบ**
    (`main_table` = บรรทัด PS ใบสั่งซื้อ, `sec_table` = บรรทัด IS ใบกำกับที่โยงด้วย `milLinkVcno`)
    ตัวพิมพ์ของรหัสสินค้าจึงต่างกันได้ · **วัด 2026-09-03: IS 3,660,081 คีย์ →
    จับ PS ได้เพิ่ม 412 คีย์** ซึ่งเดิมตกเป็น `item_status = 'On Order'` ผิด
    ที่จริงต้องเป็น `'Complete'` หรือ `'In Process'`
  **จุดที่เป็น no-op (ใส่เพื่อความสม่ำเสมอ วัดแล้วได้เพิ่ม 0)**
  · `fact_transcation.sqlx` 2 จุด `trans.milstk = mds.ProductID` — pattern เป็นเลข/อักษรไทย
  · `view_fact_transcation.sqlx` 3 จุด (`pump.milStk`, `t2 = fact_invoice`, `t3 = fact_order`)
    — ทุกฝั่งสืบค่ามาจาก `curated_mil` สายเดียวกัน ตัวพิมพ์ตรงกันอยู่แล้ว
    (วัด: `t2_gain = 0`, `t3_gain = 0` จาก 2,430,311 คีย์)
  **fan-out**: ตรวจครบทุกฝั่ง = 0 กลุ่ม (`ps`, `is`, `fact_invoice`, `fact_order`)
  ~~412 คีย์นั้นจะยังไม่ถูกแก้ย้อนหลังเอง~~ — **หมดไปแล้ว 2026-09-24**: `dim_order`
  เลิกกรอง `asatdate` และ UPDATE `OrderStatus` ทุกคืน (ดู "การตัดสินใจเชิงออกแบบ" 2026-09-24)
- **`fact_*_store` 3 ตัว: ถอด `asatdate` แล้วเปลี่ยน partition (2026-09-03, commit 048f746 → 5e70f83)** —
  `048f746` ลบ `CURRENT_DATE('Asia/Bangkok') AS asatdate` ออกจาก SELECT ทั้ง 3 ไฟล์ **แต่ทิ้ง
  `partitionBy: "asatdate"` ไว้ใน config** → Dataform สร้าง `PARTITION BY asatdate` บน query
  ที่ไม่มีคอลัมน์นั้น = `Unrecognized name: asatdate` (พิสูจน์ด้วย dry-run บน BigQuery)
  `5e70f83` แก้แล้วเป็น `sDate` (backlog) / `mix_date` (order, invoice) — dry-run ผ่านทั้ง 3
  **บทเรียน**: `partitionBy`/`clusterBy` ใน config ไม่ได้ถูกตรวจตอน edit — เวลาถอดคอลัมน์
  ต้องเช็ค config คู่กันเสมอ · ถ้าไม่มี dataform CLI ตรวจได้ด้วยการขยาย `${ref()}` เอง
  แล้วยิง `bq query --dry_run` ครอบด้วย `SELECT <partition_col> FROM ( ... )`
  **ผลข้างเคียงของการถอด `asatdate`**: ไม่มี consumer ใน `definitions/` (ตรวจแล้ว 0 ไฟล์)
  แต่ **fact ทั้ง 3 เลิกบอกได้ว่าแถวมาจาก snapshot วันไหน** — ถ้ารายงาน Power BI เคยใช้
  คอลัมน์นี้จะพัง · `sDate` ให้ 3,619 partition (ย้อนถึงปี 2006) ห่างจากลิมิต 10,000 มาก
  **ขอบเขตวันที่ของ 3 fact** — เดิมไม่เท่ากัน (`fact_backlog_store` ไม่กรองเลย ย้อนถึง 2006)
  **แก้แล้ว 2026-09-15**: ทั้ง 3 ใบกรอง 4 ปี trunc-to-year เท่ากัน ดูรายการด้านล่าง
- **`FlagFree` มีนิยาม 2 แบบไม่ตรงกัน — ยังไม่แก้ (2026-09-03)** —
  · `fact_order_store` / `fact_invoice_store`: `milSum = 0` **OR** `ProductGroupMAC5 = '5000'`
  · `fact_backlog_store`: **`cpssumreq = 0`** OR `ProductGroupMAC5 = '5000'`
  คนละคอลัมน์ คนละ grain → สินค้าตัวเดียวกันได้ `Yes` ในหน้างานค้าง แต่ `No` ในหน้า Order ได้
  **ขอบเขต**: `cpssumreq = 0` = 33% ของ cps (158,325/482,790) · `ProductGroupMAC5 = '5000'`
  = 95 สินค้าจาก 117,458 · `milDesc LIKE '%ของแถม%'` ที่ถูก comment ออกกระทบ **281 บรรทัด**
  (ที่เขียนว่าของแถมแต่ `milSum != 0` → เปลี่ยนจาก Yes เป็น No)
  **fan-out ที่เหลืออยู่**: `fact_backlog_store` ใส่ `FlagFree` เข้า `GROUP BY` แต่ค่ามาจาก
  `cps.cpssumreq` ซึ่งเป็นค่าต่อแถว cps → **4,342 กลุ่ม (1.0% ของ 441,976)** จะแตกเป็น
  2 แถว (Yes + No) · ยอด `qty` ไม่เบิ้ล (SUM แยกกลุ่ม) แต่ Power BI เห็นสินค้าเดียวกันสองบรรทัด
  แก้ได้ด้วย `LOGICAL_AND`/`LOGICAL_OR` ให้เหลือ 1 แถวต่อ (order, product) พร้อมค่า `Mixed`
  **ข้อเสนอที่ยังค้าง**: ย้ายนิยามไป helper ไฟล์เดียว (`function-data.js` หรือไฟล์ใหม่
  `business-rules.js`) เพื่อไม่ให้กฎ “ของแถม” กระจายอยู่ 3 ไฟล์และเพี้ยนกันเอง

- **กรอง 4 ปีแยกแต่ละ fact ไม่พอ — ต้องกรองที่ `dim_order_dedup` ด้วย (2026-09-15)** —
  เดิม `fact_order_store`/`fact_invoice_store` ต่างกรอง 4 ปีด้วย**วันที่ของเอกสารตัวเอง**
  ผลคือใบกำกับปี 2024 ที่อ้างออร์เดอร์ปี 2021 **ผ่านตัวกรองของตัวเอง แต่ต้นทางถูกตัด**
  → กลายเป็นแถวกำพร้าที่มี `Invoice Qty` แต่ `Order Qty` ว่าง และไม่มีวันที่ให้เกาะใน
  `dim_calendar` (ปฏิทินเริ่ม 2022-01-01) → Power BI โชว์ `Date` ว่างทั้งคอลัมน์
  **ขนาดปัญหา (วัด 2026-09-15)**: ใบกำกับกำพร้า **3,238 บรรทัด · 19,379 ชิ้น**
  **ทางแก้ที่ใช้**: เพิ่ม `AND ord.mix_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'),
  INTERVAL 4 YEAR), YEAR)` เข้าไปใน CTE `dim_order_dedup` ของ **ทั้ง 3 fact** — เพราะ CTE นี้
  ถูก **INNER JOIN** ทุกใบ จึงบังคับให้ออร์เดอร์กับใบกำกับ "รอดไปด้วยกัน"
  **ผลหลังแก้**: กำพร้าเหลือ **14 บรรทัด · 33 ชิ้น** (0.0007%)
  **ตรวจแล้วว่า `bq` ไม่พังเพราะคอลัมน์**: `dimension_table.dim_order` มี `mix_date` ชนิด `DATE`

- **ใบสั่งขายที่มีแต่ค่าบริการ/สินค้า Sourcing จะหายทั้งใบจาก `fact_order_store` (2026-09-15)** —
  ตัวกรองบรรทัด (`milstype not in (3)`, `LEFT(milstk,1) not in ('บ')`, `TypeMarketing != 'Sourcing'`)
  ตัดเป็น**รายบรรทัด** ถ้าใบสั่งขายไม่มีบรรทัดเหลือเลย ใบนั้นจะหายจาก fact ทั้งใบ
  แต่ **ใบกำกับที่อ้างถึงยังอยู่** เพราะบรรทัดฝั่ง IS เป็นสินค้าคนละตัว
  **ตัวอย่างที่ตรวจแล้ว**: `TW65040767` สั่ง `บ-0008` ค่ายกขึ้นชั้น 1 บรรทัด (ตกทั้งคู่)
  แต่ใบกำกับ `6504009872` ส่ง `DE-49/SB-1000L` ถังน้ำ 2 ใบ + ลูกลอยของแถม → ผ่านครบ 3 บรรทัด
  · `S67030155` = PRESSURE SWITCH (Sourcing) ×2 + `บ-0103` ค่าจัดส่ง
  **ตัดสินใจ: ปล่อยไว้** — ถ้าเอา `fact_order_store` ไปกรอง `fact_invoice_store` ยอดที่ส่งจริง
  จะหายไปจากรายงานด้วย ซึ่งแย่กว่าการมีแถวที่ `Order Qty` ว่าง (กระทบแค่ 14 บรรทัด · 33 ชิ้น)

- **อัปเดต 2026-10-21**: `fact_invoice_store` เลิกกรองตามออร์เดอร์ทั้งหมด (`flagwarehouse`, `PO.วางบิล`, อายุ 4 ปีของออร์เดอร์, `order_gate`) และใช้ `LEFT JOIN dim_order` (ไม่เจอ = `OrderSK -1`) เพื่อให้ยอดจ่ายนับทุกใบกำกับ — ข้อ 2026-09-15 สองข้อด้านบนใช้กับ `fact_invoice_store` ไม่ได้แล้ว

- **ห้ามใช้ `fact_order_store` กรอง `fact_backlog_store` (2026-09-15)** —
  วัดผลกระทบแล้ว: กรองระดับ `OrderSK` จะตัด **212 บรรทัด · 9,627 ชิ้น = 6.6% ของยอดค้าง**
  · กรองระดับ `(OrderSK, ProductSK)` ตัด **18,534 บรรทัด · 13,255 ชิ้น = 9.0%**
  เหตุผล: ยอดค้างมาจาก `cps` ซึ่งเก็บบรรทัดที่ยังเบิกไม่ครบ — บรรทัดพวกนี้มักเป็นสินค้าที่
  ถูกตัดออกจาก `fact_order_store` ด้วยตัวกรองสินค้า (Sourcing / `milstype=3` / ขึ้นต้น `บ`)
  **ยอดงานค้างซึ่งเป็นหัวใจของรายงานจะหายไป** — ไม่คุ้มกับการลดแถวกำพร้า
- **`view_dim_order.FlagExpire`: `NULL` → `'No'` (console edit 2026-09-14, pull เข้า repo 2026-09-15)** —
  เดิม `ELSE NULL` แปลว่าเอกสารที่ `ExpireDays` ไม่เป็น null และยังไม่เลยกำหนด จะได้ `NULL`
  ไม่ใช่ `'No'` ทำให้รายงานที่ `COUNT`/filter ด้วย `FlagExpire = 'No'` นับไม่ครบ
  ตอนนี้ยึดตาม BigQuery เป็น `ELSE 'No'` แล้ว · **view นี้ถูกแก้บน console เป็นรอบที่สอง**
  (รอบแรก 2026-09-10 เพิ่ม `FlagExpire` + join `mds_data_document_expire_rule_master`)
  → เป็น view ที่ควรจับตาเรื่อง drift มากที่สุด เพราะถ้ารัน tag `view` ก่อน pull งานจะหาย
- **บทเรียนจากสแกน 2026-09-15: "ต่าง" ไม่ได้แปลว่า "drift ที่ต้องดึงกลับ"** —
  สแกนเจอต่าง 6 จาก 33 view แต่ **4 ใน 6 คือ repo ล้ำหน้าเพราะยังไม่ได้ deploy** ไม่ใช่
  console edit · วิธีแยกคือเทียบ `__TABLES__.last_modified_time` กับ
  `git log -1 --format=%ad -- <path>` ของไฟล์นั้น ถ้า commit ใหม่กว่า = รอ deploy
  ถ้า BigQuery ใหม่กว่า = console edit ที่ต้อง pull · **ถ้าดึงกลับหมดทั้ง 6 จะเป็นการ
  revert งานที่ commit ไปแล้ว** (เช่น CustomerFlag ชนก่อน DepCode ที่ commit 2026-09-15)
- **`view_dim_invoice`: qualifier `cust.` — จบแล้วโดยแก้ฝั่ง BigQuery (2026-09-15)** —
  repo ใช้ `clean_company_prefix(cust.debnamet)` ส่วน console เคยเป็น `(debnamet)`
  **ผลลัพธ์เท่ากัน** (มีแค่ `view_dim_customer` ที่มีคอลัมน์ `debnamet`, `dim_invoice` ไม่มี)
  แต่เจ้าของงานเลือกให้คงรูปมี qualifier เพราะอ่านง่ายกว่าและกัน ambiguous ถ้าวันหน้ามี
  ตารางอื่นใน scope ที่มี `debnamet` · **เคยวางแผนจะปล่อยให้ต่างถาวร แล้วเปลี่ยนเป็น
  แก้ฝั่ง BigQuery ให้ตรง repo แทน** — ตอนนี้ drift scan ขึ้น identical แล้ว
  **บทเรียน**: ถ้า repo "ถูกกว่า" แต่ค่าเท่ากัน ให้ deploy repo ทับ ดีกว่าปล่อยให้ scan
  ฟ้องทุกรอบจนคนเลิกเชื่อผลสแกน
