---
type: BigQuery Table
title: "audit_logs"
description: "One row per `audit_logs` from source table `audit_logs`, unique on (id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_master_sku&t=audit_logs&page=table"
project_id: databuffet-nonprd
dataset_id: validated_master_sku
table_id: audit_logs
tags: ["validated", "validated_master_sku", "master_sku", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/master_sku/audit_logs.sqlx"
    title: "Dataform definition (validated/master_sku/audit_logs.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex", at: "2026-11-08T21:13:49+07:00" }
status: draft
---

# What it is

Validated copy of MASTER_SKU `audit_logs`: string values are cleaned, types are cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Audit events for entities in the master_sku 3.0 product master.

# Grain and key

One row per (id). The key is declared in both `uniqueKey` and `pk_key`; the definition adds it as a `NOT ENFORCED` primary key after a full build.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | STRING | Source identifier for the record. |
| `entity_type` | STRING | Type of entity affected by the event. |
| `entity_id` | STRING | Identifier of the affected entity. |
| `action` | STRING | Action recorded in the audit event. |
| `action_id` | STRING | Identifier of the action. |
| `user_id` | STRING | Identifier of the user associated with the record. |
| `changes` | STRING | Serialized change details. |
| `metadata` | STRING | Additional serialized metadata. |
| `scope_business_unit_id` | STRING | Business unit scope identifier. |
| `scope_vendor_id` | STRING | Vendor scope identifier. |
| `correlation_id` | STRING | Identifier used to correlate related events. |
| `is_from_master_sku_v2` | BOOL | Whether the event originated from master_sku version 2. |
| `created_at` | DATETIME | UTC timestamp when the record was created. |
| `asatdate` | DATE | Extract date parsed from the raw ASATDATE partition; used for deduplication and partitioning. |

# How it is built

- Definition: `definitions/validated/master_sku/audit_logs.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_master_sku.audit_logs](/initial/raw_master_sku/audit_logs.md).
- Incremental runs read raw partitions within the configured `BACKFILL_DAYS` window and MERGE on `uniqueKey`; the first or a full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY id ORDER BY asatdate DESC, created_at DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `id`.

# Examples

Recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_master_sku.audit_logs`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_master_sku.audit_logs`
GROUP BY id
HAVING n > 1
```
