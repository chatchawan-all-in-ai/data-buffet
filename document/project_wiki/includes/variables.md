# `includes/controller/variables.json` — Tags & Dataset Names

> **LLM context**: The single registry of every BigQuery dataset name and Dataform tag.
> All keys are spread into the `databuffet` object, so `databuffet.TAG_DIM_DAILY`,
> `databuffet.DIMENSION_TABLE`, etc. work in any SQLX file.
> **Add new tags/datasets here — never inline string literals in SQLX.**

## Tags

| Constant | Value | Runs |
|---|---|---|
| `TAG_INITIAL` | `initial` | ⚠️ External-table setup and destructive validated drops; see [scope and manual execution](../initial/initial-layer.md#การผูก-dependency). Schema/UDF bootstrap actions are untagged |
| `TAG_REINITIAL` | `re-initial` | ⚠️ Drops validated/curated MAC5 tables; does not recreate external tables |
| `TAG_VALIDATED` | `validated` | All validated tables |
| `TAG_VALIDATED_FULL` | `validated_full` | Full-load reference tables |
| `TAG_VALIDATED_INCREMENTAL` | `validated_incremental` | Partitioned transactional tables |
| `TAG_CURATED` / `TAG_CURATED_FULL` / `TAG_CURATED_INCREMENTAL` | `curated`, `curated_full`, `curated_incremental` | Curated layer |
| `TAG_DIM_DAILY` / `TAG_DIM_MONTHLY` / `TAG_DIM_YEARLY` | `dimension_daily`, `dimension_monthly`, `dimension_yearly` | Dimension refresh cadence |
| `TAG_FACT_DAILY` / `TAG_FACT_MONTHLY` / `TAG_FACT_YEARLY` | `fact_daily`, `fact_monthly`, `fact_yearly` | Fact refresh cadence |
| `TAG_PROCESS` | `process` | Process layer (address parsing + `rls_customer360`) |
| `TAG_CDC` / `TAG_CDC_INCREMENTAL` | `cdc`, `cdc_incremental` | CDC pipeline |
| `TAG_PUB_SUB` | `pub_sub` | [Pub/Sub pilot objects](../cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24); no scheduler runs it — run by hand per the [pilot deployment steps](../cdc-process/process.md#deploy) |
| `TAG_VIEW` | `view` | View layer (`definitions/view/`) — presentation views over dim/fact/curated · [Deployment procedure](../../how-to/deploy-view.md) |

## Dataset (BigQuery schema) names

### Per-source raw → validated → curated

| Source | Raw | Validated | Curated |
|---|---|---|---|
| MAC5 | `raw_mac5_ag01`, `raw_mac5_aa05`, `raw_mac5_ab01`, `raw_mac5_ac02`, `raw_mac5_ak02` (one per company) | `validated_mac5` | `curated_mac5` |
| CIS360 | `raw_cis360` | `validated_cis360` | `curated_cis360` |
| MASTERSKU | `raw_mastersku` | `validated_mastersku` | `curated_mastersku` |
| MASTER_SKU (`master_sku` 3.0) | `raw_master_sku` (`RAW_MASTER_SKU`) | `validated_master_sku` (`VALIDATED_MASTER_SKU`) | `curated_master_sku` (`CURATED_MASTER_SKU`) |
| DERP | `raw_derp` (`RAW_DERP`) | `validated_derp` (`VALIDATED_DERP`) | — (no constant) |
| SALEOUT_MDT | `raw_saleout_mdt` | `validated_saleout_mdt` | **`curated_saleout_mdt`** (`CURATED_SALEOUT_MDT`, เพิ่ม 2026-09) |
| ALLKONS_COMMISSION | `raw_allkons_commission` | `validated_allkons_commission` ⚠️ **ไม่มีไฟล์ validated แล้ว** (pause ใน `74a10e0`) dataset ยังค้างข้อมูลเก่า | — |

### Shared datasets

| Constant | Value | Holds |
|---|---|---|
| `DIMENSION_TABLE` | `dimension_table` | Physical dimension tables |
| `DIMENSION_VIEW` | `dimension_view` | Dimension views (`definitions/view/dimension_view/`) |
| `FACT_TABLE` | `fact_table` | Physical fact tables |
| `FACT_VIEW` | `fact_view` | Fact views (`definitions/view/fact_view/`) |
| `ONETIME` | `onetime` | Data-mart / Power BI / model views + externally-loaded base tables |
| `BRIDGE` | `bridge_dataset` | Bridge views (many-to-many SK maps) — `definitions/view/bridge_dataset/` |
| `CDC_DATESET` (sic) | `cdc_dataset` | CDC change log |
| `PROCESS_DATASET` | `process_dataset` | Derived datasets (address parsing) + RLS/address views + Pub/Sub export config + memory (`mart_export_config`) and sent state (`mart_sent_state`) |
| `PUB_SUB` | `pub_sub` | Views read by the Pub/Sub publish workflow (`definitions/view/pub_sub/`), e.g. `export_dim_company` |
| `ORG_CENTER` | `org_center` | Org center tables `org_center_unit` / `org_center_member` / `org_center_person` (`definitions/org_center/`) — see [org-center.md](../org_center/org-center.md) |
| `FUNCTION_DATASET` | `function_dataset` | BigQuery UDFs (7 ตัว) |
| `MDS_DATASET` | `mds_dataset` | Master-data-service tables (externally loaded, **not** created by this repo) |

> Note the historical typo: the constant is `CDC_DATESET`, not `CDC_DATASET`. Keep using
> it as-is; renaming would touch every consumer.

### GCS folder names (`GCS_*`)

Map source system → folder under `gs://file-raw-data`:
`mac5_ag01`, `mac5_aa05`, `mac5_ab01`, `mac5_ac02`, `mac5_ak02`, `mac5_report`,
`mac5_gps`, `mastersku`, `master_sku` (`GCS_MASTER_SKU`), `cis360`, `saleout_mdt`,
`allkons_commission`, `derp_temp` (`GCS_DERP` — DERP; a temp-sounding name that may change).

## MAC5 multi-company note

MAC5 has **5 company instances** (ag01, aa05, ab01, ac02, ak02), each with its own raw
dataset and GCS folder. The validated layer consolidates them into the single
`validated_mac5` dataset with a `company_id` column.

## ขอบเขตของหน้านี้

หน้านี้อธิบายด้วย **ค่า**
(เช่น `raw_mac5_ag01`) ไม่ใช่ชื่อ constant ทุกตัว เพราะ key กลุ่ม `RAW_*` / `GCS_*` /
`VALIDATED_*` / `CURATED_*` เดาได้จากค่าตรง ๆ · ถ้าต้องการรายชื่อครบ ให้อ่านจาก
`includes/controller/variables.json` ตรง ๆ — **อย่าเชื่อหน้านี้เป็นรายการครบ**
