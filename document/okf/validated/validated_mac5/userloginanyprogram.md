---
type: BigQuery Table
title: "userloginanyprogram"
description: "One row = one login account for one web application (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=userloginanyprogram&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: userloginanyprogram
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/userloginanyprogram.sqlx"
    title: "Dataform definition (validated/mac5/userloginanyprogram.sqlx)"
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

Validated copy of MAC5 `userloginanyprogram`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Login accounts for the MAC5 companion web applications (pay-in, bill payment, billing, promotion master), with user department and permission level.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `id` | INT64 | Running ID of the login account row. |
| `username` | STRING | Login user name (usually the employee code). |
| `password` | STRING | Account password, stored as a bcrypt hash or as plain text. |
| `actionapp` | STRING | Web application the login is for (PayinOnline, Billpayment, BillingOnline, MasterPromotion, ManagementTAOut). |
| `name` | STRING | Full name of the user. |
| `notes` | STRING | Free-text note on the user's section or role (e.g. general accounting, credit). |
| `department` | STRING | Department of the user (e.g. Account, Admin, Marketing, IT). |
| `levelaction` | STRING | Extra permission level in the application (e.g. `printBilling`, `CheckPayment`). |
| `email` | STRING | Email address of the user. |
| `token` | STRING | Access or reset token issued to the account. |
| `tokenexpiry` | DATETIME | Expiry date and time of `token`. |
| `istokenvalid` | INT64 | Flag whether `token` is still valid (1 = valid, 0 = not). |

# How it is built

- Definition: `definitions/validated/mac5/userloginanyprogram.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.userloginanyprogram](/initial/raw_mac5_ag01/userloginanyprogram.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY username desc, name desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.userloginanyprogram`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.userloginanyprogram`
GROUP BY company_id, id
HAVING n > 1
```
