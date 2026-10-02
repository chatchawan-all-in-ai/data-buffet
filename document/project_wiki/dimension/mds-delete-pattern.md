# MDS Inactive-Row DELETE (tombstone) Pattern

> **LLM context**: ⚠️ Scope shrank on **2026-07-20**: 34 mds dims were converted to
> [full daily rebuild](full-rebuild-pattern.md) (rebuild from `is_active = TRUE`
> makes the tombstone unnecessary), so this pattern now applies to only the **2
> remaining MERGE dims: `dim_company` and `dim_aging_rang`**.
> (ตัวเลข 34 คือจำนวน ณ วันที่แปลง · ปัจจุบัน full-rebuild มี **43 ตัว** เพราะมี dim ใหม่เพิ่มหลังจากนั้น)
> History: implemented 2026-07-10 across all then-MERGE mds dims (commit `e64a62d`).
> Design decision: **hard DELETE, no downstream FK checks** — chosen explicitly over
> a soft-delete `IsActive` flag.

## The problem it solves

Every mds-sourced dim MERGE filters `WHERE t1.is_active = TRUE`. Rows deactivated at
the mds source (soft-deleted) therefore stayed in the dimension forever — the dim
never saw them again.

## The pattern

Placed as the **last statement before `END;`** of the mds MERGE block:

```sql
  DELETE FROM `${Dim<Name>TableRef}`
  WHERE MdsID IN (
    SELECT id FROM `${MdsSourceTableRef}` WHERE is_active = FALSE
  );
END;
```

Properties:

- **No date filter** — intentionally scans the whole mds table so rows deactivated at
  any time are removed (mds masters are small reference tables).
- **NULL-safe by construction**: `WHERE MdsID IN (subquery)` never matches rows with
  `MdsID IS NULL` — this protects placeholder rows such as `dim_stk_mkt`'s
  'Waiting Master' rows (inserted with `MdsID = NULL`).
- **No downstream checks**: facts referencing a deleted SK keep the orphan value.
  Accepted risk per the 2026-07-10 decision; a full live scan of 172 SK relationships
  (fact_table, dimension_table, bridge_dataset, process_dataset) found **0 dangling
  SK-FKs** at implementation time.

## Where it applies — **2 ไฟล์เท่านั้น** (ตรวจซ้ำ 2026-09-15)

หลังการแปลงเป็น full rebuild เมื่อ 2026-07-20 **เหลือ dim ที่ต้องมี tombstone DELETE แค่ 2 ตัว**
คือ dim ที่ยังใช้ MERGE กับ mds:

| File | ทำไมยังต้อง MERGE |
|---|---|
| `dim_company` | CompanySK ถูก persist ไว้ทั่วทั้ง warehouse |
| `dim_aging_rang` | AgingRangSK ถูกแช่แข็งใน `dim_aging_history` |

**dim ที่อ่าน mds อีก 43 ตัวไม่ต้องมี tombstone** — เพราะอ่านเฉพาะ
`is_active = TRUE` ทั้งตารางทุกคืน แถวที่ต้นทาง soft-delete จึงหายเอง
ดู [full-rebuild-pattern.md](full-rebuild-pattern.md)

ตรวจซ้ำได้ทุกเมื่อ:

```bash
grep -l "is_active *= *FALSE" definitions/dimension/*.sqlx
# ต้องได้แค่ dim_company.sqlx กับ dim_aging_rang.sqlx
```

> ประวัติ: ชุดแรก 2026-07-10 ครอบคลุม 35 ไฟล์ และตก `dim_rebate` ไป เพราะ grep
> หา literal `"mds_dataset"` มองไม่เห็น · ต่อมาขยายเป็น 36 ไฟล์ ก่อนจะยุบเหลือ 2
> ตอน 2026-07-20 · **บทเรียนที่ยังใช้ได้**: grep หา `mds_data_` ทั้งไฟล์ ไม่ใช่แค่
> `name:` หรือ literal `"mds_dataset"` — dim ชุด MDT อ้างผ่าน const ใน `js {}`

Exclusions:
- **`dim_change_district`** — mds-sourced but `type: "table"` full rebuild; the
  `WHERE is_active = true` filter already drops inactive rows every run.
- **`dim_sale_representative` block 2** — the fallback-reps MERGE from
  `validated_mac5.per` has no MdsID; the DELETE lives at the end of **block 1 only**.
- Lake-sourced dims (group b) — no mds master to tombstone against.

## Consequences to remember

| Scenario | Outcome |
|---|---|
| mds row set `is_active = FALSE` | Dim row hard-deleted on next daily run |
| Same row later reactivated | Re-inserted with a **new SK** (old SK is gone) |
| Fact rows holding the deleted SK | Orphaned (accepted); daily full-rebuild dims (`dim_target_product_group_by_sale*`) self-heal |
| Placeholder rows (`MdsID IS NULL`) | Never deleted (IN-subquery can't match NULL) |
