---
type: BigQuery Table
title: "tmp_pdf_ap"
description: "One row = one cleaned source record of `tmp_pdf_ap` (no declared key; append-style, not deduplicated)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tmp_pdf_ap&page=table"
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tmp_pdf_ap.sqlx"
    title: "Dataform definition (validated/mac5/tmp_pdf_ap.sqlx)"
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

Validated copy of MAC5 `tmp_pdf_ap`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer.
No other table or view in this repository reads it.

# Grain and key

No key: `uniqueKey` is not set, so rows are not deduplicated and no primary key is created.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code (ag01 / aa05 / ab01 / ac02 / ak02): a literal injected per UNION branch, one per MAC5 company database. |
| `crdate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `vendorno` | STRING | Meaning not documented in the repo. |
| `vendorname` | STRING | Meaning not documented in the repo. |
| `newpo` | STRING | Meaning not documented in the repo. |
| `pono` | STRING | Meaning not documented in the repo. |
| `podate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `potype` | STRING | Likely document/type code (inferred from the column name only; not documented in the repo). |
| `deliverydate` | STRING | Meaning not documented in the repo. |
| `siteno` | STRING | Meaning not documented in the repo. |
| `sitename` | STRING | Meaning not documented in the repo. |
| `siteaddress` | STRING | Meaning not documented in the repo. |
| `totalqty` | STRING | Meaning not documented in the repo. |
| `totalamount` | STRING | Meaning not documented in the repo. |
| `totalitem` | STRING | Meaning not documented in the repo. |
| `cancelpo` | STRING | Meaning not documented in the repo. |
| `termcode` | STRING | Meaning not documented in the repo. |
| `poremark` | STRING | Likely free-text remark (inferred from the column name only; not documented in the repo). |
| `quotationno` | STRING | Meaning not documented in the repo. |
| `quotationdate` | STRING | Meaning not documented in the repo. |
| `poitemno` | STRING | Meaning not documented in the repo. |
| `artno` | STRING | Meaning not documented in the repo. |
| `artdesc` | STRING | Meaning not documented in the repo. |
| `hpeancode` | STRING | Meaning not documented in the repo. |
| `vdeancode` | STRING | Meaning not documented in the repo. |
| `vdproductname` | STRING | Meaning not documented in the repo. |
| `qty` | STRING | Likely quantity (inferred from the column name only; not documented in the repo). |
| `purchunit` | STRING | Meaning not documented in the repo. |
| `price` | STRING | Likely price (inferred from the column name only; not documented in the repo). |
| `qtyperunit` | STRING | Meaning not documented in the repo. |
| `priceperunit` | STRING | Meaning not documented in the repo. |
| `priceunit` | STRING | Meaning not documented in the repo. |
| `packsize` | STRING | Meaning not documented in the repo. |
| `articleremark` | STRING | Meaning not documented in the repo. |
| `freegoodsflag` | STRING | Meaning not documented in the repo. |
| `stk` | STRING | Likely stock (SKU) code (inferred from the column name only; not documented in the repo). |
| `novat` | STRING | Meaning not documented in the repo. |
| `status` | STRING | Likely status code (inferred from the column name only; not documented in the repo). |
| `statusticket` | STRING | Meaning not documented in the repo. |
| `duedate` | STRING | Likely date (inferred from the column name only; not documented in the repo). |
| `reciver` | STRING | Meaning not documented in the repo. |
| `deladd` | STRING | Meaning not documented in the repo. |
| `que` | STRING | Meaning not documented in the repo. |
| `delvname` | STRING | Meaning not documented in the repo. |
| `delvtel` | STRING | Meaning not documented in the repo. |
| `credit` | STRING | Meaning not documented in the repo. |
| `dinsert` | STRING | Meaning not documented in the repo. |

# How it is built

- Definition: `definitions/validated/mac5/tmp_pdf_ap.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tmp_pdf_ap](/initial/raw_mac5_ag01/tmp_pdf_ap.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Storage: partition by `(none)`, cluster by `company_id`, `vendorno`.
- Approximate size (BigQuery metadata, 2026-10-31): 8,631 rows, 3.4 MB.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tmp_pdf_ap`
LIMIT 100
```
