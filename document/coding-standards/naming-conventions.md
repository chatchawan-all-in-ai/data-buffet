# Naming Conventions

สรุปกติกาตั้งชื่อทั้งโปรเจกต์ (สแกนจากโค้ดจริง 2026-07-10)

## ไฟล์ / Action

| ประเภท | Pattern | ตัวอย่าง |
|---|---|---|
| Validated | `<ชื่อตาราง raw>.sqlx` (ชื่อไฟล์ = ชื่อตาราง ผ่าน `name()`) | `mih.sqlx`, `customer_profile.sqlx` |
| Schema bootstrap | `validated_schema_<source>.sqlx`, `curated_schema_<source>.sqlx` | |
| Initial | `create_all_table_raw_<source>[_<company>].sqlx`, `drop_all_tables_<layer>_<source>.sqlx` | |
| Curated | `curated_<ชื่อ>.sqlx` | `curated_mih.sqlx` |
| Dimension | `dim_<entity>.sqlx` snake_case; snapshot ปัจจุบันต่อท้าย `_last`; aggregate ต่อ suffix ตามเรื่อง | `dim_sale_representative_last.sqlx` |
| ตัวช่วย imperative | prefix `update_sk_` | `update_sk_sale_rep_group.sqlx` |
| Fact | `fact_<entity>.sqlx` | `fact_invoice.sqlx` (ระวัง `fact_transcation` สะกดตามนี้จริง) |

## Dataset (BigQuery schema)

`raw_<source>[_<company>]` → `validated_<source>` → `curated_<source>` +
dataset กลางตาม [registry reference](../project_wiki/includes/variables.md#shared-datasets)
— ทั้งหมดอ้างผ่านคีย์ใน `variables.json`

## คอลัมน์

| ที่ | Convention | ตัวอย่าง |
|---|---|---|
| validated (mac5) | ชื่อ raw ตัวพิมพ์เล็ก | `MIHvnos` → `mihvnos` |
| validated (master_sku) | ชื่อ raw คงเดิม (snake_case) ไม่เติม prefix | `brand_id`, `language_id`, `created_at` |
| validated (mastersku) | prefix `prd_*` snake_case | `prd_id` |
| curated | camelCase | `mihVnos`, `prdSku` |
| dimension/fact | PascalCase | `CompanyID`, `WaterPacName` |
| org_center | snake_case, ชื่อเอกพจน์เสมอ แม้เป็นคอลัมน์ list (ARRAY) — ไม่ใช้ `_ids` / `_codes` | `company_id`, `department_id`, `section_code` |
| Surrogate key | Keep the dimension’s established `<Entity>SK` name in PascalCase; fact row keys normally use `Fact<Entity>SK` (retain legacy `FactOrderSk`, `BillingSK` and `ReceiveSK`) | `CompanySK`, `SaleRepSK`, `FactQuotationSK` |
| mds row id ใน dim | `MdsID` สำหรับคอลัมน์ใหม่; คอลัมน์เดิมคงตัวพิมพ์ตาม schema ใน [table card](../okf/README.md) ของตารางนั้น | |
| คอลัมน์ก่อนปรับเครื่องหมาย | `<ชื่อ>_raw` | `mihnetsum_raw` |
| วันที่ snapshot | `asatdate` (DATE) | |
| วันที่ business ใน fact | `mix_date` | |
| multi-company | `company_id` (validated) / `CompanyID` + `CompanySK` (dim) | |

หมายเหตุ: SK ไม่จำเป็นต้องแปลตรงจากชื่อตาราง — `dim_collection_status → CollectSK`,
`dim_status_not_receive → NotReceiveSK`, `dim_avg_collection_score → AvgCollectSK`,
`dim_product_master → ProductSK`

The 11 facts with row-level SKs keep their existing column names and use a typed
business-key STRUCT plus an occurrence number for stable key values; see the
[fact row-key standard](sqlx-coding-standard.md#fact-row-surrogate-keys).

For dimension key selection and allocation, follow the
[stable-key synchronization contract](../project_wiki/dimension/merge-sk-pattern.md);
conversion scope and exceptions are owned by the [inventory](../project_wiki/dimension/inventory.md).

## ตัวแปร JavaScript ใน js block

| ตัวแปร | ใช้กับ |
|---|---|
| `<Name>Table` / `<Name>TableRef` | object + FQN string ของทุกตารางที่อ้างตรง |
| `MdsSourceTable` / `MdsSourceTableRef` | ตารางต้นทาง mds |
| `sourceTable` / `sourceTableRef` | ต้นทาง raw ใน validated |
| `pk_key` | array PK ใน validated (ต้องตรงกับ `uniqueKey`) |
| `doc_key` | array คีย์ระดับเอกสารสำหรับ DELETE ราย document (`mih`/`mil`/`mir`) |
| `temp_table` | ชื่อ TEMP table ของ batch — `new_data_<table>` (`mih`/`mil`/`mir`) |
| `partition_statement`, `post_operations_statement` | statement ที่ generate |

## Alias ใน SQL

| Alias | ความหมาย |
|---|---|
| `t1` | ตารางต้นทาง |
| `t2` | self-join ด้วย natural key |
| `t3` | self-join ด้วย `MdsID` |
| `dim_com` | lookup `dim_company` |
| `T` / `S` | MERGE target / source |

## Tags

รูปแบบ `<layer>_<cadence|mode>`: `validated_incremental`, `validated_full`,
`dimension_daily`, `dimension_yearly`, `fact_daily`, `cdc_incremental`, `process`,
`initial`, `re-initial` — นิยามใน `variables.json` เท่านั้น

## ตาราง mds

`mds_data_<entity>_master` — มี `id`, `is_active`, `updated_at` ทุกตาราง


## Named exceptions retained for compatibility

### File / action names

Keep `curated/master_sku/product_for_aisearch_v3.sqlx`, `curated/mastersku/product_for_aisearch.sqlx`, `curated/saleout_mdt/curated_schema_saleout.sqlx`, and `validated/saleout_mdt/validated_schema_saleout.sqlx`; renaming changes the Dataform action name and its consumers.

### Public columns

#### Recent outputs

Keep these established public names until their consumers can be migrated.

- `curated/derp/curated_invoice_line_cost.sqlx`: `company_id`
- `curated/derp/curated_journal_invoice.sqlx`: `company_id`
- `fact/fact_saleout_mdt.sqlx`: `sale_date`, `store_code`, `branch_sk`, `zone_sk`, `product_mdt_sk`, `product_sk`, `product_mkt_sk`, `report_sk`, `region_sk`, `region_manager_sk`, `director_sk`, `doc_type`, `doc_type_source`, `sale_qty`, `sale_amount`, `days_covered`, `date_is_estimated`, `branch_code`, `product_code`
- `fact/fact_saleout_monthly_mdt.sqlx`: `store_code`, `branch_code`, `month_date`, `sales_channel`, `product_code`, `product_name`, `branch_sk`, `zone_sk`, `product_mdt_sk`, `product_sk`, `product_mkt_sk`, `report_sk`, `region_sk`, `region_manager_sk`, `director_sk`, `sale_qty`, `sale_amount`
- `fact/fact_target_saleout_mdt.sqlx`: `target_date`, `store_code`, `branch_sk`, `zone_sk`, `product_mkt_sk`, `region_sk`, `region_manager_sk`, `director_sk`, `marketing_group_id`, `marketing_group_name`, `sub_marketing_id`, `sub_marketing_name`, `segment_id`, `segment_name`, `target_amt`, `target_qty`, `target_year`, `target_month`, `days_in_month`, `branch_code`, `mds_id`
- `fact/fact_target_series_mdt.sqlx`: `target_date`, `store_code`, `branch_sk`, `zone_sk`, `series_sk`, `region_sk`, `region_manager_sk`, `director_sk`, `series_code`, `series_name`, `target_amt`, `target_qty`, `target_year`, `target_month`, `days_in_month`, `branch_code`, `mds_id`
- `fact/fact_transcation.sqlx`: `companyID`, `milDay`, `milMonth`, `milYear`, `milType`, `milVnos`, `milStk`, `memoextract`, `milDep`, `milCus`, `milPer`, `milListno`, `milJob`, `milSum`, `milDesc`, `mihdesc`

#### Legacy outputs

Keep these long-lived public names for downstream, report, and source compatibility; rename only with a consumer migration.

- `curated/mac5/curated_mih.sqlx`: `company_id`, `mihstatus_desc`
- `curated/mac5/curated_mil.sqlx`: `company_id`, `percent_sale`
- `curated/mac5/curated_tbook_quotation.sqlx`: `company_id`, `ID`, `Running`, `Atten`, `Address`, `SDate`, `Project`, `TelePhone`, `Sale`, `PriceValidity`, `TermDelivery`, `TermPayment`, `UInsert`, `DInsert`, `UUpdate`, `Dupdate`, `Agent1`, `Agent2`, `Period`, `Position`, `Vat`, `Disc`, `ExtraSum`, `ExtraDesc`, `DateStart1`, `DateEnd1`, `DateStart2`, `DateEnd2`, `CashStatus`, `Note`, `NoteForApp`, `MemoForApp`, `Rev`, `TypeCus`, `Channel`, `Channel2`, `TypePrice`, `FOB`, `Cancel`, `AppType`, `TypeDeb`, `SaleDep`, `TypeProject`, `SelectStatus`, `ConpoStatus`, `Lat`, `Long`, `MapNote`, `FileUpload`, `City`, `RdoSend`, `CustomerName`, `CustomerTelePhone`, `CustomerAddress`, `CheckNote`, `TextNote`, `StatusSpread`, `ChkBox`, `FobStt`, `QuotationRef`, `CustomerId`, `CustomerGroup`, `QuotationId`, `EStatus`, `Area`, `District`, `PostCode`, `QtStepPrice`, `ExtraDis`
- `curated/saleout_mdt/curated_eom_bt.sqlx`: `month_date`, `branch_code`, `product_code`, `product_name`, `sale_qty`, `sale_amount`, `store_code`
- `curated/saleout_mdt/curated_eom_gb.sqlx`: `month_date`, `branch_code`, `branch_name`, `product_code`, `product_name`, `doc_type`, `sale_qty`, `sale_amount`, `store_code`
- `curated/saleout_mdt/curated_eom_hp.sqlx`: `month_date`, `store_code`, `branch_code`, `branch_name`, `product_code`, `product_name`, `sale_qty`, `sale_amount`
- `curated/saleout_mdt/curated_eom_tw.sqlx`: `month_date`, `branch_code`, `product_code`, `product_name`, `barcode_match`, `sale_qty`, `sale_amount`, `store_code`
- `curated/saleout_mdt/curated_saleout_mdt.sqlx`: `branch_code`, `branch_name`, `product_code`, `product_name`, `barcode_match`, `sale_qty`, `sale_amount`, `doc_type`, `doc_type_source`, `days_covered`, `date_is_estimated`, `sale_date`, `store_code`
- `curated/saleout_mdt/curated_saleout_monthly_mdt.sqlx`: `month_date`, `store_code`, `product_code`, `branch_code`, `branch_name`, `product_name`, `sale_qty`, `sale_amount`, `source_type`, `sales_channel`
- `curated/saleout_mdt/curated_stock_mdt.sqlx`: `stock_date`, `store_code`, `branch_code`, `product_code`, `product_name`, `onhand_qty`, `onhand_amt`, `onorder_qty`
- `fact/fact_stock_mdt.sqlx`: `stock_date`, `store_code`, `branch_sk`, `zone_sk`, `product_mdt_sk`, `product_sk`, `product_mkt_sk`, `onhand_qty`, `onhand_amt`, `onorder_qty`, `branch_code`, `product_code`
- `fact/fact_stock_mdt_monthly.sqlx`: `store_code`, `snapshot_date`, `onhand_qty`, `month_end`, `is_month_end`, `branch_sk`, `zone_sk`, `product_mdt_sk`, `product_sk`, `product_mkt_sk`, `onhand_amt`, `onorder_qty`, `branch_code`, `product_code`
