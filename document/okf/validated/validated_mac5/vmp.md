---
type: BigQuery Table
title: "vmp"
description: "One row = one month of document counts (per company), unique on (company_id, vmmonth, vmyear)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=vmp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: vmp
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/vmp.sqlx"
    title: "Dataform definition (validated/mac5/vmp.sqlx)"
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

Validated copy of MAC5 `vmp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Monthly counts of documents per module (GL books, AR, AP, inventory, payroll).
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `vmmonth`, `vmyear`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `vmmonth` | INT64 | Month (1 to 12) the counts refer to. |
| `vmyear` | INT64 | Year (AD) the counts refer to. |
| `vmgltotal` | INT64 | Total number of GL vouchers in the month. |
| `vmglb1` | INT64 | Number of GL vouchers in GL book 1 in the month. |
| `vmglb2` | INT64 | Number of GL vouchers in GL book 2 in the month. |
| `vmglb3` | INT64 | Number of GL vouchers in GL book 3 in the month. |
| `vmglb4` | INT64 | Number of GL vouchers in GL book 4 in the month. |
| `vmglb5` | INT64 | Number of GL vouchers in GL book 5 in the month. |
| `vmglb6` | INT64 | Number of GL vouchers in GL book 6 in the month. |
| `vmglb7` | INT64 | Number of GL vouchers in GL book 7 in the month. |
| `vmglb8` | INT64 | Number of GL vouchers in GL book 8 in the month. |
| `vmglb9` | INT64 | Number of GL vouchers in GL book 9 in the month. |
| `vmglb10` | INT64 | Number of GL vouchers in GL book 10 in the month. |
| `vmglb11` | INT64 | Number of GL vouchers in GL book 11 in the month. |
| `vmglb12` | INT64 | Number of GL vouchers in GL book 12 in the month. |
| `vmglb13` | INT64 | Number of GL vouchers in GL book 13 in the month. |
| `vmglb14` | INT64 | Number of GL vouchers in GL book 14 in the month. |
| `vmglb15` | INT64 | Number of GL vouchers in GL book 15 in the month. |
| `vmglb16` | INT64 | Number of GL vouchers in GL book 16 in the month. |
| `vmglb17` | INT64 | Number of GL vouchers in GL book 17 in the month. |
| `vmglb18` | INT64 | Number of GL vouchers in GL book 18 in the month. |
| `vmglb19` | INT64 | Number of GL vouchers in GL book 19 in the month. |
| `vmglb20` | INT64 | Number of GL vouchers in GL book 20 in the month. |
| `vmglb21` | INT64 | Number of GL vouchers in GL book 21 in the month. |
| `vmglb22` | INT64 | Number of GL vouchers in GL book 22 in the month. |
| `vmglb23` | INT64 | Number of GL vouchers in GL book 23 in the month. |
| `vmglb24` | INT64 | Number of GL vouchers in GL book 24 in the month. |
| `vmglb25` | INT64 | Number of GL vouchers in GL book 25 in the month. |
| `vmglb26` | INT64 | Number of GL vouchers in GL book 26 in the month. |
| `vmglb27` | INT64 | Number of GL vouchers in GL book 27 in the month. |
| `vmglb28` | INT64 | Number of GL vouchers in GL book 28 in the month. |
| `vmglb29` | INT64 | Number of GL vouchers in GL book 29 in the month. |
| `vmglb30` | INT64 | Number of GL vouchers in GL book 30 in the month. |
| `vmglb31` | INT64 | Number of GL vouchers in GL book 31 in the month. |
| `vmglb32` | INT64 | Number of GL vouchers in GL book 32 in the month. |
| `vmglb33` | INT64 | Number of GL vouchers in GL book 33 in the month. |
| `vmglb34` | INT64 | Number of GL vouchers in GL book 34 in the month. |
| `vmglb35` | INT64 | Number of GL vouchers in GL book 35 in the month. |
| `vmglb36` | INT64 | Number of GL vouchers in GL book 36 in the month. |
| `vmglb37` | INT64 | Number of GL vouchers in GL book 37 in the month. |
| `vmglb38` | INT64 | Number of GL vouchers in GL book 38 in the month. |
| `vmglb39` | INT64 | Number of GL vouchers in GL book 39 in the month. |
| `vmglb40` | INT64 | Number of GL vouchers in GL book 40 in the month. |
| `vmglb41` | INT64 | Number of GL vouchers in GL book 41 in the month. |
| `vmglb42` | INT64 | Number of GL vouchers in GL book 42 in the month. |
| `vmglb43` | INT64 | Number of GL vouchers in GL book 43 in the month. |
| `vmglb44` | INT64 | Number of GL vouchers in GL book 44 in the month. |
| `vmglb45` | INT64 | Number of GL vouchers in GL book 45 in the month. |
| `vmglb46` | INT64 | Number of GL vouchers in GL book 46 in the month. |
| `vmglb47` | INT64 | Number of GL vouchers in GL book 47 in the month. |
| `vmglb48` | INT64 | Number of GL vouchers in GL book 48 in the month. |
| `vmglb49` | INT64 | Number of GL vouchers in GL book 49 in the month. |
| `vmglb50` | INT64 | Number of GL vouchers in GL book 50 in the month. |
| `vmartotal` | INT64 | Total number of AR (sales) documents in the month. |
| `vmarquo` | INT64 | Number of AR quotations in the month. |
| `vmarpo` | INT64 | Number of AR sales orders in the month. |
| `vmardel` | INT64 | Number of AR delivery notes in the month. |
| `vmarbil` | INT64 | Number of AR billing notes in the month. |
| `vmarinv` | INT64 | Number of AR invoices in the month. |
| `vmardrn` | INT64 | Number of AR debit notes in the month. |
| `vmarcrn` | INT64 | Number of AR credit notes in the month. |
| `vmarcash` | INT64 | Number of AR cash sales in the month. |
| `vmarlease` | INT64 | Number of AR hire-purchase documents in the month. |
| `vmarrec` | INT64 | Number of AR receipts in the month. |
| `vmaptotal` | INT64 | Total number of AP (purchase) documents in the month. |
| `vmapquo` | INT64 | Number of AP supplier quotations in the month. |
| `vmappo` | INT64 | Number of AP purchase orders in the month. |
| `vmapdel` | INT64 | Number of AP goods received notes in the month. |
| `vmapbil` | INT64 | Number of AP supplier billing notes in the month. |
| `vmapinv` | INT64 | Number of AP supplier invoices in the month. |
| `vmapdrn` | INT64 | Number of AP debit notes in the month. |
| `vmapcrn` | INT64 | Number of AP credit notes in the month. |
| `vmapcash` | INT64 | Number of AP cash purchases in the month. |
| `vmaplease` | INT64 | Number of AP hire-purchase documents in the month. |
| `vmaprec` | INT64 | Number of AP payment vouchers in the month. |
| `vmictotal` | INT64 | Total number of inventory documents in the month. |
| `vmicgin` | INT64 | Number of inventory goods receipts in the month. |
| `vmicgout` | INT64 | Number of inventory goods issues in the month. |
| `vmicgrt` | INT64 | Number of inventory goods returns in the month. |
| `vmicgrf` | INT64 | Number of inventory goods refunds in the month. |
| `vmicjour` | INT64 | Number of inventory stock journal entries in the month. |
| `vmicmstr` | INT64 | Number of inventory stock transfers in the month. |
| `vmicpr` | INT64 | Number of inventory production documents in the month. |
| `vmprtotal` | INT64 | Total number of payroll documents in the month. |
| `vmprsalary` | INT64 | Number of payroll salary documents in the month. |
| `vmprmemo` | INT64 | Number of payroll memo documents in the month. |

# How it is built

- Definition: `definitions/validated/mac5/vmp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.vmp](/initial/raw_mac5_ag01/vmp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY vmyear desc, vmmonth desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `vmmonth`, `vmyear`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.vmp`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, vmmonth, vmyear, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.vmp`
GROUP BY company_id, vmmonth, vmyear
HAVING n > 1
```
