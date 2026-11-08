# มาตรฐานการพัฒนา

อ่านมาตรฐานที่เกี่ยวข้องก่อนแก้ไข และตรวจ diff กับมาตรฐานก่อน commit

- [มาตรฐาน SQLX](sqlx-coding-standard.md) — โครงสร้าง SQLX, config, references, data cleaning, timezone และ dimension/fact
- [หลักเกณฑ์การตั้งชื่อ](naming-conventions.md) — ชื่อไฟล์ action, dataset, คอลัมน์ และตัวแปร

## กฎทั่วไป (ใช้กับทุกงาน)

- คงคำสะกด identifier ที่ใช้งานจริง: `fact_transcation`, `CDC_DATESET`, `prdDiminsionData`
- ทุกการเปลี่ยน `definitions/`, `includes/` หรือ `workflow_settings.yaml` ต้องประเมินผลต่อเอกสารก่อนจบงานตาม mapping ใน `.claude/skills/update-docs/SKILL.md`; ถ้ามีผลให้อัปเดต `document/` และ commit โค้ดกับเอกสารใน commit เดียวกัน ถ้าไม่มีผลให้แจ้งสั้น ๆ; บังคับด้วย Stop hook และมี pre-commit warning สำรอง
- OKF card เก็บเฉพาะข้อมูลตาราง; สร้าง/ปรับ/ลบ card ใน commit เดียวกับการเพิ่ม/เปลี่ยน/ลบตารางหรือวิว
