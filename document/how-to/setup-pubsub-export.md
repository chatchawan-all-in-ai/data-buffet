# How-to: Setup Pub/Sub สำหรับส่งออกข้อมูลจาก BigQuery

> สถานะ: **ใช้งานจริง** (ไม่ใช่ POC ทิ้ง) — scope ตารางเริ่มที่ `mil`, `mih`
> (validated_mac5) รายละเอียดแต่ละส่วนจะถูกปรับเพิ่มทีหลังตามที่ผู้ใช้เห็นเหมาะสม
> เอกสารนี้อยู่นอก pipeline หลักของ Dataform (ไม่แก้ `definitions/`, `includes/`,
> `workflow_settings.yaml`) — เป็น GCP infra แยกสำหรับส่งข้อมูลออกไปให้ระบบ/ทีมอื่นใช้

## ภาพรวม

ทุกคืน หลัง Dataform nightly run เสร็จ ระบบจะดึง **เฉพาะแถวที่เปลี่ยน** จากตาราง
export ที่ (คุณ) เตรียมไว้เอง แล้ว publish เข้า Pub/Sub topic เดียว ทีมที่จะมาใช้ข้อมูล
— ไม่ว่าอยู่ในบริษัทหรือนอกบริษัท — **ดึงข้อมูลด้วยวิธี pull เหมือนกันหมด** ไม่มี push/webhook

```
Dataform nightly run
        │
        ▼
Cloud Scheduler (trigger ตามเวลา)
        │
        ▼
Cloud Function  ── query ตาราง export (มี update_on + flag NEW/UPDATE/DELETE) ──▶ publish
        │
        ▼
Pub/Sub topic (1 topic)
        │
   ┌────┴────┬────────────┐
   ▼         ▼            ▼
 sub-team-A sub-team-B  sub-team-C   ← แต่ละทีม pull เอง ด้วย service account ของตัวเอง
```

**สิ่งที่เอกสารนี้ไม่ครอบคลุม** (ผู้ใช้ออกแบบเอง): logic การหา "แถวไหนเปลี่ยน" (query/table/view
export + column `update_on` + flag สถานะ) — เอกสารนี้ครอบคลุมแค่ตัว Pub/Sub infra
กับวิธีที่ทีมต่างๆ มาดึงข้อมูลออกไปใช้

## Message format (มาตรฐานเดียว ทุกทีมใช้ร่วมกัน)

```json
{
  "table": "mil",
  "run_date": "2026-09-21",
  "operation": "NEW",
  "primary_key": { "company_id": "ag01", "milType": "IV", "milVnos": "000123" },
  "data": { "...": "แถวข้อมูลเต็ม" }
}
```

| field | ค่า | หมายเหตุ |
|---|---|---|
| `table` | ชื่อตารางต้นทาง | `mil` / `mih` (ตอนนี้) |
| `run_date` | วันที่ export | ใช้ debug/ตรวจสอบ ไม่ใช่ key |
| `operation` | `NEW` \| `UPDATE` \| `DELETE` | ปลายทางใช้ตัดสินว่าจะ upsert หรือ delete |
| `primary_key` | object ของ key column | สำหรับ `DELETE` — `data` อาจไม่มีเพราะแถวถูกลบไปแล้วจากต้นทาง |
| `data` | แถวข้อมูลเต็ม | มีเฉพาะกรณี `NEW`/`UPDATE` |

⚠️ **ข้อควรระวังตอนออกแบบ query ฝั่ง publish (ยังไม่ทำในเอกสารนี้ แต่ต้องรู้ไว้)**:
query ต้อง drive จากตาราง CDC/flag เป็นหลัก ไม่ใช่ join ออกจากตาราง `mil`/`mih` ตรงๆ
เพราะแถวที่ถูก `DELETE` จะไม่มีอยู่ใน `mil`/`mih` แล้ว ถ้า join แบบ inner จะได้ 0 แถว
และ `DELETE` นั้นจะไม่ถูกส่งไป Pub/Sub เลย

⚠️ **ทีมใหม่ที่ต่อ topic ครั้งแรก**: เพราะ export เป็น **delta อย่างเดียว** (ไม่ใช่ full
dump ทุกวัน) ทีมใหม่จะได้แค่ข้อมูลที่เปลี่ยนตั้งแต่วันที่เขาต่อ subscription เท่านั้น
**ต้องรัน export แบบไม่กรอง `update_on` (เอาทั้งหมดตั้งแต่แรกจนปัจจุบัน) ให้เขาก่อน 1
รอบ** ก่อนสลับไปใช้ watermark กรองตามปกติ ไม่งั้นทีมใหม่จะไม่มีข้อมูลตั้งต้น

## Prerequisites

- สิทธิ์ Owner/Editor บน project `databuffet-nonprd` (หรือสิทธิ์สร้าง Pub/Sub, IAM,
  Cloud Functions, Cloud Scheduler อย่างน้อย)
- ตาราง/view export ที่มี column `update_on` + flag สถานะ (`NEW`/`UPDATE`/`DELETE`) —
  เตรียมแยกจากเอกสารนี้

---

## ส่วน A — Setup Pub/Sub infra (ทำครั้งเดียว)

ทำผ่านหน้า [console.cloud.google.com](https://console.cloud.google.com) ทั้งหมด
เลือก project **databuffet-nonprd** ที่มุมบนซ้ายก่อนเริ่ม

### 1. เปิด API ที่ต้องใช้

**ทำ**: เมนู ☰ → **APIs & Services → Library** → ค้นหาแล้วกด **Enable** ทีละตัว:
`Cloud Pub/Sub API`, `Cloud Functions API`, `Cloud Scheduler API`, `Cloud Run API`

**ทำไม**: GCP ปิด service เหล่านี้ไว้เป็น default ต่อ project ถ้าไม่เปิดก่อน ขั้นตอน
หลังจะสร้าง resource ไม่ได้เลย

### 2. สร้าง Pub/Sub topic

**ทำ**: เมนู ☰ → **Pub/Sub → Topics → CREATE TOPIC**
- Topic ID: `databuffet-export-mil-mih`
- ปล่อย default อื่นไว้ (ไม่ต้องติ๊ก default subscription) → **CREATE**

**ทำไม**: topic คือ "ท่อกลาง" ที่ข้อมูลทุกแถวที่เปลี่ยนจะถูกส่งเข้ามา และเป็นจุดเดียว
ที่ทุกทีมจะมาต่อ subscription เพื่อดึงออกไป — มี topic เดียวพอ ไม่ต้องแยกทีมแยกตาราง

### 3. ทดสอบว่า topic ใช้งานได้ก่อนไปต่อ

**ทำ**:
1. ในหน้า topic → **CREATE SUBSCRIPTION** → ID: `sub-test-poc` → Delivery type:
   **Pull** → **CREATE**
2. กลับหน้า topic → tab **MESSAGES → PUBLISH MESSAGE** → พิมพ์ข้อความทดสอบ (เช่น
   `{"table":"mil","operation":"NEW"}`) → **PUBLISH**
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
custom SA แยกเหมือนที่วางไว้แต่แรก เพื่อลดขั้นตอน setup — ต่างจาก service account
ของทีมภายนอกในส่วน B ที่ยังคง **แยกต่อทีมเสมอ** (เรื่องนั้นกระทบความปลอดภัยข้ามทีม
โดยตรง จึงไม่ใช้ default SA ร่วม)

### 5. ให้สิทธิ์ default service account

**ทำ**:
- topic `databuffet-export-mil-mih` → tab **PERMISSIONS → ADD PRINCIPAL** →
  principal = default compute service account จากขั้น 4 → Role: **Pub/Sub
  Publisher** → **SAVE**
- BigQuery → dataset `validated_mac5` → **SHARING → Permissions → ADD PRINCIPAL** →
  principal เดิม → Role: **BigQuery Data Viewer** → **SAVE**

**ทำไม**: default service account ของ project ที่สร้างใหม่ **ไม่มีสิทธิ์ Editor
กว้างให้อัตโนมัติแล้ว** (Google เปลี่ยนพฤติกรรม default นี้ไปแล้ว) ต้องเช็ค/เพิ่ม
สิทธิ์ 2 อย่างนี้เอง ไม่งั้น Cloud Function จะ publish เข้า topic ไม่ได้ และอ่าน
BigQuery ไม่ได้ (permission denied)

### 6. Deploy Cloud Function

**ทำ**: เมนู ☰ → **Cloud Functions → CREATE FUNCTION**
- Environment: **2nd gen**
- Function name: `databuffet-export-publisher`, Region: `us-central1`
- Trigger type: **HTTPS**, ติ๊ก **Require authentication** → **NEXT**
- Runtime: **Python 3.12**, Entry point: `export_daily`
- Runtime service account: ปล่อยเป็นค่า default — จะใช้ default compute service
  account จากขั้น 4 อัตโนมัติ ไม่ต้องเลือกเอง
- วางโค้ด query (ตาราง export + `update_on` + flag) และ publish logic ในตัวแก้ไข
  inline → **DEPLOY**

**ทำไม**: นี่คือตัว "คนงาน" ที่ไปดึงแถวที่เปลี่ยนจาก BigQuery แล้วแปลงเป็น message
ตาม format ด้านบน ส่งเข้า topic จริง

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
TOPIC_ID = "databuffet-export-mil-mih"

bq_client = bigquery.Client()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@functions_framework.http
def export_daily(request):
    # 1) อ่าน watermark ล่าสุด (รันครั้งก่อนถึงไหน) จาก control table ของคุณ
    last_exported_at = get_last_watermark("mil")

    # 2) ดึงเฉพาะแถวที่เปลี่ยน — WHERE/flag column เป็นของคุณ ใส่ตัวอย่างไว้
    query = """
        SELECT *
        FROM `databuffet-nonprd.<export_dataset>.<export_view_or_table>`
        WHERE update_on > @last_exported_at
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter(
            "last_exported_at", "TIMESTAMP", last_exported_at)]
    )
    rows = bq_client.query(query, job_config=job_config).result()

    # 3) แปลงเป็น message ตาม format ที่ตกลงกัน แล้ว publish
    futures = []
    count = 0
    latest_seen = last_exported_at
    for row in rows:
        envelope = {
            "table": "mil",
            "run_date": str(row.update_on.date()),
            "operation": row.record_status,          # "NEW"/"UPDATE"/"DELETE" จากตารางคุณ
            "primary_key": {"company_id": row.company_id, "milType": row.milType,
                             "milVnos": row.milVnos, "milListno": row.milListno},
            "data": None if row.record_status == "DELETE" else dict(row),
        }
        future = publisher.publish(topic_path, json.dumps(envelope, default=str).encode("utf-8"))
        futures.append(future)
        count += 1
        latest_seen = max(latest_seen, row.update_on)

    # 4) รอให้ publish จบจริงก่อน function return — ไม่รอจะเสี่ยงข้อความหาย
    for f in futures:
        f.result()   # จะ raise ถ้า publish ล้มเหลว

    # 5) อัปเดต watermark เฉพาะตอน publish สำเร็จทั้งหมดแล้ว
    set_last_watermark("mil", latest_seen)

    return f"published {count} messages", 200
```

จุดที่พลาดบ่อย: **ต้องรอ `future.result()` ทุกตัวก่อน return** (ไม่งั้น process ถูกฆ่า
ก่อน publish จบ ข้อความหายเงียบๆ) และ **อัปเดต watermark หลัง publish สำเร็จเท่านั้น**
(อัปเดตก่อนแล้ว publish fail กลางทาง = รอบถัดไปข้ามแถวที่ยังไม่ถูกส่งจริงไปเลย)

### 7. ทดสอบ trigger มือ

**ทำ**: หน้า Cloud Function → tab **TESTING → TEST THE FUNCTION** → เช็คว่า
message เข้า `sub-test-poc` จริงไหม (ทำซ้ำแบบขั้น 3.3)

**ทำไม**: ยืนยันว่า Cloud Function ทำงานจริง (query ได้ + publish ได้) ก่อนตั้งให้
รันอัตโนมัติทุกคืน — ถ้าตั้ง Scheduler ไปเลยแล้วพัง จะไม่รู้ว่าพังตรงไหนจนกว่าจะถึง
กลางคืน

### 8. ตั้ง Cloud Scheduler ให้รันอัตโนมัติทุกคืน

**ทำ**: เมนู ☰ → **Cloud Scheduler → CREATE JOB**
- Name: `databuffet-export-trigger`, Region: `us-central1`
- Frequency (cron): `30 3 * * *`, Timezone: `Asia/Bangkok`
- Target type: **HTTP** → URL: จาก Cloud Function (tab **TRIGGER**)
- Auth header: **Add OIDC token** → Service account: default compute service
  account (ตัวเดียวกับขั้น 4) → **CREATE**

**ทำไม**: ทำให้ Cloud Function รันอัตโนมัติทุกคืนโดยไม่ต้องมีคนกดเอง — เวลาต้องตั้ง
**หลัง** Dataform nightly run (`validated`/`validated_full`) เสร็จจริง เช็คจาก
`check-runs` skill ก่อนตั้ง ไม่ใช่เดา

### 9. ลบ subscription ทดสอบ

**ทำ**: **Pub/Sub → Subscriptions → sub-test-poc → ⋮ → Delete**

**ทำไม**: เป็น subscription ที่สร้างไว้ทดสอบเท่านั้น ปล่อยไว้จะกินโควตา/สร้างความ
สับสนว่าเป็นของทีมจริง

---

## ส่วน B — ต่อทีมที่มาใช้ข้อมูล (ทำซ้ำทุกครั้งที่มีทีมใหม่)

ทุกทีม — ในบริษัทหรือนอกบริษัท — ใช้ขั้นตอนเดียวกันนี้เสมอ (pull เท่านั้น)

### 10. สร้าง subscription ให้ทีมนั้น

**ทำ**: **Pub/Sub → Topics → databuffet-export-mil-mih → CREATE SUBSCRIPTION** →
ID: `sub-export-<ชื่อทีม>` → Delivery: **Pull** → **CREATE**

**ทำไม**: subscription คือ "ช่องรับ" ส่วนตัวของแต่ละทีม แยกจากทีมอื่นเสมอ — ทีมนี้
หายไป/ล่ม ไม่กระทบทีมอื่นที่ต่ออยู่กับ topic เดียวกัน

### 11. สร้าง service account ให้ทีมนั้นใช้ดึงข้อมูล

**ทำ**: **IAM & Admin → Service Accounts → CREATE SERVICE ACCOUNT** → name:
`sa-consumer-<ชื่อทีม>`

**ทำไม**: แต่ละทีมต้องมี identity แยกของตัวเอง เพื่อให้ตัด/จำกัดสิทธิ์เขาได้โดยไม่
กระทบทีมอื่น

### 12. ให้สิทธิ์แค่ subscription ของทีมนั้น

**ทำ**: หน้า `sub-export-<ชื่อทีม>` → **PERMISSIONS → ADD PRINCIPAL** → service
account จากขั้น 11 → Role: **Pub/Sub Subscriber** → **SAVE**

**ทำไม**: จำกัดสิทธิ์ให้แคบที่สุด — ทีมนี้ดึงได้แค่ subscription ของตัวเอง ดึงของ
ทีมอื่นไม่ได้ ถึงแม้อยู่ topic เดียวกัน

### 13. Backfill ให้ทีมใหม่ (ครั้งแรกที่ต่อเข้ามาเท่านั้น)

**ทำ**: รัน export แบบไม่กรอง `update_on` (ดึงทั้งหมดตั้งแต่แรกจนปัจจุบัน) ครั้งเดียว
ให้ตรงกับ subscription ของทีมใหม่นี้เท่านั้น ก่อนให้ Cloud Scheduler เดินตามปกติ

**ทำไม**: export ปกติเป็น delta อย่างเดียว ทีมใหม่ที่เพิ่งต่อจะไม่มีข้อมูลตั้งต้น
ถ้าไม่ backfill ก่อน (ดูหัวข้อ "ข้อควรระวัง" ด้านบน)

### 14. ส่ง handover package ให้ทีมไปเขียนโค้ดฝั่งเขา

ส่งให้ครบ 4 อย่าง:
1. ชื่อ subscription: `sub-export-<ชื่อทีม>`
2. Credentials ของ service account จากขั้น 11 (ส่งผ่านช่องทาง secure เท่านั้น)
3. Message format (ตารางด้านบน)
4. รายชื่อตาราง + primary key ของตารางนั้น (เช่น `mil` → `company_id, milType,
   milVnos, milListno`)

**ทำไม**: เป็น handover package มาตรฐานเดียว ใช้ซ้ำได้กับทุกทีมที่มาใหม่ ไม่ต้อง
คิดใหม่ทุกครั้ง

### ตัวอย่างโค้ด consumer (ฝั่งทีมที่มาใช้ — เหมือนกันทุกทีม)

```python
from google.cloud import pubsub_v1
import json

subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path("databuffet-nonprd", "sub-export-<ชื่อทีม>")

def callback(message):
    envelope = json.loads(message.data)
    op, pk = envelope["operation"], envelope["primary_key"]
    if op in ("NEW", "UPDATE"):
        upsert_by_primary_key(pk, envelope["data"])
    elif op == "DELETE":
        delete_by_primary_key(pk)
    message.ack()

subscriber.subscribe(sub_path, callback=callback)
```

⚠️ Pub/Sub การันตีแค่ "ส่งอย่างน้อย 1 ครั้ง" (at-least-once) — handler ฝั่ง consumer
ต้อง idempotent (upsert/delete ตาม primary key ปลอดภัยอยู่แล้ว) และควร dedupe เอง
ถ้า process ซ้ำมีผลกระทบ

---

## Checklist

- [ ] เปิด Pub/Sub, Cloud Functions, Cloud Scheduler API แล้ว
- [ ] สร้าง topic `databuffet-export-mil-mih` แล้ว
- [ ] ทดสอบ publish/pull มือผ่านแล้ว (ขั้น 3)
- [ ] Default compute service account มีสิทธิ์ Pub/Sub Publisher (topic) +
      BigQuery Data Viewer (dataset ต้นทาง) แล้ว
- [ ] Cloud Function deploy แล้ว และทดสอบ trigger มือผ่าน (ขั้น 7)
- [ ] Cloud Scheduler ตั้งเวลาไว้ **หลัง** Dataform nightly run เสร็จจริง (เช็คจาก
      `check-runs` ไม่ใช่เดา)
- [ ] ลบ `sub-test-poc` แล้ว
- [ ] ต่อทีมใหม่: subscription + service account + IAM แยกต่อทีมเสมอ (ไม่ใช้ร่วมกัน)
- [ ] ต่อทีมใหม่: backfill แบบไม่กรอง `update_on` ให้ 1 รอบก่อนเข้าโหมด delta ปกติ
- [ ] ส่ง handover package ครบ 4 อย่างให้ทุกทีมที่มาใหม่

## งานที่ยังไม่ปิด (นอกเอกสารนี้)

- ตาราง/view export ที่มี `update_on` + flag สถานะ — ผู้ใช้ออกแบบเอง (อ้างอิงจาก
  pattern document-grain purge ที่มีอยู่แล้วใน `mil`/`mih`, ดู [project_wiki/validated/validated-layer.md](../project_wiki/validated/validated-layer.md))
- query ฝั่ง publish ต้อง drive จากตาราง CDC/flag ไม่ใช่ join ออกจาก `mil`/`mih`
  ตรงๆ (ดูคำเตือนเรื่อง `DELETE` ด้านบน)
- ยังไม่ตัดสินใจว่าจะย้าย setup นี้ไปเป็น Terraform เมื่อไหร่ — แนะนำรอให้ pattern
  "เพิ่มทีมใหม่" นิ่งก่อน
