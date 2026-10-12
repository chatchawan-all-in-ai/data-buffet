# How-to: Setup Pub/Sub สำหรับส่งออกข้อมูลจาก BigQuery

> สถานะ: **ใช้งานจริง** (ไม่ใช่ POC ทิ้ง) — scope แรก = query commission ของคุณแป้ง
> (8 ไฟล์ T-SQL → **14 ชุดข้อมูล**) ส่งให้ **ทีม TF** รายละเอียดแต่ละส่วนจะถูกปรับเพิ่ม
> ทีหลังตามที่ผู้ใช้เห็นเหมาะสม
> เอกสารนี้อยู่นอก pipeline หลักของ Dataform (ไม่แก้ `definitions/`, `includes/`,
> `workflow_settings.yaml`) — เป็น GCP infra แยกสำหรับส่งข้อมูลออกไปให้ระบบ/ทีมอื่นใช้

## ภาพรวม

ทุกเช้า 07:00 หลัง Dataform nightly run (06:00) เสร็จ ระบบจะดึง **เฉพาะแถวที่เปลี่ยน** จากตาราง
export ทีละชุด แล้ว publish เข้า **topic ของชุดนั้น (1 query = 1 topic)** ทีมที่จะมาใช้
ข้อมูล — ไม่ว่าอยู่ในบริษัทหรือนอกบริษัท — **รับข้อมูลแบบ push เหมือนกันหมด**:
Pub/Sub ยิงทีละข้อความ (HTTPS POST) ไปที่ **endpoint ของทีมนั้นเอง** พร้อม OIDC token
ที่ออกโดย service account ภายใน project เรา — **ไม่มี service account key ออกไปนอก
project เลย** ทีมปลายทางไม่ต้องมีบัญชีหรือสิทธิ์อะไรใน `databuffet-nonprd`

```
Dataform nightly run (06:00 เสร็จราว 06:08)
        │
        ▼
Cloud Scheduler (07:00 ทุกเช้า)
        │  HTTP + OIDC (default compute SA ต้องมี Cloud Run Invoker)
        ▼
Cloud Function export_daily ── วนทีละชุด: query ตาราง export (update_on > watermark) ──▶ publish
        │
        ├──▶ export-commission-order    ──▶ sub-tf-order (push)    ─┐
        ├──▶ export-commission-invoice  ──▶ sub-tf-invoice (push)  ─┤   HTTPS POST + OIDC token
        ├──▶ ...                        ──▶ ...                    ─┼──▶ ของ sa-push-tf ──▶ endpoint ของ TF
        └──▶ export-commission-fob      ──▶ sub-tf-fob (push)      ─┘   (ตรวจ token → upsert/delete
            (14 topic)                      (14 sub ต่อ 1 ทีม)            → ตอบ 204) ──▶ ตารางปลายทางของ TF
```

**จำนวน resource**: ส่วนกลาง (ทำครั้งเดียว) = topic 14 + Cloud Function 1 + Scheduler
job 1 (ใช้ default compute SA ไม่สร้าง SA ใหม่) · ต่อ 1 ทีม = push subscription ตามจำนวน
ชุดที่ได้รับ (TF = 14) + push service account ภายใน 1 ตัว (`sa-push-<ทีม>`, ไม่มี key)
+ alert policy 1

**สิ่งที่เอกสารนี้ไม่ครอบคลุม** (ผู้ใช้ออกแบบเอง): logic การหา "แถวไหนเปลี่ยน" (query/table/view
export + column `update_on` + flag สถานะ) — เอกสารนี้ครอบคลุมแค่ตัว Pub/Sub infra
กับวิธีที่ทีมต่างๆ รับข้อมูลออกไปใช้

### ผู้รับผิดชอบ

| ส่วน | ผู้รับผิดชอบ |
|---|---|
| query ต้นฉบับ 8 ไฟล์ (spec ของแต่ละชุดข้อมูล) | คุณแป้ง |
| port T-SQL เป็นตาราง export บน BigQuery (+ `update_on`, flag) | Data Mart |
| topic 14 อัน, Cloud Function, Cloud Scheduler, watermark | Data Mart |
| push subscription ของ TF 14 อัน + push service account ภายใน (`sa-push-tf`) + สิทธิ์ | Data Mart |
| ตัวอย่างโค้ด endpoint รับ push | Data Mart เขียน แล้วส่งให้ TF |
| endpoint HTTPS (รัน + ดูแล), ตรวจ token, ดูแลตารางปลายทาง | ทีม TF |

### รายชื่อ topic (1 query = 1 topic)

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

**ทำไม 1 query = 1 topic** (ไม่รวมเป็น topic เดียว): ดูแลแยกกันได้ — replay/seek
ย้อนเฉพาะชุดที่พัง, ให้สิทธิ์ทีละชุดได้ถ้าวันหน้ามีทีมที่ห้ามเห็นบางชุด, ชุดใหญ่ (order)
ค้างไม่ถ่วงชุดเล็ก, ผูก schema ต่อ topic ได้ แลกกับจำนวน resource ที่ต้องสร้างมากขึ้น

**กฎของ Pub/Sub ที่ต้องรู้** (ต่างจาก Kafka/RabbitMQ):
- 1 subscription ผูกได้ **1 topic เท่านั้น** (ผูกตอนสร้าง เปลี่ยนทีหลังไม่ได้)
- 1 topic มีได้ **หลาย subscription** — ทีมละ 1 อัน ทุกทีมได้ข้อความครบของตัวเอง
- ชื่อ subscription **ห้ามซ้ำทั้ง project** — ตั้ง `sub-tf` ซ้ำ 14 topic ไม่ได้ จึงใช้
  `sub-<ทีม>-<ชุด>`
- แบบ push: Pub/Sub เป็นฝ่ายเรียก endpoint ของทีม — ดูรหัสตอบกลับที่ใช้ ack ใน
  [รูปแบบ push body](#รูปแบบ-push-body-สิ่งที่-endpoint-ได้รับ) ด้านล่าง ทีมไม่ต้องเข้ามาดึง
  และไม่ต้องมีสิทธิ์ใน project เรา; endpoint รู้ว่าข้อความมาจากเราจริงด้วยการตรวจ
  OIDC token ที่ Pub/Sub แนบมา (ออกในนาม `sa-push-<ทีม>` ของเรา)

## Message format (มาตรฐานเดียว ทุก topic ทุกทีมใช้ร่วมกัน)

```json
{
  "table": "order",
  "run_date": "2026-10-12",
  "operation": "NEW",
  "primary_key": { "company_id": "ag01", "Order_No": "SO2610-0042", "No": 1 },
  "data": { "...": "แถวข้อมูลเต็ม ชื่อคอลัมน์ตาม query ต้นฉบับ" }
}
```

| field | ค่า | หมายเหตุ |
|---|---|---|
| `table` | ชื่อชุดข้อมูล | ตรงกับชื่อท้าย topic (`order`, `stk`, ...) — เก็บไว้ให้ consumer ใช้ callback ตัวเดียวได้ |
| `run_date` | วันที่ export | ใช้ debug/ตรวจสอบ ไม่ใช่ key |
| `operation` | `NEW` \| `UPDATE` \| `DELETE` | ปลายทางใช้ตัดสินว่าจะ upsert หรือ delete |
| `primary_key` | object ของ key column | key ของแต่ละชุดกำหนดตอน port query |
| `data` | แถวข้อมูลเต็ม | มีเฉพาะ `NEW`/`UPDATE`; `DELETE` = `null` (แถวไม่มีแล้วที่ต้นทาง) |

⚠️ **ข้อควรระวังตอนออกแบบ query ฝั่ง publish (ยังไม่ทำในเอกสารนี้ แต่ต้องรู้ไว้)**:
query ต้อง drive จากตาราง CDC/flag เป็นหลัก ไม่ใช่ join ออกจากตาราง `mil`/`mih` ตรงๆ
เพราะแถวที่ถูก `DELETE` จะไม่มีอยู่ใน `mil`/`mih` แล้ว ถ้า join แบบ inner จะได้ 0 แถว
และ `DELETE` นั้นจะไม่ถูกส่งไป Pub/Sub เลย

⚠️ **ทีมใหม่ที่ต่อครั้งแรก**: เพราะ export เป็น **delta อย่างเดียว** (ไม่ใช่ full dump
ทุกวัน) ทีมใหม่จะได้แค่ข้อมูลที่เปลี่ยนตั้งแต่วันที่เขาต่อ subscription เท่านั้น **ต้องรัน
export แบบไม่กรอง `update_on` (เอาทั้งหมดตั้งแต่แรกจนปัจจุบัน) ให้ 1 รอบ** ก่อนเข้าโหมด
delta ปกติ (ขั้น 14)

## Prerequisites

- สิทธิ์ Owner/Editor บน project `databuffet-nonprd` (หรือสิทธิ์สร้าง Pub/Sub, IAM,
  Cloud Functions, Cloud Scheduler อย่างน้อย)
- ตาราง/view export ทั้ง 14 ชุดที่มี column `update_on` + flag สถานะ
  (`NEW`/`UPDATE`/`DELETE`) — เตรียมแยกจากเอกสารนี้
- control table เก็บ watermark (`last_exported_at`) **แยกต่อชุด** — เตรียมแยกจากเอกสารนี้

---

## ส่วน A — Setup Pub/Sub infra (ทำครั้งเดียว)

ทำผ่านหน้า [console.cloud.google.com](https://console.cloud.google.com) ทั้งหมด
เลือก project **databuffet-nonprd** ที่มุมบนซ้ายก่อนเริ่ม

### 1. เปิด API ที่ต้องใช้

**ทำ**: เมนู ☰ → **APIs & Services → Library** → ค้นหาแล้วกด **Enable** ทีละตัว:
`Cloud Pub/Sub API`, `Cloud Functions API`, `Cloud Scheduler API`, `Cloud Run API`

**ทำไม**: GCP ปิด service เหล่านี้ไว้เป็น default ต่อ project ถ้าไม่เปิดก่อน ขั้นตอน
หลังจะสร้าง resource ไม่ได้เลย

### 2. สร้าง Pub/Sub topic 14 อัน

**ทำ**: เมนู ☰ → **Pub/Sub → Topics → CREATE TOPIC** ทำซ้ำ 14 รอบ ตามตาราง
"รายชื่อ topic" ด้านบน
- Topic ID: `export-commission-<ชุด>` (เช่น `export-commission-order`)
- **เอาติ๊ก "Add a default subscription" ออก** → ปล่อย default อื่นไว้ → **CREATE**

**ทำไม**: topic คือ "ท่อ" ของแต่ละชุดข้อมูล — 1 query = 1 ท่อ เพื่อให้ดูแล/replay/
ให้สิทธิ์แยกกันได้ ต้องเอา default subscription ออก ไม่งั้นได้ sub ชื่อ `<topic>-sub`
ที่ไม่มีใครใช้ติดมา 14 อัน (มีข้อความค้างสะสมโดยไม่มีคนดึง)

### 3. ทดสอบว่า topic ใช้งานได้ก่อนไปต่อ

**ทำ** (ทดสอบกับ topic เดียวพอ — `export-commission-order`):
1. ในหน้า topic → **CREATE SUBSCRIPTION** → ID: `sub-test-poc` → Delivery type:
   **Pull** → **CREATE**
2. กลับหน้า topic → tab **MESSAGES → PUBLISH MESSAGE** → พิมพ์ข้อความทดสอบ (เช่น
   `{"table":"order","operation":"NEW"}`) → **PUBLISH**
3. ไปหน้า `sub-test-poc` → tab **MESSAGES → PULL** (ติ๊ก "Enable ack messages") →
   **PULL** → ต้องเห็นข้อความที่ publish ไปกลับมา

**ทำไม**: เช็คว่า "ท่อ" ทำงานถูกต้องก่อนไปเสียเวลาตั้ง Cloud Function — ถ้าขั้นนี้
ผ่าน ปัญหาที่เจอทีหลัง (ถ้ามี) มาจาก Cloud Function/Scheduler แน่นอน ไม่ใช่จาก
Pub/Sub เอง

### 4. ระบุ default service account ที่จะใช้ (ไม่ต้องสร้างใหม่)

**ทำ**: เมนู ☰ → **IAM & Admin → Service Accounts** → หา service account ชื่อ
`PROJECT_NUMBER-compute@developer.gserviceaccount.com` (Compute Engine default
service account) — จดชื่อเต็มไว้ใช้ในขั้นต่อไป

**ทำไม**: ตัดสินใจให้ service ภายใน GCP ที่คุยกันเอง (Cloud Scheduler → Cloud
Function → BigQuery/Pub-Sub) **ใช้ default service account ร่วมกัน** ไม่สร้าง
custom SA แยก เพื่อลดขั้นตอน setup — ต่างจาก push service account ในส่วน B ที่ยังคง
**แยกต่อทีมเสมอ** (endpoint ของแต่ละทีมใช้อีเมล SA นี้ยืนยันว่าข้อความมาถึงตัวเองจริง)

### 5. ให้สิทธิ์ default service account

**ทำ**:
- **IAM & Admin → IAM → GRANT ACCESS** → principal = default compute service account
  จากขั้น 4 → เพิ่ม 2 role ระดับ project: **Pub/Sub Publisher** และ **BigQuery Job
  User** → **SAVE**
- BigQuery → dataset `validated_mac5` และ dataset ที่เก็บตาราง export → **SHARING →
  Permissions → ADD PRINCIPAL** → principal เดิม → Role: **BigQuery Data Viewer**
- BigQuery → dataset ที่เก็บ control table watermark → Role: **BigQuery Data Editor**

**ทำไม**: default service account ของ project ใหม่ **ไม่ได้ Editor กว้างอัตโนมัติแล้ว**
(Google เปลี่ยนพฤติกรรม default นี้ไปแล้ว) ต้องเพิ่มเอง — Publisher ให้ระดับ project
ครั้งเดียวแทนที่จะให้ทีละ topic 14 ครั้ง (SA นี้เป็นของภายใน Data Mart อยู่แล้ว),
Job User เพื่อให้รัน query ได้, Data Viewer เพื่ออ่านตาราง, Data Editor เพื่อเขียน
watermark ขาดตัวไหน Cloud Function จะ permission denied — สิทธิ์ **Cloud Run Invoker**
ให้ทำในขั้น 7 เพราะต้อง deploy function ก่อนถึงจะมี service ให้ผูกสิทธิ์

### 6. Deploy Cloud Function

**ทำ**: เมนู ☰ → **Cloud Functions → CREATE FUNCTION**
- Environment: **2nd gen**
- Function name: `databuffet-export-publisher`, Region: `us-central1`
- Trigger type: **HTTPS**, ติ๊ก **Require authentication**
- **Runtime, build, connections and security settings** → Timeout: **1800** วินาที,
  Memory: **1 GiB** → **NEXT**
- Runtime: **Python 3.12**, Entry point: `export_daily`
- Runtime service account: ปล่อยเป็นค่า default — จะใช้ default compute service
  account จากขั้น 4 อัตโนมัติ ไม่ต้องเลือกเอง
- วางโค้ดด้านล่างในตัวแก้ไข inline → **DEPLOY**

**ทำไม**: นี่คือตัว "คนงาน" ตัวเดียวที่วนทีละชุด ดึงแถวที่เปลี่ยนจาก BigQuery แปลงเป็น
message แล้วส่งเข้า topic ของชุดนั้น — timeout default 60 วินาทีไม่พอสำหรับ 14 ชุด
(ครั้ง backfill ยิ่งนาน) จึงต้องขยาย

**ตัวอย่างโค้ด** — วางเป็น 2 ไฟล์ในตัวแก้ไข inline (`requirements.txt` + `main.py`):

```
# requirements.txt
google-cloud-bigquery
google-cloud-pubsub
functions-framework
```

```python
# main.py
import json
from google.cloud import bigquery, pubsub_v1
import functions_framework

PROJECT_ID = "databuffet-nonprd"

# 1 ชุด = 1 topic: ตาราง export ใน BigQuery + primary key (key จริงกำหนดตอน port query)
EXPORTS = {
    "order": {"source": "<export_dataset>.order", "pk": ["company_id", "Order_No", "No"]},
    "stk":   {"source": "<export_dataset>.stk",   "pk": ["company_id", "stkcode"]},
    # ... ใส่ให้ครบ 14 ชุด ตามตาราง "รายชื่อ topic"
}

bq_client = bigquery.Client()
publisher = pubsub_v1.PublisherClient()


@functions_framework.http
def export_daily(request):
    published, failed = {}, []
    for name, cfg in EXPORTS.items():
        try:
            published[name] = export_one(name, cfg)
        except Exception as e:               # ชุดหนึ่งพัง ชุดอื่นยังส่งต่อได้
            failed.append(name)
            print(f"export {name} failed: {e}")
    if failed:
        return f"failed {failed}, published {published}", 500
    return f"published {published}", 200


def export_one(name, cfg):
    topic_path = publisher.topic_path(PROJECT_ID, f"export-commission-{name}")

    # 1) อ่าน watermark ล่าสุดของชุดนี้ จาก control table ของคุณ
    last_exported_at = get_last_watermark(name)

    # 2) ดึงเฉพาะแถวที่เปลี่ยน — WHERE/flag column เป็นของคุณ ใส่ตัวอย่างไว้
    query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{cfg['source']}`
        WHERE update_on > @last_exported_at
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter(
            "last_exported_at", "TIMESTAMP", last_exported_at)]
    )
    rows = bq_client.query(query, job_config=job_config).result()

    # 3) แปลงเป็น message ตาม format ที่ตกลงกัน แล้ว publish
    futures = []
    latest_seen = last_exported_at
    for row in rows:
        envelope = {
            "table": name,
            "run_date": str(row["update_on"].date()),
            "operation": row["record_status"],       # "NEW"/"UPDATE"/"DELETE" จากตารางคุณ
            "primary_key": {k: row[k] for k in cfg["pk"]},
            "data": None if row["record_status"] == "DELETE" else dict(row.items()),
        }
        futures.append(publisher.publish(
            topic_path, json.dumps(envelope, default=str).encode("utf-8")))
        latest_seen = max(latest_seen, row["update_on"])

    # 4) รอให้ publish จบจริงก่อนไปต่อ — ไม่รอจะเสี่ยงข้อความหาย
    for f in futures:
        f.result()   # จะ raise ถ้า publish ล้มเหลว

    # 5) อัปเดต watermark ของชุดนี้ เฉพาะตอน publish สำเร็จทั้งหมดแล้ว
    set_last_watermark(name, latest_seen)
    return len(futures)
```

จุดที่พลาดบ่อย: **ต้องรอ `future.result()` ทุกตัวก่อนไปต่อ** (ไม่งั้น process ถูกฆ่า
ก่อน publish จบ ข้อความหายเงียบๆ) และ **อัปเดต watermark หลัง publish สำเร็จเท่านั้น**
(อัปเดตก่อนแล้ว publish fail กลางทาง = รอบถัดไปข้ามแถวที่ยังไม่ถูกส่งจริงไปเลย)
watermark แยกต่อชุด — ชุดที่พังรอบนี้จะส่งซ้ำรอบหน้าเอง ไม่กระทบชุดที่ผ่านแล้ว

### 7. ให้สิทธิ์ Cloud Run Invoker กับ SA ที่ Scheduler ใช้เรียก function

**ทำ**: เมนู ☰ → **Cloud Run** → service `databuffet-export-publisher` (function 2nd gen
คือ Cloud Run service ชื่อเดียวกัน) → tab **SECURITY** หรือ **PERMISSIONS → ADD
PRINCIPAL** → principal = default compute service account จากขั้น 4 → Role: **Cloud Run
Invoker** → **SAVE** — ให้ที่ **ระดับ service นี้เท่านั้น ไม่ใช่ระดับ project**

**ทำไม**: function ที่ติ๊ก Require authentication จะรับเฉพาะคนที่มี `roles/run.invoker`
บน service นั้น — Cloud Scheduler ส่ง OIDC token ในนาม default compute SA (ขั้น 9)
ซึ่ง **ไม่มี** role นี้มาแต่แรก ถ้าข้ามขั้นนี้ Scheduler จะได้ **403 ทุกรอบที่เรียก** ให้ระดับ service
เพื่อให้ SA นี้เรียกได้แค่ function นี้ ไม่ใช่ทุก Cloud Run service ใน project

### 8. ทดสอบ trigger มือ

**ทำ**: หน้า Cloud Function → tab **TESTING → TEST THE FUNCTION** → เช็คว่า
message เข้า `sub-test-poc` จริงไหม (ทำซ้ำแบบขั้น 3.3) และ response ไม่มีชุดไหนใน
`failed`

**ทำไม**: ยืนยันว่า Cloud Function ทำงานจริง (query ได้ + publish ได้) ก่อนตั้งให้
รันอัตโนมัติทุกวัน — ⚠️ ปุ่ม test ใน console เรียกด้วยตัวตน **ของคนที่กด** ไม่ใช่ของ SA
จึง **ผ่าน** แม้ลืมขั้น 7 ต้องทดสอบเส้นทางจริงอีกรอบด้วย **FORCE RUN** ในขั้น 9

### 9. ตั้ง Cloud Scheduler ให้รันอัตโนมัติทุกวัน 07:00

**ทำ**: เมนู ☰ → **Cloud Scheduler → CREATE JOB**
- Name: `databuffet-export-trigger`, Region: `us-central1`
- Frequency (cron): `0 7 * * *`, Timezone: `Asia/Bangkok`
- Target type: **HTTP** → URL: จาก Cloud Function (tab **TRIGGER**)
- Auth header: **Add OIDC token** → Service account: default compute service
  account (ตัวเดียวกับขั้น 4 ที่ได้ Cloud Run Invoker ในขั้น 7)
- **Configure optional settings** → Attempt deadline: **30m** → ปล่อย retry settings
  เป็น default → **CREATE**
- กด **FORCE RUN** ที่ job แล้วดูคอลัมน์ result / log — ต้องสำเร็จและไม่มี 403

**ทำไม**: ทำให้ Cloud Function รันอัตโนมัติทุกวันโดยไม่ต้องมีคนกดเอง — 07:00 คือ **หลัง**
Dataform nightly (`daily_process` 06:00 เสร็จราว 06:08 เช็คจาก `check-runs` skill)
ส่วน attempt deadline default 3 นาที ถ้า function รันนานกว่านั้น Scheduler
จะขึ้นว่า fail ทั้งที่ function ยังทำงานอยู่ · FORCE RUN ใช้ OIDC token ของ SA จริง จึงจับ
403 จากการลืมขั้น 7 ได้ (ต่างจากปุ่ม test ในขั้น 8)

### 10. ลบ subscription ทดสอบ

**ทำ**: **Pub/Sub → Subscriptions → sub-test-poc → ⋮ → Delete**

**ทำไม**: เป็น subscription ที่สร้างไว้ทดสอบเท่านั้น ปล่อยไว้จะมีข้อความ order สะสม
จากการ export และสร้างความสับสนว่าเป็นของทีมจริง

---

## ส่วน B — ต่อทีมที่มาใช้ข้อมูล (ทำซ้ำทุกครั้งที่มีทีมใหม่)

ทุกทีม — ในบริษัทหรือนอกบริษัท — ใช้ขั้นตอนเดียวกันนี้เสมอ (push ไปที่ endpoint ของทีม)
ตัวอย่างด้านล่างใช้ทีม TF (`<ทีม>` = `tf`)

### 11. ขอ HTTPS endpoint จากทีมนั้น

**ทำ**: ขอ URL ของ endpoint ที่จะรับข้อมูลจากทีม (เช่น `https://<โดเมนของทีม>/pubsub`)
endpoint เดียวรับได้ทุกชุด (แยกชุดด้วย field `table` ใน message) — เงื่อนไขของ endpoint:
- เป็น **HTTPS** ที่มี certificate ถูกต้อง และเปิดให้ Pub/Sub ของ Google เรียกจาก internet ได้
  (ถ้าทีมใช้ GCP จะเป็น Cloud Run ก็ได้)
- รับ `POST` ได้หลาย request พร้อมกัน และตอบภายในไม่กี่วินาที
- ถ้าใช้ Cloud Run ให้ทีมส่ง **Service URL** จากหน้า service มาด้วย เช่น
  `https://service.run.app` — ใช้เป็น audience ในขั้น 13 แม้ endpoint จะเป็น
  `https://service.run.app/pubsub` หรือใช้โดเมนของทีมเอง

**ทำไม**: แบบ push ทีมเป็นฝ่ายเปิดประตูรับ เราเป็นฝ่ายส่ง — ทีมจึงไม่ต้องมีบัญชีหรือ key
ใดๆ ของ project เรา ไม่มี secret อายุยาวต้องส่งข้ามองค์กร ถ้าเลิกส่งให้ทีมนี้ก็แค่ลบ sub ของเขา

### 12. สร้าง push service account ภายในให้ทีมนั้น (1 ทีม = 1 SA, ไม่สร้าง key)

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
· คนที่จะสร้าง sub ในขั้น 13 ต้องมีสิทธิ์ใช้ SA นี้ (Service Account User — Owner มีอยู่แล้ว)
· Cloud Run ตรวจสิทธิ์ Invoker ก่อนส่ง request เข้า handler ถ้าข้ามข้อ 3 จะได้ 403
แม้ token ถูกต้อง — ดู [การต่อ Pub/Sub กับ Cloud Run](https://docs.cloud.google.com/run/docs/tutorials/pubsub)

### 13. สร้าง push subscription ให้ทีมนั้น — 1 อันต่อ 1 topic ที่ทีมได้รับ

**ทำ**: **Pub/Sub → Topics → `export-commission-<ชุด>` → CREATE SUBSCRIPTION**
- ID: `sub-<ทีม>-<ชุด>` (เช่น `sub-tf-order`)
- Delivery type: **Push** → Endpoint URL: URL จากขั้น 11
- ติ๊ก **Enable authentication** → Service account: `sa-push-<ทีม>` (ขั้น 12) →
  Audience: ถ้า endpoint เป็น **Cloud Run** ใส่ **Service URL** จากขั้น 11
  (`https://service.run.app` ไม่รวม `/pubsub`); endpoint HTTPS อื่นใช้ endpoint URL
  — ให้ทีมใช้ค่าเดียวกันตรวจ token
- ปล่อย Acknowledgement deadline, Retry policy และ Message retention เป็น **default**
  → **CREATE**

ทำซ้ำทุก topic ที่ทีมนั้นได้รับ (TF ได้ครบ 14 → 14 อัน; ทีมที่ได้บางชุด สร้างเฉพาะชุดนั้น)

**ทำไม**: subscription คือ "ตัวชี้ว่าส่งถึงไหน" ส่วนตัวของแต่ละทีมบน topic นั้น — endpoint
ทีมนี้ล่ม/ตอบช้า ไม่กระทบทีมอื่นที่ต่อ topic เดียวกัน 1 sub ผูกได้ 1 topic และชื่อห้ามซ้ำ
ทั้ง project จึงต้องมีชื่อชุดต่อท้าย · ไม่ต้องให้สิทธิ์ Subscriber กับใครเลย เพราะทีมไม่ได้
เข้ามาดึงเอง · Cloud Run ต้องใช้ Service URL เป็น audience แม้ POST จะส่งไปที่ path
`/pubsub` — ดู [ข้อกำหนด audience ของ Cloud Run](https://docs.cloud.google.com/run/docs/authenticating/service-to-service)
· ข้อความที่ส่งไม่สำเร็จเก็บไว้ได้ **7 วัน** ตาม default หลังจากนั้นหาย (เฝ้าด้วยขั้น 15)

### 14. Backfill ให้ทีมใหม่ (ครั้งแรกที่ต่อเข้ามาเท่านั้น)

**ทำ**: หลังสร้าง sub ครบแล้ว รัน export แบบไม่กรอง `update_on` (ดึงทั้งหมดตั้งแต่แรก
จนปัจจุบัน) 1 รอบ ก่อนให้ Cloud Scheduler เดินตามปกติ

**ทำไม**: export ปกติเป็น delta อย่างเดียว ทีมใหม่ที่เพิ่งต่อจะไม่มีข้อมูลตั้งต้นถ้าไม่
backfill ก่อน — ข้อความ publish เข้า topic จะไปถึง **ทุก sub บน topic นั้น** ไม่ใช่แค่
ทีมใหม่ ทีมเดิมจึงได้ข้อมูลซ้ำด้วย ซึ่งไม่เพี้ยนเพราะ consumer เป็น upsert/delete ตาม key
แต่ควรแจ้งทีมเดิมก่อนว่ารอบนั้นข้อความจะเยอะ (ทีม TF เป็นทีมแรก จึงไม่มีผลกับใคร)

### 15. ตั้ง alert เมื่อข้อความค้าง

**ทำ**: **Monitoring → Alerting → CREATE POLICY** → metric
`Pub/Sub Subscription → Unacked messages` (`num_undelivered_messages`) → filter
`subscription_id` starts with `sub-<ทีม>-` → Group by `subscription_id` → threshold
ตามที่เหมาะสม → ส่งแจ้งเตือนทาง channel ของทีม

**ทำไม**: policy เดียวครอบ sub ของทีมนั้นทั้ง 14 อัน ไม่ต้องตั้งทีละอัน — ข้อความค้าง =
endpoint ของทีมล่มหรือรับข้อความไม่สำเร็จ ข้อความเก็บไว้ 7 วัน ถ้า endpoint ไม่กลับมารับนาน
เกินนั้นข้อมูลจะหาย ต้องรู้ก่อน

### 16. ส่ง handover package ให้ทีม

ส่งให้ครบ 5 อย่าง (ไม่มีอะไรเป็น secret — ส่งช่องทางปกติได้):
1. รายชื่อชุดข้อมูลที่จะถูก push ไป endpoint ของทีม (`sub-<ทีม>-<ชุด>` ทุกชุดที่ได้รับ)
2. ค่าที่ endpoint ต้องใช้ตรวจ token: อีเมล `sa-push-<ทีม>@databuffet-nonprd.iam.gserviceaccount.com`
   และ audience ที่ตั้งในขั้น 13 (Cloud Run = Service URL, HTTPS อื่น = endpoint URL)
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
    "attributes": {},
    "messageId": "1234567890",
    "publishTime": "2026-10-13T00:05:12.345Z"
  },
  "subscription": "projects/databuffet-nonprd/subscriptions/sub-tf-order"
}
```

- `message.data` = message format ด้านบน (JSON) ที่เข้ารหัส **base64** — ต้อง decode ก่อน
  ค่าในตัวอย่างเป็น placeholder ต้องแทนด้วย base64 ของ JSON จริงก่อนใช้
- `message.attributes` = ตอนนี้ว่าง (publisher ไม่ได้ใส่)
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

ตั้ง `AUDIENCE` ให้ตรงกับค่าที่ได้รับใน handover (ขั้น 16): ตัวอย่างใช้ Cloud Run
Service URL; ถ้าเป็น HTTPS endpoint อื่น ให้เปลี่ยนเป็น endpoint URL ที่ตั้งในขั้น 13
ตัวตรวจ token ใช้ CacheControl cache certificate ตาม HTTP expiry โดยยังตรวจลายเซ็น,
audience และอีเมล SA ทุก request — ดู [คำแนะนำ cache ของ google-auth](https://google-auth.readthedocs.io/en/latest/reference/google.oauth2.id_token.html)

จุดที่พลาดบ่อย: **ห้ามข้ามการตรวจ token** (endpoint เปิดบน internet ใครก็ยิงข้อมูลปลอมเข้ามาได้)
และ **ack หลังเขียนสำเร็จเท่านั้น** (ตอบก่อนแล้วเขียนพัง = ข้อความหายเพราะ Pub/Sub ถือว่า ack แล้ว)
ถ้า body/base64/JSON หรือ field ที่จำเป็นอ่านไม่ได้ ให้ตอบรหัสที่ไม่ ack (ดู "รูปแบบ push body")
งานเขียนแต่ละข้อความควรเสร็จในไม่กี่วินาที — ถ้าช้ากว่า ack deadline Pub/Sub จะส่งซ้ำทั้งที่
ข้อความแรกยังทำอยู่

⚠️ Pub/Sub การันตีแค่ "ส่งอย่างน้อย 1 ครั้ง" (at-least-once) และไม่เรียงลำดับ —
handler ต้อง idempotent (upsert/delete ตาม primary key ปลอดภัยอยู่แล้ว) ทุกข้อความเป็น
สถานะล่าสุดของแถวนั้น จึงไม่ต้องสนลำดับ

---

## Checklist

- [ ] เปิด Pub/Sub, Cloud Functions, Cloud Scheduler, Cloud Run API แล้ว
- [ ] สร้าง topic `export-commission-<ชุด>` ครบ 14 อัน (ไม่มี default subscription ติดมา)
- [ ] ทดสอบ publish/pull มือผ่านแล้ว (ขั้น 3)
- [ ] Default compute service account มี Pub/Sub Publisher + BigQuery Job User
      (project), BigQuery Data Viewer (dataset ต้นทาง/export),
      BigQuery Data Editor (dataset watermark)
- [ ] Cloud Function deploy แล้ว (timeout 1800s) และทดสอบ trigger มือผ่าน (ขั้น 8)
- [ ] Default compute SA ได้ **Cloud Run Invoker บน service `databuffet-export-publisher`**
      (ระดับ service ไม่ใช่ project — ขั้น 7)
- [ ] Cloud Scheduler `0 7 * * *` Asia/Bangkok (**หลัง** Dataform nightly 06:00 เสร็จจริง
      เช็คจาก `check-runs` ไม่ใช่เดา), attempt deadline 30m, retry settings เป็น default,
      **FORCE RUN แล้วไม่ได้ 403** (ปุ่ม test ของ function ไม่นับ)
- [ ] ลบ `sub-test-poc` แล้ว
- [ ] ต่อทีมใหม่: ได้ HTTPS endpoint จากทีมแล้ว
- [ ] ต่อทีมใหม่: `sa-push-<ทีม>` (ไม่มี key) + Pub/Sub service agent เป็น Service Account
      Token Creator บน SA นั้น
- [ ] ต่อทีมใหม่ที่ใช้ Cloud Run: `sa-push-<ทีม>` ได้ Cloud Run Invoker บน service
      ที่รับ push ใน project ของทีม (ขั้น 12.3)
- [ ] ต่อทีมใหม่: push sub `sub-<ทีม>-<ชุด>` ครบทุกชุดที่ได้รับ — authentication =
      `sa-push-<ทีม>` + audience ตรงกับ handover (Cloud Run = Service URL,
      HTTPS อื่น = endpoint URL), acknowledgment/retry settings เป็น default
- [ ] ต่อทีมใหม่: backfill แบบไม่กรอง `update_on` 1 รอบก่อนเข้าโหมด delta ปกติ
- [ ] ต่อทีมใหม่: alert backlog 1 policy ครอบ `sub-<ทีม>-*`
- [ ] ส่ง handover package ครบ 5 อย่าง (ไม่มี SA key)

## งานที่ยังไม่ปิด (นอกเอกสารนี้)

- port query คุณแป้ง 8 ไฟล์ (T-SQL) เป็นตาราง export 14 ชุดบน BigQuery พร้อม
  `update_on` + flag — ผู้ใช้ออกแบบ logic flag เอง (อ้างอิงจาก pattern document-grain
  purge ที่มีอยู่แล้วใน `mil`/`mih`, ดู [project_wiki/validated/validated-layer.md](../project_wiki/validated/validated-layer.md))
- ตาราง/function ต้นทางที่ยังไม่มีในคลัง (`mih_payment_method`, `mih_payment_mapping`,
  `FOB61`, `fn_returnMihmemopaymentfromorder`) และเงื่อนไข query ที่ต้องยืนยันกับ
  คุณแป้ง — ต้องได้คำตอบก่อน port ชุดที่เกี่ยวข้อง
- primary key ของแต่ละชุด (โดยเฉพาะ `receipt` ที่ query ต้นฉบับยังไม่มี key ที่ไม่ซ้ำ)
- query ฝั่ง publish ต้อง drive จากตาราง CDC/flag ไม่ใช่ join ออกจาก `mil`/`mih`
  ตรงๆ (ดูคำเตือนเรื่อง `DELETE` ด้านบน)
- ยังไม่ตัดสินใจว่าจะย้าย setup นี้ไปเป็น Terraform เมื่อไหร่ — 14 topic × จำนวนทีม
  ทำมือใน Console จะเริ่มหนัก แนะนำย้ายเมื่อมีทีมที่ 2
