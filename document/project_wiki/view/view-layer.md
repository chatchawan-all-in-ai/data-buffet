# View Layer (`definitions/view/`)

> **LLM context**: The presentation layer — BigQuery **views** that sit on top of the
> physical dim/fact/curated/validated tables (and a few external sources). Migrated
> into Dataform on **2026-07-24** from views that previously lived only in BigQuery
> (created by hand in the console). **34 views**, `type: "view"`, tag `view`. นับ 2026-09-28 (+`view_dim_calendar`)
>
> **Non-obvious constraints:**
> - **A view's folder is not its dataset.** Files live under `definitions/view/<dataset>/`
>   purely for organization; the BigQuery target is set by `config.schema` and **must
>   stay the original dataset** (`dimension_view`, `fact_view`, `onetime`,
>   `process_dataset`, `bridge_dataset`) so Power BI / downstream consumers that point
>   at those datasets keep working.
> - Views are **logical** — `CREATE OR REPLACE VIEW` stores no data. Correctness at
>   query time depends on the underlying *tables* having data, not on when the view DDL
>   ran. This is why an existing table (`fact_transcation`) can read a view
>   (`dimension_view.view_dim_channel`) without a Dataform dependency and still work.
> - `dependencies[]` lists only Dataform actions that are **not** read through `${ref()}`
>   — i.e. dims, facts and upstream views (unique `.sqlx` basenames). Two exclusions:
>   1. **`validated_*` / `curated_*` are read via `${ref()}` and must NOT be listed**
>      — Dataform wires those edges itself (double-listing is banned by coding-standard §10).
>   2. Things this repo does not build are interpolated but not listed (they pre-exist):
>      `mds_dataset.*`, `onetime.mapping_invoice`,
>      `process_dataset.mih_address_data`, UDFs (`function_dataset.fn_*` — created together
>      by `create_all_function`, not separate actions), and `dim_districts`, `dim_provinces`,
>      `dim_geographies`, `dim_sub_districts`, `dim_aging_history`.
>   3. **`process_dataset.rls_customer360` และ `dim_rebate` ไม่ได้อยู่ในข้อ 2 แล้ว**
>      (แก้ 2026-08-11) — ทั้งคู่ repo สร้างเอง (`definitions/process/rls_customer360.sqlx`,
>      `definitions/dimension/dim_rebate.sqlx`) จึงต้องอยู่ใน `dependencies[]`
>      เอกสารเดิมเขียนชื่อผิดเป็น `RLS_Customer360` (ตัวใหญ่) และ `dim_product_rebate`

## Pattern

Blocks in fixed order: `config` → `js` (optional) → SQL body. References follow the
project-wide two-tier rule in
[coding-standards/sqlx-coding-standard.md §3](../../coding-standards/sqlx-coding-standard.md):
**`${ref()}` for validated/curated, js-block `TableRef` for everything else.**

```js
config {
  type: "view",
  schema: databuffet.DIMENSION_VIEW,          // original target dataset — DO NOT change
  dependencies: ["dim_company"],              // NON-ref() repo actions only (dims/facts/views)
  tags: [databuffet.TAG_VIEW],
}

js {
    const DimCompanyTable = {
        database: databuffet.DATABASE,
        schema: databuffet.DIMENSION_TABLE,
        name: "dim_company",
    };
    const DimCompanyTableRef = `${DimCompanyTable.database}.${DimCompanyTable.schema}.${DimCompanyTable.name}`;
}

SELECT ...
FROM `${DimCompanyTableRef}`                        -- dimension: js-block ref
LEFT JOIN ${ref(databuffet.CURATED_MAC5, "curated_mih")} AS mih   -- curated: ref()
```

Rules:
1. `validated_*` / `curated_*` → `${ref(databuffet.<CONST>, "<table>")}`, **no backticks**,
   and the table must **not** appear in `dependencies[]` (Dataform wires it).
2. Everything else → declare `<Pascal>Table` + `<Pascal>TableRef` in `js`, use
   `` `${XxxTableRef}` ``: repo dims/facts, other views, `process_dataset`,
   `mds_dataset`, `onetime` bases, `function_dataset`. Repo actions
   among these go in `dependencies[]` — including `rls_customer360`, which this repo
   does build (`type: "table"` in `process_dataset`).
3. No inline `` `${databuffet.DATABASE}.${databuffet.X}.tbl` ``, no `databuffet-nonprd`
   literal. Declarations follow first-use order; declare only what is used. A view that
   reads only validated/curated needs **no `js` block** — as of 2026-09-28 all 34 views
   happen to have one, so there is no live example.
4. No trailing `;` (the view DDL wraps the query).
4b. **Backslash ในโค้ด SQL ใช้ตัวเดียว** — Dataform ส่งผ่านให้ตรงๆ ไม่กิน
   ([coding-standard §3.3](../../coding-standards/sqlx-coding-standard.md)). `r'\d'`,
   `r'\1'`, `'\n'` เขียนแบบปกติได้เลย **ยกเว้นใน `--` comment ที่ต้อง double**
   (`\\1`) เพราะ comment ถูกประมวลผลเป็น JS template literal
   > ข้อนี้เคยเขียนกลับด้าน ("double ทุกที่") มาตั้งแต่ 2026-07-27 จากการอนุมาน
   > แก้เป็นฉบับนี้ 2026-08-10 หลังเปิด Compiled queries panel ดูของจริง — ดู
   > [known-issues.md](../../operations/known-issues.md) หัวข้อ backslash
5. Dataset → constant map is the same registry as everywhere else
   (`includes/controller/variables.json`).

### Snapshot table + regenerated SK → derive ที่ view (2026-08-11)

`view_dim_aging_history` เป็นเคสตัวอย่าง: ตารางต้นทาง `dim_aging_history` เป็น snapshot
สะสมที่ freeze `AgingSK`/`BillingSK` ไว้ แต่ต้นทางทั้งสอง (`dim_aging`, `fact_mir_vs`)
ปั้น SK ด้วย `ROW_NUMBER()` ใหม่ทุกคืน → เลขเก่าชี้คนละใบ 97%

แก้โดย **ทิ้งค่าที่เก็บไว้แล้ว join กลับหาต้นทางด้วย natural key ที่ snapshot เก็บไว้อยู่แล้ว**:

```sql
select
  cur_aging.AgingSK,
  cur_vs.BillingSK,
  dim_aging.* except(AgingSK, BillingSK)
from `${DimAgingHistoryTableRef}` as dim_aging
left join `${DimAgingTableRef}` as cur_aging
  on dim_aging.companyID = cur_aging.companyID
  and dim_aging.cfsVnosID = cur_aging.cfsVnosID
  and dim_aging.cfsTypeID = cur_aging.cfsTypeID
left join `${FactMirVsTableRef}` as cur_vs
  on dim_aging.companyID = cur_vs.company_id
  and dim_aging.cfsVnosID = cur_vs.mirbinvno
qualify row_number() over(partition by asatdate, dim_aging.companyID,
                          dim_aging.cfsVnosID, dim_aging.cfsTypeID
                          order by ChannelSK, cur_vs.BillingSK) = 1
```

ใช้ท่านี้ได้เมื่อ snapshot เก็บ natural key ครบ — ถูกกว่าการเปลี่ยน dim/fact ต้นทางเป็น
MERGE มาก (ไม่ต้องแตะ pipeline เลย) เหตุผลเต็ม + ตัวเลขที่วัดได้อยู่ใน
[known-issues.md](../../operations/known-issues.md) หัวข้อ "การตัดสินใจเชิงออกแบบ"

**ห้ามเอา `QUALIFY` ออก** — ต้นทางทั้งสองมีคีย์ซ้ำอย่างละ 1 คู่ ถ้าเอาออกแถวจะบาน

### `QUALIFY` ที่กันแถวบานใน view เหนือ fact (2026-08-11)

`view_fact_mir_vs` / `view_fact_mir_rs` join `dim_aging` ด้วย `cfsvnosid` + `company_id`
อย่างเดียว แต่ `dim_aging` มีได้หลายแถวต่อใบ (คนละ `cfsTypeID`) จึงต้องปิดท้ายด้วย

```sql
qualify row_number() over(partition by t1.BillingSK order by t2.AgingSK desc) = 1  -- vs
qualify row_number() over(partition by t1.ReceiveSK order by t2.AgingSK desc) = 1  -- rs
```

`QUALIFY` นี้ทำให้ view เป็น **1 แถวต่อ 1 SK** เท่ากับจำนวนแถวใน fact ต้นทางเป๊ะ
(1,234,886 / 1,733,446) ถ้าเอาออกจะเกินมา 2 และ 4 แถวตามลำดับ แล้วใครเอาไป `SUM`
จะได้ยอดเบิ้ล

> เคยแก้ไว้บน BigQuery console เท่านั้นและไม่ได้เข้า git — พบตอนสแกน drift 2026-08-11
> **ถ้ารัน tag `view` ตอนนั้นจะโดนเขียนทับหายทันที** ตอนนี้อยู่ใน `.sqlx` แล้ว

### Run order: ประกาศ dependency เป็น "ตาราง" ไม่ใช่ "view" (ตัดสินใจ 2026-08-11)

**กฎ**: ถ้าไฟล์หนึ่งอ่าน view ของอีก layer **ห้ามใส่ชื่อ view ใน `dependencies[]`**
ให้ใส่ **ตารางที่อยู่หลัง view นั้น** แทน

เหตุผล: view เป็น logical — พอตารางต้นทางรันเสร็จ view ก็ใช้งานได้ทันที ไม่มีอะไร
ต้อง "รัน" ให้เสร็จก่อน สิ่งที่ต้องรอจริงคือตาราง

ตัวอย่างที่ใช้กฎนี้:

| ไฟล์ | อ่าน view | ประกาศ dependency เป็น |
|---|---|---|
| `dim_customer` | `view_deb_address_data` | `deb_address_data` |
| `fact_transcation` | `view_dim_channel`, `view_deb_address_data` | `dim_channel_finance`, `dim_channel_sales`, `deb_address_data` (`dim_channel` + `dim_channel_cost` มีอยู่แล้ว) |

> ก่อนหน้านี้ 15 ไฟล์อ้างตารางของ repo ผ่าน js ref แต่ไม่ประกาศใน `dependencies[]`
> รวม 27 เส้น — เติมครบเมื่อ 2026-08-11 (เหลือ 3 เส้นที่เป็น view โดยตั้งใจตามกฎข้างบน)
> เส้นที่เสี่ยงที่สุดคือ `dim_target_product_group_by_sale(_dayofwork)` → `dim_*`/`dim_*_last`
> 13 เส้น เพราะ dims เหล่านั้นปั้น SK ใหม่ทุกคืน ถ้ารันสลับลำดับจะได้ SK ของเมื่อวาน
> ตรวจ timestamp แล้วที่ผ่านมาเรียงถูกตลอด — เป็นการกันไว้ ไม่ใช่แก้ของที่พังอยู่

## Inventory (34 views)

> นับตาม `config.schema` ไม่ใช่ชื่อโฟลเดอร์ — โฟลเดอร์ ≠ dataset ปลายทาง
> `DIMENSION_VIEW` 17 · `FACT_VIEW` 6 · `ONETIME` 5 · `PROCESS_DATASET` 5 · `BRIDGE` 1

### `dimension_view` → schema `DIMENSION_VIEW` (17)

| View | Key upstream (repo tables) | External refs (not deps) |
|---|---|---|
| `view_dim_aging` | dim_aging, dim_aging_rang, dim_sale_representative_last, view_dim_channel | — |
| `view_dim_aging_history` | view_dim_channel, dim_aging, fact_mir_vs | dim_aging_history |
| `view_dim_calendar` | dim_calendar | — · เพิ่ม 2026-09-28: `dim_calendar.*` + `LatestDateFilter` (ดูหัวข้อด้านล่าง) |
| `view_dim_channel` | dim_channel, dim_channel_cost, dim_channel_finance, dim_channel_sales | — |
| `view_dim_company` | dim_company | — |
| `view_dim_customer` | dim_customer, dim_group_customer | mds ×3, dim_districts/provinces/geographies/sub_districts |
| `view_dim_customer_credit_management` | dim_customer, dim_customer_grade | — |
| `view_dim_guarantee` | dim_customer, dim_guarantee | — |
| `view_dim_invoice` | dim_aging, dim_invoice | fn_flag_scg |
| `view_dim_order` | dim_order, mih2 | fn_order_type, mds_data_document_expire_rule_master |
| `view_dim_product_master` | dim_product_master, dim_product_mkt, dim_rebate, dim_waterpac | — |
| `view_dim_product_mkt` | dim_product_mkt, dim_product_mkt_director | — |
| `view_dim_sale_representative` | dim_department, dim_sale_representative | — |
| `view_dim_sale_representative_last` | dim_department_last, dim_sale_representative_last | — |
| `view_dim_target_by_agent` | dim_rate_target + 9 dims | — |
| `view_dim_target_by_agent_dayofwork` | dim_calendar + 8 dims | — |
| `view_sales_representative_last` | dim_department_last, dim_region_last, dim_section_last, view_dim_sale_representative_last | — |

### `fact_view` → schema `FACT_VIEW` (4)

| View | Key upstream | External refs |
|---|---|---|
| `view_fact_transcation` | fact_invoice, fact_order, fact_transcation, curated_mih, deb, ~20 dims, dim_pump_information, view_dim_aging, view_dim_invoice | onetime.mapping_invoice, fn_flag_scg/exc |
| `view_aging_ri` | fact_mir_vs, dim_aging_rang, dim_invoice, dim_status_not_receive, curated_mih, ar_s/chq/cql/mir, view_dim_aging | — |
| `view_fact_mir_rs` | fact_mir_rs, dim_aging, curated_mih, ar_s | — |
| `view_fact_mir_vs` | fact_mir_vs, dim_aging | — |
| `view_fact_salein_mdt` | fact_transcation, dim_customer, dim_sales_branch_mdt — ตัวเชื่อม sell-**in** (ขายเข้าห้าง) กับชุด MDT ที่เป็น sell-**out** | — |

### `onetime` → schema `ONETIME` (6 — data marts / Power BI / models)

| View | Key upstream | External refs |
|---|---|---|
| `Transaction_Data_Mart` | curated_mih/mil/tbook_quotation, dim_company, view_deb_address_data, stk, dim_rebate | fn_flag_sales_kpi |

> `view_fact_transcation` ไม่คำนวณ `NewProductMktSK` เองแล้ว (ย้ายไป `fact_transcation`
> 2026-08-26) แต่รับ **mapping-invoice override ของ `Change*SK` ทั้ง 5 ตัว** มาทำแทน
> (ย้ายมาจาก fact 2026-08-25) — ทั้งสองทิศทางสลับกันในสัปดาห์เดียว
> และเพิ่ม `PumpSK` จาก `dim_pump_information` (join ด้วย natural key 4 ตัว ไม่ใช่ SK:
> `CompanySK` + `IFNULL(milStk,'')` + `FlagNewProductMKT` + `IFNULL(RegionID,'')`)
| `Model_Invoice_Transaction` | 15 dims, view_fact_transcation, view_dim_customer | — |
| `Model_Target_DayOfWork` | 11 dims | — |
| `Product_Attribute` | dim_company, dim_product_master, stg, stk, mastersku ×4 | — |
| `Product_Master_ALL` | dim_product_master, dim_product_mkt_director, view_dim_product_mkt, Product_Attribute | — |

### `process_dataset` → schema `PROCESS_DATASET` (5)

| View | Key upstream | External refs |
|---|---|---|
| `view_deb_address_data` | deb_address_data | dim_districts/provinces/sub_districts |
| `view_mih_address_data` | — | mih_address_data (no .sqlx), dim geo ×3 |
| `view_rls_data` | dim_*_last ×6 | — |
| `view_rls_sale_data` | view_rls_data, rls_customer360 | mds |
| `view_rls_special_data` | rls_customer360 | mds ×2 |

### `bridge_dataset` → schema `BRIDGE` (1)

| View | Key upstream |
|---|---|
| `GroupCustomerSK_CustomerSK` | dim_customer, dim_group_customer |

## Not migrated

- **Test (3):** `temp_dim.fact_transcation`, `temp_dim.view_dim_aging`,
  `temp_dim.view_fact_transcation`.
- **`peem_using` dataset — excluded entirely (7):** the four
  `view_1..4_Product_DOS_CAT1*` (wrap externally-loaded `peem_using.Product_*` tables),
  plus `view_rls_data` / `view_rls_sale_data` / `view_rls_special_data` — the RLS trio
  in `peem_using` is a **personal test copy** of the `process_dataset` RLS views and is
  intentionally not managed by Dataform. (The canonical RLS views live in
  `process_dataset`.) No `PEEM_USING` dataset constant exists.

## `view_dim_calendar` — `LatestDateFilter` (dynamic page filter, 2026-09-28)

`dim_calendar.*` ทุกคอลัมน์ (ไม่แก้ `dim_calendar`) + คอลัมน์ BOOL `LatestDateFilter` ไว้ใช้เป็น
page filter "วันล่าสุด" ใน Power BI ทุก model — **ไม่ได้รวมยอด แค่กรองวันที่**

- **กฎ (แบบสะสม)**: TRUE เมื่อ `LastWorkDate <= Date <= Yesterday`
  - `Yesterday` = `CURRENT_DATE('Asia/Bangkok') - 1` — ข้อมูลเข้าแบบ day −1
  - `LastWorkDate` = วันทำงานล่าสุดที่ `<= Yesterday` → ปกติ = เมื่อวานวันเดียว; ถ้าเมื่อวานเป็นวันหยุด
    จะสะสมย้อนไปเรื่อย ๆ จนถึงวันทำงานล่าสุด (รวมวันทำงานนั้นด้วย)
  - วันทำงาน = **จันทร์–ศุกร์** ที่ `HolidayFlag = 'No'` — เสาร์นับเป็นวันหยุดเสมอ (ทีมที่ดูรายงานหยุด
    แม้ระบบ/คลังยังมีข้อมูลเข้า และ `dim_calendar` นับเสาร์เป็นวันทำงาน) · ผู้ใช้ตัดสิน 2026-09-28
- **ตัวอย่าง** (วันที่เปิดรายงาน → filter): ส. 03/10/2026 → 02 · อา. 04/10 → 02, 03 · จ. 05/10 → 02, 03, 04 ·
  อ. 06/10 → 05 · พ. 14/10 → 12, 13 (13 = วันนวมินทร์) · จ. 26/10 → 22, 23, 24, 25 (23 = วันปิยะ) ·
  อ. 08/12 → 04, 05, 06, 07 (07 = หยุดชดเชย)
- ข้อมูลทุกวันถูกแสดงครบในวันทำงานถัดไป — วันศุกร์ไม่หลุด เพราะเสาร์/อาทิตย์สะสมต่อจนถึงวันจันทร์
- **คิดจาก `dim_calendar` อย่างเดียว** — ตั้งใจไม่อิง fact (เช่น `MAX(mix_date)`) เพื่อให้ใช้ร่วมกันได้ทุก model
  ข้อแลก: ถ้า Dataform รอบคืนล้ม ธงยังชี้เมื่อวานทั้งที่ข้อมูลยังไม่เข้า
- `CURRENT_DATE` ถูกประเมินตอน query view → model แบบ Import ต้อง **refresh รายวัน** ธงถึงจะขยับ
- ขึ้นกับ `dim_holiday` — ถ้าวันหยุดปีไหนยังไม่ถูกบันทึก (ณ 2026-09-28 ปี 2027 = 0 วัน) วันนั้นจะถูกนับเป็นวันทำงาน

## Compile-verification checklist (local `dataform` CLI unavailable)

1. All 34 views compile and the `view` tag runs after the table-building tags.
2. Views referencing other views (chains — e.g. `view_dim_aging` → `view_dim_channel`,
   `Model_Invoice_Transaction` → `view_fact_transcation`) resolve in the right order.

## repo ล้ำหน้า BigQuery — ยังรอ deploy (สแกนล่าสุด 2026-09-15 ช่วงบ่าย)

**"ค้าง" = แก้ใน git แล้วแต่ view จริงบน BigQuery ยังเป็นของเก่า** เพราะเจ้าของงานเลือก
ไม่รัน Dataform ทั้ง tag แต่ไป `CREATE OR REPLACE VIEW` ทีละตัวบน BigQuery เอง

### ✅ 2026-09-15 — drift = 0 ทุกตัว

สแกนปิดท้ายวัน: **40 objects · 40 identical · 0 different** · `unbackticked = 0`
เป็นครั้งแรกที่ repo กับ BigQuery ตรงกันทั้งชั้น view + UDF

เคลียร์ไป **5 view ในวันเดียว**:

| view | ค้างมาตั้งแต่ | สิ่งที่ไม่เคยถึง BigQuery |
|---|---|---|
| `view_dim_aging_history` | 2026-08-11 (5 สัปดาห์) | derive `AgingSK`/`BillingSK` เอง — ปัญหา SK ชี้ผิด 97% |
| `Model_Invoice_Transaction` | 2026-04-16 (5 เดือน) | `LOWER(milstk) = LOWER(ProductCode)` |
| `Transaction_Data_Mart` | 2026-09-03 | `LOWER(s.stkcode) = LOWER(b.milstk)` |
| `view_fact_transcation` | 2026-08-26 | `LOWER()` 6 จุด + CustomerFlag ชนก่อน DepCode |
| `view_dim_invoice` | — | แก้ฝั่ง console ให้ตรง repo แทนการปล่อยต่างถาวร |

**บทเรียนที่ต้องจำ**: commit ≠ deploy · ชั้น view ไม่ได้ถูกรันพร้อม `fact_daily`
ถ้าไม่ใส่ tag `view` ในตารางเวลา งานที่ merge เข้า `dev` แล้วอาจไม่มีผลกับ BigQuery
**เป็นเดือน ๆ** โดยไม่มีอะไรเตือน — `Model_Invoice_Transaction` ค้าง 5 เดือน
`view_dim_aging_history` ค้าง 5 สัปดาห์ทั้งที่แก้บั๊ก SK ชี้ผิด 97%
รัน skill `bq-drift-scan` เป็นระยะคือตัวจับเรื่องนี้

✅ **`dimension_view.view_dim_invoice` ตรงกันแล้ว** — เจ้าของงานแก้ฝั่ง BigQuery ให้เป็น
`clean_company_prefix(cust.debnamet)` ตามที่ repo เก็บไว้ (2026-09-15 ช่วงบ่าย)
จบเรื่องที่เคยจะปล่อยให้ต่างถาวร

จนกว่าจะ apply ครบทั้ง 3 **repo กับ BigQuery จะ drift** — ตรวจด้วย skill `bq-drift-scan`

> **สถานะ ณ 2026-09-10 (drift scan)**: ยังไม่ได้ deploy ทั้ง 3 — BigQuery ยังเป็นเวอร์ชัน
> ก่อน `LOWER()` (last_modified 2026-08-26 / 2026-04-16) ส่วน repo commit ไปตั้งแต่ 2026-09-03

## `view_dim_aging_history` — เคยค้าง 2026-08-11 → **deploy แล้ว 2026-09-15** ✅

การแก้ "derive `AgingSK`/`BillingSK` แทนการเชื่อค่าใน snapshot" (หัวข้อด้านบน) commit
เข้า git เมื่อ 2026-08-11 แต่ **ไม่เคย deploy** — view จริงบน BigQuery ยัง last_modified
2026-07-20 และยังใช้ `dim_aging.*` + `qualify ... partition by asatdate, AgingSK` แบบเดิม
แปลว่าปัญหา SK ชี้ผิด 97% **เกิดอยู่จริงบน BigQuery ตลอด 5 สัปดาห์** (similarity ตอนสแกน
= 0.462 ต่ำสุดในทั้ง repo) · เจ้าของงานรัน view นี้เมื่อ 2026-09-15 11:08 แก้ไปแล้ว
**บทเรียน**: commit แล้วไม่ได้แปลว่า deploy — ชั้น view ต้องรัน tag `view` หรือ
`CREATE OR REPLACE VIEW` เองทุกครั้ง ไม่งั้นแก้ไปก็ไม่มีผล

## Pull กลับจาก BigQuery — 2026-09-10

| object | ทิศทาง | ทำอะไร |
|---|---|---|
| `dimension_view.view_dim_order` | BigQuery ล้ำหน้า (console edit 2026-09-10 13:57) | pull เข้า repo: เพิ่มคอลัมน์ `FlagExpire` + join `mds_data_document_expire_rule_master` ด้วย `lower(left(mihVnos,2)) = lower(DocPrefix)` |
| `dimension_view.view_dim_invoice` | ต่างกันแต่ผลลัพธ์เท่ากัน | console ถอด qualifier เป็น `clean_company_prefix(debnamet)` — repo คงรูป `cust.debnamet` ไว้ (ชัดกว่า และกัน ambiguous ในอนาคต) |

> **ที่จงใจไม่ดึงเข้า repo**: `fact_view.view_fact_saleout_pc_mdt` (สร้างบน BigQuery
> 2026-09-10 07:31) **ยัง dev อยู่** — เจ้าของงานขอให้ปล่อยไว้บน console ก่อน อย่าเพิ่ง
> สร้าง `.sqlx` และอย่านับรวมใน inventory จนกว่าจะนิ่ง (drift scan จะรายงานเป็น
> "extra in BigQuery" ทุกรอบ — ถูกต้องแล้ว) ส่วน `onetime.PowerBI_Data_Buffet_Transaction`
> ถูกย้ายไป `backup/` ตั้งใจแล้วเมื่อ 2026-09-03 — ไม่ต้องดึงกลับเช่นกัน

## Pull กลับจาก BigQuery — 2026-09-15

สแกนเจอต่าง 6 จาก 33 view · 4 ตัวเป็น "repo ล้ำหน้า" (ตารางด้านบน ไม่ใช่ drift) ·
2 ตัวเป็น console edit ที่ไม่เคยเข้า git → **เจ้าของงานสั่ง "ยึดตาม BigQuery"** แต่ยกเว้น `view_dim_invoice` ที่สั่งให้คง `cust.debnamet` ไว้:

| object | console edit | ทำอะไร |
|---|---|---|
| `dimension_view.view_dim_order` | 2026-09-14 07:12 | `FlagExpire` เปลี่ยน `ELSE NULL` → **`ELSE 'No'`** — เป็นความต่างเชิงพฤติกรรมจริง เอกสารหน้านี้เคยบันทึกรอบ pull 2026-09-10 ไว้แล้ว แสดงว่า view นี้ถูกแก้บน console **ซ้ำรอบที่สอง** |
| `dimension_view.view_dim_invoice` | 2026-09-03 03:48 | **ไม่ pull** — ยืนยันให้ repo คง `clean_company_prefix(cust.debnamet)` ไว้ (ชัดกว่า กัน ambiguous ในอนาคต) ส่วน console ตอนนั้นเป็น `(debnamet)` · ผลลัพธ์เท่ากันอยู่แล้ว: ในขอบเขตนั้นมีแค่ `view_dim_customer` ที่มีคอลัมน์ `debnamet` (`dim_invoice` ไม่มี) · **จบด้วยการแก้ฝั่ง BigQuery ให้ตรงกับ repo แทน** (2026-09-15 ช่วงบ่าย) — ตอนนี้ scan ขึ้น identical ไม่ต่างอีกแล้ว |

ตรวจหลัง pull: `scan.py --check-backticks` → `unbackticked=0` · เหลือ literal path 1 จุดที่
`definitions/process/rls_customer360.sqlx` ซึ่ง**มีอยู่ก่อนแล้ว** ไม่ได้เกิดจากรอบนี้
