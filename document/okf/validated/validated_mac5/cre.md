---
type: BigQuery Table
title: "cre"
description: "One row = one supplier (per company), unique on (company_id, crecode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cre&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cre
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cre.sqlx"
    title: "Dataform definition (validated/mac5/cre.sqlx)"
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

Validated copy of MAC5 `cre`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Supplier (creditor) master of MAC5: names, address, tax ID, payable account and terms.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `crecode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `crecode` | STRING | Supplier (creditor) code. |
| `cregroup` | STRING | Supplier group code. |
| `crenamet` | STRING | Supplier name in Thai. |
| `crenamee` | STRING | Supplier name in English. |
| `crecontactt` | STRING | Contact person name in Thai. |
| `crecontacte` | STRING | Contact person name in English. |
| `creadd1at` | STRING | Thai address line 1 (house number, road, sub-district). |
| `creadd2at` | STRING | Thai address line 2 (usually the province). |
| `creadd3at` | STRING | Thai address line 3 (usually the postal code). |
| `creadd1ae` | STRING | English address line 1. |
| `creadd2ae` | STRING | English address line 2. |
| `creadd3ae` | STRING | English address line 3. |
| `cretel` | STRING | Supplier phone number. |
| `cretaxnos` | STRING | Supplier 13-digit tax identification number. |
| `crezone` | STRING | Zone code of the supplier. |
| `cregrade` | STRING | Grade of the supplier. |
| `crelimit` | FLOAT64 | Credit limit granted by the supplier. |
| `cretaxclass` | FLOAT64 | Withholding tax class or rate of the supplier. |
| `cregoodsdef` | INT64 | Default goods type of the supplier. |
| `crecreditterm` | INT64 | Credit term in days granted by the supplier. |
| `credate` | DATETIME | Date the supplier record was opened. |
| `crehide` | INT64 | Flag: supplier hidden from selection lists. |
| `crefax` | STRING | Supplier fax number. |
| `creemail` | STRING | Supplier email address. |
| `cretarget` | FLOAT64 | Purchase target for the supplier. |
| `crememo` | STRING | Free-text memo of the supplier. |
| `creac` | STRING | General-ledger payable account code of the supplier (e.g. 214401, 214999). |
| `crelock` | INT64 | Flag: supplier record locked against editing. |
| `creoname` | STRING | Other (alternative) name of the supplier. |
| `creprice` | STRING | Price level of the supplier. |
| `creeditlk` | DATETIME | Timestamp of the current edit lock on the supplier record. |
| `crerefwe` | STRING | Web reference of the supplier. |
| `cresortnt` | STRING | Thai sort name of the supplier. |
| `cresortne` | STRING | English sort name of the supplier. |
| `crecardid` | STRING | 13-digit national ID card number of an individual supplier. |
| `creeditdt` | DATETIME | Date and time the supplier record was last edited. |
| `creeditmf` | STRING | User code of the person who last edited the supplier record. |
| `cretaxtype` | INT64 | Tax type of the supplier (0 or 1). |
| `creinex` | INT64 | VAT inclusion mode of the supplier's prices. |
| `crebranch` | STRING | Supplier branch number for tax purposes (`00000` = head office). |

# How it is built

- Definition: `definitions/validated/mac5/cre.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cre](/initial/raw_mac5_ag01/cre.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY crenamet desc, crenamee desc, credate desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `crecode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cre`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, crecode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cre`
GROUP BY company_id, crecode
HAVING n > 1
```
