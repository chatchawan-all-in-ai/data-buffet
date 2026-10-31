---
type: Reference
title: Data Mart OKF bundle
description: What the document/okf bundle contains, the card layout, and the rule for what a card may contain and how it is kept in sync.
status: draft
---

# What this is

An [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) (v0.2) bundle with one
card per BigQuery table or view that this repository's Dataform definitions create or maintain in project
`databuffet-nonprd`. It tells other AI agents what each table is and how to use it. The entry point is [index.md](index.md).

# Layout

- `<layer>/<table>.md` for single-dataset layers (`dimension`, `fact`, `process`, `cdc`, `org_center`);
  `<layer>/<dataset>/<table>.md` for `initial`, `validated`, `curated`, `view`.
- `index.md` in the root, every layer folder and every dataset folder; `log.md` lists bundle changes (newest first).
- A card is a markdown file with YAML frontmatter (`type` is `BigQuery Table` or `BigQuery View`, plus title, description,
  resource, project_id, dataset_id, table_id, tags, sources, generated, status) and these sections: `# What it is` (what it is and who uses it),
  `# Grain and key`, `# Schema` (every column: name, type, meaning), `# How it is built`, `# Examples`.
- `project_id`, `dataset_id` and `table_id` are plain strings that state where the table lives in BigQuery; they match
  the `resource` console URL (`p`, `d`, `t`). They are producer extensions allowed by OKF v0.2.
- Not covered: MDS, Dify, other repositories, tables Dataform does not build, operations that own no table.

# Rule

An OKF card contains only table information. It has no warnings or caveats, no discussion or decision notes,
and no answers from people. Sources in frontmatter point only to repository files or public URLs.

- A new table or view has a new card and a line in the folder `index.md`.
- Changed columns, grain, source or behavior are reflected in that table's own card.
- A dropped table or view has its card and index line deleted.

Card and index changes and a `log.md` entry accompany the code change in the same commit.
