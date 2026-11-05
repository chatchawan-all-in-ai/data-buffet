---
type: BigQuery Table
title: "pro_crc"
description: "One row = one product in a CRC-channel promotion, a record of source table `pro_crc` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=pro_crc&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: pro_crc
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

External table over AVRO files in `gs://file-raw-data/mac5_ag01/pro_crc/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `pro_crc` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Products included in CRC-channel promotions of the MAC5 ERP, with promotion set code, period and region.

Read by: [validated_mac5.pro_crc](/validated/validated_mac5/pro_crc.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `id` | INT64 | Running ID of the promotion item row. |
| `procrcstkcode` | STRING | Stock (product) code included in the promotion. |
| `procrcsttcode` | STRING | Promotion set code the product belongs to (numeric, e.g. `80164`). |
| `procrcstt` | STRING | Promotion item status flag (`y` = active). |
| `procrcstrdate` | STRING | Start date of the promotion period. |
| `procrcenddate` | STRING | End date of the promotion period. |
| `procrcregion` | STRING | Region the promotion applies to (`ALL` = all regions). |
| `dinsert` | STRING | Date and time the row was inserted. |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/pro_crc/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.pro_crc`
LIMIT 100
```
