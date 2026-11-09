# View Layer (`definitions/view/`)

### Sale-rep order windows (2026-10-28)

`view_fact_transcation.fact_transaction` derives internal `OrderDate` before the
`raw_table` join to `dim_sale_representative_last`, following the shared
[order-date lookup and matching contract](../fact/fact-layer.md#sale-rep-order-window-matching-2026-10-28).
The last-side join has no bill-date restriction: historical bills are reassigned
using the latest snapshot. Expected historical moves are recorded in
[known issues](../../operations/known-issues.md#2026-10-28--sale-rep-order-windows).
The existing t5/t6 invoice joins remain intact; `OrderDate` is removed before the
public view output. Other `_last` consumers keep their existing rules, including
the [customer-report TA policy](#customer-report-info--customer-segment-2026-10-01).

### Project / IsProject ใน `view_fact_transcation` (2026-11-09)

ที่มา: ประชุมทีม 5 พ.ย. 2026 · ระบบต้นทางไม่มีคอลัมน์ชื่อโครงการ จึงตัดจากหมายเหตุบิล
`mihdesc` (มีอยู่แล้วใน `fact_transcation` ไม่ต้อง join `dim_invoice`) คำนวณใน CTE `final`:

- **`Project`** = ช่วงแรก (คั่นด้วย `#`) ที่มีคำว่า `โครงการ` · **ไม่มีช่วงไหนมี = NULL** (บิลที่ไม่ใช่โครงการ
  ตัดสินใจ 2026-11-09 — เดิมใช้ช่วงแรก ทำให้ได้ `ลงร้าน`/`ส่งต่อ`/`สาขา…` ปนกับชื่อโครงการ) · ทิ้ง `คุณ` ที่อยู่หน้า
  `โครงการ` (เช่น `#คุณโครงการวิลล่าพลาโน่` → `โครงการวิลล่าพลาโน่`)
  - **ตัดที่อยู่ออก (2026-11-09)**: ช่วงที่มี `โครงการ` → เริ่มที่คำว่า `โครงการ` (ทิ้งคำนำหน้าเช่น `ส่ง`, `ลง`,
    เลขไซต์ `1200 `) แล้วตัดตั้งแต่ตัวบอกที่อยู่/คนติดต่อตัวแรกจนจบ: `ถนน แขวง ตำบล อำเภอ เขต จังหวัด ซอย หมู่ที่
    หมู่<เลข> (บ้าน)เลขที่ ติดต่อ โทร Tel ตามแผนที่`, ` คุณ` (ต้องมีช่องว่าง/วงเล็บนำหน้า — กัน `โครงการคุณาภัทร`),
    `ถ. ต. อ. จ. ซ. ม.` (ต้องมีช่องว่างนำหน้า — กัน `บมจ.`), เบอร์โทร, `12/3` · ตัดแล้วเหลือแค่ `โครงการ`
    (เช่น `โครงการ คุณสมชาย`) → ใช้ค่าก่อนตัด · `dim_invoice`: ค่าไม่ซ้ำของ Project 33,378 → 27,165
    เช่น `โครงการเพฟ บางนา (PAVE-BN)ถนนบางบ่อ-คลองด่าน แขวง/…` → `โครงการเพฟ บางนา (PAVE-BN)`
    - `เขต`/`จังหวัด` ตัดเฉพาะที่ขึ้นคำใหม่ (ช่องว่าง/วงเล็บ/`/` นำหน้า) — กัน `โครงการศาลจังหวัดพิษณุโลก` · `โทร`
      ตัดเฉพาะที่ตามด้วยเลข (`โทร.087…`) — กัน `โครงการเมโทรทาวน์` (เดิมได้ `โครงการเม`)
  - **โครงการแบบมีเลข (2026-11-09)**: ตัดแล้วเหลือแค่ `โครงการ <เลข>` → เอาชื่อข้างหน้ามาต่อ
    (ส่วนหลังเลขบ้าน/`เลขที่`/`คุณ`/`ส่ง` ตัวสุดท้าย, ทิ้ง `ซอย`/`อาคาร/` ท้าย) เช่น
    `314/83 หมู่บ้านพิศาลบางกระดี่โครงการ3 ซอย…` → `หมู่บ้านพิศาลบางกระดี่ โครงการ 3`,
    `หมู่บ้านฉัตรหลวง โครงการ 15/2 แขวง/…` → `หมู่บ้านฉัตรหลวง โครงการ 15/2` — เดิมหมู่บ้านคนละแห่งรวมเป็น
    `โครงการ 1` ค่าเดียวกัน · กระทบ 852 บิล · เหลือ `โครงการ <เลข>` ล้วน 59 แถว (ไม่มีชื่อข้างหน้าจริง)
  - **ที่อยู่ไม่มีคำนำหน้า (2026-11-09)**: `… คูคต ลำลูกกา ปทุมธานี 12130` → ตัดชื่อจังหวัด (77 จังหวัด + กรุงเทพฯ/กทม./อยุธยา)
    ที่ตามด้วยรหัสไปรษณีย์ 5 หลัก พร้อมคำไทยไม่เกิน 2 คำข้างหน้า · ตัดแล้วเหลือแค่ `โครงการ` → ไม่ตัด ·
    ตัด `แวะร้าน`/`ส่งต่อ` ท้ายชื่อ · ยุบช่องว่างซ้ำเป็นช่องเดียว (ชื่อเดียวกันไม่แตกเป็นหลายค่า)
- **ชื่อช่องฟอร์ม `อาคาร/โครงการ` (2026-11-09)**: ฟอร์มที่อยู่จัดส่งมีช่องชื่อนี้ — บิลส่งร้าน/ปั๊ม/บริษัทได้ Yes
  เพราะชื่อช่อง 1,273 บิล · js `ProjectDesc` แทนชื่อช่องเป็น `อาคาร/` ก่อนหา Project/IsProject **ยกเว้น**ค่าในช่อง
  (ถึง `ซอย`/`ถนน`/`ต.`/`แขวง`/`#`) มีคำบอกหมู่บ้านจัดสรร (`หมู่บ้าน ม. วิลล์ วิลล่า วิลเลจ ทาวน์ เฟส นิเวศ
  การ์เด้น โฮม ปาร์ค ซิตี้ คอนโด แกรนด์ ไพรด์ พฤกษา villa town park home garden city …`) — เก็บ Yes 161 บิล
  (เช่น `ดารินแกรนด์วิลเลจ`, `ศุภาลัยปาร์ควิว`) · เป็น No 1,112 บิล
- **`IsProject`** = `ProjectDesc` (mihdesc ที่ไม่นับชื่อช่องข้างบน) มีคำว่า `โครงการ` → `Yes` ไม่มี → `No` ซึ่งเท่ากับ `Project IS NOT NULL` เสมอ
  (`#` ไม่มีทางตัดกลางคำ) — ตรวจกับ `dim_invoice` แล้ว: No 1,548,256 แถว Project NULL ทั้งหมด · Yes 142,638 มีค่าทั้งหมด

เลือกแบบนี้ (ตัดสินใจ 2026-11-09) แทน "ช่วงแรกก่อน `#` ตรง ๆ" เพราะช่วงแรกมักเป็นคำสั่งส่งของหรือชื่อคนติดต่อ
(`#ส่งต่อ #โครงการ…`) — แบบตรง ๆ พลาดโครงการ 16,209 บิลใน `dim_invoice` · ไม่ข้ามช่วงคำสั่งส่งของแบบทั่วไป
เพราะบิล `ลงร้าน` จะได้ Project เป็นที่อยู่แทน · ผล ณ วันที่ทำ: fact 2,732,499 แถว · Yes 116,301 (4.26%) ·
หลังรอบ audit (2026-11-09): บิล Yes 54,407 → 53,295 · ชื่อเปลี่ยน 4,737 บิล · ค่าไม่ซ้ำ 17,555 → 16,068 ·
ข้อจำกัดดู [known issues](../../operations/known-issues.md#2026-11-09--project--isproject-ตัดจากหมายเหตุบิล)

> **LLM context**: The presentation layer — BigQuery **views** that sit on top of the
> physical dim/fact/curated/validated tables (and a few external sources). Migrated
> into Dataform on **2026-07-24** from views that previously lived only in BigQuery
> (created by hand in the console). `type: "view"`, tag `view`. Current counts are in the
> [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview).
>
> **Non-obvious constraints:**
> - **Pub/Sub export views** follow the separate
>   [export contract](../cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24),
>   including their dataset, tags and hand deployment with tag `pub_sub` (no scheduler runs them).
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
   reads only validated/curated needs **no `js` block**.
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

### Snapshot history and regenerated keys

`view_dim_aging_history` reads accumulated snapshots from `dim_aging_history`. The
daily rebuild of `dim_aging` regenerates `AgingSK`; `BillingSK` follows the
[fact_mir_vs key contract](../../okf/fact/fact_mir_vs.md#grain-and-key).
Each history row keeps the values captured for that snapshot, including pre-migration
billing keys; the view
looks up current keys using the stored natural keys. A document absent from the current
`dim_aging` or `fact_mir_vs` has no current key in the view.

The view joins the current dimension and fact with the natural keys stored in history:

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

Keep the `QUALIFY` because joins can still return multiple rows for the same history
snapshot key.

### `QUALIFY` prevents duplicate rows in views over facts

`view_fact_mir_vs` / `view_fact_mir_rs` join `dim_aging` ด้วย `cfsvnosid` + `company_id`
อย่างเดียว แต่ `dim_aging` มีได้หลายแถวต่อใบ (คนละ `cfsTypeID`) จึงต้องปิดท้ายด้วย

```sql
qualify row_number() over(partition by t1.BillingSK order by t2.AgingSK desc) = 1  -- vs
qualify row_number() over(partition by t1.ReceiveSK order by t2.AgingSK desc) = 1  -- rs
```

This keeps one view row per source fact key after the aging join. Keep it when changing
the view source or its natural-key matching.

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

> Keep declared table dependencies so dimension keys are synchronized before consumers
> run, including `dim_target_product_group_by_sale(_dayofwork)` and their upstream
> dimensions.

## Inventory

> นับตาม `config.schema` ไม่ใช่ชื่อโฟลเดอร์ — โฟลเดอร์ ≠ dataset ปลายทาง
> จำนวนและ dependencies จากโค้ด: [generated lineage](../../diagrams/pipeline_lineage.md#6-view-layer--what-each-view-reads)

### `dimension_view` → schema `DIMENSION_VIEW`

| View | Key upstream (repo tables) | External refs (not deps) |
|---|---|---|
| `view_dim_aging` | dim_aging, dim_aging_rang, dim_sale_representative_last, view_dim_channel | — |
| `view_dim_aging_history` | view_dim_channel, dim_aging, fact_mir_vs | dim_aging_history |
| `view_dim_calendar` | dim_calendar | — · เพิ่ม 2026-09-28: `dim_calendar.*` + `LatestDateFilter` (ดูหัวข้อด้านล่าง) |
| `view_dim_channel` | dim_channel, dim_channel_cost, dim_channel_finance, dim_channel_sales | — |
| `view_dim_company` | dim_company | — |
| `view_dim_customer` | dim_customer, dim_group_customer | mds ×3, dim_districts/provinces/geographies/sub_districts |
| `view_dim_customer_report_info` | See [SQLX definition](../../../definitions/view/dimension_view/view_dim_customer_report_info.sqlx) for active upstream sources | dim_districts/provinces/sub_districts · [Customer Report Info contract](#customer-report-info--customer-segment-2026-10-01) |
| `view_dim_customer_credit_management` | dim_customer, dim_customer_grade | — |
| `view_dim_guarantee` | dim_customer, dim_guarantee | — |
| `view_dim_invoice` | See [SQLX definition](../../../definitions/view/dimension_view/view_dim_invoice.sqlx) for active upstream sources | fn_flag_scg |
| `view_dim_order` | dim_order, mih2 | fn_order_type, mds_data_document_expire_rule_master |
| `view_dim_product_master` | dim_product_master, dim_product_mkt, dim_rebate, dim_waterpac | — |
| `view_dim_product_mkt` | dim_product_mkt, dim_product_mkt_director | — |
| `view_dim_sale_representative` | dim_department, dim_sale_representative | — |
| `view_dim_sale_representative_last` | dim_department_last, dim_sale_representative_last | — |
| `view_dim_target_by_agent` | dim_rate_target + 9 dims | — |
| `view_dim_target_by_agent_dayofwork` | dim_calendar + 8 dims | — |
| `view_sales_representative_last` | dim_department_last, dim_region_last, dim_section_last, view_dim_sale_representative_last | — |

### `fact_view` → schema `FACT_VIEW`

| View | Key upstream | External refs |
|---|---|---|
| `view_fact_transcation` | See [SQLX definition](../../../definitions/view/fact_view/view_fact_transcation.sqlx) for active upstream sources | onetime.mapping_invoice, fn_flag_scg/exc |
| `view_aging_ri` | fact_mir_vs, dim_aging_rang, dim_invoice, dim_status_not_receive, curated_mih, ar_s/chq/cql/mir, view_dim_aging | — |
| `view_fact_mir_rs` | fact_mir_rs, dim_aging, curated_mih, ar_s | — |
| `view_fact_mir_vs` | fact_mir_vs, dim_aging | — |
| `view_fact_salein_mdt` | fact_transcation, dim_customer, dim_sales_branch_mdt — ตัวเชื่อม sell-**in** (ขายเข้าห้าง) กับชุด MDT ที่เป็น sell-**out** | — |
| `view_fact_salein_director_mdt` | See [SQLX definition](../../../definitions/view/fact_view/view_fact_salein_director_mdt.sqlx) for active upstream sources | — |
| `view_fact_saleout_pc_mdt` | See [SQLX definition](../../../definitions/view/fact_view/view_fact_saleout_pc_mdt.sqlx) for active upstream sources | — |
| `view_fact_stock_nonmove_mdt` | See [SQLX definition](../../../definitions/view/fact_view/view_fact_stock_nonmove_mdt.sqlx) for active upstream sources | — |
| `view_fact_target_product_group_mdt` | See [SQLX definition](../../../definitions/view/fact_view/view_fact_target_product_group_mdt.sqlx) for active upstream sources | — |
| `view_fact_target_section_mdt` | See [SQLX definition](../../../definitions/view/fact_view/view_fact_target_section_mdt.sqlx) for active upstream sources | — |

### `onetime` → schema `ONETIME` (data marts / Power BI / models)

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
| `Product_Attribute` | See [SQLX definition](../../../definitions/view/onetime/Product_Attribute.sqlx) for active upstream sources | — |
| `Product_Master_ALL` | dim_product_master, dim_product_mkt_director, view_dim_product_mkt, Product_Attribute | — |

`Product_Attribute` retains the matched series' `SeriesSK` and `SeriesCode`;
unmatched or NULL product series use the `OTHERS` values for both columns.
The fallback requires exactly one `OTHERS` row, supplied by the
[dimension definition](../../../definitions/dimension/dim_product_series.sqlx),
to avoid multiplying product rows.

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

## Customer Report Info + Customer Segment (2026-10-01)

ข้อมูลร้านค้าตาม `CustomerReportName` (MDS `Customer_Report_Master`) และ Segment ลูกค้า
(MDS `Customer_Segment_Master`) — dim 2 ตัว (`dim_customer_segment` stable SK sync · `dim_customer_report_info` MERGE with retained names) · ใน Power BI ผูกเป็นทอด:
`view_fact_transcation` → `view_dim_customer_report_info` (`CustomerReportInfoSK`) → `dim_customer_segment` (`CustomerSegmentSK`)
· ตั้งแต่ 2026-10-07 ตาราง Power BI `Dimension Customer Report Info` ควรอ่านจาก **`view_dim_customer_report_info`**
(`SELECT` ธรรมดา ไม่ต้อง left join เอง) — สลับ source เป็นขั้นตอนแยกหลัง merge + deploy view

- **`dim_customer_report_info` มีทุกชื่อร้านใน `view_dim_invoice`**
  ไม่ใช่แค่ชื่อใน MDS — ไม่งั้น relationship ใน Power BI กรองแถวที่ชื่อไม่อยู่ใน MDS หายหมด · dim อ่าน
  `view_dim_invoice` จึง**ห้าม**ให้ `view_dim_invoice` join dim นี้กลับ (วนกัน) — join อยู่ที่ `view_fact_transcation`
- แถวร้านมีหนึ่งแถวต่อ `CompanyID` + ชื่อที่ตัด whitespace ทั้งหมด (`CustomerReportKey` — ตั้งแต่ 2026-10-28 เก็บเป็นคอลัมน์ท้ายตาราง ใช้เป็น key ของ MERGE: ชื่อเดิมคง `CustomerReportInfoSK`, ชื่อใหม่ได้ `max_sk + ROW_NUMBER()`, ชื่อที่หายจาก source ไม่ลบ): MDS เลือก `updated_at DESC, id`
  ส่วน invoice เลือกตัวสะกดที่มีจำนวน invoice มากสุด แล้วเรียงชื่อตัดสินกรณีเสมอ; ชื่อว่างใน invoice ไม่ถูกนำเข้า dim
- **แถวสงวน `CustomerReportInfoSK = -1` (2026-10-09)** — หนึ่งแถวร่วมทุกบริษัท (ตั้งแต่ 2026-10-28 `INSERT ... WHERE NOT EXISTS` นอก MERGE แทน `UNION ALL`): `CustomerReportName`/`CompanyID`/
  `CompanySK` เป็น NULL, `CustomerSegmentSK = -1` (Non-Segment), `SegmentSource = 'DEFAULT'`, ไม่มีข้อมูล MDS/TA ·
  ไม่นับใน `max_sk` จึง**ไม่ทำให้ SK ของร้านขยับ** · มีเสมอแม้วันนั้นไม่มีบิลที่ join ไม่เจอ · ใช้กับบิลที่ join ไม่พบร้าน
  (ดู `view_fact_transcation.CustomerReportInfoSK`) · `view_dim_invoice` ไม่แก้ (ชื่อยังเป็น NULL ตามเดิม)
- คอลัมน์ SK อยู่หน้าสุด: `CustomerReportInfoSK`, `CompanySK`, `CustomerSegmentSK`.
  ชื่อนอก MDS มี `MdsID` และข้อมูล MDS เป็น NULL. ในตาราง `FlagPC` ยังเป็น BOOL, `OnlinePercent` cast เป็น FLOAT64
- ไม่มีคอลัมน์ `FlagMDS`, `DepartmentName`, `SectionID`, `RegionID`, `CustomerTier`
  ในผลลัพธ์ของตาราง (ตัดออก 2026-10-02 ตอนเปลี่ยนผลลัพธ์เป็น SK ของสายงาน) — `CustomerTier` ยังใช้ภายในเลือก Segment
  · `CustomerReportKey` กลับมาเป็นคอลัมน์ 2026-10-28 (key ของ MERGE) — `view_dim_customer_report_info` ทำ `cri.*` จึงเห็นคอลัมน์นี้ด้วย
- **TA chain เก็บเป็น SK เท่านั้น (2026-10-07)** — ตารางเก็บ `DepartmentSK`, `SectionSK`, `RegionSK`,
  `SectionManagerSK`, `RegionManagerSK`, `DirectorSK` ของแถว `dim_department_last` ที่เป็น TA ที่เลือก
  (ค่าที่ `update_sk_sale_rep_group` ตั้งไว้) และ `SaleRepSK` ของพนักงาน; **ไม่มี** `DepartmentID`/`TAEmployeeID`/
  `TAEmployeeName` ในตาราง — รหัส/ชื่อทั้งหมดไป get ที่ **`view_dim_customer_report_info`**
  (ส่งผ่านคอลัมน์ตารางโดยแปลงค่าตามสัญญาด้านล่าง + `LEFT JOIN` ตาม SK ซึ่ง unique ทุกตัวในตารางปลายทาง จึงไม่มีแถวบาน):
  `TADepartmentID`/`TADepartmentName`, `TASectionID`/`TASectionName`, `TARegionID`/`TARegionName`,
  `TASectionManagerID`/`TASectionManagerName`, `TARegionManagerID`/`TARegionManagerName`,
  `TADirectorID`/`TADirectorName` (`dim_director_last.DirectorID/DirectorName` ไม่ใช่ DirectorOfSales; ไม่มีระดับ director manager),
  `TAEmployeeID`/`TAEmployeeName` · ชื่อคน = `ชื่อ นามสกุล (ชื่อเล่น)` ตัดช่องว่าง ไม่มีชื่อเล่นก็ไม่มีวงเล็บ
  · `CustomerSegmentSK` ส่งผ่านเฉย ๆ ไม่ join `dim_customer_segment` ใน view (Power BI relate เองแล้ว)
  · view แปลงให้ Power BI (2026-10-07; ตารางยังเก็บแบบเดิม): `FlagPC` เป็น STRING `'Yes'`/`'No'` (TRUE → Yes, FALSE หรือ NULL
  → No ไม่มีค่าว่าง รวมร้านที่ไม่อยู่ใน MDS; ร้านใน MDS ที่ค่าเป็น FALSE หรือ NULL ก็ได้ No)
  · `OnlinePercent` = **STRING** ค่าเปอร์เซ็นต์ของร้านนั้นในตาราง + `%` (2026-10-09, `CAST(... AS STRING) || '%'`;
  เดิม 2026-10-07 เป็น FLOAT64 / 100 สำหรับ format Percentage) เช่น 80 → `80%`, 12.5 → `12.5%`, 0 → `0%`, 100 → `100%`
  (ไม่มี `.0` ต่อท้าย; NULL ยังคงเป็น NULL) · ตารางยังเก็บตัวเลข FLOAT64 เหมือนเดิม
  · ผลวัด 2026-10-07 ก่อนเปลี่ยนเปอร์เซ็นต์เป็นข้อความ: Yes 149 · No 41,228 (NULL ในตาราง 39,505) · `OnlinePercent` 22 แถว สูงสุด 0.8
  · ผลวัด 2026-10-09 (SELECT query ที่ compile แล้วบน live): `OnlinePercent` 22 แถว = `0%` 12 · `20%` 1 · `70%` 1 · `80%` 8
  · `TADebcode` เก็บเป็นคอลัมน์ธรรมดาในตาราง (ไม่ใช่ SK)
  · **ที่อยู่ร้าน + credit term (2026-10-22)** — `ReportDebcode` = `COALESCE(SegmentDebcode, TADebcode)`;
  `DEBcreditTerm` จาก validated_mac5 `deb` และ `InvoiceProvinceSK`/`InvoiceDistrictSK`/`InvoiceSubDistrictSK` จาก
  `process_dataset.view_deb_address_data` (แบบเดียวกับ `dim_customer`) join ด้วย company + `ReportDebcode` · view คืนได้หลายแถวต่อรหัส
  จึงเลือกแถวเดียว: `sub_districts` > `districts` > `provinces` แล้ว SK น้อยสุด · `view_dim_customer_report_info` เพิ่ม
  `SubDistrict`/`District`/`Province` (`name_th` จาก `dim_sub_districts`/`dim_districts`/`dim_provinces` แบบ `view_dim_customer`)
  · ผลวัด 2026-10-22 (SELECT query ที่ compile แล้ว): 41,536 แถวเท่าเดิม SK unique · ag01 40,995 ร้าน: credit term 40,971,
  Province 6,653, District 4,146, SubDistrict 4,058 — ที่อยู่น้อยเพราะ `deb_address_data` parse ได้แค่ส่วนน้อยของ debtor
  · ภายใน dim ยัง join ด้วย SK · `dependencies[]` เป็นชุดเล็กสุด (2026-10-06): `update_sk_sale_rep_group` (รันหลัง `*_last`
  ทั้งหมดและเติม `DepartmentSK` ของ `dim_sale_representative_last` ที่ใช้หา TA), `dim_customer_segment`, และตารางหลัง view
  ตามกฎ Run order: `dim_aging`, `dim_order`, `mec` (`view_dim_invoice` อ่านตรง ๆ; `dim_aging` ครอบ
  `dim_invoice`/`dim_customer` ด้วย), `dim_group_customer` (`view_dim_customer`) และ `deb_address_data` (`view_deb_address_data`)
  · ใน repo/BigQuery ผู้อ่านตารางนี้คือ `view_fact_transcation` (อ่านแค่ `CustomerReportInfoSK`/`CompanySK`/`CustomerReportName`)
  และ `view_dim_customer_report_info`
  · **Deploy (2026-10-09)**: หลัง merge รัน `dim_customer_report_info` (`dimension_daily`) ให้มีแถว -1 **ก่อน**
  deploy `view_fact_transcation` แล้ว deploy `view_dim_customer_report_info` — ทั้งสอง view อยู่ tag `view` ไม่อยู่ในรอบรันกลางคืน
  (ถ้า deploy fact view ก่อน rebuild จะมี SK -1 ที่ dim ยังไม่มี; merge โค้ดอย่างเดียวไม่เปลี่ยนตาราง live)
  · **Power BI (ขั้นตอนภายนอกหลัง deploy)**: เปลี่ยน source ของ `Dimension Customer Report Info` เป็น
  `view_dim_customer_report_info` แบบ `SELECT` ธรรมดา; ตารางเดิมไม่มี `DepartmentID` แล้ว · ตั้งชนิด `OnlinePercent` เป็น **Text**
  แทนชนิดตัวเลข/format Percentage เดิม แล้วทำ **full refresh** ของ model เพื่อโหลด dimension และ fact ตามสัญญาใหม่
- **TA ของร้าน (`DepartmentSK` → `TADepartmentID` ใน view, กฎแก้ 2026-10-09)** — 1 แถว = 1 TA หรือว่าง ตามลำดับ:
  1. **ไม่อ่าน TA จาก MDS แล้ว (ตัด 2026-10-09 ตามที่ผู้ใช้สั่ง)** — เดิม `DepartmentID` ใน `mds_data_customer_report_master`
     ชนะเสมอ (`TASource = 'MDS'`) และพนักงานมาจากคนเดียวที่ถือ TA นั้น (CTE `mds_emp`, PR #25) — ตัดทั้งคู่ ทุกร้านใช้ข้อ 2–4
     · dim **ไม่ select `DepartmentID` จาก MDS เลย** เพื่อให้ MDS ลบคอลัมน์นี้ได้ (ขั้นตอนแยกใน MDS app หลัง deploy)
     · MDS ยังให้ `CustomerTier` (Segment), `FlagPC`, `ShopOnline`, `OnlinePercent`, `MdsID` เหมือนเดิม
  2. เลือก**รหัสลูกค้าที่ชื่อของตัวเองตรงกับชื่อรายงาน** จาก `mihCus` ทุกบิลของชื่อนั้นใน `view_dim_invoice`
     (ชื่อของรหัส = สูตรเดียวกับ `view_dim_invoice`: `NicknameCustomer` เมื่อ `FlagMDSNickName` ไม่งั้น
     `clean_company_prefix(debnamet)` จาก `view_dim_customer`, ตัด whitespace) · หลายรหัสตรงใช้**บิลล่าสุด**
     (`mix_date DESC, mihVnos DESC` แบบ Segment) · ไม่มีรหัสที่ชื่อตรง (ชื่อจาก SCG/CRC/`mec`) → ว่าง
  3. รหัสนั้น → `validated_mac5.deb.debsalesp` (บริษัทเดียวกัน) → `dim_sale_representative_last` ที่ `EmployeeID = debsalesp`,
     ตรวจสิทธิ์ทั้งบริษัท + พนักงาน **ก่อนกรองวันที่**: ถ้าแถว `DepartmentID` ไม่ว่างและไม่ใช่ `Dummy*` ของพนักงาน
     ใน `dim_sale_representative_last` มี `CostChannelID` หรือ `DepCode` ไม่ว่างแม้เพียงแถวเดียว
     (รวมแถวปัจจุบัน หมดอายุ และยังไม่เริ่มมีผล โดยไม่ต้องจับคู่ `dim_department_last` ได้) = **พนักงาน MDT** (CTE `mdt_emp`)
     → ไม่ใช้กฎ TA เดียวด้านล่าง แต่ใช้ข้อ 4
     · พนักงานปกติที่ไม่มีแถวดังกล่าว ใช้แถว `DepartmentID` ไม่ว่าง, วันนี้อยู่ใน `StartDate..EndDate`,
     TA ไม่ใช่ `Dummy*` และ `dim_department_last.EndDate` ยังไม่หมด (วันที่เป็น NULL ไม่จำกัดขอบเขตด้านนั้น)
     → **TA เดียวเท่านั้น** ได้ `TASource = 'DEBSALESP'`
     · ย้ายจาก TA หมดอายุมา TA ปัจจุบันเดียวได้ TA ปัจจุบัน · ไม่มี TA หรือมีหลาย TA ปัจจุบัน → ว่าง
  4. **พนักงาน MDT (ห้างเชน, 2026-10-08)** — CTE `mdt_cand` → `mdt_ta` ต่อ (บริษัท, รหัสลูกค้าใน `TADebcode`): แปลง
     `deb.debgroup` ของรหัสนั้นเป็นเชนด้วยกฎเดียวกับ `view_fact_transcation` (HP/HPEXPO→`hp`, TW/TWEXPO→`tw`,
     BT/BT.C→`bt`, GB→`gb`, MH→`mh`, DOHOME→`dh`; ค่าอื่นหรือว่าง = ไม่ใช่เชน) แล้วเลือกแถว TA ของพนักงานคนนั้น
     ที่ใช้ได้วันนี้และไม่ใช่ `Dummy*` (เงื่อนไขวัน/Dummy เดียวกับข้อ 3, CTE `rep_cur`) และ `LOWER(DepartmentID)` ขึ้นต้นด้วย
     `<เชน>_` → **TA เดียว** ได้ TA นั้น `TASource = 'MDT'`
     · **หลาย TA ในเชน (2026-10-08, พนักงานแยกภาคด้วย `DepCode` เช่น `TW_S01_TA01`/`TW_S02_TA01`)** — CTE `mdt_slot`:
     ใช้ `TRIM(mihDep)` ของ**บิลล่าสุดที่พนักงานคนนี้ขายให้ร้านนี้** ใน `inv_rows` (`view_dim_invoice` บริษัท + ชื่อรายงาน
     ไม่สนช่องว่างเดียวกับ `ta_cus`, `mihPer = debsalesp`) เฉพาะบิลที่ `mihDep` อยู่ใน list `DepCode` ของตัวเลือก
     ตาม [กฎ DepCode หลายค่า](../fact/fact-layer.md#depcode-รับหลายค่า-ab-2026-10-17)
     และตัดบิลยกเลิก (`mihCancel = -1`) ออกใน `mdt_slot` **ก่อนเรียงบิลล่าสุด**; `mihCancel` เป็น NULL ถือว่าไม่ยกเลิก
     (`mix_date DESC, mihVnos DESC, DepartmentSK ASC` — ถ้าบิลเดียวชนหลาย TA เลือก `DepartmentSK` ต่ำสุด)
     → TA ที่ `DepCode` ตรง ได้ `TASource = 'MDT'` เหมือนกัน · ไม่มีบิลตรง = ว่าง
     (`mihDep` ตรงกับ `milDep` 99.8% ของบิลพนักงานเชน) · TA อาจเปลี่ยนเองเมื่อบิลล่าสุดย้ายภาค (ย้อนทดสอบ 1 ปี เปลี่ยน 3 ร้าน)
     · กรองบิลยกเลิกเฉพาะการเลือกภาคนี้: `inv_rows` ยังเก็บบิลเหล่านั้นให้ `inv`, `inv_cus`, `ta_cus` ใช้เลือกชื่อร้าน,
     รหัสลูกค้าสำหรับ Segment และ `TADebcode` ตามเดิม · กรณีมี TA เดียวในเชนยังใช้ TA นั้นโดยไม่ต้องมีบิลที่ไม่ยกเลิก
     · ว่าง: ไม่มี TA ปัจจุบันในเชน หรือ debgroup ว่าง/ไม่ใช่เชน (ลูกค้าบุคคล ลูกค้าต่างประเทศ — ไม่มี fallback จาก `DepCode` อย่างเดียว,
     ไม่ใช้ `*_OTHER`)
     · ยอมรับ: ร้าน "โฮมโปรดักส์ เซ็นเตอร์ สาขาเมกาโฮม-…" มี debgroup = HP จึงได้ TA ของโฮมโปร (`HP_*`) แม้บิลจะลง
     เมกาโฮม (`MH_*`) — ไม่มีกฎจากชื่อร้าน และแผนกในบิลใช้แค่เลือกภาคในเชนที่ได้จาก debgroup · กฎ TA ของ `fact_transcation`/`view_fact_transcation` คงเดิม
     · `TADebcode`/`SaleRepSK` ของร้าน MDT เหมือนเดิม (พนักงาน `debsalesp`)
  - trace: `TASource` (`DEBSALESP`/`MDT`/NULL — ไม่มี `MDS` ตั้งแต่ 2026-10-09), `TADebcode` — รหัสลูกค้า (debcode/`mihCus`)
    ที่ใช้ค้นหา TA ในข้อ 2–4; หากมีรหัสที่ชื่อตรงก็เก็บไว้แม้ TA ว่าง เพื่อใช้ตรวจสอบ
    · `SaleRepSK` — พนักงาน `deb.debsalesp` ของ `TADebcode` ทุกแถว (NULL เมื่อ `debsalesp` ว่าง) · map เป็น SK: แถว
    `dim_sale_representative_last` หนึ่งแถวต่อบริษัท + `EmployeeID` โดยเลือกแถวที่ `EmployeeName` ไม่เป็น NULL ก่อน
    (รวมแถวชื่ออย่างเดียวจาก `per`); ถ้ามีหลายแถวเลือก `SaleRepSK` ต่ำสุดในกลุ่มที่มีชื่อ
    ถ้าไม่มีแถวที่มีชื่อ เลือก `SaleRepSK` ต่ำสุดของพนักงานนั้น
    · การ map `EmployeeID` ที่เลือกแล้วเป็น `SaleRepSK` ไม่กรองด้วย `DepartmentSK`/`DepartmentID` หรือวันที่;
    จึงมี SK ได้แม้ TA ว่าง
    · พนักงานที่ไม่อยู่ใน `dim_sale_representative_last` → `SaleRepSK` ว่าง (`TAEmployeeID`/`TAEmployeeName` ใน view เป็น NULL)
    แต่รหัสเดิมยังตรวจได้ผ่าน `TADebcode` → `deb.debsalesp` (ผลวัด live 2026-10-07 พบ 52 แถว)
    · ประวัติ: ตัด `TAEmployeeID`/`TADebcode` 2026-10-06 · `TADebcode` กลับมา 2026-10-07 ·
    พนักงานกลับมาเป็น `SaleRepSK` + TA chain เป็น SK + view 2026-10-07 · กฎเลือก TA/Segment ไม่เปลี่ยน
    · ผลวัด 2026-10-07 ก่อนแยกการเลือกพนักงานจาก TA (SELECT บน live 41,377 แถว; SK unique, TASource เท่าเดิม MDS 1,631 · DEBSALESP 13,354 · ว่าง 26,392):
    TA SK ครบ 6 ระดับ 14,985 แถว (= MDS + DEBSALESP) · `SaleRepSK` 23,510 · `TADebcode` 38,901 (ไม่มี `debsalesp` 15,339 ·
    พนักงานไม่อยู่ใน `dim_sale_representative_last` 52) · view 41,377 แถว ไม่บาน, SK ทุกตัวหาเจอ 100%, ชื่อเต็มทุกแถวที่มี SK
  - ผลวัด 2026-10-08 หลังเพิ่มข้อ 4 (SELECT query ที่ compile แล้วเทียบกับตาราง live 41,389 แถว ไม่ได้รันตาราง):
    จำนวนแถว/SK unique/1 แถวต่อ (`CompanyID`, ชื่อไม่สนช่องว่าง) เท่าเดิม · MDS 1,631 · DEBSALESP 13,356 (เท่าเดิม) ·
    **MDT 210** · ว่าง 26,192 (เดิม 26,402) · แถวที่ไม่ใช่ MDT TA/SK ทั้ง 6 ระดับ/`TADebcode`/`SaleRepSK` ตรงกับตารางเดิม 100% ·
    แถว MDT มี `SectionSK` ครบ · ยอดขายร้าน MDT ที่ได้ TA = 14.30% ของยอด 4 ปี / 14.75% ของ 12 เดือน
    · ร้าน MDT ที่ยังว่าง 336 ร้าน (หลาย TA ภาคในเชน 89 · debgroup ไม่ใช่เชน 247)
  - ผลวัด 2026-10-08 หลังเพิ่ม `mdt_slot` ก่อนเพิ่มตัวกรองบิลยกเลิก (SELECT query ที่ compile แล้วเทียบกับตาราง live 41,389 แถว ไม่ได้รันตาราง):
    จำนวนแถว/SK unique/1 แถวต่อ (`CompanyID`, ชื่อไม่สนช่องว่าง) เท่าเดิม · MDS 1,631 · DEBSALESP 13,356 (เท่าเดิม) ·
    **MDT 286** (เดิม 210 ได้ `DepartmentSK` เดิมทุกร้าน + ใหม่ 76) · ว่าง 26,116 · แถวอื่นทั้งหมดตรงกับตารางเดิม 100% ·
    แถว MDT ใหม่มี `SectionSK` ครบ และ `DepCode` ของ TA = `mihDep` ของบิลล่าสุดที่ตรงทุกร้าน (76/76) ·
    ร้านใหม่ตามพนักงาน 1053173: 39 · 1062411: 25 · 1065043: 12 (HP 46 · TW 24 · BT 6) · ยอด 12 เดือน 148.1M
  - ผลวัด 2026-10-08 หลังเติมพนักงานให้แถว MDS (SELECT query ที่ compile แล้วเทียบกับ query ที่ 3c7bad4 และตาราง live 41,389 แถว ไม่ได้รันตาราง):
    แถวที่มี TA แต่ไม่มีพนักงาน **MDS 1,631 → 243** (DEBSALESP 0 · MDT 0 ทั้งก่อน/หลัง) · MDS ได้พนักงาน 1,388 ·
    ว่าง 243 ร้านเพราะ TA มีคนถือพร้อมกันหลายคน (14 TA เช่น `N2_TA03` 39 ร้าน, `NE4_TA03` 30, `S1_TA04` 29;
    `*_OTHER` มี 2–5 คน) · TA ที่ไม่มีคนถือวันนี้ 0 ร้าน · แถวที่ไม่ใช่ MDS และคอลัมน์อื่นของแถว MDS ตรงเดิม 100% ·
    1 แถวต่อ (`CompanyID`, ชื่อไม่สนช่องว่าง), SK unique, TASource เท่าเดิม (MDS 1,631 · DEBSALESP 13,356 · MDT 286)
  - ผลวัด 2026-10-09 หลังตัด MDS (SELECT query ที่ compile แล้ว เทียบ query ที่ 350ebec บน live, ไม่ได้รันตาราง/deploy view):
    TASource **MDS 1,631 · DEBSALESP 13,361 · MDT 286 → DEBSALESP 14,394 · MDT 286** · ว่าง 26,129 → 26,727 ·
    ร้าน MDS เดิม 1,631: TA เดิมจาก debsalesp **715** (17.79% ของยอด 12 เดือน) · TA ต่าง **318** (4.76%) ·
    **ว่าง 598** (11.12%) — คอลัมน์อื่นนอกจาก TA chain/`TASource`/`TADebcode`/`SaleRepSK` ตรงเดิมทุกแถว ·
    แถวอื่น 39,776 ตรงเดิม 100% · ร้าน 41,407 แถวเท่าเดิม + แถวสงวน -1 = 41,408 แถว, 1 แถวต่อ (`CompanyID`, ชื่อไม่สนช่องว่าง),
    SK unique ไม่ NULL · **`CustomerReportInfoSK` ของร้านไม่ขยับเลย** (0 แถว)
  - ข้อจำกัด: `debsalesp` คือพนักงานที่ลงไว้ใน Mac5 (มักเป็นคนเปิดลูกค้า) ไม่ได้อัปเดตตามคนดูแลปัจจุบัน
  - ไม่เติม TA จากบิล (`DepartmentSKLast` ของ fact) ในไฟล์นี้ — `view_fact_transcation` อ่าน dim นี้ จึงวนกัน
  - ผลวัด 2026-10-06 (SQL แบบ SELECT บนข้อมูล live 41,357 แถว หลังตัดพนักงาน MDT ก่อนกรองวันที่):
    MDS 1,631 · DEBSALESP 13,349 · ว่าง 26,377 (ไม่มี `debsalesp` 15,340 · พนักงานปกติไม่มี TA ที่ใช้ได้หรือมีหลาย TA 9,646 ·
    ไม่มีรหัสที่ชื่อตรง 845 · พนักงาน MDT 546) ·
    SK/จำนวนแถว/คอลัมน์ Segment เท่าเดิมทุกแถว · แถว MDS เดิมได้ TA เดิม
- `CustomerReportInfoSK` is retained for matching `CompanyID` + `CustomerReportKey`;
  the view still joins by natural key rather than storing it in the fact;
  แถวสงวนใช้สัญญาข้างต้น
- **`view_dim_invoice.CustomerReportName` เลือกตามลำดับ** (`CASE` ใน [view_dim_invoice.sqlx](../../../definitions/view/dimension_view/view_dim_invoice.sqlx), แก้ 2026-10-02):
  1. บิล SCG (`fn_flag_scg(RefOrder, mihCus) IS NOT NULL`) **และ** `mec.mecdesc IS NOT NULL`
     → `clean_company_prefix(mec.mecdesc)` (ชื่อสาขาที่ส่งของจาก `mihMec`)
  2. `cust.FlagMDSNickName = TRUE` → `cust.NicknameCustomer` (ชื่อเล่นใน MDS)
  3. `COALESCE(mds_crc.crc_shop_name_change, main.CRCShopName) IS NOT NULL` → ใช้ชื่อร้าน CRC ค่านี้
  4. ไม่งั้น `clean_company_prefix(cust.debnamet)`
  - บิลที่ไม่ใช่ SCG หรือ `mec.mecdesc` เป็น NULL ใช้ลำดับ 2–4
- **`view_dim_invoice.mecdesc`** — ชื่อสาขาที่ส่งของจาก `validated_mac5.mec` จับคู่ด้วย `mihMec = meccode`
  และ `companyID = company_id` · ส่งออกโดยไม่ผ่าน `clean_company_prefix` ทั้งบิล SCG และบิลอื่น;
  ถ้า join ไม่พบจะเป็น NULL · Power BI ที่ต้องการยอดรายสาขาของลูกค้าที่ชื่อรายงานรวมเป็นชื่อเครือ
  ให้ใช้คอลัมน์นี้จาก `view_dim_invoice` โดยผูกกับ fact ผ่าน `InvoiceSK`
- **`view_fact_transcation.CustomerReportInfoSK`** — `InvoiceSK` → `CustomerReportName` ของ invoice นั้นใน `view_dim_invoice`
  → จับคู่ด้วย `CompanySK` และชื่อแบบ **ไม่สนช่องว่าง** (`REGEXP_REPLACE(..., r'\s', '')` ทั้งชื่อจาก invoice และ `cri.CustomerReportName`)
  (ผลเท่ากับ join `CustomerReportKey` เดิม — วัด 2026-10-02: 1,671,914 InvoiceSK ได้ SK ตรงกันทุกแถว);
  แถวที่มี `InvoiceSK` (บิลจริง) แต่ join ไม่เจอ → **-1** = แถวสงวนของ dim (2026-10-09, เดิม NULL) ทั้งชื่อว่าง
  (ชื่อมีแค่คำนำหน้า, `debnamet` ว่าง, รหัสลูกค้าไม่อยู่ใน `deb` เช่น `111020730.`/`TEST`) และชื่อไม่ว่างที่ยังไม่มีใน dim ·
  แถวที่ `InvoiceSK` เป็น NULL ไม่ถูกแทนด้วย -1 รวมแถวเติมปฏิทิน (ยอด 0) ที่ยังเป็น NULL ตามเดิม ·
  แก้แค่คอลัมน์นี้ใน `final` CTE (`IF(t2.InvoiceSK IS NOT NULL AND cri... IS NULL, -1, ...)`)
  · ผลวัด 2026-10-09 (query ที่ compile แล้ว เทียบ view live, ไม่ได้ deploy): 2,695,179 แถวเท่าเดิม ยอดรวมเท่าเดิม ·
  บิลที่ SK ว่าง 44 บรรทัด (24 บรรทัดยอดไม่เป็น 0) → **0** · SK -1 = 44 บรรทัด / 11 invoice / **147,013.60** (ag01 IS 2022–2024
  ที่เดิมเป็นแถวว่างใน Power BI) · แถวเติมปฏิทิน 4,005 แถว SK NULL เท่าเดิม · กลุ่ม SK อื่นตรงเดิมทุกกลุ่ม
- **`dim_customer_report_info.CustomerSegmentSK` ของแถวร้าน** — 1 ชื่อ = 1 Segment, ค่าปัจจุบัน (ไม่ย้อนตามเดือนบิล)
  จับคู่แถวของบริษัทเดียวกันด้วย `CompanySK` ตามลำดับ:
  1. `CustomerTier` ไม่ว่าง → ใช้รหัส tier จับคู่ `Segment3` · เมื่อจับคู่ได้ `SegmentSource = 'MDS'`
     ถ้า tier ไม่มีใน segment master จะใช้ fallback ข้อ 3 โดยไม่ลอง channel
  2. `CustomerTier` ว่าง → debcode ของ**บิลล่าสุด**ของชื่อนั้น (`mix_date DESC, mihVnos DESC` — ชื่อเดียวมีหลาย debcode ได้)
     → channel ล่าสุดจาก `validated_mac5.tbook_quotation` **ใน allowlist `TT/DC/DA/DG/DD/DT/DR`**
     (debcode = คำแรกของ `agent1` ที่ไม่ว่าง, เรียง `dinsert DESC, SAFE_CAST(id AS INT64) DESC`)
     กรอง allowlist ก่อนเลือกแถวล่าสุด: channel ว่างหรือนอก allowlist ไม่แทนที่แถวเก่าที่อยู่ใน allowlist
     · เมื่อจับคู่ `Segment3` ได้ `SegmentSource = 'CHANNEL'`
     - `TT` → `BRONZE` ถ้า `deb.debdate` อยู่ในเดือนปัจจุบัน (Asia/Bangkok) ไม่งั้น `SILVER`
       (debdate ว่าง = SILVER) — เงื่อนไขจาก `เงื่อนไข cust.xlsx`: ร้าน TT เปิดใหม่ = BRONZE เดือนถัดไป auto SILVER
     - channel อื่น → Segment3 เดียวกัน (DD/DA/DC/DT/DG)
  3. join รหัส segment ไม่พบ (tier ไม่มีใน master, ไม่มี quotation, หรือ channel ไม่มีใน master เช่น `DR`)
     → ใช้แถว `Segment3 = 'DC'` ของบริษัทนั้นเมื่อมี · `SegmentSource = 'DEFAULT'` · fallback DC เดิมคงไว้
  4. join ไม่เจอทั้ง segment และ `DC` ของบริษัทนั้น (เช่น บริษัทที่ไม่มีแถวใน segment master — ณ 2026-10-02 ทุกบริษัทนอกจาก ag01)
     → **Non-Segment `CustomerSegmentSK = -1`** · `SegmentSource = 'DEFAULT'` · **ไม่มีแถวที่ `CustomerSegmentSK` เป็น NULL**
     (แก้ 2026-10-02 — เดิมได้ NULL)
  - `dim_customer_segment` มีแถว default `CustomerSegmentSK = -1` (`UNION ALL` ตาม convention แถว Unknown ของ
    `dim_store`/MDT dims): `Segment1/2/3` และ `DescriptionThai/Eng` = `Non-Segment`, `SortOrder = 99`,
    `CompanySK`/`CompanyID`/`MdsID` NULL · matching MDS segment keys retain their SK.
  - trace: `SegmentDebcode`, `SegmentChannel`
- `CURRENT_DATE` ถูกประเมินตอน dim รัน → BRONZE→SILVER ขยับวันละครั้งตามรอบ `dimension_daily`

### ผลกระทบสูตร SCG (2026-10-02)

สูตรก่อนแก้ใช้ `mecdesc` ที่ไม่เป็น NULL กับทุกบิล · ผลเปรียบเทียบกับสูตรที่เลือกข้างบนราย `InvoiceSK`:
เปลี่ยนเฉพาะ ag01 **14,414 invoice** จากชื่อสาขาเป็นชื่อเครือ 3 ชื่อ; บริษัทอื่นไม่เปลี่ยน

| ชื่อเครือ | ชื่อสาขา/โครงการที่รวม | invoice ที่เปลี่ยน |
|---|---:|---:|
| `สยามโกลบอลเฮ้าส์` | 102 | 9,981 |
| `ดูโฮม` | 27 | 4,431 |
| `เอสซี แอสเสท คอร์ปอเรชั่น` | 2 | 2 |

- ยอดที่ย้ายชื่อรายงาน: 41,190 แถว fact / 265,328,119.43 บาท · จำนวนแถว fact ไม่เปลี่ยน
- MDS match เท่าเดิม **1,850/1,872** · แถว fact ที่ไม่มี `CustomerReportInfoSK` เท่าเดิม **44** · join key ไม่ซ้ำ

## Compile-verification checklist

CLI availability and setup: [onboarding §3.2](../../getting-started/onboarding.md).

1. All views compile and the `view` tag runs after the table-building tags.
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
