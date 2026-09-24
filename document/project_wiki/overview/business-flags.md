# Business Flags & Derived Statuses

> **LLM context**: พจนานุกรมของ "ธง" เชิงธุรกิจทุกตัวที่คำนวณในไพป์ไลน์นี้ —
> ตัวไหนนิยามที่ไหน คิดยังไง และตัวไหนนิยามไม่ตรงกันหลายที่
> อ่านหน้านี้ก่อนจะ **เพิ่มธงใหม่** หรือก่อน **เอาธงจาก fact หนึ่งไปใช้คู่กับ measure
> ของอีก fact หนึ่งใน BI** · ตรวจกับโค้ดจริง 2026-09-15

## ตารางสรุป

| Flag | นิยามอยู่ที่ | ค่า | สรุปกฎ |
|---|---|---|---|
| `FlagFree` | `fact_order_store`, `fact_invoice_store`, `fact_backlog_store` (**3 ที่ ไม่เหมือนกัน**) | `Yes`/`No` | ของแถม/ของไม่คิดเงิน |
| `FlagExpire` | `view_dim_order` | `Yes`/`No` | ใบสั่งซื้อเกินอายุตามกฎ `mds_data_document_expire_rule_master` |
| `FlagNewProductMKT` | `fact_transcation:737` | `TRUE`/`FALSE` | มี `NewProductMktSK` จาก mds mapping หรือไม่ |
| `FlagSCG` | `view_fact_transcation`, `view_dim_invoice` (UDF `fn_flag_scg`) | ข้อความไทย | ซื้อตรง / ซื้อผ่านร้าน สำหรับลูกค้ากลุ่ม SCG |
| `FlagExc` | UDF `fn_flag_exc` (ประกาศไว้ ยังไม่มีคนเรียกในชั้น view) | flag | ตัดรายการที่ cancel/status ผิดออก |
| `FlagSalesKPI` | UDF `fn_flag_sales_kpi` — เรียกใน `Transaction_Data_Mart` แต่ **ถูก comment ไว้** | `Yes`/`No` | นับเข้า KPI ขายไหม |
| `item_status` | `dim_order`, `dim_quotation` | `On Order`/`In Process`/`Complete` | เทียบบรรทัดใบสั่ง (PS) กับบรรทัดใบกำกับ (IS) |
| `seq_condition` | `fact_transcation:300–315` | `1,2,2.5,3,4,5,9` | ลำดับความแม่นของกฎจับคู่พนักงานขาย |

---

## `FlagFree` — ⚠️ นิยาม 3 แบบ ไม่ตรงกัน

นี่คือธงที่มีปัญหาที่สุดในระบบตอนนี้ — **3 fact นิยามคนละอย่าง**:

| ไฟล์ | บรรทัด | เงื่อนไข `Yes` |
|---|---:|---|
| `fact_order_store.sqlx` | 112–118 | `mil.milsum = 0.0` **or** `ProductGroupMAC5 = '5000'` **or** `IFNULL(milDesc,'') LIKE 'โปรโมชั่น%'` |
| `fact_invoice_store.sqlx` | 130–136 | `mil.milsum = 0.0` **or** `ProductGroupMAC5 = '5000'` *(เงื่อนไข `milDesc like '%ของแถม%'` ถูก comment ไว้)* |
| `fact_backlog_store.sqlx` | 113–118 | `cps.cpssumreq = 0.0` **or** `ProductGroupMAC5 = '5000'` |

ความต่างที่ต้องรู้:

1. **คนละคอลัมน์ฐาน** — order/invoice ใช้ `mil.milsum` (ยอดบรรทัดใบขาย)
   ส่วน backlog ใช้ `cps.cpssumreq` (ยอดที่ขอค้างส่ง) · เอกสารเดียวกันจึงได้ค่า
   ต่างกันได้โดยไม่มีอะไรผิด
2. **order มีเงื่อนไข `milDesc LIKE 'โปรโมชั่น%'` เพิ่มมาอีกข้อ** ที่อีกสองตัวไม่มี
3. `ProductGroupMAC5 = '5000'` เป็นข้อเดียวที่เหมือนกันทั้งสามที่

### ผลกระทบที่วัดได้ (2026-09-03 / 09-09)

- ออเดอร์ **47%** มีทั้ง `Yes` และ `No` ปนกันในใบเดียว → ถ้าเอา `FlagFree` ไปเป็น
  grouping field จะได้หลายแถวต่อหนึ่งใบเสมอ
- `fact_backlog_store` มี `FlagFree` อยู่ใน `GROUP BY` ทั้งที่มันมาจากคอลัมน์ระดับ
  `cps` แต่ละแถว → แตกเป็น **4,342 กลุ่ม (1.0%)** ที่ควรเป็นแถวเดียว
- **3,285 แถว** จะกลายเป็น `Mixed` ถ้ายุบด้วย `LOGICAL_AND`/`LOGICAL_OR`
- **19,565 แถว (5.3%)** ของ backlog ไม่มีคู่ใน `fact_order_store` เลย — เอาธงจาก
  ฝั่งหนึ่งไปใช้กับอีกฝั่งไม่ได้ตรง ๆ

### กับดักใน Power BI

`FlagFree` เป็น **column** ของ fact ตัวหนึ่ง ถ้าเอาไปวางเป็น grouping field ข้าง
**measure** ของ fact อีกตัว จะได้ cross product (เคสจริง: order 1 ใบขึ้นเป็น 4 แถว)
ธงที่นิยามต่างกัน 3 ที่ทำให้เรื่องนี้แย่ลงอีก เพราะเลขสองฝั่งไม่ตรงกันแต่แรก

### ทางแก้ที่เสนอไว้ (ยังไม่ทำ)

1. ย้ายนิยามไปไฟล์ helper เดียว (`includes/controller/function-data.js` หรือ UDF)
   แล้วให้ทั้ง 3 fact เรียกตัวเดียวกัน — ตัดสินใจก่อนว่าจะยึด `milsum` หรือ `cpssumreq`
   เป็นฐานของ backlog
2. ใน `fact_backlog_store` ถอด `FlagFree` ออกจาก `GROUP BY` แล้วยุบด้วย
   `LOGICAL_AND`/`LOGICAL_OR` → หนึ่งแถวต่อ (order, product) พร้อมค่า `Mixed`
   เมื่อในกลุ่มมีทั้งสองค่า

---

## `FlagExpire` — `view_dim_order`

```sql
CASE
  WHEN mds.ExpireDays is null THEN 'No'
  WHEN DATE_DIFF(CURRENT_DATE('Asia/Bangkok'), DATE(ord.mix_date), DAY) > mds.ExpireDays THEN 'Yes'
  ELSE 'No'
END
```

- กฎอายุมาจาก `mds_data_document_expire_rule_master` join ด้วย
  `lower(left(mihVnos,2)) = lower(DocPrefix)`
- **ประวัติ**: ค่าเดิมคือ `ELSE NULL` เปลี่ยนเป็น `ELSE 'No'` ตอนแก้บน console
  2026-09-14 แล้ว pull กลับเข้า repo 2026-09-15 — ถ้าเจอ `NULL` ในรายงานเก่า
  นั่นคือสาเหตุ
- view นี้ถูกแก้บน console **สองรอบ** (09-10 และ 09-14) — เป็นตัวที่ drift บ่อยที่สุด

## `FlagNewProductMKT` — `fact_transcation`

`IF(mds.NewProductMktSK is not null, True, False)` — เป็น BOOL ไม่ใช่ `Yes`/`No`
ใช้เป็นหนึ่งใน 4 คีย์ธรรมชาติที่ `view_fact_transcation` ใช้ join `dim_pump_information`
(`CompanySK` + `IFNULL(milStk,'')` + `FlagNewProductMKT` + `IFNULL(RegionID,'')`)

## `item_status` — `dim_order` / `dim_quotation`

```sql
CASE
  when sec.millinkvcno is null and sec.milstk is null then 'On Order'
  when sec.milQuan >= main.milQuan and sec.milSum >= main.milSum then 'Complete'
  else 'In Process'
end
```

`main` = บรรทัด PS (ใบสั่งซื้อ) · `sec` = บรรทัด IS (ใบกำกับ) ที่โยงด้วย `milLinkVcno`
— **คนละเอกสาร** ตัวพิมพ์ของรหัสสินค้าจึงต่างกันได้ จึงต้อง `lower()` ทั้งสองฝั่ง
(แก้ 2026-09-03: จับคู่เพิ่มได้ **412 คีย์** ที่เดิมตกเป็น `'On Order'` ผิด)

ระดับใบ (`OrderStatus` ใน `dim_order`): มีบรรทัด `In Process` → `In Process` ·
ไม่มีแต่มี `On Order` → `On Order` · นอกนั้น `Complete`

ตั้งแต่ 2026-09-24 `dim_order` คำนวณจาก mil ครบ window 4 ปี (ไม่กรอง `asatdate`)
และ `UPDATE SET` เขียน `OrderStatus` ทุกคืน — สถานะตาม invoice ล่าสุดเสมอ
(เดิมเขียนแค่ตอน INSERT จึงค้าง `On Order` 56,755 ใบ / `NULL` 377,982 ใบ ดู
`operations/known-issues.md` 2026-09-24)

## `seq_condition` — `fact_transcation`

ไม่ใช่ธง Yes/No แต่เป็น **ลำดับความแม่น** ของกฎจับคู่พนักงานขาย ใช้เป็นคีย์แรกใน
`ORDER BY` ของ `QUALIFY ROW_NUMBER() = 1` (เลขน้อย = แม่นกว่า = ชนะ):

| ค่า | เงื่อนไขที่ครบ (นอกจาก `EmployeeID`) |
|---:|---|
| 1 | `DepCode` + `CostChannelID` |
| 2 | `CostChannelID` |
| 2.5 | `DepCode` + `CustomerFlag` — ชนะ `DepCode` ล้วน แต่ยังแพ้กฎที่มี `CostChannelID` |
| 3 | `DepCode` |
| 4 | `ProvinceID` |
| 5 | `DepartmentID` |
| 9 | ไม่เข้ากฎไหนเลย |

`2.5` เป็นค่าที่แทรกทีหลัง (งาน CustomerFlag) จึงเป็นทศนิยม — คอลัมน์นี้จึงเป็น
`FLOAT64` ไม่ใช่ `INT64` ระวังตอนเทียบ

## UDF ที่เป็นธง

รายละเอียด signature ครบทุกตัว: [initial/initial-layer.md](../initial/initial-layer.md)

| UDF | สถานะการใช้งานจริง |
|---|---|
| `fn_flag_scg(mihvnos, mihcus)` | ใช้จริงใน `view_fact_transcation`, `view_dim_invoice` |
| `fn_flag_sales_kpi(mihcancel, mihstatus, rebate)` | **ถูก comment ไว้** ใน `Transaction_Data_Mart` — ประกาศแต่ไม่ได้เรียก |
| `fn_flag_exc(mihcancel, mihstatus, FlagExc)` | ประกาศไว้ ยังไม่พบที่เรียกในชั้น view |
| `fn_order_type(mihref2)` | ใช้ใน `view_dim_order` → `OrderType` (`Online-AllkonsM` / `Offline`) |

## กฎเวลาจะเพิ่มธงใหม่

1. **นิยามที่เดียว** — ถ้าต้องใช้หลาย fact ให้ทำเป็น UDF ใน `function_dataset`
   หรือ helper ใน `function-data.js` อย่าก็อปปี้ `CASE` ไปวางซ้ำ
2. **อย่าใส่ธงระดับบรรทัดลงใน `GROUP BY` ของ fact ที่ grain เป็นเอกสาร** —
   จะแตกแถวเงียบ ๆ (เคส `fact_backlog_store` 1.0%)
3. ถ้า BI จะเอาธงไปใช้ ต้องอยู่ใน fact เดียวกับ measure ที่จะวางคู่กัน
   ไม่งั้นได้ cross product
4. เพิ่มแถวในตารางสรุปหน้านี้ พร้อมไฟล์+บรรทัดที่นิยาม
