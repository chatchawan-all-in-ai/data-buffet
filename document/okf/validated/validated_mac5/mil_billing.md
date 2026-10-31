---
type: BigQuery Table
title: "mil_billing"
description: "One row = one cleaned source record of `mil_billing` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mil_billing&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mil_billing.sqlx"
    title: "Dataform definition (validated/mac5/mil_billing.sqlx)"
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

Validated copy of MAC5 `mil_billing`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: billing document line snapshot. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

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
| `milquanp2` | FLOAT64 | Meaning not documented in the repo. |
| `miladisc` | FLOAT64 | Meaning not documented in the repo. |
| `milcog` | FLOAT64 | Meaning not documented in the repo. |
| `milconv` | FLOAT64 | Meaning not documented in the repo. |
| `mildisca` | FLOAT64 | Meaning not documented in the repo. |
| `mildisct` | STRING | Meaning not documented in the repo. |
| `milvat` | FLOAT64 | Meaning not documented in the repo. |
| `milsum` | FLOAT64 | Meaning not documented in the repo. |
| `milcut` | INT64 | Meaning not documented in the repo. |
| `milstype` | INT64 | Meaning not documented in the repo. |
| `miluname` | STRING | Meaning not documented in the repo. |
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
| `milexpdate` | DATETIME | Meaning not documented in the repo. |
| `milnotes` | STRING | Meaning not documented in the repo. |
| `milnotkl` | INT64 | Meaning not documented in the repo. |
| `mildelvdt` | DATETIME | Meaning not documented in the repo. |
| `mildatesp` | DATETIME | Meaning not documented in the repo. |
| `milnumcsp` | FLOAT64 | Meaning not documented in the repo. |
| `milnumisp` | INT64 | Meaning not documented in the repo. |
| `milcost` | FLOAT64 | Meaning not documented in the repo. |
| `milucost` | FLOAT64 | Meaning not documented in the repo. |
| `miluprice` | FLOAT64 | Meaning not documented in the repo. |
| `milusequanp` | INT64 | Meaning not documented in the repo. |
| `milvcol5` | STRING | Meaning not documented in the repo. |
| `milfitem` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/mil_billing.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mil_billing](/initial/raw_mac5_ag01/mil_billing.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `miltype`, `milvnos`, `milcus`.
- Approximate size (BigQuery metadata, 2026-10-31): 13,850 rows, 4.6 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mil_billing`
LIMIT 100
```
