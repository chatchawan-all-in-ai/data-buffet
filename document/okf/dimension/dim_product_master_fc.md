---
type: BigQuery Table
title: "dim_product_master_fc"
description: "One row = one product/variant (by barcode) per company from the MDS finance product master, with MAC5 and D365 codes, variant attributes, dimensions and product hierarchy."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=dimension_table&t=dim_product_master_fc&page=table"
project_id: databuffet-nonprd
dataset_id: dimension_table
table_id: dim_product_master_fc
tags: ["dimension", "mds", "dimension_daily"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/dimension/dim_product_master_fc.sqlx"
    title: "Dataform definition (dimension/dim_product_master_fc.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/dimension/inventory.md"
    title: "Data Mart wiki (document/project_wiki/dimension/inventory.md)"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-10-31T00:17:08+07:00" }
status: draft
---

# What it is

Finance-owned product master that bridges old MAC5 product codes to new D365 codes and carries variant attributes (size, colour, style, config), weights, dimensions, units and the six-level TM product hierarchy. Nothing else in the repo reads it (no downstream consumer in `definitions/`); it is published for BI/finance use directly. Source: mds `mds_data_product_finance_master`.

# Grain and key

One row per (company, Barcode) among active mds rows (the SK ordering key; uniqueness is not enforced by the SQL). Key: `ProductMasterFcSK` (surrogate, unstable across days).

# Schema

| Column | Type | Description |
|---|---|---|
| `ProductMasterFcSK` | INT64 | `ProductMasterFcSK` is `ROW_NUMBER() OVER(ORDER BY companyID, Barcode)` over the active mds rows; it regenerates on every daily run. |
| `CompanySK` | INT64 | Company surrogate key from [dim_company](/dimension/dim_company.md), found by a LEFT JOIN on `companyID`; NULL when the mds company code has no match in dim_company. |
| `companyID` | STRING | Company code (e.g. `ag01`), passed through `cleanString` from the mds column `companyID`; natural join key to dim_company.companyID. |
| `ProductIDOldMac5` | STRING | Pass-through of mds `ProductIDOldMac5`, cleaned with `cleanString` (empty string becomes NULL). Product code in the old MAC5 system. |
| `ProductNameOldMac5` | STRING | Pass-through of mds `ProductNameOldMac5`, cleaned with `cleanString` (empty string becomes NULL). Product name in MAC5. |
| `ProductIDNewD365` | STRING | Pass-through of mds `ProductIDNewD365`, cleaned with `cleanString` (empty string becomes NULL). Product code in the new D365 ERP. |
| `ProductNameNewD365` | STRING | Pass-through of mds `ProductNameNewD365`, cleaned with `cleanString` (empty string becomes NULL). Product name in D365. |
| `SerchName` | STRING | Pass-through of mds `SerchName`, cleaned with `cleanString` (empty string becomes NULL). Search name (spelling `Serch` is from the source). |
| `Size` | STRING | Pass-through of mds `Size`, cleaned with `cleanString` (empty string becomes NULL). Variant size code. |
| `SizeDescription` | STRING | Pass-through of mds `SizeDescription`, cleaned with `cleanString` (empty string becomes NULL). Size description. |
| `Color` | STRING | Pass-through of mds `Color`, cleaned with `cleanString` (empty string becomes NULL). Variant colour code. |
| `ColorDescription` | STRING | Pass-through of mds `ColorDescription`, cleaned with `cleanString` (empty string becomes NULL). Colour description. |
| `Style` | STRING | Pass-through of mds `Style`, cleaned with `cleanString` (empty string becomes NULL). Variant style code. |
| `StyleDescription` | STRING | Pass-through of mds `StyleDescription`, cleaned with `cleanString` (empty string becomes NULL). Style description. |
| `Config` | STRING | Pass-through of mds `Config`, cleaned with `cleanString` (empty string becomes NULL). Variant configuration code. |
| `ConfigDescription` | STRING | Pass-through of mds `ConfigDescription`, cleaned with `cleanString` (empty string becomes NULL). Configuration description. |
| `ProductNumber` | STRING | Pass-through of mds `ProductNumber`, cleaned with `cleanString` (empty string becomes NULL). D365 product number (base item before variants). |
| `ProductDescription` | STRING | Pass-through of mds `ProductDescription`, cleaned with `cleanString` (empty string becomes NULL). Product description. |
| `Unit` | STRING | Pass-through of mds `Unit`, cleaned with `cleanString` (empty string becomes NULL). Base unit of measure. |
| `NetWeight` | STRING | Pass-through of mds `NetWeight`, cleaned with `cleanString` (empty string becomes NULL). Net weight of the product as text, usually a number such as `4.2`, sometimes the placeholder `โปรดระบุ` (please specify). |
| `GrossWeight` | STRING | Pass-through of mds `GrossWeight`, cleaned with `cleanString` (empty string becomes NULL). Gross weight of the product as text, usually a number such as `19`, sometimes the placeholder `โปรดระบุ` (please specify). |
| `DeepMM` | STRING | Pass-through of mds `DeepMM`, cleaned with `cleanString` (empty string becomes NULL). Depth in millimetres (STRING). |
| `WideMM` | STRING | Pass-through of mds `WideMM`, cleaned with `cleanString` (empty string becomes NULL). Width in millimetres (STRING). |
| `HeightMM` | STRING | Pass-through of mds `HeightMM`, cleaned with `cleanString` (empty string becomes NULL). Height in millimetres (STRING). |
| `DoNotStackOverLayer` | INT64 | `castInt64` of mds `DoNotStackOverLayer`: maximum number of layers the product may be stacked (values 1 to 10). |
| `Barcode` | STRING | Pass-through of mds `Barcode`, cleaned with `cleanString` (empty string becomes NULL). Product barcode; the row-order key (with companyID) for the SK. |
| `ItemGroup` | STRING | Pass-through of mds `ItemGroup`, cleaned with `cleanString` (empty string becomes NULL). Item group code. |
| `ItemGroupName` | STRING | Pass-through of mds `ItemGroupName`, cleaned with `cleanString` (empty string becomes NULL). Item group name. |
| `TM1Category` | STRING | Pass-through of mds `TM1Category`, cleaned with `cleanString` (empty string becomes NULL). Product hierarchy level 1: category. |
| `TM2Brand` | STRING | Pass-through of mds `TM2Brand`, cleaned with `cleanString` (empty string becomes NULL). Hierarchy level 2: brand. |
| `TM3Series` | STRING | Pass-through of mds `TM3Series`, cleaned with `cleanString` (empty string becomes NULL). Level 3: series. |
| `TM4FactorySection` | STRING | Pass-through of mds `TM4FactorySection`, cleaned with `cleanString` (empty string becomes NULL). Level 4: factory section. |
| `TM5Material` | STRING | Pass-through of mds `TM5Material`, cleaned with `cleanString` (empty string becomes NULL). Level 5: material. |
| `TM6PackageShape` | STRING | Pass-through of mds `TM6PackageShape`, cleaned with `cleanString` (empty string becomes NULL). Level 6: package shape. |
| `Remark` | STRING | Pass-through of mds `Remark`, cleaned with `cleanString` (empty string becomes NULL). Free-text remark. |
| `PurchaseUnit` | STRING | Pass-through of mds `PurchaseUnit`, cleaned with `cleanString` (empty string becomes NULL). Purchasing unit. |
| `UnitConversions` | STRING | Pass-through of mds `UnitConversions`, cleaned with `cleanString` (empty string becomes NULL). Unit conversion factor text. |
| `ToUnit` | STRING | Pass-through of mds `ToUnit`, cleaned with `cleanString` (empty string becomes NULL). Target unit of the conversion. |
| `SalesUnit` | STRING | Pass-through of mds `SalesUnit`, cleaned with `cleanString` (empty string becomes NULL). Sales unit. |
| `PackSize` | STRING | Pass-through of mds `PackSize`, cleaned with `cleanString` (empty string becomes NULL). Pack size text. |
| `MdsID` | STRING | Row id of the source record in the mds master table (`id`, cleaned with `cleanString`); trace column back to MDS. |

# How it is built

- Definition: `definitions/dimension/dim_product_master_fc.sqlx` (`type: "table"`, tags `dimension_daily`).
- `uniqueKey`: `ProductMasterFcSK`.
- Storage options: `{"clusterBy": ["ProductMasterFcSK"]}`.
- Reads: `mds_dataset.mds_data_product_finance_master` (master data loaded outside this repo), [dimension_table.dim_company](/dimension/dim_company.md).
- Full daily rebuild (`type: "table"`, tag `dimension_daily`) from active mds rows (`is_active = TRUE`); runs after dim_company (declared dependency).

# Examples

Map old MAC5 product codes to new D365 codes.

```sql
SELECT companyID, ProductIDOldMac5, ProductIDNewD365, ProductNameNewD365, Barcode
FROM `databuffet-nonprd.dimension_table.dim_product_master_fc`
WHERE ProductIDOldMac5 IS NOT NULL AND ProductIDNewD365 IS NOT NULL;
```

Duplicate (company, barcode) keys.

```sql
SELECT companyID, Barcode, COUNT(*) AS n
FROM `databuffet-nonprd.dimension_table.dim_product_master_fc`
GROUP BY 1, 2
HAVING n > 1;
```
