---
type: BigQuery Table
title: "tbook_quodetail"
description: "One row = one quotation detail line (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_quodetail&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbook_quodetail
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_quodetail.sqlx"
    title: "Dataform definition (validated/mac5/tbook_quodetail.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `tbook_quodetail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Item lines of quotations: stock code, quantity, list price, discounts, net price, total and line type; source of fact_quotation.
Used by: [dimension_table.dim_quotation](/dimension/dim_quotation.md), [fact_table.fact_quotation](/fact/fact_quotation.md).

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Quotation detail line identifier. |
| `linkid` | INT64 | Quotation identifier (`tbook_quotation.id`) the line belongs to. |
| `stkcode` | STRING | MAC5 stock code of the item. |
| `stkdesc` | STRING | Item description. |
| `quantity` | FLOAT64 | Quoted quantity. |
| `lp` | FLOAT64 | List price per unit. |
| `nd` | FLOAT64 | Normal discount percent applied to the list price. |
| `sd1` | FLOAT64 | Step discount 1 percent. |
| `sd2` | FLOAT64 | Step discount 2 percent. |
| `sd3` | FLOAT64 | Step discount 3 percent. |
| `dispercent` | FLOAT64 | Discount amount of the line (negative value). |
| `crc` | FLOAT64 | CRC rate percent of the line. |
| `price` | FLOAT64 | Net unit price. |
| `total` | FLOAT64 | Line total amount. |
| `priceforag` | FLOAT64 | Unit price for the dealer (agent). |
| `com` | FLOAT64 | Commission amount of the line. |
| `setcb` | INT64 | Number of sets in the combo line. |
| `type` | STRING | Line type (`ขาย` = sale, `แถม` = free item, `แถมจากโปรโมชั่น` = promotion giveaway, `ข้อมูล Comboset` = combo-set component, `ชุดข้อมูลสี` = colour set). |
| `status` | STRING | Line status label (e.g. `ขายได้`, `ทำสลพ`, `แถมจากโปรโมชั่น`, `ข้อมูล Comboset`). |
| `sent` | STRING | Delivery date of the line (text). |
| `datepart` | STRING | Delivery time slot (`เช้า` = morning, `บ่าย` = afternoon). |
| `fg` | STRING | Factory or warehouse code that supplies the item (e.g. `KTB`, `HY`, `LP`, `KK`, `PK`, `UB`). |
| `pic` | STRING | Image file name attached to the line. |
| `productcp` | STRING | Competitor product or brand quoted against (e.g. `WAVE`, `BUDDY`). |
| `pricecp` | FLOAT64 | Competitor price. |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dinsert` | STRING | Date and time the row was created (text). |
| `dupdate` | STRING | Date and time the row was last updated (text). |
| `giveaway` | STRING | Giveaway flag of the line. |
| `givestk` | STRING | Stock code of the giveaway item. |
| `bgcount` | FLOAT64 | Count value of the line. |
| `orderno` | INT64 | Order number of the line. |
| `lat` | STRING | Latitude of the delivery location. |
| `long` | STRING | Longitude of the delivery location. |
| `mapnote` | STRING | Map note for the delivery location. |
| `fileupload` | STRING | Uploaded file name. |
| `city` | STRING | Province of the delivery address. |
| `rdosend` | INT64 | Delivery method option code. |
| `cname` | STRING | Customer contact name. |
| `ctel` | STRING | Customer contact phone number. |
| `caddress` | STRING | Customer delivery address. |
| `checknote` | STRING | Delivery checklist note. |
| `textnote` | STRING | Free-text note of the line, such as a paint colour formula. |
| `ref_quodetail` | INT64 | Parent quotation detail line in the same quotation (`tbook_quodetail.id`). |
| `productgrade` | INT64 | Product grade code (0, 1, 2). |
| `fobprice` | FLOAT64 | FOB price of the line. |
| `isshow` | INT64 | Show-on-quotation flag (1 = shown). |

# How it is built

- Definition: `definitions/validated/mac5/tbook_quodetail.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_quodetail](/initial/raw_mac5_ag01/tbook_quodetail.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stkdesc desc, cname desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_quodetail`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbook_quodetail`
GROUP BY company_id, id
HAVING n > 1
```
