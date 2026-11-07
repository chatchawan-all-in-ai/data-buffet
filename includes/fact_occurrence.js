function assignedOccurrences(source, keyColumn, fields) {
  const grain = fields.map(field => Array.isArray(field)
    ? { name: field[0], sql: field[1] }
    : { name: field, sql: `stored.${field}` });
  return `
    SELECT stored.* EXCEPT(_occ_count),
      (SELECT occurrence
       FROM UNNEST(GENERATE_ARRAY(1, stored._occ_count)) AS occurrence
       WHERE stored.${keyColumn} = FARM_FINGERPRINT(TO_JSON_STRING(STRUCT(
         ${grain.map(field => `${field.sql} AS ${field.name}`).join(', ')},
         occurrence AS occ
       )))) AS _occ
    FROM (
      SELECT stored.*, COUNT(*) OVER (
        PARTITION BY ${grain.map(field => field.sql).join(', ')}
      ) AS _occ_count
      FROM (${source}) AS stored
    ) AS stored`;
}

module.exports = { assignedOccurrences };
