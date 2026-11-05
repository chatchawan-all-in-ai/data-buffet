---
type: BigQuery Table
title: "crm_business_unit"
description: "One row = one business unit node from source table `crm_business_unit`, unique on (business_unit_id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_derp&t=crm_business_unit&page=table"
project_id: databuffet-nonprd
dataset_id: validated_derp
table_id: crm_business_unit
tags: ["validated", "validated_derp", "derp", "validated_incremental"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/derp/crm_business_unit.sqlx"
    title: "Dataform definition (validated/derp/crm_business_unit.sqlx)"
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

Validated copy of DERP `crm_business_unit`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Business unit (product line) hierarchy of the CRM, with the responsible employee and two alternates per unit.
No other table or view in this repository reads it.

# Grain and key

One row per `business_unit_id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `business_unit_id` | STRING | UUID of the business unit. |
| `bu_code` | STRING | Business unit code (e.g. `0311`; hierarchical, child codes extend the parent code). |
| `bu_name` | STRING | Business unit name. |
| `bu_description` | STRING | Description of the business unit (product line). |
| `level` | INT64 | Depth of the node in the hierarchy (1 = top level). |
| `parent_id` | STRING | UUID of the parent node in the same hierarchy (NULL at the top level). |
| `parent_code` | STRING | Code of the parent business unit. |
| `path_id` | STRING | Chain of business-unit UUIDs from the top level down to this unit. |
| `path_code` | STRING | Chain of business-unit codes from the top level down to this unit (e.g. `03`, `031`, `0311`). |
| `path_name` | STRING | Chain of business-unit names from the top level down to this unit. |
| `company_id` | STRING | UUID of the company that owns the record. |
| `company_code` | STRING | Code of the company that owns the record. |
| `organization_id` | STRING | UUID of the organization that owns the record. |
| `organization_code` | STRING | Code of the organization that owns the record. |
| `responsible_employee_id` | STRING | UUID of the employee responsible for the business unit. |
| `responsible_employee_no` | STRING | Employee number of the employee responsible for the business unit. |
| `responsible_user_id` | STRING | User UUID of the employee responsible for the business unit. |
| `responsible_name` | STRING | Name of the employee responsible for the business unit. |
| `responsible_effective_date` | DATE | Date the responsible employee assignment starts. |
| `responsible_expiry_date` | DATE | Date the responsible employee assignment ends. |
| `alt1_employee_id` | STRING | UUID of the first alternate responsible employee. |
| `alt1_employee_no` | STRING | Employee number of the first alternate responsible employee. |
| `alt1_user_id` | STRING | User UUID of the first alternate responsible employee. |
| `alt1_name` | STRING | Name of the first alternate responsible employee. |
| `alt1_effective_date` | DATE | Date the first alternate assignment starts. |
| `alt1_expiry_date` | DATE | Date the first alternate assignment ends. |
| `alt2_employee_id` | STRING | UUID of the second alternate responsible employee. |
| `alt2_employee_no` | STRING | Employee number of the second alternate responsible employee. |
| `alt2_user_id` | STRING | User UUID of the second alternate responsible employee. |
| `alt2_name` | STRING | Name of the second alternate responsible employee. |
| `alt2_effective_date` | DATE | Date the second alternate assignment starts. |
| `alt2_expiry_date` | DATE | Date the second alternate assignment ends. |
| `status` | STRING | Record status (`ACTIVE`, `INACTIVE` or `DELETED`). |
| `created_at` | DATETIME | Timestamp when the record was created. |
| `created_by` | STRING | Identifier of the user who created the record. |
| `created_by_name` | STRING | Display name of the user who created the record. |
| `updated_at` | DATETIME | Timestamp when the record was last updated. |
| `updated_by` | STRING | Identifier of the user who last updated the record. |
| `updated_by_name` | STRING | Display name of the user who last updated the record. |
| `asatdate` | DATE | Extract date (the raw ASATDATE partition parsed to DATE) of the winning row; used as the dedup tiebreaker and the partition column. |

# How it is built

- Definition: `definitions/validated/derp/crm_business_unit.sqlx` (`type: "incremental"`, tags `validated`, `validated_incremental`).
- Reads: [raw_derp.crm_business_unit](/initial/raw_derp/crm_business_unit.md).
- **Incremental**: each run reads only raw partitions with `ASATDATE` within the last `BACKFILL_DAYS` days and MERGEs on `uniqueKey`. A first or full build reads every raw partition.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY COALESCE(updated_at, created_at) DESC, asatdate DESC) = 1`.
- Storage: partition by `asatdate`, cluster by `business_unit_id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_derp.crm_business_unit`
WHERE asatdate >= DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL 7 DAY)
LIMIT 100
```

Duplicate keys:

```sql
SELECT business_unit_id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_derp.crm_business_unit`
GROUP BY business_unit_id
HAVING n > 1
```
