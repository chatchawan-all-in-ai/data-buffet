---
type: BigQuery Table
title: "tdis_mail"
description: "One row = one cleaned source record of `tdis_mail` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tdis_mail&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tdis_mail.sqlx"
    title: "Dataform definition (validated/mac5/tdis_mail.sqlx)"
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

Validated copy of MAC5 `tdis_mail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: distribution mail log. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `saleid` | STRING | Meaning not documented in the repo. |
| `spass` | STRING | Meaning not documented in the repo. |
| `salename` | STRING | Meaning not documented in the repo. |
| `salemail` | STRING | Meaning not documented in the repo. |
| `mail1` | STRING | Meaning not documented in the repo. |
| `mail2` | STRING | Meaning not documented in the repo. |
| `mail3` | STRING | Meaning not documented in the repo. |
| `mail4` | STRING | Meaning not documented in the repo. |
| `lv` | STRING | Meaning not documented in the repo. |
| `cc1` | STRING | Meaning not documented in the repo. |
| `cc2` | STRING | Meaning not documented in the repo. |
| `cc3` | STRING | Meaning not documented in the repo. |
| `cc4` | STRING | Meaning not documented in the repo. |
| `cc5` | STRING | Meaning not documented in the repo. |
| `cc6` | STRING | Meaning not documented in the repo. |
| `cc7` | STRING | Meaning not documented in the repo. |
| `cc8` | STRING | Meaning not documented in the repo. |
| `cc9` | STRING | Meaning not documented in the repo. |
| `passlv1` | STRING | Meaning not documented in the repo. |
| `passlv2` | STRING | Meaning not documented in the repo. |
| `passlv3` | STRING | Meaning not documented in the repo. |
| `passlv4` | STRING | Meaning not documented in the repo. |
| `f1` | STRING | Meaning not documented in the repo. |
| `f2` | STRING | Meaning not documented in the repo. |
| `f3` | STRING | Meaning not documented in the repo. |
| `f4` | STRING | Meaning not documented in the repo. |
| `f5` | STRING | Meaning not documented in the repo. |
| `f6` | STRING | Meaning not documented in the repo. |
| `f7` | STRING | Meaning not documented in the repo. |
| `f8` | STRING | Meaning not documented in the repo. |
| `f9` | STRING | Meaning not documented in the repo. |
| `f10` | STRING | Meaning not documented in the repo. |
| `pum1` | STRING | Meaning not documented in the repo. |
| `pum2` | STRING | Meaning not documented in the repo. |
| `pum3` | STRING | Meaning not documented in the repo. |
| `ppass1` | STRING | Meaning not documented in the repo. |
| `ppass2` | STRING | Meaning not documented in the repo. |
| `ppass3` | STRING | Meaning not documented in the repo. |
| `ma` | STRING | Meaning not documented in the repo. |
| `ta` | STRING | Meaning not documented in the repo. |
| `ceo` | STRING | Meaning not documented in the repo. |
| `app` | STRING | Meaning not documented in the repo. |
| `lv_pum` | STRING | Meaning not documented in the repo. |
| `lv_rp` | STRING | Meaning not documented in the repo. |
| `rp1` | STRING | Meaning not documented in the repo. |
| `rp2` | STRING | Meaning not documented in the repo. |
| `rp3` | STRING | Meaning not documented in the repo. |
| `rpass1` | STRING | Meaning not documented in the repo. |
| `rpass2` | STRING | Meaning not documented in the repo. |
| `rpass3` | STRING | Meaning not documented in the repo. |
| `lv_ele` | STRING | Meaning not documented in the repo. |
| `ele1` | STRING | Meaning not documented in the repo. |
| `ele2` | STRING | Meaning not documented in the repo. |
| `ele3` | STRING | Meaning not documented in the repo. |
| `epass1` | STRING | Meaning not documented in the repo. |
| `epass2` | STRING | Meaning not documented in the repo. |
| `epass3` | STRING | Meaning not documented in the repo. |
| `type` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `menu1` | STRING | Meaning not documented in the repo. |
| `download` | STRING | Meaning not documented in the repo. |
| `pic` | STRING | Meaning not documented in the repo. |
| `lv_boq_lyn` | STRING | Meaning not documented in the repo. |
| `active` | INT64 | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tdis_mail.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tdis_mail](/initial/raw_mac5_ag01/tdis_mail.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `saleid`.
- Approximate size (BigQuery metadata, 2026-10-31): 731 rows, 447.9 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tdis_mail`
LIMIT 100
```
