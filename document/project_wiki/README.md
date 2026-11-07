# Data-Buffet — LLM Wiki

> **Purpose**: Machine-oriented knowledge base for LLM agents working on this repo.
> Every page opens with an "LLM context" block stating what the page covers and the
> non-obvious constraints. Generated from a full code scan on **2026-07-10** — when
> code and wiki disagree, trust the code and update the wiki.

## Routing — read what the task needs

| Task | Read |
|---|---|
| Any task (start here) | [overview/architecture.md](overview/architecture.md) |
| Understand a source system / raw data (incl. SALEOUT_MDT end-to-end, DERP) | [overview/source-systems.md](overview/source-systems.md), [initial/initial-layer.md](initial/initial-layer.md) |
| Add/edit a validated table | [validated/validated-layer.md](validated/validated-layer.md), [validated/source-inventory.md](validated/source-inventory.md) |
| Add/edit a curated table | [curated/curated-layer.md](curated/curated-layer.md) |
| Add/edit a dimension | [dimension/dimension-layer.md](dimension/dimension-layer.md) → [dimension/merge-sk-pattern.md](dimension/merge-sk-pattern.md) (common stable-key sync) → [dimension/special-cases.md](dimension/special-cases.md) |
| MDS soft-delete / `is_active` / overwrite import | [dimension/mds-delete-pattern.md](dimension/mds-delete-pattern.md) and [dimension/inventory.md](dimension/inventory.md) |
| Which dim owns which SK | [dimension/inventory.md](dimension/inventory.md) |
| Add/edit a fact | [fact/fact-layer.md](fact/fact-layer.md) |
| Add/edit a view (presentation layer) | [view/view-layer.md](view/view-layer.md), how-to: `document/how-to/add-view.md` |
| Deploy a view to BigQuery (done by hand — `view` tag is not scheduled) | `document/how-to/deploy-view.md` |
| What a business flag means (`FlagFree`, `FlagExpire`, `item_status`, `seq_condition`) | [overview/business-flags.md](overview/business-flags.md) |
| Org center (units, positions, PC → TA links, TA customer portfolios, code mapping, company names, data-quality flags) | [org_center/org-center.md](org_center/org-center.md) |
| CDC / change tracking | [cdc-process/cdc.md](cdc-process/cdc.md) |
| AI address parsing | [cdc-process/process.md](cdc-process/process.md) |
| Config, tags, helpers | [includes/databuffet-js.md](includes/databuffet-js.md), [includes/variables.md](includes/variables.md), [includes/function-data.md](includes/function-data.md), [includes/cdc-config.md](includes/cdc-config.md) |
| Run / debug / env facts / what runs on schedule | [operations/running-and-troubleshooting.md](operations/running-and-troubleshooting.md) |
| How work reaches `nonprod` (release flow) | `document/getting-started/onboarding.md` § Release flow |

## Hard rules (apply to every change)

1. Timezone is always `Asia/Bangkok`.
2. Follow the [data-cleaning rules, including incremental string keys](../coding-standards/sqlx-coding-standard.md#4-การ-cast--ทำความสะอาดข้อมูล).
3. Never hardcode dataset names/tags — use `databuffet.*` constants.
4. Follow the [dimension sync contract](dimension/merge-sk-pattern.md) and
   [inventory](dimension/inventory.md), preserving held and unchanged actions.
5. `type: "operations"` targets (dimension sync actions and `fact_transcation`) pre-exist in
   BigQuery — Dataform does not create them.
6. Preserve load-bearing typos verbatim: `fact_transcation`, `CDC_DATESET`, `prdDiminsionData`.
7. Stable dimension sync uses a complete active-source snapshot; do not limit delete-by-
   source to an `updated_at` window.
8. Dimension build dependencies: see [dimension inventory](dimension/inventory.md).

## Companion tooling

`.claude/` was rebuilt 2026-07-10 to point into this wiki: `CLAUDE.md` (repo root, tracked in git since 2026-09-01; session
context), skills (`add-initial-table`, `add-validated-table`, `add-curated-table`,
`add-dimension`, `add-fact-table`, `dataform-run`, `enable-cdc`,
`backfill-dimension`, `fk-integrity-scan`, `data-quality-check`, `update-docs`,
plus `bq-drift-scan`, `ship`, `check-runs`, `verify-setup`, `show-me` added later
— 16 total)
and agents (`dataform-expert`, `data-architect`, `bigquery-optimizer`,
`data-quality-auditor`, `bq-drift-auditor` — 5 total). The old `.claude/knowledge/` and root scaffold guides were
deleted as stale — the historical error list is preserved in
`document/operations/known-issues.md`. Root `README.md` was rewritten the same day
and is accurate.
