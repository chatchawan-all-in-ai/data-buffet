---
type: BigQuery Table
title: "tbook_quodetail"
description: "One row = one booking quotation detail, unique on (company_id, id)."
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

Validated copy of MAC5 `tbook_quodetail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: booking quotation detail. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_quotation](/dimension/dim_quotation.md), [fact_table.fact_quotation](/fact/fact_quotation.md).

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `linkid` | INT64 | Meaning not documented in the repo. |
| `stkcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `stkdesc` | STRING | Meaning not documented in the repo. |
| `quantity` | FLOAT64 | Meaning not documented in the repo. |
| `lp` | FLOAT64 | Meaning not documented in the repo. |
| `nd` | FLOAT64 | Meaning not documented in the repo. |
| `sd1` | FLOAT64 | Meaning not documented in the repo. |
| `sd2` | FLOAT64 | Meaning not documented in the repo. |
| `sd3` | FLOAT64 | Meaning not documented in the repo. |
| `dispercent` | FLOAT64 | Meaning not documented in the repo. |
| `crc` | FLOAT64 | Meaning not documented in the repo. |
| `price` | FLOAT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `total` | FLOAT64 | Likely total amount (inferred from the column name only; not documented in the repo). |
| `priceforag` | FLOAT64 | Meaning not documented in the repo. |
| `com` | FLOAT64 | Meaning not documented in the repo. |
| `setcb` | INT64 | Meaning not documented in the repo. |
| `type` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `sent` | STRING | Meaning not documented in the repo. |
| `datepart` | STRING | Meaning not documented in the repo. |
| `fg` | STRING | Meaning not documented in the repo. |
| `pic` | STRING | Meaning not documented in the repo. |
| `productcp` | STRING | Meaning not documented in the repo. |
| `pricecp` | FLOAT64 | Meaning not documented in the repo. |
| `uinsert` | STRING | Meaning not documented in the repo. |
| `uupdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `dinsert` | STRING | Meaning not documented in the repo. |
| `dupdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `giveaway` | STRING | Meaning not documented in the repo. |
| `givestk` | STRING | Meaning not documented in the repo. |
| `bgcount` | FLOAT64 | Meaning not documented in the repo. |
| `orderno` | INT64 | Meaning not documented in the repo. |
| `lat` | STRING | Meaning not documented in the repo. |
| `long` | STRING | Meaning not documented in the repo. |
| `mapnote` | STRING | Meaning not documented in the repo. |
| `fileupload` | STRING | Meaning not documented in the repo. |
| `city` | STRING | Meaning not documented in the repo. |
| `rdosend` | INT64 | Meaning not documented in the repo. |
| `cname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `ctel` | STRING | Meaning not documented in the repo. |
| `caddress` | STRING | Meaning not documented in the repo. |
| `checknote` | STRING | Meaning not documented in the repo. |
| `textnote` | STRING | Meaning not documented in the repo. |
| `ref_quodetail` | INT64 | Meaning not documented in the repo. |
| `productgrade` | INT64 | Meaning not documented in the repo. |
| `fobprice` | FLOAT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `isshow` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tbook_quodetail.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_quodetail](/initial/raw_mac5_ag01/tbook_quodetail.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stkdesc desc, cname desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 868,699 rows, 277.6 MB.

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
