---
type: BigQuery Table
title: "vmp"
description: "One row = one reference code table (vmp), unique on (company_id, vmmonth, vmyear)."
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

Validated copy of MAC5 `vmp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: reference code table (vmp). Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `vmmonth`, `vmyear`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `vmmonth` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `vmyear` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `vmgltotal` | INT64 | Meaning not documented in the repo. |
| `vmglb1` | INT64 | Meaning not documented in the repo. |
| `vmglb2` | INT64 | Meaning not documented in the repo. |
| `vmglb3` | INT64 | Meaning not documented in the repo. |
| `vmglb4` | INT64 | Meaning not documented in the repo. |
| `vmglb5` | INT64 | Meaning not documented in the repo. |
| `vmglb6` | INT64 | Meaning not documented in the repo. |
| `vmglb7` | INT64 | Meaning not documented in the repo. |
| `vmglb8` | INT64 | Meaning not documented in the repo. |
| `vmglb9` | INT64 | Meaning not documented in the repo. |
| `vmglb10` | INT64 | Meaning not documented in the repo. |
| `vmglb11` | INT64 | Meaning not documented in the repo. |
| `vmglb12` | INT64 | Meaning not documented in the repo. |
| `vmglb13` | INT64 | Meaning not documented in the repo. |
| `vmglb14` | INT64 | Meaning not documented in the repo. |
| `vmglb15` | INT64 | Meaning not documented in the repo. |
| `vmglb16` | INT64 | Meaning not documented in the repo. |
| `vmglb17` | INT64 | Meaning not documented in the repo. |
| `vmglb18` | INT64 | Meaning not documented in the repo. |
| `vmglb19` | INT64 | Meaning not documented in the repo. |
| `vmglb20` | INT64 | Meaning not documented in the repo. |
| `vmglb21` | INT64 | Meaning not documented in the repo. |
| `vmglb22` | INT64 | Meaning not documented in the repo. |
| `vmglb23` | INT64 | Meaning not documented in the repo. |
| `vmglb24` | INT64 | Meaning not documented in the repo. |
| `vmglb25` | INT64 | Meaning not documented in the repo. |
| `vmglb26` | INT64 | Meaning not documented in the repo. |
| `vmglb27` | INT64 | Meaning not documented in the repo. |
| `vmglb28` | INT64 | Meaning not documented in the repo. |
| `vmglb29` | INT64 | Meaning not documented in the repo. |
| `vmglb30` | INT64 | Meaning not documented in the repo. |
| `vmglb31` | INT64 | Meaning not documented in the repo. |
| `vmglb32` | INT64 | Meaning not documented in the repo. |
| `vmglb33` | INT64 | Meaning not documented in the repo. |
| `vmglb34` | INT64 | Meaning not documented in the repo. |
| `vmglb35` | INT64 | Meaning not documented in the repo. |
| `vmglb36` | INT64 | Meaning not documented in the repo. |
| `vmglb37` | INT64 | Meaning not documented in the repo. |
| `vmglb38` | INT64 | Meaning not documented in the repo. |
| `vmglb39` | INT64 | Meaning not documented in the repo. |
| `vmglb40` | INT64 | Meaning not documented in the repo. |
| `vmglb41` | INT64 | Meaning not documented in the repo. |
| `vmglb42` | INT64 | Meaning not documented in the repo. |
| `vmglb43` | INT64 | Meaning not documented in the repo. |
| `vmglb44` | INT64 | Meaning not documented in the repo. |
| `vmglb45` | INT64 | Meaning not documented in the repo. |
| `vmglb46` | INT64 | Meaning not documented in the repo. |
| `vmglb47` | INT64 | Meaning not documented in the repo. |
| `vmglb48` | INT64 | Meaning not documented in the repo. |
| `vmglb49` | INT64 | Meaning not documented in the repo. |
| `vmglb50` | INT64 | Meaning not documented in the repo. |
| `vmartotal` | INT64 | Meaning not documented in the repo. |
| `vmarquo` | INT64 | Meaning not documented in the repo. |
| `vmarpo` | INT64 | Meaning not documented in the repo. |
| `vmardel` | INT64 | Meaning not documented in the repo. |
| `vmarbil` | INT64 | Meaning not documented in the repo. |
| `vmarinv` | INT64 | Meaning not documented in the repo. |
| `vmardrn` | INT64 | Meaning not documented in the repo. |
| `vmarcrn` | INT64 | Meaning not documented in the repo. |
| `vmarcash` | INT64 | Meaning not documented in the repo. |
| `vmarlease` | INT64 | Meaning not documented in the repo. |
| `vmarrec` | INT64 | Meaning not documented in the repo. |
| `vmaptotal` | INT64 | Meaning not documented in the repo. |
| `vmapquo` | INT64 | Meaning not documented in the repo. |
| `vmappo` | INT64 | Meaning not documented in the repo. |
| `vmapdel` | INT64 | Meaning not documented in the repo. |
| `vmapbil` | INT64 | Meaning not documented in the repo. |
| `vmapinv` | INT64 | Meaning not documented in the repo. |
| `vmapdrn` | INT64 | Meaning not documented in the repo. |
| `vmapcrn` | INT64 | Meaning not documented in the repo. |
| `vmapcash` | INT64 | Meaning not documented in the repo. |
| `vmaplease` | INT64 | Meaning not documented in the repo. |
| `vmaprec` | INT64 | Meaning not documented in the repo. |
| `vmictotal` | INT64 | Meaning not documented in the repo. |
| `vmicgin` | INT64 | Meaning not documented in the repo. |
| `vmicgout` | INT64 | Meaning not documented in the repo. |
| `vmicgrt` | INT64 | Meaning not documented in the repo. |
| `vmicgrf` | INT64 | Meaning not documented in the repo. |
| `vmicjour` | INT64 | Meaning not documented in the repo. |
| `vmicmstr` | INT64 | Meaning not documented in the repo. |
| `vmicpr` | INT64 | Meaning not documented in the repo. |
| `vmprtotal` | INT64 | Likely total amount (inferred from the column name only; not documented in the repo). |
| `vmprsalary` | INT64 | Meaning not documented in the repo. |
| `vmprmemo` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/vmp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.vmp](/initial/raw_mac5_ag01/vmp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY vmyear desc, vmmonth desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `vmmonth`, `vmyear`.
- Approximate size (BigQuery metadata, 2026-10-31): 240 rows, 49.1 KB.

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
