# How-to — index งานทั้งหมด

> ตารางเดียวจบ: งานที่ต้องทำ → ใช้ skill ไหน → อ่านเอกสารหน้าไหน
> ตรงกับ `.claude/skills/` จริงเมื่อ 2026-09-15 (**16 skills**)

`skill` เรียกในแชทด้วย `/<ชื่อ skill>` · skill ที่ไม่มีคอลัมน์ "เอกสาร" คือขั้นตอน
อยู่ในตัว `SKILL.md` เองทั้งหมด ไม่ได้ย่อไว้ที่อื่น

## สร้าง / แก้ตาราง

| งาน | Skill | เอกสาร |
|---|---|---|
| เพิ่ม raw external table (ไฟล์ใหม่ลง GCS) | `add-initial-table` | [project_wiki/initial/initial-layer.md](../project_wiki/initial/initial-layer.md) |
| เพิ่มตาราง validated | `add-validated-table` | [add-validated-table.md](add-validated-table.md) |
| เพิ่มตาราง curated | `add-curated-table` | [add-curated-table.md](add-curated-table.md) |
| เพิ่ม dimension | `add-dimension` | [add-dimension.md](add-dimension.md) |
| เพิ่ม fact table | `add-fact-table` | [add-fact-table.md](add-fact-table.md) |
| เพิ่ม view (ชั้นนำเสนอ) | — | [add-view.md](add-view.md) |
| เปิด CDC ให้ตารางใหม่ | `enable-cdc` | [project_wiki/includes/cdc-config.md](../project_wiki/includes/cdc-config.md) |

## รัน / deploy

| งาน | Skill | เอกสาร |
|---|---|---|
| รัน / compile / dry-run ตาม tag | `dataform-run` | [run-and-debug.md](run-and-debug.md) |
| **deploy view ขึ้น BigQuery (ทำมือ)** | — | [deploy-view.md](deploy-view.md) |
| commit + push `dev` + ff `nonprod` | `ship` | [run-and-debug.md §Environment](run-and-debug.md) |
| ย้าย nonprd → prd | — | [operations/deploy-to-prod.md](../operations/deploy-to-prod.md) |
| backfill dim ย้อนหลังเกิน 1 วัน | `backfill-dimension` | [project_wiki/operations/running-and-troubleshooting.md](../project_wiki/operations/running-and-troubleshooting.md) |
| backfill validated/curated ย้อนหลัง | — | เดียวกัน (`BACKFILL_DAYS` ใน `workflow_settings.yaml`) |

## ตรวจ / debug

| งาน | Skill | เอกสาร |
|---|---|---|
| ไล่ปัญหาตอนรันพัง | — | [run-and-debug.md](run-and-debug.md) |
| ดูประวัติการรัน (fail / เวลา / bytes) | `check-runs` | [project_wiki/operations/running-and-troubleshooting.md](../project_wiki/operations/running-and-troubleshooting.md) |
| ตรวจคุณภาพข้อมูล (dup key, NULL, freshness) | `data-quality-check` | — |
| หา SK ที่ชี้ไปยัง dimension ที่ไม่มีอยู่ | `fk-integrity-scan` | — |
| เทียบ view/UDF บน BigQuery กับ repo | `bq-drift-scan` | [project_wiki/view/view-layer.md](../project_wiki/view/view-layer.md), [deploy-view.md](deploy-view.md) |
| เช็กเครื่องใหม่ครบไหม | `verify-setup` | [getting-started/onboarding.md](../getting-started/onboarding.md) |

## เอกสาร / สื่อสาร

| งาน | Skill | เอกสาร |
|---|---|---|
| sync `document/` หลังแก้โค้ด (**บังคับ**) | `update-docs` | [README.md](../README.md) §การดูแลเอกสารชุดนี้ |
| สรุปสิ่งที่คุยกันออกมาเป็นภาพเดียว | `show-me` | — |

## หน้าอ้างอิงที่ไม่ใช่ how-to แต่ใช้บ่อย

| เรื่อง | หน้า |
|---|---|
| ธงเชิงธุรกิจ (`FlagFree`, `FlagExpire`, `item_status`, `seq_condition`, ...) | [project_wiki/overview/business-flags.md](../project_wiki/overview/business-flags.md) |
| dim ไหนออก SK อะไร | [project_wiki/dimension/inventory.md](../project_wiki/dimension/inventory.md) |
| คำผิดที่ห้ามแก้ / หนี้เทคนิค / งานค้าง | [operations/known-issues.md](../operations/known-issues.md) |
| มาตรฐานเขียน `.sqlx` | [coding-standards/sqlx-coding-standard.md](../coding-standards/sqlx-coding-standard.md) |
