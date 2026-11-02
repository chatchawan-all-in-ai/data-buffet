---
type: BigQuery Table
title: "rcv"
description: "One row = one received serial-numbered unit (per company), unique on (company_id, serial)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=rcv&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: rcv
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/rcv.sqlx"
    title: "Dataform definition (validated/mac5/rcv.sqlx)"
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

Validated copy of MAC5 `rcv`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Finished-goods receiving log by unit serial number (product, warehouse, order and packing details).
No other table or view in this repository reads it.

# Grain and key

One row per `company_id`, `serial`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `serial` | STRING | Serial number of the received unit; unique within the company. |
| `rcvdate` | STRING | Receiving date, as text. |
| `rcvtype` | INT64 | Receiving type code. |
| `rcvvnos` | STRING | Number of the receiving document. |
| `rcvstk` | STRING | Product (stock) code of the received unit. |
| `desct1` | STRING | Product description in Thai. |
| `qty` | STRING | Received quantity, as text. |
| `unit` | STRING | Unit of the received quantity. |
| `rcvsto` | STRING | Warehouse (store) code the unit is received into. |
| `username` | STRING | User who recorded the receipt. |
| `remark` | STRING | Free-text remark. |
| `rcvtime` | STRING | Receiving time, as text. |
| `fdatetime2` | STRING | Record date and time, as text. |
| `rcvstatus` | STRING | Receiving status code. |
| `rcvtypefg` | STRING | Finished-goods receiving type code. |
| `rcvstatusmr` | STRING | Material-receipt status code. |
| `rcvzone` | STRING | Storage zone code. |
| `rcvorder` | STRING | Order number the unit is received for. |
| `rcvcommand` | STRING | Production command (work order) number. |
| `rcvextcode` | STRING | External code of the received unit. |
| `mixvnos` | STRING | Number of the linked ERP document. |
| `mixdate` | DATETIME | Date of the linked ERP document. |
| `rcvtrancode` | STRING | Transfer code of the receipt. |
| `rcvcancel` | INT64 | Cancellation flag of the receipt. |
| `rcvorder_pack` | STRING | Order number used for packing. |
| `adjvnos` | STRING | Number of the related stock-adjustment document. |
| `packdate` | STRING | Packing date, as text. |
| `packtime` | STRING | Packing time, as text. |
| `rcvconvert` | INT64 | Flag: receipt converted into an ERP document. |
| `odate` | STRING | Date of the last status change, as text. |
| `ouser` | STRING | User of the last status change. |
| `fmil2listno` | INT64 | Line number of the linked document line. |
| `ostatus` | STRING | Status after the last change. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/mac5/rcv.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.rcv](/initial/raw_mac5_ag01/rcv.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `company_id`, `serial`.
- Approximate size (BigQuery metadata, 2026-10-31): 0 rows, 0 B.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.rcv`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, serial, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.rcv`
GROUP BY company_id, serial
HAVING n > 1
```
