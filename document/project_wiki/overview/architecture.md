# Architecture Overview

> **LLM context**: Read this first. Data-Buffet is a BigQuery warehouse on Dataform 3.0.0
> (project `databuffet-nonprd`, region `us-central1`). Medallion layers
> (raw → validated → curated) feed a star schema (dimension + fact), with CDC and an
> AI-address-parsing process pipeline on the side.

## Data flow

```
GCS files  gs://file-raw-data  (AVRO, Hive-partitioned by ASATDATE=YYYYMMDD; 1 CSV table)
      │
      ▼
INITIAL      definitions/initial/     External tables + UDFs + drop files (⚠️ tag `initial` drops validated)
      │
      ▼
VALIDATED    definitions/validated/   Clean, cast, dedup — 1 file per source table
      │                               sources: mac5 · cis360 · mastersku · master_sku · saleout_mdt · derp
      ▼
CURATED      definitions/curated/     Business joins, JSON parsing, split-sale
      │
      ├────────────────────────────┐
      ▼                            ▼
DIMENSION    definitions/dimension/ FACT    definitions/fact/
(SK dims)                    ◄──── (star-schema joins)
      │                            │
      └──────────────┬─────────────┘
                     ▼
VIEW         definitions/view/      Presentation views (type: "view") for Power BI /
                                    data marts / RLS. schema stays dimension_view,
                                    fact_view, onetime, process_dataset,
                                    bridge_dataset, pub_sub (folder ≠ target dataset)

Side pipelines:
  CDC      definitions/cdc/       change log driven by cdc-config.json
  PROCESS  definitions/process/   AI Thai-address parsing, gated on CDC + RLS access maps (see process reference below) + Pub/Sub export pilot
```

File counts per layer are generated from the code — see the
[generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview). Per-source
validated lists: [validated/source-inventory.md](../validated/source-inventory.md).
Per-source context (what each system is, who reads it):
[overview/source-systems.md](source-systems.md).

## Layer contracts

| Layer | Dataset(s) | Materialization | Detail page |
|---|---|---|---|
| Initial | `raw_*`, `function_dataset` | operations (external tables, UDFs) | [initial/initial-layer.md](../initial/initial-layer.md) |
| Validated | `validated_*` | incremental / table + QUALIFY dedup | [validated/validated-layer.md](../validated/validated-layer.md) |
| Curated | `curated_*` | incremental / table / operations | [curated/curated-layer.md](../curated/curated-layer.md) |
| Dimension | `dimension_table`, `dimension_view` | operations / table; scope and exceptions in the [inventory](../dimension/inventory.md) | [dimension/dimension-layer.md](../dimension/dimension-layer.md) |
| Fact | `fact_table`, `fact_view` | table rebuild / operations upsert | [fact/fact-layer.md](../fact/fact-layer.md) |
| CDC | `cdc_dataset` | operations (config-generated) | [cdc-process/cdc.md](../cdc-process/cdc.md) |
| Process | `process_dataset` | incremental (`deb_address_data`, AI.GENERATE) + table (RLS access maps; see detail page) + Pub/Sub export pilot (operations, tag `pub_sub`) | [cdc-process/process.md](../cdc-process/process.md) |
| View | `dimension_view`, `fact_view`, `onetime`, `process_dataset`, `bridge_dataset`, `pub_sub` | `type: "view"` (presentation; folder ≠ target dataset) | [view/view-layer.md](../view/view-layer.md) |
| Pub/Sub | `pub_sub` | operations (`pub_sub_schema` creates the dataset); future shaping tables before Pub/Sub | [cdc-process/process.md](../cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) |
| Org center | `org_center` | table rebuild (`dimension_daily`, after `update_sk_sale_rep_group`) + operations (`org_center_schema` creates the dataset) | [org_center/org-center.md](../org_center/org-center.md) |

## External inputs NOT managed by this repo

- **`mds_dataset`** — master-data-service tables (`mds_data_*_master`). Loaded by an
  external process. Every table has `id`, `is_active`, `updated_at`. Source of most
  dimensions.
- **Externally loaded base tables** in `onetime`, `dimension_table` and
  `process_dataset` — the authoritative list and consumers are in
  [known-issues — BigQuery objects not built by the repo](../../operations/known-issues.md).
  Keep every object in the required-input group; Dataform cannot recreate it.
- **`dim_company` exists in `dimension_table`** and has a `dim_company.sqlx`, but note
  the repo README's caveat about dependencies — most dims list `dim_company` in
  `dependencies` and it is the DAG root.
- **View layer now defined** (2026-07-24): views under `definitions/view/`
  (e.g. `onetime.Transaction_Data_Mart`, `view_dim_aging`, `view_deb_address_data`) are Dataform-managed as of the view
  migration. See [view/view-layer.md](../view/view-layer.md); current counts are in the
  [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview).

## Critical global conventions

1. **Timezone**: always `Asia/Bangkok` (`CURRENT_DATE('Asia/Bangkok')`).
2. **NULL policy**: empty string → NULL via `cleanString` everywhere — except string
   columns in an incremental `uniqueKey`, which use `IFNULL(cleanString(...), '')`
   (MERGE can't match NULL; see `validated/validated-layer.md`, `mie.miecus`).
3. **Config through `databuffet.*`** — no hardcoded dataset names/tags. The last
   holdout (`"mds_dataset"` as a literal in 36 dim files) was converted to
   `databuffet.MDS_DATASET` on 2026-08-26; there are now **zero** literals.
4. **`type: "operations"` tables are not created by Dataform** — they must pre-exist
   in BigQuery. The common stable-key sync uses operation actions; two dimensions keep
   distinct source behavior and 13 files were unchanged. See
   [dimension/dimension-layer.md](../dimension/dimension-layer.md).
5. **Load-bearing typos** — keep verbatim: `fact_transcation` (table + file),
   `CDC_DATESET` (variables.json key), `prdDiminsionData` (JSON field).
6. **No Dataform assertions exist** — quality is enforced via casting, QUALIFY dedup,
   and NOT ENFORCED primary keys.

## Environment

- `workflow_settings.yaml` (environment-specific, tracked): defaultProject
  `databuffet-nonprd`, vars `RAW_BUCKET`, `MDS_BACKFILL_DAYS` (currently 1),
  `BACKFILL_DAYS` (currently 1 — validated/curated incremental look-back).
- Branches: `dev` (working) → `nonprod` → `prod`; also `hotfix`. The schedule compiles
  `nonprod` at 05:45 and runs at 06:00 / 08:55:
  [operations/running-and-troubleshooting.md § Schedule](../operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd).
  How work reaches `nonprod` (two lanes):
  [release flow](../../getting-started/onboarding.md#release-flow).
- Local validation and execution setup: [run/debug guide](../../how-to/run-and-debug.md).
