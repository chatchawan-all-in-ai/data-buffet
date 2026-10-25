#!/usr/bin/env bash
# GCP setup of the Pub/Sub export pilot (dim_company) in databuffet-nonprd.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน A). Idempotent: every step checks or
# re-applies its resource, so re-running after a fix or after adding an export table is safe.
#
# Prerequisites (the script stops with a message when one is missing):
#   * tag pub_sub already run from Dataform release `production` (creates
#     process_dataset.mart_export_config / mart_sent_state and the pub_sub export views);
#   * Secret Manager secret slack-datamart-dataform holds the Slack incoming webhook URL;
#   * gcloud + bq logged in as a project owner (IAM, Workflows, Scheduler, Pub/Sub admin).
#
# Usage: bash infra/pubsub/setup.sh
set -euo pipefail

PROJECT=databuffet-nonprd
REGION=asia-southeast1            # Workflows + Cloud Scheduler
WORKFLOW=datamart-publish
SCHEDULER_JOB=datamart-publish-every-5m
SCHEDULE='*/5 * * * *'
TRIGGER_SA_NAME=datamart-publish-trigger
PUBLISHER_SA_NAME=datamart-publisher
SLACK_SECRET=slack-datamart-dataform
BQ_DATASET=process_dataset
TEST_MAX_DELIVERY_ATTEMPTS=5

# Base tables each export view reads: the publisher needs read on them as well as on the view.
# Add a line when a new table is added to includes/controller/mart-export-config.json.
declare -A SOURCE_TABLES=(
  [dim_company]="dimension_table.dim_company"
)

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$here/../.." && pwd)"
config_json="$repo_root/includes/controller/mart-export-config.json"
workflow_yaml="$here/datamart-publish.workflows.yaml"

trigger_sa="$TRIGGER_SA_NAME@$PROJECT.iam.gserviceaccount.com"
publisher_sa="$PUBLISHER_SA_NAME@$PROJECT.iam.gserviceaccount.com"

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

# table_name<TAB>source_view<TAB>topic for every export table in the config JSON.
read_export_tables() {
  "$1" - "$config_json" <<'PY'
import json, sys
for t in json.load(open(sys.argv[1], encoding="utf-8"))["tables"]:
    print(f"{t['table_name']}\t{t['source_view']}\t{t['topic']}")
PY
}

bq_table_exists() { bq --project_id="$PROJECT" show "$PROJECT:$1" >/dev/null 2>&1; }

grant_bq() { # <dataset.table> <role>
  bq --project_id="$PROJECT" add-iam-policy-binding \
    --member="serviceAccount:$publisher_sa" --role="$2" "$PROJECT:$1" >/dev/null
  echo "  $2 on $1"
}

ensure_topic() {
  gcloud pubsub topics describe "$1" --project="$PROJECT" >/dev/null 2>&1 ||
    gcloud pubsub topics create "$1" --project="$PROJECT"
}

ensure_sa() { # <name> <display name>
  gcloud iam service-accounts describe "$1@$PROJECT.iam.gserviceaccount.com" --project="$PROJECT" >/dev/null 2>&1 ||
    gcloud iam service-accounts create "$1" --project="$PROJECT" --display-name="$2"
}

log "Checking prerequisites"
command -v gcloud >/dev/null || die "gcloud not found"
command -v bq >/dev/null || die "bq not found"
[ -f "$workflow_yaml" ] || die "missing $workflow_yaml"
python_bin="$(pick_python)"
export_tables="$(read_export_tables "$python_bin")"
[ -n "$export_tables" ] || die "no tables in $config_json"
for t in "$BQ_DATASET.mart_export_config" "$BQ_DATASET.mart_sent_state"; do
  bq_table_exists "$t" || die "$PROJECT:$t not found - run tag pub_sub from Dataform release production first"
done
while IFS=$'\t' read -r table_name source_view _topic; do
  bq_table_exists "pub_sub.$source_view" || die "view pub_sub.$source_view not found - run tag pub_sub first"
  [ -n "${SOURCE_TABLES[$table_name]:-}" ] || die "SOURCE_TABLES has no entry for $table_name"
done <<< "$export_tables"
gcloud secrets describe "$SLACK_SECRET" --project="$PROJECT" >/dev/null 2>&1 ||
  die "secret $SLACK_SECRET not found - store the Slack webhook URL in it first"
project_number="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
pubsub_agent="service-$project_number@gcp-sa-pubsub.iam.gserviceaccount.com"

log "Enabling APIs"
gcloud services enable --project="$PROJECT" \
  workflows.googleapis.com workflowexecutions.googleapis.com cloudscheduler.googleapis.com \
  pubsub.googleapis.com secretmanager.googleapis.com dataform.googleapis.com bigquery.googleapis.com

log "Service accounts (keyless - never create keys)"
ensure_sa "$TRIGGER_SA_NAME" "Cloud Scheduler -> Workflows datamart-publish"
ensure_sa "$PUBLISHER_SA_NAME" "Workflows datamart-publish runner"

log "Topics and the test subscription (with dead-letter topic)"
while IFS=$'\t' read -r table_name _source_view topic; do
  dlq_topic="$topic-dead-letter"
  test_sub="sub-test-$table_name"
  ensure_topic "$topic"
  ensure_topic "$dlq_topic"
  # Holds dead letters so they can be read; a topic without a subscription drops them.
  gcloud pubsub subscriptions describe "$test_sub-dead-letter" --project="$PROJECT" >/dev/null 2>&1 ||
    gcloud pubsub subscriptions create "$test_sub-dead-letter" --project="$PROJECT" --topic="$dlq_topic" \
      --message-retention-duration=7d
  if gcloud pubsub subscriptions describe "$test_sub" --project="$PROJECT" >/dev/null 2>&1; then
    gcloud pubsub subscriptions update "$test_sub" --project="$PROJECT" \
      --dead-letter-topic="$dlq_topic" --max-delivery-attempts="$TEST_MAX_DELIVERY_ATTEMPTS"
  else
    gcloud pubsub subscriptions create "$test_sub" --project="$PROJECT" --topic="$topic" \
      --ack-deadline=60 --message-retention-duration=7d \
      --dead-letter-topic="$dlq_topic" --max-delivery-attempts="$TEST_MAX_DELIVERY_ATTEMPTS"
  fi
  # Pub/Sub service agent forwards undeliverable messages: publish on the DLQ, subscribe on the source sub.
  gcloud pubsub topics add-iam-policy-binding "$dlq_topic" --project="$PROJECT" \
    --member="serviceAccount:$pubsub_agent" --role=roles/pubsub.publisher >/dev/null
  gcloud pubsub subscriptions add-iam-policy-binding "$test_sub" --project="$PROJECT" \
    --member="serviceAccount:$pubsub_agent" --role=roles/pubsub.subscriber >/dev/null
  # Publisher: publish to this topic only.
  gcloud pubsub topics add-iam-policy-binding "$topic" --project="$PROJECT" \
    --member="serviceAccount:$publisher_sa" --role=roles/pubsub.publisher >/dev/null
  echo "  $topic (+ $dlq_topic), $test_sub"
done <<< "$export_tables"

log "Least-privilege roles for $publisher_sa"
for role in roles/dataform.viewer roles/bigquery.jobUser roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$publisher_sa" \
    --role="$role" --condition=None >/dev/null
  echo "  $role on project (read Dataform invocations / run BigQuery jobs / write workflow logs)"
done
grant_bq "$BQ_DATASET.mart_export_config" roles/bigquery.dataEditor
grant_bq "$BQ_DATASET.mart_sent_state" roles/bigquery.dataEditor
while IFS=$'\t' read -r table_name source_view _topic; do
  grant_bq "pub_sub.$source_view" roles/bigquery.dataViewer
  for base in ${SOURCE_TABLES[$table_name]}; do
    grant_bq "$base" roles/bigquery.dataViewer
  done
done <<< "$export_tables"
gcloud secrets add-iam-policy-binding "$SLACK_SECRET" --project="$PROJECT" \
  --member="serviceAccount:$publisher_sa" --role=roles/secretmanager.secretAccessor >/dev/null
echo "  roles/secretmanager.secretAccessor on secret $SLACK_SECRET"

log "Workflow $WORKFLOW ($REGION)"
gcloud workflows deploy "$WORKFLOW" --project="$PROJECT" --location="$REGION" \
  --source="$workflow_yaml" --service-account="$publisher_sa" \
  --description="Publish changed rows of Pub/Sub export tables (infra/pubsub in data-buffet)"
# Workflows has no per-workflow IAM, so the invoker role is project-wide; it is the trigger SA's only role.
gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$trigger_sa" \
  --role=roles/workflows.invoker --condition=None >/dev/null
echo "  roles/workflows.invoker on project for $trigger_sa (its only role)"

log "Scheduler job $SCHEDULER_JOB ($SCHEDULE)"
scheduler_flags=(
  --project="$PROJECT" --location="$REGION"
  --schedule="$SCHEDULE" --time-zone=Asia/Bangkok
  --uri="https://workflowexecutions.googleapis.com/v1/projects/$PROJECT/locations/$REGION/workflows/$WORKFLOW/executions"
  --http-method=POST --message-body='{}'
  --oauth-service-account-email="$trigger_sa"
  --oauth-token-scope=https://www.googleapis.com/auth/cloud-platform
)
if gcloud scheduler jobs describe "$SCHEDULER_JOB" --project="$PROJECT" --location="$REGION" >/dev/null 2>&1; then
  gcloud scheduler jobs update http "$SCHEDULER_JOB" "${scheduler_flags[@]}"
else
  gcloud scheduler jobs create http "$SCHEDULER_JOB" "${scheduler_flags[@]}"
fi

log "Done. Test with the pull subscription: document/how-to/setup-pubsub-export.md"
