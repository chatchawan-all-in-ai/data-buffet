---
type: BigQuery Table
title: "cpx"
description: "One row = one outstanding internal request line (per company), unique on (company_id, cpxstkid, cpxlinkid, cpxvnosid, cpxdateid)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=cpx&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: cpx
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/cpx.sqlx"
    title: "Dataform definition (validated/mac5/cpx.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `cpx`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Outstanding internal request (`PX`) lines: requested versus issued quantity, with clearing flags.
No other repo object reads it.

# Grain and key

One row per `company_id`, `cpxstkid`, `cpxlinkid`, `cpxvnosid`, `cpxdateid`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `cpxstkid` | STRING | Product (stock) code of the outstanding request line, matching `stk.stkcode`. |
| `cpxlinkid` | INT64 | Internal ID linking the outstanding record to its document line. |
| `cpxvnosid` | STRING | Number of the internal request (`PX`) document that has the outstanding line. |
| `cpxdateid` | DATETIME | Date of the internal request document. |
| `cpxjob` | STRING | Job code of the document (sales job or project category). |
| `cpxdep` | STRING | Department code of the document, used as the sales channel code. |
| `cpxper` | STRING | Requesting employee code of the document. |
| `cpxdoc` | STRING | Document reference code. |
| `cpxmec` | STRING | Memo-card code of the document, matching `mec.meccode`. |
| `cpxsto` | STRING | Warehouse (store) code the request is issued from. |
| `cpxstkreq` | FLOAT64 | Quantity requested on the line. |
| `cpxstkcut` | FLOAT64 | Quantity already issued against the request line. |
| `cpxclearstk` | INT64 | Flag: outstanding quantity cleared (-1 = cleared). |
| `cpxclearuser` | INT64 | Flag: line cleared manually by a user (-1 = yes). |
| `cpxclearall` | INT64 | Flag: line fully cleared (-1 = cleared). |
| `cpxstatus` | INT64 | Status code of the outstanding line. |

# How it is built

- Definition: `definitions/validated/mac5/cpx.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.cpx](/initial/raw_mac5_ag01/cpx.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY cpxdateid desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `cpxstkid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.cpx`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, cpxstkid, cpxlinkid, cpxvnosid, cpxdateid, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.cpx`
GROUP BY company_id, cpxstkid, cpxlinkid, cpxvnosid, cpxdateid
HAVING n > 1
```
