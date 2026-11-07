# How-to: เพิ่ม Fact Table

## เลือก pattern ตามลักษณะงาน (มี 3 แบบในโปรเจกต์)

| Pattern | เหมาะกับ | ตัวอย่างจริง |
|---|---|---|
| **Dataform `type: "table"`** | rebuild ทั้งก้อนได้ ข้อมูลไม่ใหญ่มาก | `fact_order`, `fact_invoice`, `fact_chq`, `fact_mir_vs`, `fact_mir_rs` |
| **`CREATE OR REPLACE TABLE AS`** (operations) | rebuild ทั้งก้อน + ต้องใช้ BigQuery scripting | `fact_delivery`, `fact_quotation`, `fact_transaction_delivery` |
| **TEMP → DELETE → INSERT upsert** (operations) | ตารางใหญ่ อัปเดตเฉพาะช่วง + retention | `fact_transcation` |

หมายเหตุ: fact layer **ไม่ใช้ MERGE**

## ขั้นตอน (pattern upsert — ซับซ้อนสุด)

### 1. กำหนด grain และ business key

- grain: 1 row คืออะไร (เช่น invoice line ต่อ sale rep)
- business key สำหรับ DELETE matching (เช่น `milVnos, milType, CompanySK`)
- ตารางเป้าหมายต้องมีใน BigQuery ก่อน (operations ไม่สร้างให้)
  พร้อม `PARTITION BY mix_date CLUSTER BY Fact<Entity>SK`

### 2. สร้าง `definitions/fact/fact_<entity>.sqlx`

```javascript
config {
  type: "operations",
  dependencies: [ /* dim ทุกตัวที่ join + view ที่ใช้ */ ],
  tags: [databuffet.TAG_FACT_DAILY],
}
js { /* TableRef ของทุก dim ที่ join */ }
```

### 3. โครง SQL

```sql
BEGIN
  CREATE OR REPLACE TEMP TABLE temp_fact_<entity> AS (
    -- CTE: grain source (ref() จาก curated) + join dim เพื่อเอา SK
    -- join dim ด้วย natural key ที่ถูก cleanString ทั้งสองฝั่ง
    -- คำนวณ mix_date = PARSE_DATE('%Y%m%d', CONCAT(year, month, day))
    -- กรอง 4 ปี: mix_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR)
  );
  DELETE FROM `${FactTableRef}` T
  WHERE EXISTS (SELECT 1 FROM temp_fact_<entity> S
                WHERE T.<key1>=S.<key1> AND T.<key2>=S.<key2> AND T.CompanySK=S.CompanySK);
  INSERT INTO `${FactTableRef}` SELECT * FROM temp_fact_<entity>;
END;

BEGIN  -- retention purge
  DELETE FROM `${FactTableRef}`
  WHERE mix_date < DATE_TRUNC(DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 4 YEAR), YEAR);
END;
```

### 4. เรื่อง SK ที่ต้องระวัง

- dim อ้างด้วย string interpolation → **ต้องใส่ชื่อ dim ใน `dependencies` เอง**
  (ref() ใช้ได้เฉพาะ curated/validated)
- Converted dimensions synchronize SKs by natural key; their SKs remain stable while
  the source key remains present. Check the [dimension inventory](../project_wiki/dimension/inventory.md)
  for exceptions: `dim_target_product_group_by_sale_dayofwork` is held and still
  regenerates `TargetBySaleDayofworkSK` on each rebuild, so do not persist that key
  across runs. Keep the dimension in `dependencies[]`; fact surrogate keys may still
  regenerate when the fact is rebuilt.
- ถ้า dim อาจไม่มี match ให้ LEFT JOIN (SK เป็น NULL แทนที่จะ drop row)
- SCD dims (มี StartDate/EndDate): join ด้วยช่วงวันที่ให้ตรงกับ `mix_date`

ตัวอย่างเต็มที่ควรอ่าน: `definitions/fact/fact_transcation.sqlx`
(sales-org hierarchy matching ด้วย seq_condition + กรณี COST99999)
ลำดับ `seq_condition` และข้อจำกัดเรื่อง renumber ดู
[business-flags.md](../project_wiki/overview/business-flags.md#seq_condition--fact_transcation)

## Checklist

- [ ] ตารางเป้าหมายมีอยู่แล้ว พร้อม partition/cluster
- [ ] business key ของ DELETE ครอบ grain จริง (ไม่งั้น row ซ้ำ)
- [ ] dim ทุกตัวอยู่ใน `dependencies`
- [ ] retention purge block แยกท้ายไฟล์
- [ ] `mix_date` + `asatdate` ตาม convention
- [ ] tag `fact_daily`
- [ ] สร้างการ์ด OKF ของตารางนี้ใน `document/okf/` (ข้อมูลตารางเท่านั้น ไม่มีคำเตือนหรือบันทึกการคุย) ตาม [okf/README.md](../okf/README.md) ใน commit เดียวกับโค้ด
- [ ] comment สั้น 1 บรรทัด บอก "ทำไม" — รายละเอียดไปไว้ใน `document/` ([coding-standard §9](../coding-standards/sqlx-coding-standard.md))
