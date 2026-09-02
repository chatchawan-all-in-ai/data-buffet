# Known Issues & Gotchas

รวมจุดที่รู้แล้วว่า "เป็นแบบนี้โดยตั้งใจ" หรือ "ต้องระวัง" — อัปเดตล่าสุด 2026-07-24

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
    จะ**ไม่มี js block** เลย (เช่น `PowerBI_Data_Buffet_Transaction`)
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

## การตัดสินใจเชิงออกแบบ

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
- **`is_store_*` ใน Query "ยอดจ่าย" ทับกันเองที่ prefix `MEMO-H`** — เอกสารที่เลขขึ้นต้น
  `MEMO-H` ได้ทั้ง `is_store_ktb` และ `is_store_hy` เป็น TRUE พร้อมกัน เพราะ `'MEMO-H'`
  ไม่อยู่ใน exclusion list ของ `p5` (มีแค่ MEMO-K/P/L/U) · **เก็บพฤติกรรมนี้ไว้ตามเดิม**
  ใน `fact_invoice_store` (การตัดสินใจของเจ้าของงาน 2026-09-01 — เงื่อนไขจากระบบเดิม
  ไม่แก้) · การสไลซ์สาขาจริงให้ใช้ `dim_store` ที่มาจาก `validated_mac5.sto` แทน
  โดย `KTB` = ธนาคารกรุงไทย ไม่ใช่คลัง จึงไม่มีใน `sto` (แสดงเป็น "อื่นๆ" รอ desc)
- **`curated_mil` ฝั่ง `IS` แตกบรรทัดตามสัดส่วนพนักงานขาย — ห้าม QUALIFY ทิ้ง**
  (วัด 2026-09-01): `curated_mil` มี 4,344,147 แถวเทียบกับ `validated_mac5.mil` 4,339,108
  → **เกิน 5,039 แถว** เพราะบรรทัดเดียวถูกแตกตาม `percent_sale` (70/30, 50/50)
  โดย `milPer_raw` เก็บพนักงานคนเดิมไว้ · `miltype = 'PS'` ไม่มีปัญหานี้ (3,012,477 = distinct PK)
  **ตัวเลขที่พิสูจน์**: `SUM(milQuan)` ของ curated ทั้งหมด = 22,209,217.12 เทียบกับ validated
  22,209,216.72 (ต่างกัน 0.40 = เศษปัดจากการหารสัดส่วน) แต่ถ้า `QUALIFY ROW_NUMBER() = 1`
  เหลือแถวเดียวจะได้ 22,199,705.31 → **qty หาย 9,512 และ `milSum` หาย 141 ล้าน**
  ดังนั้น `fact_invoice_store` ใช้ grain ที่รวม `milPer` และเก็บ `percent_sale` ไว้
  (การตัดสินใจของเจ้าของงาน 2026-09-01: "แตกยอดให้พนักงานขาย ไม่ต้องยุ่ง")
