# Known Issues & Gotchas

รวมจุดที่รู้แล้วว่า "เป็นแบบนี้โดยตั้งใจ" หรือ "ต้องระวัง" — อัปเดตล่าสุด 2026-09-07

## คำสะกดผิดที่เป็น identifier จริง (ห้ามแก้)

| ที่ | คำ | หมายเหตุ |
|---|---|---|
| `definitions/fact/fact_transcation.sqlx` | `fact_transcation` | ชื่อไฟล์ + ตารางจริงใน BigQuery |
| `includes/controller/variables.json` | `CDC_DATESET` | คีย์ constant (ค่า `cdc_dataset` ถูกต้อง) |
| MASTERSKU JSON | `prdDiminsionData`, `SpeciFeild`, `dimFeild` | field จริงในข้อมูล |
| `FactOrderSk` vs `FactOrderSK` | casing ไม่คงที่ในไฟล์เดียวกัน | ใช้ตามที่ไฟล์นั้นใช้ |

## พฤติกรรมที่ตั้งใจ (อย่า "แก้")

- **mds dims 34 ตัวเป็น full daily rebuild** (ตัดสินใจ 2026-07-20): แปลงจาก MERGE
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
  - ⚠️ ยังไม่ได้ compile-verify (เครื่องนี้ไม่มี dataform CLI) — ต้องเช็คตอนขึ้น service:
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

- เครื่อง local WSL ไม่มี `dataform` CLI (`dataform` และ `npx dataform` fail ทั้งคู่)
- `bq` ต้องระบุ `--project_id=databuffet-nonprd` (default gcloud project เป็นตัวอื่น)
- INFORMATION_SCHEMA ระดับ region ถูก deny — ใช้ระดับ dataset
- `workflow_settings.yaml` เป็นค่าเฉพาะ environment — `BACKFILL_DAYS` ตั้งเองในแต่ละ
  workspace ไม่ได้ติดมากับ commit
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
- **2026-09-07 — `validated_saleout_mdt.saleout_hp` นับได้ 259 สาขา ทั้งที่จริงมี 137**

  **สาเหตุ**: ไฟล์ HomePro ส่งค่าครอบด้วย `="..."` (ร่องรอย Excel force-text) และ
  **ห้างย้ายคอลัมน์ที่ครอบได้** — ช่วง 2-4 ส.ค. 2026 (601 แถว) `="` ย้ายจาก
  `PERIODDATE` ไปอยู่ `SITENO` / `VENDORNO` / `ARTNO` แทน
  `saleout_hp.sqlx` แกะ `="` ให้แค่ 3 คอลัมน์ (`PERIODDATE`, `ARTEAN`, `VDARTNO`)
  ส่วน `SITENO` ใช้ `cleanString` ซึ่งทำแค่ TRIM → ค่า `="S107"` ติดเข้าตาราง

  **ผล**: สาขาเดียวปรากฏ 2 รูปแบบ (`S107` และ `="S107"`) →
  `COUNT(DISTINCT siteno)` = 259 · **ไม่มี error ไม่มี NULL ไม่มีสัญญาณอะไรเลย**
  และถ้ามีโค้ดที่แยกห้างด้วย `LEFT(siteno, 1)` จะได้ `=` แทน `S`/`M`
  → ยอดทั้ง HomePro และ Megahome หายไป 3 วันโดยเงียบ

  **ตรวจซ้ำได้ด้วย**:
  ```sql
  SELECT COUNT(DISTINCT NULLIF(CAST(TRIM(SITENO) AS STRING),'')) AS old_way,
         COUNT(DISTINCT NULLIF(CAST(TRIM(REGEXP_REPLACE(SITENO, r'^="|"$', '')) AS STRING),'')) AS unquoted
  FROM `databuffet-nonprd.raw_saleout_mdt.saleout_hp`
  ```
  ได้ `259` กับ `137` — วิธีที่แกะแล้วเหลือ prefix ที่ไม่ใช่ `S`/`M` แค่ 5 แถว คือ
  `CS01` (3) และ `EX99` Inter Company (2) ซึ่งเป็นรหัสจริงของห้าง ไม่ใช่ของสกปรก

  **บทเรียน**: กับต้นทางที่เป็นไฟล์ Excel **ห้ามล้างของสกปรกแบบเลือกคอลัมน์** —
  ห้างเปลี่ยนตำแหน่งได้ ต้องใช้ `REGEXP_REPLACE(x, r'^="|"$', '')` กับทุกคอลัมน์ข้อความ
  (ใช้ `cleanCode(col, pattern)` ที่มีอยู่แล้ว ส่ง pattern เข้าไป ไม่ต้องเพิ่ม helper)

  **จุดใกล้กันที่ยังไม่แก้**: `uniqueKey` ของ `saleout_hp` มี `crdate` (เวลาที่ห้าง
  สร้างไฟล์ เปลี่ยนทุกวัน) อยู่ในคีย์ → การขายเดียวกันจากไฟล์ต่างวันไม่ยุบเข้าหากัน
  แก้แล้วพร้อมกับการเพิ่ม `curated_saleout_mdt` — คีย์ใหม่คือ
  `siteno · artno · sale_date` ไม่มี `crdate`

- **2026-09-09 — Sales Out MDT: master data เข้า `mds_dataset` แล้ว 6 ตาราง · เกณฑ์แยก fact/dim**

  **เกณฑ์ที่ตกลงกับหัวหน้า**: *ข้อมูลที่คนกำหนดหรือดูแลไว้ล่วงหน้า = dim · ข้อมูลที่บันทึก
  จากเหตุการณ์ที่เกิดขึ้นจริง = fact* — ไม่ใช่ "มี measure = fact" ตามตำรา Kimball
  หลักฐานว่าเป็น convention ของรีโปอยู่แล้ว: target 6 ตารางอยู่ในชั้น dim ทั้งหมด
  (`dim_rate_target`, `dim_target_product_group*`, `view_dim_target_by_agent*`) และ
  `dim_target_product_group_by_sale` เก็บคอลัมน์ยอด `Amt`/`Qty`/`CalAmt`/`CalQty` ไว้ในตัว dim
  → เป้าขายออกและ market share ของ MDT จึงเป็น `dim_target_saleout_mdt` / `dim_market_mdt`
  ไม่ใช่ fact  **fact ของโปรเจกต์นี้เหลือแค่ยอดขายและสต็อก**

  **ตัด `dim_store_mdt` ออก** (เคยมี 7 แถวใน BigQuery ต้อง DROP ทิ้ง) — mds ไม่มีตาราง store
  master และห้างเป็นแค่ `region_id` คอลัมน์หนึ่งใน `mds_data_sales_branch_master`
  ห้างจึงเป็น degenerate `store_code STRING` ใน fact ทั้งสองฝั่ง ไม่ใช่ dimension แยก
  ที่เสียไปคือชื่อห้างภาษาไทย/อังกฤษ และคอลัมน์ `HasFeed` ที่แยก "ยอด 0 เพราะขายไม่ได้"
  ออกจาก "ยังไม่ส่งไฟล์" — รับได้เพราะรหัส 6 ห้างอ่านออกอยู่แล้ว

  **คีย์ join สาขาคือ `store_id` ค่าดิบ ห้ามตัดแปลง**: แต่ละห้างเขียนไม่เหมือนกัน
  (HP `S015` · GH `GH-101` · BT ชื่อสาขา · TW `60001-CRC Thai Watsadu Limited (Head Office)`)
  ตอนแรกตัดหลัง `-` ทำให้ TW และ GH match 0% ทั้งที่ข้อมูลตรงกันทุกตัวอักษร
  วัดด้วยค่าดิบได้ HP 107/107 · GH 99/99 · BT 16/16 · MH 27/28 · TW 101/109 = **97.5%**

  **ของที่ยังไม่ถูกต้องในฝั่ง MDS** (ต้องแจ้งคนดูแล):
  `mds_data_product_master_mdt` มี 2,348 แถวแต่ Excel ต้นทางมี 2,478 → **หาย 130 แถว** ·
  `product_mdt_code` เป็น FLOAT ทั้งที่ต้นทางเป็น STRING ทุกแถว และมี 1 แถวที่ 0 นำหน้า
  ซึ่งเพี้ยนแน่นอน · `mds_data_sales_zone_manager_master` **ว่าง 0 แถว** ·
  `product_mac5_code` หลุดจาก `dim_product_master` (ag01) 27 จาก 961 รหัส

  **คีย์จับคู่สินค้าไม่ต้องมีรหัสห้าง** — ดีไซน์เดิมเขียนว่า `StoreCode + ProductCode`
  แต่วัดจริงแล้วผิด: `product_mdt_code` ไม่ซ้ำเลยทั้ง 2,348 แถว และการไม่สนห้างให้ผล
  เท่ากับจับคู่แยกห้างทุกห้าง โดยไม่จับผิดเพิ่มแม้แถวเดียว  การใส่ห้างในคีย์ทำให้
  **Megahome จับได้แค่ 6 จาก 214 รหัส (2.8%)** เพราะ HP กับ MH มาจากไฟล์เดียวและใช้
  `ARTNO` ชุดเดียวกัน แต่ mds ลงทะเบียนรหัสไว้ใต้ห้างเดียว  แก้เป็นคีย์เดี่ยวแล้วได้
  HP 317 · MH 196 · TW 341 · GH 164 · BT 172 = **1,190/1,287 = 92.5%**
  และ **ฝั่ง fact ต้อง `LTRIM(product_code,'0')` ก่อน join** — TW ส่งรหัสพร้อม 0 นำหน้า
  ทุกตัว ถ้าไม่ตัดจะจับได้ 0 จาก 383 รหัส

  **`mds_data_sales_pc_master` เป็น many-to-many** — 578 แถว = 528 PC × 349 สาขา
  สูงสุด 5 PC ต่อสาขา และ **1 PC ดูแลได้ถึง 47 สาขา** จึงต้องแยกเป็น `dim_pc` (528 แถว)
  + `bridge_pc_branch_mdt` (578 แถว) **ห้าม SUM ยอดหลัง join bridge** ยอดจะคูณตามจำนวน PC
  และยังไม่มีใครกำหนดสูตรแบ่งยอดต่อ PC

  **`onetime.Table_Model_Target_DayOfWork` ตัดออกจากขอบเขต** — 12.7 ล้านแถว มีถึงระดับ
  `SalesRepID` แต่ **ไม่มีคอลัมน์ห้างหรือรหัสลูกค้า** เทียบเป้าขายเข้าได้แค่ระดับช่องทาง MDT
  รวมทุกห้าง และพนักงานขาย 1 คนดูแลหลายลูกค้า จะแบ่งลงห้างต้องมีกฎที่ยังไม่มีใครกำหนด

  **SK ของ dim ตระกูล MDT ใช้ `ROW_NUMBER` สร้างใหม่ทุกคืน** — ปลอดภัยเพราะ
  `fact_saleout_mdt` เป็น `type: "table"` rebuild ทุกคืนเหมือนกัน SK เลื่อนพร้อมกันทั้งคู่
  ⚠️ **วันที่ fact เปลี่ยนไปเป็น incremental ต้องเปลี่ยน dim มาใช้ MERGE ก่อน** ไม่งั้น
  ยอดเดือนเก่าจะชี้ผิดสาขา แบบเดียวกับที่ `AgingSK` เคยชี้ผิด 97.1% — มีคอมเมนต์
  `ponytail:` กำกับไว้ในทั้ง 3 ไฟล์

## การตัดสินใจเชิงออกแบบ

- **2026-09-08 — dim ของ Sales Out MDT: สร้างเปลือกที่มีแต่แถว `-1` ก่อนไฟล์ master มา**

  **เหตุผล**: `Master Branch MDT_final.xlsx` (BI ดูแล) ยังไม่ได้โหลดเข้า BigQuery
  ถ้ารอ จะเขียน `fact_saleout_mdt` ไม่ได้เลย และถ้าเขียน fact ด้วย `-1 AS branch_sk`
  ค่าคงที่ไปก่อน จะต้องกลับมาแก้ fact อีกรอบตอน dim มีข้อมูล → **เขียน fact 2 ครั้ง**

  **ที่เลือก**: สร้าง `dim_sales_branch_mdt` / `dim_zone_mdt` / `dim_product_mdt`
  ที่มีแต่แถว `-1` แถวเดียว แล้วเขียน fact ด้วย `LEFT JOIN` จริงตั้งแต่แรก
  วันนี้ join ไม่เจอใคร → `IFNULL(SK,-1)` → ได้ `-1` ถูกตามดีไซน์
  วันหน้าเติมแถวจริงเข้า dim → fact สร้างใหม่คืนนั้น → SK เข้าที่เอง
  **fact เขียนครั้งเดียว ไม่ต้องแตะอีก**

  **หนี้ที่ตั้งใจก่อ (มีคอมเมนต์ `ponytail:` ในทั้ง 3 ไฟล์)**: ตอนนี้เป็น
  `type: "table"` สร้างใหม่ทุกคืน ซึ่งใช้ได้เพราะมีแถวเดียว แต่**วันที่มีแถวจริง
  ต้องเปลี่ยนไปใช้ MERGE** ไม่งั้น SK เลื่อนทุกคืนแล้ว `fact_saleout_mdt`
  ที่เก็บ SK ข้ามเดือนจะชี้ผิดสาขา (เคสเดียวกับ `AgingSK` ด้านล่าง)

- **2026-09-08 — dim ลูกเก็บ SK ของแม่ไว้ในตัวเอง fact จึง join แค่ 2 ตาราง**

  `dim_sales_branch_mdt` เก็บ `ZoneMdtSK` · `dim_product_mdt` เก็บ `ProductSK`
  และ `ProductMktSK` → `fact_saleout_mdt` join แค่ 2 ตาราง แต่ได้ SK 5 ตัว
  ไม่ต้อง join `dim_zone_mdt` / `dim_product_master` (117,618 แถว) / `dim_product_mkt`

  (แก้ 2026-09-11: เดิมเขียน "3 ตาราง" — ตัวเลขนั้นนับ `dim_store_mdt` ที่ถูกลบไปแล้ว)

- **2026-09-08 — `dim_store_mdt` ต้องมี ยุบเข้า `dim_sales_branch_mdt` ไม่ได้**

  ⚠️ **ข้อนี้ถูกกลับคำแล้ว 2026-09-09** — `dim_store_mdt` ถูกลบทั้งไฟล์และลบตาราง
  ห้างกลายเป็น degenerate column `StoreCode` ใน `dim_sales_branch_mdt`
  เก็บข้อความข้างล่างไว้เป็นประวัติว่าเคยคิดแบบนี้ ไม่ใช่ข้อสรุปปัจจุบัน

  ตามหลัก Kimball ห้างเป็นชั้นหนึ่งของลำดับชั้นสาขา (ห้าง → โซน → สาขา)
  ควรอยู่ตารางเดียวกัน — แต่ยุบไม่ได้เพราะ **ฝั่งขายเข้าไม่มีสาขา**
  (`view_salein_mdt` คืน `store_sk` ไม่มี `branch_sk` — เราขายให้บริษัทห้าง ไม่ได้ขายให้สาขา)
  Requirement ขอให้เทียบขายเข้ากับขายออกที่ระดับห้าง × เดือน
  → ห้างเป็น **conformed dimension เดียวที่ fact ทั้งสองฝั่งใช้ร่วมกันได้**

  เหตุผลที่ **ไม่ใช่** เหตุผลที่ดี (เคยยกไปตอนแรก): `INT64` เล็กกว่า `STRING`
  (2 ตัวอักษร 6 ค่า ไม่ต่างหลังบีบอัด) · เก็บชื่อไว้ที่เดียว (ชีท Master Branch
  มีคอลัมน์ Store อยู่แล้ว) · แถว `-1` (`branch_sk = -1` ครอบเคสเดียวกัน)
- **2026-09-11 — ไฟล์ยอดขายย้อนหลังจาก BI เข้า raw แล้ว แต่ยังไม่ต่อเข้า curated**

  BI ส่ง `Sales_Out_LastYear_Daily.xlsx` มาให้ (430,639 แถว · 2022-01-01 ถึง 2026-08-23 ·
  4,185,331,780.32 บาท · ครบ 6 ห้างรวม **DH ที่ฟีดรายวันยังไม่มีเลย**)
  แปลงเป็น CSV ขึ้น GCS แล้วสร้าง external table `raw_saleout_mdt.saleout_lastyear`

  **ยังไม่ต่อเข้า curated/fact เพราะ 2 เหตุผล**

  1. **ช่วง ก.พ.-ส.ค. 2026 ซ้อนกับฟีดรายวัน** — ใส่ทั้งก้อนยอดจะนับซ้ำ
  2. **เดือนที่ทั้งสองฝั่งครบ ตัวเลขยังต่างกันถึง 19%** ยังหาสาเหตุไม่ได้

  | ห้าง | เดือน | ไฟล์ | pipeline | ต่าง |
  |---|---|---:|---:|---:|
  | HP | 2026-02 | 18,310,880 | 4,359,436 | **+320%** ฟีดเราเพิ่งเริ่มกลางทาง |
  | HP | 2026-03 | 24,173,909 | 12,008,658 | **+101%** |
  | HP | 2026-04 | 25,071,188 | 24,245,695 | +3.4% |
  | HP | 2026-05 | 22,193,618 | 18,795,901 | **+18.1%** |
  | HP | 2026-06 | 18,985,937 | 18,572,072 | +2.2% |
  | HP | 2026-07 | 20,759,727 | 17,437,038 | **+19.1%** |
  | HP | 2026-08 | 13,403,456 | 17,011,108 | -21.2% ไฟล์ตัดที่ 23 ส.ค. |

  MH/BT รูปแบบเดียวกัน · BT มี.ค./มิ.ย./ก.ค. ต่างกันแค่ -0.4% ถึง -1.5% (เกือบตรง)

  **สรุปว่าใครดีกว่าตรงไหน**
  ```
  ไฟล์ดีกว่า      อดีต 2022-01 ถึง 2026-03   เรายังไม่มีข้อมูลช่วงนั้นเลย
  pipeline ดีกว่า  2026-08 เป็นต้นไป          ไฟล์หยุดที่ 23 ส.ค.
  ```

  **แผนที่เสนอ (ยังไม่ได้ทำ)**: ตัดด้วยวันที่ — `sale_date <= 2026-07-31` ใช้ไฟล์ ·
  `>= 2026-08-01` ใช้ pipeline · **ต้องหาสาเหตุที่ เม.ย.-ก.ค. ต่างกัน 19% ก่อน**
  ไม่งั้นไม่รู้ว่ากำลังเอาตัวเลขผิดมาทับตัวเลขถูกหรือเปล่า

- **2026-09-11 — `dim_zone_manager_mdt` เคยขับจากโซนชั่วคราวตอนต้นทางว่าง แล้วกลับคืน**

  บ่ายวันนั้น `mds_data_sales_zone_manager_master` ยังว่าง 0 แถว ถ้าขับ dim จากต้นทางตรง ๆ
  ตารางจะมีแต่แถว `-1` และ `dim_sales_branch_mdt.ZoneManagerMdtSK` จะเป็น `-1` ทั้ง 494 สาขา
  จึง**ขับจาก `dim_zone_mdt` ไว้ชั่วคราว** เพื่อให้ได้โครง 15 โซนและสาขาจับ SK ได้จริง

  เย็นวันเดียวกัน mds นำเข้าครบ 15 แถว → **กลับมาขับจากต้นทางตัวเอง** ตามกฎที่ตกลงไว้
  ว่า dim ต้องตรงกับ MDS แถวต่อแถว · สูตรเช็คกลับมาใช้ได้: `COUNT(dim) - 1 = COUNT(mds)` → 15 = 15

  **บทเรียน**: การขับ dim จากตารางอื่นเพื่อ "ตั้งโครงไว้ก่อน" ใช้ได้เป็นมาตรการชั่วคราว
  แต่ต้องกลับคืนทันทีที่ต้นทางมีข้อมูล ไม่งั้นจะเหลือโครงที่เช็คกับต้นทางไม่ได้ค้างอยู่
  โดยไม่มีใครรู้ว่าทำไม

- **2026-09-11 — รหัสโกลบอลเฮ้าส์รวมเป็น `GB` แก้ที่ MDS ไม่แก้ในโค้ด · เป้ายังค้าง 897.7 ล้าน**

  **ปัญหา**: `dim_sales_branch_mdt` เพิ่ม `RegionSK` จาก `dim_region` แต่ฝั่ง MDT ใช้รหัส
  `GH` ส่วน `mds_data_sales_region_master` ของ MAC5 ใช้ `GB` → GH ไม่ติดทั้ง 100 สาขา

  **ที่วัดได้ก่อนแก้**: `GH` มี 6,085 ค่าใน 4 ตาราง MDS (branch 100 + branch_code 100 +
  product 351 + pc 158 + target 5,376) · `GB` มีแค่ 2 แถวใน region master ของ MAC5

  **ที่เลือก**: **แก้ที่ต้นทาง ไม่ใส่ `CASE WHEN 'GH' THEN 'GB'` ในโค้ด** — กฎเดียวกับรหัสสินค้า
  (ห้ามเดารหัสแทนต้นทาง) เพราะการแปลงในโค้ดคือกฎที่ซ่อนอยู่ คนรุ่นหลังหาไม่เจอ

  **สถานะ 2026-09-11** — mds แก้แล้ว 3 จาก 5 จุด
  | ตาราง MDS | คอลัมน์ | สถานะ |
  |---|---|---|
  | `mds_data_sales_branch_master` | `region_id` | ✅ `GB` 100 |
  | `mds_data_sales_branch_master` | `branch_code` | ✅ `GB_` 100 |
  | `mds_data_sales_pc_master` | `branch_code` | ✅ `GB_` 158 |
  | `mds_data_sales_target_by_mdt_master` | `branch_code` | ❌ ยัง `GH_` 5,376 |
  | `mds_data_product_master_mdt` | `region_id` | ❌ ยัง `GH` 351 |

  **ผลที่ยังค้าง**: เป้า join สาขาไม่ติด **5,376 จาก 16,903 แถว = 897,670,291.65 บาท (24.36%)**
  เดิมติดครบ 386/386 · ⚠️ **ห้ามรัน `dim_target_saleout_mdt` จนกว่า mds จะแก้เป้า**
  ไม่งั้นเป้าของโกลบอลเฮ้าส์ทั้งก้อนจะไปกองที่ `BranchMdtSK = -1`
  `mds_data_product_master_mdt.region_id` ไม่ทำให้ join พัง (`dim_product_mdt` ใช้
  `ProductCode` เดี่ยว) แต่ควรแก้ให้ตรงกัน

- **2026-09-11 — `dim_region` แบ่งตามช่วงเวลา รหัสละ 2 แถว — join ตรงทำให้สาขาบวม 2 เท่า**

  `dim_region` มี 1 แถวต่อ (companyID, RegionID, SubRegionID, StartDate, EndDate)
  เช่น HP: `RegionSK 21` = 2022-01-01→2025-12-31 · `RegionSK 22` = 2026-01-01→2066-12-31
  join ด้วย `RegionID` เฉย ๆ ทำให้ `dim_sales_branch_mdt` บวมจาก 494 เป็น 988 แถว

  **ที่ทำ**: CTE `region_current` กรอง `companyID = 'ag01'` + ช่วงที่ครอบวันนี้
  แล้วปิดท้ายด้วย `QUALIFY ROW_NUMBER() OVER(PARTITION BY RegionID ...) = 1` เป็นตัวกันชั้นที่สอง
  ตารางนี้ rebuild ทุกคืน `RegionSK` จึงขยับเองเมื่อข้ามช่วง ไม่ต้องมีใครมาแก้

- **2026-09-11 — dim ของ MDT ไม่เก็บ `MdsID` และคอลัมน์ audit (ผู้ใช้ตัดสิน)**

  รอบแรกตกลงว่า "เก็บทุกคอลัมน์ของ MDS ห้ามตัด" แล้วเปลี่ยนใจตัด `MdsID` +
  `IsActive/Version/CreatedAt/CreatedBy/UpdatedAt/UpdatedBy` ออกจาก
  `dim_sales_branch_mdt` และ `dim_pc` · `dim_zone_mdt` / `dim_zone_manager_mdt`
  ยังเก็บอยู่ — **ยังไม่ตรงกันทั้ง 4 ตัว ต้องเลือกให้เหมือนกัน**

  ผลข้างเคียง: ไม่มี `MdsID` แล้วสืบกลับไปหาแถวใน MDS ไม่ได้ เช็ค "MDS = dim"
  เหลือแค่เทียบจำนวนแถว เทียบค่าทีละช่องด้วย `EXCEPT DISTINCT` ไม่ได้

  ⚠️ ตอนตัดคอลัมน์ต้องปิดให้ตรงกันทั้ง CTE หลักและ CTE แถว `-1` — พลาดจุดนี้ไป 3 ครั้ง
  ได้ error `Queries in UNION ALL have mismatched column count`

- **2026-09-11 — `saleout_gb` มี `sale_date` เป็นปี 2569 ถึง 74% ของยอด**

  **สิ่งที่พบ**: ไฟล์โกลบอลเฮ้าส์ส่งวันที่มา 2 รูปแบบผสมกัน และรูปแบบผูกกับ "ปี"
  ปี 2569 (พ.ศ.) มาแบบ `วัน/เดือน` · ปี 2026 (ค.ศ.) มาแบบ `เดือน/วัน`
  วัด 32,799 แถว ไม่มีข้อยกเว้นแม้แถวเดียว — ห้างเปลี่ยนรูปแบบราว 15 มิ.ย. 2026

  **ต้นเหตุ**: โค้ดเดิมใช้ `COALESCE` ลอง `%m/%d/%Y` ก่อน แล้วค่อยลอง พ.ศ.
  แต่แถว พ.ศ. ที่เลขทั้งสองตัว ≤ 12 **parse ผ่านรูปแบบแรกได้** เป็นปี 2569 จริง ๆ
  สาขา พ.ศ. จึงไม่เคยทำงาน → 18,776 แถว / 75,548,135 บาท ลงวันที่ผิดไป 543 ปี

  **บทเรียนทั่วไป**: `COALESCE` ที่ไล่ลองรูปแบบวันทีละอัน **ใช้ไม่ได้เมื่อวันกำกวม**
  เพราะรูปแบบผิดก็ parse ผ่าน ต้องหาสัญญาณที่ตัดสินได้ก่อน (ที่นี่คือปี) แล้วค่อยเลือก
  และใช้ `SAFE.DATE` เพื่อให้ได้ `NULL` ให้เห็น ถ้าวันหน้าห้างเปลี่ยนรูปแบบอีก

  **แก้แล้ว 2026-09-11** — หลังแก้: parse พลาด 0 · วันอนาคต 0 · วันขายหลังวันไฟล์ 0
  ช่วงวัน 2026-02-09 ถึง 2026-07-05

- **2026-09-11 — `saleout_gb` คีย์ขาด `row_no` ทิ้ง 1,311 แถว / 6.7 ล้าน**

  บิลใบเดียวมีสินค้าตัวเดียวกันได้หลายบรรทัด คีย์ 4 ตัวแยกไม่ออก
  เพิ่ม `row_no` (คอลัมน์ `No_`) เป็นตัวที่ 5 → 22,700 → **24,011 แถว**
  95,851,374 → **102,548,397**

  ที่ `row_no` ยังแยกไม่ออกอีก 1,166 กลุ่ม ตรวจแล้วเป็นแถวซ้ำทุกคอลัมน์
  (0 กลุ่มที่ต่างกันจริง) การยุบทิ้งจึงถูกต้อง

  **ยอด GH ที่เคยรายงาน 144.9 ล้านผิด** — เป็นผลรวมของทุกไฟล์รวมการส่งซ้ำ
  ห้างส่งบางบรรทัดซ้ำถึง 44 ไฟล์ · 547 บรรทัดที่ส่งซ้ำ ถ้านับทุกไฟล์เป็น 41 ล้าน
  จากของจริง 2.7 ล้าน · ค่าที่ถูกคือ **102,548,397**

  ⚠️ **ฟีด GB ค้าง** — วันขายล่าสุด 5 ก.ค. 2026 แต่ไฟล์เข้าถึง 11 ก.ย. 2026 ต้องถามห้าง

- **2026-09-11 — บุญถาวรส่งยอดสะสม ต้องหาส่วนต่างที่ curated ไม่ใช่ที่ validated**

  **สิ่งที่พบ**: ต้นทางส่ง MTD (ยอดสะสมตั้งแต่ต้นเดือน) ใหม่ทุกวัน การขาย 1 ครั้ง
  ถูกส่งซ้ำจนสิ้นเดือน — 12,756 แถว มีการขายจริง 1,370 — `SUM` ตรง ๆ ได้ 156.2 ล้าน
  แทนที่จะเป็น **15.55 ล้าน** (ยืนยัน 2 วิธีเป็นอิสระ: ผลต่าง `LAG` = ค่าสุดท้ายของเดือน
  ตรงกันทั้งเงินและจำนวนชิ้น 1,687)

  ⚠️ **ตัวเลข 171.1 ล้านที่เคยรายงานไว้ผิด** — เป็นการ SUM ยอดสะสมซ้ำ ค่าที่ถูก 15.55 ล้าน

  **ที่เลือก**: validated เก็บ MTD ตามต้นทาง (ต่อท้ายชื่อ `_mtd`) แล้วหาส่วนต่าง
  ที่ curated ด้วย `LAG` — เพราะ validated ต้องสะท้อนต้นทางตรง ๆ และการหาส่วนต่าง
  ต้องเห็นประวัติ ซึ่งขัดกับหน้าต่าง incremental 1 วันของ validated

  **หนี้ที่ตั้งใจก่อ**: บล็อก `bt` ใน curated อ่านต้นทางทั้งก้อนทุกคืน (12,756 แถว /
  0.3 MB) มีคอมเมนต์ `ponytail:` กำกับ — ถ้าโตเกินหลักล้านแถว เปลี่ยนเป็นย้อน
  **2 เดือนปฏิทิน** ต้องเป็นเดือนเต็ม ไม่ใช่ N วัน เพราะการรีเซ็ตผูกกับต้นเดือน

- **2026-09-11 — ยุบช่องทางขายของบุญถาวรรวมกันที่ curated**

  ต้นทางแยก Showroom / Anyhome / Web แต่เกรนของ `curated_saleout_mdt` และ
  `fact_saleout_mdt` คือ วัน × ห้าง × สาขา × สินค้า ไม่มีช่องทาง จึงบวกรวม
  27 จาก 1,343 กลุ่มมี 2 ช่องทาง คิดเป็นเงิน 395,197 — ยอดรวมไม่เปลี่ยน
  ช่องทางยังอยู่ครบในชั้น validated ถ้าวันหน้ามีคนขอ

  `Web` ผูกกับสาขา `ECOMMERCE` ซึ่งเป็นสาขาแยกใน `dim_sales_branch_mdt` อยู่แล้ว
  จึงไม่เคยชนกับสาขาจริง · สาขาของ BT จับคู่ dim ได้ **16/16** เพราะ `BranchCode`
  ของ BT เป็นชื่อไทย ตรงกับที่ต้นทางส่งมา

- **2026-09-11 — `store_code IS NULL` ใน curated เป็นระเบิดเวลาของ MERGE**

  `saleout_hp` ให้ `store_code = NULL` กับสาขาที่ไม่ใช่ขายปลีก (`CS01` / `EX99`)
  โดยเจตนา — ตอนนี้ 4 แถว / 81,716 บาท — แต่ `store_code` อยู่ใน `uniqueKey`
  และ `NULL = NULL` เป็นเท็จ จึงหา match ไม่เจอแล้ว **INSERT ซ้ำ**

  ยังไม่ระเบิดเพราะ `asatdate` ของ 4 แถวนั้นเก่ากว่าหน้าต่าง 1 วัน (ตรวจ 2026-09-11
  ซ้ำ 0 แถว) จะระเบิดวันที่ห้างส่งแถว `CS01`/`EX99` มาใหม่ — **ยังไม่แก้**
  (0.04% ของยอด) ทางแก้ที่ควรทำ: ให้ค่าแทนที่ไม่ใช่ NULL เช่น `'XX'` ที่ชั้น validated

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
  - `BACKFILL_DAYS` **ตั้งเองรายเครื่อง ไม่ได้ติดมากับ commit ของ repo**
    `databuffet.js` จึงใส่ `|| "1"` ไว้ (เป็นตัวเดียวในไฟล์ที่มี fallback)
    ไม่งั้น workspace ที่ยังไม่มี var จะ interpolate เป็น `undefined` ใส่ SQL 74 จุด
  - รูปแบบนี้ nest `${databuffet.BACKFILL_DAYS}` ไว้ข้างใน
    `${when(incremental(), ...)}` ซึ่งไม่เคยมีในโปรเจกต์มาก่อน —
    **ยืนยันแล้วว่า compile ผ่าน** (ดู Compiled queries ของ `mih` 2026-08-10
    ออกมาเป็น `INTERVAL 1 DAY`)
  - รันซ้ำวันที่เก็บไปแล้วปลอดภัย เพราะ `QUALIFY ROW_NUMBER() ... ORDER BY
    asatdate DESC` คัดเหลือ 1 แถวต่อ PK อยู่แล้ว

## หนี้ทางเทคนิค / งานค้าง

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
- Tag ที่ประกาศแต่ไม่ใช้: `dimension_monthly`, `fact_monthly`, `fact_yearly`,
  `curated_full`, `curated_incremental`, `onetime`
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
  `'Unknown'` · เป็นตัวแทนของ `is_store_*` ที่ถอดออกไปตอน 2026-09-03
  **`'KTB'` ที่นี่คือถังรวม "ที่เหลือทั้งหมด" ไม่ได้หมายถึงคลังของธนาคารกรุงไทย** —
  ชื่อพ้องกับ `is_store_ktb` เดิมแต่ความหมายไม่เหมือนกัน อย่าอ่านว่าเป็นสาขา ·
  commit เดียวกันนี้ลบคอมเมนต์อธิบายใน `dim_store.sqlx` ทิ้ง (ถูก re-save ทับจาก
  Dataform web IDE) — **เจ้าของงานตัดสินใจไม่เอากลับ** คำอธิบายอยู่ที่ไฟล์นี้กับ
  `project_wiki/dimension/inventory.md` แทน
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
  **⚠️ 412 คีย์นั้นจะยังไม่ถูกแก้ย้อนหลังเอง** — `dim_order` เป็น MERGE ที่มี
  `and mil.asatdate >= current_date('Asia/Bangkok')-1` จึงมองแค่เอกสารที่เพิ่งขนเข้ามา
  ถ้าต้องการให้ `item_status` ย้อนหลังถูก ต้องขยายหน้าต่าง `asatdate` ชั่วคราวแล้วรันรอบเดียว
  (แนวเดียวกับ skill `backfill-dimension`)
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
  **ขอบเขตวันที่ของ 3 fact ไม่เท่ากัน**: `fact_order_store`/`fact_invoice_store` กรอง 4 ปี
  ส่วน `fact_backlog_store` ไม่กรองเลย (ย้อนถึง 2006)
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
