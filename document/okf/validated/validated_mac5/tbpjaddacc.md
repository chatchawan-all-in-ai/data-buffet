---
type: BigQuery Table
title: "tbpjaddacc"
description: "One row = one contact person attached to a project (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbpjaddacc&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbpjaddacc
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbpjaddacc.sqlx"
    title: "Dataform definition (validated/mac5/tbpjaddacc.sqlx)"
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

Validated copy of MAC5 `tbpjaddacc`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Contact persons attached to sales projects, with their role, decision power and personal profile fields.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Running ID of the project contact row. |
| `pjid` | STRING | Project ID the contact is attached to. |
| `accid` | STRING | Account (organisation) code of the contact. |
| `accname` | STRING | Account (organisation) name of the contact. |
| `acctype` | STRING | Position or role of the contact (Thai, e.g. managing director, purchasing officer, contractor). |
| `acctype2` | STRING | Secondary position or role of the contact. |
| `accpow` | STRING | Decision-power flag (1 = the contact has decision power, 0 = not). |
| `conid` | STRING | Contact ID (e.g. `ICM`-prefixed code). |
| `conname` | STRING | Contact person name. |
| `contel` | STRING | Phone number of the contact. |
| `condetail` | STRING | Free-text detail about the contact. |
| `uinsert` | STRING | User code of the person who created the record. |
| `insertdate` | DATE | Date the record was created. |
| `textnote` | STRING | Free-text note on the contact. |
| `nickname` | STRING | Nickname of the contact. |
| `religion` | STRING | Religion of the contact. |
| `birthdate` | DATE | Birth date of the contact. |
| `lineidper` | STRING | Personal LINE ID of the contact. |
| `emailper` | STRING | Personal email address of the contact. |
| `idcardper` | STRING | National ID card number of the contact. |
| `addressper` | STRING | Personal address of the contact. |
| `country` | STRING | Country of the contact's address. |
| `province` | STRING | Province of the contact's address. |
| `district` | STRING | District of the contact's address. |
| `sub_district` | STRING | Sub-district of the contact's address. |
| `zipcode` | STRING | Postal code of the contact's address. |
| `spousefullname` | STRING | Full name of the contact's spouse. |
| `birthdatespouse` | DATE | Birth date of the contact's spouse. |
| `numberofchildren` | STRING | Number of children of the contact. |
| `favoriteactivity` | STRING | Activities the contact likes. |
| `unfavoriteactivity` | STRING | Activities the contact dislikes. |
| `trait` | STRING | Personality traits of the contact. |

# How it is built

- Definition: `definitions/validated/mac5/tbpjaddacc.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbpjaddacc](/initial/raw_mac5_ag01/tbpjaddacc.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY insertdate desc, accname desc, conname desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbpjaddacc`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbpjaddacc`
GROUP BY company_id, id
HAVING n > 1
```
