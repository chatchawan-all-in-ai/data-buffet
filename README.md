# Data-Buffet

A BigQuery data warehouse built on **Dataform**, transforming raw enterprise data into
analytics-ready facts and dimensions. It implements a medallion architecture
(**raw → validated → curated**) feeding a **star schema** (**dimension + fact**),
with built-in Change Data Capture (CDC) and an AI address-processing pipeline.

| | |
|---|---|
| **Platform** | Google Cloud BigQuery (`databuffet-nonprd`) |
| **Framework** | Dataform `3.0.0` |
| **Location** | `us-central1` |
| **Language** | SQLX (SQL + JavaScript) |
| **Raw Data** | `gs://file-raw-data` (AVRO, Hive-partitioned by `ASATDATE`; one CSV table, `saleout_lastyear`) |
| **Sources** | MAC5 (×5 companies), MASTERSKU, MASTER_SKU (`master_sku` 3.0), CIS360, SALEOUT_MDT, DERP, ALLKONS_COMMISSION + external `mds_dataset` |
| **Docs** | [`document/`](document/README.md) — developer guides (TH) + [LLM wiki (EN)](document/project_wiki/README.md) |
| **New here?** | [`document/getting-started/onboarding.md`](document/getting-started/onboarding.md) — access to request, tooling, then `bash .claude/skills/verify-setup/scripts/verify.sh` |

---

## Architecture

```
GCS AVRO/CSV files (gs://file-raw-data)
        │
        ▼
┌─────────────────┐   definitions/initial/
│ INITIAL         │   External tables over GCS + schema/UDF bootstrap
└─────────────────┘
        │
        ▼
┌─────────────────┐   definitions/validated/
│ VALIDATED       │   Type casting, NULL/empty handling, dedup, schema enforcement
└─────────────────┘
        │
        ▼
┌─────────────────┐   definitions/curated/
│ CURATED         │   Business logic, joins, JSON/text enrichment, split-sale
└─────────────────┘
        │
        ├──────────────────────────────┐
        ▼                              ▼
┌─────────────────┐            ┌─────────────────┐
│ DIMENSION       │            │ FACT            │
│ (SK + SCD)      │◄───────────│ (fact tables)   │
└─────────────────┘            └─────────────────┘
   definitions/dimension/         definitions/fact/
        ▲          │                    │
        │          └────────┬───────────┘
        │                   ▼
        │          ┌─────────────────┐   definitions/view/
        │          │ VIEW            │   BI/reporting layer (type: "view")
        │          └─────────────────┘   reads dim/fact/curated + other views
        │  mds_dataset (external master-data-service tables — not built by this repo)

Supporting pipelines:
  • CDC      definitions/cdc/        Change tracking driven by includes/controller/cdc-config.json
  • PROCESS  definitions/process/    AI Thai-address parsing (AI.GENERATE, gated on CDC) + RLS access maps + Pub/Sub export pilot
```

### Layers

File counts per layer are generated from the code: see the
[generated lineage](document/diagrams/pipeline_lineage.md#1-layer-overview).
Counts there are **SQLX files**, including the `*_schema_*.sqlx` bootstrap files;
JavaScript-generated actions are outside that diagram's scope.

| Layer | Path | Purpose |
|-------|------|---------|
| **Initial** | `definitions/initial/` | Create raw external tables over GCS; bootstrap schemas & UDFs; drop files for (re-)initialising validated |
| **Validated** | `definitions/validated/` | Clean, cast, dedup; one table per source object, plus one `validated_schema_<source>` bootstrap per source |
| **Curated** | `definitions/curated/` | Business-ready joins, enrichment, JSON parsing, plus one `curated_schema_<source>` bootstrap per source |
| **Dimension** | `definitions/dimension/` | Conformed dimensions; synchronization patterns and exceptions are listed in the [inventory](document/project_wiki/dimension/inventory.md) |
| **Fact** | `definitions/fact/` | Star-schema fact tables joined to dimensions (4-year retention) |
| **View** | `definitions/view/` | BI/reporting views (`type: "view"`) over dim/fact/curated: `dimension_view`, `fact_view`, `bridge_dataset`, `onetime`, `process_dataset`, `pub_sub` (Pub/Sub export views) |
| **CDC** | `definitions/cdc/` | Config-driven change log over validated tables |
| **Pub/Sub** | `definitions/pub_sub/` | `pub_sub_schema` creates the `pub_sub` dataset; future shaping tables before Pub/Sub (export views live in `definitions/view/pub_sub/`) |
| **Org center** | `definitions/org_center/` | Who sits in which unit and position, plus TA customer portfolios and special access exceptions, rebuilt nightly (`dimension_daily`); see the [Org Center reference](document/project_wiki/org_center/org-center.md) for tables, sources, PC → TA links, plan codes, company names, and data-quality flags |
| **Process** | `definitions/process/` | AI address parsing + row-level security (see the [process reference](document/project_wiki/cdc-process/process.md), including TA customer access) + [Pub/Sub export pilot](document/project_wiki/cdc-process/process.md#pubsub-export-pilot--dim_company-2026-10-24) |

The Pub/Sub export includes the `dim_company` pilot, commission datasets for TF, the nine org-center tables of the TA app and 33 sample tables for the AI team.
Dataform objects live here, with the publishing Cloud Run jobs (check + send) and their idempotent
GCP setup script in `pubsub/`, deployed by hand.
See the [setup and message guide](document/how-to/setup-pubsub-export.md).

**Validated by source:** MAC5, CIS360, MASTERSKU, MASTER_SKU (3.0),
SALEOUT_MDT and DERP, each with its own schema-bootstrap file. ALLKONS_COMMISSION
has only an initial layer (its validated files were removed). Per-source file lists:
[source inventory](document/project_wiki/validated/source-inventory.md).

**Dimension patterns:** See the [dimension inventory](document/project_wiki/dimension/inventory.md)
for conversion scope, held dimensions, and unchanged behaviors.

---

## Repository Layout

```
definitions/
├── initial/          # External tables (GCS AVRO/CSV) + create_all_schema / create_all_function
│   ├── mac5/         # raw_mac5_ag01, _aa05, _ab01, _ac02, _ak02
│   ├── cis360/  mastersku/  master_sku/  saleout_mdt/  derp/
│   └── allkons_commission/
├── validated/        # Raw → clean, one file per table, per source
│   ├── mac5/  cis360/  mastersku/  master_sku/  derp/
│   └── saleout_mdt/{BT,DH,EOM,GB,HP,LASTYEAR,TW}/
├── curated/          # Clean → business-ready
│   ├── mac5/         # curated_mih, curated_mil, curated_tbook_quotation
│   ├── mastersku/    # curated_product, product_for_aisearch
│   ├── master_sku/   # curated_products, product_for_aisearch_v3
│   ├── saleout_mdt/  # curated_saleout_mdt, curated_stock_mdt, curated_saleout_monthly_mdt
│   └── cis360/       # (schema only)
├── dimension/        # dim_company, other mds dims, dim_customer,
│                     # dim_invoice, dim_order, *_last snapshots, dim_calendar, ...
├── fact/             # fact_invoice, fact_order, fact_delivery, fact_quotation,
│                     # fact_transaction_delivery, fact_transcation (sic — real name),
│                     # fact_chq, fact_mir_vs, fact_mir_rs (AR billing/receive chain),
│                     # fact_*_store, fact_*_mdt (SALEOUT_MDT)
├── view/             # BI/reporting views (dimension_view, fact_view, ...)
├── cdc/              # cdc_schema, cdc_change_log
├── process/          # AI address parsing, RLS access maps, Pub/Sub export pilot
├── pub_sub/          # pub_sub_schema (creates the pub_sub dataset)
└── org_center/       # Org Center objects (see the Org Center reference above)

includes/
├── databuffet.js                 # Central config hub (imported by every SQLX file)
└── controller/
    ├── variables.json            # Dataset names & tag constants
    ├── function-data.js          # Reusable SQL-generating helpers
    ├── cdc-config.json           # Which source tables participate in CDC
    └── mart-export-config.json   # Pub/Sub export selection + task groups (see the process reference)

pubsub/               # Pub/Sub export, GCP side (not Dataform)
├── publisher/        # Cloud Run publisher: main.py (check / send modes), requirements.txt, Dockerfile
├── sql/              # diff.sql - the diff query shared by the publisher and export-snapshot.sh
└── scripts/          # setup.sh, add-consumer.sh, export-snapshot.sh

document/
├── getting-started/  architecture/  coding-standards/  how-to/  operations/   (Thai)
└── project_wiki/     # LLM-oriented wiki (English) — per-layer patterns & inventories

CLAUDE.md                         # project context loaded every session (tracked in git)

.claude/                          # Claude Code working set — NOT in git, ask the team for it
├── skills/                       # /add-validated-table, /ship, /verify-setup, ...
├── agents/  (5)                  # dataform-expert, data-architect, ...
├── hooks/                        # guard-dangerous, doc-sync-check, pre-commit
└── settings.json                 # shared read-only allowlist (personal → settings.local.json)
```

`.claude/` is deliberately git-ignored and handed over by copy. After you place it
in the repo root, the `SessionStart` hook sets `git config core.hooksPath .claude/hooks`
on the first Claude Code session (no manual step).

Packaging and permission steps:
[document/getting-started/onboarding.md §4](document/getting-started/onboarding.md).

---

## Configuration

### `workflow_settings.yaml`
Project-level Dataform settings — **tracked in git** (edits are committed and shared;
the old `.gitignore` entry never took effect and was removed 2026-08-16):

```yaml
defaultProject: databuffet-nonprd
defaultLocation: us-central1
defaultDataset: dataform
defaultAssertionDataset: dataform_assertions
dataformCoreVersion: 3.0.0
vars:
    RAW_BUCKET: "gs://file-raw-data"
    MDS_BACKFILL_DAYS: "1"     # retained project variable; active dimension actions do not use it
    BACKFILL_DAYS: "1"         # incremental look-back window for validated/curated
```

> `BACKFILL_DAYS` now ships in the committed file at `"1"`. `databuffet.js` still
> resolves it with a `|| "1"` fallback, so an older workspace without the var
> compiles to a 1-day window instead of emitting `undefined`. Bump it temporarily
> (and revert) when you need a wider backfill.

### `includes/databuffet.js`
Imported by all SQLX files; merges project config, variables, CDC config and helpers:

```javascript
const databuffet = require("includes/databuffet");

databuffet.DATABASE              // defaultDatabase (databuffet-nonprd)
databuffet.RAW_BUCKET            // gs://file-raw-data
databuffet.REGION                // us-central1
databuffet.MDS_BACKFILL_DAYS     // "1"
databuffet.BACKFILL_DAYS         // "1"  (falls back to "1" if the var is unset)

databuffet.VALIDATED_MAC5        // "validated_mac5"
databuffet.DIMENSION_TABLE       // "dimension_table"
databuffet.TAG_DIM_DAILY         // "dimension_daily"

databuffet.functionData.cleanString(col)   // SQL helpers (see below)
databuffet.cdcConfig                        // CDC source/table config
```

### SQL helpers — `includes/controller/function-data.js`

| Helper | Returns |
|--------|---------|
| `cleanString(col)` | `NULLIF(CAST(TRIM(col) AS STRING), '')` |
| `cleanCode(col, pattern?)` | strips `\n\r\t` (or custom regex), trims, nullifies empty |
| `parseFlexibleDatetime(col)` | parses `%b %d %Y %I:%M%p` **or** `%Y-%m-%d %H:%M:%S` (SAFE) |
| `parseFlexibleUtcDatetime(col)` | parses a UTC `%Y-%m-%d %H:%M:%E*S`, with or without a `+00:00` offset, and returns Bangkok `DATETIME` (SAFE; master_sku, derp journals) |
| `parseAsatDate()` | `PARSE_DATE('%Y%m%d', ASATDATE)` |
| `castInt64(col)` / `castFloat64(col)` / `castBool(col)` | type casts (not SAFE — fail fast) |

---

## BigQuery Schemas

| Source | Raw | Validated | Curated |
|--------|-----|-----------|---------|
| MAC5 | `raw_mac5_ag01`, `raw_mac5_aa05`, `raw_mac5_ab01`, `raw_mac5_ac02`, `raw_mac5_ak02` | `validated_mac5` | `curated_mac5` |
| CIS360 | `raw_cis360` | `validated_cis360` | `curated_cis360` |
| MASTERSKU | `raw_mastersku` | `validated_mastersku` | `curated_mastersku` |
| MASTER_SKU (3.0) | `raw_master_sku` | `validated_master_sku` | `curated_master_sku` |
| SALEOUT_MDT | `raw_saleout_mdt` | `validated_saleout_mdt` | `curated_saleout_mdt` |
| DERP | `raw_derp` | `validated_derp` | — |
| ALLKONS_COMMISSION | `raw_allkons_commission` | `validated_allkons_commission` (left in BigQuery, no repo files) | — |

Shared datasets and their purposes are listed in the
[dataset registry reference](document/project_wiki/includes/variables.md#shared-datasets).
The externally loaded `mds_dataset` supplies most dimensions through master-data
tables `mds_data_*_master` with `id` / `is_active` / `updated_at`.

---

## Tags

Select tags for an execution in the Dataform service (see the
[run guide](document/how-to/run-and-debug.md#รันด้วย-tag)):

| Group | Tags in use |
|-------|-------------|
| Initial | `initial` (⚠️ drops the validated tables of cis360, mastersku, master_sku, saleout_mdt, allkons_commission and derp), `re-initial` (⚠️ drops validated/curated MAC5 tables) |
| Validated | `validated`, `validated_full`, `validated_incremental` |
| Curated | `curated`, `curated_full`, `curated_incremental` (SALEOUT_MDT curated) |
| Dimension | `dimension_daily` (every dim except `dim_calendar`, plus org center and [TA customer access](document/okf/process/rls_ta_customer.md)), `dimension_yearly` (`dim_calendar` only) |
| Fact | `fact_daily` |
| Support | `process`, `cdc`, `cdc_incremental`, `pub_sub` (Pub/Sub pilot objects, run by hand — [pilot deploy](document/project_wiki/cdc-process/process.md#deploy)) |

> ⚠️ To add or refresh raw tables, never run the whole `initial` tag. Run only the
> single `create_all_table_raw_<source>` action. See the
> [initial-layer guide](document/project_wiki/initial/initial-layer.md#การผูก-dependency)
> for dependency safety and deliberate manual rebuilds.

Declared in `variables.json` but currently unused: `dimension_monthly`,
`fact_monthly`, `fact_yearly`. There is no `assertions` tag — the project has no
Dataform assertions. What runs on a schedule (05:45 release from `nonprod`,
`daily_process` 06:00, `saleout_morning` 08:55, `yearly_process`):
[running-and-troubleshooting § Schedule](document/project_wiki/operations/running-and-troubleshooting.md#schedule-dataform-service-databuffet-nonprd).

---

## Common Commands

Execution happens in GCP through the Dataform UI — see
[running by tag](document/how-to/run-and-debug.md#รันด้วย-tag), which also covers
`dataform compile` with the optional global CLI. To check SQL before running, use a
free `bq --dry_run` — see
[checking SQL without the Dataform CLI](document/how-to/run-and-debug.md#ตรวจ-sql-โดยไม่มี-dataform-cli).

Ad-hoc queries: `bq --project_id=databuffet-nonprd query --use_legacy_sql=false '...'`
(always pass `--project_id`).

---

## Key Patterns

### Validated — dedup + non-enforced primary key
Each validated table casts/cleans raw columns with the `functionData` helpers,
deduplicates with `QUALIFY ROW_NUMBER()` over its primary key (defined per file as
`uniqueKey` in config **and** `pk_key` in the js block — keep them in sync), then
attaches a `NOT ENFORCED` primary key in a retry-wrapped post-operation.

```sql
${ when(incremental(), `WHERE ASATDATE >= FORMAT_DATE("%Y%m%d", DATE_SUB(CURRENT_DATE('Asia/Bangkok'), INTERVAL ${databuffet.BACKFILL_DAYS} DAY))`) }
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY <primary key columns>
  ORDER BY asatdate DESC          -- or a business column, per table
) = 1
```

14 MAC5 tables (`mih`, `mil`, `deb`, `stk`, …) UNION ALL five company datasets with a
literal `company_id` column.

### Curated — incremental with Bangkok-time window
```javascript
config {
  type: "incremental",
  schema: databuffet.CURATED_MAC5,
  tags: [databuffet.TAG_CURATED],
  uniqueKey: ["company_id", "mihType", "mihVnos"],
  bigquery: { partitionBy: "asatdate", clusterBy: ["company_id", "mihVnos", "mihType"] }
}
```
Complex reallocation (e.g. the `ag01` split-sale expansion in `curated_mil`) lives in
`post_operations { BEGIN ... END }` as a TEMP → DELETE → INSERT on `self()`.

### Dimension — stable surrogate-key synchronization
See the [dimension sync contract](document/project_wiki/dimension/merge-sk-pattern.md)
for the complete-source pattern and the [inventory](document/project_wiki/dimension/inventory.md)
for scope and exceptions. Follow the [add-dimension guide](document/how-to/add-dimension.md)
when implementing a new dimension.

### Fact — star-schema joins to dimensions (no MERGE)
Three materialization styles: Dataform `type: "table"` rebuilds (`fact_order`,
`fact_invoice`, and — added 2026-07-20 — the AR chain `fact_chq` → `fact_mir_vs` →
`fact_mir_rs`), `CREATE OR REPLACE TABLE AS` scripts (`fact_delivery`,
`fact_quotation`, `fact_transaction_delivery`), and TEMP → DELETE → INSERT upsert
(`fact_transcation`, keyed on `milVnos, milType, CompanySK`). Facts join dimension
surrogate keys, derive `mix_date` from `milYear/Month/Day`, and keep a rolling
**4-year** window (truncated to start-of-year). Dimension refs use string
interpolation + `dependencies[]`; curated/validated sources use `ref()`.

### CDC — config-driven change tracking
`cdc_change_log` loops over the tables flagged in
`includes/controller/cdc-config.json` (currently `mac5.deb`), compares normalized
`check_fields` between raw and validated, and records NEW/CHANGED rows as JSON
(7-day partition expiration). Downstream, `process/deb_address_data` re-parses
**only today's changed addresses** through BigQuery `AI.GENERATE`
(`gemini-3.5-flash-lite`) — the CDC gate is the cost control.

---

## Adding Work

Step-by-step guides with checklists live in [`document/how-to/`](document/how-to/):

| Task | Guide |
|------|-------|
| New validated table | [add-validated-table.md](document/how-to/add-validated-table.md) |
| New curated table | [add-curated-table.md](document/how-to/add-curated-table.md) |
| New dimension (stable surrogate key) | [add-dimension.md](document/how-to/add-dimension.md) |
| New fact table | [add-fact-table.md](document/how-to/add-fact-table.md) |
| Run & debug | [run-and-debug.md](document/how-to/run-and-debug.md) |

---

## Conventions

- **Timezone:** always `Asia/Bangkok` (e.g. `CURRENT_DATE('Asia/Bangkok')`).
- **NULL handling:** follow the [data-cleaning rules, including incremental string keys](document/coding-standards/sqlx-coding-standard.md#4-การ-cast--ทำความสะอาดข้อมูล).
- **DDL:** initial/validated/curated objects are created by Dataform; dimension sync
  actions and `fact_transcation` use existing BigQuery targets.
- **Primary keys:** declared `NOT ENFORCED` for query optimization, not constraints.
- **Surrogate keys:** stable dimension sync keeps an SK attached to its natural key;
  do not regenerate the whole dimension SK column with `ROW_NUMBER()`. Fact row SKs may
  still regenerate when their fact tables rebuild.
- **Partitioning/clustering:** partition incremental tables by `asatdate`; cluster on up to 4 frequently-filtered columns.
- **Load-bearing typos (keep verbatim):** `fact_transcation` (table/file name),
  `CDC_DATESET` (variables.json key), `prdDiminsionData` (MASTERSKU JSON field).
- **Known issues & gotchas:** [document/operations/known-issues.md](document/operations/known-issues.md).
