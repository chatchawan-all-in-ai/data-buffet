# How-to: รันและ Debug

> ตรวจกับ `includes/controller/variables.json` และโค้ดจริงเมื่อ 2026-09-15

## ตรวจงานในเครื่องด้วย no-mistakes

คำสั่งประจำอยู่ใน [README — Common Commands](../../README.md#common-commands)
และตั้งค่าไว้ใน [`.no-mistakes.yaml`](../../.no-mistakes.yaml) · ใช้ Linux/WSL
และเตรียมเครื่องมือตาม [onboarding §3.2](../getting-started/onboarding.md#32-เครื่องมือ)

### Environment ที่ใช้ซ้ำ

ทั้งสองคำสั่งเรียก [`scripts/_nm-env.sh`](../../scripts/_nm-env.sh) เพื่อติดตั้ง
`@dataform/cli` และ `@dataform/core` เวอร์ชันตรงกับ `dataformCoreVersion` ใน
`workflow_settings.yaml` พร้อม Python venv ที่มี `google-cloud-bigquery`
(เวอร์ชัน client pin ไว้ในสคริปต์) · รอบแรกต้องดาวน์โหลด dependencies;
รอบถัดไปที่ cache พร้อมและ version stamp ตรงจะใช้ของเดิม ไม่รัน npm/pip install

Cache สำหรับ **data-buffet เท่านั้น** อยู่ที่
`${XDG_CACHE_HOME:-$HOME/.cache}/fm-envs/data-buffet`
(ปกติ `~/.cache/fm-envs/data-buffet`) · เปลี่ยนได้ด้วย `NM_ENV_DIR` แต่ต้องคงแยก
จากโปรเจกต์อื่น · สคริปต์ตัด Windows PATH `/mnt/<drive>/...` ออก จึงต้องมี
Node/npm ฝั่ง Linux/WSL ไม่ใช้ CLI global ฝั่ง Windows และไม่เพิ่ม CLI ลง PATH global

Compile ใช้สำเนา `definitions/`, `includes/` และ config ใน staging directory
ชั่วคราว เชื่อมกับ dependencies ที่ cache ไว้ เพื่อไม่ให้ Dataform ติดตั้ง core ซ้ำ
ใน checkout · แต่ละ invocation มี compile output และรายชื่อไฟล์เปลี่ยนใน directory
ชั่วคราวของตัวเอง และลบเมื่อจบ ไม่แชร์ `compile.json`/`changed.txt` ระหว่าง worktree
ดู regression coverage ใน [`test_nm_commands.py`](../../scripts/test_nm_commands.py)

### Compile กับ SQL dry run

`nm-test.sh` ตรวจ JS/config, `ref()`, `dependencies` และ dependency cycle
พร้อมรายงานจำนวน action · ไม่ต้องมี credentials และไม่เรียก BigQuery
แต่ **compile ไม่ตรวจ SQL** เช่น ชื่อคอลัมน์ผิดหรือ `FORM` แทน `FROM`

`nm-lint.sh` ตรวจ whitespace โดยยอมรับ CRLF และ compile ก่อนตรวจ SQL:

- ค่าเริ่มต้นเลือก table/operation actions ที่ source เปลี่ยนใน **commits** ระหว่าง
  merge-base ของ `HEAD` กับ `origin/dev` ถึง `HEAD` ไม่รวมการแก้ที่ยังไม่ commit
- ถ้า `includes/` หรือ `workflow_settings.yaml` เปลี่ยน จะขยายเป็นทุก
  table/operation action · `--all` หรือไม่มี merge-base ก็เลือกทั้งหมด
- ตรวจ query แบบ full-refresh และ incremental พร้อม pre/post-operations ของ
  แต่ละ mode และตัด sequence ซ้ำเมื่อ SQL และ materialization context ตรงกัน
- ใช้ BigQuery client จาก cached venv กับ Application Default Credentials (ADC;
  ดู [onboarding §3.3](../getting-started/onboarding.md#33-ล็อกอิน)) · query jobs ใช้
  `dry_run=True` และปิด query cache ใน project `databuffet-nonprd` · action ที่ target
  project อื่นถูกปฏิเสธ · ไม่ execute SQL หรือเขียนข้อมูลใน BigQuery

Whitespace ตรวจ diff ช่วง merge-base ถึง `HEAD` เมื่อมี base; ใน mode `--all`
หรือไม่มี merge-base สคริปต์ลองตรวจเฉพาะ `HEAD~1` ถึง `HEAD` และไม่บล็อกเมื่อ
whitespace check ล้มเหลว จึงไม่รับรองว่า whitespace ผ่านในสองกรณีนี้

อ่านผลราย action และ summary เสมอ; exit code 0 อาจมี SQL ที่ยังไม่ได้ตรวจ:

| ผล | ความหมาย / exit status |
|---|---|
| `ok` | BigQuery dry run ตรวจ SQL ที่ส่งได้ ไม่รับรองการ materialize หรือผลข้อมูลจริง |
| `WARN` | Table/view ที่หาไม่พบต้องตรง project/dataset/name ของ target ใน compile graph (`tables`, `operations`, `assertions`) เท่านั้น จึงข้ามพร้อมเตือน; ไม่นับเป็น `ok` และไม่ทำให้ fail |
| `UNVERIFIED` | ไม่ส่ง sequence ที่มี post-operations เพราะต้องใช้ schema ของ target ที่เพิ่ง materialize; ข้าม script/control flow, temp-table SQL หรือ DDL ที่มี statement ตามหลังซึ่ง dry run ตรวจไม่ครบ; ไม่นับเป็น `ok` และไม่ทำให้ fail |
| `WARNING: SKIP` | ไม่พบ ADC เลย จึงข้าม SQL dry run ทั้งหมดพร้อมประกาศว่า SQL ยัง `UNVERIFIED`; compile ผ่านแล้ว และ exit 0 |
| `FAIL` / `REFUSED` | SQL error, missing source/typo ที่ไม่ใช่ graph target, client library หาย, credentials ผิดหรือ client error อื่น และ target project ที่ไม่อนุญาต ทำให้ exit ไม่เป็น 0 |

รายละเอียดขอบเขตอยู่ใน [`nm_dryrun.py`](../../scripts/nm_dryrun.py) และ
regression coverage ใน [`test_nm_dryrun.py`](../../scripts/test_nm_dryrun.py)
หากรายงานเตือนหรือยังไม่ได้ตรวจ ต้องตรวจ action นั้นเพิ่มเติมใน Dataform service
ก่อนถือว่าพร้อมรันจริง

## รันด้วย tag

**รันจริงผ่าน Dataform UI บน GCP** — โปรเจกต์ไม่ได้ตั้ง `.df-credentials.json`
สำหรับ CLI execution · สร้าง execution แล้วเลือก tag เช่น `validated_incremental`,
`dimension_daily`, `fact_daily`, `view` หรือเลือก action เดียว เช่น
`validated_mac5.mih` และรวม dependencies เมื่อต้องการ · คำสั่ง no-mistakes ข้างบน
ใช้ตรวจงานในเครื่องเท่านั้น

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
การตรวจคุณภาพข้อมูลทำด้วย skill `data-quality-check` แทน

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

สำหรับการตรวจอัตโนมัติใช้ [no-mistakes ข้างบน](#ตรวจงานในเครื่องด้วย-no-mistakes)
ถ้าต้องตรวจ query เองและมี CLI ใช้ SQL จาก `dataform compile --json`
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

1. compile ผ่านไหม (JS/config / dependency ผิด) — ตรวจในเครื่องตาม [README](../../README.md#common-commands) หรือใน Dataform UI
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
| dim ไม่เห็นข้อมูล mds ที่แก้ไปแล้ว | เกิน window `MDS_BACKFILL_DAYS` (1 วัน) — ใช้ skill `backfill-dimension` · **เฉพาะ dim แบบ MERGE** (2 mds + 10 lake) dim full-rebuild เห็นทันทีอยู่แล้ว |
| validated ขาดข้อมูลย้อนหลัง | window incremental = `BACKFILL_DAYS` (1 วัน, string compare `ASATDATE`) — เพิ่มค่าชั่วคราวใน `workflow_settings.yaml` แล้วรันรอบเดียว (รอบ schedule compile branch `nonprod` ตอน 05:45 — ถ้าจะให้รอบอัตโนมัติใช้ค่าใหม่ ต้อง commit ลง `nonprod` ก่อน 05:45) |
| บรรทัดที่ต้นทางลบไปแล้วยังค้าง | PK ระดับบรรทัด MERGE ลบให้ไม่ได้ — `mih`/`mil`/`mir`/`curated_mil` ใช้ doc-grain purge ใน `pre_operations` แล้ว ถ้าตารางใหม่มีอาการนี้ต้องทำแบบเดียวกัน |
| parse datetime fail | รูปแบบ timestamp จาก raw เปลี่ยน — `parseFlexibleDatetime` รองรับ 2 แบบ ถ้ามีแบบที่ 3 ต้องเพิ่ม |
| ALTER PRIMARY KEY fail ซ้ำ ๆ | BigQuery metadata ชนกัน — retry loop จัดการเอง ถ้ายัง fail ให้รันใหม่ |
| fact row ซ้ำ | grain ของ temp table ไม่ตรง DELETE key · หรือ join กับตารางที่มีรหัสซ้ำ (ใส่ `QUALIFY ROW_NUMBER() = 1` ฝั่ง dim ก่อน join) |
| SK ค้างใน fact หลัง mds ลบ | พฤติกรรมที่ยอมรับ (hard delete 2026-07-10) — dim full-rebuild จะหายเองวันถัดไป |
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
