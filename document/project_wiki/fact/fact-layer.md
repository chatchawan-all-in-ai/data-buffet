# Fact Layer — `definitions/fact/`

> **LLM context**: 9 files, all in dataset `fact_table` (`databuffet.FACT_TABLE`),
> all tagged `fact_daily`. Three distinct materialization patterns — there is **no MERGE**
> in the fact layer. Dimension tables are referenced by raw string interpolation
> (`${...TableRef}`) + `dependencies[]`, while curated/validated sources use `${ref()}`.
> **Load-bearing typo**: the table/file is `fact_transcation` (not "transaction") — keep as-is.

## Inventory

| File | Target | Type | Pattern | Upsert keys | Partition / Cluster | Retention |
|---|---|---|---|---|---|---|
| `fact_order.sqlx` | `fact_order` | table | Dataform-managed rebuild | — (uniqueKey `FactOrderSk`) | `asatdate` / `FactOrderSk` | none active |
| `fact_invoice.sqlx` | `fact_invoice` | table | Dataform-managed rebuild | — (uniqueKey `FactInvoiceSK`) | `asatdate` / `FactInvoiceSK` | 4-year window in query |
| `fact_quotation.sqlx` | `fact_quotation` | operations | `DROP` + `CREATE OR REPLACE ... AS` | — | `asatdate` / `FactQuotationSK` | full refresh |
| `fact_transaction_delivery.sqlx` | `fact_transaction_delivery` | operations | `CREATE OR REPLACE TABLE AS` | — | `mix_date` / `FactTransDeliverySK` | 4-year window |
| `fact_delivery.sqlx` | `fact_delivery` | operations | `CREATE OR REPLACE TABLE AS` | — | (no partition) / `FactDeliverySK` | full refresh |
| `fact_transcation.sqlx` | `fact_transcation` | operations | **TEMP → DELETE → INSERT upsert** | `milVnos, milType, CompanySK` | `mix_date` / `milType, milVnos, milCus, milPer` | DELETE < 4-year trunc-to-year |
| `fact_chq.sqlx` | `fact_chq` | table | Dataform-managed rebuild | — (uniqueKey `FactChqSK`) | (no partition) / `FactChqSK` | full refresh |
| `fact_mir_vs.sqlx` | `fact_mir_vs` | table | Dataform-managed rebuild | — (uniqueKey `BillingSK`) | (no partition) / `BillingSK, InvoiceSK, CustomerSK` | full refresh |
| `fact_mir_rs.sqlx` | `fact_mir_rs` | table | Dataform-managed rebuild | — (uniqueKey `ReceiveSK`) | (no partition) / `ReceiveSK, FactChqSK, InvoiceSK` | full refresh |
| `fact_order_store.sqlx` | `fact_order_store` | table | Dataform-managed rebuild | — (uniqueKey `FactOrderStoreSK`) | `mix_date` / `FactOrderStoreSK` | 4-year trunc-to-year (WHERE หลัก **+ `dim_order_dedup`**, 2026-09-15) |
| `fact_invoice_store.sqlx` | `fact_invoice_store` | table | Dataform-managed rebuild | — (uniqueKey `FactInvoiceStoreSK`) · grain รวม `milPer` | `mix_date` / `FactInvoiceStoreSK` | 4-year trunc-to-year (WHERE หลัก **+ `dim_order_dedup`**, 2026-09-15) |
| `fact_backlog_store.sqlx` | `fact_backlog_store` | table | Dataform-managed rebuild | — (uniqueKey `FactBacklogStoreSK`) | `sDate` / `FactBacklogStoreSK` | snapshot ล่าสุดของ `cps` **+ 4-year trunc-to-year** (WHERE หลัก + `dim_order_dedup`, 2026-09-15) |

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
| `fact_order_store` | dim_order, dim_company, dim_customer, dim_product_master, dim_store — source `curated_mih` + `curated_mil` (`mihType='PS'`) · **ตัวกรองบรรทัด (2026-09-15)**: `milstype not in (3)` + `LEFT(milstk,1) not in ('บ')` — ตัดค่าบริการ/ค่าขนส่ง ให้ตรงกับ `fact_invoice_store` · ใบสั่งขายที่มีแต่บรรทัดพวกนี้หรือสินค้า Sourcing จะ**หายทั้งใบ** ดู `known-issues.md` · ชื่อพนักงานขาย (`pernamet`) ย้ายไปอยู่ `dim_order` แล้ว 2026-09-03 fact เก็บแค่ `mihPer` · `FlagFree` (เพิ่ม 2026-09-03, แก้นิยาม 048f746) = `'Yes'` เมื่อ `milSum = 0` **OR** `dim_product_master.ProductGroupMAC5 = '5000'` — เงื่อนไข `milDesc LIKE '%ของแถม%'` ถูก comment ออกแล้ว · **`fact_backlog_store` ใช้นิยามคนละแบบ** (`cpssumreq = 0`) ดู `known-issues.md` · `partitionBy` = `mix_date` (เดิม `asatdate` ถอดออก 2026-09-03) |
| `fact_invoice_store` | dim_invoice, dim_order, dim_company, dim_customer, dim_product_master, dim_store — เหมือน `fact_order_store` แต่ `mihType='IS'`; `InvoiceSK` = ตัวใบกำกับเอง (join `dim_invoice` บน `(CompanySK, mihVnos)` + QUALIFY dedup, แมตช์ 100% วัด 2026-09-03); `OrderSK` มาจาก `milLinkVcno` เมื่อ `milLinkVcType='PS'`; สไลซ์สาขาใช้ `StoreSK` → `dim_store` (`is_store_*` 6 คอลัมน์ของ query ต้นฉบับถอดออกแล้ว 2026-09-03) · **grain รวม `milPer`** เพราะ `curated_mil` ฝั่ง IS แตกบรรทัดตามสัดส่วนพนักงานขาย · `FlagFree` (เพิ่ม 2026-09-03, แก้นิยาม 048f746) = `'Yes'` เมื่อ `milSum = 0` **OR** `dim_product_master.ProductGroupMAC5 = '5000'` — เงื่อนไข `milDesc LIKE '%ของแถม%'` ถูก comment ออกแล้ว · **`fact_backlog_store` ใช้นิยามคนละแบบ** (`cpssumreq = 0`) ดู `known-issues.md` · `partitionBy` = `mix_date` (เดิม `asatdate` ถอดออก 2026-09-03) |
| `fact_backlog_store` | dim_order, dim_company, dim_customer, dim_product_master, dim_store — source `curated_mih` + `validated_mac5.cps` (snapshot ล่าสุด); `SUM` ต่อ (cpsVnosID, cpsCusID, cpsStkID) · `FlagFree` = `'Yes'` เมื่อ `cps.cpssumreq = 0` OR `ProductGroupMAC5 = '5000'` (อยู่ใน `GROUP BY`) · `partitionBy` = `sDate` (เดิม `asatdate` ถอดออก 2026-09-03) |

> `fact_chq` / `fact_mir_vs` / `fact_mir_rs` were migrated into the repo **2026-07-20**
> (previously ad-hoc SQL, last rebuilt May 2026). They rebuild fully every night —
> this is what makes it safe for them to store `CollectSK` from the daily-rebuild
> `dim_collection_status` (see the condition in
> [dimension/full-rebuild-pattern.md](../dimension/full-rebuild-pattern.md)).
> Build order via `dependencies[]`: dims → `fact_chq` → `fact_mir_vs` → `fact_mir_rs`;
> `dim_aging` (dimension_daily) reads `fact_mir_vs` and declares it as a dependency.
> Their SKs (`FactChqSK`, `BillingSK`, `ReceiveSK`) are ROW_NUMBER-based and regenerate
> daily — never persist them across days.

## `fact_transcation` walkthrough (canonical upsert fact)

> โครงถูกจัดใหม่ 2026-08-20 (ผลลัพธ์ไม่เปลี่ยน — ยืนยันด้วย checksum) เหตุผลและตัวเลขที่วัดได้
> อยู่ใน [known-issues.md](../../operations/known-issues.md) หัวข้อการตัดสินใจเชิงออกแบบ 2026-08-20

`dependencies[]` อ้าง **view ที่อ่านตรง** (view เหล่านั้นประกาศ dependency ของตารางเบื้องหลังเอง):
`Transaction_Data_Mart`, `view_dim_channel`, `view_deb_address_data`
\+ dimension ที่อ่านตรง: dim_product_master, dim_payment, dim_customer, dim_cost_stk,
dim_cost_group, dim_channel_cost, dim_change_district, dim_stk_mkt, dim_product_mkt,
dim_target_product_group_by_sale_dayofwork, dim_sale_representative, dim_department,
dim_director, dim_region, dim_region_manager, dim_section, dim_section_manager.
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
     ├─ sale_rep         : dim_sale_representative + seq_condition (1, 2, 2.5, 3, 4, 5, else 9)
     │                     TRIM ฝั่ง dim ครั้งเดียวโดยคงชื่อคอลัมน์เดิม (* EXCEPT + ประกาศทับ)
     ├─ pre_raw_transction: Transaction_Data_Mart + Product/Payment/Channel SKs
     │                     + deb.debgroup; mix_date from milYear/Month/Day;
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

CustomerFlag เก็บ list รหัสลูกค้าคั่นด้วย `|` และอยู่บนแถวเดียวกับ DepCode เสมอ
(`dim_sale_representative` ยุบแถว flag ที่ user กรอกแยกเข้ามาให้ — ดู
[dimension/special-cases.md](../dimension/special-cases.md)) กฎที่ใช้จริงคือ

> ถ้าแถวมี CustomerFlag และ `milCus` อยู่ใน list → ชนด้วย EmployeeID + customer list
> ถ้าไม่มี flag หรือลูกค้าไม่อยู่ใน list → EmployeeID + DepCode ตามเดิม

ใน `saleRepMatchOn` จึงเป็นกิ่ง DepCode กิ่งเดียวที่ `OR` กันสองเงื่อนไข และ
`SPLIT(REPLACE(<rep>.CustomerFlag, ' ', ''), '|')` กันช่องว่างรอบตัวคั่น
**กิ่ง CustomerFlag เดี่ยว ๆ ถูกลบไปแล้ว** พร้อมกับ `seq_condition = 6`

`seq_condition` แทรก **2.5** (EmployeeID + DepCode + CustomerFlag) ไว้ก่อน 3
เพื่อให้แถวที่มี flag ชนะแถว DepCode ล้วนของพนักงานคนเดียวกัน แต่ยังแพ้กฎที่มี
CostChannelID (1, 2) ค่าเป็น FLOAT64 ทั้ง CASE — logic 3.1–3.7 ใน
`view_fact_transcation` ที่เทียบ `= 3` ยังทำงานเหมือนเดิม **ห้าม renumber 1–5**

กิ่งแรกของ CASE เป็น **guard**: แถวที่มี CustomerFlag แต่ไม่มี DepCode / CostChannelID /
ProvinceID ให้ `FALSE` — ปกติแถวแบบนี้ถูกยุบไปแล้วตั้งแต่ dim ถ้าหลุดมาได้จะไม่กลายเป็น
catch-all ผ่าน `ELSE TRUE`

`view_fact_transcation` (~645 seq_condition, ~661 CASE match) ถือ **สำเนา** ของกฎนี้
สำหรับคอลัมน์ `*Last` ที่ join กับ `dim_sale_representative_last` — แก้ที่ไหนต้องแก้อีกที่เสมอ

วัดเมื่อ 2026-09-15 (ag01 ทั้งตาราง เทียบกฎเดิมกับกฎใหม่บน dim ปัจจุบัน): เปลี่ยน **33 แถว**
ของพนักงาน 1059254 จาก SK 254 (Lao_TA03) ไป SK 337 (Myanmar_TA01) พนักงานคนอื่นไม่ขยับ

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

- Fact PK column: `Fact<Entity>SK` (PascalCase; casing occasionally inconsistent — `FactOrderSk`).
- `mix_date` = business date derived by `PARSE_DATE('%Y%m%d', CONCAT(milYear, milMonth, milDay))`.
- `asatdate` = `CURRENT_DATE('Asia/Bangkok')` snapshot column.
- Retention = rolling 4 years, truncated to start-of-year.
- New fact checklist → see [how-to/add-fact-table.md](../../how-to/add-fact-table.md).
