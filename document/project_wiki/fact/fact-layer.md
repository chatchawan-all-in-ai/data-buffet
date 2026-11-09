# Fact Layer — `definitions/fact/`

## Sale-rep order-window matching (2026-10-28)

The [fact_transcation card](../../okf/fact/fact_transcation.md#how-it-is-built) owns the
shared `OrderDate` lookup used by `fact_transcation` and `view_fact_transcation`.

The first branch inside each sale-rep join's existing CASE is
`WHEN OrderStartDate IS NOT NULL THEN OrderDate BETWEEN OrderStartDate AND OrderEndDate`.
The range is inclusive. When OrderStartDate is present, an out-of-range or missing
OrderDate, or a missing OrderEndDate, rejects that row; other rows still compete
under the existing normal rules. Rows without OrderStartDate retain those rules.
Selection priority is owned by the
[`seq_condition` reference](../overview/business-flags.md#seq_condition--fact_transcation).

In `fact_transcation`, `saleRepMatchOn` applies this to part1, part2, and addon;
existing bill StartDate/EndDate checks remain. The last-side date policy is owned by
the [view reference](../view/view-layer.md#sale-rep-order-windows-2026-10-28).
`OrderDate` is excluded from the final temp-table SELECT:
the positional DELETE/INSERT flow and fact-table column schema remain unchanged.

> **LLM context**: fact ทุกไฟล์อยู่ใน dataset `fact_table` (`databuffet.FACT_TABLE`)
> และ tag `fact_daily` ทุกตัว · มี 3 แบบการ materialize — **ไม่มี MERGE** ในชั้นนี้เลย
> ตาราง dimension อ้างด้วย string interpolation (`${...TableRef}`) + `dependencies[]`
> ส่วนต้นทาง curated/validated อ้างด้วย `${ref()}`
> **Load-bearing typo**: ไฟล์/ตารางคือ `fact_transcation` (ไม่ใช่ "transaction") ห้ามแก้
> ตรวจกับโค้ดจริง 2026-10-18 · จำนวนไฟล์ล่าสุดดูที่
> [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview)

## Inventory (18 ไฟล์ ณ 2026-10-18)

### กลุ่ม MAC5 — ขาย/วางบิล/รับชำระ (9)

| File | Type | Pattern | Upsert keys | Partition / Cluster | Retention |
|---|---|---|---|---|---|
| `fact_order.sqlx` | table | Dataform rebuild | uniqueKey `FactOrderSk` | `asatdate` / `FactOrderSk` | ไม่มี |
| `fact_invoice.sqlx` | table | Dataform rebuild | uniqueKey `FactInvoiceSK` | `asatdate` / `FactInvoiceSK` | 4 ปีใน query |
| `fact_quotation.sqlx` | operations | `DROP` + `CREATE OR REPLACE ... AS` | — | `asatdate` / `FactQuotationSK` | full refresh |
| `fact_transaction_delivery.sqlx` | operations | `CREATE OR REPLACE TABLE AS` | — | `mix_date` / `FactTransDeliverySK` | 4 ปี |
| `fact_delivery.sqlx` | operations | `CREATE OR REPLACE TABLE AS` | — | ไม่ partition / `FactDeliverySK` | full refresh |
| `fact_transcation.sqlx` | operations | **TEMP → DELETE → INSERT upsert** | `milVnos, milType, CompanySK` | `mix_date` / `milType, milVnos, milCus, milPer` | DELETE < 4 ปี ตัดถึงต้นปี |
| `fact_chq.sqlx` | table | Dataform rebuild | uniqueKey `FactChqSK` | ไม่ partition / `FactChqSK` | full refresh |
| `fact_mir_vs.sqlx` | table | Dataform rebuild | uniqueKey `BillingSK` | ไม่ partition / `BillingSK, InvoiceSK, CustomerSK` | full refresh |
| `fact_mir_rs.sqlx` | table | Dataform rebuild | uniqueKey `ReceiveSK` | ไม่ partition / `ReceiveSK, FactChqSK, InvoiceSK` | full refresh |

### กลุ่ม store — ใบสั่ง/ใบกำกับ/งานค้าง แยกตามคลัง (3)

| File | Type | uniqueKey | Partition / Cluster | Retention |
|---|---|---|---|---|
| `fact_order_store.sqlx` | table | `FactOrderStoreSK` | `mix_date` / `FactOrderStoreSK` | 4 ปีตัดถึงต้นปี (WHERE หลัก **+ `dim_order_dedup`**, 2026-09-15) |
| `fact_invoice_store.sqlx` | table | `FactInvoiceStoreSK` · grain รวม `milPer` | `mix_date` / `FactInvoiceStoreSK` | 4 ปีตัดถึงต้นปี (WHERE หลักตามวันที่ใบกำกับ · **ไม่กรองตามออร์เดอร์** — `LEFT JOIN dim_order`, 2026-10-21) |
| `fact_backlog_store.sqlx` | table | `FactBacklogStoreSK` | `sDate` / `FactBacklogStoreSK` | snapshot ล่าสุดของ `cps` **+ 4 ปีตัดถึงต้นปี** + กรองบรรทัดให้ตรง `fact_order_store` |

> ทั้งสามตัว `partitionBy` เดิมเป็น `asatdate` · commit `048f746` ถอดคอลัมน์ `asatdate`
> ออกจาก SELECT แต่ลืมแก้ config ทำให้ `PARTITION BY asatdate` ชี้คอลัมน์ที่ไม่มี →
> `5e70f83` แก้เป็น `mix_date` / `sDate` · **ถอดคอลัมน์เมื่อไร ต้องเช็ค `partitionBy`
> ใน config ทุกครั้ง** (ดู known-issues.md 2026-09-03)

### กลุ่ม SALEOUT_MDT — sell-out / สต็อก / เป้า modern trade (6, เพิ่ม 2026-09/10)

| File | Type | uniqueKey | Partition / Cluster | ต้นทาง |
|---|---|---|---|---|
| `fact_saleout_mdt.sqlx` | table | `sale_date, store_code, branch_code, product_code, doc_type` | `sale_date` / `store_code, branch_sk, product_mdt_sk` | `curated_saleout_mdt` |
| `fact_saleout_monthly_mdt.sqlx` | table | `month_date, store_code, branch_code, sales_channel, product_code` | `month_date` / `store_code, branch_sk, product_mdt_sk` | `curated_saleout_monthly_mdt` — ส่งต่อ `month_date` ตามเดิม: เดือนปัจจุบันรายวัน / เดือนที่ปิดแล้ววันสิ้นเดือน (เลิกอ่าน `onetime.saleout_monthly_mdt` 2026-10-05) |
| `fact_stock_mdt.sqlx` | table | `stock_date, store_code, branch_code, product_code` | `stock_date` / `store_code, branch_sk, product_mdt_sk` | `curated_stock_mdt` |
| `fact_stock_mdt_monthly.sqlx` | table | `month_end, store_code, branch_code, product_code` | `month_end` / `store_code, branch_sk, product_mdt_sk` | **`fact_stock_mdt`** (ไม่แตะ curated) |
| `fact_target_saleout_mdt.sqlx` | table | `target_date, branch_code, marketing_group_id, sub_marketing_id, segment_id` | `target_date` / `store_code, branch_sk, marketing_group_id` | `dim_target_saleout_mdt` — เป้ารายวันระดับกลุ่มการตลาด (ไม่ใช่รายสินค้า) |
| `fact_target_series_mdt.sqlx` | table | `target_date, branch_code, series_code` | `target_date` / `store_code, branch_sk, series_sk` | `dim_target_series_mdt` — เป้ารายวันราย series (ต้นทาง Value = 0 ทุกแถว วัด 2026-10-02 มีแค่จำนวน) |

- ทั้งหมดอยู่ในรอบ `daily_process` 06:00 และรันซ้ำใน workflow `saleout_morning` 08:55
  (ดู [running-and-troubleshooting § Schedule](../operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd))
- `fact_saleout_monthly_mdt` มีเกรนผสมตาม curated: เดือนปัจจุบันเก็บวันขายรายวัน
  ส่วนเดือนที่ปิดแล้วใช้วันสิ้นเดือน · รวมยอดรายเดือนด้วย `SUM(sale_qty)` /
  `SUM(sale_amount)` และ `GROUP BY DATE_TRUNC(month_date, MONTH)` พร้อม key ที่ต้องการ
  · กรองเดือนด้วย `DATE_TRUNC(month_date, MONTH) = DATE '2026-10-01'`
  แทน `month_date = DATE '2026-10-31'` ซึ่งตกหล่นยอดรายวันของเดือนปัจจุบัน
- fact ยอดขาย/เป้าทั้งสี่ตัว (`fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `fact_target_*`)
  ผูก "Region Transaction" ผ่าน `dim_report` / `dim_region` / `dim_region_manager` /
  `dim_director` ค่า ณ วันที่ของแถว ไม่ใช่ค่าปัจจุบัน
- fact ยอดขายและสต็อก (`fact_saleout_mdt`, `fact_saleout_monthly_mdt`, `fact_stock_mdt`,
  `fact_stock_mdt_monthly`) เก็บ `store_code` / `branch_code` / `product_code` เป็น **degenerate dimension**
  ไว้สืบกลับถึงแถวต้นทางที่ห้างส่งมา คู่กับ `branch_sk` / `product_mdt_sk` ที่ใช้ join จริง
- `fact_stock_mdt_monthly` เลือก **วันสุดท้ายที่แต่ละห้างมีข้อมูลในเดือนนั้น** แยกรายห้าง
  เพราะ BT กับ TW ส่งไฟล์คนละจังหวะ วันขาดคนละวัน · ตัดวันที่ไฟล์ไม่สมบูรณ์ทิ้งก่อนเลือก
  **เดือนที่ยังไม่จบ (เดือนปัจจุบัน) ค่าที่ได้เป็นค่าล่าสุด ไม่ใช่ค่าสิ้นเดือน**

## Dimension SK joins per fact

| Fact | Dimensions joined |
|---|---|
| `fact_order` | dim_order, dim_company, dim_product_master, dim_customer, + `fact_quotation` (QuotationSK) — source `curated_mil` · join `dim_product_master` ด้วย `lower(milstk) = lower(ProductCode)` และ `FactOrderSk` `order by lower(milStk)` (2026-09-03 — ดู `known-issues.md`) |
| `fact_invoice` | dim_invoice, dim_company, dim_customer, + `fact_order` (deduped `QUALIFY ROW_NUMBER()=1`) — source `curated_mil` · join `fact_order` ด้วย `LOWER(milStk)` ทั้งใน `ON` และใน `QUALIFY ... PARTITION BY` (2026-09-03) |
| `fact_quotation` | dim_quotation, dim_company, dim_product_master, dim_customer — source `validated_mac5.tbook_quodetail` |
| `fact_transaction_delivery` | dim_invoice, dim_product_master, dim_company — source `curated_mil` (type='IS') |
| `fact_delivery` | dim_delivery, dim_company, + `fact_transaction_delivery` — sources `ttrip_document, ttrip, tdelivery, deb, curated_mih, curated_mil`; Thai delivery-status labels |
| `fact_transcation` | ~20 dims (see below) — source `onetime.Transaction_Data_Mart`; external `mds_data_change_marketinggroup_master` (marketing-group re-map) · dedup `QUALIFY` ทั้ง `final_part1`/`final_part2` partition ด้วย **`CompanySK` + 6 คีย์เอกสาร** ให้ตรงกับคีย์ upsert (เพิ่ม `CompanySK` 2026-09-03) และ `milStk` ใน partition เป็น `LOWER(milStk)` · join `dim_product_master` / `dim_cost_stk` / `dim_stk_mkt` ใส่ `LOWER()` สองฝั่งแล้ว (2026-09-03 — ดู `known-issues.md`) |
| `fact_chq` | dim_customer, dim_company — sources `validated_mac5.chq + cql` (`cqlbook = 0`); Thai cheque-status labels |
| `fact_mir_vs` | dim_invoice (deduped `QUALIFY`), dim_customer, dim_collection_status, dim_company — sources `validated_mac5.mir/mie` + `curated_mih` (mirtype `'VS'`, `mihcancel = 0`) |
| `fact_mir_rs` | same dims as `fact_mir_vs` + `fact_mir_vs` (BillingSK) + **FULL JOIN** `fact_chq` (FactChqSK) — mirtype `'RS'` |
| `fact_order_store` | dim_order, dim_company, dim_customer, dim_product_master, dim_store — source `curated_mih` + `curated_mil` (`mihType='PS'`) · **ตัวกรองบรรทัด (2026-09-15)**: `milstype not in (3)` + `LEFT(milstk,1) not in ('บ')` — ตัดค่าบริการ/ค่าขนส่ง ให้ตรงกับ `fact_invoice_store` · **+ `milstk NOT LIKE 'TEST%'` (2026-09-23)** ตัดสินค้าทดสอบ — ใส่ทั้ง 3 ตาราง store (`LIKE` แยกตัวพิมพ์ วัดแล้วไม่มีรหัส `test` ตัวพิมพ์อื่น) · ใบสั่งขายที่มีแต่บรรทัดพวกนี้หรือสินค้า Sourcing จะ**หายทั้งใบ** ดู `known-issues.md` · ชื่อพนักงานขาย (`pernamet`) ย้ายไปอยู่ `dim_order` แล้ว 2026-09-03 fact เก็บแค่ `mihPer` · `FlagFree` (เพิ่ม 2026-09-03, แก้นิยาม 048f746) = `'Yes'` เมื่อ `milSum = 0` **OR** `dim_product_master.ProductGroupMAC5 = '5000'` — เงื่อนไข `milDesc LIKE '%ของแถม%'` ถูก comment ออกแล้ว · **`fact_backlog_store` ใช้นิยามคนละแบบ** (`cpssumreq = 0`) ดู `known-issues.md` · `partitionBy` = `mix_date` (เดิม `asatdate` ถอดออก 2026-09-03) |
| `fact_invoice_store` | dim_invoice, dim_order, dim_company, dim_customer, dim_product_master, dim_store — เหมือน `fact_order_store` แต่ `mihType='IS'`; `InvoiceSK` = ตัวใบกำกับเอง (join `dim_invoice` บน `(CompanySK, mihVnos)` + QUALIFY dedup, แมตช์ 100% วัด 2026-09-03); `OrderSK` มาจาก `milLinkVcno` ผ่าน **LEFT JOIN** `dim_order` (dedup `(CompanySK, mihVnos)` ตาม [business order](../../okf/fact/fact_invoice_store.md#schema), **ไม่กรอง status/PO.วางบิล/อายุออร์เดอร์/order_gate** — ใบกำกับของออร์เดอร์ที่ยกเลิก/ห้ามส่งยังอยู่; ไม่เจอออร์เดอร์ = `OrderSK = -1`) (2026-10-21); สไลซ์สาขาใช้ `StoreSK` → `dim_store` (`is_store_*` 6 คอลัมน์ของ query ต้นฉบับถอดออกแล้ว 2026-09-03) · **grain รวม `milPer`** เพราะ `curated_mil` ฝั่ง IS แตกบรรทัดตามสัดส่วนพนักงานขาย · `FlagFree` (เพิ่ม 2026-09-03, แก้นิยาม 048f746) = `'Yes'` เมื่อ `milSum = 0` **OR** `dim_product_master.ProductGroupMAC5 = '5000'` — เงื่อนไข `milDesc LIKE '%ของแถม%'` ถูก comment ออกแล้ว · **`fact_backlog_store` ใช้นิยามคนละแบบ** (`cpssumreq = 0`) ดู `known-issues.md` · `partitionBy` = `mix_date` (เดิม `asatdate` ถอดออก 2026-09-03) |
| `fact_backlog_store` | dim_order, dim_company, dim_customer, dim_product_master, dim_store — source `curated_mih` + `validated_mac5.cps` (snapshot ล่าสุด) + `curated_mil` (CTE `mil_line_scope`); `SUM` ต่อ (cpsVnosID, cpsCusID, cpsStkID) · **ตัวกรองบรรทัด (2026-09-23)**: `INNER JOIN mil_line_scope` บน (company_id, cpsVnosID, cpsStkID) — ลอก `milstype not in (3)` + `LEFT(milstk,1) not in ('บ')` + `milstk NOT LIKE 'TEST%'` มาจาก `fact_order_store` เพื่อให้ 3 ตาราง store เทียบกันได้ระดับบรรทัด (ตัด 18,030 แถว / qty 4,419 = 3.3% วัด 2026-09-23; 18,029 แถวเป็นบรรทัดที่ `milstype = 3` ล้วน อีก 1 แถวไม่มีบรรทัดใน `mil` เลย) · เงื่อนไข `LEFT(cps.cpsStkID,1) not in ('บ')` ที่อยู่ใน `WHERE` เป็น **no-op** (ไม่มีแถวขึ้นต้น `บ` ใน cps เลย) เก็บไว้ประกาศเจตนา · `FlagFree` = `'Yes'` เมื่อ `cps.cpssumreq = 0` OR `ProductGroupMAC5 = '5000'` (อยู่ใน `GROUP BY`) · `partitionBy` = `sDate` (เดิม `asatdate` ถอดออก 2026-09-03) |
| `fact_saleout_mdt` | dim_sales_branch_mdt, dim_product_mdt, dim_product_mkt, dim_report, dim_region, dim_region_manager, dim_director — source `curated_saleout_mdt` · ไม่ join dim สินค้า/ลูกค้าของ MAC5 (คนละจักรวาลสินค้า) |
| `fact_saleout_monthly_mdt` | dims เดียวกับ `fact_saleout_mdt` — source `curated_saleout_monthly_mdt` |
| `fact_target_saleout_mdt` | dim_target_saleout_mdt, dim_sales_branch_mdt, dim_region, dim_region_manager, dim_director |
| `fact_target_series_mdt` | dim_target_series_mdt, dim_sales_branch_mdt, dim_region, dim_region_manager, dim_director |
| `fact_stock_mdt` | dim_sales_branch_mdt, dim_product_mdt — source `curated_stock_mdt` |
| `fact_stock_mdt_monthly` | dim เดียวกับ `fact_stock_mdt` — อ่านจาก `fact_stock_mdt` ไม่ใช่ curated |

> `fact_chq` / `fact_mir_vs` / `fact_mir_rs` were migrated into the repo **2026-07-20**
> (previously ad-hoc SQL, last rebuilt May 2026). They rebuild fully every night —
> this keeps their source data current; `CollectSK` from `dim_collection_status` is now
> stable by natural key (see
> [dimension/full-rebuild-pattern.md](../dimension/full-rebuild-pattern.md)).
> Build order via `dependencies[]`: dims → `fact_chq` → `fact_mir_vs` → `fact_mir_rs`;
> `dim_aging` (dimension_daily) reads `fact_mir_vs` and declares it as a dependency.
> Row-key contracts are owned by the [OKF cards](../../okf/fact/index.md).
> The `CollectSK` FK follows the `dim_collection_status` refresh policy.

## Stable fact row SKs

The [coding standard](../../coding-standards/sqlx-coding-standard.md#fact-row-surrogate-keys)
owns migration scope, the shared occurrence rule and producer/consumer exceptions;
each fact's [OKF card](../../okf/fact/index.md) owns its grain and schema.

## `fact_transcation` walkthrough (canonical upsert fact)

> โครงถูกจัดใหม่ 2026-08-20 (ผลลัพธ์ไม่เปลี่ยน — ยืนยันด้วย checksum) เหตุผลและตัวเลขที่วัดได้
> อยู่ใน [known-issues.md](../../operations/known-issues.md) หัวข้อการตัดสินใจเชิงออกแบบ 2026-08-20

`dependencies[]` อ้าง **view และ dimension ที่อ่านตรง** (view เหล่านั้นประกาศ dependency
ของตารางเบื้องหลังเอง) — รายการจริงอยู่ใน
[generated lineage](../../diagrams/pipeline_lineage.md#3-star-schema--what-feeds-each-fact)
ซึ่งสร้างจาก SQLX
`validated_mac5.deb` อ้างด้วย `${ref()}` จึง**ไม่**อยู่ใน `dependencies[]` (§3.1);
`onetime.mapping_invoice` เป็น BASE TABLE ที่ไม่มี `.sqlx` จึงอ้างด้วย js-block Ref แต่ไม่ list เป็น dep.
CompanySK ติดมากับ `Transaction_Data_Mart` แล้ว ไฟล์นี้จึงไม่ join `dim_company` เอง.

```
BEGIN
  1. CREATE OR REPLACE TEMP TABLE temp_fact_transcation AS
     ├─ src_dim_*        : CTE ห่อ dim ที่ถูกอ้างหลายครั้ง 9 ตัว (department, section,
     │                     section_manager, region, region_manager, director, cost_stk,
     │                     cost_group, change_district) -> แก้ชื่อตารางจุดเดียว
     │                     src_dim_change_district ทำ TRIM(customerCode) ให้ครั้งเดียว
     ├─ mds_change_mktgroup: `mds_data_change_marketinggroup_master` (is_active) +
     │                     dim_product_mkt -> NewProductMktSK (ย้ายมาจาก view 2026-08-26)
     ├─ department_change: DISTINCT CompanyID/RegionID/SectionID/StartDate/EndDate
     ├─ sale_rep         : dim_sale_representative + seq_condition
     │                     TRIM ฝั่ง dim ครั้งเดียวโดยคงชื่อคอลัมน์เดิม (* EXCEPT + ประกาศทับ)
     ├─ pre_raw_transction: Transaction_Data_Mart + Product/Payment/Channel SKs
     │                     + deb.debgroup + order-date lookup described above;
     │                     mix_date from milYear/Month/Day;
     │                     window = PARSE_DATE(milYear||Month||Day)
     │                              >= DATE_TRUNC(CURRENT_DATE - 4 YEAR, YEAR)
     ├─ raw_transction   : + onetime.mapping_invoice -> FlagMappingInvoice, SectionMappingID
     ├─ raw_part1/2      : แยกสาย ChannelCostID != / = 'COST99999' ก่อนเข้า join chain
     ├─ final_part1      : sales-org hierarchy SKs (SaleRep→Department→Region→
     │                     RegionManager→Section→SectionManager→Director) + Change* chain
     │                     QUALIFY keeps best seq_condition per line
     ├─ final_part2      : COST99999 special case — re-derive ChannelCostID via
     │                     dim_channel_cost add-on chain, re-join CostStk/CostGroup
     ├─ mix_table        : part1 UNION ALL part2
     └─ final SELECT     : + address SKs (view_deb_address_data), dim_stk_mkt,
                           dim_product_mkt, dim_target_product_group_by_sale_dayofwork,
                           dim_customer + mapping override chain (sec/reg/dir _map_sk)
                           ที่ gate ด้วย FlagMappingInvoice — Section/SectionManager/
                           Region/RegionManager/Director SK ใช้รูป CASE เดียวกัน
                           (NULL -> ค่าเดิม, 'Yes' -> ค่า mapping, 'No' -> NULL) ไม่ใช่ COALESCE
                           **Change* ทั้ง 5 ตัวไม่ผ่าน CASE นี้แล้ว** (ย้ายไปทำใน
                           view_fact_transcation 2026-08-25) ไหลผ่าน trans.* ดิบ ๆ
                           + FlagNewProductMKT / NewProductMktSK จาก mds_change_mktgroup
                           (19 กลุ่มเงื่อนไข: depcode/job/salesregion+amt/productgroup+
                           description/productid+remark) — COALESCE กลับไป
                           product_mkt.ProductMktSk เมื่อไม่ match
  2. DELETE FROM fact_transcation T WHERE EXISTS (
       SELECT 1 FROM temp WHERE T.milVnos=S.milVnos AND T.milType=S.milType
       AND T.CompanySK=S.CompanySK)
  3. INSERT INTO fact_transcation SELECT * FROM temp
END;
BEGIN  -- retention purge
  DELETE FROM fact_transcation
  WHERE mix_date < DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR);
END;
```

Because it's `operations`, the target table must already exist — Dataform does not create it.
ตารางจริงมี **124 คอลัมน์** (เดิม 116 — เพิ่ม FlagNewProductMKT/NewProductMktSK และอื่น ๆ 2026-08-26) และปิดท้ายด้วย `INSERT ... SELECT *` → ถ้าแก้ไฟล์นี้แล้วจำนวนหรือ
**ลำดับ**คอลัมน์เปลี่ยน ต้องแก้ DDL ของตารางเองด้วย (repo ไม่มี `CREATE TABLE` ของ fact นี้)

### เงื่อนไข match sale representative — ประกาศใน `js {}` ที่เดียว

เดิมเขียนซ้ำ 3 ชุด (`sale_sk` ใน part1 / `sale_sk` ใน part2 / `sale_addon` ใน part2)
ตรวจแล้ว byte-identical ต่างแค่ชื่อ alias → ยุบเป็นฟังก์ชันใน `js {}`:

```javascript
const saleRepMatchOn = (r) => `trans.mix_date BETWEEN ${r}.StartDate AND ${r}.EndDate ... `;
```
```sql
LEFT JOIN sale_rep AS sale_sk    ON ${saleRepMatchOn('sale_sk')}
LEFT JOIN sale_rep AS sale_addon ON ${saleRepMatchOn('sale_addon')}
```

equality `TRIM(IFNULL(trans.DummyChannel, trans.milPer)) = <rep>.EmployeeID` ถูกดึงออกมาเป็น
`AND` ชั้นนอกของ `CASE` (เดิมอยู่ในทุกกิ่ง) → BigQuery ใช้เป็น hash join key ได้
ยืนยันจาก query plan ว่ากลายเป็น `LEFT OUTER HASH JOIN` แล้ว (เดิมเป็น cross join + filter)
กฎการ generate SQL fragment ใน `js {}`: [coding-standards §3.4](../../coding-standards/sqlx-coding-standard.md)

### CustomerFlag ชนก่อน DepCode (2026-09-15)

สำหรับแถวที่ไม่มี OrderStartDate: CustomerFlag เก็บ list รหัสลูกค้าคั่นด้วย `|`
และอยู่บนแถวเดียวกับ DepCode
(`dim_sale_representative` ยุบแถว flag ที่ user กรอกแยกเข้ามาให้ — ดู
[dimension/special-cases.md](../dimension/special-cases.md)) กฎที่ใช้จริงคือ

> ถ้าแถวมี CustomerFlag และ `milCus` อยู่ใน list → ชนด้วย EmployeeID + customer list
> ถ้าไม่มี flag หรือลูกค้าไม่อยู่ใน list → EmployeeID + DepCode ตามเดิม

ใน `saleRepMatchOn` จึงเป็นกิ่ง DepCode กิ่งเดียวที่ `OR` กันสองเงื่อนไข และ
`SPLIT(REPLACE(<rep>.CustomerFlag, ' ', ''), '|')` กันช่องว่างรอบตัวคั่น
**กิ่ง CustomerFlag เดี่ยว ๆ ถูกลบไปแล้ว** พร้อมกับ `seq_condition = 6`

ลำดับความสำคัญของ CustomerFlag และข้อจำกัดเรื่อง renumber อยู่ที่
[`seq_condition` reference](../overview/business-flags.md#seq_condition--fact_transcation)

หลัง OrderStartDate branch เป็น **guard**: แถวที่มี CustomerFlag แต่ไม่มี DepCode / CostChannelID /
ProvinceID ให้ `FALSE` — ปกติแถวแบบนี้ถูกยุบไปแล้วตั้งแต่ dim ถ้าหลุดมาได้จะไม่กลายเป็น
catch-all ผ่าน `ELSE TRUE`

`view_fact_transcation` (ส่วน SaleRepSK join) ถือ **สำเนา** ของกฎนี้
สำหรับคอลัมน์ `*Last` ที่ join กับ `dim_sale_representative_last` — แก้ที่ไหนต้องแก้อีกที่เสมอ

วัดเมื่อ 2026-09-15 (ag01 ทั้งตาราง เทียบกฎเดิมกับกฎใหม่บน dim ปัจจุบัน): เปลี่ยน **33 แถว**
ของพนักงาน 1059254 จาก SK 254 (Lao_TA03) ไป SK 337 (Myanmar_TA01) พนักงานคนอื่นไม่ขยับ

### DepCode รับหลายค่า `A|B` (2026-10-17)

`DepCode` ของ `mds_data_sales_representative_master` เก็บได้หลายรหัสแผนก MAC5 คั่นด้วย `|`
(เช่น `TW_S1|TW_S`) ส่วนรหัสลูกค้าอยู่ใน `CustomerFlag` — กิ่ง DepCode ทั้งสองกิ่งใน
`saleRepMatchOn` (`seq_condition` 1 และ 2.5/3)
เทียบเป็น `TRIM(trans.milDep) IN UNNEST(SPLIT(REPLACE(<rep>.DepCode, ' ', ''), '|'))`
แทน `=` และ `view_fact_transcation` (สำเนากฎ `*Last`) แก้แบบเดียวกัน

ตัดอักขระช่องว่างธรรมดา (`' '`) ทุกตัวใน DepCode ก่อน split แล้วเทียบรหัสเต็มแต่ละค่า;
`dim_sale_representative` และ `dim_sale_representative_last` ยังเก็บ `A|B` เป็นค่าเดียว
(รวม partition key ของ `_last`) ไม่มีการแตกแถวต่อรหัส · `dim_customer_report_info` ใช้การเทียบ list
เดียวกันกับ `TRIM(mihDep)` ใน `inv_rows` — กฎเลือก TA อยู่ที่
[Customer Report Info](../view/view-layer.md#customer-report-info--customer-segment-2026-10-01)

- ค่าเดียวที่ไม่มีช่องว่าง (`A`) ให้ผลเท่าเดิม: `SPLIT('A','|') = ['A']` · วัด 2026-10-17 ด้วย SELECT ของ
  query ใหม่เทียบตารางปัจจุบัน: fact 2,707,406 แถว / view 2,703,216 แถว / `dim_customer_report_info`
  41,497 แถว ต่างกัน 0
- ไม่แตกแถว: `UNNEST` อยู่ใน predicate ของ join ไม่ใช่ FROM และ QUALIFY เดิมยังเลือก rep เดียวต่อบรรทัด
- `seq_condition` ไม่เปลี่ยน — แถว `A|B` อยู่ priority เดียวกับแถว `A`
- ทดสอบ: ag01/1053173 แถว `TW_S1` (SK 546) ใส่เป็น `TW_S1|TW_S` → บรรทัด `TW_S1` 746 แถวคง SK 546,
  บรรทัด `TW_S` ในช่วงวันของแถวนั้น 11 แถวย้ายจาก SK 535 (TW_OTHER) มา 546 นอกนั้นไม่ขยับ
- ข้อควรระวังเมื่อรหัสในหลายแถวซ้อนกันและขั้นตอนเปิดใช้: ดูหัวข้อ DepCode หลายค่าใน
  [Known Issues](../../operations/known-issues.md#depcode-หลายค่า-ab-ใน-mds-sales-representative-2026-10-17)

### CompanySK ต่อเป็นลูกโซ่ตาม hierarchy (2026-08-20)

join ปลายลูกโซ่ใช้ CompanySK ของ **dim ตัวก่อนหน้า** ไม่ใช่ `trans.CompanySK`
(`sale_sk` → `dep_sk` → `reg_sk`/`sec_sk` → `reg_m_sk`/`sec_m_sk`/`dir_sk`, และชุด
`change_*` / `*_addon` / `*_map_sk` เช่นเดียวกัน) รวม 28 จุด

- 27 จุดเป็น **no-op เชิงผลลัพธ์** (พิสูจน์แล้ว: ย้อนกลับเป็น `trans.CompanySK` ทั้งหมด
  แล้ว output เท่ากันเป๊ะ 0 แถวต่าง) แต่อ่านง่ายกว่าและกันพลาดตอนแก้ต่อ
- 1 จุดเป็น **การแก้บั๊กจริง**: `sec_m_map_sk` เดิมเขียน `trans.CompanySK = sec_map_sk.CompanySK`
  (เป็นจริงตลอดเพราะบรรทัดก่อนบังคับไว้แล้ว) → ไม่กรอง `dim_section_manager` ตามบริษัท
  ทำให้แถว fan-out **2,332 แถว** แก้เป็น `sec_map_sk.CompanySK = sec_m_map_sk.CompanySK`
  แล้วได้ 2,647,354 แถว ต้นเหตุฝั่งข้อมูลคือ `dim_section_manager` มี SectionID
  `Dummy999993` และ `PS1-2` อยู่ทั้ง ab01 และ ag01 ช่วงวันซ้อนกัน (SectionID เดียวในตาราง
  ที่ซ้ำข้ามบริษัท)

`department_change` ต้อง `SELECT DISTINCT CompanySK, CompanyID, ...` ด้วย เพราะ
`change_dep` / `dep_map` อ้าง `.CompanySK` — CompanyID:CompanySK เป็น 1:1 (2:2) ใน
`dim_department` จึงไม่เปลี่ยน grain ของ DISTINCT

### จุดที่ยังค้าง (บันทึกไว้ ไม่ได้แก้ 2026-08-20)

1. `sale_addon` join ด้วยเงื่อนไขเดียวกับ `sale_sk` เป๊ะ → part2 ได้ M×M แถวก่อน `QUALIFY`
   และ `ChannelCostSK` / `CostStkSk` / `CostGroupSK` **ไม่ deterministic** (571,900 กลุ่ม)
   เพราะ `ORDER BY` ระบุแค่ `sale_sk` — ยุบแล้ววัดได้ slot-ms −24% แต่ค่าบางส่วนจะเปลี่ยน
2. `QUALIFY` แยกแถวที่เสมอกันไม่ออก → **output ไม่คงที่ระหว่างรอบรัน** พิสูจน์แล้วโดยเอา
   query เดิมมาสลับลำดับ `LEFT JOIN` 2 ตัวที่ไม่เกี่ยวกัน (ไม่เปลี่ยน semantic) → ต่างกัน
   147 แถว; เปลี่ยน plan มากกว่านั้นต่างได้ถึง ~11,000 แถว แก้ได้ด้วยการเติม tiebreak
   ใน `ORDER BY` (ถือเป็นการเปลี่ยน output)
3. `CostStkSk` เป็น **NULL ทุกแถว** ทั้งใน production ปัจจุบันและ query ใหม่ (2,647,354/2,647,354)
   → join `dim_cost_stk` ไม่ match เลย ยังไม่ได้สืบว่าเป็นข้อมูล dim หรือเงื่อนไข join

## Conventions

- Fact row-SK names follow the [naming conventions](../../coding-standards/naming-conventions.md).
- `mix_date` = business date derived by `PARSE_DATE('%Y%m%d', CONCAT(milYear, milMonth, milDay))`.
- `asatdate` = `CURRENT_DATE('Asia/Bangkok')` snapshot column.
- Retention = rolling 4 years, truncated to start-of-year.
- New fact checklist → see [how-to/add-fact-table.md](../../how-to/add-fact-table.md).
