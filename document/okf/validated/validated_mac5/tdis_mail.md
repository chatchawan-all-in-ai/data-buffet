---
type: BigQuery Table
title: "tdis_mail"
description: "One row = one sales user of the approval system from source table `tdis_mail` (no declared key; not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tdis_mail&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tdis_mail
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

Validated copy of MAC5 `tdis_mail`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`. There is no business logic at this layer. Table meaning: Sales users of the quotation approval system with their approval level, approver email chains per product line and access flags.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `saleid` | STRING | Employee code of the sales user. |
| `spass` | STRING | Login password of the sales user (mostly hashed). |
| `salename` | STRING | Name of the sales user. |
| `salemail` | STRING | Email address of the sales user. |
| `mail1` | STRING | Email address of the level-1 approver of the sales user. |
| `mail2` | STRING | Email address of the level-2 approver of the sales user. |
| `mail3` | STRING | Email address of the level-3 approver of the sales user. |
| `mail4` | STRING | Email address of the level-4 approver of the sales user. |
| `lv` | STRING | Approval level code of the sales user (e.g. `lv0`, `lv2`, `RP`). |
| `cc1` | STRING | CC email address 1 for approval mails. |
| `cc2` | STRING | CC email address 2 for approval mails. |
| `cc3` | STRING | CC email address 3 for approval mails. |
| `cc4` | STRING | CC email address 4 for approval mails. |
| `cc5` | STRING | CC email address 5 for approval mails. |
| `cc6` | STRING | CC email address 6 for approval mails. |
| `cc7` | STRING | CC email address 7 for approval mails. |
| `cc8` | STRING | CC email address 8 for approval mails. |
| `cc9` | STRING | CC email address 9 for approval mails. |
| `passlv1` | STRING | Approval password of the level-1 approver. |
| `passlv2` | STRING | Approval password of the level-2 approver. |
| `passlv3` | STRING | Approval password of the level-3 approver. |
| `passlv4` | STRING | Approval password of the level-4 approver. |
| `f1` | STRING | Additional notification email address 1. |
| `f2` | STRING | Additional notification email address 2. |
| `f3` | STRING | Additional notification email address 3. |
| `f4` | STRING | Additional notification email address 4. |
| `f5` | STRING | Additional notification email address 5. |
| `f6` | STRING | Additional notification email address 6. |
| `f7` | STRING | Additional notification email address 7. |
| `f8` | STRING | Additional notification email address 8. |
| `f9` | STRING | Additional notification email address 9. |
| `f10` | STRING | Additional notification email address 10. |
| `pum1` | STRING | Email address of the level-1 PUMP product-line approver. |
| `pum2` | STRING | Email address of the level-2 PUMP product-line approver. |
| `pum3` | STRING | Email address of the level-3 PUMP product-line approver. |
| `ppass1` | STRING | Approval password of the level-1 PUMP product-line approver. |
| `ppass2` | STRING | Approval password of the level-2 PUMP product-line approver. |
| `ppass3` | STRING | Approval password of the level-3 PUMP product-line approver. |
| `ma` | STRING | Employee code of the manager approver of the sales user. |
| `ta` | STRING | Employee code of the team approver of the sales user. |
| `ceo` | STRING | Employee code of the top-level (CEO) approver. |
| `app` | STRING | Approval option code of the sales user. |
| `lv_pum` | STRING | Employee code of the PUMP product-line approver. |
| `lv_rp` | STRING | Code of the RP product-line approver. |
| `rp1` | STRING | Email address of the level-1 RP product-line approver. |
| `rp2` | STRING | Email address of the level-2 RP product-line approver. |
| `rp3` | STRING | Email address of the level-3 RP product-line approver. |
| `rpass1` | STRING | Approval password of the level-1 RP product-line approver. |
| `rpass2` | STRING | Approval password of the level-2 RP product-line approver. |
| `rpass3` | STRING | Approval password of the level-3 RP product-line approver. |
| `lv_ele` | STRING | Code of the electrical product-line approver. |
| `ele1` | STRING | Email address of the level-1 electrical product-line approver. |
| `ele2` | STRING | Email address of the level-2 electrical product-line approver. |
| `ele3` | STRING | Email address of the level-3 electrical product-line approver. |
| `epass1` | STRING | Approval password of the level-1 electrical product-line approver. |
| `epass2` | STRING | Approval password of the level-2 electrical product-line approver. |
| `epass3` | STRING | Approval password of the level-3 electrical product-line approver. |
| `type` | STRING | User type code (e.g. `PBK`). |
| `menu1` | STRING | Menu access flag. |
| `download` | STRING | Download permission flag (1 = allowed). |
| `pic` | STRING | Picture file name of the sales user. |
| `lv_boq_lyn` | STRING | Approver level for LYNN BOQ quotations. |
| `active` | INT64 | Active flag (1 = active, 0 = inactive). |

# How it is built

- Definition: `definitions/validated/mac5/tdis_mail.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tdis_mail](/initial/raw_mac5_ag01/tdis_mail.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `saleid`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tdis_mail`
LIMIT 100
```
