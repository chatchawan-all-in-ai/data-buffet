---
type: BigQuery Table
title: "organize_type"
description: "One row = one organization type, a record of source table `organize_type` (CIS360) as delivered in the GCS extract for one ASATDATE folder (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_cis360&t=organize_type&page=table"
project_id: databuffet-nonprd
dataset_id: raw_cis360
table_id: organize_type
tags: ["initial", "raw_cis360", "cis360"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/cis360/create_all_table_raw_cis360.sqlx"
    title: "Dataform definition (initial/cis360/create_all_table_raw_cis360.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/cis360/organize_type/*` (Hive-partitioned by `ASATDATE=YYYYMMDD`). It is the raw landing copy of the `organize_type` table from CIS360; nothing is cleaned or deduplicated here. Table meaning: Lookup of CIS360 organization types (head office, branch).

Read by: [validated_cis360.organize_type](/validated/validated_cis360/organize_type.md).

# Grain and key

One row per source record **per ASATDATE partition**: the same business record appears again in every day's extract (full snapshots) or only when it changed (incremental feeds), depending on the source. There is no key at this layer; the validated table defines the key and keeps the newest `asatdate` per key.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key of the organization type lookup. |
| `organize_type_name` | STRING | Organization type name in Thai. |
| `organize_type_name_en` | STRING | Organization type name in English. |
| `organize_type_code` | STRING | Organization type code (`HEAD_OFFICE`, `BRANCH`). |
| `organize_type_order` | INT64 | Display sort order of the organization type. |
| `is_constant` | BOOL | Whether the organization type is a fixed system-defined value. |
| `active_status` | BOOL | Whether the organization type is active. |
| `is_delete` | BOOL | Soft-delete flag (TRUE = record deleted). |
| `create_date` | STRING | Timestamp when the record was created. |
| `create_by` | STRING | Identifier of the user or system that created the record. |
| `create_by_platform` | STRING | Code of the platform that created the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_by_platform` | STRING | Code of the platform that last updated the record (`D365`, `ALLKONS_AMRP`, `ALLKONS_ID`, `ALLKONS_M_SELLER`, `ALLKONS_M_BUYER`, `CIS360`, `SYSTEM`). |
| `update_date` | STRING | Timestamp when the record was last updated. |
| `update_by` | STRING | Identifier of the user or system that last updated the record. |
| `ASATDATE` | STRING | Hive partition column (STRING `YYYYMMDD`): the extract date of the GCS folder the row came from. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_cis360` (`definitions/initial/cis360/create_all_table_raw_cis360.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/cis360/organize_type/*`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

Yesterday's extract:

```sql
SELECT *
FROM `databuffet-nonprd.raw_cis360.organize_type`
WHERE ASATDATE = FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 1 DAY))
LIMIT 100
```

Row counts per extract day over the last week:

```sql
SELECT ASATDATE, COUNT(*) AS n
FROM `databuffet-nonprd.raw_cis360.organize_type`
WHERE ASATDATE >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY))
GROUP BY ASATDATE
ORDER BY ASATDATE
```
