# Onboarding — เริ่มงานกับ Data-Buffet

คู่มือสำหรับ developer ใหม่ อ่านจบแล้วควรเข้าใจว่าโปรเจกต์ทำอะไร ต้องขอสิทธิ์อะไร
ตั้งเครื่องยังไง รันยังไง และแก้โค้ดตรงไหน

> **ทางลัด day 1**: ทำ §3 (สิทธิ์ + เครื่องมือ) → §4 (Claude Code) → รัน
> `bash .claude/skills/verify-setup/scripts/verify.sh` ให้ขึ้น `FAIL 0` → แล้วค่อยอ่าน §5 ต่อ

## 1. โปรเจกต์นี้คืออะไร

Data warehouse บน **Google BigQuery** (project `databuffet-nonprd`, region `us-central1`)
สร้างด้วย **Dataform 3.0.0** — โค้ดทั้งหมดเป็นไฟล์ `.sqlx` (SQL + JavaScript template)

ข้อมูลไหลตามชั้น (medallion → star schema):

```
GCS AVRO (gs://file-raw-data)
  → initial   (external table + schema + UDF 7 ตัว — 17 ไฟล์)
  → validated (ทำความสะอาด cast dedup — 136 ไฟล์ = 132 transformation + 4 schema)
  → curated   (business logic, join — 11 ไฟล์ = 7 transformation + 4 schema)
  → dimension (69 ไฟล์) + fact (15 ไฟล์)
  → view      (ชั้น BI/report — 34 ไฟล์)
  ท่อเสริม: cdc (จับ change) + process (แกะที่อยู่ไทยด้วย AI)
```

> จำนวนไฟล์ในเอกสารนี้นับ **ไฟล์ `.sqlx` ทั้งหมด** ส่วน `README.md` บางตารางนับเฉพาะ
> **transformation** (ไม่รวมไฟล์ `*_schema_*.sqlx` ที่ใช้ bootstrap dataset) ตัวเลข
> ต่างกันด้วยเหตุนี้ ไม่ใช่เอกสารขัดกัน

อ่านคำศัพท์ก่อน: [glossary.md](glossary.md)

## 2. โครงสร้าง repo

```
definitions/         โค้ดหลักทุก layer (แยกโฟลเดอร์ตามชั้น/ตาม source)
includes/
  databuffet.js      config hub — ทุกไฟล์ .sqlx เรียกผ่าน databuffet.*
  controller/
    variables.json   ชื่อ dataset + tag ทั้งหมด (แก้ที่นี่ ห้าม hardcode)
    function-data.js SQL helper (cleanString, castInt64, ...)
    cdc-config.json  ตารางที่เปิด CDC
workflow_settings.yaml  ตั้งค่า project (track ใน git — แก้แล้วติด commit)
.claude/             ชุดทำงานของ Claude Code (track ใน git — ดู §4)
backup/              สำเนาไฟล์เวอร์ชันเก่า (อย่าแก้)
document/            เอกสาร (โฟลเดอร์นี้)
```

## 3. สิทธิ์ + เครื่องมือ

### 3.1 บัญชี / สิทธิ์ที่ต้องขอ (ทำก่อนอย่างอื่น — รออนุมัติ)

| # | ขออะไร | จากใคร | เช็กว่าได้แล้วยังไง |
|---|---|---|---|
| 1 | สิทธิ์ GitHub repo `ALL-IN-AI-ASIA/data-buffet` (write) | admin ทีม | `git clone` ได้ |
| 2 | บัญชี `@dos.co.th` เข้าถึง GCP project `databuffet-nonprd` | admin GCP | เห็น project ใน console |
| 3 | Role บน `databuffet-nonprd` (ดูตารางล่าง) | admin GCP | `verify-setup` ผ่าน |
| 4 | สิทธิ์อ่าน bucket `gs://file-raw-data` | admin GCP | `gsutil ls gs://file-raw-data` |
| 5 | เข้าถึง Dataform repository/workspace บน console | admin GCP | เปิด [Dataform console](https://console.cloud.google.com/bigquery/dataform?project=databuffet-nonprd) แล้วเห็น repo |
| 6 | (ถ้าต้องดู prod) สิทธิ์อ่าน `databuffet-prd` | admin GCP | — |

**Role ที่ใช้จริงในทีมตอนนี้** (ตรวจจาก IAM policy เมื่อ 2026-08-16): dev ส่วนใหญ่ถือ
`roles/editor` ทั้งก้อน ส่วนคนที่ใช้แค่ query ถือชุด
`roles/bigquery.dataViewer` + `roles/bigquery.jobUser` + `roles/bigquery.metadataViewer`

**ชุดที่แนะนำสำหรับคนใหม่ (least privilege — ให้ admin ตัดสินใจ)**:

| Role | ใช้ทำอะไร |
|---|---|
| `roles/bigquery.dataViewer` | อ่านข้อมูลทุก dataset |
| `roles/bigquery.jobUser` | สั่ง query ได้ (ขาดตัวนี้ = query ไม่ออกแม้อ่าน schema ได้) |
| `roles/bigquery.metadataViewer` | ดู schema / INFORMATION_SCHEMA ระดับ dataset |
| `roles/dataform.editor` | แก้/รัน workspace บน Dataform |
| `roles/storage.objectViewer` (bucket `file-raw-data`) | ส่องไฟล์ AVRO ต้นทาง |

> เขียนข้อมูลลง BigQuery ตรง ๆ **ไม่ต้องมีสิทธิ์** — ทุกการเขียนไปทาง Dataform
> ถ้าต้องแก้ตาราง `type: "operations"` ที่ Dataform ไม่สร้างให้ ให้คุยกับเจ้าของ project ก่อน

### 3.2 เครื่องมือ

| เครื่องมือ | หมายเหตุ |
|---|---|
| `gcloud` + `bq` + `gsutil` (Cloud SDK) | query ตรง: `bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'` — **ต้องใส่ `--project_id` เสมอ** เพราะ default project ของเครื่องมักไม่ใช่ตัวนี้ |
| Python 3.x | hooks และ `document/diagrams/generate_lineage.py` ใช้ |
| git | branch: `dev` (ทำงาน) → `nonprod` → `prod` |
| Node.js 20+ (มี `npm`) | ใช้ลง Dataform CLI · Windows: ลงฝั่ง Windows (`node --version`) |
| Dataform CLI **3.0.0** (แนะนำ) | `npm install -g @dataform/cli@3.0.0` · เวอร์ชัน**ต้องตรง** `dataformCoreVersion` ใน `workflow_settings.yaml` · เช็ก: `dataform --version` · `dataform compile` ตรวจ JS/config, `ref()`, `dependencies` ที่ไม่มีจริง และ dependency วน ในเครื่องก่อน push (ไม่ต้องล็อกอิน) — **ไม่ตรวจ SQL** (ชื่อคอลัมน์ผิด, พิมพ์ `FORM` ก็ผ่าน) ต้องเอา SQL จาก `dataform compile --json` ไปยิง `bq --dry_run` ต่อ · Claude Code ใช้ตัวนี้ตรวจงานที่เขียนให้ — ไม่มีก็ทำงานได้ แต่ต้องไปดู compile ใน Dataform UI แทน · **run ยังทำผ่าน Dataform UI** (ไม่ได้ตั้ง `.df-credentials.json`) · `dataform format` แก้ไฟล์ทั้ง repo — รันเฉพาะตอนตั้งใจ |

**ถ้าใช้ Windows**: Cloud SDK ของทีมติดตั้งฝั่ง **WSL (Ubuntu)** ไม่ใช่ฝั่ง Windows
เพราะฉะนั้นสั่ง `bq` / `gcloud` / `gsutil` จาก terminal WSL (repo อยู่ที่
`/mnt/d/github/data-buffet`) ส่วน git + Claude Code ใช้ฝั่ง Windows ได้ปกติ

### 3.3 ล็อกอิน

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project databuffet-nonprd
```

### 3.4 ตรวจว่าเครื่องพร้อม

```bash
bash .claude/skills/verify-setup/scripts/verify.sh
```

เช็ก 13 อย่าง (git remote / branch / hooksPath / python / gcloud auth / bq / gsutil /
hooks ของ Claude Code) แล้วบอก `PASS` `FAIL` `SKIP` พร้อมวิธีแก้ทีละข้อ
รันฝั่ง Windows จะได้ `SKIP` ที่หัวข้อ GCP — รันซ้ำใน WSL เพื่อดูครบ
รายละเอียด: [.claude/skills/verify-setup/SKILL.md](../../.claude/skills/verify-setup/SKILL.md)

## 4. Claude Code

`.claude/` **ไม่ได้อยู่ใน git** (ตั้งใจ) — clone มาแล้วจะไม่มีโฟลเดอร์นี้
ต้อง **ขอจากคนในทีม** แล้ววางไว้ที่ root ของ repo

| ของ | อยู่ที่ | ทำอะไร |
|---|---|---|
| Project context | `CLAUDE.md` (root ของ repo — **อยู่ใน git** ตั้งแต่ 2026-09-01, มากับ clone เลย ไม่ต้อง copy) | สรุปสถาปัตยกรรม + กติกา ให้ Claude อ่านอัตโนมัติทุก session |
| Skills (16) | `.claude/skills/*/SKILL.md` | `add-*-table`, `dataform-run`, `check-runs`, `data-quality-check`, `fk-integrity-scan`, `bq-drift-scan`, `backfill-dimension`, `enable-cdc`, `update-docs`, `ship`, `verify-setup` — เรียกด้วย `/<ชื่อ skill>` |
| Agents (5) | `.claude/agents/*.md` | `dataform-expert`, `data-architect`, `bigquery-optimizer`, `data-quality-auditor`, `bq-drift-auditor` |
| Hooks | `.claude/hooks/` | `ensure-hookspath.sh` (SessionStart — ตั้ง `core.hooksPath` + `chmod +x` ให้เองครั้งแรก), `guard-dangerous.sh` (บล็อกคำสั่งทำลายข้อมูล), `doc-sync-check.sh` (กันลืมอัปเดตเอกสาร), `pre-commit.sh` (เตือน doc-sync + regenerate diagram — **block commit ถ้า regenerate ไม่ผ่าน**; ไม่มี CI สำรองแล้วตั้งแต่ 2026-08-27; ขั้น `dataform format`/`compile` ถูกถอดออก 2026-09-23 — สั่ง `dataform compile` เองก่อน commit (§3.2) หรือดูใน Dataform UI) |
| Permissions | `.claude/settings.json` | allowlist แบบอ่านอย่างเดียว — ของส่วนตัวใส่ `settings.local.json` (git ไม่เก็บ) |

### 4.1 การส่งมอบ `.claude/` (สำหรับคนที่ส่งให้)

แพ็กเฉพาะของที่ใช้ทำงาน — **ห้ามติด** `settings.local.json` (permission ส่วนตัวของ
เครื่องคนส่ง) ไปด้วย:

```bash
tar --exclude='.claude/settings.local.json' --exclude='__pycache__' -czf claude-setup.tar.gz .claude .mcp.json
```

> เอกสารสมัครงาน/CV และสไลด์ ย้ายออกไปอยู่ `FromAI/` (git ignore) ตั้งแต่ 2026-08-17
> แล้ว — ไม่อยู่ใต้ `.claude/` อีก จึงไม่ติดไปกับชุด copy โดยบังเอิญ

`.mcp.json` (ประกาศ MCP server ที่ใช้ร่วมกัน) ก็ไม่ได้อยู่ใน git เหมือนกัน — ไปพร้อมชุดนี้

> `ai_context/` ที่โผล่มาที่ root คือ scaffold ของ plugin `spk@inline` ไม่ใช่ของ repo
> ซ้ำกับ `document/project_wiki/` จึงใส่ `.gitignore` ไว้ตั้งแต่ 2026-08-26 — ลบทิ้งได้เลย
> (plugin จะสร้างกลับมาเองทุก session)

คนรับแตกไฟล์ที่ root ของ repo แล้วเช็กว่ามีครบ: `agents/` (5),
`skills/` (16), `hooks/` (5), `settings.json`, `.mcp.json`
(`CLAUDE.md` ไม่อยู่ในชุด copy แล้ว — มากับ `git clone` เอง)

### 4.2 หลังวาง `.claude/` แล้ว — **ตั้งให้อัตโนมัติแล้ว ไม่ต้องทำเอง**

เปิด Claude Code ที่ root ของ repo ครั้งแรก **SessionStart hook
(`.claude/hooks/ensure-hookspath.sh`) จะตั้งให้เองทันที**:

```
[data-buffet] ตั้ง core.hooksPath = .claude/hooks ให้อัตโนมัติแล้ว
[data-buffet] pre-commit จะ regenerate diagram ให้ตอน commit ที่แตะ definitions/
```

มันทำ 2 อย่าง: `git config core.hooksPath .claude/hooks` และ `chmod +x` ให้ไฟล์ hook
(สิทธิ์ execute หายตอน copy ข้ามเครื่อง) — รันซ้ำได้ ไม่พูดอะไรถ้าตั้งถูกอยู่แล้ว
และ**ไม่ทับ**ถ้าเครื่องนั้นตั้ง `core.hooksPath` เป็นค่าอื่นไว้ตั้งใจ

> **ทำไมต้องมี**: `.claude/` git-ignore ไว้ ส่งด้วยการ copy — git จะไม่ใช้ hook ข้างในจนกว่า
> จะตั้ง `core.hooksPath` เอง และตั้งแต่ลบ GitHub Action ทิ้ง (2026-08-27) hook ตัวนี้คือ
> **ตาข่ายเดียว**ที่กัน `pipeline_lineage.md` / `topic_flows.md` ไม่ให้ล้าสมัย
> เครื่องที่ลืมตั้งจะ commit diagram เก่าขึ้นไปแบบเงียบ ๆ

ถ้าไม่ได้ใช้ Claude Code (สั่ง git จาก terminal เปล่า ๆ) ต้องสั่งเองครั้งเดียว:

```bash
git config core.hooksPath .claude/hooks
chmod +x .claude/hooks/*.sh .claude/hooks/pre-commit .claude/skills/verify-setup/scripts/verify.sh
```

ถ้าไฟล์กลายเป็น CRLF ตอน copy ให้แปลงกลับเป็น LF ด้วย `dos2unix .claude/hooks/*.sh`
ไม่งั้น bash ฟ้อง `$'\r': command not found` แล้ว **guard จะเงียบไปเฉย ๆ** —
รัน `verify-setup` (§3.4) เพื่อจับกรณีนี้

ข้อควรรู้:

- `guard-dangerous.sh` บล็อก `re-initial`, `drop_all_tables`, `--full-refresh`,
  `bq` ที่มี DML/DDL, `gcloud delete`, `gsutil rm`, `git push --force`
  **ถ้าโดนบล็อก อย่าหาทางเลี่ยง** — ให้คนตัดสินใจแล้วรันเอง
- `doc-sync-check.sh` จะไม่ยอมให้จบ turn ถ้าแก้ `definitions/` หรือ `includes/`
  แล้วไม่แตะ `document/` (ดู mapping ใน `.claude/skills/update-docs/SKILL.md`)
- MCP: `.mcp.json` (มากับชุด copy ไม่ได้อยู่ใน git) เปิด `context7` ไว้ดู doc ของ
  library — Claude Code จะถามอนุญาตครั้งแรก ปฏิเสธได้ ไม่กระทบงานหลัก

## 5. Flow การทำงาน

1. แตกงานจาก branch `dev` (หรือแก้บน `dev` ตามธรรมเนียมทีม)
2. แก้/เพิ่มไฟล์ `.sqlx` ตาม pattern ของ layer นั้น — ดู [how-to/](../how-to/)
3. ตรวจว่าใช้ `databuffet.*` ไม่ hardcode ชื่อ dataset
4. `dataform compile` ในเครื่อง (ต้องได้ 0 error — ลง CLI ตาม §3.2) · ถ้ายังไม่ได้ลง push แล้วดู compile ใน Dataform UI
5. อัปเดต `document/` ถ้าการแก้กระทบ pattern/inventory
6. commit → push `dev` → merge เข้า `nonprod` เมื่อพร้อมทดสอบ
   (ขึ้น prod: [../operations/deploy-to-prod.md](../operations/deploy-to-prod.md))

## 6. กติกาที่ห้ามพลาด

1. **Timezone Bangkok เสมอ** — `CURRENT_DATE('Asia/Bangkok')`
2. **String ทุกตัวผ่าน `cleanString`** — `''` ต้องกลายเป็น `NULL`
3. **SK มี 2 ระบบ** — dim แบบ MERGE (`dim_company`, `dim_aging_rang`, lake dims):
   SK คงที่ตลอดชีพ ห้าม regenerate / dim mds แบบ full rebuild (43 ตัว): SK ออกเลขใหม่
   ทุกวัน **ห้ามเก็บข้ามวัน**
4. **ตาราง `type: "operations"` Dataform ไม่สร้างให้** — dim แบบ MERGE และ
   `fact_transcation` ต้องมีตารางอยู่ก่อน
5. **คำผิดที่ห้ามแก้** (เป็นชื่อจริงใน BigQuery): `fact_transcation`, `CDC_DATESET`,
   `prdDiminsionData`
6. dim mds แบบ MERGE (2 ตัว) ต้องจบด้วย DELETE row ที่ `is_active = FALSE` ก่อน `END;`
   (แบบ full rebuild ไม่ต้อง)

## 7. อ่านต่อ

| เรื่อง | เอกสาร |
|---|---|
| ภาพรวมสถาปัตยกรรม | [../architecture/overview.md](../architecture/overview.md) |
| มาตรฐานการเขียนโค้ด | [../coding-standards/sqlx-coding-standard.md](../coding-standards/sqlx-coding-standard.md) |
| วิธีเพิ่มตารางแต่ละ layer | [../how-to/](../how-to/) |
| รัน / debug | [../how-to/run-and-debug.md](../how-to/run-and-debug.md) |
| ขึ้น prod (runbook ทีละ step) | [../operations/deploy-to-prod.md](../operations/deploy-to-prod.md) |
| ปัญหาที่เจอบ่อย | [../operations/known-issues.md](../operations/known-issues.md) |
| Wiki ฉบับเต็ม (สำหรับคน + LLM) | [../project_wiki/README.md](../project_wiki/README.md) |
