---
type: BigQuery Table
title: "curated_invoice_line_cost"
description: "One row = one MAC5 document line (per salesperson row) of a document with a matched posted DERP journal, carrying the DERP cost allocated to it, plus NO_LINE rows for journal cost that no line accounts for."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=curated_derp&t=curated_invoice_line_cost&page=table"
project_id: databuffet-nonprd
dataset_id: curated_derp
table_id: curated_invoice_line_cost
tags: ["curated", "curated_derp", "derp", "DERP"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/curated/derp/curated_invoice_line_cost.sqlx"
    title: "Dataform definition (curated/derp/curated_invoice_line_cost.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/curated/curated-layer.md"
    title: "Data Mart wiki (document/project_wiki/curated/curated-layer.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:00:00+07:00" }
status: draft
---

# What it is

DERP cost per MAC5 document line. The cost of a document is the net sum of the `journalCost` of its posted journals with `matchStatus = 'MATCHED'` in [curated_journal_invoice](/curated/curated_derp/curated_journal_invoice.md). It is allocated by product, not by sales value: a line is mapped to a DERP item key through its stock barcode and the master SKU barcode, and the cost of each key in the journal entries is split over the lines that carry that key. Cost that no line accounts for is kept in separate `NO_LINE` rows, so the sum of `costDerp` per document equals `invoiceCostDerp`.

# Grain and key

One row = one document line of [curated_mil](/curated/curated_mac5/curated_mil.md): key `company_id`, `milType`, `milVnos`, `milListno`, `milPer` (ag01 split-sale lines are one row per salesperson); rows identical on those five columns plus `milStk`, `milQuan` and `milSum` are collapsed (`SELECT DISTINCT`). Only documents with at least one matched, posted journal that has a non-NULL cost are included. A document also gets one `NO_LINE` row per DERP item key (`itemNumber`, color, size, style) of its journal entries that no line was mapped to; those rows have NULL line columns. No declared `uniqueKey`.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code of the document; part of the key. |
| `milType` | STRING | Document type code of the line (`mihType` of the matched journal document); part of the key. |
| `milVnos` | STRING | Document number of the line; part of the key. |
| `milListno` | INT64 | Line number within the document; NULL on `NO_LINE` rows. |
| `milPer` | STRING | Salesperson code of the line row from [curated_mil](/curated/curated_mac5/curated_mil.md) (second rep on ag01 split-sale rows); NULL on `NO_LINE` rows. |
| `milStk` | STRING | Product (stock) code of the line; NULL on `NO_LINE` rows. |
| `milQuan` | FLOAT64 | Line quantity from `curated_mil` (`milQuan`); NULL on `NO_LINE` rows. |
| `milSum` | FLOAT64 | Net line amount from `curated_mil` (`milSum`); NULL on `NO_LINE` rows. |
| `itemNumber` | STRING | DERP item number (`item_number` of the journal entries) of the unmatched key; set only on `NO_LINE` rows, otherwise NULL. |
| `productColorId` | STRING | DERP product color of the unmatched key; set only on `NO_LINE` rows (NULL when empty). |
| `productSizeId` | STRING | DERP product size of the unmatched key; set only on `NO_LINE` rows (NULL when empty). |
| `productStyleId` | STRING | DERP product style of the unmatched key; set only on `NO_LINE` rows (NULL when empty). |
| `costStatus` | STRING | Result of the cost mapping for the line: `MATCHED` (cost allocated), `NO_BARCODE` (the line's `milStk` has no barcode in `validated_mac5.stk`), `NO_SKU` (barcode found but no master SKU with a D365 code carries it), `NO_ENTRY` (SKU found but the document's journal entries have no cost for that item key), `NO_LINE` (cost key with no line). |
| `allocationBasis` | STRING | How the key cost was split over lines sharing the same item key in the document: `MILSUM` (in proportion to `milSum`, when the key's `milSum` total is not 0), `MILQUAN` (in proportion to `milQuan`, when `milSum` totals 0), `EQUAL` (equal split). Comma-joined when the line has several keys with different bases; NULL unless `costStatus = 'MATCHED'`. |
| `costDerp` | FLOAT64 | DERP cost allocated to the line (sum over its item keys); the full key cost on `NO_LINE` rows; NULL when the line could not be mapped (not a cost of 0). |
| `invoiceCostDerp` | FLOAT64 | Net cost of the whole document: sum of `journalCost` over its matched, posted journals; repeated on every row of the document. |
| `journalCount` | INT64 | Number of matched, posted journals counted in `invoiceCostDerp`. |

# How it is built

- Definition: `definitions/curated/derp/curated_invoice_line_cost.sqlx` (`type: "table"`, tags `curated`).
- Storage options: `{"clusterBy": ["company_id", "milVnos", "milType"]}`.
- Reads: [curated_derp.curated_journal_invoice](/curated/curated_derp/curated_journal_invoice.md) (`matchStatus = 'MATCHED'`, `isPosted`, `journalCost` not NULL), [validated_derp.inventory_movement_journal_entries](/validated/validated_derp/inventory_movement_journal_entries.md), [curated_mac5.curated_mil](/curated/curated_mac5/curated_mil.md), [validated_mac5.stk](/validated/validated_mac5/stk.md) (`stkbarc1`, `stkbarc2`, `stkbarc3`, `stkcode885`), [validated_master_sku.products](/validated/validated_master_sku/products.md) (`universal_barcode`, `internal_barcode`, `d365_code`, `d365_color`, `d365_size`, `d365_style`).
- Key cost per document and item key (`item_number`, color, size, style; empty values compared as `''`) is the negated sum of `cost_amount` of the journal entries; the key cost is split over the line rows of the document that map to the same key.
- Full rebuild (`type: "table"`, tag `curated`); runs after `curated_schema_derp`.

# Examples

Lines of one invoice with their allocated cost.

```sql
SELECT milListno, milPer, milStk, milSum, costStatus, allocationBasis, costDerp, invoiceCostDerp
FROM `databuffet-nonprd.curated_derp.curated_invoice_line_cost`
WHERE company_id = 'ag01' AND milType = 'IS' AND milVnos = 'REPLACE_WITH_DOCUMENT_NUMBER'
ORDER BY milListno
```

Cost status breakdown.

```sql
SELECT costStatus, COUNT(*) AS n, SUM(costDerp) AS total_cost
FROM `databuffet-nonprd.curated_derp.curated_invoice_line_cost`
GROUP BY costStatus
ORDER BY n DESC
```
