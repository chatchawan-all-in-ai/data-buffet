---
type: BigQuery Table
title: "log_print_billing"
description: "One row = one printed bill-payment slip, a record of source table `log_print_billing` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=log_print_billing&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: log_print_billing
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/log_print_billing/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `log_print_billing` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Log of printed billing (bill-payment) slips, with references, billing document number and amount.

Read by: [validated_mac5.log_print_billing](/validated/validated_mac5/log_print_billing.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Row identifier of the print log entry. |
| `ref1` | STRING | Bill-payment reference 1, holding the MAC5 customer (debtor) code. |
| `ref2` | STRING | Bill-payment reference 2, a 13-digit code built from the billing document number. |
| `order_no` | STRING | Billing document number (e.g. `BAB6610247`). |
| `amount` | FLOAT64 | Billed amount in THB. |
| `status` | INT64 | Status flag of the print log entry (0 or 1). |
| `dinsert` | STRING | Date the billing slip was printed. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/log_print_billing/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.log_print_billing`
LIMIT 100
```
