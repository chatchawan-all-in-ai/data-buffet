---
type: BigQuery Table
title: "audit_logs"
description: "One row = one source record in `audit_logs` (MASTER_SKU) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_master_sku&t=audit_logs&page=table"
project_id: databuffet-nonprd
dataset_id: raw_master_sku
table_id: audit_logs
tags: ["initial", "raw_master_sku", "master_sku"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx"
    title: "Dataform definition (initial/master_sku/create_all_table_raw_master_sku.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:codex", at: "2026-11-08T21:13:49+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/master_sku/audit_logs/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of `audit_logs` from MASTER_SKU; no columns are cleaned or deduplicated here. Table meaning: Audit events for entities in the master_sku 3.0 product master.

Read by: [validated_master_sku.audit_logs](/validated/validated_master_sku/audit_logs.md).

# Grain and key

One row per source record per ASATDATE partition. The same business record may appear in multiple extracts; the validated table defines the key and keeps the newest row.

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
| `created_at` | STRING | UTC timestamp when the record was created. |
| `ASATDATE` | STRING | Hive partition date (`YYYYMMDD`) of the GCS extract. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_master_sku` (`definitions/initial/master_sku/create_all_table_raw_master_sku.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery; queries read the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/master_sku/audit_logs/*`.
- Refresh: the extract job writes the files; the external table sees them without a Dataform refresh.

# Examples

Rows in a recent extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_master_sku.audit_logs`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

File-backed row counts per extract date:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_master_sku.audit_logs`
GROUP BY ASATDATE
ORDER BY ASATDATE
```
