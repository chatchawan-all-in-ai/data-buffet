#!/usr/bin/env bash
# GCP setup of the Pub/Sub export; inventory and contract: document/project_wiki/cdc-process/process.md.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน A). Idempotent: every step checks or
# re-applies its resource, so re-running after a fix or after adding an export table is safe.
# Every grant is the narrowest that works; a rerun also removes the wider grants older
# versions of this script made, so only the narrow ones remain.
#
# What it builds: the publisher image (Cloud Build -> Artifact Registry), two Cloud Run jobs
# (check: 1 task, started by Cloud Scheduler every 5 minutes; send: SEND_TASKS tasks in parallel),
# the topics + dead-letter topics, one BigQuery-type "record" subscription per topic, the
# staging dataset, the snapshot bucket and the least-privilege grants of every identity.
#
# Prerequisites (the script stops with a message when one is missing):
#   * tag pub_sub already run from Dataform release `production` (creates
#     process_dataset.mart_export_config / mart_sent_state and the pub_sub export views);
#   * Secret Manager secret slack-datamart-dataform holds the Slack incoming webhook URL;
#   * Artifact Registry repository cloud-run-source-deploy exists in the job region;
#   * gcloud + bq logged in as a project owner (IAM, Cloud Run, Scheduler, Pub/Sub admin);
#   * curl (the Dataform repository IAM policy goes through the REST API).
#
# Usage: bash pubsub/scripts/setup.sh [--enable-scheduler]
#   --enable-scheduler  resume the Cloud Scheduler job (a new job is created PAUSED so the cutover
#                       from the old Cloud Workflows sender is a deliberate step)
#        bash pubsub/scripts/setup.sh --cleanup-old
#   --cleanup-old       ONLY the removal of the old Cloud Workflows sender (Scheduler job, workflow,
#                       custom role + binding, logging.logWriter, Workflows APIs). Never part of a
#                       normal run; run it after the new sender has been verified.
set -euo pipefail

PROJECT=databuffet-nonprd
REGION=us-central1                # Cloud Run jobs, Cloud Build, Cloud Scheduler
CHECK_JOB=datamart-publish-check
SEND_JOB=datamart-publish-send
SEND_TASKS=5                      # tasks of the send job = parallelism (each takes the next group)
SCHEDULER_JOB=datamart-publish-check-every-5m
SCHEDULE='*/5 * * * *'
TRIGGER_SA_NAME=datamart-publish-trigger   # Cloud Scheduler identity: run.invoker on the check job only
PUBLISHER_SA_NAME=datamart-publisher       # runs the send job
CHECKER_SA_NAME=datamart-publish-checker   # runs the check job
SLACK_SECRET=slack-datamart-dataform
BQ_DATASET=process_dataset
DATAFORM_LOCATION=us-central1
DATAFORM_REPO=data-buffet
# Image: the existing Artifact Registry repository of Cloud Run deployments (no new repository,
# no new IAM); the tag is a hash of the staged files, so unchanged code is not rebuilt.
AR_REPO=cloud-run-source-deploy
IMAGE_NAME=datamart-publisher
# Staging (diff result per table, 1-day table expiration) and the record of what Pub/Sub accepted
# (one table written by every record subscription, partitioned by publish_time).
STAGING_DATASET=pubsub_staging
RECORD_DATASET=pubsub_record
RECORD_TABLE=messages
RECORD_RETENTION_DAYS=14
RECORD_SUB_PREFIX=rec.datamart.
# Project custom role holding only the permissions the publisher identities use on Dataform.
DATAFORM_ROLE_ID=datamartPublishDataformReader
DATAFORM_ROLE_PERMISSIONS=dataform.workflowInvocations.list,dataform.workflowInvocations.query
# First-load files (export-snapshot.sh): one bucket in the location of the BigQuery dataset the
# export views live in (EXPORT DATA writes only there); add-consumer.sh grants each team SA
# this role on its own folder <team>/ only.
SNAPSHOT_BUCKET=databuffet-nonprd-datamart-snapshot
SNAPSHOT_LOCATION=us-central1
EXPORT_DATASET=pub_sub
SNAPSHOT_GET_ROLE_ID=datamartSnapshotGet
SNAPSHOT_GET_ROLE_PERMISSIONS=storage.objects.get
# The old Cloud Workflows sender, removed only by --cleanup-old.
OLD_REGION=asia-southeast1
OLD_WORKFLOW=datamart-publish
OLD_SCHEDULER_JOB=datamart-publish-every-5m
OLD_TRIGGER_ROLE_ID=datamartPublishTrigger

enable_scheduler=0
cleanup_old=0
for arg in "$@"; do
  case "$arg" in
    --enable-scheduler) enable_scheduler=1 ;;
    --cleanup-old) cleanup_old=1 ;;
    *) printf 'setup.sh: unknown argument %s\n' "$arg" >&2; exit 1 ;;
  esac
done
[ "$enable_scheduler$cleanup_old" != 11 ] || { echo "setup.sh: --enable-scheduler and --cleanup-old do not go together" >&2; exit 1; }

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pubsub_dir="$(cd "$here/.." && pwd)"
repo_root="$(cd "$here/../.." && pwd)"
# The single copy of the export config: Dataform requires it from includes/ (a path outside
# includes/ cannot be shown to compile in the Dataform release), so the scripts read it there.
config_json="$repo_root/includes/controller/mart-export-config.json"

trigger_sa="$TRIGGER_SA_NAME@$PROJECT.iam.gserviceaccount.com"
publisher_sa="$PUBLISHER_SA_NAME@$PROJECT.iam.gserviceaccount.com"
checker_sa="$CHECKER_SA_NAME@$PROJECT.iam.gserviceaccount.com"

log() { printf '\n== %s\n' "$*"; }
die() { printf 'setup.sh: %s\n' "$*" >&2; exit 1; }

pick_python() {
  local py
  for py in python3 python py; do
    if command -v "$py" >/dev/null 2>&1 && "$py" --version >/dev/null 2>&1; then
      echo "$py"
      return
    fi
  done
  die "python3/python not found (needed to read $config_json)"
}

# table_name<TAB>source_view<TAB>topic<TAB>source tables (space separated) for every export table
# in the config JSON; an entry without task_group or source_tables stops the script.
read_export_tables() {
  "$1" - "$config_json" <<'PY'
import json, sys
for t in json.load(open(sys.argv[1], encoding="utf-8"))["tables"]:
    if not t.get("task_group"):
        sys.exit(f"setup.sh: {t['table_name']} has no task_group in the config JSON")
    if not t.get("source_tables"):
        sys.exit(f"setup.sh: {t['table_name']} has no source_tables in the config JSON")
    print(f"{t['table_name']}\t{t['source_view']}\t{t['topic']}\t{' '.join(t['source_tables'])}")
PY
}

bq_table_exists() { bq --project_id="$PROJECT" show "$PROJECT:$1" >/dev/null 2>&1; }

grant_bq_to() { # <member> <dataset.table> <role>
  bq --project_id="$PROJECT" add-iam-policy-binding \
    --member="$1" --role="$3" "$PROJECT:$2" >/dev/null
  echo "  $3 on $2 for $1"
}

grant_bq() { # <dataset.table> <role>   (the publisher)
  grant_bq_to "serviceAccount:$publisher_sa" "$1" "$2"
}

# Dataset-level WRITER (= bigquery.dataEditor) for a service account, through the dataset access list.
grant_dataset_writer() { # <dataset> <service account email>
  local dataset_json
  dataset_json="$(mktemp)"
  bq --project_id="$PROJECT" show --format=prettyjson "$PROJECT:$1" |
    "$python_bin" -c '
import json, sys
dataset = json.load(sys.stdin)
entry = {"role": "WRITER", "userByEmail": sys.argv[1]}
access = dataset.setdefault("access", [])
if entry not in access:
    access.append(entry)
    print(json.dumps(dataset))
' "$2" > "$dataset_json"
  if [ -s "$dataset_json" ]; then
    bq --project_id="$PROJECT" update --source="$dataset_json" "$PROJECT:$1" >/dev/null
  fi
  rm -f "$dataset_json"
  echo "  WRITER (bigquery.dataEditor) on dataset $1 for $2"
}

grant_project() { # <member> <role>
  gcloud projects add-iam-policy-binding "$PROJECT" --member="$1" --role="$2" --condition=None >/dev/null
  echo "  $2 on project for $1"
}

grant_job() { # <job> <member> <role>
  gcloud run jobs add-iam-policy-binding "$1" --project="$PROJECT" --region="$REGION" \
    --member="$2" --role="$3" >/dev/null
  echo "  $3 on job $1 for $2"
}

# Succeeds when the IAM policy JSON on stdin binds <member> to <role>.
policy_has() { # <member> <role>
  "$python_bin" -c '
import json, sys
policy = json.load(sys.stdin)
member, role = sys.argv[1], sys.argv[2]
sys.exit(0 if any(b["role"] == role and member in b.get("members", []) for b in policy.get("bindings", [])) else 1)
' "$1" "$2"
}

# Superseded grants: removed when present, no error when already gone.
revoke_project() { # <member> <role>
  local policy
  policy="$(gcloud projects get-iam-policy "$PROJECT" --format=json)"
  if policy_has "$1" "$2" <<<"$policy"; then
    gcloud projects remove-iam-policy-binding "$PROJECT" --member="$1" --role="$2" --all >/dev/null
    echo "  removed $2 on project from $1"
  fi
}

revoke_bq() { # <dataset.table> <role>
  local policy
  policy="$(bq --project_id="$PROJECT" get-iam-policy --format=prettyjson "$PROJECT:$1")"
  if policy_has "serviceAccount:$publisher_sa" "$2" <<<"$policy"; then
    bq --project_id="$PROJECT" remove-iam-policy-binding \
      --member="serviceAccount:$publisher_sa" --role="$2" "$PROJECT:$1" >/dev/null
    echo "  removed $2 on $1"
  fi
}

ensure_custom_role() { # <role id> <title> <comma-separated permissions>
  local deleted
  if deleted="$(gcloud iam roles describe "$1" --project="$PROJECT" --format='value(deleted)' 2>/dev/null)"; then
    [ "$deleted" != True ] || gcloud iam roles undelete "$1" --project="$PROJECT" >/dev/null
    gcloud iam roles update "$1" --project="$PROJECT" --title="$2" \
      --permissions="$3" --stage=GA --quiet >/dev/null
  else
    gcloud iam roles create "$1" --project="$PROJECT" --title="$2" \
      --permissions="$3" --stage=GA >/dev/null
  fi
  echo "  custom role $1 = $3"
}

# gcloud has no Dataform commands, so the repository policy goes through the Dataform REST API.
grant_dataform_repo() { # <member> <role>
  local url auth policy request
  url="https://dataform.googleapis.com/v1/projects/$PROJECT/locations/$DATAFORM_LOCATION/repositories/$DATAFORM_REPO"
  auth="Authorization: Bearer $(gcloud auth print-access-token)"
  policy="$(curl -fsS -H "$auth" "$url:getIamPolicy")"
  request="$("$python_bin" -c '
import json, sys
policy = json.load(sys.stdin)
member, role = sys.argv[1], sys.argv[2]
bindings = policy.setdefault("bindings", [])
binding = next((b for b in bindings if b["role"] == role and "condition" not in b), None)
if binding is None:
    bindings.append({"role": role, "members": [member]})
elif member not in binding["members"]:
    binding["members"].append(member)
print(json.dumps({"policy": policy}))
' "$1" "$2" <<<"$policy")"
  curl -fsS -X POST -H "$auth" -H 'Content-Type: application/json' --data-binary @- \
    "$url:setIamPolicy" <<<"$request" >/dev/null
  echo "  $2 on Dataform repository $DATAFORM_REPO ($DATAFORM_LOCATION)"
}

# Adds pub_sub.<view> to the access list of <dataset>, so the view reads that dataset for its readers.
authorize_view() { # <dataset> <view>
  local dataset_json
  dataset_json="$(mktemp)"
  bq --project_id="$PROJECT" show --format=prettyjson "$PROJECT:$1" |
    "$python_bin" -c '
import json, sys
dataset = json.load(sys.stdin)
view = {"projectId": sys.argv[1], "datasetId": "pub_sub", "tableId": sys.argv[2]}
access = dataset.setdefault("access", [])
if all(a.get("view") != view for a in access):
    access.append({"view": view})
    print(json.dumps(dataset))
' "$PROJECT" "$2" > "$dataset_json"
  if [ -s "$dataset_json" ]; then
    bq --project_id="$PROJECT" update --source="$dataset_json" "$PROJECT:$1" >/dev/null
  fi
  rm -f "$dataset_json"
  echo "  pub_sub.$2 authorized on dataset $1"
}

ensure_topic() {
  gcloud pubsub topics describe "$1" --project="$PROJECT" >/dev/null 2>&1 ||
    gcloud pubsub topics create "$1" --project="$PROJECT"
}

ensure_sa() { # <name> <display name>
  gcloud iam service-accounts describe "$1@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" >/dev/null 2>&1 ||
    gcloud iam service-accounts create "$1" --project="$PROJECT" --display-name="$2"
}

ensure_dataset() { # <dataset> [bq flags...]
  local dataset="$1"
  shift
  if bq_table_exists "$dataset"; then
    [ $# -eq 0 ] || bq --project_id="$PROJECT" update "$@" "$PROJECT:$dataset" >/dev/null
    echo "  dataset $dataset exists, settings re-applied"
  else
    bq --project_id="$PROJECT" mk --dataset --location="$REGION" "$@" "$PROJECT:$dataset" >/dev/null
    echo "  dataset $dataset created ($REGION)"
  fi
}

# Removes the old Cloud Workflows sender and everything that belonged only to it. Only reached by
# --cleanup-old, after the new sender has run a night: the old Scheduler job goes first so the
# workflow is no longer started, then the workflow, then the grants and APIs only it used.
cleanup_old_sender() {
  local others
  log "Old sender: Scheduler job $OLD_SCHEDULER_JOB ($OLD_REGION)"
  if gcloud scheduler jobs describe "$OLD_SCHEDULER_JOB" --project="$PROJECT" --location="$OLD_REGION" >/dev/null 2>&1; then
    gcloud scheduler jobs delete "$OLD_SCHEDULER_JOB" --project="$PROJECT" --location="$OLD_REGION" --quiet
  else
    echo "  already gone"
  fi
  log "Old sender: workflow $OLD_WORKFLOW ($OLD_REGION)"
  if gcloud workflows describe "$OLD_WORKFLOW" --project="$PROJECT" --location="$OLD_REGION" >/dev/null 2>&1; then
    gcloud workflows delete "$OLD_WORKFLOW" --project="$PROJECT" --location="$OLD_REGION" --quiet
  else
    echo "  already gone"
  fi
  log "Old sender: custom role $OLD_TRIGGER_ROLE_ID and its binding"
  revoke_project "serviceAccount:$trigger_sa" "projects/$PROJECT/roles/$OLD_TRIGGER_ROLE_ID"
  revoke_project "serviceAccount:$trigger_sa" roles/workflows.invoker
  if gcloud iam roles describe "$OLD_TRIGGER_ROLE_ID" --project="$PROJECT" --format='value(name)' >/dev/null 2>&1; then
    gcloud iam roles delete "$OLD_TRIGGER_ROLE_ID" --project="$PROJECT" --quiet >/dev/null
    echo "  custom role $OLD_TRIGGER_ROLE_ID deleted"
  fi
  log "Old sender: logging.logWriter of $publisher_sa (the Cloud Run jobs log to stdout)"
  revoke_project "serviceAccount:$publisher_sa" roles/logging.logWriter
  log "Old sender: Workflows APIs"
  others="$(curl -fsS -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    "https://workflows.googleapis.com/v1/projects/$PROJECT/locations/-/workflows" |
    "$python_bin" -c 'import json, sys; print(len(json.load(sys.stdin).get("workflows", [])))' 2>/dev/null || echo unknown)"
  if [ "$others" = 0 ]; then
    gcloud services disable --project="$PROJECT" workflowexecutions.googleapis.com workflows.googleapis.com
    echo "  Workflows APIs disabled (no workflow left in the project)"
  else
    echo "  Workflows APIs left enabled: $others workflow(s) still exist in the project (or the list failed)"
  fi
  log "Old sender removed"
}

log "Checking prerequisites"
command -v gcloud >/dev/null || die "gcloud not found"
command -v bq >/dev/null || die "bq not found"
command -v curl >/dev/null || die "curl not found (needed for the Dataform repository policy and the Workflows list)"
python_bin="$(pick_python)"
if [ "$cleanup_old" = 1 ]; then
  cleanup_old_sender
  exit 0
fi
[ -f "$pubsub_dir/publisher/main.py" ] && [ -f "$pubsub_dir/publisher/Dockerfile" ] && [ -f "$pubsub_dir/sql/diff.sql" ] ||
  die "missing pubsub/publisher or pubsub/sql/diff.sql next to this script"
export_tables="$(read_export_tables "$python_bin")"
[ -n "$export_tables" ] || die "no tables in $config_json"
for t in "$BQ_DATASET.mart_export_config" "$BQ_DATASET.mart_sent_state"; do
  bq_table_exists "$t" || die "$PROJECT:$t not found - run tag pub_sub from Dataform release production first"
done
# The publisher reads mart_export_config by column name; task_group comes from the Dataform release.
bq --project_id="$PROJECT" show --schema --format=json "$PROJECT:$BQ_DATASET.mart_export_config" |
  "$python_bin" -c 'import json, sys; sys.exit(0 if {"task_group", "group_claimed_at", "recovery_started_at", "recovery_until"} <= {f["name"] for f in json.load(sys.stdin)} else 1)' ||
  die "$BQ_DATASET.mart_export_config is missing publisher ownership/recovery columns - run tag pub_sub from Dataform release production first"
missing_group="$(bq --project_id="$PROJECT" --location="$REGION" --format=csv query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`$PROJECT.$BQ_DATASET.mart_export_config\` WHERE task_group IS NULL" | tail -n 1)"
[ "$missing_group" = 0 ] ||
  die "$missing_group row(s) of $BQ_DATASET.mart_export_config have no task_group - run tag pub_sub from Dataform release production first"
declare -A SOURCE_TABLES=()
while IFS=$'\t' read -r table_name source_view _topic source_tables; do
  bq_table_exists "pub_sub.$source_view" || die "view pub_sub.$source_view not found - run tag pub_sub first"
  SOURCE_TABLES["$table_name"]="$source_tables"
done <<< "$export_tables"
gcloud secrets describe "$SLACK_SECRET" --project="$PROJECT" >/dev/null 2>&1 ||
  die "secret $SLACK_SECRET not found - store the Slack webhook URL in it first"
gcloud artifacts repositories describe "$AR_REPO" --project="$PROJECT" --location="$REGION" >/dev/null 2>&1 ||
  die "Artifact Registry repository $AR_REPO not found in $REGION"
export_location="$(bq --project_id="$PROJECT" show --format=prettyjson "$PROJECT:$EXPORT_DATASET" |
  "$python_bin" -c 'import json, sys; print(json.load(sys.stdin)["location"].lower())')"
[ "$export_location" = "$SNAPSHOT_LOCATION" ] ||
  die "dataset $EXPORT_DATASET is in $export_location but SNAPSHOT_LOCATION is $SNAPSHOT_LOCATION; EXPORT DATA needs them to match"
project_number="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
pubsub_agent="service-$project_number@gcp-sa-pubsub.iam.gserviceaccount.com"

log "Enabling APIs"
gcloud services enable --project="$PROJECT" \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com pubsub.googleapis.com secretmanager.googleapis.com \
  dataform.googleapis.com bigquery.googleapis.com bigquerystorage.googleapis.com \
  monitoring.googleapis.com storage.googleapis.com

log "Service accounts (keyless - never create keys)"
ensure_sa "$TRIGGER_SA_NAME" "Cloud Scheduler -> Cloud Run job $CHECK_JOB"
ensure_sa "$CHECKER_SA_NAME" "Cloud Run job $CHECK_JOB runner"
ensure_sa "$PUBLISHER_SA_NAME" "Cloud Run job $SEND_JOB runner"

log "Topics and dead-letter topics"
while IFS=$'\t' read -r _table_name _source_view topic _source_tables; do
  dlq_topic="$topic-dead-letter"
  ensure_topic "$topic"
  ensure_topic "$dlq_topic"
  # Dead letters of every consumer subscription on $topic (add-consumer.sh); the Pub/Sub service
  # agent forwards them, so it publishes here.
  gcloud pubsub topics add-iam-policy-binding "$dlq_topic" --project="$PROJECT" \
    --member="serviceAccount:$pubsub_agent" --role=roles/pubsub.publisher >/dev/null
  # Publisher: publish to this topic only.
  gcloud pubsub topics add-iam-policy-binding "$topic" --project="$PROJECT" \
    --member="serviceAccount:$publisher_sa" --role=roles/pubsub.publisher >/dev/null
  echo "  $topic (+ $dlq_topic)"
done <<< "$export_tables"

log "Staging dataset $STAGING_DATASET (tables expire after 1 day) and record table $RECORD_DATASET.$RECORD_TABLE"
ensure_dataset "$STAGING_DATASET" --default_table_expiration=86400
ensure_dataset "$RECORD_DATASET"
record_retention_seconds=$((RECORD_RETENTION_DAYS * 86400))
if bq_table_exists "$RECORD_DATASET.$RECORD_TABLE"; then
  bq --project_id="$PROJECT" update --time_partitioning_expiration="$record_retention_seconds" \
    --require_partition_filter "$PROJECT:$RECORD_DATASET.$RECORD_TABLE" >/dev/null
  echo "  $RECORD_DATASET.$RECORD_TABLE exists, retention $RECORD_RETENTION_DAYS days re-applied"
else
  # Columns written by a BigQuery subscription with "write metadata" and no topic schema.
  bq --project_id="$PROJECT" mk --table \
    --time_partitioning_type=DAY --time_partitioning_field=publish_time \
    --time_partitioning_expiration="$record_retention_seconds" --require_partition_filter \
    --description="What Pub/Sub accepted per export topic (record subscriptions $RECORD_SUB_PREFIX<topic>); read by the publisher to recover after a crash" \
    "$PROJECT:$RECORD_DATASET.$RECORD_TABLE" \
    subscription_name:STRING,message_id:STRING,publish_time:TIMESTAMP,data:STRING,attributes:STRING >/dev/null
  echo "  $RECORD_DATASET.$RECORD_TABLE created (partitioned by publish_time, kept $RECORD_RETENTION_DAYS days)"
fi
# The Pub/Sub service agent writes the table.
grant_bq_to "serviceAccount:$pubsub_agent" "$RECORD_DATASET.$RECORD_TABLE" roles/bigquery.dataEditor

log "Record subscriptions $RECORD_SUB_PREFIX<topic> (BigQuery type, no dead-letter)"
# Created before the new sender publishes its first message: a BigQuery subscription records only
# messages published after it exists. No dead-letter topic, so a message the table refuses stays
# in the subscription backlog instead of leaving the record.
while IFS=$'\t' read -r _table_name _source_view topic _source_tables; do
  record_sub="$RECORD_SUB_PREFIX$topic"
  record_flags=(
    --project="$PROJECT"
    --bigquery-table="$PROJECT:$RECORD_DATASET.$RECORD_TABLE" --write-metadata
    --expiration-period=never
  )
  if gcloud pubsub subscriptions describe "$record_sub" --project="$PROJECT" >/dev/null 2>&1; then
    gcloud pubsub subscriptions update "$record_sub" "${record_flags[@]}" >/dev/null
    echo "  $record_sub exists, settings re-applied"
  else
    gcloud pubsub subscriptions create "$record_sub" --topic="$topic" "${record_flags[@]}" >/dev/null
    echo "  $record_sub created"
  fi
  gcloud pubsub subscriptions add-iam-policy-binding "$record_sub" --project="$PROJECT" \
    --member="serviceAccount:$publisher_sa" --role=roles/pubsub.viewer >/dev/null
done <<< "$export_tables"

log "Least-privilege roles for $publisher_sa (send job)"
# Project level only for roles that exist only there: run BigQuery jobs, open Storage Read sessions,
# read the backlog metric of the record subscriptions. The jobs log to stdout, no logWriter.
for role in roles/bigquery.jobUser roles/bigquery.readSessionUser roles/monitoring.viewer; do
  grant_project "serviceAccount:$publisher_sa" "$role"
done
# The publisher lists workflow invocations of the repository and queries their actions, nothing
# else of Dataform: a custom role with those two permissions, granted on the repository only.
ensure_custom_role "$DATAFORM_ROLE_ID" "Data Mart publish: read Dataform invocations" "$DATAFORM_ROLE_PERMISSIONS"
grant_dataform_repo "serviceAccount:$publisher_sa" "projects/$PROJECT/roles/$DATAFORM_ROLE_ID"
revoke_project "serviceAccount:$publisher_sa" roles/dataform.viewer
grant_bq "$BQ_DATASET.mart_export_config" roles/bigquery.dataEditor
grant_bq "$BQ_DATASET.mart_sent_state" roles/bigquery.dataEditor
grant_dataset_writer "$STAGING_DATASET" "$publisher_sa"
grant_bq "$RECORD_DATASET.$RECORD_TABLE" roles/bigquery.dataViewer
# Read on the export view only; the view is authorized on its base tables' datasets.
declare -A view_datasets=()
while IFS=$'\t' read -r table_name source_view _topic _source_tables; do
  grant_bq "pub_sub.$source_view" roles/bigquery.dataViewer
  for base in ${SOURCE_TABLES[$table_name]}; do
    view_datasets["${base%%.*} $source_view"]=1
  done
done <<< "$export_tables"
for dataset_view in "${!view_datasets[@]}"; do
  authorize_view "${dataset_view% *}" "${dataset_view#* }"
done
while IFS=$'\t' read -r table_name _source_view _topic _source_tables; do
  for base in ${SOURCE_TABLES[$table_name]}; do
    # Routines (function_dataset) have no table IAM policy: only tables and views carry an old grant to remove.
    bq_table_exists "$base" || continue
    revoke_bq "$base" roles/bigquery.dataViewer
  done
done <<< "$export_tables"
gcloud secrets add-iam-policy-binding "$SLACK_SECRET" --project="$PROJECT" \
  --member="serviceAccount:$publisher_sa" --role=roles/secretmanager.secretAccessor >/dev/null
echo "  roles/secretmanager.secretAccessor on secret $SLACK_SECRET"

log "Least-privilege roles for $checker_sa (check job)"
# It reads and advances mart_export_config, lists Dataform invocations, starts and looks at the send job.
grant_project "serviceAccount:$checker_sa" roles/bigquery.jobUser
grant_dataform_repo "serviceAccount:$checker_sa" "projects/$PROJECT/roles/$DATAFORM_ROLE_ID"
grant_bq_to "serviceAccount:$checker_sa" "$BQ_DATASET.mart_export_config" roles/bigquery.dataEditor
gcloud secrets add-iam-policy-binding "$SLACK_SECRET" --project="$PROJECT" \
  --member="serviceAccount:$checker_sa" --role=roles/secretmanager.secretAccessor >/dev/null
echo "  roles/secretmanager.secretAccessor on secret $SLACK_SECRET"

log "Publisher image ($AR_REPO in $REGION)"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/publisher" "$stage/sql" "$stage/config"
cp "$pubsub_dir/publisher/main.py" "$pubsub_dir/publisher/requirements.txt" "$pubsub_dir/publisher/Dockerfile" "$stage/publisher/"
cp "$pubsub_dir/sql/diff.sql" "$stage/sql/"
# The group order of the send tasks comes from this file (the single copy stays in includes/).
cp "$config_json" "$stage/config/"
image_tag="$(cd "$stage" && find . -type f | LC_ALL=C sort | xargs sha256sum | sha256sum | cut -c1-12)"
image_uri="$REGION-docker.pkg.dev/$PROJECT/$AR_REPO/$IMAGE_NAME:$image_tag"
if gcloud artifacts docker images describe "$image_uri" --project="$PROJECT" >/dev/null 2>&1; then
  echo "  $image_uri exists, not rebuilt"
else
  cat > "$stage/cloudbuild.yaml" <<YAML
steps:
  - name: gcr.io/cloud-builders/docker
    args: ['build', '-t', '$image_uri', '-f', 'publisher/Dockerfile', '.']
images: ['$image_uri']
YAML
  gcloud builds submit "$stage" --project="$PROJECT" --region="$REGION" --config="$stage/cloudbuild.yaml"
fi

log "Cloud Run jobs ($REGION)"
gcloud run jobs deploy "$SEND_JOB" --project="$PROJECT" --region="$REGION" --image="$image_uri" \
  --service-account="$publisher_sa" --tasks="$SEND_TASKS" --parallelism="$SEND_TASKS" \
  --task-timeout=30m --max-retries=0 --cpu=2 --memory=4Gi --args=send \
  --set-env-vars="PROJECT_ID=$PROJECT"
gcloud run jobs deploy "$CHECK_JOB" --project="$PROJECT" --region="$REGION" --image="$image_uri" \
  --service-account="$checker_sa" --tasks=1 --parallelism=1 \
  --task-timeout=5m --max-retries=0 --cpu=1 --memory=512Mi --args=check \
  --set-env-vars="PROJECT_ID=$PROJECT,SEND_JOB=$SEND_JOB,RUN_REGION=$REGION"
# The check job starts the send job (run.invoker) and looks whether an execution is still running (run.viewer).
grant_job "$SEND_JOB" "serviceAccount:$checker_sa" roles/run.invoker
grant_job "$SEND_JOB" "serviceAccount:$checker_sa" roles/run.viewer
# Cloud Scheduler starts the check job and nothing else.
grant_job "$CHECK_JOB" "serviceAccount:$trigger_sa" roles/run.invoker

log "Scheduler job $SCHEDULER_JOB ($SCHEDULE, $REGION)"
scheduler_flags=(
  --project="$PROJECT" --location="$REGION"
  --schedule="$SCHEDULE" --time-zone=Asia/Bangkok
  --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT/jobs/$CHECK_JOB:run"
  --http-method=POST
  --oauth-service-account-email="$trigger_sa"
  --oauth-token-scope=https://www.googleapis.com/auth/cloud-platform
)
if gcloud scheduler jobs describe "$SCHEDULER_JOB" --project="$PROJECT" --location="$REGION" >/dev/null 2>&1; then
  gcloud scheduler jobs update http "$SCHEDULER_JOB" "${scheduler_flags[@]}"
  echo "  updated (state unchanged)"
else
  gcloud scheduler jobs create http "$SCHEDULER_JOB" "${scheduler_flags[@]}"
  # Paused until the old Cloud Workflows Scheduler job is out of the way (--enable-scheduler).
  gcloud scheduler jobs pause "$SCHEDULER_JOB" --project="$PROJECT" --location="$REGION" >/dev/null
  echo "  created PAUSED"
fi
if [ "$enable_scheduler" = 1 ]; then
  gcloud scheduler jobs resume "$SCHEDULER_JOB" --project="$PROJECT" --location="$REGION" >/dev/null
  echo "  resumed"
fi

log "Snapshot bucket gs://$SNAPSHOT_BUCKET ($SNAPSHOT_LOCATION)"
if bucket_location="$(gcloud storage buckets describe "gs://$SNAPSHOT_BUCKET" --format='value(location)' 2>/dev/null)"; then
  [ "${bucket_location,,}" = "$SNAPSHOT_LOCATION" ] ||
    die "gs://$SNAPSHOT_BUCKET is in $bucket_location, expected $SNAPSHOT_LOCATION"
  gcloud storage buckets update "gs://$SNAPSHOT_BUCKET" \
    --uniform-bucket-level-access --public-access-prevention >/dev/null
  echo "  exists, settings re-applied"
else
  gcloud storage buckets create "gs://$SNAPSHOT_BUCKET" --project="$PROJECT" --location="$SNAPSHOT_LOCATION" \
    --uniform-bucket-level-access --public-access-prevention >/dev/null
  echo "  created (uniform bucket-level access, public access prevention enforced)"
fi
snapshot_policy="$(gcloud storage buckets get-iam-policy "gs://$SNAPSHOT_BUCKET" --format=json)"
snapshot_bindings="$("$python_bin" -c '
import json, sys
policy = json.load(sys.stdin)
members = {"projectViewer:" + sys.argv[1], "projectEditor:" + sys.argv[1]}
for role, member in sorted({(b["role"], m) for b in policy.get("bindings", [])
                            for m in b.get("members", []) if m in members}):
    print(role, member, sep="\t")
' "$PROJECT" <<<"$snapshot_policy")"
while IFS=$'\t' read -r role member; do
  [ -n "$role" ] || continue
  gcloud storage buckets remove-iam-policy-binding "gs://$SNAPSHOT_BUCKET" \
    --member="$member" --role="$role" --all >/dev/null
  echo "  removed $role on gs://$SNAPSHOT_BUCKET from $member"
done <<< "$snapshot_bindings"
ensure_custom_role "$SNAPSHOT_GET_ROLE_ID" "Data Mart snapshot: read files" "$SNAPSHOT_GET_ROLE_PERMISSIONS"

log "Done. The Scheduler job is PAUSED unless --enable-scheduler was given. Verify the first run: document/how-to/setup-pubsub-export.md (A4)"
