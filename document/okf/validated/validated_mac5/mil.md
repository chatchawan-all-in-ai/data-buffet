---
type: BigQuery Table
title: "mil"
description: "One row = one document line item (invoice/delivery lines, per company), unique on (company_id, MILtype, MILvnos, MILlistNo)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mil&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mil
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mil.sqlx"
    title: "Dataform definition (validated/mac5/mil.sqlx)"
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

Validated copy of MAC5 `mil` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: document line item (invoice/delivery lines, per company). Table meaning is inferred from column prefixes.
Used by: [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md).

# Grain and key

One row per `company_id`, `MILtype`, `MILvnos`, `MILlistNo`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `milday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `milmonth` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `milyear` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `miltype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `milvnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `milcus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `milstk` | STRING | Likely stock (SKU) code (inferred from the column name only; not documented in the repo). |
| `miljob` | STRING | Meaning not documented in the repo. |
| `mildep` | STRING | Meaning not documented in the repo. |
| `milper` | STRING | Meaning not documented in the repo. |
| `mildoc` | STRING | Meaning not documented in the repo. |
| `milmec` | STRING | Meaning not documented in the repo. |
| `milsto` | STRING | Meaning not documented in the repo. |
| `milstomt` | STRING | Meaning not documented in the repo. |
| `millistno` | INT64 | Meaning not documented in the repo. |
| `milquan` | FLOAT64 | Meaning not documented in the repo. |
| `milquan_raw` | FLOAT64 | Meaning not documented in the repo. |
| `milquanp2` | FLOAT64 | Meaning not documented in the repo. |
| `miladisc` | FLOAT64 | Meaning not documented in the repo. |
| `miladisc_raw` | FLOAT64 | Meaning not documented in the repo. |
| `milcog` | FLOAT64 | Meaning not documented in the repo. |
| `milcog_raw` | FLOAT64 | Meaning not documented in the repo. |
| `milconv` | FLOAT64 | Meaning not documented in the repo. |
| `mildisca` | FLOAT64 | Meaning not documented in the repo. |
| `mildisca_raw` | FLOAT64 | Meaning not documented in the repo. |
| `mildisct` | STRING | Meaning not documented in the repo. |
| `milvat` | FLOAT64 | Meaning not documented in the repo. |
| `milvat_raw` | FLOAT64 | Meaning not documented in the repo. |
| `milsum` | FLOAT64 | Meaning not documented in the repo. |
| `milsum_raw` | FLOAT64 | Meaning not documented in the repo. |
| `milcut` | INT64 | Meaning not documented in the repo. |
| `milstype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `miluname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `mildesc` | STRING | Meaning not documented in the repo. |
| `milvcol1` | STRING | Meaning not documented in the repo. |
| `milvcol2` | STRING | Meaning not documented in the repo. |
| `milvcol3` | STRING | Meaning not documented in the repo. |
| `milvcol4` | STRING | Meaning not documented in the repo. |
| `milcurc` | INT64 | Meaning not documented in the repo. |
| `milexchg` | FLOAT64 | Meaning not documented in the repo. |
| `milacost` | FLOAT64 | Meaning not documented in the repo. |
| `milpqm` | INT64 | Meaning not documented in the repo. |
| `milpmfrom` | INT64 | Meaning not documented in the repo. |
| `milpmto` | INT64 | Meaning not documented in the repo. |
| `miltag` | INT64 | Meaning not documented in the repo. |
| `millinkvcno` | STRING | Meaning not documented in the repo. |
| `millinkvcdate` | DATETIME | Meaning not documented in the repo. |
| `millinkvctype` | STRING | Meaning not documented in the repo. |
| `millinkvcdeposit` | STRING | Meaning not documented in the repo. |
| `millinkvcid` | INT64 | Meaning not documented in the repo. |
| `milclearum` | INT64 | Meaning not documented in the repo. |
| `milexpdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `milnotes` | STRING | Meaning not documented in the repo. |
| `milnotkl` | INT64 | Meaning not documented in the repo. |
| `mildelvdt` | DATETIME | Meaning not documented in the repo. |
| `mildatesp` | DATETIME | Meaning not documented in the repo. |
| `milnumcsp` | FLOAT64 | Meaning not documented in the repo. |
| `milnumisp` | INT64 | Meaning not documented in the repo. |
| `milcost` | FLOAT64 | Meaning not documented in the repo. |
| `milucost` | FLOAT64 | Meaning not documented in the repo. |
| `miluprice` | FLOAT64 | Likely price (inferred from the column name only; not documented in the repo). |
| `milusequanp` | INT64 | Meaning not documented in the repo. |
| `milvcol5` | STRING | Meaning not documented in the repo. |
| `milfitem` | INT64 | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mil.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mil](/initial/raw_mac5_ag01/mil.md), [raw_mac5_aa05.mil](/initial/raw_mac5_aa05/mil.md), [raw_mac5_ab01.mil](/initial/raw_mac5_ab01/mil.md), [raw_mac5_ac02.mil](/initial/raw_mac5_ac02/mil.md), [raw_mac5_ak02.mil](/initial/raw_mac5_ak02/mil.md), [validated_mac5.mih](/validated/validated_mac5/mih.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `miltype`, `milvnos`.
- **Document-grain purge**: `pre_operations` builds a TEMP table of the batch and DELETEs whole documents (company_id + type + vnos) from the target before the MERGE, so lines deleted at source disappear.
- Approximate size (BigQuery metadata, 2026-10-31): 9,365,029 rows, 4.1 GB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mil`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MILtype, MILvnos, MILlistNo, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mil`
GROUP BY company_id, MILtype, MILvnos, MILlistNo
HAVING n > 1
```
