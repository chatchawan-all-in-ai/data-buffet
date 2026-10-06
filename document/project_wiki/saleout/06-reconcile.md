# 06 · Reconcile — query ตรวจยอดประจำ

> **LLM context**: query สำเร็จรูปสำหรับตรวจว่ายอด Sales Out ถูก/ครบ/สด · ใช้หลังรันทุกครั้งที่แก้โค้ด
> และก่อนส่ง BI · ทุก query อ่านอย่างเดียว · รันด้วย
> `bq --project_id=databuffet-nonprd query --use_legacy_sql=false '<sql>'`
> · ทุก query ผ่าน `--dry_run` แล้ว (2026-10-06, สแกนไม่เกิน 21 MB) · ยังไม่ได้รันจริง ตัวเลข baseline มาจากบท 04

## 0. กติกาก่อนเทียบ (ห้ามข้าม)

1. **เทียบกับ BI เป็นรายเดือน หรือรายสัปดาห์ที่ครบ เท่านั้น** ไฟล์ BI ลงวันไม่ตรงวันขาย ถ้าเทียบรายวันจะต่างทุกวันแม้ยอดถูก
2. ไฟล์ BI มีถึง **2026-08-23** หลังจากนั้นไม่มีอะไรให้เทียบ ให้ใช้ EOM (ยอดปิดเดือนที่ห้างส่ง) แทน
3. ก่อนวัน `feed_from` (บท 05 ข้อ 5) ยอดใน curated **มาจากไฟล์ BI เอง** เทียบช่วงนั้นจะตรงแน่นอนแต่ไม่มีความหมาย
   ให้เทียบเฉพาะเดือนที่อยู่หลัง `feed_from`
4. GB: บิลคู่ที่เลขติดกันเป็นยอดจริง ไม่ใช่แถวซ้ำ
5. ยอดที่ต่างกัน**ต้องอธิบายได้** ก่อนบอกว่าผ่าน เช่น ตัดปั๊ม Hitachi, ตัด Segment `00221/00222`, TW ตัดวันที่มีไม่ถึง 30 สาขา

ตาราง:
- `C` = `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`
- `F` = `databuffet-nonprd.fact_table.fact_saleout_mdt`
- `LY` = `databuffet-nonprd.validated_saleout_mdt.saleout_lastyear`

## Q1. ความสด — ฟีดล่าสุดของแต่ละห้าง (ดูทุกเช้า)

```sql
SELECT store_code,
       MAX(sale_date) AS last_sale_date,
       DATE_DIFF(CURRENT_DATE('Asia/Bangkok'), MAX(sale_date), DAY) AS days_behind,
       MAX(asatdate) AS last_asatdate
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`
GROUP BY store_code
ORDER BY days_behind DESC
```
**อ่านผล:** HP/MH/BT ปกติช้า 1–2 วัน · TW ขึ้นกับ `Last_Sold_Date` · DH ช้าได้ถึง 1 เดือน (ห้างอัปเดือนละครั้ง)
· GB เคยค้าง 6 ก.ค. – ก.ย. **กลับมาแล้ว** (วัด 2026-10-06 ทุกห้างช้า 1 วัน ยกเว้น DH 36 วัน) · ถ้า `days_behind` ของห้างไหนโตขึ้นเรื่อย ๆ ให้ไปดู Airflow / GCS (บท 07)

## Q2. วันที่ฟีดหายทั้งวัน (หลัง feed_from)

```sql
WITH feed_start AS (
  SELECT 'HP' s, DATE '2026-02-09' d UNION ALL SELECT 'MH', DATE '2026-02-09'
  UNION ALL SELECT 'GB', DATE '2026-02-09' UNION ALL SELECT 'BT', DATE '2026-02-10'
  UNION ALL SELECT 'TW', DATE '2026-05-13' UNION ALL SELECT 'DH', DATE '2026-08-01'
), days AS (
  SELECT s AS store_code, day
  FROM feed_start, UNNEST(GENERATE_DATE_ARRAY(d, CURRENT_DATE('Asia/Bangkok') - 2)) AS day
)
SELECT d.store_code, d.day
FROM days d
LEFT JOIN (SELECT DISTINCT store_code, sale_date
           FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`) c
  ON c.store_code = d.store_code AND c.sale_date = d.day
WHERE c.sale_date IS NULL
ORDER BY 1, 2
```
**อ่านผล:** วันที่ได้ออกมาคือวันที่ไม่มียอดเลย หลัง `feed_from` จะไม่มีไฟล์ BI มาอุดแล้ว
· BT: ถ้าฟีดขาดหนึ่งวัน ยอดจะไปกองที่วันถัดไป (`date_is_estimated = TRUE`) จึงไม่หายแต่วันเพี้ยน
· รายการ GCS ที่หายในเดือน ส.ค. ดูบท 02

## Q3. เทียบกับไฟล์ BI รายเดือน (เดือนที่ครบหลัง feed_from)

```sql
WITH c AS (
  SELECT store_code, DATE_TRUNC(sale_date, MONTH) AS m, SUM(sale_amount) AS feed_amt
  FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`
  WHERE sale_date BETWEEN '2026-02-01' AND '2026-07-31'
  GROUP BY 1, 2
), ly AS (
  SELECT store_code, DATE_TRUNC(sale_date, MONTH) AS m, SUM(sale_amount) AS bi_amt
  FROM `databuffet-nonprd.validated_saleout_mdt.saleout_lastyear`
  WHERE sale_date BETWEEN '2026-02-01' AND '2026-07-31'
  GROUP BY 1, 2
)
SELECT COALESCE(c.store_code, ly.store_code) AS store_code,
       COALESCE(c.m, ly.m) AS month,
       ROUND(feed_amt) AS feed_amt, ROUND(bi_amt) AS bi_amt,
       ROUND(SAFE_DIVIDE(feed_amt - bi_amt, bi_amt) * 100, 2) AS diff_pct
FROM c FULL JOIN ly USING (store_code, m)
ORDER BY 1, 2
```
**อ่านผล:** ช่วงเดือนที่ยังไม่ถึง `feed_from` ต้องได้ ≈ 0% (ยอดมาจากไฟล์ BI เอง) · เดือนต้นทาง `feed_from` จะปนกัน
· **±1% ถือว่าผ่าน** ❓ (เกณฑ์ยังไม่ได้ตกลงกับ BI) · ถ้าเกิน ให้ไล่ตามห้าง → สาขา (Q3b)
· TW มิ.ย.–ก.ค. ขาด ~13 ลบ. เป็นของที่รู้อยู่แล้ว (ฟีดมาไม่ครบ) · comment ในโค้ดพูดถึงช่องว่าง 19% เม.ย.–ก.ค. ❓

Q3b เจาะสาขา: เพิ่ม `branch_code` ลงใน SELECT, GROUP BY และ USING ทั้งสองฝั่ง แล้วกรองห้างและเดือนที่ต้องการ

## Q4. ยอดที่ยังไม่รู้ว่าเป็นของใคร (SK = -1)

```sql
SELECT store_code,
       ROUND(SUM(sale_amount)) AS total_amt,
       ROUND(SUM(IF(branch_sk = -1, sale_amount, 0))) AS amt_branch_unknown,
       ROUND(SUM(IF(product_mdt_sk = -1, sale_amount, 0))) AS amt_product_unknown,
       ROUND(SUM(IF(region_sk = -1, sale_amount, 0))) AS amt_region_unknown,
       ROUND(SAFE_DIVIDE(SUM(IF(branch_sk = -1 OR product_mdt_sk = -1, sale_amount, 0)), SUM(sale_amount)) * 100, 2) AS pct_unknown
FROM `databuffet-nonprd.fact_table.fact_saleout_mdt`
WHERE sale_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 3 MONTH)
GROUP BY store_code
ORDER BY pct_unknown DESC
```
**อ่านผล:** baseline **0% ทุกห้าง** (วัด 2026-10-06, 3 เดือนล่าสุด — เดิม 1.5% ก่อนมี `new_branch` และ fallback กลุ่ม 999) ถ้าตัวเลขขึ้นจาก 0แปลว่ามีสาขาหรือสินค้าใหม่ที่ยังไม่อยู่ใน mds
· หาว่าเป็นรหัสไหนด้วย Q4b → ส่งรายการให้ BI/MDS เติม **ห้ามแก้ใน SQL** (บท 04 ข้อ 7)

```sql
-- Q4b: รหัสที่ map ไม่ได้ เรียงตามยอด
SELECT store_code,
       IF(branch_sk = -1, branch_code, NULL)       AS unknown_branch,
       IF(product_mdt_sk = -1, product_code, NULL) AS unknown_product,
       ROUND(SUM(sale_amount)) AS amt, COUNT(*) AS rows_
FROM `databuffet-nonprd.fact_table.fact_saleout_mdt`
WHERE (branch_sk = -1 OR product_mdt_sk = -1)
  AND sale_date >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 3 MONTH)
GROUP BY 1, 2, 3
ORDER BY amt DESC
LIMIT 50
```
สาขาที่ `dim_sales_branch_mdt` เติมเองผ่าน `new_branch` จะ**ไม่**เป็น -1 แต่จะได้ `ZoneName = 'รอข้อมูล Master'` ต้องดูด้วย Q5

## Q5. ของที่ "รอข้อมูล Master"

```sql
SELECT 'branch' AS kind, StoreCode AS store_code, BranchCode AS code
FROM `databuffet-nonprd.dimension_table.dim_sales_branch_mdt`
WHERE ZoneName = 'รอข้อมูล Master'
UNION ALL
SELECT DISTINCT 'product_mkt', f.store_code, f.product_code
FROM `databuffet-nonprd.fact_table.fact_saleout_mdt` f
JOIN `databuffet-nonprd.dimension_table.dim_product_mkt` m ON m.ProductMktSK = f.product_mkt_sk
WHERE m.MarketingGroupID = '999'
```
**อ่านผล:** สาขาหรือสินค้าที่ระบบเติมให้ชั่วคราว ยอดของพวกนี้ไปอยู่ในกลุ่ม 999 หรือโซนว่าง

## Q6. curated ไม่มีแถวซ้ำตาม key

```sql
SELECT sale_date, store_code, branch_code, product_code, doc_type, COUNT(*) AS n
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt`
GROUP BY 1, 2, 3, 4, 5
HAVING n > 1
LIMIT 20
```
**อ่านผล:** ผลต้องเป็น **0 แถว** · PK ใน BigQuery เป็น `NOT ENFORCED` จึงไม่กันซ้ำให้ ถ้ามีแถวซ้ำ ให้ดูว่า (ห้าง, วัน) นั้นมีทั้งยอดจากฟีดและยอดจากไฟล์ BI ไหม (วันตัดผิด, บท 05)

## Q7. fact = curated (ไม่มียอดหายระหว่างทาง)

```sql
SELECT 'curated' AS layer, store_code, ROUND(SUM(sale_amount)) AS amt
FROM `databuffet-nonprd.curated_saleout_mdt.curated_saleout_mdt` GROUP BY 2
UNION ALL
SELECT 'fact', store_code, ROUND(SUM(sale_amount))
FROM `databuffet-nonprd.fact_table.fact_saleout_mdt` GROUP BY 2
ORDER BY 2, 1
```
**อ่านผล:** ทุกห้างต้องเท่ากัน **ยกเว้น GB** ที่ fact ตัด Segment `00221/00222` ออก (บท 05 ข้อ 9)
ถ้าห้างอื่นไม่เท่ากัน แปลว่ามี join ที่ทำให้แถวเพิ่ม (fan-out) เช่น dim มีรหัสซ้ำ หรือช่วงวันที่ของภาคซ้อนกัน

## Q8. เป้า: สาขาที่จับไม่ได้

```sql
-- StoreCode มาจาก join สาขา จึงเป็น NULL เมื่อ -1 → ใช้ prefix ของ BranchCodeMdt แทน
SELECT SPLIT(BranchCodeMdt, '_')[OFFSET(0)] AS store_prefix,
       ROUND(SUM(Amt)) AS target_amt_unknown_branch, COUNT(*) AS rows_
FROM `databuffet-nonprd.dimension_table.dim_target_saleout_mdt`
WHERE BranchMdtSK = -1 AND BranchCodeMdt IS NOT NULL  -- ตัดแถว dummy -1
GROUP BY 1
```
**อ่านผล:** หลังแก้ GH→GB ควรได้ **0 แถว** (เดิม 163,685 แถว / 897.7 ลบ.) · วัด 2026-10-06 = 0 แถว ✅

## เช็กลิสต์หลังแก้โค้ด / ก่อนส่ง BI
| # | ตรวจ | ผ่านเมื่อ |
|---|---|---|
| 1 | Q6 แถวซ้ำ | 0 แถว |
| 2 | Q7 fact = curated | เท่ากัน (GB ต่างได้เท่ายอด Segment ที่ตัด) |
| 3 | Q4 ยอด -1 + Q5 รอ Master | Q4 = 0% · Q5 ไม่เพิ่ม |
| 4 | Q3 เทียบ BI | ต่างไม่เกินเกณฑ์ หรืออธิบายได้ |
| 5 | Q1 ความสด | ไม่มีห้างที่ช้าผิดปกติ |
