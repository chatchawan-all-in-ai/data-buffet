---
type: BigQuery Table
title: "tdis_approveqt"
description: "One row = one quotation approval request per product line, a record of source table `tdis_approveqt` (MAC5 for company `ag01`) as delivered in the GCS extract (raw, uncleaned)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=raw_mac5_ag01&t=tdis_approveqt&page=table"
project_id: databuffet-nonprd
dataset_id: raw_mac5_ag01
table_id: tdis_approveqt
tags: ["initial", "raw_mac5_ag01", "mac5"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/initial/mac5/create_all_table_raw_mac5.sqlx"
    title: "Dataform definition (initial/mac5/create_all_table_raw_mac5.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/initial/initial-layer.md"
    title: "Data Mart wiki (document/project_wiki/initial/initial-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

External table over AVRO files in `gs://file-raw-data/mac5_ag01/tdis_approveqt/*.avro` (no partition columns, the whole glob is read). It is the raw landing copy of the `tdis_approveqt` table from MAC5 for company `ag01`; nothing is cleaned or deduplicated here. Table meaning: Approval requests of quotations per product-line approval type, with approval results, users, dates and notes per level. Used by: [validated_mac5.tdis_approveqt](/validated/validated_mac5/tdis_approveqt.md).

# Grain and key

One row per source record in the files under the URI. No key is declared at this layer. The files are replaced or appended by the extract job, so the row set is the content of the files.

# Schema

| Column | Type | Description |
|---|---|---|
| `docno` | STRING | Quotation identifier (`tbook_quotation.id`) sent for approval. |
| `lv1` | STRING | Level-1 approval result code. |
| `lv2` | STRING | Level-2 approval result code. |
| `lv3` | STRING | Level-3 approval result code (1, 2, 0). |
| `note1` | STRING | Level-1 approval note. |
| `note2` | STRING | Level-2 approval note. |
| `note3` | STRING | Level-3 approval note. |
| `u1` | STRING | User who acted at approval level 1. |
| `u2` | STRING | User who acted at approval level 2. |
| `u3` | STRING | Employee code of the user who acted at approval level 3. |
| `d1` | STRING | Date and time of the level-1 approval (text). |
| `d2` | STRING | Date and time of the level-2 approval (text). |
| `d3` | STRING | Date and time of the level-3 approval (text). |
| `sendto` | STRING | Sent-for-approval flag (1 = sent). |
| `sendtime` | STRING | Date the quotation was sent for approval (text). |
| `comment` | STRING | Sales comment attached to the approval request, such as delivery instructions. |
| `stktype` | STRING | Product-line approval type code (`tbook_apptype.iddesc`, e.g. `PE`, `PUMP`, `RP`). |

# How it is built

- Created by the Dataform operation `create_all_table_raw_mac5` (`definitions/initial/mac5/create_all_table_raw_mac5.sqlx`, tag `initial`) with `CREATE OR REPLACE EXTERNAL TABLE` (preceded by `DROP TABLE IF EXISTS`). It is a metadata object: no data is stored in BigQuery, every query reads the GCS files.
- Format `AVRO`, URI `gs://file-raw-data/mac5_ag01/tdis_approveqt/*.avro`.
- Refresh: the extract job drops new files in the bucket; the external table sees them immediately. Dataform does not refresh it daily.

# Examples

File sample (scans all files):

```sql
SELECT *
FROM `databuffet-nonprd.raw_mac5_ag01.tdis_approveqt`
LIMIT 100
```
