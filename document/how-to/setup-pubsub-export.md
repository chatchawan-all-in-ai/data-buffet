# How-to: Setup Pub/Sub สำหรับส่งออกข้อมูลจาก BigQuery

> สถานะ 2026-10-25: pilot `dim_company` ใน **`databuffet-nonprd` เท่านั้น** · repo มีครบทั้ง
> Dataform (export view + ตาราง bookkeeping), Workflow
> [`infra/pubsub/datamart-publish.workflows.yaml`](../../infra/pubsub/datamart-publish.workflows.yaml)
> และสคริปต์สร้าง infra [`infra/pubsub/setup.sh`](../../infra/pubsub/setup.sh) · ยัง **ไม่ได้ deploy**
> ฝั่ง GCP — ทำตาม [ส่วน A](#ส่วน-a--deploy-และทดสอบ-pilot) หลัง PR merge
> รายละเอียด repo และวิธีเพิ่มตารางอยู่ที่
> [process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

## ภาพรวม

ฝั่ง GCP (region `asia-southeast1`): Cloud Scheduler `datamart-publish-every-5m` เรียก Cloud
Workflows `datamart-publish` ทุก 5 นาทีตลอดวัน (`*/5 * * * *`) เพื่อถาม **Dataform API**
ว่ามีรอบ Dataform ใหม่ที่สำเร็จและรันตารางนั้นหรือไม่ — รองรับทุก scheduler และการรัน
manual ตาม [สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)
· ถ้ามี จึงส่งเฉพาะแถวที่เปลี่ยน · ใช้ service accounts `datamart-publisher` (รัน workflow)
และ `datamart-publish-trigger` (Scheduler → Workflows) แบบ keyless · เมื่อล้มเหลวแจ้ง Slack
ผ่าน incoming webhook ที่เก็บใน Secret Manager ชื่อ `slack-datamart-dataform`
ไม่มี Cloud Logging trigger

รายการตาราง, source view และ topic ที่ต้องสร้างอ่านจาก
[`mart-export-config.json`](../../includes/controller/mart-export-config.json)
ชื่อ topic ใช้รูปแบบ `export-<sys>-<set>` · หนึ่งชุดข้อมูลต่อหนึ่ง topic
เพื่อให้ replay/seek และให้สิทธิ์แยกต่อชุดได้ และชุดที่มีข้อความค้างไม่ถ่วงชุดอื่น
ตาราง bookkeeping และการกันส่งซ้ำอยู่ใน
[process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

เมื่อ infra พร้อม ทีมที่จะรับข้อมูลสามารถใช้ push subscription ไปยัง HTTPS endpoint
ของทีม พร้อม OIDC token จาก `sa-push-<ทีม>` ภายใน project เรา **ไม่มี service account
key ส่งให้ทีมปลายทาง** และทีมปลายทางไม่ต้องมีบัญชีหรือสิทธิ์ใน `databuffet-nonprd`
ส่วน B เป็นแนวทางฝั่งผู้รับสำหรับตอนนั้น ยังไม่ได้ยืนยันว่า deploy แล้ว

## Message format (มาตรฐานเดียว ทุก topic ทุกทีมใช้ร่วมกัน)

```json
{
  "table": "dim_company",
  "run_date": "2026-10-24",
  "operation": "NEW",
  "primary_key": { "CompanyID": "zz01" },
  "data": { "CompanyID": "zz01", "CompanyCode": "EXAMPLE", "CompanyNameTH": "บริษัทตัวอย่าง", "CompanyNameEN": "Example Company" }
}
```

| field | ค่า | หมายเหตุ |
|---|---|---|
| `table` | ชื่อชุดข้อมูล | ตรงกับ `table_name` ใน export config — ให้ consumer ใช้ callback ตัวเดียวได้ |
| `run_date` | วันที่ส่งตาม `Asia/Bangkok` | ใช้ debug/ตรวจสอบ ไม่ใช่ key |
| `operation` | `NEW` \| `UPDATE` \| `DELETE` | ปลายทางใช้ตัดสินว่าจะ upsert หรือ delete |
| `primary_key` | object ของ natural key (field จริงใน `data` ไม่ใช่ hash) | key ของแต่ละชุดกำหนดใน export view — `dim_company` ใช้ `CompanyID` อย่างเดียว · ชุดอื่นในอนาคตอาจมีค่า `null` ใน key ได้ (เช่น ใบเสร็จเงินสดไม่มีเลขเช็ค) ฝั่งปลายทางต้องถือว่า `null` เท่ากัน |
| `data` | ทุก data column ของ export view (ไม่รวม `row_key` / `row_hash`) ตามชื่อและลำดับคอลัมน์ของ view | มีเฉพาะ `NEW`/`UPDATE`; `DELETE` = `null` (แถวไม่มีแล้วที่ต้นทาง) |

JSON ทั้งก้อน **สร้างโดย BigQuery** (`TO_JSON_STRING`) จึงมีรูปแบบตายตัว: ไม่มีช่องว่าง,
DATETIME = `"2026-01-30T09:10:00"`, ตัวเลขไม่มี `.0` เกิน (`700`), ค่าว่าง = `null` —
ชื่อ field ใน `data` / `primary_key` คือชื่อคอลัมน์ของตารางต้นทาง (เช่น `CompanyID` ตาม
`dim_company`) ไม่มีการเปลี่ยนชื่อ · สัญญาการเลือกคอลัมน์อยู่ที่ process reference ด้านล่าง

ตัวอย่างนี้ใช้ค่าบริษัทสมมติ (`CompanyID = zz01`) · JSON หลัง decode มีเฉพาะ 5 field ข้างบน
ส่งหนึ่งแถวต่อหนึ่งข้อความ และ publisher ไม่ใส่ message attributes เพิ่ม
สัญญา export view และการหา `NEW` / `UPDATE` / `DELETE` อยู่ที่
[process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

⚠️ **ทีมใหม่ที่ต่อครั้งแรก**: delta มีเฉพาะแถวที่เปลี่ยนหลังต่อ subscription จึงต้องรับ
full snapshot ก่อนเข้าโหมด delta (ดูขั้น 4) · เครื่องมือ backfill ยังไม่อยู่ใน pilot นี้

## ส่วน A — deploy และทดสอบ pilot

ทำครั้งเดียวหลัง PR merge และ code ถึง `nonprod` (คนทำต้องเป็น project owner ของ
`databuffet-nonprd` และรันจาก WSL ที่มี `gcloud` / `bq`) · ทีมปลายทางดูแล HTTPS endpoint,
การตรวจ token และตารางปลายทางตามส่วน B

| ไฟล์ | หน้าที่ |
|---|---|
| [`infra/pubsub/datamart-publish.workflows.yaml`](../../infra/pubsub/datamart-publish.workflows.yaml) | Workflow 9 ขั้นตาม [สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) — generic ทุกแถวใน `mart_export_config` |
| [`infra/pubsub/setup.sh`](../../infra/pubsub/setup.sh) | สร้าง/อัปเดต infra ทั้งหมด แบบ idempotent (รันซ้ำได้) |

### A1. สร้างตาราง bookkeeping และ export view

ทำตาม [ขั้น deploy ของ pilot](../project_wiki/cdc-process/process.md#deploy) — รัน tag
`pub_sub` จาก release `production` แบบ include dependencies **ปิด** · `setup.sh` จะหยุด
ถ้ายังไม่มี `process_dataset.mart_export_config`, `process_dataset.mart_sent_state` หรือ
`pub_sub.export_dim_company`

### A2. ตรวจ secret ของ Slack

Webhook ของ Slack เก็บไว้แล้วใน Secret Manager ชื่อ **`slack-datamart-dataform`** (ไม่ต้องสร้างใหม่)
· ห้ามพิมพ์หรือ log ค่าของ secret · workflow อ่านค่าเฉพาะตอนต้องแจ้งความล้มเหลว

### A3. รัน `setup.sh`

```bash
bash infra/pubsub/setup.sh
```

สคริปต์ทำตามลำดับ (ทุกขั้นเช็คก่อนสร้าง หรือ apply ซ้ำได้ไม่เสียหาย):

1. ตรวจ prerequisite ของ A1–A2
2. เปิด API: Workflows, Workflow Executions, Cloud Scheduler, Pub/Sub, Secret Manager
   (และ Dataform / BigQuery ที่เปิดอยู่แล้ว)
3. สร้าง service accounts `datamart-publish-trigger` และ `datamart-publisher` — **ไม่สร้าง key**
4. ต่อทุกตารางใน [`mart-export-config.json`](../../includes/controller/mart-export-config.json):
   topic (`export-ta-dim_company`), dead-letter topic (`<topic>-dead-letter`) พร้อม sub ที่เก็บ
   dead letter (`sub-test-<table>-dead-letter`), pull subscription ทดสอบ `sub-test-<table>`
   (dead letter หลังส่งไม่สำเร็จ 5 ครั้ง) และสิทธิ์ของ Pub/Sub service agent ที่ใช้ส่ง dead letter
5. ให้สิทธิ์แบบ least privilege กับ `datamart-publisher`:

   | Role | ขอบเขต | ใช้ทำ |
   |---|---|---|
   | `roles/dataform.viewer` | project | list workflow invocations + query actions |
   | `roles/bigquery.jobUser` | project | รัน query/DML |
   | `roles/logging.logWriter` | project | `sys.log` ของ workflow |
   | `roles/bigquery.dataEditor` | ตาราง `mart_export_config`, `mart_sent_state` เท่านั้น | อ่าน config (tabledata.list), claim, MERGE sent state |
   | `roles/bigquery.dataViewer` | view `pub_sub.export_dim_company` + ตารางต้นทาง `dimension_table.dim_company` เท่านั้น | diff query (view ต้องอ่านตารางต้นทางได้ด้วย) |
   | `roles/pubsub.publisher` | topic ของแต่ละชุดเท่านั้น | publish |
   | `roles/secretmanager.secretAccessor` | secret `slack-datamart-dataform` เท่านั้น | อ่าน webhook |

   `datamart-publish-trigger` ได้ `roles/workflows.invoker` อย่างเดียว (ระดับ project เพราะ
   Workflows ไม่มี IAM รายตัว)
6. deploy workflow `datamart-publish` (`asia-southeast1`) ให้รันเป็น `datamart-publisher`
7. สร้าง/อัปเดต Scheduler job `datamart-publish-every-5m` (`*/5 * * * *`, Asia/Bangkok)
   ที่ POST ไป Workflow Executions API ด้วย OAuth ของ `datamart-publish-trigger`

### A4. ทดสอบด้วย pull subscription

Workflow จะ export เมื่อมีรอบ Dataform ที่สำเร็จและรัน action `dim_company` สำเร็จ —
`daily_process` รันทุกวันอยู่แล้ว · ครั้งแรก (`last_invocation_end` ยังเป็น `NULL`)
มองย้อนหลัง 48 ชั่วโมง จึงไม่ต้องรอรอบใหม่

1. รอ Scheduler รอบถัดไป (ไม่เกิน 5 นาที) หรือสั่งเองทันที:
   `gcloud workflows run datamart-publish --location=asia-southeast1 --project=databuffet-nonprd`
   ผลลัพธ์ต้องเป็น `["dim_company: sent 5 rows for <invocation id>"]`
2. ดึงข้อความ: `gcloud pubsub subscriptions pull sub-test-dim_company --project=databuffet-nonprd --limit=10 --auto-ack`
   ต้องได้ **5 ข้อความ `NEW`** (หนึ่งข้อความต่อบริษัท) ตาม Message format ด้านบน
3. ตรวจ bookkeeping: `process_dataset.mart_sent_state` มี 5 แถวของ `dim_company` และ
   `mart_export_config.last_invocation_id` = invocation นั้น, `claimed_at` = `NULL`
4. สั่ง workflow อีกครั้ง → ผลลัพธ์ `no new invocation` (หรือ `advanced to ...` ถ้ามีรอบอื่น
   จบระหว่างนั้น) และ pull อีกครั้งต้องได้ **0 ข้อความ** · หลังรอบ `daily_process` ถัดไปก็ยัง
   0 ข้อความถ้า `dim_company` ไม่เปลี่ยน (ผลคือ `sent 0 rows for ...`)
5. ทดสอบ Slack: ดู execution ที่ล้มเหลวใน **Workflows → datamart-publish → Executions**
   ต้องมีข้อความใน channel ของ webhook · ถ้ายังไม่เคยล้มเหลว ไม่ต้องสร้างความล้มเหลวเอง

ถ้า export ล้มเหลว `last_invocation_*` ไม่ขยับ และ `claimed_at` ค้างไว้จนครบ 30 นาที
แล้ว Scheduler รอบถัดไปจะทำซ้ำเอง (ข้อความที่ publish ไปแล้วแต่ยังไม่บันทึกอาจถูกส่งซ้ำ)

---

## ส่วน B — ต่อทีมที่มาใช้ข้อมูล (ทำซ้ำทุกครั้งที่มีทีมใหม่)

ทุกทีม — ในบริษัทหรือนอกบริษัท — ใช้ขั้นตอนเดียวกันนี้เสมอ (push ไปที่ endpoint ของทีม)
ตัวอย่างด้านล่างใช้ทีม TF (`<ทีม>` = `tf`)

### 1. ขอ HTTPS endpoint จากทีมนั้น

**ทำ**: ขอ URL ของ endpoint ที่จะรับข้อมูลจากทีม (เช่น `https://<โดเมนของทีม>/pubsub`)
endpoint เดียวรับได้ทุกชุด (แยกชุดด้วย field `table` ใน message) — เงื่อนไขของ endpoint:

- เป็น **HTTPS** ที่มี certificate ถูกต้อง และเปิดให้ Pub/Sub ของ Google เรียกจาก internet ได้
  (ถ้าทีมใช้ GCP จะเป็น Cloud Run ก็ได้)
- รับ `POST` ได้หลาย request พร้อมกัน และตอบภายในไม่กี่วินาที
- ถ้าใช้ Cloud Run ให้ทีมส่ง **Service URL** จากหน้า service มาด้วย เช่น
  `https://service.run.app` — ใช้เป็น audience ในขั้น 3 แม้ endpoint จะเป็น
  `https://service.run.app/pubsub` หรือใช้โดเมนของทีมเอง

**ทำไม**: แบบ push ทีมเป็นฝ่ายเปิดประตูรับ เราเป็นฝ่ายส่ง — ทีมจึงไม่ต้องมีบัญชีหรือ key
ใดๆ ของ project เรา ไม่มี secret อายุยาวต้องส่งข้ามองค์กร ถ้าเลิกส่งให้ทีมนี้ก็แค่ลบ sub ของเขา

### 2. สร้าง push service account ภายในให้ทีมนั้น (1 ทีม = 1 SA, ไม่สร้าง key)

**ทำ**:

1. **IAM & Admin → Service Accounts → CREATE SERVICE ACCOUNT** → name: `sa-push-<ทีม>`
   → **CREATE AND CONTINUE** → ไม่ต้องให้ role ใดๆ ระดับ project → **DONE**
   **ห้ามกด Keys → ADD KEY** — SA นี้ใช้แค่ภายใน project
2. เปิด `sa-push-<ทีม>` → tab **PERMISSIONS → GRANT ACCESS** → principal = Pub/Sub
   service agent `service-<PROJECT_NUMBER>@gcp-sa-pubsub.iam.gserviceaccount.com`
   → Role: **Service Account Token Creator** → **SAVE**
3. ถ้า endpoint เป็น **Cloud Run** ให้ทีมเปิด **Cloud Run ใน project ของทีม** → service
   ที่รับ push → **PERMISSIONS → ADD PRINCIPAL** → principal =
   `sa-push-<ทีม>@databuffet-nonprd.iam.gserviceaccount.com` → Role: **Cloud Run Invoker**
   → **SAVE** — ให้เฉพาะ service ที่รับ push

**ทำไม**: Pub/Sub แนบ OIDC token ที่ออกในนาม SA นี้ไปกับทุก request ที่ยิงไป endpoint ของทีม
— ทีมตรวจลายเซ็นของ Google + อีเมล SA + audience ก็รู้ว่าข้อความมาจากเราจริง โดยไม่ต้อง
มีอะไรของเราอยู่ในมือ · Token Creator ให้ที่ **ระดับ SA นี้** (ไม่ใช่ project) เพื่อให้ Pub/Sub
ออก token ในนาม SA นี้ได้ (project ที่สร้างก่อน 8 เม.ย. 2021 ขาดไม่ได้ ใหม่กว่านั้นใส่ไว้ก็ไม่เสียหาย)
· แยก SA ต่อทีม เพื่อให้แต่ละทีมเช็คอีเมลของตัวเอง และปิดทีมใดทีมหนึ่งได้ไม่กระทบทีมอื่น
· คนที่จะสร้าง sub ในขั้น 3 ต้องมีสิทธิ์ใช้ SA นี้ (Service Account User — Owner มีอยู่แล้ว)
· Cloud Run ตรวจสิทธิ์ Invoker ก่อนส่ง request เข้า handler ถ้าข้ามข้อ 3 จะได้ 403
แม้ token ถูกต้อง — ดู [การต่อ Pub/Sub กับ Cloud Run](https://docs.cloud.google.com/run/docs/tutorials/pubsub)

### 3. สร้าง push subscription ให้ทีมนั้น — 1 อันต่อ 1 topic ที่ทีมได้รับ

**ทำ**: เลือก topic จาก [export config](../../includes/controller/mart-export-config.json)
ใน **Pub/Sub → Topics → CREATE SUBSCRIPTION**

- ID: `sub-<ทีม>-<ชุด>` (เช่น `sub-tf-dim_company`)
- Delivery type: **Push** → Endpoint URL: URL จากขั้น 1
- ติ๊ก **Enable authentication** → Service account: `sa-push-<ทีม>` (ขั้น 2) →
  Audience: ถ้า endpoint เป็น **Cloud Run** ใส่ **Service URL** จากขั้น 1
  (`https://service.run.app` ไม่รวม `/pubsub`); endpoint HTTPS อื่นใช้ endpoint URL
  — ให้ทีมใช้ค่าเดียวกันตรวจ token
- ปล่อย Acknowledgement deadline, Retry policy และ Message retention เป็น **default**
  → **CREATE**

สร้างเฉพาะ topic ที่ทีมนั้นได้รับตาม export config

**ทำไม**: subscription คือ "ตัวชี้ว่าส่งถึงไหน" ส่วนตัวของแต่ละทีมบน topic นั้น — endpoint
ทีมนี้ล่ม/ตอบช้า ไม่กระทบทีมอื่นที่ต่อ topic เดียวกัน 1 sub ผูกได้ 1 topic และชื่อห้ามซ้ำ
ทั้ง project จึงต้องมีชื่อชุดต่อท้าย · ไม่ต้องให้สิทธิ์ Subscriber กับใครเลย เพราะทีมไม่ได้
เข้ามาดึงเอง · Cloud Run ต้องใช้ Service URL เป็น audience แม้ POST จะส่งไปที่ path
`/pubsub` — ดู [ข้อกำหนด audience ของ Cloud Run](https://docs.cloud.google.com/run/docs/authenticating/service-to-service)
· ข้อความที่ส่งไม่สำเร็จเก็บไว้ได้ **7 วัน** ตาม default หลังจากนั้นหาย (เฝ้าด้วยขั้น 5)

### 4. Backfill ให้ทีมใหม่ (ครั้งแรกที่ต่อเข้ามาเท่านั้น)

**ทำ**: หลังสร้าง sub ครบแล้ว ประสาน Data Mart ให้ส่ง full snapshot ของ export view
ก่อนรับ delta ตามปกติ เครื่องมือ backfill ยังไม่อยู่ใน pilot นี้ (จะทำแยก)
ห้ามล้าง sent state ที่ใช้ร่วมกันเพื่อเริ่มต้นให้ทีมใหม่

**ทำไม**: export ปกติเป็น delta อย่างเดียว ทีมใหม่ที่เพิ่งต่อจะไม่มีข้อมูลตั้งต้นถ้าไม่
backfill ก่อน — ข้อความ publish เข้า topic จะไปถึง **ทุก sub บน topic นั้น** ไม่ใช่แค่
ทีมใหม่ ทีมเดิมจึงได้ข้อมูลซ้ำด้วย ต้องประสานทุกทีมและตกลงวิธีรับมือ snapshot กับ delta
ที่อาจมาสลับลำดับกันก่อนส่ง

### 5. ตั้ง alert เมื่อข้อความค้าง

**ทำ**: **Monitoring → Alerting → CREATE POLICY** → metric
`Pub/Sub Subscription → Unacked messages` (`num_undelivered_messages`) → filter
`subscription_id` starts with `sub-<ทีม>-` → Group by `subscription_id` → threshold
ตามที่เหมาะสม → ส่งแจ้งเตือนไป Slack channel เดียวกับ Dataform

**ทำไม**: policy เดียวครอบ sub ของทีมนั้นทุกชุด ไม่ต้องตั้งทีละอัน — ข้อความค้าง =
endpoint ของทีมล่มหรือรับข้อความไม่สำเร็จ ข้อความเก็บไว้ 7 วัน ถ้า endpoint ไม่กลับมารับนาน
เกินนั้นข้อมูลจะหาย ต้องรู้ก่อน

### 6. ส่ง handover package ให้ทีม

ส่งให้ครบ 5 อย่าง (ไม่มีอะไรเป็น secret — ส่งช่องทางปกติได้):

1. รายชื่อชุดข้อมูลที่จะถูก push ไป endpoint ของทีม (`sub-<ทีม>-<ชุด>` ทุกชุดที่ได้รับ)
2. ค่าที่ endpoint ต้องใช้ตรวจ token: อีเมล `sa-push-<ทีม>@databuffet-nonprd.iam.gserviceaccount.com`
   และ audience ที่ตั้งในขั้น 3 (Cloud Run = Service URL, HTTPS อื่น = endpoint URL)
3. Message format (ตารางด้านบน) + รูปแบบ push body (ด้านล่าง)
4. รายชื่อชุดข้อมูล + primary key ของแต่ละชุด
5. ตัวอย่างโค้ด endpoint (Data Mart เขียนให้ — ตัวอย่างด้านล่าง)

**ทำไม**: เป็น handover package มาตรฐานเดียว ใช้ซ้ำได้กับทุกทีมที่มาใหม่ ไม่ต้อง
คิดใหม่ทุกครั้ง — และไม่มี service account key หรือ credential ใดๆ ของเราออกไปนอก project

### รูปแบบ push body (สิ่งที่ endpoint ได้รับ)

Pub/Sub ยิง `POST` มาพร้อม header `Authorization: Bearer <OIDC token>` และ body JSON:

```json
{
  "message": {
    "data": "<base64 ของ JSON ตาม Message format ด้านบน>",
    "messageId": "1234567890",
    "publishTime": "2026-10-13T00:05:12.345Z"
  },
  "subscription": "projects/databuffet-nonprd/subscriptions/sub-tf-dim_company"
}
```

- `message.data` = message format ด้านบน (JSON) ที่เข้ารหัส **base64** — ต้อง decode ก่อน
  ค่าในตัวอย่างเป็น placeholder ต้องแทนด้วย base64 ของ JSON จริงก่อนใช้
- Publisher ไม่ใส่ `message.attributes`; field นี้อาจไม่ปรากฏใน push body
- รหัสตอบกลับที่ Pub/Sub ถือว่า **ack** คือ `102`, `200`, `201`, `202`, `204` —
  ตัวอย่าง endpoint ใช้ **204 หลังเขียนสำเร็จ** รหัสอื่นหรือเกิน ack deadline = ส่งใหม่
  ตามค่า default ของ subscription ดู [รหัสตอบกลับของ Pub/Sub push](https://docs.cloud.google.com/pubsub/docs/push#how_push_endpoints_receive_messages)

### ตัวอย่างโค้ด endpoint (ฝั่งทีมที่มาใช้ — endpoint เดียว รับทุกชุด)

```python
# pip install flask google-auth requests cachecontrol
import base64
import json
import cachecontrol
import requests
from flask import Flask, request
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

AUDIENCE = "https://service.run.app"   # ตรงกับ audience ที่ Data Mart ตั้งใน sub
PUSH_SA = "sa-push-tf@databuffet-nonprd.iam.gserviceaccount.com"

app = Flask(__name__)
_google_request = google_requests.Request(
    session=cachecontrol.CacheControl(requests.Session())
)


@app.post("/pubsub")
def receive():
    # 1) ตรวจว่า request มาจาก Pub/Sub ของ Data Mart จริง (ลายเซ็น Google + audience + อีเมล SA)
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return "", 401
    try:
        claims = id_token.verify_oauth2_token(auth[7:], _google_request, audience=AUDIENCE)
    except ValueError:
        return "", 401
    if claims.get("email") != PUSH_SA or not claims.get("email_verified"):
        return "", 403

    # 2) decode message
    msg = request.get_json()["message"]
    env = json.loads(base64.b64decode(msg["data"]))
    table, op, pk = env["table"], env["operation"], env["primary_key"]

    # 3) เขียนลงปลายทางตาม primary key แล้วค่อย ack
    try:
        if op == "DELETE":
            delete_row(table, pk)
        else:                       # NEW กับ UPDATE ทำเหมือนกัน = upsert
            upsert_row(table, pk, env["data"])
    except Exception as e:
        print(f"retry {table} {op} {pk}: {e}")
        return "", 500              # ไม่ ack → Pub/Sub ส่งมาใหม่ตาม backoff
    return "", 204                  # ack หลังเขียนสำเร็จเท่านั้น


def upsert_row(table, pk, data): ...   # ทีมปลายทางเขียนลงฐานข้อมูลของตัวเอง ตาม key
def delete_row(table, pk): ...
```

ตั้ง `AUDIENCE` ให้ตรงกับค่าที่ได้รับใน handover (ขั้น 6): ตัวอย่างใช้ Cloud Run
Service URL; ถ้าเป็น HTTPS endpoint อื่น ให้เปลี่ยนเป็น endpoint URL ที่ตั้งในขั้น 3
ตัวตรวจ token ใช้ CacheControl cache certificate ตาม HTTP expiry โดยยังตรวจลายเซ็น,
audience และอีเมล SA ทุก request — ดู [คำแนะนำ cache ของ google-auth](https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html)

จุดที่พลาดบ่อย: **ห้ามข้ามการตรวจ token** (endpoint เปิดบน internet ใครก็ยิงข้อมูลปลอมเข้ามาได้)
และ **ack หลังเขียนสำเร็จเท่านั้น** (ตอบก่อนแล้วเขียนพัง = ข้อความหายเพราะ Pub/Sub ถือว่า ack แล้ว)
ถ้า body/base64/JSON หรือ field ที่จำเป็นอ่านไม่ได้ ให้ตอบรหัสที่ไม่ ack (ดู "รูปแบบ push body")
งานเขียนแต่ละข้อความควรเสร็จในไม่กี่วินาที — ถ้าช้ากว่า ack deadline Pub/Sub จะส่งซ้ำทั้งที่
ข้อความแรกยังทำอยู่

⚠️ Pub/Sub การันตีแค่ "ส่งอย่างน้อย 1 ครั้ง" (at-least-once) และไม่เรียงลำดับ —
handler ต้อง idempotent (รับข้อความเดิมซ้ำแล้วผลไม่เปลี่ยน) และต้องมีวิธีรับมือข้อความ
ต่างรอบที่มาสลับลำดับ เพราะ upsert/delete ตาม key อย่างเดียวกันข้อมูลเก่าทับข้อมูลใหม่ไม่ได้
message format นี้ไม่มีลำดับต่อแถว; วิธี reconcile ต้องตกลงกับทีมผู้ส่งก่อนใช้งานจริง

---

## Checklist ก่อนเปิดใช้งานจริง (หลัง merge)

- [ ] ทำตาม [ขั้น deploy ของ pilot](../project_wiki/cdc-process/process.md#deploy) รวมการตรวจ live compilation ก่อนรันด้วยมือ; การเพิ่ม เปลี่ยน หรือเอาตาราง export ออกให้ยึด lifecycle ใน process reference เดียวกัน
- [ ] รัน `infra/pubsub/setup.sh` ตามส่วน A (A1–A3)
- [ ] ทดสอบ publish/pull ผ่าน `sub-test-dim_company`: รอบแรก 5 `NEW`, รอบถัดไป 0 (A4)
- [ ] ต่อทีมใหม่: ได้ HTTPS endpoint และสร้าง `sa-push-<ทีม>` โดยไม่มี key (ขั้น 1–2)
- [ ] ต่อทีมใหม่ที่ใช้ Cloud Run: ให้ Invoker บน service ที่รับ push (ขั้น 2.3)
- [ ] สร้าง push subscription เฉพาะชุดที่ได้รับ พร้อม authentication และ audience ตรงกับ handover (ขั้น 3)
- [ ] ส่ง full snapshot ก่อนเข้าโหมด delta โดยคง sent state เดิมของผู้รับรายอื่น (ขั้น 4)
- [ ] ตั้ง alert backlog และส่ง handover package ครบ (ขั้น 5–6)

## งาน commission เดิม — นอก pilot นี้

รายการต่อไปนี้เป็น scope เดิมสำหรับทีม TF จาก query คุณแป้ง 8 ไฟล์ T-SQL
ยังไม่ได้เปิดส่งใน pilot และไม่ใช่รายการ resource ที่ต้องสร้างตอนนี้
รายการที่เปิดส่งจริงยึด export config ด้านบนเท่านั้น

| # | ชุดข้อมูล (`table`) | Topic | Subscription ของ TF | ไฟล์ต้นฉบับ |
|---:|---|---|---|---|
| 1 | `order` | `export-commission-order` | `sub-tf-order` | `order.sql` |
| 2 | `invoice` | `export-commission-invoice` | `sub-tf-invoice` | `invoice.sql` |
| 3 | `credit_note` | `export-commission-credit_note` | `sub-tf-credit_note` | `CreditNote.sql` |
| 4 | `debit_note` | `export-commission-debit_note` | `sub-tf-debit_note` | `DebitNote.sql` |
| 5 | `receipt` | `export-commission-receipt` | `sub-tf-receipt` | `Receipt.sql` |
| 6 | `chqri` | `export-commission-chqri` | `sub-tf-chqri` | `chqri.sql` |
| 7 | `status` | `export-commission-status` | `sub-tf-status` | `masterdate.sql` |
| 8 | `payment_method` | `export-commission-payment_method` | `sub-tf-payment_method` | `masterdate.sql` |
| 9 | `condition_payment` | `export-commission-condition_payment` | `sub-tf-condition_payment` | `masterdate.sql` |
| 10 | `company` | `export-commission-company` | `sub-tf-company` | `masterdate.sql` |
| 11 | `sell` | `export-commission-sell` | `sub-tf-sell` | `masterdate.sql` |
| 12 | `warehouse` | `export-commission-warehouse` | `sub-tf-warehouse` | `masterdate.sql` |
| 13 | `stk` | `export-commission-stk` | `sub-tf-stk` | `masterdate.sql` |
| 14 | `fob` | `export-commission-fob` | `sub-tf-fob` | `fob.sql` |

ก่อนเพิ่มชุด commission ต้องยืนยันตาราง/function ต้นทางที่ยังไม่มีในคลัง
(`mih_payment_method`, `mih_payment_mapping`, `FOB61`,
`fn_returnMihmemopaymentfromorder`) และเงื่อนไข query กับคุณแป้ง รวมถึง natural key
ที่ไม่ซ้ำของแต่ละชุด (โดยเฉพาะ `receipt`) แล้วจึงเพิ่ม config และ export view ตาม
[process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)
