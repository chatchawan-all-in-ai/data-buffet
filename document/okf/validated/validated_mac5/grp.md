---
type: BigQuery Table
title: "grp"
description: "One row = one user permission group from source table `grp` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=grp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: grp
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/grp.sqlx"
    title: "Dataform definition (validated/mac5/grp.sqlx)"
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

Validated copy of MAC5 `grp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: User permission groups of the MAC5 web applications, with the role name, granted menu IDs and product lines.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `grpid` | INT64 | Permission group ID. |
| `grpstatus` | STRING | Comma-separated list of menu or permission IDs granted to the group. |
| `grpname` | STRING | Permission group name in Thai, describing the role (e.g. sales admin, installation manager). |
| `grpline` | STRING | Product lines the group covers, as a quoted list (e.g. `'LYN','TEC'`). |

# How it is built

- Definition: `definitions/validated/mac5/grp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.grp](/initial/raw_mac5_ag01/grp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `grpstatus`, `grpid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.grp`
LIMIT 100
```
