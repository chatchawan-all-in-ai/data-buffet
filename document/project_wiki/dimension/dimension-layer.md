# Dimension Layer — `definitions/dimension/`

> **LLM context**: every `dim_*` file + `update_sk_sale_rep_group`, all writing to
> dataset `dimension_table`. Tag `dimension_daily` on every file except `dim_calendar`,
> which uses `dimension_yearly`; `dimension_monthly` is defined but unused. File count:
> [generated lineage](../../diagrams/pipeline_lineage.md#1-layer-overview).

## Current key patterns

The [inventory](inventory.md) owns conversion scope, natural keys, held dimensions,
and unchanged actions. The [stable SK contract](merge-sk-pattern.md) describes the
complete-source synchronization pattern for converted actions.

See the [full dimension inventory](inventory.md) for every file, key, source, and current
build behavior. [Special cases](special-cases.md) records preserved UNION, fallback,
latest-row, and history logic.

## SCD-2-style dimensions

A new validity interval receives a new SK when `StartDate` and `EndDate` are part of the
natural key. The `_last` dimensions keep their existing latest-row selection and sync on
the retained row’s natural key. Sentinel range for ledger-only sales representatives:
`1900-01-01` → `2499-12-31`.

## Conventions

- SK column: PascalCase `<Entity>SK`; established names include `CollectSK`, `NotReceiveSK`,
  `AvgCollectSK`, and `ProductSK`.
- Dimension table references use `<Name>Table` and `<Name>TableRef` in `js {}`.
- `hasOutput: true` is used by operation actions that expose a dimension target.
- `update_sk_sale_rep_group` remains an UPDATE-only backfill for foreign-key columns in
  the seven `_last` tables.
