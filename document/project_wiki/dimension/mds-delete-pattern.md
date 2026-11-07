# MDS inactive and missing row synchronization

MDS-sourced dimensions converted to the common stable-key pattern build a complete source
snapshot from active rows on every daily run. The dimension action updates matching
natural keys, inserts new keys, and deletes target rows that are inactive or missing from
the complete snapshot. There is no separate tombstone statement or `updated_at` window.

See [stable dimension SK synchronization](merge-sk-pattern.md) for the three-clause
action and [inventory](inventory.md) for the affected dimensions and their natural keys.

## Identity and source rules

Follow the [common key and synchronization rules](merge-sk-pattern.md#key-and-synchronization-rules)
and the table's OKF card for identity, source completeness and allocation. Company’s
legacy identity lookup is an exception described in its
[card](../../okf/dimension/dim_company.md#how-it-is-built).

## Exceptions

- `dim_customer_report_info` intentionally retains rows that leave its current source.
- `dim_order` remains outside this sync under captain decision; its lake sync has no
  delete clause and the fix touches many downstream tables.

The eight existing lake-sourced MERGE dimensions retain their current source-specific
actions; they do not read MDS and are listed separately in the [inventory](inventory.md).
