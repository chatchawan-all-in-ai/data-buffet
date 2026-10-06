# Sales Out MDT — Knowledge

> **LLM context**: ความรู้การทำงานทั้งหมดของโปรเจกต์ Sales Out MDT (ยอดขายออกจากห้างค้าปลีก
> HP/MH/GB/BT/TW (+DH) → BigQuery → Power BI) ผู้อ่านคือคนในทีม (DE/BI) และ AI
> เก็บไว้ในรีโปแต่**ไม่ push** (docs อยู่ local) · ตัวเลขทุกตัวระบุวันที่วัด ถ้าจะอ้างอิงให้วัดใหม่
> · ถ้าเอกสารกับโค้ดไม่ตรงกัน ให้เชื่อ**โค้ดบน dev ของ Dataform** แล้วแก้เอกสาร
>   (แต่เหตุผล/comment ให้อ่านจาก local repo — Dataform workspace ตัด comment ทิ้งตอน commit)

เริ่มเขียน 2026-10-06

## Routing — จะทำอะไร อ่านหน้าไหน

| บท | ไฟล์ | ใช้เมื่อ | สถานะ |
|---|---|---|---|
| 01 | [01-business.md](01-business.md) | อยากรู้ว่า Sales Out คืออะไร ห้างไหนบ้าง ใครใช้ | ร่าง รอตรวจ ❓ |
| 02 | [02-sources.md](02-sources.md) | แตะ raw ของห้างไหนก็ตาม / Airflow / GCS / ASATDATE | ร่าง รอตรวจ ❓ |
| 03 | [03-design.md](03-design.md) | ออกแบบหรือแก้ fact/dim, grain, นิยาม measure | ร่าง รอตรวจ ❓ |
| 04 | [04-mapping.md](04-mapping.md) | จับคู่สินค้า/สาขา/zone, แถวที่ map ไม่ได้ | ร่าง รอตรวจ ❓ |
| 05 | [05-pipeline.md](05-pipeline.md) | แก้ไฟล์ใน `definitions/**/saleout_mdt/` และ view ปลายทาง | ร่าง รอตรวจ ❓ |
| 06 | [06-reconcile.md](06-reconcile.md) | ตรวจยอดเทียบ BI/ห้าง | ร่าง รอตรวจ ❓ |
| 07 | [07-runbook.md](07-runbook.md) | ไฟล์ขาด, ห้างส่งช้า, ห้างใหม่เข้ามา | ร่าง รอตรวจ ❓ |
| 08 | [08-backlog-decisions.md](08-backlog-decisions.md) | งานค้าง + ใครตัดสินอะไรเมื่อไหร่ | ร่าง รอตรวจ ❓ |
| – | [sales-out-wbs.md](sales-out-wbs.md) | timeline/WBS เดิม (2026-08-24) | มีแล้ว |
| – | [saleout-mdt-backlog.md](saleout-mdt-backlog.md) | backlog ต้นฉบับ (ถึง 2026-09-29) — สถานะล่าสุดอยู่บท 08 | ประวัติ |
| – | [_from-cool-elion/](_from-cool-elion/) | ความรู้ที่ dev ไม่มี (comment ที่ Dataform ตัดทิ้ง, design fact รายเดือน, ทางเลือกที่ไม่ได้ใช้) | อ้างอิง |

## แหล่งความรู้ต้นทาง (ที่ใช้ประกอบการเขียน)

| ที่ | มีอะไร |
|---|---|
| `upstream/dev` (`definitions/**/saleout_mdt/`, dim/fact/view `*_mdt`) | โค้ดจริง — ยืนยัน @ `fe7afdf` 2026-10-06 |
| `~/Desktop/_Projects/SaleOut/saleout-drive/` | design/spec xlsx, kickoff deck, `target_saleout.xlsx` |
| `~/Downloads/Project_SaleOut/` | Requirement, Timeline, วิดีโอ req 2026-08-21, โน้ต Airflow ไฟล์ขาด, `saleout_check/*.sql` |
| Claude memory (เครื่องผู้ใช้) | quirks ของแต่ละห้าง, bridge บาร์โค้ด, ผลรีวิว 2026-09-08 |
| [saleout-mdt-backlog.md](saleout-mdt-backlog.md) | ไฟล์งานค้างตัวจริง (ย้ายมาจาก worktree cool-elion ซึ่งลบแล้ว 2026-10-06) → บท 08 |
| session "สรุปโปรแจก saleout" (2026-09-24) | สรุปทั้งโปรเจกต์ + ไล่โค้ด initial → validated 2.4 · ⚠️ ครึ่งแรกอ่านจาก worktree ที่ตามหลัง `upstream/dev` |
| session "ตรวจสอบ sale out บน dataform (fork 3)" | สถานะโค้ดล่าสุด (curated/DH/view) → ตอบ 7 ข้อแล้ว 2026-10-06 (ใส่ในบท 03, 05) |
