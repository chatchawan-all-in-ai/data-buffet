---
type: BigQuery Table
title: "rls_ta_sale"
description: "One row = one viewer (employee) x one company x one seller scope (director, region, section, seller or ALL) x one product scope that the viewer may see today; sales lines are matched by the seller's org, expanded from org center seats and special-access exceptions."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=process_dataset&t=rls_ta_sale&page=table"
project_id: databuffet-nonprd
dataset_id: process_dataset
table_id: rls_ta_sale
tags: ["process", "RLS", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/process/rls_ta_sale.sqlx"
    title: "Dataform definition (process/rls_ta_sale.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/cdc-process/process.md"
    title: "Data Mart wiki (document/project_wiki/cdc-process/process.md)"
generated: { by: "agent:claude-code/claude-opus-5-5", at: "2026-11-02T00:00:00+07:00" }
status: draft
---

# What it is

Precomputed "who sees which sales" table for the TA AI Assistant. Sales are counted by seller: a sales line belongs to the seller on the line and to that seller's section, region and division. Sales lines of [view_fact_transcation](/view/fact_view/view_fact_transcation.md) are filtered with the rule under Examples on the viewer's `employee_id`. It is built from [org_center_unit](/org_center/org_center_unit.md), [org_center_member](/org_center/org_center_member.md) and [org_center_exception](/org_center/org_center_exception.md). It is separate from [rls_ta_customer](/process/rls_ta_customer.md) (visibility by customer portfolio).

# Grain and key

One row per `employee_id` + `company_id` + `director_id` + `region_id` + `section_id` + `sale_employee_id` + `marketing_group_id` + `sub_marketing_id` + `segment_id`, as of today (Asia/Bangkok). `'ALL'` in a level or product column means no restriction on that column. `company_id` is never `'ALL'`: a grant for every company is one row per company. No column is NULL.

# Schema

| Column | Type | Description |
|---|---|---|
| `employee_id` | STRING | The viewer: MDS employee code. |
| `company_id` | STRING | Company of the sales lines (`dim_company.CompanyID`, e.g. `ag01`, `ab01`). |
| `director_id` | STRING | `ALL` or a division code (`dim_director_last.DirectorID`, e.g. `00001`). |
| `region_id` | STRING | `ALL` or a sub-region code (`dim_region_last.SubRegionID`, e.g. `NE`, `PS1-4`). |
| `section_id` | STRING | `ALL` or a section code (`dim_section_last.SectionID`, e.g. `E1`). |
| `sale_employee_id` | STRING | `ALL` or the seller's employee code (`view_dim_sale_representative_last.EmployeeID`). |
| `marketing_group_id` | STRING | `ALL` or a marketing group code (non-`ALL` only on special-access product rows). |
| `sub_marketing_id` | STRING | `ALL` or a marketing sub-group code. |
| `segment_id` | STRING | `ALL` or a segment code. |
| `access_source` | STRING | Where the access comes from: `TA` (own sales), `SECTION_MGR`, `REGION_MGR`, `DIRECTOR` (every sale in the viewer's unit) or `EXCEPTION` (special access). When several give the same row the first in this order is kept. |

# How it is built

- Definition: `definitions/process/rls_ta_sale.sqlx` (`type: "table"`, tag `dimension_daily`).
- `uniqueKey`: the nine key columns listed under Grain and key.
- Storage options: `{"clusterBy": ["employee_id", "company_id"]}`.
- Reads: [org_center.org_center_unit](/org_center/org_center_unit.md), [org_center.org_center_member](/org_center/org_center_member.md), [org_center.org_center_exception](/org_center/org_center_exception.md), [dimension_view.view_dim_company](/view/dimension_view/view_dim_company.md) (over [dimension_table.dim_company](/dimension/dim_company.md)).
- Only rows valid today are used: units and members `BETWEEN valid_from AND valid_to`.
- Seats (`org_center_member`): find the seat company’s `CompanyReportID` in `view_dim_company`, then emit one row for every physical `CompanyID` with that reporting company (`ag01` and `ab01` seats both grant `ag01` and `ab01`). Every other level and product column is `ALL`:
  - `TA` (the department level): `sale_employee_id` = the TA's own `employee_id`.
  - `SECTION_MGR`: `section_id` = the section's `unit_code`.
  - `REGION_MGR`: `region_id` = the region's `unit_code` (SubRegionID).
  - `DIRECTOR`: `director_id` = the division's `unit_code`.
  - Manager seats need their unit to be valid today.
- Exceptions (`org_center_exception`, rows without `employee_id` skipped): `company_code` is a report company and becomes every `CompanyID` whose `view_dim_company.CompanyReportID` or `CompanyID` equals it case-insensitively (`ag01` gives `ag01` and `ab01`; `ALL` gives every company). One row per division x region x section code of the exception (`ALL` stays `ALL`); a region code becomes every sub-region `unit_code` of that company whose `region_code` or `unit_code` equals it (`PS1` gives `PS1-1` to `PS1-5`) and is kept as is when no unit matches. `sale_employee_id` is `ALL`; product columns come from the exception row. Any case variant of `all` in company, division, region, section or the three product fields is normalized to `ALL` at this grant boundary; real codes retain their stored case. Company-wide access is available only through exceptions.
- Full nightly rebuild; runs after the three `org_center_*` tables and `dim_company`.

# Examples

A sales line passes for a viewer when at least one row of that viewer matches it on every column. The line's codes come from these joins: company = `CompanySK` → `dim_company.CompanyID`; seller = `SaleRepSKLast` → `view_dim_sale_representative_last.EmployeeID`; section = `ChangeSectionSKLast` → `dim_section_last.SectionID`; region = that section's `RegionSK` → `dim_region_last.SubRegionID`; division = that section's `DirectorSK` → `dim_director_last.DirectorID`; product = `NewProductMktSK` → `view_dim_product_mkt` (`MarketingGroupID`, `SubMarketingID`, `SegmentID`). A column equal to `ALL` matches any line value, including NULL; any other value must equal the line's code. Use `EXISTS` so overlapping rows do not duplicate sales lines.

```sql
DECLARE viewer STRING DEFAULT '<viewer employee code>';

SELECT COUNT(*) AS sales_lines, ROUND(SUM(m.milSum), 2) AS net_sales
FROM `databuffet-nonprd.fact_view.view_fact_transcation` AS m
JOIN `databuffet-nonprd.dimension_table.dim_company` AS c
  ON c.CompanySK = m.CompanySK
LEFT JOIN `databuffet-nonprd.dimension_view.view_dim_sale_representative_last` AS s
  ON s.SaleRepSK = m.SaleRepSKLast
LEFT JOIN `databuffet-nonprd.dimension_table.dim_section_last` AS sec
  ON sec.SectionSK = m.ChangeSectionSKLast
LEFT JOIN `databuffet-nonprd.dimension_table.dim_region_last` AS reg
  ON reg.RegionSK = sec.RegionSK
LEFT JOIN `databuffet-nonprd.dimension_table.dim_director_last` AS dir
  ON dir.DirectorSK = sec.DirectorSK
LEFT JOIN `databuffet-nonprd.dimension_view.view_dim_product_mkt` AS p
  ON p.ProductMktSK = m.NewProductMktSK
WHERE m.mix_date BETWEEN '2026-10-01' AND '2026-10-22'
  AND UPPER(IFNULL(m.FlagSaleExc, '')) <> 'YES'
  AND EXISTS (
    SELECT 1
    FROM `databuffet-nonprd.process_dataset.rls_ta_sale` AS r
    WHERE r.employee_id = viewer
      AND r.company_id = c.CompanyID
      AND (r.director_id = 'ALL' OR r.director_id = dir.DirectorID)
      AND (r.region_id = 'ALL' OR r.region_id = reg.SubRegionID)
      AND (r.section_id = 'ALL' OR r.section_id = sec.SectionID)
      AND (r.sale_employee_id = 'ALL' OR r.sale_employee_id = s.EmployeeID)
      AND (r.marketing_group_id = 'ALL' OR r.marketing_group_id = p.MarketingGroupID)
      AND (r.sub_marketing_id = 'ALL' OR r.sub_marketing_id = p.SubMarketingID)
      AND (r.segment_id = 'ALL' OR r.segment_id = p.SegmentID)
  );
```

Rows of one viewer by source.

```sql
SELECT access_source, COUNT(*) AS rows_granted
FROM `databuffet-nonprd.process_dataset.rls_ta_sale`
WHERE employee_id = '<viewer employee code>'
GROUP BY access_source
```
