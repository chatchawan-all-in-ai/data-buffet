---
type: BigQuery Table
title: "match_deb_bot_re"
description: "One row = one developer company to MAC5 customer mapping (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=match_deb_bot_re&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: match_deb_bot_re
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/match_deb_bot_re.sqlx"
    title: "Dataform definition (validated/mac5/match_deb_bot_re.sqlx)"
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

Validated copy of MAC5 `match_deb_bot_re`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Mapping of developer company names on purchase orders to MAC5 customer (debtor) codes, used by the real-estate PO bot.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Row identifier of the mapping. |
| `deb_code` | STRING | MAC5 customer (debtor) code of the developer company. |
| `vendor_name` | STRING | Developer company name as printed on its purchase orders, used to match the MAC5 customer. |
| `channel` | STRING | Developer group of the purchase order (e.g. `AP`, `SC`, `QH`, `Sansiri`, `Frasers`). |

# How it is built

- Definition: `definitions/validated/mac5/match_deb_bot_re.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.match_deb_bot_re](/initial/raw_mac5_ag01/match_deb_bot_re.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY vendor_name desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 47 rows, 5.3 KB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.match_deb_bot_re`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.match_deb_bot_re`
GROUP BY company_id, id
HAVING n > 1
```
