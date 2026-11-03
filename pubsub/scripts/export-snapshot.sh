#!/usr/bin/env bash
# First full load of one export table for one consumer team, as files instead of Pub/Sub.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน B ขั้น 3).
#
# Writes every current row of the topic's export view to
#   gs://<bucket>/<team>/<topic>/<export time>/<YYYY>/<MM>/<DD>/data-<n>.json + manifest.json
# as newline-delimited JSON: each line is exactly the Pub/Sub message the publisher
# would send for that row as NEW. <YYYY>/<MM>/<DD> is the row's document date, read from the
# message data column named by `snapshot_date` of the topic's entry in mart-export-config.json
# ({"column", "format"} for PARSE_DATETIME); an entry without it (master data) puts every row
# under the export date (Asia/Bangkok). The query is the publisher's own diff query
# (pubsub/sql/diff.sql) with an empty sent state, so the envelope and
# the JSON of every value cannot drift from the messages. BigQuery exports it as CSV (date
# folder + one quoted message column); the shards are unquoted and split into the date folders
# on the way back into the team folder, and every line is checked.
#
# Refuses unless sub.<team>.<topic> exists (add-consumer.sh), so no change made after the
# export can be missed. Writes mart_sent_state only for the one-time seed of an unseeded table.
#
# Prerequisites: setup.sh and add-consumer.sh already run; gcloud + bq logged in as a project
# owner in Google Cloud Shell (CLOUD_SHELL=true); python3/python.
#
# Usage: bash pubsub/scripts/export-snapshot.sh <team> <topic>
#   e.g. bash pubsub/scripts/export-snapshot.sh ai-dev export-ta-dim_company
set -euo pipefail

PROJECT=databuffet-nonprd
BQ_LOCATION=us-central1
BQ_DATASET=process_dataset
EXPORT_DATASET=pub_sub
SNAPSHOT_BUCKET=databuffet-nonprd-datamart-snapshot   # created by setup.sh
STAGING_PREFIX=_staging                                # outside every team folder
FILE_ROWS=100000                                       # lines per data file in one date folder

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../.." && pwd)"
# The single copy of the export config stays in includes/ (Dataform reads it from there).
config_json="$repo_root/includes/controller/mart-export-config.json"
diff_sql="$here/../sql/diff.sql"

log() { printf '\n== %s\n' "$*"; }
die() { printf 'export-snapshot.sh: %s\n' "$*" >&2; exit 1; }

[ $# -eq 2 ] || die "usage: bash pubsub/scripts/export-snapshot.sh <team> <topic>"
team="$1"
topic="$2"
[[ "$team" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] ||
  die "team '$team' must be lowercase letters, digits and '-', starting and ending with a letter or digit"
[ "${CLOUD_SHELL:-}" = "true" ] ||
  die "first-load data must not pass through a workstation; run from Google Cloud Shell, which is GCP-hosted"
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
[ -f "$diff_sql" ] || die "missing $diff_sql"
python_bin="$(pick_python)"

# table_name<TAB>source_view<TAB>date column<TAB>date format of the topic's entry in the config
# JSON (the last two empty for an entry without snapshot_date). Column and format are checked
# here because they are written into the query.
export_entry="$("$python_bin" - "$config_json" "$topic" <<'PY'
import json, re, sys
for t in json.load(open(sys.argv[1], encoding="utf-8"))["tables"]:
    if t["topic"] == sys.argv[2]:
        d = t.get("snapshot_date") or {}
        column, fmt = d.get("column", ""), d.get("format", "")
        if d and not (re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", column) and re.fullmatch(r"[%A-Za-z0-9/:. _-]+", fmt)):
            sys.exit(f"export-snapshot.sh: snapshot_date of {t['table_name']} needs a plain column name and a PARSE_DATETIME format")
        print(f"{t['table_name']}\t{t['source_view']}\t{column}\t{fmt}")
PY
)"
[ -n "$export_entry" ] || die "topic $topic is not in $config_json"
IFS=$'\t' read -r table_name source_view date_column date_format <<< "$export_entry"
if [ -n "$date_column" ]; then
  # Document date of the row, from the message data exactly as sent; an unparsable value fails the export.
  file_date_sql="DATE(PARSE_DATETIME('$date_format', JSON_VALUE(message, '\$.data.$date_column')))"
  date_note="document date from data.$date_column"
else
  file_date_sql="DATE(export_time, 'Asia/Bangkok')"
  date_note="export date (no snapshot_date)"
fi
gcloud pubsub subscriptions describe "$sub" --project="$PROJECT" >/dev/null 2>&1 ||
  die "subscription $sub not found - run add-consumer.sh $team $topic first (the subscription must exist before the export)"
gcloud storage buckets describe "gs://$SNAPSHOT_BUCKET" >/dev/null 2>&1 ||
  die "bucket gs://$SNAPSHOT_BUCKET not found - run setup.sh first"
echo "  $topic = $table_name from $EXPORT_DATASET.$source_view; $sub exists; folders by $date_note"

# The publisher's diff query (pubsub/sql/diff.sql), unchanged except: mart_sent_state is replaced
# by an empty relation (every row of the view becomes NEW) and only the message column is kept.
query="$("$python_bin" - "$diff_sql" "$PROJECT.$BQ_DATASET" "$PROJECT.$EXPORT_DATASET.$source_view" <<'PY'
import sys
sql_path, dataset, source_view = sys.argv[1:4]
sql = open(sql_path, encoding="utf-8").read().strip()
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

seed_mode="$(bq --project_id="$PROJECT" --location="$BQ_LOCATION" --format=json query --use_legacy_sql=false \
  --parameter="table_name::$table_name" \
  "SELECT seeded_at IS NULL AS seed_mode FROM \`$PROJECT.$BQ_DATASET.mart_export_config\`
   WHERE table_name = @table_name" |
  "$python_bin" -c 'import json, sys; rows = json.load(sys.stdin); assert len(rows) == 1, "expected one export config row"; print(str(rows[0]["seed_mode"]).lower())')"

# Job ids allow letters, digits, '_' and '-'; the topic may hold '.' or '~'.
job_id="snapshot_${team}_${topic//[^A-Za-z0-9_-]/_}_$(date -u +%Y%m%d%H%M%S)_$RANDOM"
staging="gs://$SNAPSHOT_BUCKET/$STAGING_PREFIX/$team/$topic/$job_id"
folder=""
manifest_written=""
count_file="$(mktemp)"
local_dir="$(mktemp -d)"
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
      printf 'export-snapshot.sh: export succeeded; publisher claim release failed; the claim expires automatically after 35 minutes\n' >&2
      status=0
    else
      printf 'export-snapshot.sh: could not release the publisher claim; the claim must be cleared before retrying\n' >&2
      status=1
    fi
  fi
  rm -f "$count_file"
  rm -rf "$local_dir"
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
# A script prints one JSON entry per statement (a DML entry is its message string); the
# final SELECT is the last entry.
claimed="$(bq --project_id="$PROJECT" --location="$BQ_LOCATION" --format=json query --use_legacy_sql=false \
  --parameter="table_name::$table_name" --parameter="claim::$claim" \
  "UPDATE \`$PROJECT.$BQ_DATASET.mart_export_config\`
   SET claimed_at = TIMESTAMP(@claim)
   WHERE table_name = @table_name AND claimed_at IS NULL;
   SELECT @@row_count AS claimed" |
  "$python_bin" -c 'import json, sys; print(json.load(sys.stdin)[-1][0]["claimed"])')"
[ "$claimed" -eq 1 ] || die "publisher claim unavailable for $table_name; the claim must be cleared before retrying"

# The publisher's claim is valid for 35 minutes (CLAIM_TIMEOUT_MINUTES in publisher/main.py). The
# 30-minute assertion below is deliberately shorter: this script fails before the publisher can
# take over an expired claim, so the two never export the same table at once.
log "Checking publisher catch-up and exporting $EXPORT_DATASET.$source_view (BigQuery job $job_id)"
job_facts="$(bq --project_id="$PROJECT" --location="$BQ_LOCATION" --format=json query --use_legacy_sql=false \
  --job_id="$job_id" --parameter="table_name::$table_name" --parameter="claim::$claim" --parameter="seed_mode:BOOL:$seed_mode" \
  "DECLARE export_time TIMESTAMP;
   BEGIN TRANSACTION;
   SET export_time = CURRENT_TIMESTAMP();
   ASSERT (SELECT COUNT(*) = 1 FROM \`$PROJECT.$BQ_DATASET.mart_export_config\`
     WHERE table_name = @table_name AND claimed_at = TIMESTAMP(@claim)
       AND claimed_at >= TIMESTAMP_SUB(export_time, INTERVAL 30 MINUTE))
     AS 'publisher claim expired or was lost; retry later';
   CREATE TEMP TABLE snapshot AS
SELECT row_key, row_hash, message, $file_date_sql AS file_date FROM (
$query
);
   ASSERT NOT EXISTS (SELECT 1 FROM snapshot WHERE file_date IS NULL)
     AS 'a row has no date for its folder ($date_note)';
   IF @seed_mode THEN
     ASSERT (SELECT COUNT(*) = 1 FROM \`$PROJECT.$BQ_DATASET.mart_export_config\`
       WHERE table_name = @table_name AND seeded_at IS NULL AND claimed_at = TIMESTAMP(@claim))
       AS 'table already seeded or publisher claim was lost';
     ASSERT NOT EXISTS (SELECT 1 FROM \`$PROJECT.$BQ_DATASET.mart_sent_state\`
       WHERE table_name = @table_name) AS 'unseeded table already has sent state';
     INSERT INTO \`$PROJECT.$BQ_DATASET.mart_sent_state\`
       (table_name, row_key, row_hash, invocation_id, sent_at)
     SELECT @table_name, row_key, row_hash, 'seed', export_time FROM snapshot;
     UPDATE \`$PROJECT.$BQ_DATASET.mart_export_config\`
     SET seeded_at = export_time, last_invocation_id = 'seed', last_invocation_end = export_time
     WHERE table_name = @table_name AND claimed_at = TIMESTAMP(@claim);
   END IF;
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
     SELECT FORMAT_DATE('%Y/%m/%d', file_date) AS folder, message FROM snapshot;
   SELECT FORMAT_TIMESTAMP('%Y-%m-%dT%H:%M:%E6SZ', export_time, 'UTC') AS export_time,
     COUNT(*) AS row_count FROM snapshot" |
  "$python_bin" -c '
import json, sys
from datetime import datetime
facts = json.load(sys.stdin)[-1][0]
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
# CSV (folder, message) -> message line in <YYYY>/<MM>/<DD>/data-<n>.json under a local
# directory, FILE_ROWS lines per file. strict + exactly two fields + a date folder + a NEW
# envelope on every line, so a quoting difference fails here instead of reaching the team.
split='
import csv, io, json, os, re, sys
out_dir, count_path, file_rows = sys.argv[1], sys.argv[2], int(sys.argv[3])
files = {}
count = 0
for fields in csv.reader(io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", newline=""), strict=True):
    if len(fields) != 2:
        sys.exit(f"export-snapshot.sh: line {count + 1} has {len(fields)} CSV fields, expected 2")
    day, message = fields
    if not re.fullmatch(r"\d{4}/\d{2}/\d{2}", day):
        sys.exit(f"export-snapshot.sh: line {count + 1} has folder {day!r}, expected YYYY/MM/DD")
    envelope = json.loads(message)
    if list(envelope) != ["table", "run_date", "operation", "primary_key", "data"] or envelope["operation"] != "NEW":
        sys.exit(f"export-snapshot.sh: line {count + 1} is not a NEW message: {message[:200]}")
    f = files.get(day)
    if f is None or f["rows"] == file_rows:
        if f is not None:
            f["handle"].close()
        n = 0 if f is None else f["n"] + 1
        os.makedirs(os.path.join(out_dir, day), exist_ok=True)
        f = files[day] = {"n": n, "rows": 0,
                          "handle": open(os.path.join(out_dir, day, f"data-{n:06d}.json"), "wb")}
    f["handle"].write(message.encode("utf-8") + b"\n")
    f["rows"] += 1
    count += 1
for f in files.values():
    f["handle"].close()
with open(count_path, "w") as c:
    c.write(str(count))
'
shards="$(gcloud storage ls "$staging/" | sort)"
[ -n "$shards" ] || die "the export wrote no file to $staging"
while read -r shard; do
  [ -z "$shard" ] || gcloud storage cat "$shard"
done <<< "$shards" | "$python_bin" -c "$split" "$local_dir" "$count_file" "$FILE_ROWS"
total="$(cat "$count_file")"
gcloud storage cp --recursive --content-type=application/x-ndjson "$local_dir"/* "$folder/" >/dev/null
files=()
while read -r rel; do
  [ -n "$rel" ] || continue
  files+=("$folder/$rel")
done < <(cd "$local_dir" && find . -type f -name 'data-*.json' | sed 's|^\./||' | sort)
[ "${#files[@]}" -gt 0 ] || die "the export wrote no data file"
echo "  ${#files[@]} file(s) in $(cd "$local_dir" && find . -mindepth 3 -maxdepth 3 -type d | wc -l) date folder(s)"
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
