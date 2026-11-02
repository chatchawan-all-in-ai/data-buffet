---
type: BigQuery Table
title: "dim_customer_report_info"
description: "One row = one customer report name (shop/account name as shown on reports, whitespace-insensitive) per company, with segment, TA (team-area) chain, sale rep, address and online-shop attributes."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_customer_report_info&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_customer_report_info
tags: ["dimension", "mds", "mac5", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_customer_report_info.sqlx"
    title: "Dataform definition (dimension/dim_customer_report_info.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Report-level customer dimension for Power BI. Invoices carry a `CustomerReportName` (a business display name, which may differ from the debtor code); this table has one row for every such name found in MDS (`mds_data_customer_report_master`) or on any invoice (`view_dim_invoice`), and resolves for it: the customer segment ([dim_customer_segment](/dimension/dim_customer_segment.md): MDS tier, else TT/DC/DA... channel from the latest quotation), the TA department chain (department/section/region/managers/director) and sale rep derived from `deb.debsalesp` or the MDT chain rules, the representative debtor code, credit term and invoice-address SKs. It is joined by [view_fact_transcation](/view/fact_view/view_fact_transcation.md) and exposed through [view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md).

Used by: [dimension_view.view_dim_customer_report_info](/view/dimension_view/view_dim_customer_report_info.md), [fact_view.view_fact_transcation](/view/fact_view/view_fact_transcation.md).

# Grain and key

One row per (`CompanyID`, `CustomerReportKey`), where the key is the report name with all whitespace removed (names differing only by spaces collapse to one row; the spelling kept is the one with most invoices). `CustomerReportInfoSK` is a stable surrogate key (`max_sk + ROW_NUMBER()` for new names). Reserved row `CustomerReportInfoSK = -1` (NULL company/name, `CustomerSegmentSK = -1`, `SegmentSource = 'DEFAULT'`) exists for invoices whose name cannot be joined.

# Schema

| Column | Type | Description |
|---|---|---|
| `CustomerReportInfoSK` | INT64 | Stable surrogate key. -1 is a reserved row for invoices with an empty or unmatched report name; max_sk excludes it. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md) (NULL on the -1 row). |
| `CustomerSegmentSK` | INT64 | Segment SK from [dim_customer_segment](/dimension/dim_customer_segment.md) (matched on company and `Segment3` = tier or channel code); falls back to the 'DC' segment, then to -1 (Non-Segment). |
| `CompanyID` | STRING | MAC5 company code (natural key part; NULL on the -1 row). |
| `CustomerReportName` | STRING | Display name of the shop/account as printed on reports: the spelling most used on invoices (after MDS renames), else the MDS name. |
| `FlagPC` | BOOL | Boolean flag from the MDS customer report master marking a PC (promoter) customer report name; NULL when the name comes only from invoices. |
| `ShopOnline` | STRING | Online-shop attribute from the MDS customer report master (string, cleaned); NULL when not in MDS. |
| `OnlinePercent` | FLOAT64 | Online share from the MDS customer report master (FLOAT64, cast with castFloat64); NULL when not in MDS. |
| `SegmentSource` | STRING | How the segment was determined: 'MDS' (MDS `CustomerTier` matched a segment), 'CHANNEL' (derived from the quotation channel), 'DEFAULT' (fallback / Non-Segment). |
| `SegmentDebcode` | STRING | Debtor code of the shop's most recent invoice, used to look up its channel (a name can have several debcodes). |
| `SegmentChannel` | STRING | Channel code (TT, DC, DA, DG, DD, DT, DR) of that debtor's latest quotation in `tbook_quotation`; NULL if none. |
| `MdsID` | STRING | Id of the source row in the MDS customer report master (trace column); NULL for names that exist only on invoices. |
| `DepartmentSK` | INT64 | Department SK of the shop's TA row in `dim_department_last` (chain level 1). NULL when no TA could be determined. |
| `SectionSK` | INT64 | Section SK of the TA chain (from `dim_department_last`). |
| `RegionSK` | INT64 | Region SK of the TA chain (from `dim_department_last`). |
| `SectionManagerSK` | INT64 | Section manager SK of the TA chain (from `dim_department_last`). |
| `RegionManagerSK` | INT64 | Region manager SK of the TA chain (from `dim_department_last`). |
| `DirectorSK` | INT64 | Director SK of the TA chain (from `dim_department_last`). |
| `TASource` | STRING | How the TA was found: 'DEBSALESP' (the customer's `deb.debsalesp` has exactly one current non-dummy TA), 'MDT' (modern-trade chain employee: chain from `deb.debgroup`, slot picked via latest invoice `mihDep`), or NULL (no TA). Not read from MDS. |
| `TADebcode` | STRING | Debtor code used to find the TA (a code whose own display name equals the report name; latest invoice if several). |
| `SaleRepSK` | INT64 | Sale representative SK from `dim_sale_representative_last` for the employee behind the TA (`debsalesp`); NULL if none. |
| `ReportDebcode` | STRING | Representative debtor code of the shop: `SegmentDebcode` if present, else `TADebcode`. |
| `DEBcreditTerm` | INT64 | Credit term in days. |
| `InvoiceProvinceSK` | INT64 | Province SK of `ReportDebcode`'s address (from `view_deb_address_data`, one row chosen per debtor: sub-district > district > province, then lowest SK). |
| `InvoiceDistrictSK` | INT64 | District SK from the same address row. |
| `InvoiceSubDistrictSK` | INT64 | Sub-district SK from the same address row. |
| `CustomerReportKey` | STRING | Natural key part: report name with all whitespace removed (`REGEXP_REPLACE(name, r'\s', '')`); used to join invoices to this table. |

# How it is built

- Definition: `definitions/dimension/dim_customer_report_info.sqlx` (`type: "operations"`, tags `dimension_daily`); the operation owns this table.
- Reads: `mds_dataset.mds_data_customer_report_master` (master data loaded outside this repo), [dimension_view.view_dim_invoice](/view/dimension_view/view_dim_invoice.md), [dimension_view.view_dim_customer](/view/dimension_view/view_dim_customer.md), `function_dataset.clean_company_prefix` (UDF), [dimension_table.dim_sale_representative_last](/dimension/dim_sale_representative_last.md), [dimension_table.dim_department_last](/dimension/dim_department_last.md), [validated_mac5.deb](/validated/validated_mac5/deb.md), [validated_mac5.tbook_quotation](/validated/validated_mac5/tbook_quotation.md), [dimension_table.dim_company](/dimension/dim_company.md), [process_dataset.view_deb_address_data](/view/process_dataset/view_deb_address_data.md), [dimension_table.dim_customer_segment](/dimension/dim_customer_segment.md).
- Refresh: MERGE with stable SK on `CompanyID` + `CustomerReportKey`, full source read (no MDS window), updates every non-key column, never deletes; reserved -1 row inserted outside the MERGE. `type: "operations"`, tag `dimension_daily`; target table pre-exists (clustered by `CustomerReportInfoSK`). Runs after `update_sk_sale_rep_group`, `dim_customer_segment`, `dim_aging`, `dim_order`, `dim_group_customer`, `mec` and `deb_address_data` because it reads views over them.
- Approximate size (BigQuery metadata, 2026-10-31): 41,746 rows, 8.9 MB.

# Examples

Segment and TA coverage per company.

```sql
SELECT CompanyID, SegmentSource, COUNT(*) AS names, COUNTIF(TASource IS NOT NULL) AS with_ta
FROM `databuffet-nonprd.dimension_table.dim_customer_report_info`
WHERE CustomerReportInfoSK <> -1
GROUP BY CompanyID, SegmentSource
ORDER BY CompanyID, SegmentSource;
```

Join pattern used by fact views: the report row for an invoice name.

```sql
SELECT r.CustomerReportInfoSK, r.CustomerSegmentSK, r.DepartmentSK, r.SaleRepSK
FROM `databuffet-nonprd.dimension_table.dim_customer_report_info` AS r
WHERE r.CompanyID = 'ag01'
  AND r.CustomerReportKey = REGEXP_REPLACE('Example Shop Name', r'\s', '');
```
