# How-to: Setup Pub/Sub สำหรับส่งออกข้อมูลจาก BigQuery

> สถานะ 2026-10-26: pilot `dim_company` ใน **`databuffet-nonprd` เท่านั้น** · repo มีครบทั้ง
> Dataform (export view + ตาราง bookkeeping), Workflow
> [`infra/pubsub/datamart-publish.workflows.yaml`](../../infra/pubsub/datamart-publish.workflows.yaml)
> และสคริปต์สร้าง infra [`infra/pubsub/setup.sh`](../../infra/pubsub/setup.sh) · deploy ฝั่ง GCP
> แล้ว — หลัง PR merge รัน `setup.sh` ซ้ำตาม [ส่วน A](#ส่วน-a--deploy-และทดสอบ-pilot) เพื่อลดสิทธิ์
> ให้เหลือเท่าที่ใช้ แล้วต่อทีมผู้รับตาม [ส่วน B](#ส่วน-b--ต่อทีมที่มาใช้ข้อมูล-ทำซ้ำทุกครั้งที่มีทีมใหม่)
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

ทีมที่รับข้อมูล **ดึงเอง (pull)** จาก subscription ของทีมใน `databuffet-nonprd` ด้วย JSON key
ของ service account `sa-pull-<ทีม>` — backend ของทีมจะรันบน platform ไหนก็ได้ ไม่ต้องมี
project GCP ของตัวเอง · SA ของทีมมีสิทธิ์แค่ pull จาก subscription ของทีมเองเท่านั้น (ไม่มี
role ระดับ project) · สร้างด้วย [`infra/pubsub/add-consumer.sh`](../../infra/pubsub/add-consumer.sh)
ตาม [ส่วน B](#ส่วน-b--ต่อทีมที่มาใช้ข้อมูล-ทำซ้ำทุกครั้งที่มีทีมใหม่)

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
full snapshot ก่อนเข้าโหมด delta (ดูขั้น 3 ของส่วน B) · เครื่องมือ backfill ยังไม่อยู่ใน pilot นี้

## ส่วน A — deploy และทดสอบ pilot

ทำครั้งเดียวหลัง PR merge และ code ถึง `nonprod` (คนทำต้องเป็น project owner ของ
`databuffet-nonprd` และรันจาก WSL ที่มี `gcloud` / `bq` / `curl`) · การต่อทีมผู้รับ (subscription,
key) อยู่ในส่วน B

| ไฟล์ | หน้าที่ |
|---|---|
| [`infra/pubsub/datamart-publish.workflows.yaml`](../../infra/pubsub/datamart-publish.workflows.yaml) | Workflow 9 ขั้นตาม [สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) — generic ทุกแถวใน `mart_export_config` |
| [`infra/pubsub/setup.sh`](../../infra/pubsub/setup.sh) | สร้าง/อัปเดต infra ทั้งหมด แบบ idempotent (รันซ้ำได้) |
| [`infra/pubsub/add-consumer.sh`](../../infra/pubsub/add-consumer.sh) | ต่อทีมผู้รับแบบ pull (ส่วน B) แบบ idempotent |

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
   topic (`export-ta-dim_company`), dead-letter topic (`<topic>-dead-letter`) และสิทธิ์ publisher
   ของ Pub/Sub service agent บน dead-letter topic · ไม่สร้าง subscription ทดสอบ
   - dead-letter topic รับ dead letter ของทุก subscription ของทีมบน topic นั้น — subscription
     ของทีมและ `dlq.<ทีม>.<topic>` ที่เก็บ dead letter สร้างตอนต่อทีมด้วย `add-consumer.sh` (ส่วน B)
5. ให้สิทธิ์แบบ least privilege กับ `datamart-publisher` (สิทธิ์เท่าที่ใช้จริงเท่านั้น):

   | Role | ขอบเขต | ใช้ทำ |
   |---|---|---|
   | custom role `datamartPublishDataformReader` (`dataform.workflowInvocations.list`, `dataform.workflowInvocations.query`) | Dataform repository `data-buffet` (`us-central1`) เท่านั้น | list workflow invocations + query actions |
   | `roles/bigquery.jobUser` | project (role นี้ให้ได้แค่ระดับ project) | รัน query/DML |
   | `roles/logging.logWriter` | project (role นี้ให้ได้แค่ระดับ project) | `sys.log` ของ workflow |
   | `roles/bigquery.dataEditor` | ตาราง `mart_export_config`, `mart_sent_state` เท่านั้น | อ่าน config (tabledata.list), claim, MERGE sent state |
   | `roles/bigquery.dataViewer` | view `pub_sub.export_dim_company` เท่านั้น | diff query — view เป็น **authorized view** บน dataset ของตารางต้นทาง (`dimension_table`) จึงอ่านได้เฉพาะคอลัมน์ที่ export โดยไม่มีสิทธิ์บนตารางต้นทาง |
   | `roles/pubsub.publisher` | topic ของแต่ละชุดเท่านั้น | publish |
   | `roles/secretmanager.secretAccessor` | secret `slack-datamart-dataform` เท่านั้น | อ่าน webhook |

   `datamart-publish-trigger` ได้ custom role `datamartPublishTrigger` (`workflows.executions.create`
   อย่างเดียว) เป็น role เดียวของมัน — ระดับ project เพราะ Workflows ไม่มี IAM รายตัวและ IAM
   Conditions ไม่รองรับ resource ของ Workflows
   · สิทธิ์ที่กว้างกว่าซึ่งสคริปต์รุ่นก่อนให้ไว้ (`roles/dataform.viewer` และ `roles/workflows.invoker`
   ระดับ project, `roles/bigquery.dataViewer` บนตารางต้นทาง) ถูกถอดออกทุกครั้งที่รัน ถ้ายังมีอยู่
6. deploy workflow `datamart-publish` (`asia-southeast1`) ให้รันเป็น `datamart-publisher`
7. สร้าง/อัปเดต Scheduler job `datamart-publish-every-5m` (`*/5 * * * *`, Asia/Bangkok)
   ที่ POST ไป Workflow Executions API ด้วย OAuth ของ `datamart-publish-trigger`

### A4. ตรวจผลรอบแรก

Workflow จะ export เมื่อมีรอบ Dataform ที่สำเร็จและรัน action `dim_company` สำเร็จ —
`daily_process` รันทุกวันอยู่แล้ว · ครั้งแรก (`last_invocation_end` ยังเป็น `NULL`)
มองย้อนหลัง 48 ชั่วโมง จึงไม่ต้องรอรอบใหม่

1. รอ Scheduler รอบถัดไป (ไม่เกิน 5 นาที) หรือสั่งเองทันที:
   `gcloud workflows run datamart-publish --location=asia-southeast1 --project=databuffet-nonprd`
   ผลลัพธ์ execution (ดูได้ใน **Workflows → datamart-publish → Executions** ด้วย) ต้องเป็น
   `["dim_company: sent 5 rows for <invocation id>"]` — 5 แถว `NEW` หนึ่งแถวต่อบริษัท
2. ตรวจ bookkeeping: `process_dataset.mart_sent_state` มี 5 แถวของ `dim_company` และ
   `mart_export_config.last_invocation_id` = invocation นั้น, `claimed_at` = `NULL`
3. สั่ง workflow อีกครั้ง → ผลลัพธ์ `no new invocation` (หรือ `advanced to ...` ถ้ามีรอบอื่น
   จบระหว่างนั้น) และ `mart_sent_state` ไม่เปลี่ยน · หลังรอบ `daily_process` ถัดไปผลคือ
   `dim_company: sent 0 rows for <invocation id>` ถ้า `dim_company` ไม่เปลี่ยน
4. ทดสอบ Slack: ดู execution ที่ล้มเหลวใน **Workflows → datamart-publish → Executions**
   ต้องมีข้อความใน channel ของ webhook · ถ้ายังไม่เคยล้มเหลว ไม่ต้องสร้างความล้มเหลวเอง

ถ้า export ล้มเหลว `last_invocation_*` ไม่ขยับ และ `claimed_at` ค้างไว้จนครบ 30 นาที
แล้ว Scheduler รอบถัดไปจะทำซ้ำเอง (ข้อความที่ publish ไปแล้วแต่ยังไม่บันทึกอาจถูกส่งซ้ำ)

---

## ส่วน B — ต่อทีมที่มาใช้ข้อมูล (ทำซ้ำทุกครั้งที่มีทีมใหม่)

ทุกทีม — ในบริษัทหรือนอกบริษัท — ใช้ขั้นตอนเดียวกันนี้เสมอ: ทีม **pull** จาก subscription
ของตัวเองด้วย JSON key ของ `sa-pull-<ทีม>` · ทุกอย่างอยู่ใน `databuffet-nonprd` ไม่มี project
แยก IAM เป็นตัวคุม · ตัวอย่างด้านล่างใช้ทีม AI ฝั่ง dev (`<ทีม>` = `ai-dev`)

### 1. รัน `add-consumer.sh`

**ทำ**: ใส่ชื่อทีม (รวม environment ในชื่อ เช่น `ai-dev`) และ topic ทุกชุดที่ทีมได้รับจาก
[export config](../../includes/controller/mart-export-config.json)

```bash
bash infra/pubsub/add-consumer.sh ai-dev export-ta-dim_company
```

ชื่อทีมใช้ได้เฉพาะตัวพิมพ์เล็ก ตัวเลข และ `-` (ขึ้นต้นและลงท้ายด้วยตัวอักษรหรือตัวเลข)
ยาวไม่เกิน 22 ตัว เพราะ `sa-pull-<ทีม>` ต้องไม่เกิน 30 ตัว · สคริปต์หยุดถ้า topic หรือ
`<topic>-dead-letter` ยังไม่มี (รัน `setup.sh` ก่อน) · รันซ้ำได้ — apply ค่าเดิมซ้ำ หรือเพิ่ม
topic ให้ทีมเดิม · พิมพ์ทุกอย่างที่สร้าง และ **ไม่สร้าง key**

สิ่งที่สร้าง:

| Resource | ชื่อ | ค่าที่ตั้ง | สิทธิ์ |
|---|---|---|---|
| Service account (1 ต่อทีม) | `sa-pull-<ทีม>` | ไม่มี key, ไม่มี role ระดับ project | — |
| Pull subscription (1 ต่อ topic) | `sub.<ทีม>.<topic>` เช่น `sub.ai-dev.export-ta-dim_company` | ack deadline 60 วินาที · เก็บข้อความ 7 วัน **รวมข้อความที่ ack แล้ว** · ไม่หมดอายุ · retry 10–600 วินาที · ส่งไม่สำเร็จครบ 5 ครั้ง → `<topic>-dead-letter` | `roles/pubsub.subscriber` ให้ `sa-pull-<ทีม>` และ Pub/Sub service agent บน subscription นี้เท่านั้น |
| Dead-letter hold (1 ต่อ topic) | `dlq.<ทีม>.<topic>` บน `<topic>-dead-letter` | เก็บ 31 วัน · ไม่หมดอายุ · filter `attributes.CloudPubSubDeadLetterSourceSubscription = "sub.<ทีม>.<topic>"` | ไม่ให้ทีม — เราอ่านเองเท่านั้น |

Pub/Sub service agent มี `roles/pubsub.publisher` บน `<topic>-dead-letter` — `setup.sh` เป็นผู้ให้สิทธิ์นี้ (ส่วน A ขั้น 4) สคริปต์นี้ไม่ให้ซ้ำ

**ทำไม**: SA แยกต่อทีม ปิดทีมใดทีมหนึ่งได้ไม่กระทบทีมอื่น · สิทธิ์ pull ให้ที่ **subscription
ของทีมเท่านั้น** ไม่ให้ระดับ project เพราะ role Pub/Sub ระดับ project จะ pull subscription ของ
ทีมอื่นได้ด้วย · subscription คือ "ตัวชี้ว่าส่งถึงไหน" ส่วนตัวของแต่ละทีม ทีมนี้ดึงช้าไม่กระทบ
ทีมอื่นบน topic เดียวกัน · เก็บข้อความที่ ack แล้ว 7 วัน เพื่อ replay หลังเกิดเหตุได้ (ดู "Replay")
· ข้อความที่ทีมรับไม่สำเร็จ 5 ครั้งไปพักที่ `dlq.<ทีม>.<topic>` แทนการวนส่งไม่จบ —
`dlq` สร้างก่อน subscription เสมอ dead letter จึงไม่หายเพราะไม่มีที่รับ

### 2. สร้าง JSON key ด้วยมือ แล้วส่งให้ทีม

**ทำ**: project owner สร้าง key หนึ่งครั้งต่อทีม เขียนไฟล์ไว้ **นอก repo**:

```bash
gcloud iam service-accounts keys create "$HOME/sa-pull-ai-dev.json" --iam-account=sa-pull-ai-dev@databuffet-nonprd.iam.gserviceaccount.com --project=databuffet-nonprd
```

ส่งไฟล์ให้ทีมผ่านช่องทางที่ปลอดภัย (ไม่แปะในแชทหรืออีเมลแบบเปิด) แล้วลบไฟล์ในเครื่อง ·
ห้าม commit key เข้า repo

**ทำไม**: backend ของทีมอาจรันบน platform ไหนก็ได้ จึงใช้ key แทน identity ของ GCP · key
ไม่หมดอายุและไม่ rotate · การสร้างและส่ง key ทำด้วยมือเท่านั้น สคริปต์ไม่สร้างหรือพิมพ์ key ·
key นี้ทำได้แค่ pull จาก `sub.<ทีม>.*` ของทีมเอง ถ้าหลุดก็ไม่ถึงข้อมูลอื่น · ถ้าต้องตัดทีม ลบ
key (`gcloud iam service-accounts keys delete`) หรือลบ subscription ของทีม

### 3. Backfill ให้ทีมใหม่ (ครั้งแรกที่ต่อเข้ามาเท่านั้น)

**ทำ**: หลังสร้าง sub ครบแล้ว ประสาน Data Mart ให้ส่ง full snapshot ของ export view
ก่อนรับ delta ตามปกติ เครื่องมือ backfill ยังไม่อยู่ใน pilot นี้ (จะทำแยก)
ห้ามล้าง sent state ที่ใช้ร่วมกันเพื่อเริ่มต้นให้ทีมใหม่

**ทำไม**: export ปกติเป็น delta อย่างเดียว ทีมใหม่ที่เพิ่งต่อจะไม่มีข้อมูลตั้งต้นถ้าไม่
backfill ก่อน — ข้อความ publish เข้า topic จะไปถึง **ทุก sub บน topic นั้น** ไม่ใช่แค่
ทีมใหม่ ทีมเดิมจึงได้ข้อมูลซ้ำด้วย ต้องประสานทุกทีมและตกลงวิธีรับมือ snapshot กับ delta
ที่อาจมาสลับลำดับกันก่อนส่ง

### 4. ตั้ง alert เมื่อข้อความค้าง

**ทำ**: **Monitoring → Alerting → CREATE POLICY** → metric
`Pub/Sub Subscription → Unacked messages` (`num_undelivered_messages`) → filter
`subscription_id` starts with `sub.<ทีม>.` → Group by `subscription_id` → threshold
ตามที่เหมาะสม → ส่งแจ้งเตือนไป Slack channel เดียวกับ Dataform · ตั้งอีก policy สำหรับ
`subscription_id` starts with `dlq.<ทีม>.` ที่ threshold `> 0`

**ทำไม**: policy เดียวครอบ sub ของทีมนั้นทุกชุด ไม่ต้องตั้งทีละอัน — ข้อความค้าง = ทีมไม่ได้
ดึงหรือดึงแล้วไม่ ack ข้อความที่ยังไม่ ack เก็บไว้ 7 วัน ถ้าทีมไม่กลับมาดึงนานเกินนั้นข้อมูลจะหาย
ต้องรู้ก่อน · ข้อความใน `dlq.<ทีม>.` = ทีมรับไม่สำเร็จครบ 5 ครั้ง ต้องคุยกับทีม

### 5. ส่ง handover package ให้ทีม

ส่งให้ครบ 5 อย่าง:

1. JSON key จากขั้น 2 — **เป็น secret** ส่งผ่านช่องทางที่ปลอดภัยเท่านั้น
2. ชื่อเต็มของ subscription ทุกชุดที่ได้รับ เช่น
   `projects/databuffet-nonprd/subscriptions/sub.ai-dev.export-ta-dim_company`
3. Message format (ตารางด้านบน) + พฤติกรรมของ subscription (ด้านล่าง)
4. รายชื่อชุดข้อมูล + primary key ของแต่ละชุด
5. ตัวอย่างโค้ด consumer (Data Mart เขียนให้ — ตัวอย่างด้านล่าง)

**ทำไม**: เป็น handover package มาตรฐานเดียว ใช้ซ้ำได้กับทุกทีมที่มาใหม่ ไม่ต้องคิดใหม่ทุกครั้ง

### พฤติกรรมของ subscription (สิ่งที่ทีมต้องรู้)

- `message.data` = JSON ตาม Message format ด้านบน (client library ถอด base64 ให้แล้ว) ·
  publisher ไม่ใส่ message attributes
- ต้อง **ack ภายใน 60 วินาที** หลังเขียนสำเร็จ (client library ต่อเวลาให้อัตโนมัติระหว่างประมวลผล)
  — nack หรือเกินเวลา = ส่งใหม่ โดยรอ 10 วินาทีเพิ่มขึ้นจนถึง 10 นาที
- ส่งไม่สำเร็จครบ **5 ครั้ง** ข้อความย้ายไปที่ `dlq.<ทีม>.<topic>` ซึ่งทีมอ่านไม่ได้ — แจ้ง
  Data Mart ให้ตรวจ (`gcloud pubsub subscriptions pull dlq.<ทีม>.<topic> --project=databuffet-nonprd --limit=10`
  ไม่ ack จึงดูได้โดยข้อความไม่หาย) · เก็บไว้ 31 วัน
- ข้อความที่ยังไม่ ack เก็บไว้ **7 วัน** หลังจากนั้นหาย

### Replay หลังเกิดเหตุ

ข้อความที่ ack แล้วยังเก็บไว้ 7 วัน จึงย้อนส่งใหม่ได้ด้วยการ seek subscription ของทีมไปเวลา
ก่อนเกิดเหตุ — ทุกข้อความหลังเวลานั้นจะถูกส่งอีกครั้ง (ทีมต้องรับซ้ำได้):

```bash
gcloud pubsub subscriptions seek sub.ai-dev.export-ta-dim_company --time=2026-10-26T00:00:00+07:00 --project=databuffet-nonprd
```

### ตัวอย่างโค้ด consumer (ฝั่งทีมที่มาใช้ — pull ทุกชุดด้วย callback เดียว)

```python
# pip install google-cloud-pubsub
import json
from google.cloud import pubsub_v1
from google.oauth2 import service_account

KEY_FILE = "/secure/path/sa-pull-ai-dev.json"   # key จาก handover — ห้าม commit
SUBSCRIPTIONS = [
    "projects/databuffet-nonprd/subscriptions/sub.ai-dev.export-ta-dim_company",
]


def upsert_row(table, pk, data): ...   # ทีมปลายทางเขียนลงฐานข้อมูลของตัวเอง ตาม key
def delete_row(table, pk): ...


def callback(message):
    env = json.loads(message.data)
    table, op, pk = env["table"], env["operation"], env["primary_key"]
    try:
        if op == "DELETE":
            delete_row(table, pk)
        else:                       # NEW กับ UPDATE ทำเหมือนกัน = upsert
            upsert_row(table, pk, env["data"])
    except Exception as e:
        print(f"retry {table} {op} {pk}: {e}")
        message.nack()              # ส่งใหม่ตาม retry; ครบ 5 ครั้งไป dead letter
        return
    message.ack()                   # ack หลังเขียนสำเร็จเท่านั้น


credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
futures = [subscriber.subscribe(s, callback=callback) for s in SUBSCRIPTIONS]
with subscriber:
    for f in futures:
        f.result()                  # รันจนกว่าจะหยุด process
```

จุดที่พลาดบ่อย: **ack หลังเขียนสำเร็จเท่านั้น** (ack ก่อนแล้วเขียนพัง = ข้อความหายเพราะ Pub/Sub
ถือว่ารับแล้ว) · ถ้า JSON หรือ field ที่จำเป็นอ่านไม่ได้ ให้ nack (ครบ 5 ครั้งจะไป dead letter
ให้ Data Mart ตรวจ) · เก็บ key ไว้นอก source code และไม่ log ค่าใน key

⚠️ Pub/Sub การันตีแค่ "ส่งอย่างน้อย 1 ครั้ง" (at-least-once) และไม่เรียงลำดับ —
handler ต้อง idempotent (รับข้อความเดิมซ้ำแล้วผลไม่เปลี่ยน) และต้องมีวิธีรับมือข้อความ
ต่างรอบที่มาสลับลำดับ เพราะ upsert/delete ตาม key อย่างเดียวกันข้อมูลเก่าทับข้อมูลใหม่ไม่ได้
message format นี้ไม่มีลำดับต่อแถว; วิธี reconcile ต้องตกลงกับทีมผู้ส่งก่อนใช้งานจริง

---

## Checklist ก่อนเปิดใช้งานจริง (หลัง merge)

- [ ] ทำตาม [ขั้น deploy ของ pilot](../project_wiki/cdc-process/process.md#deploy) รวมการตรวจ live compilation ก่อนรันด้วยมือ; การเพิ่ม เปลี่ยน หรือเอาตาราง export ออกให้ยึด lifecycle ใน process reference เดียวกัน
- [ ] รัน `infra/pubsub/setup.sh` ตามส่วน A (A1–A3)
- [ ] ตรวจผล execution ของ `datamart-publish` และ `mart_sent_state`: รอบแรก `sent 5 rows`, รอบถัดไป `sent 0 rows` (A4)
- [ ] ต่อทีมใหม่: รัน `add-consumer.sh <ทีม> <topic>...` เฉพาะชุดที่ทีมได้รับ (ขั้น 1)
- [ ] สร้าง JSON key ด้วยมือนอก repo แล้วส่งผ่านช่องทางที่ปลอดภัย (ขั้น 2)
- [ ] ส่ง full snapshot ก่อนเข้าโหมด delta โดยคง sent state เดิมของผู้รับรายอื่น (ขั้น 3)
- [ ] ตั้ง alert backlog + dead letter และส่ง handover package ครบ (ขั้น 4–5)

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
