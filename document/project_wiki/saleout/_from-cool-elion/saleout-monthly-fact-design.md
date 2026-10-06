# ออกแบบ fact ยอดขายออกรายเดือน (MDT)

ร่าง 2026-09-28 · **สร้าง `definitions/fact/fact_saleout_monthly_mdt.sqlx` แล้ว 2026-09-29**
ต้นทางยังเป็นตารางชั่วคราว `onetime.saleout_monthly_mock_2026` (โหลดจาก CSV ด้วยมือ)
รอไฟล์ขึ้น GCS แล้วทำชั้น initial/validated → แก้ `SourceRef` บรรทัดเดียว

## ทำไมต้องมี

ห้างส่งไฟล์สรุปรายเดือนมาให้ต่างหากจากฟีดรายวัน ตัวอย่างอยู่ที่
`~/Downloads/Raw Data Monty/` (เดือน ส.ค. 2026 · ได้มา 2026-09-28)

**ผู้ใช้ตัดสินแล้ว 2026-09-28: ทำเป็น fact แยก ไว้เทียบอย่างเดียว ไม่เอาไปอุดยอดในฟีดรายวัน**
จึงไม่มีความเสี่ยงยอดซ้ำ และไม่ต้องตั้งวันตัดแบบที่ backlog ข้อ 13 เตือนไว้สำหรับ DH

## เกรน

**1 แถว = 1 ห้าง x 1 สาขา x 1 ช่องทางขาย x 1 สินค้า x 1 เดือน**

ช่องทางขายมีแค่ BT ที่ส่งมา ห้างอื่นใส่ `'-'` ไว้ ไม่ใช้ NULL เพราะ NULL ในคีย์
ทำให้ join และ GROUP BY ไม่ตรงกันเงียบ ๆ

## ต้นทางแต่ละห้าง

| ห้าง | ไฟล์ | เกรนต้นทาง | ต้องทำอะไร |
|---|---|---|---|
| HP/MH | `VRM_..._202608.csv` | สินค้า x สาขา x เดือน | ตรงเกรนแล้ว · แยก MH ออกจาก HP ด้วยตัวอักษรแรกของ SITENO เหมือนฟีดรายวัน |
| GH | `GH_Aug 26_Final.xlsx` 1 ชีต 4,034 แถว | **รายบิล x สินค้า x วัน** | ยุบขึ้นเดือน |
| BT | `BT_Aug 26_Final.xlsx` ชีต `Sale by branch detail` 175 แถว | สินค้า x สาขา x ช่องทาง x เดือน | ตรงเกรนแล้ว |
| TW | `TW_Aug 26_Final.xls` ชีต `ReportSaleSubscriptionMonth` 5,564 แถว | สินค้า x สาขา x เดือน | ตรงเกรนแล้ว · หัวตารางอยู่แถว 6 ไม่ใช่แถว 1 |
| DH | `DH_Aug 26.zip` 28 ไฟล์ | รายบิล x สินค้า x วัน | **พักไว้** — ดู backlog ข้อ 17 |

## ตารางแปลงคอลัมน์

| คอลัมน์ปลายทาง | HP | GH | BT | TW |
|---|---|---|---|---|
| `month_date` | `PERIODDATE` `08/2026` | ยุบจาก `Sale Date` | `YEAR_DATE_ID` + `MONTH_DATE_ID` | `Period :` แถว 3 |
| `store_code` | จาก `SITENO` (S=HP · M=MH) | `GH` คงที่ | `BT` คงที่ | `TW` คงที่ |
| `branch_code` | `SITENO` | `Branch Code` (`GH-101`) | `BRANCH` (ชื่อไทย) | `Store` (`61604-CRC ...`) |
| `sales_channel` | `'-'` | `'-'` | `ช่องทางการขาย` | `'-'` |
| `product_code` | `ARTNO` | `Product Code` | `ARTICLE_ID` | `SKU` |
| `sale_qty` | `QTY` | รวม `Sale Quantity` | `SALE_QTY` | `Sales Qty` |
| `sale_amount` | `VALUE` | รวม `Sale Amount` | `NET_INC_TAX` | `Sales Amount` |

## จุดที่ต้องระวัง

- **BT `NET_INC_TAX` รวม VAT แล้ว** ชื่อบอกชัด ส่วนห้างอื่นยังไม่ยืนยันว่ารวมหรือยัง
  ถ้าไม่ปรับให้ฐานเดียวกัน เทียบข้ามห้างไม่ได้ — **ต้องถาม BI**
- **รหัสสาขาคนละชุดกันทุกห้าง** GH ส่ง `GH-101` ซึ่งไม่ใช่ `GH_BK1_001` ที่ MDS ใช้
  และ BT ส่งชื่อสาขาเป็นภาษาไทยไม่ใช่รหัส ต้องทำตัวจับคู่แยกต่อห้าง
- **GH เป็นรายบิล** มี `Sale No.` กับ `Reference No.` ซึ่งฟีดรายวันไม่มี
  ถ้าอยากสืบกลับได้ ต้องเก็บไว้ใน fact อีกตัวที่เกรนรายบิล ไม่ใช่ตัวนี้

## ของแถมในไฟล์ที่ยังไม่ได้ใช้ — อย่าทิ้ง

| ที่มา | มีอะไร | ใช้ทำอะไรได้ |
|---|---|---|
| TW | `Stock On Hand` · `Stock On Order` · **`Last Sold Date`** | เทียบกับ `view_fact_stock_nonmove_mdt` ที่คำนวณวันขายล่าสุดเอง |
| BT ชีต `Stock aging` | `AGING_TIER` · **`CLASS_STOCK` = `B3G Dead`** | ห้างจัดหมวดของตายมาให้เอง เทียบกับตรรกะของเราได้ตรง ๆ |
| BT ชีต `Turnover` | `T_O` · `% Dead` รายสาขา | ตัวชี้วัดหมุนเวียนสต็อกที่เรายังไม่มี |
| BT | `SALE_SQM` · `BRAND` | หน่วยตารางเมตรและยี่ห้อ ระบบยังไม่มีทั้งคู่ |

ทั้งหมดนี้เป็นสต็อกไม่ใช่ยอดขาย **อย่าเอามาใส่ fact ตัวนี้** ทำแยกทีหลัง

## สิ่งที่ยังขาด ทำต่อไม่ได้จนกว่าจะมี

1. **ไฟล์ต้องขึ้น GCS** เสนอ `gs://file-raw-data/saleout_mdt/monthly/<ห้าง>/ASATDATE=YYYYMMDD/`
   ตอนนี้อยู่แค่ใน Downloads · ต้องตกลงกับคนดูแล Airflow ว่าใครวาง
2. **ตอบเรื่อง VAT** ยอดแต่ละห้างรวม VAT หรือยัง
3. **ตัวจับคู่รหัสสาขา** ต่อห้าง โดยเฉพาะ GH กับ BT
4. **ตกลงว่าจะเทียบอะไร** ยอดเงิน · จำนวนชิ้น · ระดับสาขา หรือลงถึงสินค้า

## โครง SQL คร่าว ๆ

ยังเขียนเป็น .sqlx ไม่ได้เพราะตาราง validated ยังไม่มี ถ้าวางไฟล์ที่อ้างตาราง
ซึ่งไม่มีจริงลงใน definitions/ จะทำให้ Dataform compile ทั้งโปรเจกต์พัง

```sql
-- definitions/fact/fact_saleout_monthly_mdt.sqlx  (ยังไม่สร้าง)
-- config: type "table" · schema FACT_TABLE · tag fact_monthly (tag นี้ประกาศไว้แล้วแต่ยังไม่มีใครใช้)
-- uniqueKey: month_date, store_code, branch_code, sales_channel, product_code

WITH hp AS (
  SELECT month_date, 'HP' AS store_code, ... FROM validated_saleout_mdt.saleout_hp_monthly
), gh AS (
  SELECT DATE_TRUNC(sale_date, MONTH) AS month_date, 'GH', ...
  FROM validated_saleout_mdt.saleout_gh_monthly GROUP BY ...
), bt AS ( ... ), tw AS ( ... ),

all_stores AS (
  SELECT * FROM hp UNION ALL SELECT * FROM gh
  UNION ALL SELECT * FROM bt UNION ALL SELECT * FROM tw
)

SELECT
  a.*,
  IFNULL(b.BranchMdtSK, -1) AS branch_sk,
  IFNULL(p.ProductMdtSK, -1) AS product_mdt_sk
FROM all_stores a
LEFT JOIN dim_sales_branch_mdt b ON ...
LEFT JOIN dim_product_mdt p ON LTRIM(a.product_code, '0') = p.ProductCode
```
