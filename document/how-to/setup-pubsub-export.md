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
project GCP ของตัวเอง · SA ของทีมมีสิทธิ์แค่ pull จาก subscription ของทีมเอง และอ่านไฟล์
โหลดครั้งแรกใน folder ของทีมเองเท่านั้น (ไม่มี role ระดับ project) · สร้างด้วย [`infra/pubsub/add-consumer.sh`](../../infra/pubsub/add-consumer.sh)
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

⚠️ **ทีมใหม่ที่ต่อครั้งแรก**: Pub/Sub ส่งเฉพาะแถวที่เปลี่ยนหลังต่อ subscription · ข้อมูลตั้งต้น
ทั้งตาราง **ไม่ส่งผ่าน Pub/Sub** แต่เป็นไฟล์ JSON ใน GCS ที่หนึ่งบรรทัดคือหนึ่งข้อความ `NEW`
ตาม format ข้างบน (ดูขั้น 3 ของส่วน B)

## ส่วน A — deploy และทดสอบ pilot

ทำครั้งเดียวหลัง PR merge และ code ถึง `nonprod` (คนทำต้องเป็น project owner ของ
`databuffet-nonprd` และรันจาก WSL ที่มี `gcloud` / `bq` / `curl`) · การต่อทีมผู้รับ (subscription,
key) อยู่ในส่วน B

| ไฟล์ | หน้าที่ |
|---|---|
| [`infra/pubsub/datamart-publish.workflows.yaml`](../../infra/pubsub/datamart-publish.workflows.yaml) | Workflow 9 ขั้นตาม [สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) — generic ทุกแถวใน `mart_export_config` |
| [`infra/pubsub/setup.sh`](../../infra/pubsub/setup.sh) | สร้าง/อัปเดต infra ทั้งหมด แบบ idempotent (รันซ้ำได้) |
| [`infra/pubsub/add-consumer.sh`](../../infra/pubsub/add-consumer.sh) | ต่อทีมผู้รับแบบ pull (ส่วน B) แบบ idempotent |
| [`infra/pubsub/export-snapshot.sh`](../../infra/pubsub/export-snapshot.sh) | export ไฟล์โหลดครั้งแรกของทีมใหม่ (ส่วน B ขั้น 3) |

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
2. เปิด API: Workflows, Workflow Executions, Cloud Scheduler, Pub/Sub, Secret Manager, Cloud Storage
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
8. สร้าง bucket `databuffet-nonprd-datamart-snapshot` สำหรับไฟล์โหลดครั้งแรก (ส่วน B ขั้น 3)
   ใน `us-central1` ที่เดียวกับ dataset `pub_sub` (สคริปต์หยุดถ้าไม่ตรง) · uniform bucket-level
   access + public access prevention · ถอด convenience bindings ของ `projectViewer` และ
   `projectEditor` บน bucket ทั้งหลังสร้างและเมื่อรันซ้ำ · คง `projectOwner` ไว้ให้ operator
   export และจัดการไฟล์ได้ · สร้าง custom role `datamartSnapshotGet` (`storage.objects.get`)
   ไว้ให้ `add-consumer.sh` ผูกกับ folder ของแต่ละทีม ดังนั้น policy บน bucket ให้ Owner
   อ่านได้ทั้ง bucket ส่วน SA ผู้รับอ่านตามชื่อไฟล์ได้เฉพาะ folder ของทีม

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
| สิทธิ์อ่านไฟล์โหลดครั้งแรก (1 ต่อทีม) | folder `gs://databuffet-nonprd-datamart-snapshot/<ทีม>/` | — | `datamartSnapshotGet` เมื่อชื่อ object ขึ้นต้นด้วย `<ทีม>/` (IAM Condition บน bucket) ให้ `sa-pull-<ทีม>` — ดาวน์โหลด manifest และไฟล์ตามชื่อที่ระบุเท่านั้น |

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
key นี้ทำได้แค่ pull จาก `sub.<ทีม>.*` และอ่านไฟล์ใน folder `<ทีม>/` ของทีมเอง ถ้าหลุดก็ไม่ถึง
ข้อมูลอื่น · ถ้าต้องตัดทีม ลบ key (`gcloud iam service-accounts keys delete`) — ลบแค่
subscription ของทีม ทีมยังอ่านไฟล์ใน folder ของทีมได้

### 3. โหลดครั้งแรกด้วยไฟล์ (ครั้งแรกที่ทีมต่อ topic นั้นเท่านั้น)

**ทำ**: หลังขั้น 1 (subscription ของทีมต้องมีอยู่แล้ว — สคริปต์ไม่ยอมรันถ้ายังไม่มี) export
ทุกแถวปัจจุบันของ export view ของ topic นั้นลง folder ของทีม ทีละ topic:

```bash
bash infra/pubsub/export-snapshot.sh ai-dev export-ta-dim_company
```

สคริปต์พิมพ์ folder และ **export time** (UTC) แล้วส่งทั้งสองค่าให้ทีม · ใช้ path ของ folder
ตามที่สคริปต์พิมพ์ ซึ่งลงท้ายด้วยเวลาแบบ `YYYYMMDDTHHMMSSffffffZ` (microseconds 6 หลัก)
ส่วน `export_time` ใน manifest เป็น RFC3339 · ใน folder มี:

- `data-<เลข>.json` (ตารางใหญ่แบ่งหลายไฟล์) — newline-delimited JSON หนึ่งบรรทัดต่อแถว
  แต่ละบรรทัด **ตรงทุก byte** กับข้อความที่ workflow publish ให้แถวนั้นเป็น `NEW` (สร้างจาก diff
  query ตัวเดียวกับใน workflow) ทีมจึงโหลดด้วยโค้ดเดียวกับ consumer
- `manifest.json` — `table`, `topic`, `team`, `export_time`, `row_count`, `files` · เขียนเป็นไฟล์
  สุดท้ายหลัง seek สำเร็จและรอ 90 วินาทีแล้ว folder ที่ไม่มี manifest คือ export ที่ไม่เสร็จ
  ห้ามโหลดหรือเริ่ม pull

สคริปต์ claim แถวของตารางนั้นใน `mart_export_config` เฉพาะเมื่อ `claimed_at` ว่างเท่านั้น
ถ้ามี claim อยู่ แม้เกิน 30 นาทีแล้ว ให้รอ publisher รอบถัดไปคืน claim แล้วลองใหม่
สคริปต์ไม่ยึด claim ที่หมดอายุ · จากนั้นอ่าน export view ลงตาราง
ชั่วคราวและเทียบ `row_key`/`row_hash` กับ `mart_sent_state` ใน transaction เดียวกัน
ต้องตรงกันทั้งหมด ไม่มีแถวขาด เกิน หรือ hash ต่างกัน มิฉะนั้นหยุด ให้รอ publisher รอบถัดไป
แล้วลองใหม่ · **export time คือเวลาเริ่ม transaction นี้** (UTC) และไฟล์สร้างจากตารางชั่วคราว
ชุดที่ตรวจแล้ว จึงไม่เปลี่ยนตาม Dataform ระหว่าง export

หลังเขียนไฟล์ข้อมูลครบและตรวจจำนวนแถวแล้ว สคริปต์ seek `sub.<ทีม>.<topic>` ไปที่ export time
ขณะยังถือ claim เพื่อ mark ข้อความที่ publish ก่อนจุดนี้เป็น acknowledged รวม key ที่ไม่มีในไฟล์
เมื่อ seek สำเร็จ สคริปต์ยังถือ claim และรอ **90 วินาที** ก่อนเขียน manifest เป็นไฟล์สุดท้าย
แล้วคืน claim เพราะ [seek อาจใช้เวลาถึงหนึ่งนาทีจึงมีผลต่อการส่งข้อความครบถ้วน](https://docs.cloud.google.com/pubsub/docs/replay-overview#eventual_consistency_of_seek_operations)
· ถ้า seek หรือการรอล้มเหลว การ export ถือว่าล้มเหลว ไม่มี manifest และลบไฟล์ที่เขียนค้าง
พร้อมคืน claim · ทีมต้องรอ manifest แล้วโหลดไฟล์ให้เสร็จก่อนเริ่ม pull

ค่าใช้จ่าย BigQuery = อ่าน export view หนึ่งรอบ อ่าน sent state เพื่อตรวจ และอ่านตารางชั่วคราว
เพื่อ export/นับแถว · ไฟล์ผ่านเครื่องที่รันสคริปต์หนึ่งรอบเพื่อแปลงจาก CSV เป็นบรรทัดข้อความ ·
สคริปต์เขียนเฉพาะ `claimed_at` และพยายามคืน claim ด้วย token ของตัวเองเมื่อจบ รวมกรณีล้มเหลว
โดยไม่เปลี่ยน `last_invocation_*` · `mart_sent_state` อ่านอย่างเดียว ไม่เปลี่ยน workflow
และไม่ส่งอะไรเข้า Pub/Sub — ห้ามล้าง sent state ที่ใช้ร่วมกันเพื่อเริ่มต้นให้ทีมใหม่

ถ้าเขียน manifest สำเร็จแล้วแต่คืน claim ไม่สำเร็จ สคริปต์แจ้งว่า export สำเร็จและจบด้วย exit 0
ไฟล์พร้อมใช้งานตามเดิม ส่วน claim หมดอายุเองตาม timeout 30 นาทีของ publisher ·
ไม่ต้องรัน export ซ้ำเพื่อคืน claim เพราะจะ seek subscription ไปที่ cut ใหม่

ฝั่งทีม ตามลำดับนี้:

1. รอให้ `manifest.json` มีอยู่ก่อน แล้วดาวน์โหลดทุกไฟล์ใน `files` ด้วย key เดียวกับที่ใช้ pull ส่งทุกบรรทัดเข้า
   handler เดียวกับ consumer (`apply` ในตัวอย่างด้านล่าง) โดยบันทึก **`export_time` เป็น version ของทุกแถว**
2. หลังมี manifest และโหลดไฟล์ครบแล้วจึงเริ่ม pull · สคริปต์ seek ให้ subscription เริ่มที่ export time
   และรอ propagation แล้ว จึงไม่ต้องใช้
   version ของแถวข้ามข้อความก่อน export · สำหรับข้อความหลัง cut ใช้ `apply` เดิมข้ามข้อความ
   ที่ `publish_time` ไม่ใหม่กว่า version ของแถว รวม DELETE และข้อความซ้ำ ข้อความที่ใหม่กว่า
   เขียนทับแล้วเก็บ `publish_time` เป็น version ใหม่ · ต้องเริ่ม pull ภายใน 7 วันหลัง export
   (ข้อความที่ยังไม่ ack เก็บ 7 วัน) หากพลาดระยะเก็บข้อความ ให้ติดต่อทีม Data Mart

```python
# pip install google-cloud-storage — ใช้ credentials เดียวกับ consumer
import json
from google.cloud import storage

client = storage.Client(project="databuffet-nonprd", credentials=credentials)
bucket = client.bucket("databuffet-nonprd-datamart-snapshot")      # ไม่เรียก get_bucket: ไม่มีสิทธิ์บน bucket
manifest = json.loads(bucket.blob(FOLDER + "manifest.json").download_as_bytes())   # FOLDER = path ที่สคริปต์พิมพ์ ตัด gs://<bucket>/ ออก
for uri in manifest["files"]:
    with bucket.blob(uri.split("/", 3)[3]).open("r", encoding="utf-8") as f:
        for line in f:
            env = json.loads(line)
            apply(env, manifest["export_time"])
```

**ทำไม**: Pub/Sub ส่งเฉพาะการเปลี่ยนแปลง (forward-only) และข้อความที่ publish เข้า topic ไปถึง
**ทุก sub บน topic นั้น** การส่งข้อมูลตั้งต้นผ่าน topic จะทำให้ทีมเดิมได้ข้อมูลซ้ำทั้งตาราง ·
ไฟล์ใน GCS รองรับตารางทุกขนาด (เช่น `sales_daily` ~1.65 ล้านแถว) และใช้ key เดิม ·
ลำดับ "subscription ก่อน → claim เฉพาะเมื่อว่าง → ตรวจว่า view ตรงกับ sent state → export
ชุดที่ตรวจแล้ว → seek ไปที่ cut → ถือ claim รอ 90 วินาที → manifest → คืน claim" ทำให้ไฟล์ตรงกับสถานะที่ publisher
ส่งสำเร็จ ณ export time และ subscription ตัดข้อความก่อน cut ออก รวมแถวที่ไม่มีในไฟล์ ·
ข้อมูลที่เปลี่ยนหลังจุดนี้จะถูกเทียบกับ sent state เดิมในรอบถัดไป ข้อความมี `publish_time`
หลัง export time และรอใน subscription ของทีม · `apply` จัดการการรับซ้ำหรือสลับลำดับของ
ข้อความหลัง cut รวม DELETE ด้วย · ยังต้องให้ publisher รันสำเร็จและทีม pull ภายใน
ระยะเก็บข้อความ การเปลี่ยนไปแล้วกลับมาก่อน publisher อ่านจะไม่เกิดข้อความ แต่ไม่ทำให้
ไฟล์ค้างอยู่ที่ค่าระหว่างทาง เพราะ export ยอมผ่านเฉพาะชุดที่ตรงกับ sent state

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
ก่อนเกิดเหตุ — ทุกข้อความหลังเวลานั้นจะถูกส่งอีกครั้ง (ทีมต้องรับซ้ำได้) · เลือก `REPLAY_TIME`
เป็นเวลา RFC3339 ที่ไม่ก่อน `export_time` ของ first load ใน manifest เพื่อไม่เปิดรับข้อความ
ก่อน cut อีกครั้ง ถ้าต้องย้อนก่อนจุดนี้ ให้ติดต่อทีม Data Mart:

```bash
gcloud pubsub subscriptions seek sub.ai-dev.export-ta-dim_company --time="$REPLAY_TIME" --project=databuffet-nonprd
```

### ตัวอย่างโค้ด consumer (ฝั่งทีมที่มาใช้ — pull ทุกชุดด้วย callback เดียว)

```python
# pip install google-cloud-pubsub
import json
from datetime import datetime
from google.cloud import pubsub_v1
from google.oauth2 import service_account

KEY_FILE = "/secure/path/sa-pull-ai-dev.json"   # key จาก handover — ห้าม commit
SUBSCRIPTIONS = [
    "projects/databuffet-nonprd/subscriptions/sub.ai-dev.export-ta-dim_company",
]


def row_transaction(table, pk): ...
def read_version(tx): ...
def upsert_row(tx, data): ...
def delete_row(tx): ...
def save_version(tx, version): ...


def apply(env, version):
    version = datetime.fromisoformat(version.replace("Z", "+00:00"))
    with row_transaction(env["table"], env["primary_key"]) as tx:
        stored = read_version(tx)
        if stored is not None and version <= stored:
            return
        op = env["operation"]
        if op == "DELETE":
            delete_row(tx)
        elif op in ("NEW", "UPDATE"):
            upsert_row(tx, env["data"])
        else:
            raise ValueError(f"unknown operation: {op}")
        save_version(tx, version)


def callback(message):
    try:
        apply(json.loads(message.data), message.publish_time.isoformat())
    except Exception as e:
        print(f"retry {message.message_id}: {e}")
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

ทีมต้องเขียน 5 ฟังก์ชันเชื่อมฐานข้อมูลตามตัวอย่าง: `row_transaction` ต้องเป็น transaction ที่
serialize ทุกการเขียนต่อ `(table, primary_key)` เดียวกัน รวม key ที่ยังไม่มีแถว และ commit/rollback
ข้อมูลพร้อม version เป็นหน่วยเดียว · `read_version` คืน `None` ถ้ายังไม่เคยรับ key นั้น มิฉะนั้น
คืน timezone-aware `datetime` UTC ที่ `save_version` เก็บไว้ · DELETE ลบข้อมูลแต่ต้องเก็บ version
แยกไว้เป็น tombstone เพื่อกัน NEW/UPDATE เก่าทำให้แถวกลับมา · ใช้ `apply` เดียวกันกับโค้ด
โหลดไฟล์ในขั้น 3 ให้รอ manifest และโหลดเสร็จก่อนเรียก `subscriber.subscribe` และใช้ storage เดียวกันหลัง restart

จุดที่พลาดบ่อย: **ack หลังเขียนสำเร็จหรือข้าม version เก่าแล้วเท่านั้น** (ack ก่อนแล้วเขียนพัง = ข้อความหายเพราะ Pub/Sub
ถือว่ารับแล้ว) · ถ้า JSON หรือ field ที่จำเป็นอ่านไม่ได้ ให้ nack (ครบ 5 ครั้งจะไป dead letter
ให้ Data Mart ตรวจ) · เก็บ key ไว้นอก source code และไม่ log ค่าใน key

⚠️ Pub/Sub การันตีแค่ "ส่งอย่างน้อย 1 ครั้ง" (at-least-once) และไม่เรียงลำดับ —
สคริปต์ bootstrap seek ข้ามข้อความก่อน cut ที่ subscription และรอ 90 วินาทีก่อนเขียน manifest
ทีมเริ่ม pull หลังมี manifest และโหลดไฟล์ครบเท่านั้น ส่วน `apply` ใช้ `publish_time`
เป็น version เพื่อจัดลำดับข้อความหลัง cut และข้ามข้อความซ้ำ รวม DELETE · `publish_time`
คือลำดับการ publish ไม่ใช่ลำดับแก้ไขที่ต้นทาง

---

## Checklist ก่อนเปิดใช้งานจริง (หลัง merge)

- [ ] ทำตาม [ขั้น deploy ของ pilot](../project_wiki/cdc-process/process.md#deploy) รวมการตรวจ live compilation ก่อนรันด้วยมือ; การเพิ่ม เปลี่ยน หรือเอาตาราง export ออกให้ยึด lifecycle ใน process reference เดียวกัน
- [ ] รัน `infra/pubsub/setup.sh` ตามส่วน A (A1–A3)
- [ ] ตรวจผล execution ของ `datamart-publish` และ `mart_sent_state`: รอบแรก `sent 5 rows`, รอบถัดไป `sent 0 rows` (A4)
- [ ] ต่อทีมใหม่: รัน `add-consumer.sh <ทีม> <topic>...` เฉพาะชุดที่ทีมได้รับ (ขั้น 1)
- [ ] สร้าง JSON key ด้วยมือนอก repo แล้วส่งผ่านช่องทางที่ปลอดภัย (ขั้น 2)
- [ ] หลังมี subscription แล้ว รัน `export-snapshot.sh <ทีม> <topic>` ทีละ topic รอให้สคริปต์ seek และรอ 90 วินาทีก่อนเขียน manifest เสร็จ แล้วส่ง folder + export time ให้ทีม · ทีมรอ manifest และโหลดไฟล์ครบก่อนเริ่ม pull (ขั้น 3)
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
