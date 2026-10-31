---
type: BigQuery Table
title: "tbook_quotation"
description: "One row = one booking quotation, unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_quotation&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_quotation.sqlx"
    title: "Dataform definition (validated/mac5/tbook_quotation.sqlx)"
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

Validated copy of MAC5 `tbook_quotation`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: booking quotation. Table meaning is inferred from column prefixes.
Used by: [curated_mac5.curated_tbook_quotation](/curated/curated_mac5/curated_tbook_quotation.md), [dimension_table.dim_customer_report_info](/dimension/dim_customer_report_info.md).

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Surrogate identifier from the source system (the primary key). |
| `running` | STRING | Meaning not documented in the repo. |
| `atten` | STRING | Meaning not documented in the repo. |
| `address` | STRING | Meaning not documented in the repo. |
| `sdate` | DATE | Likely date (inferred from the column name only; not documented in the repo). |
| `project` | STRING | Meaning not documented in the repo. |
| `tel` | BOOL | Meaning not documented in the repo. |
| `sale` | BOOL | Meaning not documented in the repo. |
| `price_validity` | STRING | Meaning not documented in the repo. |
| `termdelivery` | STRING | Meaning not documented in the repo. |
| `termpayment` | STRING | Meaning not documented in the repo. |
| `uinsert` | STRING | Meaning not documented in the repo. |
| `dinsert` | STRING | Meaning not documented in the repo. |
| `uupdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `dupdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `agent1` | STRING | Meaning not documented in the repo. |
| `agent2` | STRING | Meaning not documented in the repo. |
| `period` | STRING | Meaning not documented in the repo. |
| `pos` | STRING | Meaning not documented in the repo. |
| `vat` | INT64 | Meaning not documented in the repo. |
| `disc` | INT64 | Meaning not documented in the repo. |
| `extrasum` | INT64 | Meaning not documented in the repo. |
| `extradesc` | STRING | Meaning not documented in the repo. |
| `date1st` | STRING | Meaning not documented in the repo. |
| `date1end` | STRING | Meaning not documented in the repo. |
| `date2st` | STRING | Meaning not documented in the repo. |
| `date2end` | STRING | Meaning not documented in the repo. |
| `cashstatus` | INT64 | Meaning not documented in the repo. |
| `note` | STRING | Meaning not documented in the repo. |
| `noteforapp` | STRING | Meaning not documented in the repo. |
| `memoforapp` | STRING | Meaning not documented in the repo. |
| `rev` | INT64 | Meaning not documented in the repo. |
| `typecus` | INT64 | Meaning not documented in the repo. |
| `channel` | STRING | Meaning not documented in the repo. |
| `channel2` | STRING | Meaning not documented in the repo. |
| `typeprice` | INT64 | Meaning not documented in the repo. |
| `fob` | INT64 | Meaning not documented in the repo. |
| `cancel` | INT64 | Likely cancel flag (inferred from the column name only; not documented in the repo). |
| `apptype` | INT64 | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `typedeb` | STRING | Meaning not documented in the repo. |
| `saledep` | STRING | Meaning not documented in the repo. |
| `typeproject` | STRING | Meaning not documented in the repo. |
| `selectstatus` | INT64 | Meaning not documented in the repo. |
| `conpostatus` | INT64 | Meaning not documented in the repo. |
| `lat` | STRING | Meaning not documented in the repo. |
| `long` | STRING | Meaning not documented in the repo. |
| `mapnote` | STRING | Meaning not documented in the repo. |
| `fileupload` | STRING | Meaning not documented in the repo. |
| `city` | STRING | Meaning not documented in the repo. |
| `rdosend` | INT64 | Meaning not documented in the repo. |
| `cname` | BOOL | Likely name (inferred from the column name only; not documented in the repo). |
| `ctel` | BOOL | Meaning not documented in the repo. |
| `caddress` | STRING | Meaning not documented in the repo. |
| `checknote` | STRING | Meaning not documented in the repo. |
| `textnote` | STRING | Meaning not documented in the repo. |
| `statusspread` | INT64 | Meaning not documented in the repo. |
| `chkbox` | INT64 | Meaning not documented in the repo. |
| `fobstt` | INT64 | Meaning not documented in the repo. |
| `quotation_ref` | INT64 | Meaning not documented in the repo. |
| `customer_id` | INT64 | Meaning not documented in the repo. |
| `customer_group` | INT64 | Meaning not documented in the repo. |
| `quotation_id` | INT64 | Meaning not documented in the repo. |
| `estatus` | INT64 | Likely status code (inferred from the column name only; not documented in the repo). |
| `area` | STRING | Meaning not documented in the repo. |
| `district` | STRING | Meaning not documented in the repo. |
| `postcode` | STRING | Meaning not documented in the repo. |
| `qtstepprice` | INT64 | Meaning not documented in the repo. |
| `extradis` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tbook_quotation.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_quotation](/initial/raw_mac5_ag01/tbook_quotation.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY extradesc desc, cname desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 272,467 rows, 222.1 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_quotation`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbook_quotation`
GROUP BY company_id, id
HAVING n > 1
```
