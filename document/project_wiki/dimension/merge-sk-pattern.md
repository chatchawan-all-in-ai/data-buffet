# Stable dimension SK synchronization

> **LLM context**: Common contract for the dimensions identified in the
> [conversion inventory](inventory.md). Keep each table’s existing column names, SK name,
> source branches, and derived formulas. `dim_waterpac` is a reference implementation.

## Action and source

Use a `type: "operations"` action with `hasOutput: true`, `schema: databuffet.DIMENSION_TABLE`,
and the established `dependencies` and tags. Declare the target as a `<Name>Table` object
and `<Name>TableRef` string in `js {}`. The dimension table must already exist.

The `USING` source is the complete set of rows that should exist after the sync. Preserve
the dimension’s existing SELECT, UNION, QUALIFY, fallback rows, sentinel `-1` row, and
calculated columns. Keep its existing `is_active = TRUE` filters. A complete snapshot means
that a source row becoming inactive or disappearing is removed from the dimension.

## Key and synchronization rules

- Derive the natural key from the grain retained by the existing SELECT, DISTINCT,
  QUALIFY and UNION branches. Start with MDS primary-key columns where available, then
  include every discriminator needed to preserve those rows, including validity dates,
  rule status and order-window fields. The table's OKF card owns its exact grain and key.
  If no unambiguous unique key preserves the rows, hold the conversion; do not deduplicate
  rows to make the assertions pass.
- Compare nullable natural-key parts with `IS NOT DISTINCT FROM` during the existing-SK lookup.
  After retaining or allocating the SK, use `ON T.<SK> = S.<SK>` at the MERGE boundary.
- Assert that source and target natural keys are unique. Assert that target SKs are non-NULL
  and unique before synchronizing.
- Keep the target SK when the natural key matches. Allocate new SKs after the existing
  maximum with `MAX(SK) + ROW_NUMBER()` over only new source rows, ordered by the natural key.
- Use the same three clauses for every dimension in this pattern:
  1. Matched: update descriptive and derived attributes only.
  2. Not matched: insert the complete source row, including its assigned SK.
  3. Not matched by source: delete the target row.
- Do not update the SK or natural-key columns. Do not use delete-by-source with an
  `updated_at` window; deletion requires a complete source snapshot.

This removes inactive and missing rows directly, without retaining tombstones. Keep the
process definitions and their filters unchanged. This sync applies only to dimension SQLX
files.

## Exceptions

See the [inventory](inventory.md) for held conversions and unchanged actions.
`dim_company` preserves its legacy identity lookup rather than the common natural-key
lookup and assertions; its exact behavior is owned by the
[company card](../../okf/dimension/dim_company.md#how-it-is-built).
