# How-to: รันและ Debug

> ตรวจกับ `includes/controller/variables.json` และโค้ดจริงเมื่อ 2026-09-15

## รันด้วย tag

**รันจริงผ่าน Dataform UI บน GCP** — โปรเจกต์ไม่ได้ตั้ง `.df-credentials.json`
สำหรับ CLI execution · สร้าง execution แล้วเลือก tag เช่น `validated_incremental`,
`dimension_daily`, `fact_daily`, `view` หรือเลือก action เดียว เช่น
`validated_mac5.mih` และรวม dependencies เมื่อต้องการ

ถ้ามี CLI global เพิ่มเติมตาม [onboarding §3.2](../getting-started/onboarding.md#32-เครื่องมือ)
ใช้ `dataform compile --json` ดู query/dependency graph ได้:

```bash
dataform compile --json | jq '.tables[] | {name: .target.name, deps: .dependencyTargets}'
```

`dataform format` เขียนไฟล์ใหม่ — ใช้เฉพาะไฟล์ที่ตั้งใจแก้ และตรวจ diff หลังรัน

### Tag ทั้งหมด

รายการ tag และหน้าที่อยู่ที่ [registry reference](../project_wiki/includes/variables.md#tags)
· ⚠️ `initial` / `re-initial` มี action ลบตาราง — ขอบเขตและวิธีเลือก action
ดู [initial layer](../project_wiki/initial/initial-layer.md#การผูก-dependency)

**ประกาศไว้แต่ยังไม่ถูกใช้**: `dimension_monthly`, `fact_monthly`, `fact_yearly`

**ไม่มี tag `assertions`** — โปรเจกต์นี้ไม่มี Dataform assertion เลย
การตรวจคุณภาพข้อมูลแบบเฉพาะกิจทำด้วย skill `data-quality-check`
ส่วน Org Center มี [ตารางรายงาน data-quality flags](../project_wiki/org_center/org-center.md#org_center_flags)
ที่สร้างพร้อม tag `dimension_daily` (ไม่ใช่ assertion)

### ลำดับที่ควรรัน

```
initial → validated → curated → dimension_daily → fact_daily → view
                                         ↑
                            dimension_yearly (ปีละครั้ง, dim_calendar)
cdc → process   (สายแยก — process gate อยู่บน CDC ของวันนั้น)
```

`initial` ในแผนภาพหมายถึงสร้าง raw ครั้งแรกเท่านั้น — รันทีละ action
`create_all_table_raw_<source>` ไม่ใช่ทั้ง tag (ดูคำเตือนด้านบน)

`view` ต้องรัน **หลัง** `fact_daily` เสมอ เพราะ view อ่านจาก dim/fact
`view` **ไม่อยู่ในตารางเวลาโดยตั้งใจ** — presentation views ใช้ [คู่มือ deploy](deploy-view.md)
ส่วน Pub/Sub export views ใช้ [export contract](../project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24)
ตารางเวลาจริง (05:45 / 06:00 / 08:55 / ปีละครั้ง) ดูที่
[running-and-troubleshooting § Schedule](../project_wiki/operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd)

## Query ตรงด้วย bq

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false '
SELECT COUNT(*) FROM `databuffet-nonprd.dimension_table.dim_company`'
```

- ต้องใส่ `--project_id=databuffet-nonprd` **เสมอ** (default project ของเครื่องเป็นตัวอื่น)
- บน Windows `bq`/`gcloud`/`gsutil` อยู่ใน **WSL เท่านั้น**:
  `wsl -e bash -lc "bq --project_id=databuffet-nonprd query ..."`
  (เข้าถึง repo ใน WSL ผ่าน `/mnt/d/github/data-buffet`)
- INFORMATION_SCHEMA ระดับ region ส่วนใหญ่โดน deny — ใช้ระดับ dataset:
  `` `databuffet-nonprd.<dataset>.INFORMATION_SCHEMA.COLUMNS` ``
  **ข้อยกเว้น**: `` `region-us-central1`.INFORMATION_SCHEMA.JOBS_BY_PROJECT `` อ่านได้
  ใช้ดู bytes ที่ถูกเรียกเก็บจริง (กรอง `parent_job_id IS NULL` เอาเฉพาะ job แม่)
- เขียน SQL ยาวลงไฟล์แล้ว pipe เข้าไป อย่า inline — backtick จะโดน shell กิน
  (`bash script.sh` ใน WSL ปลอดภัยกว่าการ inline ผ่าน PowerShell → WSL → bash)

## ตรวจ SQL โดยไม่มี dataform CLI

ถ้ามี CLI ใช้ SQL จาก `dataform compile --json`
(`.tables[].query`) ได้; ถ้าไม่มี CLI ให้ขยาย references เองตามตัวอย่าง

`--dry_run` ของ `bq` ตรวจ syntax + ชื่อคอลัมน์ได้ฟรี ไม่คิดเงิน:

```bash
# 1. ขยาย ${ref()} / ${XxxTableRef} เป็นชื่อเต็มเอง แล้วเซฟเป็น .sql
# 2. ยิง dry run
wsl -e bash -lc "bq --project_id=databuffet-nonprd query --use_legacy_sql=false --dry_run < q.sql"
```

เช็ค `partitionBy` ที่ config ประกาศว่ามีคอลัมน์จริงในผลลัพธ์ไหม — ครอบด้วย
`SELECT <partition_col> FROM ( <query> ) LIMIT 0` แล้ว dry run · ถ้าไม่มีจะได้
`Unrecognized name` ซึ่งคือ error เดียวกับที่ Dataform จะเจอตอนสร้างตาราง
**บทเรียนจริง 2026-09-03**: `fact_*_store` ทั้ง 3 ตัวถอดคอลัมน์ `asatdate` ออกแต่ลืมแก้
`partitionBy: "asatdate"` — จับได้ด้วยวิธีนี้ก่อนรันจริง

## ลำดับการไล่ปัญหา

1. compile ผ่านไหม (JS/config / dependency ผิด) — ตรวจด้วย `dataform compile` ถ้ามี CLI ([รันด้วย tag](#รันด้วย-tag)) หรือใน Dataform UI
2. ดู graph ว่า action ต่อกันถูกไหม
3. dry-run action ที่สงสัย (หรือ `bq --dry_run` ตามข้างบน)
4. ดู error ใน BigQuery Cloud Console (job history)
5. เช็ก `uniqueKey`/`pk_key` ตรงกันไหม (validated — ประกาศ 2 ที่ ต้องตรงกัน)
6. ดูประวัติการรันจากตาราง monitor — skill `check-runs`

## อาการที่เจอบ่อย

| อาการ | สาเหตุ/ทางแก้ |
|---|---|
| `Unrecognized name: <col>` ตอนสร้างตาราง | `partitionBy`/`clusterBy` ใน config ชี้คอลัมน์ที่ SELECT ไม่ได้คืนมา — ถอดคอลัมน์เมื่อไรต้องเช็ค config ด้วยเสมอ |
| `Octal escape sequences are not allowed in template strings` | มี `\1`–`\9` ใน **คอมเมนต์ `--`** ของ SQLX (คอมเมนต์ถูกประมวลเป็น template literal) — เขียน `\\1` ใน comment ส่วนโค้ด SQL ใช้ backslash เดี่ยวได้ ดู [coding-standard §3.3](../coding-standards/sqlx-coding-standard.md) |
| dim MERGE บอก table not found | ตาราง `operations` ต้องมีใน BigQuery ก่อนรันครั้งแรก Dataform ไม่สร้างให้ |
| dim ไม่เห็นข้อมูล mds ที่แก้ไปแล้ว | stable-key dimensions read a complete active-source snapshot on the daily run; check the action’s dependency and `is_active` filter. The active dimension definitions do not use `MDS_BACKFILL_DAYS`. |
| validated ขาดข้อมูลย้อนหลัง | window incremental = `BACKFILL_DAYS` (1 วัน, string compare `ASATDATE`) — เพิ่มค่าชั่วคราวใน `workflow_settings.yaml` แล้วรันรอบเดียว (รอบ schedule compile branch `nonprod` ตอน 05:45 — ถ้าจะให้รอบอัตโนมัติใช้ค่าใหม่ ต้อง commit ลง `nonprod` ก่อน 05:45) |
| บรรทัดที่ต้นทางลบไปแล้วยังค้าง | PK ระดับบรรทัด MERGE ลบให้ไม่ได้ — `mih`/`mil`/`mir`/`curated_mil` ใช้ doc-grain purge ใน `pre_operations` แล้ว ถ้าตารางใหม่มีอาการนี้ต้องทำแบบเดียวกัน |
| parse datetime fail | รูปแบบ timestamp จาก raw เปลี่ยน — `parseFlexibleDatetime` รองรับ 2 แบบ ถ้ามีแบบที่ 3 ต้องเพิ่ม |
| ALTER PRIMARY KEY fail ซ้ำ ๆ | BigQuery metadata ชนกัน — retry loop จัดการเอง ถ้ายัง fail ให้รันใหม่ |
| fact row ซ้ำ | grain ของ temp table ไม่ตรง DELETE key · หรือ join กับตารางที่มีรหัสซ้ำ (ใส่ `QUALIFY ROW_NUMBER() = 1` ฝั่ง dim ก่อน join) |
| Candidate dimension row is missing from the complete source but is referenced by a fact | Compare its SK with fact references before applying the delete. If a retained fact would keep the removed SK, hold the dimension and request a decision. |
| view บน BigQuery ไม่ตรงกับ repo | ยังไม่ได้รัน tag `view` หรือมีคนแก้บน console — ใช้ skill `bq-drift-scan` |

## Environment / Git

- Branch: `dev` → `nonprod` → `prod` (+ `hotfix`) · schedule compile `nonprod` ตอน 05:45
- งานเข้า `nonprod` ได้ 2 ทาง (ดู [release flow](../getting-started/onboarding.md#release-flow)):
  (i) branch `fm/*` → no-mistakes → PR เข้า `dev` → fast-forward `nonprod`
  (ii) commit ตรงบน `nonprod` ผ่านหน้า Dataform แล้ว merge กลับเข้า `dev`
  — และบางครั้งมี commit ตรงบน `dev` (ไม่ผ่าน PR) ทาง (ii) และ commit ตรงไม่ผ่าน
  pre-commit lineage gate และ doc-sync hook ต้อง regenerate lineage + อัปเดตเอกสารเองใน PR ถัดไป
- skill `ship` (commit → push `dev` → `--ff-only` `nonprod`) ใช้ได้เฉพาะตอน `nonprod`
  ไม่มี commit ของตัวเอง ถ้า ff ไม่ได้ ต้อง merge `nonprod` กลับเข้า `dev` ก่อน
- `workflow_settings.yaml` **ถูก track ใน git** — แก้แล้ว commit ร่วมกัน (ค่า
  `BACKFILL_DAYS` อยู่ในนี้)
- pre-commit hook regenerate แผนผัง lineage ให้อัตโนมัติ และ **บล็อกการ commit**
  ถ้า `generate_lineage.py` หาย/พัง
- PreToolUse hook บล็อกคำสั่งทำลายข้อมูล (`re-initial`, `drop_all_tables`,
  `--full-refresh`, DML/DDL ผ่าน `bq`, `gcloud delete`, `gsutil rm`, force-push)
  — ถ้าโดนบล็อก **อย่าหาทางเลี่ยง** ให้อธิบายแล้วให้เจ้าของงานตัดสินใจ

ดูเพิ่ม: [project_wiki/operations/running-and-troubleshooting.md](../project_wiki/operations/running-and-troubleshooting.md)
