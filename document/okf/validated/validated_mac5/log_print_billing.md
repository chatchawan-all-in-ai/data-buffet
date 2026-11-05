---
type: BigQuery Table
title: "log_print_billing"
description: "One row = one printed bill-payment slip (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=log_print_billing&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: log_print_billing
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/log_print_billing.sqlx"
    title: "Dataform definition (validated/mac5/log_print_billing.sqlx)"
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

Validated copy of MAC5 `log_print_billing`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Log of printed billing (bill-payment) slips, with references, billing document number and amount.
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | INT64 | Row identifier of the print log entry. |
| `ref1` | STRING | Bill-payment reference 1, holding the MAC5 customer (debtor) code. |
| `ref2` | STRING | Bill-payment reference 2, a 13-digit code built from the billing document number. |
| `order_no` | STRING | Billing document number (e.g. `BAB6610247`). |
| `amount` | FLOAT64 | Billed amount in THB. |
| `status` | INT64 | Status flag of the print log entry (0 or 1). |
| `dinsert` | DATE | Date the billing slip was printed. |

# How it is built

- Definition: `definitions/validated/mac5/log_print_billing.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.log_print_billing](/initial/raw_mac5_ag01/log_print_billing.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY dinsert desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.log_print_billing`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.log_print_billing`
GROUP BY company_id, id
HAVING n > 1
```
