---
type: BigQuery Table
title: "mip"
description: "One row = one file attached to a document from source table `mip` (no declared key; not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=mip&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: mip
tags: ["validated", "validated_mac5", "mac5", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/mip.sqlx"
    title: "Dataform definition (validated/mac5/mip.sqlx)"
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

Validated copy of MAC5 `mip`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`. There is no business logic at this layer. Table meaning: Files attached to ERP documents (purchase orders, maps, BOQs, quotations), one row per document, file number and revision.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `mipvnos` | STRING | Number of the document the file is attached to. |
| `mipfileno` | INT64 | Sequence number of the attached file within the document. |
| `miprev` | INT64 | Revision number of the attachment. |
| `mippath` | STRING | File path or file name of the attachment. |
| `miptype` | STRING | Attachment type code (e.g. `POD`, `MAP`, `BOQ`, `QOD`, `ETC`). |
| `mipcrdate` | DATETIME | Date and time the attachment was created. |
| `mipupdatedate` | DATETIME | Date and time the attachment was last updated. |

# How it is built

- Definition: `definitions/validated/mac5/mip.sqlx` (`type: "table"`, tags `validated`, `validated_incremental`).
- Reads: [raw_mac5_ag01.mip](/initial/raw_mac5_ag01/mip.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `mipvnos`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.mip`
LIMIT 100
```
