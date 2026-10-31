---
type: BigQuery Table
title: "tbook_profilecomp"
description: "One row = one cleaned source record of `tbook_profilecomp` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_profilecomp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbook_profilecomp
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_profilecomp.sqlx"
    title: "Dataform definition (validated/mac5/tbook_profilecomp.sqlx)"
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

Validated copy of MAC5 `tbook_profilecomp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: booking profile/company. Table meaning is inferred from column prefixes.
Used by: [dimension_table.dim_project](/dimension/dim_project.md).

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `docno` | INT64 | Meaning not documented in the repo. |
| `projectcode` | INT64 | Meaning not documented in the repo. |
| `projectname` | STRING | Meaning not documented in the repo. |
| `statuscomp` | STRING | Meaning not documented in the repo. |
| `compname` | STRING | Meaning not documented in the repo. |
| `register` | STRING | Meaning not documented in the repo. |
| `addresscomp` | STRING | Meaning not documented in the repo. |
| `province` | STRING | Meaning not documented in the repo. |
| `district` | STRING | Meaning not documented in the repo. |
| `country` | STRING | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `capital` | STRING | Meaning not documented in the repo. |
| `place` | STRING | Meaning not documented in the repo. |
| `tel` | STRING | Meaning not documented in the repo. |
| `mobile` | STRING | Meaning not documented in the repo. |
| `fax` | STRING | Meaning not documented in the repo. |
| `mail` | STRING | Meaning not documented in the repo. |
| `namedirector` | STRING | Meaning not documented in the repo. |
| `nickname` | STRING | Meaning not documented in the repo. |
| `teldirector` | STRING | Meaning not documented in the repo. |
| `profilecomp` | STRING | Meaning not documented in the repo. |
| `typecomp` | STRING | Meaning not documented in the repo. |
| `startdate` | STRING | Meaning not documented in the repo. |
| `history` | STRING | Meaning not documented in the repo. |
| `pjstart` | STRING | Meaning not documented in the repo. |
| `pjend` | STRING | Meaning not documented in the repo. |
| `pjval` | STRING | Meaning not documented in the repo. |
| `pjfor` | STRING | Meaning not documented in the repo. |
| `compgroup` | STRING | Meaning not documented in the repo. |
| `acccode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `accname` | STRING | Likely name (inferred from the column name only; not documented in the repo). |
| `closedby` | STRING | Meaning not documented in the repo. |
| `projectfrom` | STRING | Meaning not documented in the repo. |
| `ptype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `ppc` | STRING | Meaning not documented in the repo. |
| `pecom` | STRING | Meaning not documented in the repo. |
| `uinsert` | STRING | Meaning not documented in the repo. |
| `dinsert` | DATETIME | Meaning not documented in the repo. |
| `insertby` | STRING | Meaning not documented in the repo. |
| `uupdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `dupdate` | DATETIME | Likely date (inferred from the column name only; not documented in the repo). |
| `meccode` | STRING | Likely code (inferred from the column name only; not documented in the repo). |
| `contactdebcode` | STRING | Meaning not documented in the repo. |
| `refallkon` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tbook_profilecomp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_profilecomp](/initial/raw_mac5_ag01/tbook_profilecomp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `docno`.
- Approximate size (BigQuery metadata, 2026-10-31): 8,775 rows, 4.0 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_profilecomp`
LIMIT 100
```
