---
type: BigQuery Table
title: "tbcontact"
description: "One row = one booking contact, unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbcontact&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbcontact.sqlx"
    title: "Dataform definition (validated/mac5/tbcontact.sqlx)"
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

Validated copy of MAC5 `tbcontact`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: booking contact. Table meaning is inferred from column prefixes.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | STRING | Surrogate identifier from the source system (the primary key). |
| `contactpersonal` | STRING | Meaning not documented in the repo. |
| `contactcompany` | STRING | Meaning not documented in the repo. |
| `contactcop` | STRING | Meaning not documented in the repo. |
| `contactsegment` | STRING | Meaning not documented in the repo. |
| `contactchannel` | STRING | Meaning not documented in the repo. |
| `contactstatus` | STRING | Meaning not documented in the repo. |
| `contacttitle` | STRING | Meaning not documented in the repo. |
| `contactname` | STRING | Meaning not documented in the repo. |
| `contactnick` | STRING | Meaning not documented in the repo. |
| `contactaddress` | STRING | Meaning not documented in the repo. |
| `contactaddress1` | STRING | Meaning not documented in the repo. |
| `contactaddress2` | STRING | Meaning not documented in the repo. |
| `contactaddress3` | STRING | Meaning not documented in the repo. |
| `contactaddress4` | STRING | Meaning not documented in the repo. |
| `contactaddress5` | STRING | Meaning not documented in the repo. |
| `contactaddress6` | STRING | Meaning not documented in the repo. |
| `contacttel` | STRING | Meaning not documented in the repo. |
| `contactmail` | STRING | Meaning not documented in the repo. |
| `contacttype` | STRING | Meaning not documented in the repo. |
| `contactbday` | DATE | Meaning not documented in the repo. |
| `contactage` | STRING | Meaning not documented in the repo. |
| `contactbyear` | STRING | Meaning not documented in the repo. |
| `contacthob` | STRING | Meaning not documented in the repo. |
| `contactstudy` | STRING | Meaning not documented in the repo. |
| `contactmag` | STRING | Meaning not documented in the repo. |
| `contactme` | STRING | Meaning not documented in the repo. |
| `contactcolor` | STRING | Meaning not documented in the repo. |
| `contactfood` | STRING | Meaning not documented in the repo. |
| `contactlife` | STRING | Meaning not documented in the repo. |
| `contactact` | STRING | Meaning not documented in the repo. |
| `contactsday` | STRING | Meaning not documented in the repo. |
| `contactdesc` | STRING | Meaning not documented in the repo. |
| `contactlove` | STRING | Meaning not documented in the repo. |
| `contactson` | STRING | Meaning not documented in the repo. |
| `contactcntson` | STRING | Meaning not documented in the repo. |
| `contactcntgirl` | STRING | Meaning not documented in the repo. |
| `contactsonname1` | STRING | Meaning not documented in the repo. |
| `contactsonage1` | STRING | Meaning not documented in the repo. |
| `contactsonstudy1` | STRING | Meaning not documented in the repo. |
| `contactsonname2` | STRING | Meaning not documented in the repo. |
| `contactsonage2` | STRING | Meaning not documented in the repo. |
| `contactsonstudy2` | STRING | Meaning not documented in the repo. |
| `contactsonname3` | STRING | Meaning not documented in the repo. |
| `contactsonage3` | STRING | Meaning not documented in the repo. |
| `contactsonstudy3` | STRING | Meaning not documented in the repo. |
| `contactposition` | STRING | Meaning not documented in the repo. |
| `contactpower` | STRING | Meaning not documented in the repo. |
| `projectcode` | STRING | Meaning not documented in the repo. |
| `contactpp1` | STRING | Meaning not documented in the repo. |
| `contactpp2` | STRING | Meaning not documented in the repo. |
| `contactpp3` | STRING | Meaning not documented in the repo. |
| `contactpp4` | STRING | Meaning not documented in the repo. |
| `contactpp5` | STRING | Meaning not documented in the repo. |
| `contactpp6` | STRING | Meaning not documented in the repo. |
| `insertby` | STRING | Meaning not documented in the repo. |
| `insertwhen` | STRING | Meaning not documented in the repo. |
| `lastupdate` | STRING | Meaning not documented in the repo. |
| `contactpath20` | STRING | Meaning not documented in the repo. |
| `contactdebcode` | STRING | Meaning not documented in the repo. |
| `activestatus` | INT64 | Meaning not documented in the repo. |
| `lineidcorp` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tbcontact.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbcontact](/initial/raw_mac5_ag01/tbcontact.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY contactname desc, contactdesc desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.
- Approximate size (BigQuery metadata, 2026-10-31): 15,363 rows, 3.7 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbcontact`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbcontact`
GROUP BY company_id, id
HAVING n > 1
```
