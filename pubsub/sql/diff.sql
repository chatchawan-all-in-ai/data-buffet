-- Diff query of the Pub/Sub export: one row per changed row (NEW / UPDATE / DELETE) of an export
-- view against process_dataset.mart_sent_state. Used unchanged by the publisher (check / send
-- modes, pubsub/publisher/main.py) and by scripts/export-snapshot.sh, so first-load files are
-- byte-identical to the messages. Placeholders: the dataset of the bookkeeping tables and the
-- export view; the query parameter @table_name is bound by the caller.
-- The message is assembled as text so primary_key is row_key verbatim and data is
-- TO_JSON_STRING of the data columns in view order, the same JSON row_hash fingerprints.
WITH v AS (
  SELECT
    e.row_key,
    e.row_hash,
    TO_JSON_STRING((SELECT AS STRUCT e.* EXCEPT (row_key, row_hash))) AS data
  FROM `{{source_view}}` AS e
),
s AS (
  SELECT row_key, row_hash
  FROM `{{dataset}}.mart_sent_state`
  WHERE table_name = @table_name
)
SELECT
  COALESCE(v.row_key, s.row_key) AS row_key,
  v.row_hash,
  CONCAT(
    '{"table":', TO_JSON_STRING(@table_name),
    ',"run_date":', TO_JSON_STRING(FORMAT_DATE('%F', CURRENT_DATE('Asia/Bangkok'))),
    ',"operation":', TO_JSON_STRING(CASE
      WHEN s.row_key IS NULL THEN 'NEW'
      WHEN v.row_key IS NULL THEN 'DELETE'
      ELSE 'UPDATE'
    END),
    ',"primary_key":', COALESCE(v.row_key, s.row_key),
    ',"data":', IFNULL(v.data, 'null'),
    '}'
  ) AS message
FROM v
FULL OUTER JOIN s ON v.row_key = s.row_key
WHERE s.row_key IS NULL OR v.row_key IS NULL OR v.row_hash != s.row_hash
ORDER BY row_key
