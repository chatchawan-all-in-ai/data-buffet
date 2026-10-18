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
GCS AVRO/CSV (gs://file-raw-data)
  → initial   (external table + UDF 7 ตัว + ไฟล์ drop — ⚠️ อย่ารัน tag `initial` ทั้ง tag)
  → validated (ทำความสะอาด cast dedup — 1 ไฟล์ต่อตารางต้นทาง + schema 1 ไฟล์ต่อ source)
  → curated   (business logic, join)
  → dimension + fact
  → view      (ชั้น BI/report)
  ท่อเสริม: cdc (จับ change) + process (แกะที่อยู่ไทยด้วย AI + RLS)
```

จำนวนไฟล์ทุกชั้นดู [lineage ที่สร้างจากโค้ด](../diagrams/pipeline_lineage.md#1-layer-overview)

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
.claude/             ชุดทำงานของ Claude Code (git-ignored รับจากทีมโดย copy — ดู §4)
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
| Python 3.x | hooks และ `document/diagrams/generate_lineage.py` ใช้; คำสั่ง no-mistakes ต้องมี `python3` ฝั่ง Linux/WSL ที่สร้าง venv และใช้ pip ได้ |
| git | branch: `dev` (ทำงาน) → `nonprod` → `prod` |
| Node.js 20+ (มี `npm`) | คำสั่ง no-mistakes ต้องใช้ Node/npm ฝั่ง Linux/WSL (`node --version`, `npm --version`) |
| Dataform CLI global (ทางเลือก) | `npm install -g @dataform/cli@3.0.0` · เวอร์ชัน**ต้องตรง** `dataformCoreVersion` ใน `workflow_settings.yaml` · เช็ก: `dataform --version` · ไม่จำเป็นสำหรับคำสั่งใน [README — Common Commands](../../README.md#common-commands); ดู [คู่มือตรวจงานและข้อจำกัด CLI](../how-to/run-and-debug.md#ตรวจงานในเครื่องด้วย-no-mistakes) |

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
| Hooks | `.claude/hooks/` | `ensure-hookspath.sh` (SessionStart — ตั้ง `core.hooksPath` + `chmod +x` ให้เองครั้งแรก), `guard-dangerous.sh` (บล็อกคำสั่งทำลายข้อมูล), `doc-sync-check.sh` (กันลืมอัปเดตเอกสาร), `pre-commit.sh` (เตือน doc-sync + regenerate diagram — **block commit ถ้า regenerate ไม่ผ่าน**; ไม่มี CI สำรองแล้วตั้งแต่ 2026-08-27; ขั้น `dataform format`/`compile` ถูกถอดออก 2026-09-23 — การตรวจในเครื่องดู [run/debug guide](../how-to/run-and-debug.md#ตรวจงานในเครื่องด้วย-no-mistakes)) |
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
4. ตรวจ compile ในเครื่องตาม [README — Common Commands](../../README.md#common-commands); SQL dry run เลือก committed changes ตาม [ข้อจำกัดผลตรวจ](../how-to/run-and-debug.md#compile-กับ-sql-dry-run)
5. อัปเดต `document/` ถ้าการแก้กระทบ pattern/inventory
6. ส่งงานเข้า `dev` แล้วเข้า `nonprod` ตาม [Release flow](#release-flow) ด้านล่าง
   (ขึ้น prod: [../operations/deploy-to-prod.md](../operations/deploy-to-prod.md))

### Release flow

`nonprod` คือ branch ที่รอบอัตโนมัติใช้ — release config `production` compile `nonprod`
ทุกวัน 05:45 แล้วรัน 06:00 / 08:55 (ดู
[running-and-troubleshooting § Schedule](../project_wiki/operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd))
อะไรที่ไม่อยู่บน `nonprod` ก่อน 05:45 จะไม่ถูกรันในรอบเช้านั้น

งานเข้า `nonprod` ได้ **2 ทาง** (ตรวจจาก git history 2026-10-18):

| ทาง | ขั้นตอน | ด่านตรวจที่ผ่าน |
|---|---|---|
| **(i) ผ่าน PR** | branch `fm/*` → pipeline no-mistakes (review, test/lint ตาม `.no-mistakes.yaml`, docs) → PR เข้า `dev` → merge → fast-forward `nonprod` ให้เท่า `dev` | review ของ no-mistakes + review ใน PR · ต้อง regenerate lineage และอัปเดต `document/` ใน PR เอง |
| **(ii) แก้ตรงบนหน้า Dataform** | เพื่อนร่วมทีม commit บน `nonprod` ผ่าน workspace ของ Dataform (repo default branch) → ภายหลัง merge กลับเข้า `dev` ด้วย commit `Merge branch 'nonprod' into dev` | **ไม่ผ่าน** pre-commit lineage gate และ doc-sync hook (ไม่ได้ commit จากเครื่องที่มี `.claude/hooks`) |

นอกจากนี้ยังมี commit ตรงบน `dev` โดยไม่ผ่าน PR ด้วย (เช่น `7819bef` "add journal to raw,
validated" แล้ว merge เป็น `Merge branch 'dev' into dev`) — ด่านตรวจเหมือนทาง (ii) คือไม่มี
gate ใดรัน ถ้าทำจากเครื่องที่ไม่ได้ตั้ง `core.hooksPath`

ผลที่ต้องรู้:

- หลังมีงานทาง (ii) หรือ commit ตรง แผนผัง lineage และเอกสารอาจตามโค้ดไม่ทัน —
  PR ถัดไปที่แตะเรื่องนั้นควร regenerate `document/diagrams/` และอัปเดต `document/` ด้วย
- skill `ship` (commit → push `dev` → `git merge dev --ff-only` เข้า `nonprod`) ใช้ได้เฉพาะตอน
  `nonprod` ไม่มี commit ของตัวเอง ถ้า `--ff-only` ไม่ผ่าน skill จะหยุด — ต้อง merge `nonprod`
  กลับเข้า `dev` ก่อน (ให้เจ้าของงานตัดสินใจ ห้าม force push / rebase)
- ก่อนแก้ไฟล์ใด ให้ `git fetch` แล้วดูว่า `nonprod` มี commit ที่ยังไม่อยู่ใน `dev` หรือไม่

### การรีวิวงานของทีม

ก่อน commit หรือ deploy งานที่แตะ `definitions/` / `includes/` มีตัวช่วยรีวิว 2 ชั้น:

1. **workflow `review-dataform-change`** (`.claude/workflows/review-dataform-change.js` — มากับชุด
   copy `.claude/` ไม่ได้อยู่ใน git): รีวิวแบบอ่านอย่างเดียวบน diff ที่ยังไม่ commit
   ขั้นตอน Scope (อ่าน `git diff` + `dataform compile --json` เลือก lens ตามสิ่งที่ diff แตะ) →
   Review (logic, standard, compile, downstream, data-impact, doc-sync) → Verify (มีคนค้านทุก
   finding) → Sweep (หาค่าเก่าที่ซ้ำอยู่ที่อื่นใน repo) · สั่งใน Claude Code ว่า "run workflow
   review-dataform-change" · ค่า `scratch` เริ่มต้นเป็น path temp ของ Windows ถ้ารันใน WSL
   ให้ส่ง `scratch` เป็น path ของ Linux
2. **pipeline no-mistakes** (ทาง (i)): review โค้ด + test/lint + docs ก่อนเปิด PR เข้า `dev`

งานทาง (ii) ไม่ผ่านทั้งสองชั้น — ถ้าแก้บนหน้า Dataform ให้รัน workflow รีวิวจากเครื่องตัวเอง
บน branch ที่ดึงงานนั้นมาก่อน merge กลับ `dev`

## 6. กติกาที่ห้ามพลาด

1. **Timezone Bangkok เสมอ** — `CURRENT_DATE('Asia/Bangkok')`
2. **การทำความสะอาด string และข้อยกเว้นสำหรับ incremental key** — ดู [coding-standard §4](../coding-standards/sqlx-coding-standard.md#4-การ-cast--ทำความสะอาดข้อมูล)
3. **SK มี 2 ระบบ** — dim แบบ MERGE (`dim_company`, `dim_aging_rang`, lake dims):
   SK คงที่ตลอดชีพ ห้าม regenerate / dim mds แบบ full rebuild: SK ออกเลขใหม่
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
