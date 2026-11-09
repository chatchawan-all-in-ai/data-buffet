const variables = require("./controller/variables.json")
const cdcConfig = require("./controller/cdc-config.json")
const martExportConfig = require("./controller/mart-export-config.json")
const functionData = require("./controller/function-data")


module.exports = {
    DATABASE: dataform.projectConfig.defaultDatabase,
    RAW_BUCKET: dataform.projectConfig.vars.RAW_BUCKET,
    REGION: dataform.projectConfig.defaultLocation,
    MDS_BACKFILL_DAYS: dataform.projectConfig.vars.MDS_BACKFILL_DAYS,
    // Avoid undefined windows when BACKFILL_DAYS is absent.
    BACKFILL_DAYS: dataform.projectConfig.vars.BACKFILL_DAYS || "1",
    ...variables,
    cdcConfig,
    martExportConfig,
    functionData,
}