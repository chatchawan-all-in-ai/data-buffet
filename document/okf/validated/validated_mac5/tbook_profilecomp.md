---
type: BigQuery Table
title: "tbook_profilecomp"
description: "One row = one project profile from source table `tbook_profilecomp` (no declared key; not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbook_profilecomp&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbook_profilecomp
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbook_profilecomp.sqlx"
    title: "Dataform definition (validated/mac5/tbook_profilecomp.sqlx)"
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

Validated copy of MAC5 `tbook_profilecomp`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`. There is no business logic at this layer. Table meaning: Construction project and company profiles of the quotation app, with project dates, value, location and contacts; source of dim_project.

Read by: [dimension_table.dim_project](/dimension/dim_project.md).

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `docno` | INT64 | Document number of the project profile. |
| `projectcode` | INT64 | Project code, referenced by the quotation project text. |
| `projectname` | STRING | Project name. |
| `statuscomp` | STRING | Project status colour (`เขียว` = green, `เหลือง` = yellow, `แดง` = red). |
| `compname` | STRING | Company name of the project owner or contractor. |
| `register` | STRING | Company registration (tax ID) number. |
| `addresscomp` | STRING | Company address. |
| `province` | STRING | Province of the project. |
| `district` | STRING | District of the project. |
| `country` | STRING | Country of the project. |
| `status` | STRING | Work category of the project (e.g. residential, hotel, housing estate, school). |
| `capital` | STRING | Registered capital of the company. |
| `place` | STRING | Location of the project. |
| `tel` | STRING | Company phone number. |
| `mobile` | STRING | Contact mobile number. |
| `fax` | STRING | Company fax number. |
| `mail` | STRING | Contact email address. |
| `namedirector` | STRING | Name of the company director or decision maker. |
| `nickname` | STRING | Nickname of the contact person. |
| `teldirector` | STRING | Phone number of the director. |
| `profilecomp` | STRING | Project profile description (e.g. condominium, hotel). |
| `typecomp` | STRING | Business type of the company (e.g. construction contractor, hotel). |
| `startdate` | STRING | Date the profile was opened. |
| `history` | STRING | Background history of the project or company. |
| `pjstart` | STRING | Project start date (text). |
| `pjend` | STRING | Project end date (text). |
| `pjval` | STRING | Project value (text). |
| `pjfor` | STRING | Expected purchase value for the project (text). |
| `compgroup` | STRING | Company group of the project. |
| `acccode` | STRING | Account code linked to the project (e.g. `AC958-60`). |
| `accname` | STRING | Account name linked to the project. |
| `closedby` | STRING | User who closed the project. |
| `projectfrom` | STRING | Source of the project lead. |
| `ptype` | STRING | Profile type (e.g. `Project`). |
| `ppc` | STRING | PPC code of the project. |
| `pecom` | STRING | PE commission value of the project. |
| `uinsert` | STRING | Employee code of the user who created the row. |
| `dinsert` | DATETIME | Date and time the row was created. |
| `insertby` | STRING | Employee code of the user who created the profile. |
| `uupdate` | STRING | Employee code of the user who last updated the row. |
| `dupdate` | DATETIME | Date and time the row was last updated. |
| `meccode` | STRING | Customer branch (ship-to) code, matching `mec.meccode`. |
| `contactdebcode` | STRING | MAC5 customer (debtor) code of the contact. |
| `refallkon` | STRING | Allkons reference code of the project. |

# How it is built

- Definition: `definitions/validated/mac5/tbook_profilecomp.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbook_profilecomp](/initial/raw_mac5_ag01/tbook_profilecomp.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: not partitioned; cluster by `company_id`, `docno`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbook_profilecomp`
LIMIT 100
```
