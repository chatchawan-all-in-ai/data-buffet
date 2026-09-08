# Data-Buffet

คลังข้อมูล (data warehouse) บน BigQuery ของกลุ่มบริษัท สร้างด้วย Dataform — รับไฟล์ raw จากระบบขาย/บัญชี/ลูกค้า แปลงเป็น star schema ให้ Power BI และงานวิเคราะห์ใช้
เอกสารนี้คือ glossary ของภาษากลาง (ubiquitous language) — นิยามว่าแต่ละคำ "คืออะไร" เท่านั้น; วิธี implement อยู่ใน `document/` (เริ่มที่ `document/getting-started/glossary.md` และ `document/project_wiki/README.md`)

## Language

### สถาปัตยกรรมและชั้นข้อมูล

**Layer**:
ลำดับชั้นของข้อมูลตาม medallion architecture: initial → validated → curated → dimension/fact → view (มี cdc/process เป็นท่อเสริม) แต่ละชั้นสะอาดและพร้อมใช้ขึ้นเรื่อย ๆ
_Avoid_: stage, zone

**Initial layer**:
ชั้นแรกสุด — external table ที่อ่านไฟล์ AVRO บน GCS ตรง ๆ โดยไม่ copy ข้อมูลเข้า BigQuery
_Avoid_: raw layer, landing zone

**Validated layer**:
ชั้นทำความสะอาด — cast type, ล้าง string, ตัดแถวซ้ำต่อคีย์ จาก snapshot ล่าสุด แยก dataset ตามระบบต้นทาง
_Avoid_: staging, cleansed layer

**Curated layer**:
ชั้น business logic — รวม/แปลงข้าม validated tables ให้เป็นข้อมูลเชิงธุรกิจ (เช่น curated_mih, curated_product)
_Avoid_: gold layer

**Dimension**:
ตารางบริบทใน star schema (ลูกค้า สินค้า พนักงานขาย ฯลฯ) ระบุตัวด้วย surrogate key
_Avoid_: lookup table, master table (คำหลังสงวนให้ mds)

**Fact**:
ตารางเหตุการณ์/ยอดใน star schema (ใบแจ้งหนี้ คำสั่งซื้อ การรับชำระ) join กับ dimension ด้วย SK เก็บย้อนหลังแบบ rolling 4 ปี (ตัดที่ต้นปี)
_Avoid_: transaction table

**View layer**:
ชั้น presentation — BigQuery view เหนือ dim/fact/curated ที่ Power BI และผู้ใช้ปลายทางชี้เข้า; เป็น logical ล้วน ไม่เก็บข้อมูลเอง
_Avoid_: reporting layer, semantic layer

**Snapshot / ASATDATE**:
วันที่ของก้อนข้อมูลที่ระบบต้นทางส่งมาในแต่ละวัน (`YYYYMMDD` ใน raw → `DATE` ใน validated) เป็น partition หลักของตาราง incremental
_Avoid_: load date, ingestion date

**Full load**:
โหมดสร้างตารางใหม่ทั้งก้อนทุกรอบ ใช้กับ reference data ขนาดเล็ก

**Incremental**:
โหมดโหลดเฉพาะ snapshot ช่วงหลังตามหน้าต่าง `BACKFILL_DAYS` (ปกติ 1 วัน)

**Backfill**:
การขยายหน้าต่างย้อนหลัง (`BACKFILL_DAYS` / `MDS_BACKFILL_DAYS`) ชั่วคราวเพื่อเก็บข้อมูลเก่าที่ตกหล่น แล้วตั้งกลับเป็นค่าเดิม
_Avoid_: reload, re-initial (คำหลังคือ tag อันตรายที่ drop ตาราง)

### แหล่งข้อมูล

**MAC5**:
ระบบ POS/ERP/บัญชีหลัก (สัญชาติไทย) — ตารางใช้รหัส 3 ตัวอักษร เช่น `mih` = invoice header, `mil` = invoice line, `deb` = ลูกหนี้/ลูกค้า, `stk` = สต๊อก, `per` = พนักงาน

**Company**:
หนึ่งใน 5 บริษัทที่รัน MAC5 แยก instance: `ag01` (flagship), `aa05`, `ab01`, `ac02`, `ak02` — รวมใน validated ด้วยคอลัมน์ `company_id`
_Avoid_: branch, instance

**MASTERSKU**:
ระบบ product master (สี ขนาด มิติสินค้า — มี JSON ซ้อน)

**CIS360**:
ระบบข้อมูลอ้างอิงลูกค้า (customer profile, ที่อยู่, นิติบุคคล, lookup ภูมิศาสตร์)

**SALEOUT_MDT**:
ข้อมูล sell-out จาก dealer ฝั่ง modern trade 4 ราย: BT, GB, HP, TW

**ALLKONS_COMMISSION**:
แหล่งข้อมูลค่าคอมมิชชันฝ่ายขาย (7 ตาราง; ยังไม่มี downstream ใช้)

**mds (Master Data Service)**:
ชุดตาราง master data ที่โหลดมาจากภายนอก (repo นี้ไม่ได้สร้าง) — ต้นทางของ dimension ส่วนใหญ่ ทุกตารางมี `id`, `is_active`, `updated_at`
_Avoid_: MDM

**Overwrite import**:
โหมด import ของ mds ที่ล้างตารางแล้วลงใหม่ทั้งก้อน ทำให้ `id` เปลี่ยนหมด — เหตุผลหลักที่ dim ส่วนใหญ่ใช้ full rebuild

**Soft delete**:
การปิด row ต้นทางด้วย `is_active = FALSE` แทนการลบจริง — ฝั่ง dim ตอบสนองด้วย tombstone (MERGE dims) หรือกรองออกตอน rebuild (full-rebuild dims)

### Key และอายุของ Key

**SK (Surrogate Key)**:
เลขที่ warehouse ออกเองเพื่อ join fact ↔ dimension (`CompanySK`, `SaleRepSK`, ...) ห้ามมีความหมายทางธุรกิจ
_Avoid_: id, running number

**Natural key**:
คีย์จากระบบต้นทาง (เช่น `CompanyID + StkCode`) ใช้จับคู่ row ต้นทางกับ dimension row
_Avoid_: business key

**MdsID**:
คอลัมน์ trace ใน dimension เก็บ `id` ของ row ต้นทางจาก mds — ใช้จับคู่และใช้ลบตาม soft delete

**Stable SK**:
สัญญาของ MERGE dims (`dim_company`, `dim_aging_rang`, lake dims): SK คงที่ตลอดกาล ห้าม regenerate

**Regenerated SK**:
สัญญาของ full-rebuild dims (34 mds dims): SK ออกเลขใหม่ทุกคืน ห้ามเก็บข้ามวัน — consumer ที่เก็บค่าไว้ต้อง rebuild ตามทุกวัน หรือ join กลับด้วย natural key

**Orphan (dangling SK)**:
ค่า SK ใน fact ที่ไม่มีคู่ใน dimension แล้ว — สแกนด้วย fk-integrity-scan
_Avoid_: dangling FK

### Pattern ฝั่ง Dimension

**Full-rebuild dim**:
pattern มาตรฐานของ mds dims — ปั้นตารางใหม่ทุกวันจากแถว `is_active = TRUE` (SK เป็นแบบ regenerated) รองรับ overwrite import โดยธรรมชาติ

**MERGE dim**:
pattern legacy ที่ upsert เข้า target ซึ่งมีอยู่ก่อนแล้วเพื่อรักษา stable SK — เหลือ `dim_company`, `dim_aging_rang` และ lake dims

**Lake dim**:
dimension ที่สร้างจากข้อมูลธุรกรรมในคลังเอง (validated/curated) ไม่ใช่จาก mds เช่น `dim_customer`, `dim_invoice` — ทั้ง 10 ตัวใช้ MERGE + stable SK

**Tombstone**:
คำสั่งลบท้าย MERGE dim: ลบ row ที่ต้นทาง mds ถูก soft delete — บังคับเฉพาะ MERGE dims; full-rebuild ไม่ต้องมี

**`_last` dim**:
ตระกูล dim 7 ตัว (`dim_department_last`, `dim_director_last`, `dim_region_last`, `dim_region_manager_last`, `dim_section_last`, `dim_section_manager_last`, `dim_sale_representative_last`) เก็บ "แถวล่าสุดต่อ entity" สำหรับงาน RLS/target — FK SK ที่เกิดเป็น NULL ถูกเติมทีหลังโดย `update_sk_sale_rep_group`

**update_sk_sale_rep_group**:
ขั้น UPDATE เชิงคำสั่ง (ไม่ใช่ dim) ที่เติม FK SK ให้ตระกูล `_last` — ต้องรันหลัง `_last` ทุกตัว rebuild เสร็จ

**Waiting Master**:
row placeholder ใน `dim_stk_mkt` (MdsID = NULL) สำหรับรหัสสินค้า (stkcode) ที่ยังไม่มี master

**DAG root**:
`dim_company` — dimension ที่ dim อื่นทุกตัวอ้างเพื่อขอ `CompanySK` จึงต้องรันก่อนเสมอ

### Fact และงานลูกหนี้ (AR)

**fact_transcation**:
fact หลักของธุรกรรมขาย (สะกด "transcation" ผิดโดยตั้งใจ — เป็น load-bearing typo) สร้างจาก `Transaction_Data_Mart` ด้วยท่า upsert

**Transaction_Data_Mart**:
data mart ใน dataset `onetime` ที่รวม curated + dim ให้เป็นแถวธุรกรรมพร้อมใช้ — ต้นทางตรงของ `fact_transcation`

**AR chain**:
สายงานลูกหนี้/อายุหนี้: `fact_chq` → `fact_mir_vs` → `fact_mir_rs` → `dim_aging` (rebuild เต็มทุกวันตามลำดับ)

**Aging**:
การจัดอายุหนี้ของเอกสารลูกหนี้ — `dim_aging` เป็น engine หลัก, `dim_aging_rang` คือช่วงอายุ, `dim_aging_history` คือ snapshot สะสมรายวัน

**onetime**:
dataset สำหรับ data mart / ของที่โหลดด้วยมือ (เช่น `mapping_invoice`) — บางส่วน repo สร้าง บางส่วนมีอยู่ก่อน

### ท่อเสริมและปฏิบัติการ

**CDC (Change Data Capture)**:
ระบบตรวจจับแถวที่เพิ่ม/เปลี่ยนรายวัน เทียบ raw กับ validated — เปิดผ่าน config (ปัจจุบันเฉพาะ `mac5.deb`) ผลลง `cdc_change_log` (เก็บ 7 วัน)

**CDC gating**:
การใช้ผล CDC จำกัดงานแพงให้ทำเฉพาะแถวที่เปลี่ยน "วันนี้" — pattern อ้างอิงคือ AI address parsing
_Avoid_: incremental filter

**AI address parsing**:
งาน `deb_address_data` — ใช้ `AI.GENERATE` (gemini) แยกที่อยู่ภาษาไทยเป็น ตำบล/อำเภอ/จังหวัด เฉพาะลูกค้าที่ CDC บอกว่าที่อยู่เปลี่ยน

**RLS (Row-Level Security)**:
การคุมสิทธิ์เห็นข้อมูลรายลูกค้าใน Customer360 — `rls_customer360` คือ access map หนึ่งแถวต่อลูกค้า บอกว่า sales entity ใดเกี่ยวข้องบ้าง

**Drift**:
ความต่างระหว่างของจริงบน BigQuery (แก้ผ่าน console) กับไฟล์ใน git — ตรวจ/ดึงกลับด้วย bq-drift-scan; ถ้าปล่อยไว้ การรัน tag `view` จะเขียนทับของบน console หาย

**Monitor table**:
`monitor_dataset.dataform_run_action` — ตาราง telemetry ผลการรัน Dataform ใช้ตอบว่า "เมื่อคืนรันผ่านไหม"

**Tag**:
ป้ายกลุ่มการรันของ Dataform (เช่น `dimension_daily`, `validated_incremental`, `view`) — หน่วยที่ scheduler ใช้สั่งรันเป็นชุด

**Load-bearing typo**:
คำสะกดผิดที่ระบบอื่นอ้างอยู่ ห้ามแก้: `fact_transcation` (ไฟล์+ตาราง), `CDC_DATESET` (key ใน variables.json), `prdDiminsionData` (field ใน JSON ของ MASTERSKU)
