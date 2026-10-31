---
type: BigQuery Table
title: "saleout_hp"
description: "One row = one cleaned copy of the source table `saleout_hp`, unique on (siteno, artno, sale_date)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_saleout_mdt&t=saleout_hp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_saleout_mdt
table_id: saleout_hp
tags: ["validated", "validated_saleout_mdt", "saleout", "validated_incremental", "saleout_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/saleout_mdt/HP/saleout_hp.sqlx"
    title: "Dataform definition (validated/saleout_mdt/HP/saleout_hp.sqlx)"
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

Validated copy of SALEOUT_MDT `saleout_hp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
Used by: [curated_saleout_mdt.curated_saleout_mdt](/curated/curated_saleout_mdt/curated_saleout_mdt.md).

# Grain and key

One row per `siteno`, `artno`, `sale_date`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `sale_date` | DATE | Meaning not documented in the repo. |
| `store_code` | STRING | Meaning not documented in the repo. |
| `siteno` | STRING | Meaning not documented in the repo. |
| `sitename` | STRING | Meaning not documented in the repo. |
| `artno` | STRING | Meaning not documented in the repo. |
| `artdesc` | STRING | Meaning not documented in the repo. |
| `vdartno` | STRING | Meaning not documented in the repo. |
| `vdartdesc` | STRING | Meaning not documented in the repo. |
| `artean` | STRING | Meaning not documented in the repo. |
| `itemno` | STRING | Meaning not documented in the repo. |
| `mch3` | STRING | Meaning not documented in the repo. |
| `mch2desc` | STRING | Meaning not documented in the repo. |
| `mch1desc` | STRING | Meaning not documented in the repo. |
| `vendorno` | STRING | Meaning not documented in the repo. |
| `vendorname` | STRING | Meaning not documented in the repo. |
| `qty` | INT64 | Likely quantity (inferred from the column name only; not documented in the repo). |
| `value` | FLOAT64 | Meaning not documented in the repo. |
| `is_return` | BOOL | Meaning not documented in the repo. |
| `periodtype` | STRING | Meaning not documented in the repo. |
| `crdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/saleout_mdt/HP/saleout_hp.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`, `saleout_daily`).
- Reads: [raw_saleout_mdt.saleout_hp](/initial/raw_saleout_mdt/saleout_hp.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY ASATDATE DESC, value DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `siteno`, `artno`.
- Approximate size (BigQuery metadata, 2026-10-31): 45,982 rows, 13.6 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_hp`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT siteno, artno, sale_date, COUNT(*) AS n
FROM `databuffet-nonprd.validated_saleout_mdt.saleout_hp`
GROUP BY siteno, artno, sale_date
HAVING n > 1
```
