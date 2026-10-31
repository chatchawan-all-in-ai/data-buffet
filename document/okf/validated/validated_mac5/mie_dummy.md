---
type: BigQuery Table
title: "mie_dummy"
description: "One row = one document extra line, staging variant, unique on (company_id, MIEday, MIEmonth, MIEyear, MIEtype, MIEvnos, MIEcus)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mie_dummy&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mie_dummy.sqlx"
    title: "Dataform definition (validated/mac5/mie_dummy.sqlx)"
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

Validated copy of MAC5 `mie_dummy`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: document extra line, staging variant. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `MIEday`, `MIEmonth`, `MIEyear`, `MIEtype`, `MIEvnos`, `MIEcus`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `mieday` | INT64 | Likely day part of the document date (inferred from the column name only; not documented in the repo). |
| `miemonth` | INT64 | Likely month part of the document date (inferred from the column name only; not documented in the repo). |
| `mieyear` | INT64 | Likely year part of the document date (inferred from the column name only; not documented in the repo). |
| `mietype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `mievnos` | STRING | Likely document number (inferred from the column name only; not documented in the repo). |
| `miecus` | STRING | Likely customer code (inferred from the column name only; not documented in the repo). |
| `mierecdt3` | FLOAT64 | Meaning not documented in the repo. |
| `mierecdt53` | FLOAT64 | Meaning not documented in the repo. |
| `mierecdrnd` | FLOAT64 | Meaning not documented in the repo. |
| `mierecdexg` | FLOAT64 | Meaning not documented in the repo. |
| `mierecdcsh` | FLOAT64 | Meaning not documented in the repo. |
| `mierecdoth` | FLOAT64 | Meaning not documented in the repo. |
| `mierecplus` | FLOAT64 | Meaning not documented in the repo. |
| `miereccash` | FLOAT64 | Meaning not documented in the repo. |
| `miereccqrd` | FLOAT64 | Meaning not documented in the repo. |
| `miectermcx` | STRING | Meaning not documented in the repo. |
| `miectermpx` | STRING | Meaning not documented in the repo. |
| `miectermax` | STRING | Meaning not documented in the repo. |
| `miectermdx` | STRING | Meaning not documented in the repo. |
| `mietag` | INT64 | Meaning not documented in the repo. |
| `miebasedt3` | FLOAT64 | Meaning not documented in the repo. |
| `miebasedt53` | FLOAT64 | Meaning not documented in the repo. |
| `miedescdt3` | STRING | Meaning not documented in the repo. |
| `miedescdt53` | STRING | Meaning not documented in the repo. |
| `miecondt3` | INT64 | Meaning not documented in the repo. |
| `miecondt53` | INT64 | Meaning not documented in the repo. |
| `mierecfc` | STRING | Meaning not documented in the repo. |
| `mierecdt32` | FLOAT64 | Meaning not documented in the repo. |
| `mierecdt532` | FLOAT64 | Meaning not documented in the repo. |
| `miebasedt32` | FLOAT64 | Meaning not documented in the repo. |
| `miebasedt532` | FLOAT64 | Meaning not documented in the repo. |
| `miedescdt32` | STRING | Meaning not documented in the repo. |
| `miedescdt532` | STRING | Meaning not documented in the repo. |
| `miecondt32` | INT64 | Meaning not documented in the repo. |
| `miecondt532` | INT64 | Meaning not documented in the repo. |
| `mieperdt3` | FLOAT64 | Meaning not documented in the repo. |
| `mieperdt32` | FLOAT64 | Meaning not documented in the repo. |
| `mieperdt53` | FLOAT64 | Meaning not documented in the repo. |
| `mieperdt532` | FLOAT64 | Meaning not documented in the repo. |
| `mietaxpayno` | STRING | Meaning not documented in the repo. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/mie_dummy.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mie_dummy](/initial/raw_mac5_ag01/mie_dummy.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `mietype`, `mievnos`, `miecus`.
- Approximate size (BigQuery metadata, 2026-10-31): 338,652 rows, 90.9 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mie_dummy`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, MIEday, MIEmonth, MIEyear, MIEtype, MIEvnos, MIEcus, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mie_dummy`
GROUP BY company_id, MIEday, MIEmonth, MIEyear, MIEtype, MIEvnos, MIEcus
HAVING n > 1
```
