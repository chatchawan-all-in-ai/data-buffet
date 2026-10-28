/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast, trim, and nullify empty string
**/
function cleanString(col) {
    return `NULLIF(CAST(TRIM(${col}) AS STRING), '')`
}

/**
 * @param {string} col - column name or expression
 * @param {string} [pattern=r'[\n\r\t]'] - BigQuery raw string regex pattern to remove
 * @returns {string} GoogleSQL expression to regexp-replace, trim, cast, and nullify empty string
**/
function cleanCode(col, pattern = `r'[\\n\\r\\t]'`) {
    return `NULLIF(CAST(TRIM(REGEXP_REPLACE(${col}, ${pattern}, '')) AS STRING), '')`
}

/**
 * @param {string} col - column name containing datetime string
 * @returns {string} GoogleSQL expression that parses both '%b %d %Y %I:%M%p' and '%Y-%m-%d %H:%M:%S' formats
**/
function parseFlexibleDatetime(col) {
    return `COALESCE(
    SAFE.PARSE_DATETIME('%b %d %Y %I:%M%p', SUBSTR(${col}, 1, 19)),
    SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', SUBSTR(${col}, 1, 19))
  )`
}

/**
 * @param {string} col - column name containing a UTC datetime string, with or without a '+00:00' offset
 * @returns {string} GoogleSQL expression returning DATETIME in Asia/Bangkok (no-offset values are read as UTC)
**/
function parseFlexibleUtcDatetime(col) {
    return `DATETIME(COALESCE(
    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%E*S%Ez', ${col}),
    SAFE.PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%E*S', ${col})
  ), 'Asia/Bangkok')`
}

/**
 * @returns {string} GoogleSQL expression to parse ASATDATE column (YYYYMMDD format) to DATE
**/
function parseAsatDate() {
    return `PARSE_DATE('%Y%m%d', ASATDATE)`
}

/**
 * @param {string} col - column name or expression holding a 'YYYY-MM-DD' or 'YYYY/MM/DD' date string (saleout_mdt feeds)
 * @returns {string} GoogleSQL expression parsing col to DATE — NULL stays NULL; any other value that
 *                   neither format parses fails the run via ERROR() rather than turning into NULL
 *                   (same stance as castInt64)
**/
function parseFlexibleDate(col) {
    return `CASE WHEN ${col} IS NULL THEN NULL ELSE COALESCE(SAFE.PARSE_DATE('%Y-%m-%d', ${col}), SAFE.PARSE_DATE('%Y/%m/%d', ${col}), ERROR(CONCAT('parseFlexibleDate: unknown date format: ', ${col}))) END`
}

/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast column to INT64
**/
function castInt64(col) {
    return `CAST(${col} AS INT64)`
}

/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast column to FLOAT64
**/
function castFloat64(col) {
    return `CAST(${col} AS FLOAT64)`
}

/**
 * @param {string} col - column name or expression
 * @returns {string} GoogleSQL expression to cast column to BOOL
**/
function castBool(col) {
    return `CAST(${col} AS BOOL)`
}

module.exports = {
    cleanString,
    cleanCode,
    parseFlexibleDatetime,
    parseFlexibleUtcDatetime,
    parseAsatDate,
    parseFlexibleDate,
    castInt64,
    castFloat64,
    castBool,
}
