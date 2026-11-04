---
type: BigQuery Table
title: "chq"
description: "One row = one cheque (per company), unique on (company_id, chqno, chqbank, chqdatec, chqtag)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=chq&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: chq
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/chq.sqlx"
    title: "Dataform definition (validated/mac5/chq.sqlx)"
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

Validated copy of MAC5 `chq` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Cheques received from customers and issued to suppliers, with bank, dates, amount, status and memo-derived payment splits.
Used by: [fact_table.fact_chq](/fact/fact_chq.md), [fact_view.view_aging_ri](/view/fact_view/view_aging_ri.md), [dimension_table.dim_aging](/dimension/dim_aging.md), [dimension_table.dim_aging_history](/dimension/dim_aging_history.md), [dimension_table.dim_customer_grade](/dimension/dim_customer_grade.md), [dimension_table.dim_group_customer_grade](/dimension/dim_group_customer_grade.md).

# Grain and key

One row per `company_id`, `chqno`, `chqbank`, `chqdatec`, `chqtag`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `chqno` | STRING | Cheque number. |
| `chqbank` | STRING | Bank code of the cheque (e.g. `BBL`, `KBANK`, `SCB`). |
| `chqacode` | STRING | General-ledger account code of the cheque; sampled MAC5 records show 112001 for received cheques and 211101, 212000, 212400, and 214201 for issued cheques. |
| `chqcus` | STRING | Customer code (supplier code for issued cheques), matching `deb.debcode`. |
| `chqdatec` | DATETIME | Date written on the cheque. |
| `chqdater` | DATETIME | Date the cheque was received or issued. |
| `chqdatep` | DATETIME | Date the cheque was passed (cleared) at the bank. |
| `chqtype` | INT64 | Cheque direction (1 = received from customer, 2 = issued to supplier). |
| `chqstatus` | INT64 | Cheque status (1 = cleared, 2 = bounced, 3 = due). |
| `chqtotal` | FLOAT64 | Cheque amount. |
| `chqgl` | INT64 | Flag: cheque posted to the general ledger (1 = posted). |
| `chqmi` | INT64 | Cheque handling mode code (0, 1, 2). |
| `chqown` | INT64 | Cheque ownership code (1 = own cheque, 2 = third-party cheque). |
| `chqtag` | INT64 | Tag marker of the cheque. |
| `chqstatusn` | INT64 | Cheque posting status (1 = POST, 2 = PASS, 3 = cleared, 4 = not cleared, 5 = adjusted, 6 = voucher cancelled). |
| `chqlock` | INT64 | Flag: cheque locked against editing. |
| `chqpassgl` | INT64 | Flag: cheque clearing posted to the general ledger (-1 = posted). |
| `chqjob` | STRING | Job code of the cheque (sales job or project category). |
| `chqdep` | STRING | Department code of the cheque, used as the sales channel code. |
| `chqper` | STRING | Salesperson (employee) code of the cheque. |
| `chqzon` | STRING | Zone code of the cheque. |
| `chqrcode` | STRING | General-ledger account code of the bank account the cheque is deposited to or paid from. |
| `chqeditlk` | DATETIME | Timestamp of the current edit lock on the cheque. |
| `chqkeyuser` | STRING | User code of the person who keyed the cheque. |
| `chqkeydate` | DATETIME | Date and time the cheque was keyed. |
| `chqdeduct` | FLOAT64 | Amount deducted from the cheque, such as bank fees. |
| `chqecode` | STRING | External code of the cheque. |
| `chqbranch` | STRING | Bank branch of the cheque. |
| `chqmec` | STRING | Memo-card code of the cheque, matching `mec.meccode`. |
| `chqdatev` | DATETIME | Voucher date of the cheque. |
| `chqmemo_raw` | STRING | Full cheque memo as entered, including transfer and payment-split notes. |
| `chqmemo` | STRING | Cheque memo prefix before the transfer or payment-split notes. |
| `extract_text` | STRING | Free text left from the memo's payment-split notes after dates and amounts are removed. |
| `extract_value` | ARRAY<STRUCT<extract_date DATE, extract_amount FLOAT64>> | Payment splits parsed from the memo, as an array of (`extract_date`, `extract_amount`). |

# How it is built

- Definition: `definitions/validated/mac5/chq.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.chq](/initial/raw_mac5_ag01/chq.md), [raw_mac5_aa05.chq](/initial/raw_mac5_aa05/chq.md), [raw_mac5_ab01.chq](/initial/raw_mac5_ab01/chq.md), [raw_mac5_ac02.chq](/initial/raw_mac5_ac02/chq.md), [raw_mac5_ak02.chq](/initial/raw_mac5_ak02/chq.md), `function_dataset.EXTRACT_CHQ_DATA` (UDF).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY chqkeydate desc) = 1`.
- Storage: partition by `(none)`, cluster by `company_id`, `chqno`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.chq`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, chqno, chqbank, chqdatec, chqtag, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.chq`
GROUP BY company_id, chqno, chqbank, chqdatec, chqtag
HAVING n > 1
```
