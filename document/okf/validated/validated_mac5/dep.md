---
type: BigQuery Table
title: "dep"
description: "One row = one department (per company), unique on (company_id, depcode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=dep&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: dep
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/dep.sqlx"
    title: "Dataform definition (validated/mac5/dep.sqlx)"
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

Validated copy of MAC5 `dep` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Department master of the MAC5 ERP: code, group and Thai/English name.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `depcode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `depcode` | STRING | Department code. |
| `depgroup` | STRING | Department group code (e.g. `H`, `HY`, `F`, `CB`). |
| `depdesct` | STRING | Thai name of the department. |
| `depdesce` | STRING | English name of the department. |
| `dephide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `deplock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `depeditdt` | DATETIME | Date and time the record was last edited. |
| `depeditmf` | STRING | User code of the person who last edited the record. |

# How it is built

- Definition: `definitions/validated/mac5/dep.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.dep](/initial/raw_mac5_ag01/dep.md), [raw_mac5_aa05.dep](/initial/raw_mac5_aa05/dep.md), [raw_mac5_ab01.dep](/initial/raw_mac5_ab01/dep.md), [raw_mac5_ac02.dep](/initial/raw_mac5_ac02/dep.md), [raw_mac5_ak02.dep](/initial/raw_mac5_ak02/dep.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY depeditdt desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `depcode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.dep`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, depcode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.dep`
GROUP BY company_id, depcode
HAVING n > 1
```
