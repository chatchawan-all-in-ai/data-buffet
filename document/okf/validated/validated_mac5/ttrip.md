---
type: BigQuery Table
title: "ttrip"
description: "One row = one delivery trip (per company), unique on (company_id, frun, fcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=ttrip&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: ttrip
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/ttrip.sqlx"
    title: "Dataform definition (validated/mac5/ttrip.sqlx)"
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

Validated copy of MAC5 `ttrip`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Delivery trips of the GPS delivery app, with vehicle, release time and trip costs.
Used by: [dimension_table.dim_delivery](/dimension/dim_delivery.md), [fact_table.fact_delivery](/fact/fact_delivery.md).

# Grain and key

One row per `company_id`, `frun`, `fcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `frun` | STRING | Trip identifier (timestamp `yyMMddHHmmss` plus sequence), referenced by `ttrip_document.fmaster` and `tdelivery.fmaster`. |
| `fmaster` | STRING | Master reference of the trip. |
| `fcode` | STRING | Trip code (document number of the trip). |
| `fdate` | STRING | Date and time the trip was created (`yyyyMMddHHmmss`). |
| `fvehicle` | STRING | Vehicle registration plate of the trip. |
| `fother` | STRING | Other note of the trip. |
| `fprice` | INT64 | Trip price. |
| `fbuddy` | INT64 | Helper (buddy) allowance amount of the trip. |
| `fdeduct_detail` | STRING | Deduction detail of the trip. |
| `fdeduct_monkey` | FLOAT64 | Deduction amount of the trip (misspelled duplicate of `fdeduct_money`). |
| `fdeduct_money` | FLOAT64 | Deduction amount of the trip. |
| `ftype` | STRING | Trip type code. |
| `fcomplete` | STRING | Trip completion flag. |
| `foil` | STRING | Fuel rate code of the trip. |
| `fpass_date` | STRING | Date and time the vehicle was released for the trip (`yyyyMMddHHmmss`). |
| `fpay` | STRING | Paid flag of the trip (1 = paid). |
| `foil_deduct` | INT64 | Fuel deduction value of the trip. |
| `loadip` | INT64 | Load IP flag. |
| `loadvnos` | STRING | Loading document number. |
| `fremark` | STRING | Trip remark, such as the distance driven. |
| `flitre_price` | FLOAT64 | Fuel price value of the trip. |
| `flitre` | FLOAT64 | Fuel quantity value of the trip. |
| `fcubic` | FLOAT64 | Cubic volume loaded on the trip. |

# How it is built

- Definition: `definitions/validated/mac5/ttrip.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.ttrip](/initial/raw_mac5_ag01/ttrip.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY fdate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `frun`, `fcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.ttrip`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, frun, fcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.ttrip`
GROUP BY company_id, frun, fcode
HAVING n > 1
```
