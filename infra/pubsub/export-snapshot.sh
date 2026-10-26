#!/usr/bin/env bash
# First full load of one export table for one consumer team, as files instead of Pub/Sub.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน B ขั้น 3).
#
# Writes every current row of the topic's export view to
#   gs://<bucket>/<team>/<topic>/<export time>/data-<shard>.json + manifest.json
# as newline-delimited JSON: each line is exactly the Pub/Sub message the publish workflow
# would send for that row as NEW. The query is the workflow's own diff query
# (datamart-publish.workflows.yaml, step `diff`) with an empty sent state, so the envelope and
# the JSON of every value cannot drift from the messages. BigQuery exports it as CSV (one
# quoted column); each shard is unquoted on the way back into
# the team folder and every line is checked.
#
# Refuses unless sub.<team>.<topic> exists (add-consumer.sh), so no change made after the
# export can be missed. Never writes mart_sent_state or changes the publish workflow.
#
# Prerequisites: setup.sh and add-consumer.sh already run; gcloud + bq logged in as a project
# owner; python3/python.
#
# Usage: bash infra/pubsub/export-snapshot.sh <team> <topic>
#   e.g. bash infra/pubsub/export-snapshot.sh ai-dev export-ta-dim_company
set -euo pipefail

PROJECT=databuffet-nonprd
BQ_LOCATION=us-central1
BQ_DATASET=process_dataset
EXPORT_DATASET=pub_sub
SNAPSHOT_BUCKET=databuffet-nonprd-datamart-snapshot   # created by setup.sh
STAGING_PREFIX=_staging                                # outside every team folder

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../.." && pwd)"
config_json="$repo_root/includes/controller/mart-export-config.json"
workflow_yaml="$here/datamart-publish.workflows.yaml"

log() { printf '\n== %s\n' "$*"; }
die() { printf 'export-snapshot.sh: %s\n' "$*" >&2; exit 1; }

[ $# -eq 2 ] || die "usage: bash infra/pubsub/export-snapshot.sh <team> <topic>"
team="$1"
topic="$2"
[[ "$team" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] ||
  die "team '$team' must be lowercase letters, digits and '-', starting and ending with a letter or digit"
sub="sub.$team.$topic"

pick_python() {
  local py
  for py in python3 python py; do
    if command -v "$py" >/dev/null 2>&1 && "$py" --version >/dev/null 2>&1; then
      echo "$py"
      return
    fi
  done
  die "python3/python not found"
}

log "Checking prerequisites"
command -v gcloud >/dev/null || die "gcloud not found"
command -v bq >/dev/null || die "bq not found"
[ -f "$workflow_yaml" ] || die "missing $workflow_yaml"
python_bin="$(pick_python)"

# table_name<TAB>source_view of the topic's entry in the config JSON.
export_entry="$("$python_bin" - "$config_json" "$topic" <<'PY'
import json, sys
for t in json.load(open(sys.argv[1], encoding="utf-8"))["tables"]:
    if t["topic"] == sys.argv[2]:
        print(f"{t['table_name']}\t{t['source_view']}")
PY
)"
[ -n "$export_entry" ] || die "topic $topic is not in $config_json"
IFS=$'\t' read -r table_name source_view <<< "$export_entry"
gcloud pubsub subscriptions describe "$sub" --project="$PROJECT" >/dev/null 2>&1 ||
  die "subscription $sub not found - run add-consumer.sh $team $topic first (the subscription must exist before the export)"
gcloud storage buckets describe "gs://$SNAPSHOT_BUCKET" >/dev/null 2>&1 ||
  die "bucket gs://$SNAPSHOT_BUCKET not found - run setup.sh first"
echo "  $topic = $table_name from $EXPORT_DATASET.$source_view; $sub exists"

# The workflow's diff query, unchanged except: mart_sent_state is replaced by an empty
# relation (every row of the view becomes NEW) and only the message column is kept.
query="$("$python_bin" - "$workflow_yaml" "$PROJECT.$BQ_DATASET" "$PROJECT.$EXPORT_DATASET.$source_view" <<'PY'
import sys, textwrap
yaml_path, dataset, source_view = sys.argv[1:4]
lines = open(yaml_path, encoding="utf-8").read().splitlines()
try:
    step = next(i for i, l in enumerate(lines) if l.strip() == "- diff:")
    key = next(i for i in range(step, len(lines)) if lines[i].strip() == "sql: |")
except StopIteration:
    sys.exit("export-snapshot.sh: no `- diff:` step with `sql: |` in " + yaml_path)
indent = len(lines[key]) - len(lines[key].lstrip())
block = []
for l in lines[key + 1:]:
    if l.strip() and len(l) - len(l.lstrip()) <= indent:
        break
    block.append(l)
sql = textwrap.dedent("\n".join(block)).strip()
sent_state = "`{{dataset}}.mart_sent_state`"
if sql.count(sent_state) != 1:
    sys.exit("export-snapshot.sh: the diff query no longer reads " + sent_state + " exactly once")
sql = sql.replace(sent_state, "(SELECT '' AS table_name, '' AS row_key, 0 AS row_hash LIMIT 0)")
sql = sql.replace("{{dataset}}", dataset).replace("{{source_view}}", source_view)
if "{{" in sql:
    sys.exit("export-snapshot.sh: unknown placeholder left in the diff query")
print(f"SELECT row_key, row_hash, message FROM (\n{sql}\n)")
PY
)"

# Job ids allow letters, digits, '_' and '-'; the topic may hold '.' or '~'.
job_id="snapshot_${team}_${topic//[^A-Za-z0-9_-]/_}_$(date -u +%Y%m%d%H%M%S)_$RANDOM"
staging="gs://$SNAPSHOT_BUCKET/$STAGING_PREFIX/$team/$topic/$job_id"
folder=""
manifest_written=""
count_file="$(mktemp)"
claim="$("$python_bin" -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat(timespec="microseconds"))')"

# Staging never outlives the run; a failed run also removes its partial data files, so a
# folder holds data only together with its manifest.
cleanup() {
  local status=$?
  if ! bq --project_id="$PROJECT" --location="$BQ_LOCATION" --format=none query --use_legacy_sql=false \
    --parameter="table_name::$table_name" --parameter="claim::$claim" \
    "UPDATE \`$PROJECT.$BQ_DATASET.mart_export_config\`
     SET claimed_at = NULL
     WHERE table_name = @table_name AND claimed_at = TIMESTAMP(@claim)"; then
    if [ -n "$manifest_written" ]; then
      printf 'export-snapshot.sh: export succeeded; publisher claim release failed; the claim expires automatically after 30 minutes\n' >&2
      status=0
    else
      printf 'export-snapshot.sh: could not release the publisher claim; retry after the next publisher run clears it\n' >&2
      status=1
    fi
  fi
  rm -f "$count_file"
  gcloud storage rm "$staging/**" >/dev/null 2>&1 || true
  if [ -n "$folder" ] && [ -z "$manifest_written" ]; then
    gcloud storage rm "$folder/**" >/dev/null 2>&1 || true
  fi
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

log "Claiming publisher state for $table_name"
claimed="$(bq --project_id="$PROJECT" --location="$BQ_LOCATION" --format=json query --use_legacy_sql=false \
  --max_statement_results=1 --parameter="table_name::$table_name" --parameter="claim::$claim" \
  "UPDATE \`$PROJECT.$BQ_DATASET.mart_export_config\`
   SET claimed_at = TIMESTAMP(@claim)
   WHERE table_name = @table_name
     AND claimed_at IS NULL;
   SELECT @@row_count AS claimed" |
  "$python_bin" -c 'import json, sys; print(json.load(sys.stdin)[0]["claimed"])')"
[ "$claimed" -eq 1 ] || die "publisher claim unavailable for $table_name; retry after the next publisher run clears it"

log "Checking publisher catch-up and exporting $EXPORT_DATASET.$source_view (BigQuery job $job_id)"
job_facts="$(bq --project_id="$PROJECT" --location="$BQ_LOCATION" --format=json query --use_legacy_sql=false \
  --max_statement_results=1 --job_id="$job_id" --parameter="table_name::$table_name" --parameter="claim::$claim" \
  "DECLARE export_time TIMESTAMP;
   BEGIN TRANSACTION;
   SET export_time = CURRENT_TIMESTAMP();
   ASSERT (SELECT COUNT(*) = 1 FROM \`$PROJECT.$BQ_DATASET.mart_export_config\`
     WHERE table_name = @table_name AND claimed_at = TIMESTAMP(@claim)
       AND claimed_at >= TIMESTAMP_SUB(export_time, INTERVAL 30 MINUTE))
     AS 'publisher claim expired or was lost; retry later';
   CREATE TEMP TABLE snapshot AS
$query;
   ASSERT NOT EXISTS (
     SELECT 1 FROM snapshot AS v
     FULL OUTER JOIN (
       SELECT row_key, row_hash FROM \`$PROJECT.$BQ_DATASET.mart_sent_state\`
       WHERE table_name = @table_name
     ) AS s ON v.row_key = s.row_key
     WHERE v.row_key IS NULL OR s.row_key IS NULL OR v.row_hash IS DISTINCT FROM s.row_hash
   ) AS 'publisher has not caught up; wait for the next publisher run, then retry';
   COMMIT TRANSACTION;
   EXPORT DATA OPTIONS (uri = '$staging/*.csv', format = 'CSV', header = false) AS
     SELECT message FROM snapshot;
   SELECT FORMAT_TIMESTAMP('%Y-%m-%dT%H:%M:%E6SZ', export_time, 'UTC') AS export_time,
     COUNT(*) AS row_count FROM snapshot" |
  "$python_bin" -c '
import json, sys
from datetime import datetime
facts = json.load(sys.stdin)[0]
cut = datetime.fromisoformat(facts["export_time"].replace("Z", "+00:00"))
print(facts["export_time"], cut.strftime("%Y%m%dT%H%M%S%fZ"), facts["row_count"], sep="\t")
')"
IFS=$'\t' read -r export_time stamp row_count <<< "$job_facts"
folder="gs://$SNAPSHOT_BUCKET/$team/$topic/$stamp"
if gcloud storage ls "$folder/" >/dev/null 2>&1; then
  folder=""
  die "gs://$SNAPSHOT_BUCKET/$team/$topic/$stamp already holds files"
fi

log "Writing $folder"
# CSV field -> message line. strict + exactly one field + a NEW envelope on every line, so a
# quoting difference fails here instead of reaching the team.
unquote='
import csv, io, json, sys
count = 0
out = sys.stdout.buffer
for fields in csv.reader(io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", newline=""), strict=True):
    if len(fields) != 1:
        sys.exit(f"export-snapshot.sh: line {count + 1} has {len(fields)} CSV fields, expected 1")
    message = fields[0]
    envelope = json.loads(message)
    if list(envelope) != ["table", "run_date", "operation", "primary_key", "data"] or envelope["operation"] != "NEW":
        sys.exit(f"export-snapshot.sh: line {count + 1} is not a NEW message: {message[:200]}")
    out.write(message.encode("utf-8") + b"\n")
    count += 1
with open(sys.argv[1], "w") as f:
    f.write(str(count))
'
files=()
total=0
while read -r shard; do
  [ -n "$shard" ] || continue
  name="$(basename "$shard" .csv)"
  target="$folder/data-$name.json"
  gcloud storage cat "$shard" |
    "$python_bin" -c "$unquote" "$count_file" |
    gcloud storage cp --content-type=application/x-ndjson - "$target" >/dev/null
  total=$((total + $(cat "$count_file")))
  files+=("$target")
  echo "  $target ($(cat "$count_file") rows)"
done < <(gcloud storage ls "$staging/" | sort)
[ "${#files[@]}" -gt 0 ] || die "the export wrote no file to $staging"
[ "$total" -eq "$row_count" ] || die "wrote $total rows but the export job reported $row_count"

log "Seeking $sub to the snapshot cut $export_time"
gcloud pubsub subscriptions seek "$sub" --project="$PROJECT" --time="$export_time" >/dev/null

log "Waiting 90 seconds for subscription seek propagation (publisher claim held)"
sleep 90

printf '%s\n' "${files[@]}" |
  "$python_bin" -c '
import json, sys
table, topic, team, export_time, row_count = sys.argv[1:6]
print(json.dumps({
    "table": table,
    "topic": topic,
    "team": team,
    "export_time": export_time,
    "row_count": int(row_count),
    "files": sys.stdin.read().split(),
}, indent=2))
' "$table_name" "$topic" "$team" "$export_time" "$row_count" |
  gcloud storage cp --content-type=application/json - "$folder/manifest.json" >/dev/null
manifest_written=1

log "Done"
echo "  folder:      $folder/"
echo "  export time: $export_time (UTC) - publisher-consistent cut; use as every snapshot row's version"
echo "  rows:        $row_count in ${#files[@]} file(s) + manifest.json"
