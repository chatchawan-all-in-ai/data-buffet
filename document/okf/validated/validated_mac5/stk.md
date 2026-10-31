---
type: BigQuery Table
title: "stk"
description: "One row = one stock (SKU) master, unique on (company_id, stkcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=stk&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/stk.sqlx"
    title: "Dataform definition (validated/mac5/stk.sqlx)"
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

Validated copy of MAC5 `stk` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: stock (SKU) master. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_stk_mkt](/dimension/dim_stk_mkt.md), [onetime.Product_Attribute](/view/onetime/Product_Attribute.md), [onetime.Transaction_Data_Mart](/view/onetime/Transaction_Data_Mart.md), [dimension_table.dim_product_master](/dimension/dim_product_master.md).

# Grain and key

One row per `company_id`, `stkcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `stkcode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `stkgroup` | STRING | Meaning not documented in the repo. |
| `stkcode2` | STRING | Meaning not documented in the repo. |
| `stkdesct1` | STRING | Meaning not documented in the repo. |
| `stkdesct2` | STRING | Meaning not documented in the repo. |
| `stkdesct3` | STRING | Meaning not documented in the repo. |
| `stkdesce1` | STRING | Meaning not documented in the repo. |
| `stkdesce2` | STRING | Meaning not documented in the repo. |
| `stkdesce3` | STRING | Meaning not documented in the repo. |
| `stkmax` | FLOAT64 | Meaning not documented in the repo. |
| `stkmin` | FLOAT64 | Meaning not documented in the repo. |
| `stkunit1` | INT64 | Meaning not documented in the repo. |
| `stkunit2` | INT64 | Meaning not documented in the repo. |
| `stkconv1` | FLOAT64 | Meaning not documented in the repo. |
| `stkconv2` | FLOAT64 | Meaning not documented in the repo. |
| `stksnsv` | INT64 | Meaning not documented in the repo. |
| `stkuname0` | STRING | Meaning not documented in the repo. |
| `stkuname1` | STRING | Meaning not documented in the repo. |
| `stkuname2` | STRING | Meaning not documented in the repo. |
| `stkuname3` | STRING | Meaning not documented in the repo. |
| `stkuname4` | STRING | Meaning not documented in the repo. |
| `stkuname5` | STRING | Meaning not documented in the repo. |
| `stkqu1` | FLOAT64 | Meaning not documented in the repo. |
| `stkqu2` | FLOAT64 | Meaning not documented in the repo. |
| `stkqu3` | FLOAT64 | Meaning not documented in the repo. |
| `stkqu4` | FLOAT64 | Meaning not documented in the repo. |
| `stkqu5` | FLOAT64 | Meaning not documented in the repo. |
| `stkqe1` | FLOAT64 | Meaning not documented in the repo. |
| `stkqe2` | FLOAT64 | Meaning not documented in the repo. |
| `stkqe3` | FLOAT64 | Meaning not documented in the repo. |
| `stkqe4` | FLOAT64 | Meaning not documented in the repo. |
| `stkqe5` | FLOAT64 | Meaning not documented in the repo. |
| `stkqn1` | INT64 | Meaning not documented in the repo. |
| `stkqn2` | INT64 | Meaning not documented in the repo. |
| `stkqn3` | INT64 | Meaning not documented in the repo. |
| `stkqn4` | INT64 | Meaning not documented in the repo. |
| `stkqn5` | INT64 | Meaning not documented in the repo. |
| `stkvat` | FLOAT64 | Meaning not documented in the repo. |
| `stkexpire` | INT64 | Meaning not documented in the repo. |
| `stkhide` | INT64 | Meaning not documented in the repo. |
| `stkuse2` | INT64 | Meaning not documented in the repo. |
| `stku2name` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `stkfx` | INT64 | Meaning not documented in the repo. |
| `stkacp` | STRING | Meaning not documented in the repo. |
| `stkacs` | STRING | Meaning not documented in the repo. |
| `stkacc` | STRING | Meaning not documented in the repo. |
| `stklock` | INT64 | Meaning not documented in the repo. |
| `stkmemo` | STRING | Meaning not documented in the repo. |
| `stkacc1` | STRING | Meaning not documented in the repo. |
| `stkacc2` | STRING | Meaning not documented in the repo. |
| `stkeditlk` | DATETIME | Meaning not documented in the repo. |
| `stkrefwe` | STRING | Meaning not documented in the repo. |
| `stkbarc1` | STRING | Meaning not documented in the repo. |
| `stkbarc2` | STRING | Meaning not documented in the repo. |
| `stkbarc3` | STRING | Meaning not documented in the repo. |
| `stksortnt` | STRING | Meaning not documented in the repo. |
| `stksortne` | STRING | Meaning not documented in the repo. |
| `stkeditdt` | DATETIME | Meaning not documented in the repo. |
| `stkstatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `stksto` | STRING | Meaning not documented in the repo. |
| `stkeditmf` | STRING | Meaning not documented in the repo. |
| `stkcode885` | STRING | Meaning not documented in the repo. |
| `stktype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `stksalegrp` | STRING | Meaning not documented in the repo. |
| `stksaletype` | STRING | Meaning not documented in the repo. |
| `stksalesup` | STRING | Meaning not documented in the repo. |
| `stksalegrps1` | STRING | Meaning not documented in the repo. |
| `stksalegrps2` | STRING | Meaning not documented in the repo. |
| `stksub1` | STRING | Meaning not documented in the repo. |
| `stksub2` | STRING | Meaning not documented in the repo. |
| `stksub3` | STRING | Meaning not documented in the repo. |
| `stkbrand` | STRING | Meaning not documented in the repo. |
| `stkexpand` | STRING | Meaning not documented in the repo. |
| `stklggrp` | STRING | Meaning not documented in the repo. |
| `stkgroup_dge` | STRING | Meaning not documented in the repo. |
| `stkgroup1_dge_report` | STRING | Meaning not documented in the repo. |
| `stkgroup2_dge_report` | STRING | Meaning not documented in the repo. |
| `stkgroup3_dge_report` | STRING | Meaning not documented in the repo. |
| `part_dge` | STRING | Meaning not documented in the repo. |
| `stkfpass` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/stk.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.stk](/initial/raw_mac5_ag01/stk.md), [raw_mac5_aa05.stk](/initial/raw_mac5_aa05/stk.md), [raw_mac5_ab01.stk](/initial/raw_mac5_ab01/stk.md), [raw_mac5_ac02.stk](/initial/raw_mac5_ac02/stk.md), [raw_mac5_ak02.stk](/initial/raw_mac5_ak02/stk.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY stkcode885 desc, stkeditdt desc, stkdesct1 desc, stkdesct2 desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `stkcode`.
- Approximate size (BigQuery metadata, 2026-10-31): 118,828 rows, 51.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.stk`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, stkcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.stk`
GROUP BY company_id, stkcode
HAVING n > 1
```
