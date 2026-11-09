---
type: BigQuery Table
title: "grp"
description: "One row = one user permission group from source table `grp`."
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
generated: { by: "agent:codex", at: "2026-11-09T02:15:58+00:00" }
status: draft
---

# What it is

Validated copy of MAC5 `grp`: every column is trimmed/cast with the shared helpers. There is no business logic at this layer. Table meaning: User permission groups of the MAC5 web applications, with the role name, granted menu IDs and product lines.
No other repo object reads it.

# Grain and key

One row per `company_id`, `grpid`. `uniqueKey` and `pk_key` declare this key; `QUALIFY ROW_NUMBER()` keeps the first row ordered by `grpname desc`. Each full rebuild attaches a `NOT ENFORCED` primary key using the standard retry loop.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `grpid` | INT64 | Permission group ID. |
| `grpstatus` | STRING | Comma-separated list of menu or permission IDs granted to the group. |
| `grpname` | STRING | Permission group name in Thai, describing the role (e.g. sales admin, installation manager). |
| `grpline` | STRING | Product lines the group covers, as a quoted list (e.g. `'LYN','TEC'`). |

# How it is built

- Definition: `definitions/validated/mac5/grp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.grp](/initial/raw_mac5_ag01/grp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `grpstatus`, `grpid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.grp`
LIMIT 100
```
