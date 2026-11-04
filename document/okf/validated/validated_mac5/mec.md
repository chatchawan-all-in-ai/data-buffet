---
type: BigQuery Table
title: "mec"
description: "One row = one memo card (per company), unique on (company_id, meccode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mec&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mec
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mec.sqlx"
    title: "Dataform definition (validated/mac5/mec.sqlx)"
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

Validated copy of MAC5 `mec`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Memo cards attached to documents (address, contact and shop or branch name per template), referenced by `mihmec`/`milmec`.
Used by: [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md).

# Grain and key

One row per `company_id`, `meccode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `meccode` | STRING | Memo-card code, referenced by `mihmec` and `milmec` on documents. |
| `mectpl` | INT64 | Template number that defines the layout of the card's text fields. |
| `mectoctype` | INT64 | Owner type of the card (2 = card attached to a customer through `mectocode`, 11 = general card, 8 = other). |
| `mectocode` | STRING | Code of the record the card belongs to, such as the customer code when `mectoctype` is 2. |
| `mect1` | STRING | Text field 1 of the card (an address part, contact name or postal code, depending on the template). |
| `mect2` | STRING | Text field 2 of the card (an address part, contact name or postal code, depending on the template). |
| `mect3` | STRING | Text field 3 of the card (an address part, contact name or postal code, depending on the template). |
| `mect4` | STRING | Text field 4 of the card (an address part, contact name or postal code, depending on the template). |
| `mect5` | STRING | Text field 5 of the card (an address part, contact name or postal code, depending on the template). |
| `mecd1` | DATETIME | Date field 1 of the card. |
| `mecd2` | DATETIME | Date field 2 of the card. |
| `mecd3` | DATETIME | Date field 3 of the card. |
| `meci1` | INT64 | Integer field 1 of the card. |
| `meci2` | INT64 | Integer field 2 of the card. |
| `mecc1` | FLOAT64 | Numeric field 1 of the card. |
| `mecc2` | FLOAT64 | Numeric field 2 of the card. |
| `mecc3` | FLOAT64 | Numeric field 3 of the card. |
| `mecc4` | FLOAT64 | Numeric field 4 of the card. |
| `mecc5` | FLOAT64 | Numeric field 5 of the card. |
| `mecm1` | STRING | Memo field 1 of the card. |
| `mecm2` | STRING | Memo field 2 of the card. |
| `mecm3` | STRING | Memo field 3 of the card. |
| `mecm4` | STRING | Memo field 4 of the card. |
| `mecm5` | STRING | Memo field 5 of the card. |
| `mecm6` | STRING | Memo field 6 of the card. |
| `mecm7` | STRING | Memo field 7 of the card. |
| `mecm8` | STRING | Memo field 8 of the card. |
| `mecm9` | STRING | Memo field 9 of the card. |
| `mecdesc` | STRING | Card title, used as the shop or branch name of chain-store customers in invoice reporting. |
| `mechide` | INT64 | Flag: card hidden from selection lists. |
| `meclock` | INT64 | Flag: card locked against editing. |
| `meceditlk` | DATETIME | Timestamp of the current edit lock on the card. |
| `mecrefwe` | STRING | Web reference of the card. |
| `mecsortn` | STRING | Sort name of the card. |
| `mect6` | STRING | Text field 6 of the card (an address part, contact name or postal code, depending on the template). |
| `mect7` | STRING | Text field 7 of the card (an address part, contact name or postal code, depending on the template). |
| `mect8` | STRING | Text field 8 of the card (an address part, contact name or postal code, depending on the template). |
| `mect9` | STRING | Text field 9 of the card (an address part, contact name or postal code, depending on the template). |
| `mect10` | STRING | Text field 10 of the card (an address part, contact name or postal code, depending on the template). |
| `meceditdt` | DATETIME | Date and time the card was last edited. |
| `meceditmf` | STRING | User code of the person who last edited the card. |

# How it is built

- Definition: `definitions/validated/mac5/mec.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.mec](/initial/raw_mac5_ag01/mec.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY meceditdt desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `meccode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mec`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, meccode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.mec`
GROUP BY company_id, meccode
HAVING n > 1
```
