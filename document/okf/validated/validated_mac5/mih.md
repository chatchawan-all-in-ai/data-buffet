---
type: BigQuery Table
title: "mih"
description: "One row = one invoice/document header (one row per document, per company), unique on (company_id, MIHtype, MIHvnos)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mih&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mih.sqlx"
    title: "Dataform definition (validated/mac5/mih.sqlx)"
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

Validated copy of MAC5 `mih` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: invoice/document header (one row per document, per company). Table meaning is inferred from column prefixes.
Used by: [curated_mac5.curated_mih](/curated/curated_mac5/curated_mih.md), [validated_mac5.mil](/validated/validated_mac5/mil.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row per `company_id`, `MIHtype`, `MIHvnos`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mihday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `mihmonth` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `mihyear` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `mihtype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `mihvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `mihcus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `mihjob` | STRING | Meaning not documented in the repo. |
| `mihdep` | STRING | Meaning not documented in the repo. |
| `mihper` | STRING | Meaning not documented in the repo. |
| `mihdoc` | STRING | Meaning not documented in the repo. |
| `mihmec` | STRING | Meaning not documented in the repo. |
| `mihvatno` | STRING | Meaning not documented in the repo. |
| `mihdesc` | STRING | Meaning not documented in the repo. |
| `mihmemo` | STRING | Meaning not documented in the repo. |
| `mihnotes` | STRING | Meaning not documented in the repo. |
| `mihref1` | STRING | Meaning not documented in the repo. |
| `mihref2` | STRING | Meaning not documented in the repo. |
| `mihref3` | STRING | Meaning not documented in the repo. |
| `mihdischt1` | STRING | Meaning not documented in the repo. |
| `mihdischt2` | STRING | Meaning not documented in the repo. |
| `mihdelvsite` | STRING | Meaning not documented in the repo. |
| `mihdelvdate` | DATETIME | Meaning not documented in the repo. |
| `mihstanding` | INT64 | Meaning not documented in the repo. |
| `mihlinkgl` | INT64 | Meaning not documented in the repo. |
| `mihnouplink` | INT64 | Meaning not documented in the repo. |
| `mihnolist` | INT64 | Meaning not documented in the repo. |
| `mihcurc` | INT64 | Meaning not documented in the repo. |
| `mihvatinlist` | INT64 | Meaning not documented in the repo. |
| `mihlock` | INT64 | Meaning not documented in the repo. |
| `mihprintn` | INT64 | Meaning not documented in the repo. |
| `mihcheque` | INT64 | Meaning not documented in the repo. |
| `mihcancel` | INT64 | Likely cancel flag (inferred from the column name only; not documented in the repo). |
| `mihstatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `mihclearum` | INT64 | Meaning not documented in the repo. |
| `mihctermno` | INT64 | Meaning not documented in the repo. |
| `mihcog` | FLOAT64 | Meaning not documented in the repo. |
| `mihcog_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mihvatsum` | FLOAT64 | Meaning not documented in the repo. |
| `mihvatsum_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mihnetsum` | FLOAT64 | Meaning not documented in the repo. |
| `mihnetsum_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mihdisclst` | FLOAT64 | Meaning not documented in the repo. |
| `mihdisclst_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mihdischf1` | FLOAT64 | Meaning not documented in the repo. |
| `mihdischf1_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mihdischf2` | FLOAT64 | Meaning not documented in the repo. |
| `mihdischf2_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mihexchg` | FLOAT64 | Meaning not documented in the repo. |
| `mihextrasum` | FLOAT64 | Meaning not documented in the repo. |
| `mihextravat` | FLOAT64 | Meaning not documented in the repo. |
| `mihextracut` | INT64 | Meaning not documented in the repo. |
| `mihextramem` | STRING | Meaning not documented in the repo. |
| `mihrecno` | STRING | Meaning not documented in the repo. |
| `mihrecdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `mihsavetag` | STRING | Meaning not documented in the repo. |
| `mihkeyuser` | STRING | Meaning not documented in the repo. |
| `mihkeydate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `mihdocrunno` | STRING | Meaning not documented in the repo. |
| `mihdategl` | DATETIME | Meaning not documented in the repo. |
| `mihduepo` | DATETIME | Meaning not documented in the repo. |
| `miheditlk` | DATETIME | Meaning not documented in the repo. |
| `mihiscf` | INT64 | Meaning not documented in the repo. |
| `mihissp` | INT64 | Meaning not documented in the repo. |
| `mihdates1` | DATETIME | Meaning not documented in the repo. |
| `mihdates2` | DATETIME | Meaning not documented in the repo. |
| `mihnumsi` | INT64 | Meaning not documented in the repo. |
| `mihnumsc` | FLOAT64 | Meaning not documented in the repo. |
| `mihvatpc` | FLOAT64 | Meaning not documented in the repo. |
| `mihincluded` | INT64 | Meaning not documented in the repo. |
| `mihtaxvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `mihtaxdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `mihtaxsum` | FLOAT64 | Meaning not documented in the repo. |
| `mihload` | INT64 | Meaning not documented in the repo. |
| `mihpaiddate` | DATETIME | Meaning not documented in the repo. |
| `mihbookordernum` | STRING | Meaning not documented in the repo. |
| `mihsenddate` | DATETIME | Meaning not documented in the repo. |
| `mihbl` | INT64 | Meaning not documented in the repo. |
| `mihrpv` | INT64 | Meaning not documented in the repo. |
| `mihclearcut` | INT64 | Meaning not documented in the repo. |
| `mihsettlecut` | INT64 | Meaning not documented in the repo. |
| `moddate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `mihmemo_new` | STRING | Meaning not documented in the repo. |
| `memo_extract` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mih.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mih](/initial/raw_mac5_ag01/mih.md), [raw_mac5_aa05.mih](/initial/raw_mac5_aa05/mih.md), [raw_mac5_ab01.mih](/initial/raw_mac5_ab01/mih.md), [raw_mac5_ac02.mih](/initial/raw_mac5_ac02/mih.md), [raw_mac5_ak02.mih](/initial/raw_mac5_ak02/mih.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `MIHtype`, `MIHvnos`.
- Same document-grain purge pattern as `mil`/`mir`; for `mih` (one row per document) it is effectively a no-op.
- Approximate size (BigQuery metadata, 2026-10-31): 3,965,212 rows, 2.9 GB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mih`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MIHtype, MIHvnos, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mih`
GROUP BY company_id, MIHtype, MIHvnos
HAVING n > 1
```
