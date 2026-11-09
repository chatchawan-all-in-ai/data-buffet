---
type: BigQuery Table
title: "crm_quotation_terr_sale"
description: "One row = one salesperson assignment for a quotation territory from source table `crm_quotation_terr_sale`, unique on (quotation_terr_sale_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_quotation_terr_sale&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_quotation_terr_sale
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_quotation_terr_sale.sqlx"
    title: "Dataform definition (definitions/validated/derp/crm_quotation_terr_sale.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:codex/gpt-6", at: "2026-11-09T14:18:32+07:00" }
status: draft
---

# What it is

Validated copy of DERP `crm_quotation_terr_sale`: source columns are cleaned or cast with shared helpers, the extract date is standardized to `asatdate`, and duplicate keys are collapsed. There is no business logic at this layer. Table meaning: Salesperson and organization assignments recorded for a quotation territory.

# Grain and key

One row per `quotation_terr_sale_id`. The key is declared in `uniqueKey` and `pk_key`, and added as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `quotation_terr_sale_id` | STRING | Source identifier of the quotation-territory salesperson record. |
| `quotation_id` | STRING | Identifier of the quotation. |
| `quotation_date` | DATE | Date of the quotation, parsed from the source date-time text. |
| `quotation_no` | STRING | Quotation number. |
| `sale_id` | STRING | Identifier of the salesperson assigned to the quotation territory. |
| `sale_code` | STRING | Code of the salesperson assigned to the quotation territory. |
| `sale_name` | STRING | Name of the salesperson assigned to the quotation territory. |
| `sale_nickname` | STRING | Nickname of the salesperson assigned to the quotation territory. |
| `department_id` | STRING | Identifier of the department in the assignment hierarchy. |
| `department_code` | STRING | Code of the department in the assignment hierarchy. |
| `department_name` | STRING | Name of the department in the assignment hierarchy. |
| `section_id` | STRING | Identifier of the section in the assignment hierarchy. |
| `section_code` | STRING | Code of the section in the assignment hierarchy. |
| `section_name` | STRING | Name of the section in the assignment hierarchy. |
| `division_id` | STRING | Identifier of the division in the assignment hierarchy. |
| `division_code` | STRING | Code of the division in the assignment hierarchy. |
| `division_name` | STRING | Name of the division in the assignment hierarchy. |
| `ta_area_id` | STRING | Identifier of the TA area in the assignment hierarchy. |
| `ta_area_code` | STRING | Code of the TA area in the assignment hierarchy. |
| `ta_area_name` | STRING | Name of the TA area in the assignment hierarchy. |
| `path_id` | STRING | Identifier of the sales path in the assignment hierarchy. |
| `path_code` | STRING | Code of the sales path in the assignment hierarchy. |
| `path_name` | STRING | Name of the sales path in the assignment hierarchy. |
| `status` | STRING | Status of the source record. |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date of the winning row, parsed from the raw ASATDATE partition; it is the deduplication tiebreaker and table partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_quotation_terr_sale.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_quotation_terr_sale](/initial/raw_derp/crm_quotation_terr_sale.md).
- Incremental runs read the configured ASATDATE lookback and merge on the source key; the first or full build reads all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY quotation_terr_sale_id ORDER BY updated_at DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `quotation_terr_sale_id`.

# Examples

Inspect rows from the current extract:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_quotation_terr_sale`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```
