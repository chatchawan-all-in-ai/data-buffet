# How-to: รันและ Debug

> ตรวจกับ `includes/controller/variables.json` และโค้ดจริงเมื่อ 2026-09-15

## รันด้วย tag

```bash
dataform compile                      # ตรวจ JS/ref/dependencies/วน (ไม่รันจริง · ไม่ตรวจ SQL)
dataform run --dry-run                # ดูแผนก่อนรัน
dataform run --tags validated_incremental
dataform run --tags dimension_daily
dataform run --tags fact_daily
dataform run --tags view                           # ← ชั้น view (33 ไฟล์)
dataform run --actions validated_mac5.mih          # รันตัวเดียว
dataform run --actions validated_mac5.mih --include-deps
```

> ⚠️ ในเครื่องใช้ CLI ได้แค่ **`compile` / `format`** — ลงตาม
> [onboarding §3.2](../getting-started/onboarding.md) (`npm install -g @dataform/cli@3.0.0`
> ฝั่ง Windows เวอร์ชันตรง `dataformCoreVersion`) · **`run` ทำผ่าน Dataform UI บน GCP**
> (ไม่ได้ตั้ง `.df-credentials.json`) · เครื่องที่ยังไม่ได้ลง CLI ดูหัวข้อ "ตรวจ SQL โดยไม่มี CLI"

### Tag ทั้งหมด

**ใช้งานจริง**: `initial`, `re-initial` (⚠️ DROP ตาราง validated/curated ของ MAC5),
`validated`, `validated_full`, `validated_incremental`, `curated`,
`curated_full`, `curated_incremental` (เริ่มใช้กับชุด SALEOUT_MDT),
`dimension_daily`, `dimension_yearly` (`dim_calendar` ตัวเดียว), `fact_daily`,
**`view`**, `cdc`, `cdc_incremental`, `process`

**ประกาศไว้แต่ยังไม่ถูกใช้**: `dimension_monthly`, `fact_monthly`, `fact_yearly`

**ไม่มี tag `assertions`** — โปรเจกต์นี้ไม่มี Dataform assertion เลย
การตรวจคุณภาพข้อมูลทำด้วย skill `data-quality-check` แทน

### ลำดับที่ควรรัน

```
initial → validated → curated → dimension_daily → fact_daily → view
                                         ↑
                            dimension_yearly (ปีละครั้ง, dim_calendar)
cdc → process   (สายแยก — process gate อยู่บน CDC ของวันนั้น)
```

`view` ต้องรัน **หลัง** `fact_daily` เสมอ เพราะ view อ่านจาก dim/fact
ถ้าลืมใส่ `view` ในตารางเวลา view จะไม่ถูก deploy และ repo จะ drift จาก BigQuery เงียบ ๆ

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

`dataform compile` **ไม่ตรวจ SQL** (ทดสอบ 2026-10-02: ใส่คอลัมน์ที่ไม่มีจริง + พิมพ์ `FORM`
แทน `FROM` ยัง compile ผ่าน) — ต้องใช้ `--dry_run` ของ `bq` เสมอ ไม่ว่าจะมี CLI หรือไม่
ถ้ามี CLI เอา SQL จาก `dataform compile --json` (`.tables[].query`) ได้เลย ไม่ต้องขยายเอง

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

1. compile ผ่านไหม (syntax / dependency ผิด) — ทำใน Dataform UI
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
| dim ไม่เห็นข้อมูล mds ที่แก้ไปแล้ว | เกิน window `MDS_BACKFILL_DAYS` (1 วัน) — ใช้ skill `backfill-dimension` · **เฉพาะ dim แบบ MERGE 12 ตัว** dim full-rebuild 43 ตัวเห็นทันทีอยู่แล้ว |
| validated ขาดข้อมูลย้อนหลัง | window incremental = `BACKFILL_DAYS` (1 วัน, string compare `ASATDATE`) — เพิ่มค่าชั่วคราวใน `workflow_settings.yaml` แล้วรันรอบเดียว |
| บรรทัดที่ต้นทางลบไปแล้วยังค้าง | PK ระดับบรรทัด MERGE ลบให้ไม่ได้ — `mih`/`mil`/`mir`/`curated_mil` ใช้ doc-grain purge ใน `pre_operations` แล้ว ถ้าตารางใหม่มีอาการนี้ต้องทำแบบเดียวกัน |
| parse datetime fail | รูปแบบ timestamp จาก raw เปลี่ยน — `parseFlexibleDatetime` รองรับ 2 แบบ ถ้ามีแบบที่ 3 ต้องเพิ่ม |
| ALTER PRIMARY KEY fail ซ้ำ ๆ | BigQuery metadata ชนกัน — retry loop จัดการเอง ถ้ายัง fail ให้รันใหม่ |
| fact row ซ้ำ | grain ของ temp table ไม่ตรง DELETE key · หรือ join กับตารางที่มีรหัสซ้ำ (ใส่ `QUALIFY ROW_NUMBER() = 1` ฝั่ง dim ก่อน join) |
| SK ค้างใน fact หลัง mds ลบ | พฤติกรรมที่ยอมรับ (hard delete 2026-07-10) — dim full-rebuild จะหายเองวันถัดไป |
| view บน BigQuery ไม่ตรงกับ repo | ยังไม่ได้รัน tag `view` หรือมีคนแก้บน console — ใช้ skill `bq-drift-scan` |

## Environment / Git

- Branch: `dev` → `nonprod` → `prod` (+ `hotfix`)
- commit แล้ว push `dev` จากนั้น fast-forward `nonprod` (skill `ship`)
- `workflow_settings.yaml` **ถูก track ใน git** — แก้แล้ว commit ร่วมกัน (ค่า
  `BACKFILL_DAYS` อยู่ในนี้)
- pre-commit hook regenerate แผนผัง lineage ให้อัตโนมัติ และ **บล็อกการ commit**
  ถ้า `generate_lineage.py` หาย/พัง
- PreToolUse hook บล็อกคำสั่งทำลายข้อมูล (`re-initial`, `drop_all_tables`,
  `--full-refresh`, DML/DDL ผ่าน `bq`, `gcloud delete`, `gsutil rm`, force-push)
  — ถ้าโดนบล็อก **อย่าหาทางเลี่ยง** ให้อธิบายแล้วให้เจ้าของงานตัดสินใจ

ดูเพิ่ม: [project_wiki/operations/running-and-troubleshooting.md](../project_wiki/operations/running-and-troubleshooting.md)
