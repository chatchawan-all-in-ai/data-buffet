---
type: BigQuery Table
title: "per"
description: "One row = one employee (per company), unique on (company_id, percode)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=per&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: per
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/per.sqlx"
    title: "Dataform definition (validated/mac5/per.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `per` (UNION ALL of 5 company databases: ag01, aa05, ab01, ac02, ak02): every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: Employee master of the MAC5 ERP (mainly salespeople): name, department, position, employment dates and contact details.

Read by: [dimension_table.dim_sale_representative](/dimension/dim_sale_representative.md), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_invoice](/dimension/dim_invoice.md), [dimension_table.dim_order](/dimension/dim_order.md), [pub_sub.export_sell](/view/pub_sub/export_sell.md).

# Grain and key

One row per `company_id`, `percode`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `percode` | STRING | Employee (salesperson) code. |
| `perdep` | STRING | Department code of the employee (joins `dep.depcode`). |
| `pertaxnos` | STRING | Tax ID of the employee. |
| `pernamet` | STRING | Employee name in Thai (first name, surname and nickname in parentheses). |
| `pernamee` | STRING | Employee name in English. |
| `perbdate` | DATETIME | Birth date of the employee. |
| `perworks` | DATETIME | Employment start date. |
| `perworkf` | DATETIME | Employment end date. |
| `peradd1` | STRING | Address line 1 of the employee. |
| `peradd2` | STRING | Address line 2 of the employee. |
| `peradd3` | STRING | Address line 3 of the employee. |
| `pertel` | STRING | Phone number of the employee. |
| `perpositn` | STRING | Job position title in Thai (e.g. Agent salesperson, TA Water Solution). |
| `perstatus` | INT64 | Employment status code (0, 1, 2). |
| `pernchild` | INT64 | Number of children of the employee. |
| `percisstudy` | INT64 | Number of the employee's children in school. |
| `pernotstudy` | INT64 | Number of the employee's children not in school. |
| `persalary` | FLOAT64 | Salary of the employee. |
| `perhide` | INT64 | Hidden flag (-1 = hidden from pick lists, 0 = shown). |
| `perlock` | INT64 | Lock flag (-1 = locked against editing, 0 = unlocked). |
| `permemo` | STRING | Free-text memo on the employee. |
| `pereditlk` | DATETIME | Date and time the record was locked for editing. |
| `perrefwe` | STRING | External reference code of the record. |
| `pereditdt` | DATETIME | Date and time the record was last edited. |
| `pereditmf` | STRING | User code of the person who last edited the record. |
| `perzone` | STRING | Sales zone of the employee. |

# How it is built

- Definition: `definitions/validated/mac5/per.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.per](/initial/raw_mac5_ag01/per.md), [raw_mac5_aa05.per](/initial/raw_mac5_aa05/per.md), [raw_mac5_ab01.per](/initial/raw_mac5_ab01/per.md), [raw_mac5_ac02.per](/initial/raw_mac5_ac02/per.md), [raw_mac5_ak02.per](/initial/raw_mac5_ak02/per.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY perbdate desc, pernamet desc, pernamee desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `percode`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.per`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, percode, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.per`
GROUP BY company_id, percode
HAVING n > 1
```
