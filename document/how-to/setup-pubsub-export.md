# How-to: Setup Pub/Sub สำหรับส่งออกข้อมูลจาก BigQuery

> สถานะ 2026-10-26: pilot `dim_company` ใน **`databuffet-nonprd` เท่านั้น** · repo มีครบทั้ง
> Dataform (export view + ตาราง bookkeeping), publisher แบบ Cloud Run jobs
> [`pubsub/publisher/main.py`](../../pubsub/publisher/main.py)
> และสคริปต์สร้าง infra [`pubsub/scripts/setup.sh`](../../pubsub/scripts/setup.sh) · deploy ฝั่ง GCP
> แล้วเฉพาะตัวส่ง Workflows เดิม — Cloud Run jobs ใน PR นี้ยังไม่ได้ deploy หลัง PR merge
> ทำตาม [ส่วน A](#ส่วน-a--deploy-และทดสอบ-pilot) เพื่อติดตั้งและ cut over ตัวส่งใหม่
> แล้วต่อทีมผู้รับตาม [ส่วน B](#ส่วน-b--ต่อทีมที่มาใช้ข้อมูล-ทำซ้ำทุกครั้งที่มีทีมใหม่)
> · 2026-11-02: เพิ่มชุด commission 12 ชุดของ ag01 ให้ทีม TF ใน repo แล้ว (topic `export-commission-<ชุด>`
> ดู [ส่วน C](#ส่วน-c--ชุด-commission-ของทีม-tf)) — **ยังไม่ได้ทำฝั่ง GCP** ทำตามส่วน C หลัง PR merge
> · 2026-11-02: เพิ่มชุดตารางองค์กรของแอป TA 9 ชุดให้ทีม AI ใน repo แล้ว (topic `export-ta-<ตาราง>` ดู
> [ส่วน D](#ส่วน-d--ตารางองค์กรของแอป-ta-ให้ทีม-ai)) — **ยังไม่ได้ทำฝั่ง GCP**
> · 2026-11-03: เพิ่มตารางตัวอย่างที่ส่งทีม AI แล้วอีก 33 ตาราง (topic `export-ta-<ตาราง>` ดู
> [ส่วน E](#ส่วน-e--ตารางตัวอย่างของทีม-ai-33-ตาราง)) — **ยังไม่ได้ทำฝั่ง GCP**
> รายละเอียด repo และวิธีเพิ่มตารางอยู่ที่
> [process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

## ภาพรวม

ฝั่ง GCP (region `us-central1`): Cloud Scheduler `datamart-publish-check-every-5m` เรียก Cloud Run job
`datamart-publish-check` (1 vCPU, 1 task) ทุก 5 นาทีตลอดวัน (`*/5 * * * *`) เพื่อถาม **Dataform API**
ว่ามีรอบ Dataform ใหม่ที่สำเร็จและรันตารางนั้นหรือไม่ — รองรับทุก scheduler และการรัน
manual ตาม [สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)
· ถ้ามี job ตรวจจึงสั่ง Cloud Run job `datamart-publish-send` (2 vCPU / 4 GiB ต่อ task, 5 task พร้อมกัน)
ซึ่งส่งเฉพาะแถวที่เปลี่ยน: แต่ละ task หยิบ `task_group` ถัดไปตามลำดับใน config ที่ยังมีตารางรอส่ง
(กลุ่มใหญ่ 5 กลุ่มอยู่บนสุด) · job ส่งหยุดเองที่ 25 นาที บันทึกที่ส่งแล้ว แล้วรอบตรวจถัดไปส่งส่วนที่เหลือต่อ
· ใช้ service accounts `datamart-publisher` (รัน job ส่ง), `datamart-publish-checker` (รัน job ตรวจ)
และ `datamart-publish-trigger` (Scheduler → job ตรวจ) แบบ keyless · เมื่อล้มเหลวแจ้ง Slack
ผ่าน incoming webhook ที่เก็บใน Secret Manager ชื่อ `slack-datamart-dataform`
· log เป็น JSON บน stdout ไปที่ Cloud Logging · ไม่มี Cloud Logging trigger

รายการตาราง, source view และ topic ที่ต้องสร้างอ่านจาก
[`mart-export-config.json`](../../includes/controller/mart-export-config.json)
ชื่อ topic ใช้รูปแบบ `export-<sys>-<set>` · หนึ่งชุดข้อมูลต่อหนึ่ง topic
เพื่อให้ replay/seek และให้สิทธิ์แยกต่อชุดได้ และชุดที่มีข้อความค้างไม่ถ่วงชุดอื่น
ตาราง bookkeeping และการกันส่งซ้ำอยู่ใน
[process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

ทีมที่รับข้อมูล **ดึงเอง (pull)** จาก subscription ของทีมใน `databuffet-nonprd` ·
เลือกวิธีเชื่อมต่อและดูขอบเขตสิทธิ์ที่ให้ใน
[ส่วน B](#ส่วน-b--ต่อทีมที่มาใช้ข้อมูล-ทำซ้ำทุกครั้งที่มีทีมใหม่)

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
| `primary_key` | object ของ natural key (field จริงใน `data` ไม่ใช่ hash) | key ของแต่ละชุดกำหนดใน export view — `dim_company` ใช้ `CompanyID` อย่างเดียว · ชุด commission อาจมีค่า `null` ใน key ได้ (เช่น ใบเสร็จเงินสดไม่มีเลขเช็ค) ฝั่งปลายทางต้องถือว่า `null` เท่ากัน |
| `data` | ทุก data column ของ export view (ไม่รวม `row_key` / `row_hash`) ตามชื่อและลำดับคอลัมน์ของ view | มีเฉพาะ `NEW`/`UPDATE`; `DELETE` = `null` (แถวไม่มีแล้วที่ต้นทาง) |

JSON ทั้งก้อน **สร้างโดย BigQuery** (`TO_JSON_STRING`) จึงมีรูปแบบตายตัว: ไม่มีช่องว่าง,
DATETIME = `"2026-01-30T09:10:00"`, ตัวเลขไม่มี `.0` เกิน (`700`), ค่าว่าง = `null` —
ชื่อ field ใน `data` / `primary_key` ยึดตาม
[สัญญา export view](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

ตัวอย่างนี้ใช้ค่าบริษัทสมมติ (`CompanyID = zz01`) · JSON หลัง decode มีเฉพาะ 5 field ข้างบน
ส่งหนึ่งแถวต่อหนึ่งข้อความ และ publisher ไม่ใส่ message attributes เพิ่ม
สัญญา export view และการหา `NEW` / `UPDATE` / `DELETE` อยู่ที่
[process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

⚠️ **ทีมใหม่ที่ต่อครั้งแรก**: Pub/Sub ส่งเฉพาะแถวที่เปลี่ยนหลังต่อ subscription · ข้อมูลตั้งต้น
ทั้งตาราง **ไม่ส่งผ่าน Pub/Sub** แต่เป็นไฟล์ JSON ใน GCS ที่หนึ่งบรรทัดคือหนึ่งข้อความ `NEW`
ตาม format ข้างบน (ดูขั้น 3 ของส่วน B)

## ส่วน A — deploy และทดสอบ pilot

ทำครั้งเดียวหลัง PR merge และ code ถึง `nonprod` (คนทำต้องเป็น project owner ของ
`databuffet-nonprd` และรันจาก WSL ที่มี `gcloud` / `bq` / `curl`) · การต่อทีมผู้รับ (subscription
และ identity) อยู่ในส่วน B

| ไฟล์ | หน้าที่ |
|---|---|
| [`pubsub/publisher/main.py`](../../pubsub/publisher/main.py) | โปรแกรม publisher (โหมด `check` / `send`) ตาม [สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) — generic ทุกแถวใน `mart_export_config` · `requirements.txt` และ `Dockerfile` อยู่ข้างกัน |
| [`pubsub/sql/diff.sql`](../../pubsub/sql/diff.sql) | diff query ตัวเดียว ใช้ร่วมกันโดย publisher และ `export-snapshot.sh` |
| [`pubsub/scripts/setup.sh`](../../pubsub/scripts/setup.sh) | สร้าง/อัปเดต infra ทั้งหมด แบบ idempotent (รันซ้ำได้) · `--enable-scheduler` เปิด Scheduler · `--cleanup-old` ลบตัวส่ง Cloud Workflows เดิม |
| [`pubsub/scripts/add-consumer.sh`](../../pubsub/scripts/add-consumer.sh) | ต่อทีมผู้รับแบบ pull (ส่วน B) แบบ idempotent |
| [`pubsub/scripts/export-snapshot.sh`](../../pubsub/scripts/export-snapshot.sh) | export ไฟล์โหลดครั้งแรกของทีมใหม่ (ส่วน B ขั้น 3) |
| [`includes/controller/mart-export-config.json`](../../includes/controller/mart-export-config.json) | config ของทุก topic: `task_group`, `source_tables` ฯลฯ — ไฟล์เดียวที่ Dataform และสคริปต์ใน `pubsub/` อ่าน (อยู่ใน `includes/` เพราะ Dataform `require` จากที่นี่) |

### A1. สร้างตาราง bookkeeping และ export view

ทำตาม [ขั้น deploy ของ pilot](../project_wiki/cdc-process/process.md#deploy) — รัน tag
`pub_sub` จาก release `production` แบบ include dependencies **ปิด** · `setup.sh` จะหยุด
ถ้ายังไม่มี `process_dataset.mart_export_config`, `process_dataset.mart_sent_state` หรือ
export view ของตารางใดใน config (`pub_sub.export_<ตาราง>`) · รอบที่เพิ่มตารางใหม่ tag `pub_sub`
เพิ่มแถว config โดย `last_invocation_id` / `last_invocation_end` เป็น NULL และ
`claimed_at` / `seeded_at` เป็น NULL (ยังไม่ seed) · ไม่ seed หรือเขียนไฟล์
publisher ข้ามตารางที่ `seeded_at` เป็น NULL จนถึงวันโหลดครั้งแรกที่กัปตันกำหนด (ส่วน B ขั้น 3)

### A2. ตรวจ secret ของ Slack

Webhook ของ Slack เก็บไว้แล้วใน Secret Manager ชื่อ **`slack-datamart-dataform`** (ไม่ต้องสร้างใหม่)
· ห้ามพิมพ์หรือ log ค่าของ secret · publisher อ่านค่าเฉพาะตอนต้องแจ้งความล้มเหลว

### A3. รัน `setup.sh`

```bash
bash pubsub/scripts/setup.sh
```

สคริปต์ทำตามลำดับ (ทุกขั้นเช็คก่อนสร้าง หรือ apply ซ้ำได้ไม่เสียหาย):

1. ตรวจ prerequisite ของ A1–A2
2. เปิด API: Cloud Run, Cloud Build, Artifact Registry, Cloud Scheduler, Pub/Sub, Secret Manager,
   BigQuery Storage, Monitoring, Cloud Storage (และ Dataform / BigQuery ที่เปิดอยู่แล้ว)
3. สร้าง service accounts `datamart-publish-trigger`, `datamart-publish-checker` และ
   `datamart-publisher` — **ไม่สร้าง key**
4. ต่อทุกตารางใน [`mart-export-config.json`](../../includes/controller/mart-export-config.json):
   topic (`export-ta-dim_company`, `export-commission-<ชุด>` 12 topic และ `export-ta-<ตาราง>` 9 + 33 topic), dead-letter topic (`<topic>-dead-letter`) และสิทธิ์ publisher
   ของ Pub/Sub service agent บน dead-letter topic · ไม่สร้าง subscription ทดสอบ · ตารางที่ไม่มี
   `task_group` หรือ `source_tables` ใน config ทำให้สคริปต์หยุด
   - dead-letter topic รับ dead letter ของทุก subscription ของทีมบน topic นั้น — subscription
     ของทีมและ `dlq.<ทีม>.<topic>` ที่เก็บ dead letter สร้างตอนต่อทีมด้วย `add-consumer.sh` (ส่วน B)
   - dataset staging `pubsub_staging` (ตารางหมดอายุใน 1 วัน เก็บผล diff ของแต่ละตาราง) และ dataset
     `pubsub_record` ที่มีตาราง `messages` (partition ตาม `publish_time`, เก็บ 14 วัน) · ต่อ topic
     ละ 1 **record subscription** `rec.datamart.<topic>` ชนิด BigQuery เขียนลงตารางเดียวกัน
     (write metadata, ไม่มี dead-letter) — ต้องมีก่อน job ส่งส่งข้อความแรก เพราะ subscription แบบ
     BigQuery บันทึกเฉพาะข้อความหลังสร้าง · ใช้กู้สถานะเมื่อรอบก่อนล่ม
5. ให้สิทธิ์แบบ least privilege กับ `datamart-publisher` (job ส่ง — สิทธิ์เท่าที่ใช้จริงเท่านั้น):

   | Role | ขอบเขต | ใช้ทำ |
   |---|---|---|
   | custom role `datamartPublishDataformReader` (`dataform.workflowInvocations.list`, `dataform.workflowInvocations.query`) | Dataform repository `data-buffet` (`us-central1`) เท่านั้น | list workflow invocations + query actions |
   | `roles/bigquery.jobUser` | project (role นี้ให้ได้แค่ระดับ project) | รัน query/DML |
   | `roles/bigquery.readSessionUser` | project | เปิด Storage Read session อ่านตาราง staging |
   | `roles/monitoring.viewer` | project | ดู backlog ของ record subscription ก่อนกู้สถานะ |
   | `roles/pubsub.viewer` | record subscription แต่ละตัว | อ่าน message retention เพื่อตรวจว่าข้อความที่ต้องกู้ยังไม่หมดอายุ |
   | `roles/bigquery.dataEditor` | ตาราง `mart_export_config`, `mart_sent_state` และ dataset `pubsub_staging` เท่านั้น | อ่าน config, claim, MERGE sent state, สร้างตาราง staging |
   | `roles/bigquery.dataViewer` | export view แต่ละตัวใน config (`pub_sub.export_<ตาราง>`) และตาราง `pubsub_record.messages` | diff query — view เป็น **authorized view** บน dataset ของตารางต้นทาง (ตาม `source_tables` ใน config) จึงอ่านได้เฉพาะคอลัมน์ที่ export โดยไม่มีสิทธิ์บนตารางต้นทาง · อ่านตารางบันทึก |
   | `roles/pubsub.publisher` | topic ของแต่ละชุดเท่านั้น | publish |
   | `roles/secretmanager.secretAccessor` | secret `slack-datamart-dataform` เท่านั้น | อ่าน webhook |

   job ส่งเขียน log ลง stdout จึงไม่ต้องมี `roles/logging.logWriter`
6. สิทธิ์ของ `datamart-publish-checker` (job ตรวจ): `roles/bigquery.jobUser` (project), custom role Dataform
   ข้างบน (repository เท่านั้น), `roles/bigquery.dataEditor` บน `mart_export_config` (ขยับ checkpoint),
   `roles/secretmanager.secretAccessor` บน secret Slack, และ `roles/run.invoker` + `roles/run.viewer`
   บน job `datamart-publish-send` เท่านั้น (สั่งรัน + ดูว่ายังมี execution ค้างอยู่ไหม — ไม่สั่งซ้อน)
   · `datamart-publish-trigger` ได้ `roles/run.invoker` บน job `datamart-publish-check` เท่านั้น · Pub/Sub
   service agent ได้ `roles/bigquery.dataEditor` บนตาราง `pubsub_record.messages`
   · สิทธิ์ที่กว้างกว่าซึ่งสคริปต์รุ่นก่อนให้ไว้ (`roles/dataform.viewer` ระดับ project,
   `roles/bigquery.dataViewer` บนตารางต้นทาง) ถูกถอดออกทุกครั้งที่รัน ถ้ายังมีอยู่
7. build image ด้วย Cloud Build เข้า Artifact Registry repository `cloud-run-source-deploy` ที่มีอยู่แล้ว
   (ไม่สร้าง repository ใหม่ ไม่มี IAM เพิ่ม · tag = hash ของไฟล์ ถ้าโค้ดไม่เปลี่ยนไม่ build ซ้ำ) แล้ว deploy
   job `datamart-publish-send` (5 task, parallelism 5, timeout 30 นาที, retry 0, 2 vCPU / 4 GiB)
   และ `datamart-publish-check` (1 task, timeout 5 นาที, retry 0, 1 vCPU / 512 MiB) ใน `us-central1`
   แล้วสร้าง/อัปเดต Scheduler job `datamart-publish-check-every-5m` (`*/5 * * * *`, Asia/Bangkok)
   ที่เรียก job ตรวจด้วย OAuth ของ `datamart-publish-trigger` · Scheduler ที่สร้างใหม่จะ **หยุดไว้ (paused)**
   จนกว่าจะรัน `setup.sh --enable-scheduler` — เปิดหลังลบ Scheduler ของตัวส่งเดิมเท่านั้น
8. สร้าง bucket `databuffet-nonprd-datamart-snapshot` สำหรับไฟล์โหลดครั้งแรก (ส่วน B ขั้น 3)
   ใน `us-central1` ที่เดียวกับ dataset `pub_sub` (สคริปต์หยุดถ้าไม่ตรง) · uniform bucket-level
   access + public access prevention · ถอด convenience bindings ของ `projectViewer` และ
   `projectEditor` บน bucket ทั้งหลังสร้างและเมื่อรันซ้ำ · คง `projectOwner` ไว้ให้ operator
   export และจัดการไฟล์ได้ · สร้าง custom role `datamartSnapshotGet` (`storage.objects.get`)
   ไว้ให้ `add-consumer.sh` ผูกกับ folder ของแต่ละทีม ดังนั้น policy บน bucket ให้ Owner
   อ่านได้ทั้ง bucket ส่วน SA ผู้รับอ่านตามชื่อไฟล์ได้เฉพาะ folder ของทีม

### A4. ตรวจผลรอบแรก

สำหรับ pilot ที่มี sent state อยู่แล้ว tag `pub_sub` จะ backfill `seeded_at` โดยรักษา checkpoint
เดิม · ตารางใหม่ยังไม่ publish จนทำ first-load ตามส่วน B ขั้น 3; อย่าคาดหวังข้อความ NEW ทั้งตาราง
จากการ deploy

1. รอ Scheduler รอบถัดไป (ไม่เกิน 5 นาที) หรือสั่งเองทันที:
   `gcloud run jobs execute datamart-publish-check --region=us-central1 --project=databuffet-nonprd`
   ดู log ของ job ตรวจและ job ส่งใน **Cloud Run → Jobs → <job> → Logs** (JSON: `nothing to send`,
   `send job started`, `group taken`, `sent`, `advanced, nothing to export`) · ตารางที่ยังไม่ seed
   ถูกข้ามโดยไม่มี log ของตาราง
2. ตรวจ `process_dataset.mart_sent_state` และ checkpoint ของ pilot เทียบกับ log;
   หลัง publish สำเร็จ `mart_export_config.claimed_at` ต้องเป็น `NULL`
3. สั่ง job ตรวจอีกครั้งโดยไม่มี invocation ใหม่ → sent state ต้องไม่เปลี่ยน · หลัง
   `daily_process` รอบถัดไปที่สำเร็จ ผล pilot คือ `sent` 0 แถวถ้าข้อมูลไม่เปลี่ยน
4. ตรวจการแจ้ง Slack จากรอบที่ล้มเหลวถ้ามี · ไม่ต้องสร้างความล้มเหลวเอง

รายละเอียดการเลือก invocation และ checkpoint อยู่ใน
[สัญญา publisher](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

การกู้สถานะหลังล้มเหลว เงื่อนไข retention และ backlog ที่ต้องผ่านก่อนส่งต่อ
รวมถึงการบันทึกงานบางส่วนเมื่อหมดเวลา อยู่ใน
[สัญญา publisher: Send job และ Time limit](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

### A5. ลบตัวส่งเดิม (Cloud Workflows) หลังตรวจคืนแรกผ่าน

เปลี่ยนจาก Workflows มา Cloud Run ตามลำดับนี้ (ทำช่วงกลางวัน ห่างจาก `daily_process`):
ลบ Scheduler job `datamart-publish-every-5m` (`asia-southeast1`) → `bash pubsub/scripts/setup.sh --enable-scheduler`
→ ตรวจคืนแรก → `bash pubsub/scripts/setup.sh --cleanup-old` (ลบ workflow `datamart-publish`, custom role
`datamartPublishTrigger` และ binding, `roles/logging.logWriter` ของ publisher, ปิด API Workflows ถ้าไม่มี workflow อื่น)
· `--cleanup-old` ไม่รันเป็นค่าเริ่มต้น · ตัวส่งเดิมและตัวใหม่ใช้ `claimed_at` ร่วมกัน

---

## ส่วน B — ต่อทีมที่มาใช้ข้อมูล (ทำซ้ำทุกครั้งที่มีทีมใหม่)

ทุกทีม **pull** จาก subscription ของตัวเอง · subscription, dead letter และไฟล์โหลดครั้งแรก
อยู่ใน `databuffet-nonprd` ใช้ IAM แยกสิทธิ์ของแต่ละทีม · มี 2 วิธี ต่างกันแค่
**identity ที่ใช้ pull** (เรียกรวมว่า "SA ของทีม" ด้านล่าง) — subscription, dead letter, ไฟล์โหลดครั้งแรก
และสิทธิ์ที่ให้ เหมือนกันทุกอย่าง:

| วิธี | ใช้เมื่อ | SA ของทีม | Key |
|---|---|---|---|
| **Key** (ค่าเริ่มต้น) | backend ของทีมรัน **นอก GCP** หรือรันใน GCP project ที่ **ไม่อยู่ใน organization ของเรา** | `sa-pull-<ทีม>` ที่สคริปต์สร้างใน `databuffet-nonprd` | JSON key สร้างด้วยมือแล้วส่งให้ทีม (ขั้น 2) |
| **SA ของทีมเอง** (`--team-sa <email>`) | backend ของทีมรันใน GCP project **ใน organization ของเรา** | runtime service account ของทีม (ทีมแจ้ง email มา) — เราไม่สร้าง SA | ไม่มี key — ข้ามขั้น 2 |

project นี้บังคับ domain-restricted sharing (`constraints/iam.allowedPolicyMemberDomains` ยอมเฉพาะ
customer ID ของ organization เรา) จึงให้สิทธิ์ SA ของ project นอก organization ไม่ได้ — ทีมแบบนั้น
ใช้วิธี key

### 1. รัน `add-consumer.sh`

**ทำ**: ใส่ชื่อทีม (รวม environment ในชื่อ เช่น `ai-dev`) และ topic ทุกชุดที่ทีมได้รับจาก
[export config](../../includes/controller/mart-export-config.json)

```bash
# วิธี key
bash pubsub/scripts/add-consumer.sh ai-dev export-ta-dim_company
# วิธี SA ของทีมเอง — ใส่ email ของ runtime service account ที่ทีมแจ้งมา
bash pubsub/scripts/add-consumer.sh --team-sa consumer-run@ai-prod.iam.gserviceaccount.com ai-prod export-ta-dim_company
```

`--team-sa` รับเฉพาะ email ของ service account (`<ชื่อ>@<project>.iam.gserviceaccount.com`,
`<เลข>-compute@developer.gserviceaccount.com` หรือ `<project>@appspot.gserviceaccount.com`) ·
ให้สิทธิ์ per-team (folder ไฟล์โหลดครั้งแรก) ก่อนสร้าง subscription ใดๆ ถ้า IAM ปฏิเสธเพราะ
domain-restricted sharing สคริปต์หยุดทันที บอกสาเหตุ และให้รันใหม่แบบไม่ใส่ `--team-sa`
(วิธี key) · ทีมหนึ่งใช้วิธีเดียว — ถ้าเปลี่ยนวิธี ให้ถอนสิทธิ์ของ SA เดิมออกเอง

ชื่อทีมใช้ได้เฉพาะตัวพิมพ์เล็ก ตัวเลข และ `-` (ขึ้นต้นและลงท้ายด้วยตัวอักษรหรือตัวเลข)
ยาวไม่เกิน 22 ตัว เพราะ `sa-pull-<ทีม>` ต้องไม่เกิน 30 ตัว · สคริปต์หยุดถ้า topic หรือ
`<topic>-dead-letter` ยังไม่มี (รัน `setup.sh` ก่อน) · รันซ้ำได้ — apply ค่าเดิมซ้ำ หรือเพิ่ม
topic ให้ทีมเดิม · พิมพ์ทุกอย่างที่สร้าง และ **ไม่สร้าง key** ทั้งสองวิธี

สิ่งที่สร้าง:

| Resource | ชื่อ | ค่าที่ตั้ง | สิทธิ์ |
|---|---|---|---|
| Service account (1 ต่อทีม, **วิธี key เท่านั้น**) | `sa-pull-<ทีม>` | ไม่มี key, ไม่มี role ระดับ project | — |
| Pull subscription (1 ต่อ topic) | `sub.<ทีม>.<topic>` เช่น `sub.ai-dev.export-ta-dim_company` | ack deadline 60 วินาที · เก็บข้อความ 7 วัน **รวมข้อความที่ ack แล้ว** · ไม่หมดอายุ · retry 10–600 วินาที · ส่งไม่สำเร็จครบ 5 ครั้ง → `<topic>-dead-letter` | `roles/pubsub.subscriber` ให้ SA ของทีม และ Pub/Sub service agent บน subscription นี้เท่านั้น |
| Dead-letter hold (1 ต่อ topic) | `dlq.<ทีม>.<topic>` บน `<topic>-dead-letter` | เก็บ 31 วัน · ไม่หมดอายุ · filter `attributes.CloudPubSubDeadLetterSourceSubscription = "sub.<ทีม>.<topic>"` | ไม่ให้ทีม — เราอ่านเองเท่านั้น |
| สิทธิ์อ่านไฟล์โหลดครั้งแรก (1 ต่อทีม) | folder `gs://databuffet-nonprd-datamart-snapshot/<ทีม>/` | — | `datamartSnapshotGet` เมื่อชื่อ object ขึ้นต้นด้วย `<ทีม>/` (IAM Condition บน bucket) ให้ SA ของทีม — ดาวน์โหลด manifest และไฟล์ตามชื่อที่ระบุเท่านั้น |

Pub/Sub service agent มี `roles/pubsub.publisher` บน `<topic>-dead-letter` — `setup.sh` เป็นผู้ให้สิทธิ์นี้ (ส่วน A ขั้น 4) สคริปต์นี้ไม่ให้ซ้ำ

**ทำไม**: SA แยกต่อทีม ปิดทีมใดทีมหนึ่งได้ไม่กระทบทีมอื่น · สคริปต์ให้สิทธิ์ SA ของทีมเองชุดเดียวกับ
`sa-pull-<ทีม>` พอดี ไม่มากกว่า — ไม่ให้ role ระดับ project ใน `databuffet-nonprd` · วิธี SA ของทีมเอง
ไม่มี key ให้หลุดหรือต้องส่ง · สิทธิ์ pull ให้ที่ **subscription
ของทีมเท่านั้น** ไม่ให้ระดับ project เพราะ role Pub/Sub ระดับ project จะ pull subscription ของ
ทีมอื่นได้ด้วย · subscription คือ "ตัวชี้ว่าส่งถึงไหน" ส่วนตัวของแต่ละทีม ทีมนี้ดึงช้าไม่กระทบ
ทีมอื่นบน topic เดียวกัน · เก็บข้อความที่ ack แล้ว 7 วัน เพื่อ replay หลังเกิดเหตุได้ (ดู "Replay")
· ข้อความที่ทีมรับไม่สำเร็จ 5 ครั้งไปพักที่ `dlq.<ทีม>.<topic>` แทนการวนส่งไม่จบ —
`dlq` สร้างก่อน subscription เสมอ dead letter จึงไม่หายเพราะไม่มีที่รับ

### 2. สร้าง JSON key ด้วยมือ แล้วส่งให้ทีม (วิธี key เท่านั้น)

วิธี SA ของทีมเองข้ามขั้นนี้ — backend ของทีมใช้ credentials ของ runtime service account ของตัวเอง
(Application Default Credentials) ในโค้ด consumer และโหลดไฟล์ได้เลย

**ทำ**: project owner สร้าง key ใช้งานทีละหนึ่งอันต่อทีม และ rotate ทุก 90 วัน (ดูด้านล่าง) เขียนไฟล์ไว้ **นอก repo**:

```bash
gcloud iam service-accounts keys create "$HOME/sa-pull-ai-dev.json" --iam-account=sa-pull-ai-dev@databuffet-nonprd.iam.gserviceaccount.com --project=databuffet-nonprd
```

ส่งไฟล์ให้ทีมเป็น zip ใส่รหัสผ่าน ผ่านช่องทางที่ปลอดภัย (ไม่แปะในแชทหรืออีเมลแบบเปิด) แล้วลบไฟล์ในเครื่อง ·
ห้าม commit key เข้า repo

**Rotate ทุก 90 วัน** (ทำด้วยมือ): สร้าง key ใหม่นอก repo ด้วยคำสั่งเดิม (ตั้งชื่อไฟล์ใหม่ เช่น
`$HOME/sa-pull-ai-dev-<YYYYMMDD>.json`) แล้วส่งให้ทีมทางเดิม (zip ใส่รหัสผ่าน) และลบไฟล์ในเครื่อง ·
key เก่ายังใช้ได้อีก 14 วัน ทีมต้องเปลี่ยนไฟล์ key และ restart consumer ภายใน 14 วันนั้น ·
ครบ 14 วันแล้ว หา id ของ key เก่าแล้วลบ โดยแทน `OLD_KEY_ID` ด้วย id ของ key เก่าจากผล `keys list`:

```bash
gcloud iam service-accounts keys list --iam-account=sa-pull-ai-dev@databuffet-nonprd.iam.gserviceaccount.com --managed-by=user --project=databuffet-nonprd
gcloud iam service-accounts keys delete OLD_KEY_ID --iam-account=sa-pull-ai-dev@databuffet-nonprd.iam.gserviceaccount.com --project=databuffet-nonprd
```

ถ้าลูกค้าตกลงขอไม่ rotate ก็ข้ามได้ — ลูกค้าดูแลและรับผิดชอบ key เอง

**ทำไม**: backend ของทีมอาจรันบน platform ไหนก็ได้ จึงใช้ key แทน identity ของ GCP · key
ไม่หมดอายุเอง เราจึง rotate ทุก 90 วัน (เหลื่อม 14 วันให้ทีมสลับ key ได้โดยไม่สะดุด) เพื่อจำกัดอายุของ key ที่อาจหลุด · การสร้างและส่ง key ทำด้วยมือเท่านั้น สคริปต์ไม่สร้างหรือพิมพ์ key ·
key นี้ทำได้แค่ pull จาก `sub.<ทีม>.*` และอ่านไฟล์ใน folder `<ทีม>/` ของทีมเอง ถ้าหลุดก็ไม่ถึง
ข้อมูลอื่น · ถ้าต้องตัดทีม ลบ **ทุก** key ที่ `keys list --managed-by=user` แสดง (ช่วงเหลื่อม 14 วันมี key สองอัน) ด้วย `keys delete` — ลบแค่
subscription ของทีม ทีมยังอ่านไฟล์ใน folder ของทีมได้

### 3. โหลดครั้งแรกด้วยไฟล์ (ครั้งแรกที่ทีมต่อ topic นั้นเท่านั้น)

**ทำจาก Google Cloud Shell เท่านั้น** (GCP-hosted): clone repo และ checkout commit ที่ merge
และ deploy ถึง `nonprod` แล้วใน Cloud Shell จากนั้น cd เข้า repo · สคริปต์ปฏิเสธถ้า
`CLOUD_SHELL` ไม่ใช่ `true` ห้ามรันจาก WSL/workstation · หลังขั้น 1 (subscription ของทีมต้องมีอยู่แล้ว — สคริปต์ไม่ยอมรันถ้ายังไม่มี) export
ทุกแถวปัจจุบันของ export view ของ topic นั้นลง folder ของทีม ทีละ topic:

```bash
bash pubsub/scripts/export-snapshot.sh ai-dev export-ta-dim_company
```

สคริปต์พิมพ์ folder และ **export time** (UTC) แล้วส่งทั้งสองค่าให้ทีม · ใช้ path ของ folder
ตามที่สคริปต์พิมพ์ ซึ่งลงท้ายด้วยเวลาแบบ `YYYYMMDDTHHMMSSffffffZ` (microseconds 6 หลัก)
ส่วน `export_time` ใน manifest เป็น RFC3339 · ใน folder มี:

- `<YYYY>/<MM>/<DD>/data-<เลข>.json` — แบ่ง folder ตาม **วันที่ของเอกสาร** ของแถว (คอลัมน์ใน
  `snapshot_date` ของตารางนั้นใน export config เช่น `Order_Date` ของ `order`) · ตารางที่ไม่มี
  `snapshot_date` (master เช่น `stk`, `company`, `dim_company`) อยู่ใต้วันที่ export (Asia/Bangkok)
  folder เดียว · ไฟล์ละไม่เกิน 100,000 บรรทัด — newline-delimited JSON หนึ่งบรรทัดต่อแถว
  แต่ละบรรทัด **ตรงทุก byte** กับข้อความที่ publisher publish ให้แถวนั้นเป็น `NEW` (สร้างจาก diff
  query ตัวเดียวกัน `pubsub/sql/diff.sql`) ทีมจึงโหลดด้วยโค้ดเดียวกับ consumer
- `manifest.json` — `table`, `topic`, `team`, `export_time`, `row_count`, `files` · เขียนเป็นไฟล์
  สุดท้ายหลัง seek สำเร็จและรอ 90 วินาทีแล้ว folder ที่ไม่มี manifest คือ export ที่ไม่เสร็จ
  ห้ามโหลดหรือเริ่ม pull

สคริปต์อ่าน `seeded_at` ก่อนเขียนใด ๆ ถ้าอ่านไม่สำเร็จจะหยุด · จากนั้น claim แถวของตารางนั้น
ใน `mart_export_config` เมื่อ `claimed_at` ว่างเท่านั้น ถ้ามี claim อยู่สคริปต์จะหยุด
สำหรับตารางที่ seed แล้วให้รอ publisher คืน claim; ตารางที่ยังไม่ seed และมี claim ค้างจากการ
หยุดกะทันหันต้องให้ operator ตรวจว่าไม่มี exporter รันอยู่และคืน claim ด้วยมือก่อนลองใหม่
สคริปต์ไม่ยึด claim ที่หมดอายุ · จากนั้นอ่าน export view ลงตาราง
ชั่วคราว · ถ้า `seeded_at` เป็น NULL จะ ASSERT ว่ายังไม่ seed และยังถือ claim ของตัวเอง
พร้อม ASSERT ว่ายังไม่มี sent state แล้ว INSERT ทุกแถวจาก snapshot
เป็น `seed` และตั้ง `seeded_at = export_time`, `last_invocation_id = 'seed'`, `last_invocation_end = export_time`
ใน transaction เดียวกันก่อนเทียบ `row_key`/`row_hash` กับ `mart_sent_state` ใน transaction เดียวกัน
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
เพื่อ export/นับแถว · ไฟล์ผ่าน Cloud Shell ภายใน GCP หนึ่งรอบเพื่อแปลงจาก CSV เป็นบรรทัดข้อความและแยก
folder ตามวันที่ (ต้องมีพื้นที่ว่างในเครื่องเท่าขนาดชุดนั้น เช่น `order` ~0.7 GB) ·
สคริปต์พยายามคืน claim เป็น NULL ด้วย token ของตัวเองเมื่อจบ รวมกรณีล้มเหลว · ถ้า seed ยังไม่ commit
`seeded_at` ยังคง NULL ทำให้ publisher ข้ามตาราง แม้ Cloud Shell หยุดกะทันหันหรือ claim หมดอายุ
ตารางที่ seed แล้วอ่าน sent state
อย่างเดียวและไม่เปลี่ยน `last_invocation_*` · ไม่เปลี่ยน publisher
และไม่ส่งอะไรเข้า Pub/Sub — ห้ามล้าง sent state ที่ใช้ร่วมกันเพื่อเริ่มต้นให้ทีมใหม่

ถ้าเขียน manifest สำเร็จแล้วแต่คืน claim ไม่สำเร็จ สคริปต์แจ้งว่า export สำเร็จและจบด้วย exit 0
ไฟล์พร้อมใช้งานตามเดิม ส่วน claim หมดอายุเองหลัง 35 นาที (claim ของ publisher; สคริปต์นี้ assert ที่ 30 นาที จึงล้มก่อนที่ publisher จะแย่ง claim ได้) ·
ไม่ต้องรัน export ซ้ำเพื่อคืน claim เพราะจะ seek subscription ไปที่ cut ใหม่

ฝั่งทีม ตามลำดับนี้:

1. รอให้ `manifest.json` มีอยู่ก่อน แล้วดาวน์โหลดทุกไฟล์ใน `files` ด้วย identity เดียวกับที่ใช้ pull ส่งทุกบรรทัดเข้า
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
ไฟล์ใน GCS รองรับตารางทุกขนาด (เช่น `sales_daily` ~1.65 ล้านแถว) และใช้ identity เดิม ·
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

1. วิธี key: JSON key จากขั้น 2 — **เป็น secret** ส่งผ่านช่องทางที่ปลอดภัยเท่านั้น ·
   วิธี SA ของทีมเอง: ยืนยัน email ของ SA ที่ได้สิทธิ์ (ไม่มี secret ให้ส่ง)
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

KEY_FILE = "/secure/path/sa-pull-ai-dev.json"   # วิธี key: key จาก handover — ห้าม commit
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
# วิธี SA ของทีมเอง: ไม่มี KEY_FILE — ใช้ credentials = None (Application Default Credentials
# ของ runtime service account) ทั้งที่นี่และใน storage.Client ของขั้น 3
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

## ส่วน C — ชุด commission ของทีม TF

เพิ่ม 2026-11-02 · บริษัท `ag01` · เอกสารปี 2026 + master ทั้งหมด · คอลัมน์ ชื่อ ลำดับ และชนิดข้อมูล
ตามตัวอย่าง `commission_tf_ag01_2026` ที่ส่งทีม TF เมื่อ 14 ต.ค. 2026 · แต่ละชุดส่ง **หลังรอบ
`daily_process` (06:00 น.) ที่สำเร็จ** (`trigger_scheduler`) — รอบที่ล้มเหลวหรือการรันมือไม่นับ ชุดนั้นรอ
`daily_process` รอบถัดไปที่สำเร็จ แล้วส่งการเปลี่ยนทั้งหมดในครั้งเดียว · ข้อมูลตั้งต้นเป็นไฟล์ JSON ใน GCS
แยก folder ตามวันที่ ทีม TF ดึงเข้าเอง ไม่ส่งออกนอก GCP

รายชื่อชุด, natural key (รวมคอลัมน์ที่มีค่า NULL ได้), ต้นทาง และวันที่แบ่ง folder อยู่ใน
[process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) ·
รายละเอียด schema และจำนวนแถวที่บันทึกไว้ของแต่ละชุดอยู่ใน
[OKF export cards](../okf/view/pub_sub/index.md)

### C(a). ทำได้หลัง PR merge และ code ถึง `nonprod` (project owner, จาก WSL) — ชื่อทีมที่เสนอ `tf-prd`
(SA `sa-pull-tf-prd`) · วิธี key (SA ฝั่งเรา) จึง **ไม่ใส่ `--team-sa`**:

1. รัน tag `pub_sub` ตาม [ขั้น deploy](../project_wiki/cdc-process/process.md#deploy) — สร้าง 12 view,
   และเพิ่ม 12 แถว config ที่ `seeded_at` เป็น NULL โดยยังไม่ seed หรือเขียนไฟล์ ·
   การสร้างตาราง config และ backfill ดู [config reference](../okf/process/mart_export_config.md#how-it-is-built)
   `setup.sh` ตรวจว่ามีคอลัมน์ `task_group`, `group_claimed_at`, `recovery_started_at`, `recovery_until` และมี `task_group` ครบทุกแถวและหยุดถ้ายังไม่ได้รัน tag `pub_sub`
2. `bash pubsub/scripts/setup.sh` — สร้าง 12 topic + dead-letter topic + record subscription, ให้สิทธิ์ publisher อ่าน 12 view
   (authorized view บน `validated_mac5` และ `dimension_table`) และ deploy job ตรวจ/job ส่งที่รู้จัก `trigger_scheduler`
3. ```bash
   bash pubsub/scripts/add-consumer.sh tf-prd export-commission-order export-commission-invoice export-commission-credit_note export-commission-debit_note export-commission-receipt export-commission-chqri export-commission-status export-commission-company export-commission-sell export-commission-warehouse export-commission-stk export-commission-company_source
   ```
4. สร้าง key ด้วยมือนอก repo แล้วส่งเป็น zip ใส่รหัสผ่าน (ส่วน B ขั้น 2):
   `gcloud iam service-accounts keys create "$HOME/sa-pull-tf-prd.json" --iam-account=sa-pull-tf-prd@databuffet-nonprd.iam.gserviceaccount.com --project=databuffet-nonprd`
5. ตั้ง alert และส่ง handover package (ส่วน B ขั้น 4–5)

### C(b). วันโหลดครั้งแรกที่กัปตันกำหนด (ก่อน 15 พฤศจิกายน 2026)

ยังไม่ทำวันนี้และไม่ทำอัตโนมัติเมื่อ merge/deploy/setup/tag `pub_sub` · จนถึงขั้นนี้ 12 topic
จะไม่ได้รับข้อความ publisher คืน `not seeded: waiting for the first-load export` · ในวันที่กัปตันแจ้งเท่านั้น:

1. เปิด Google Cloud Shell, clone repo และ checkout commit ที่ merge/deploy แล้ว เข้า repo
2. รันทีละ topic (ส่วน B ขั้น 3) เพื่อ seed sent state และเขียนไฟล์จาก snapshot เดียวกัน:
   ```bash
   for s in order invoice credit_note debit_note receipt chqri status company sell warehouse stk company_source; do
     bash pubsub/scripts/export-snapshot.sh tf-prd "export-commission-$s" || break
   done
   ```
   ส่ง path ของ folder และ export time ของแต่ละชุดให้ TF — ไฟล์อยู่ที่
   `gs://databuffet-nonprd-datamart-snapshot/tf-prd/export-commission-<ชุด>/<export time>/<YYYY>/<MM>/<DD>/`
3. TF รอ manifest และโหลดไฟล์ครบก่อนเริ่ม pull ภายใน 7 วัน

---

## ส่วน D — ตารางองค์กรของแอป TA ให้ทีม AI

เพิ่ม 2026-11-02 · ข้อมูลองค์กรถึงทีม AI ทาง Pub/Sub อย่างเดียว (ไม่อ่าน dataset `org_center` ตรง) · 1 topic ต่อ 1 ตารางในแอป ·
คอลัมน์ตามชุดตัวอย่างองค์กรที่ส่งทีม AI 2 พ.ย. 2026 บวก `region_code` (org_units), `zone` (appointments),
`membership_company_id` (customer_ta_assignments) · ส่งหลังรอบ `daily_process` ที่สำเร็จ ·
รายชื่อชุดและ natural key อยู่ใน [process reference](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)

topic: `export-ta-org_levels`, `export-ta-org_units`, `export-ta-positions`, `export-ta-employees`,
`export-ta-memberships`, `export-ta-appointments`, `export-ta-member_links`,
`export-ta-access_exceptions`, `export-ta-customer_ta_assignments`

### D(a). หลัง PR merge และ code ถึง `nonprod`

1. รัน tag `pub_sub` ตาม [ขั้น deploy](../project_wiki/cdc-process/process.md#deploy) — สร้าง 9 view และเพิ่ม 9 แถว config
   ที่ `seeded_at` เป็น NULL (ไม่ต้องรัน `org_center_unit` ใหม่: คอลัมน์ `region_code` มีอยู่แล้ว)
2. `bash pubsub/scripts/setup.sh` — สร้าง 9 topic + dead-letter topic, ให้สิทธิ์ publisher อ่าน 9 view
   (authorized view บน dataset `org_center` และ `mds_dataset` สำหรับ `export_employees`)
3. ต่อทีม AI ด้วย `add-consumer.sh <ทีม> <topic>...` และโหลดครั้งแรกด้วย `export-snapshot.sh` ในวันที่กัปตันกำหนด
   (ส่วน B) — จนกว่าจะ seed publisher ข้ามทั้ง 9 topic

## Checklist ก่อนเปิดใช้งานจริง (หลัง merge)

- [ ] ทำตาม [ขั้น deploy ของ pilot](../project_wiki/cdc-process/process.md#deploy) รวมการตรวจ live compilation ก่อนรันด้วยมือ; การเพิ่ม เปลี่ยน หรือเอาตาราง export ออกให้ยึด lifecycle ใน process reference เดียวกัน
- [ ] รัน `pubsub/scripts/setup.sh` ตามส่วน A (A1–A3)
- [ ] ตรวจ execution และ sent state ตาม A4: ตารางที่ยังไม่ seed ถูกข้าม; pilot ที่ seed แล้วส่งเฉพาะแถวที่เปลี่ยน
- [ ] ต่อทีมใหม่: รัน `add-consumer.sh [--team-sa <email>] <ทีม> <topic>...` เฉพาะชุดที่ทีมได้รับ (ขั้น 1)
- [ ] วิธี key เท่านั้น: สร้าง JSON key ด้วยมือนอก repo แล้วส่งเป็น zip ใส่รหัสผ่านผ่านช่องทางที่ปลอดภัย และนัดรอบ rotate ทุก 90 วัน (ขั้น 2)
- [ ] ในวัน first-load ที่กัปตันกำหนด หลังมี subscription แล้ว รันจาก Cloud Shell เท่านั้น `export-snapshot.sh <ทีม> <topic>` ทีละ topic รอให้สคริปต์ seek และรอ 90 วินาทีก่อนเขียน manifest เสร็จ แล้วส่ง folder + export time ให้ทีม · ทีมรอ manifest และโหลดไฟล์ครบก่อนเริ่ม pull (ขั้น 3)
- [ ] ตั้ง alert backlog + dead letter และส่ง handover package ครบ (ขั้น 4–5)
- [ ] ชุด commission ของทีม TF: ทำตามส่วน C(a) แล้วรอกัปตันกำหนดวันทำ C(b)

---

## ส่วน E — ตารางตัวอย่างของทีม AI (33 ตาราง)

เพิ่ม 2026-11-03 · ทุกตารางที่ส่งให้ทีม AI เป็นตัวอย่างแล้ว (ชุด 26 ต.ค. 31 ตาราง, `rls_ta_customer`,
`mds_data_ta_dashboard_display_control`) · 1 topic ต่อ 1 ตาราง · คอลัมน์ = หัว CSV ของตัวอย่าง ชื่อและลำดับเดิม
อ่านจากตารางเดียวกัน ทั้งตาราง (ไม่ใช้ตัวกรองของตัวอย่าง) · เมื่อเปิดใช้งานจะส่งหลังรอบ `daily_process` ที่สำเร็จ ·
รายชื่อ view และรายละเอียด schema, key และจำนวนแถวอยู่ใน
[OKF export cards](../okf/view/pub_sub/index.md)

รายชื่อ topic อยู่ใน [`mart-export-config.json`](../../includes/controller/mart-export-config.json) ·
ข้อจำกัดด้านปริมาณการเปลี่ยนแปลงและเพดาน publisher อยู่ใน
[process reference](../project_wiki/cdc-process/process.md#ai-team-sample-tables)

### E(a). หลังทีม AI ทดสอบตัวอย่างเสร็จและอนุมัติเปิดใช้งาน

**รอบนี้ส่งมอบเฉพาะโค้ด view, config, setup และเอกสาร** · ทีม AI ทดสอบกับตัวอย่างก่อน
และอาจปรับ view ตามผลทดสอบ · การ merge ไม่ใช่คำสั่ง deploy: ยังไม่รัน Dataform หรือเปลี่ยน GCP/BigQuery,
ไม่สร้าง topic หรือ consumer และไม่ส่งข้อมูล · ขั้นตอนต่อไปนี้ใช้ภายหลังได้รับอนุมัติเปิดใช้งานเท่านั้น
และ code ถึง `nonprod` แล้ว:

1. รัน tag `pub_sub` ตาม [ขั้น deploy](../project_wiki/cdc-process/process.md#deploy) — สร้าง 33 view และเพิ่ม 33 แถว config ที่ `seeded_at` เป็น NULL
2. `bash pubsub/scripts/setup.sh` — สร้าง 33 topic + dead-letter topic, ให้สิทธิ์ publisher อ่าน 33 view
   (authorized view บนทุก dataset ในสายของ view นั้น) แล้ว dry-run `SELECT` ของแต่ละ export view ในนาม publisher
3. ต่อทีม AI ด้วย `add-consumer.sh <ทีม> <topic>...` และโหลดครั้งแรกด้วย `export-snapshot.sh` ในวันที่กัปตันกำหนด
   (ส่วน B) — จนกว่าจะ seed publisher ข้ามทุก topic
