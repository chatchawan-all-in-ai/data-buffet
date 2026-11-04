---
type: BigQuery Table
title: "address_type"
description: "One row = one address type from source table `address_type`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_cis360&t=address_type&page=table"
project_id: databuffet-nonprd
dataset_id: validated_cis360
table_id: address_type
tags: ["validated", "validated_cis360", "cis360", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/cis360/address_type.sqlx"
    title: "Dataform definition (validated/cis360/address_type.sqlx)"
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

Validated copy of CIS360 `address_type`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Lookup of CIS360 address types (official, shipping, contact, billing, KYC, work site, warehouse, etc.).
No other table or view in this repository reads it.

# Grain and key

One row per `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key of the address type lookup. |
| `address_type_name` | STRING | Address type name in Thai. |
| `address_type_name_en` | STRING | Address type name in English. |
| `address_type_code` | STRING | Address type code (`T` = official, `S` = shipping, `C` = contact, `A` = billing (AR), `D` = default, `K` = KYC document, `W` = work site, `DDA` = document delivery, `WH` = warehouse). |
| `address_type_order` | INT64 | Display sort order of the address type. |
| `is_constant` | BOOL | Whether the address type is a fixed system-defined value. |
| `active_status` | BOOL | Whether the address type is active. |
| `is_delete` | BOOL | Soft-delete flag (TRUE = record deleted). |
| `create_date` | DATETIME | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | DATETIME | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/cis360/address_type.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_cis360.address_type](/initial/raw_cis360/address_type.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days (currently 1; string compare) and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_cis360.address_type`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_cis360.address_type`
GROUP BY id
HAVING n > 1
```
