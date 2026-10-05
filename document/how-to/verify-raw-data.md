# How-to: ตรวจข้อมูลดิบก่อน/หลังเขียนไฟล์ validated

ทุกคำสั่งในหน้านี้ **อ่านอย่างเดียว** ไม่สร้าง ไม่แก้ ไม่ลบอะไรทั้งสิ้น
ใช้ได้ก่อนรัน `initial` ด้วย — ยังไม่ต้องมีตาราง raw ใน BigQuery

## ตั้งตัวแปรครั้งเดียว

```bash
export T='t::AVRO=gs://file-raw-data/<source>/<table>/ASATDATE=<YYYYMMDD>/*'
```

`--external_table_definition` สร้างตารางชั่วคราวชื่อ `t` เฉพาะในคำสั่งนั้น จบแล้วหายไป
ไม่มีอะไรค้างใน BigQuery

---

## 1. มีตารางอะไร ข้อมูลมาวันไหนบ้าง

```bash
gsutil ls gs://file-raw-data/<source>/
gsutil ls gs://file-raw-data/<source>/<table>/
```

โฟลเดอร์ `ASATDATE=YYYYMMDD/` = 1 วัน 1 โฟลเดอร์
**ถ้าวันหายเป็นช่วง ๆ ให้ระวังเรื่อง incremental window** — job จะรันแล้วได้ 0 แถวโดยไม่ error

## 2. ดูชนิดข้อมูลทุกคอลัมน์

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" 'SELECT TO_JSON_STRING(t) AS row FROM t LIMIT 1'
```

`TO_JSON_STRING` แปลงทั้งแถวเป็น JSON — JSON ใส่ `"` เฉพาะข้อความ ตัวเลขห้ามใส่
**เครื่องหมาย `"` จึงบอกชนิดได้ฟรี ๆ**

| เห็นในผลลัพธ์ | helper ที่ต้องใช้ |
|---|---|
| `"ข้อความ"` | `cleanString` |
| `"2026-08-06 10:00:00"` (ข้อความที่เป็นวันเวลา) | `parseFlexibleDatetime` |
| `123.45` ไม่มี `"` | `castFloat64` |
| `123` ไม่มี `"` | `castInt64` |
| `true` / `false` | `castBool` |

**อย่าใช้ `--format=prettyjson` แทน** — มันใส่ `"` ให้ทุกค่ารวมทั้งตัวเลข ดูชนิดไม่ออก

### จัดหน้าให้อ่านง่ายเมื่อคอลัมน์เยอะ

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" 'SELECT TO_JSON_STRING(t) AS row FROM t LIMIT 1' 2>/dev/null \
| tail -1 | python3 -c "
import sys, json
s = sys.stdin.read().strip()
if s.startswith('\"'): s = s[1:-1].replace('\"\"', '\"')
for k, v in json.loads(s).items():
    print(f'{k:32} {json.dumps(v, ensure_ascii=False)[:110]}')
"
```

### กับดักที่เจอจริงในโปรเจกต์นี้

- **เลขที่เป็นข้อความ** — `sales_id` = `"1063048"`, `inv_no` = `"6808003456"`
  หลัก: *เลขที่ใช้ระบุตัวตน = ข้อความ / เลขที่ใช้คำนวณ = ตัวเลข*
  ถ้าแปลงเป็นตัวเลข เลข 0 นำหน้าจะหาย (`"007"` -> `7`)
- **ชื่อหลอก** — `sales_target_unit` = `"THB"`, `month_key` = `"2025-02"` (ไม่ใช่วันที่เต็ม)
- **คอลัมน์ที่เป็น `null` ทั้งคอลัมน์** — ดูจากค่าไม่ได้ ให้ดูจากชื่อ (`_at` / `_date` = วันเวลา)
  หรืออ่าน schema จาก AVRO โดยตรง (ดูข้อ 6)
- **คำสงวน** — `desc`, `order`, `group`, `all`, `case`, `end`
  ต้องครอบ backtick แล้วเปลี่ยนชื่อขาออก เช่น `desc` -> `description`

## 3. ทดสอบว่าค่าจริงแปลงได้ทุกแถว

ข้อ 2 ดูแค่แถวเดียว — แถวที่ 500,000 อาจมีค่าที่ทำ job พัง

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" \
  'SELECT COUNT(*) AS n,
          COUNTIF(<col> IS NOT NULL AND SAFE_CAST(<col> AS FLOAT64) IS NULL) AS bad
   FROM t'
```

**`bad` ต้องเป็น `0`** · เปลี่ยน `FLOAT64` -> `INT64` ตามชนิดที่ใช้จริง

สำหรับคอลัมน์วันเวลา ใช้นิพจน์เดียวกับ `parseFlexibleDatetime`:

```sql
COUNTIF(<col> IS NOT NULL AND COALESCE(
  SAFE.PARSE_DATETIME("%b %d %Y %I:%M%p", SUBSTR(<col>,1,19)),
  SAFE.PARSE_DATETIME("%Y-%m-%d %H:%M:%S", SUBSTR(<col>,1,19))) IS NULL) AS bad
```

> **ทำไมขั้นนี้จำเป็น**: `castInt64` / `castFloat64` ใน `function-data.js` **ไม่ใช่ SAFE**
> เจอค่าแปลงไม่ได้แม้แถวเดียวจะ error ทั้ง job — ต่างจาก `parseFlexibleDatetime` ที่เป็น SAFE (ได้ NULL เงียบ ๆ)

## 4. ตรวจว่า PK ใช้ได้จริง

```bash
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" \
  'SELECT COUNT(*) AS n, COUNT(DISTINCT id) AS uniq, COUNTIF(id IS NULL) AS null_id FROM t'
```

**`n` = `uniq` และ `null_id` = 0** ถึงจะใช้ `id` เป็น `uniqueKey`/`pk_key` ได้
ถ้าไม่เท่า ต้องหาคีย์ผสม (ดู `uniqueKey` ของ `validated/saleout_mdt/BT/stock_aging.sqlx` เป็นตัวอย่าง)

## 5. คอลัมน์ที่เก็บ JSON เป็นข้อความ

```bash
# มี key อะไรบ้าง
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" 'SELECT <col> FROM t LIMIT 1' 2>/dev/null \
| tail -1 | python3 -c "
import sys, json
s = sys.stdin.read().strip()
if s.startswith('\"'): s = s[1:-1].replace('\"\"', '\"')
print(json.dumps(json.loads(s), indent=2, ensure_ascii=False))
"

# cleanString จะไปแตะข้างในมั้ย
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" \
  'SELECT COUNTIF(<col> <> TRIM(<col>)) AS trim_changed,
          COUNTIF(REGEXP_CONTAINS(<col>, r"[\n\r\t]")) AS has_ctrl FROM t'

# key ไหนเป็น null บ้าง (เตรียมข้อมูลให้ชั้น curated)
bq --project_id=databuffet-nonprd query --use_legacy_sql=false --format=csv \
  --external_table_definition="$T" \
  'SELECT COUNT(*) AS n,
          COUNTIF(JSON_VALUE(<col>, "$.<key>") IS NULL) AS null_key FROM t'
```

**กฎ: คอลัมน์ JSON ใช้ `cleanString` เท่านั้น ห้ามใช้ `cleanCode`**
`cleanCode` ทำ `REGEXP_REPLACE(col, r'[\n\r\t]', '')` ซึ่งลบตัวอักษร**ข้างใน**ค่าด้วย
ส่วน `cleanString` ทำแค่ `TRIM` + `NULLIF('')` -> แตะเฉพาะหัวท้าย JSON ไม่เสียรูป

ผลตรวจจริงกับ `mac5_transactions.sales_agent_data` (931,173 แถว):
`trim_changed = 0`, `has_ctrl = 0`, `JSON_VALUE` ดึงค่าได้ทุกแถว — ยืนยันว่า `cleanString` ปลอดภัย

ชั้น validated **เก็บ JSON ดิบ ไม่แกะ** — การแกะเป็นงานของชั้น curated
ถ้าแกะตั้งแต่ validated แล้วต้นทางเพิ่ม field ใหม่ ข้อมูลนั้นจะหายไปโดยไม่มีใครรู้

> ระวังการอ่านผลผิด: `JSON_VALUE(...) IS NULL` **ไม่ได้แปลว่า JSON เสีย** — แปลว่า key นั้นไม่มีค่า
> ถ้า JSON เสียรูปจริง `JSON_VALUE` จะ error ทั้ง job ไม่ใช่คืน NULL

## 6. อ่าน schema จากไฟล์ AVRO ตรง ๆ

ใช้เมื่อคอลัมน์เป็น `null` ทั้งคอลัมน์จนดูชนิดจากค่าไม่ได้
AVRO ฝัง schema ไว้ที่หัวไฟล์เป็น JSON — โหลดแค่ 256 KB แรกพอ

```bash
gsutil cat -r 0-262143 "$(gsutil ls 'gs://file-raw-data/<source>/<table>/ASATDATE=<YYYYMMDD>/*.avro' | head -1)" \
| python3 -c "
import sys, io, fastavro
r = fastavro.reader(io.BytesIO(sys.stdin.buffer.read()))
for f in r.writer_schema['fields']:
    t = f['type']
    if isinstance(t, list): t = [x for x in t if x != 'null'][0]
    if isinstance(t, dict): t = t.get('logicalType') or t.get('type')
    print(f\"{f['name']:38} {t}\")
"
```

ต้องมี `fastavro` (`pip install fastavro`)
`bq mkdef` **ใช้แทนไม่ได้** — มันไม่พ่น schema ของ AVRO ออกมา

## 7. ตรวจโค้ดหลังเขียนเสร็จ

ตรวจ compile/SQL ตาม [README — Common Commands](../../README.md#common-commands)
และดูวิธีอ่าน compiled SQL ใน [run/debug guide](run-and-debug.md#รันด้วย-tag)

## 8. ตรวจทั้ง source ทีเดียว

ขั้น 2-4 ทำมือทีละตารางได้ แต่ถ้า source มีหลายสิบตารางจะช้า - เขียนสคริปต์ครอบก็ได้
โดยวนอ่าน schema จากหัวไฟล์ AVRO (ข้อ 6) เทียบกับ `functionData.*` ที่ใช้ในไฟล์ `.sqlx`
แล้วยิง query ตามข้อ 3 ให้ทุกคอลัมน์ที่ต้อง cast

เกณฑ์เทียบ: `string` -> `cleanString` / `double` -> `castFloat64` / `int` กับ `long` -> `castInt64` /
`boolean` -> `castBool` / `string` ที่เป็นวันเวลา -> `parseFlexibleDatetime`

**ควรทำมือตามข้อ 2-4 อย่างน้อย 2-3 ตารางก่อนเขียนสคริปต์** - ไม่งั้นวันที่สคริปต์รายงานว่าไม่ผ่าน
จะไม่รู้ว่าต้องไปดูตรงไหนต่อ

---

## ลำดับที่ควรทำ

| จังหวะ | ข้อ |
|---|---|
| ก่อนเขียนไฟล์ validated | 1 -> 2 -> (6 ถ้าเจอคอลัมน์ null ล้วน) |
| หลังเขียนเสร็จ | 3 -> 4 -> 7 |
| เจอคอลัมน์ JSON | 5 |
| เพิ่ม source ใหม่ทั้งชุด | 8 |

**ข้อ 2 กับ 7 ใช้ทุกครั้ง** ที่เหลือใช้ตามสถานการณ์

## ตรวจไฟล์ initial ด้วย

ไฟล์ `create_all_table_raw_*.sqlx` **ไม่มีชื่อคอลัมน์อยู่เลย** (BigQuery อ่าน schema จาก AVRO เอง)
สิ่งที่ต้องเทียบคือ **ชื่อตารางกับ path** ว่าตรงกับโฟลเดอร์จริงใน GCS:

```bash
grep -o 'GCS_[A-Z_]*}/[a-z0-9_]*/' definitions/initial/<source>/create_all_table_raw_<source>.sqlx \
  | sed 's|.*}/||;s|/$||' | sort -u > /tmp/in_code.txt
gsutil ls gs://file-raw-data/<source>/ | sed 's|.*/\([^/]*\)/$|\1|' | sort -u > /tmp/in_gcs.txt
diff /tmp/in_code.txt /tmp/in_gcs.txt
```

- บรรทัดขึ้นต้น `>` = มีใน GCS แต่ยังไม่ได้ทำ (อาจตั้งใจข้าม)
- บรรทัดขึ้นต้น `<` = **ทำไว้แต่ GCS ไม่มี -> path ผิด** ต้องเป็น 0 เสมอ
  ถ้ามี จะไม่มีใครรู้จนกว่าจะรันแล้วได้ตารางว่าง
