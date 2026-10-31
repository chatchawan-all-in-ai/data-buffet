---
type: BigQuery Table
title: "mih_billing"
description: "One row = one cleaned source record of `mih_billing` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mih_billing&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mih_billing.sqlx"
    title: "Dataform definition (validated/mac5/mih_billing.sqlx)"
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

Validated copy of MAC5 `mih_billing`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: billing document header snapshot. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

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
| `mihvatsum` | FLOAT64 | Meaning not documented in the repo. |
| `mihnetsum` | FLOAT64 | Meaning not documented in the repo. |
| `mihdisclst` | FLOAT64 | Meaning not documented in the repo. |
| `mihdischf1` | FLOAT64 | Meaning not documented in the repo. |
| `mihdischf2` | FLOAT64 | Meaning not documented in the repo. |
| `mihexchg` | FLOAT64 | Meaning not documented in the repo. |
| `mihextrasum` | FLOAT64 | Meaning not documented in the repo. |
| `mihextravat` | FLOAT64 | Meaning not documented in the repo. |
| `mihextracut` | INT64 | Meaning not documented in the repo. |
| `mihextramem` | STRING | Meaning not documented in the repo. |
| `mihrecno` | STRING | Meaning not documented in the repo. |
| `mihrecdate` | DATETIME | Meaning not documented in the repo. |
| `mihsavetag` | STRING | Meaning not documented in the repo. |
| `mihkeyuser` | STRING | Meaning not documented in the repo. |
| `mihkeydate` | DATETIME | Meaning not documented in the repo. |
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
| `mihtaxvnos` | STRING | Meaning not documented in the repo. |
| `mihtaxdate` | DATETIME | Meaning not documented in the repo. |
| `mihtaxsum` | FLOAT64 | Meaning not documented in the repo. |
| `mihload` | INT64 | Meaning not documented in the repo. |
| `mihpaiddate` | DATETIME | Meaning not documented in the repo. |
| `mihbookordernum` | STRING | Meaning not documented in the repo. |
| `mihsenddate` | DATETIME | Meaning not documented in the repo. |
| `mihbl` | INT64 | Meaning not documented in the repo. |
| `mihrpv` | INT64 | Meaning not documented in the repo. |
| `mihclearcut` | INT64 | Meaning not documented in the repo. |
| `mihsettlecut` | INT64 | Meaning not documented in the repo. |
| `mihdebbranch` | STRING | Meaning not documented in the repo. |
| `mihdebtaxnos` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/mih_billing.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mih_billing](/initial/raw_mac5_ag01/mih_billing.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `mihtype`, `mihvnos`, `mihcus`.
- Approximate size (BigQuery metadata, 2026-10-31): 3,971 rows, 3.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mih_billing`
LIMIT 100
```
