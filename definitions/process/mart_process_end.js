// Last action of the daily_process run: set the run's STARTED row in mart_process_log to
// FINISHED. Leaves publish_claimed_at / published_at alone — those belong to the publish workflow.
//
// "Last" = after every action that carries one of the run's tags (run_tags in
// includes/controller/mart-export-config.json — keep it equal to the tag list of the
// daily_process workflow configuration in the Dataform UI). If any of them fails, Dataform
// skips this action, the row stays STARTED and nothing is published.
//
// Cloud Dataform allows at most 50 dependencies per action, so the run's actions are split
// across a fixed pool of no-op barrier actions (at most 50 each) and mart_process_end depends
// on the barriers only. Dataform has no "run after everything" option and files compile in
// alphabetical order, so the lists are built inside the queries callbacks: they run in
// session.compile(), after every definitions file has registered its actions and before
// dependencies are resolved.
const cfg = databuffet.martExportConfig;
const runTags = new Set(cfg.run_tags.map(key => databuffet[key]));
const log = `${databuffet.DATABASE}.${databuffet.PROCESS_DATASET}.mart_process_log`;
const MAX_DEPENDENCIES = 50;
const BARRIER_COUNT = 10;

const barriers = [];
const end = operate("mart_process_end");

let chunks;
function runChunks() {
  if (!chunks) {
    const own = new Set([end, ...barriers]);
    const runActions = dataform.actions
      .filter(action => !own.has(action) && (action.proto.tags || []).some(tag => runTags.has(tag)))
      .map(action => action.proto.target);
    if (runActions.length > BARRIER_COUNT * MAX_DEPENDENCIES) {
      throw new Error(`mart_process_end: ${runActions.length} run actions exceed ${BARRIER_COUNT} barriers x ${MAX_DEPENDENCIES}; raise BARRIER_COUNT`);
    }
    chunks = [];
    for (let i = 0; i < runActions.length; i += MAX_DEPENDENCIES) {
      chunks.push(runActions.slice(i, i + MAX_DEPENDENCIES));
    }
  }
  return chunks;
}

for (let i = 0; i < BARRIER_COUNT; i++) {
  const name = `mart_process_barrier_${String(i + 1).padStart(2, "0")}`;
  const barrier = operate(name)
    .tags([databuffet.TAG_RUN_LOG_DAILY])
    .description(`No-op: waits for part ${i + 1} of the daily_process run so mart_process_end stays under the 50-dependency limit`)
    .queries(() => {
      barrier.dependencies(runChunks()[i] || []);
      return "SELECT 1";
    });
  barriers.push(barrier);
}

end
  .tags([databuffet.TAG_RUN_LOG_DAILY])
  .dependencies(barriers.map(barrier => barrier.proto.target.name))
  .description("Last action of the daily_process run: set its STARTED row in mart_process_log to FINISHED after every action of the run succeeded")
  .queries(`
UPDATE \`${log}\`
SET status = 'FINISHED',
    finished_at = CURRENT_TIMESTAMP()
WHERE run_id = (
  SELECT run_id
  FROM \`${log}\`
  WHERE process_name = '${cfg.process_name}'
    AND status = 'STARTED'
  ORDER BY started_at DESC
  LIMIT 1
)`);
