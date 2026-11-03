#!/usr/bin/env bash
# GCP setup of the Pub/Sub export; inventory and contract: document/project_wiki/cdc-process/process.md.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน A). Idempotent: every step checks or
# re-applies its resource, so re-running after a fix or after adding an export table is safe.
# Every grant is the narrowest that works; a rerun also removes the wider grants older
# versions of this script made, so only the narrow ones remain.
#
# Prerequisites (the script stops with a message when one is missing):
#   * tag pub_sub already run from Dataform release `production` (creates
#     process_dataset.mart_export_config / mart_sent_state and the pub_sub export views);
#   * Secret Manager secret slack-datamart-dataform holds the Slack incoming webhook URL;
#   * gcloud + bq logged in as a project owner (IAM, Workflows, Scheduler, Pub/Sub admin);
#   * curl (the Dataform repository IAM policy goes through the REST API).
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
DATAFORM_LOCATION=us-central1
DATAFORM_REPO=data-buffet
# Project custom roles holding only the permissions each identity uses.
DATAFORM_ROLE_ID=datamartPublishDataformReader
DATAFORM_ROLE_PERMISSIONS=dataform.workflowInvocations.list,dataform.workflowInvocations.query
TRIGGER_ROLE_ID=datamartPublishTrigger
TRIGGER_ROLE_PERMISSIONS=workflows.executions.create
# First-load files (export-snapshot.sh): one bucket in the location of the BigQuery dataset the
# export views live in (EXPORT DATA writes only there); add-consumer.sh grants each team SA
# this role on its own folder <team>/ only.
SNAPSHOT_BUCKET=databuffet-nonprd-datamart-snapshot
SNAPSHOT_LOCATION=us-central1
EXPORT_DATASET=pub_sub
SNAPSHOT_GET_ROLE_ID=datamartSnapshotGet
SNAPSHOT_GET_ROLE_PERMISSIONS=storage.objects.get

# Base tables each export view reads: their datasets authorize the view, so the publisher
# reads only the view's columns and has no grant on the base tables.
# Add a line when a new table is added to includes/controller/mart-export-config.json.
declare -A SOURCE_TABLES=(
  [dim_company]="dimension_table.dim_company"
  # Commission sets for the TF team (ag01).
  [order]="validated_mac5.mih validated_mac5.mie validated_mac5.mil validated_mac5.stk"
  [invoice]="validated_mac5.mih validated_mac5.mie validated_mac5.mil validated_mac5.stk"
  [credit_note]="validated_mac5.mih validated_mac5.mil validated_mac5.stk validated_mac5.ar_s"
  [debit_note]="validated_mac5.mih validated_mac5.mil validated_mac5.stk validated_mac5.ar_s"
  [receipt]="validated_mac5.mir validated_mac5.mih validated_mac5.cql validated_mac5.chq validated_mac5.ar_s"
  [chqri]="validated_mac5.chq validated_mac5.cql"
  [status]="validated_mac5.ar_s"
  [company]="validated_mac5.deb"
  [sell]="validated_mac5.per"
  [warehouse]="validated_mac5.sto"
  [stk]="validated_mac5.stk"
  [company_source]="dimension_table.dim_company"
  # TA app org tables for the AI team (org sample 2026-11-02, one topic per app table).
  [org_levels]="org_center.org_center_unit"
  [org_units]="org_center.org_center_unit"
  [positions]="org_center.org_center_member"
  [employees]="org_center.org_center_person org_center.org_center_exception mds_dataset.mds_data_org_employee_mapping_center"
  [memberships]="org_center.org_center_member"
  [appointments]="org_center.org_center_member"
  [member_links]="org_center.org_center_link"
  [access_exceptions]="org_center.org_center_exception"
  [customer_ta_assignments]="org_center.org_center_customer_ta org_center.org_center_member"
  # AI team sample tables (2026-10-26 package, rls sample and dashboard display control): one topic per sample table.
  # The first object is the table or view the export view reads; the others are one object per upstream dataset
  # that view reads through, so the export view is authorized on every dataset of the chain.
  [dim_aging_rang]="dimension_table.dim_aging_rang"
  [dim_calendar]="dimension_table.dim_calendar"
  [dim_customer_segment]="dimension_table.dim_customer_segment"
  [dim_doctype]="dimension_table.dim_doctype"
  [dim_payment]="dimension_table.dim_payment"
  [dim_product_master_fc]="dimension_table.dim_product_master_fc"
  [dim_product_series]="dimension_table.dim_product_series"
  [dim_project]="dimension_table.dim_project"
  [dim_pump_information]="dimension_table.dim_pump_information"
  [dim_quotation]="dimension_table.dim_quotation"
  [dim_section_last]="dimension_table.dim_section_last"
  [dim_target_product_group_by_sale_dayofwork]="dimension_table.dim_target_product_group_by_sale_dayofwork"
  [view_dim_aging_history]="dimension_view.view_dim_aging_history dimension_table.dim_aging fact_table.fact_mir_vs"
  [view_dim_channel]="dimension_view.view_dim_channel dimension_table.dim_channel"
  [view_dim_company]="dimension_view.view_dim_company dimension_table.dim_company"
  [view_dim_customer]="dimension_view.view_dim_customer dimension_table.dim_customer mds_dataset.mds_data_customernickname_master"
  [view_dim_customer_report_info]="dimension_view.view_dim_customer_report_info dimension_table.dim_customer_report_info"
  [view_dim_invoice]="dimension_view.view_dim_invoice dimension_table.dim_aging function_dataset.clean_company_prefix mds_dataset.mds_data_crc_shop_name_rename validated_mac5.mec"
  [view_dim_order]="dimension_view.view_dim_order dimension_table.dim_order function_dataset.fn_order_type mds_dataset.mds_data_document_expire_rule_master validated_mac5.mih2"
  [view_dim_product_master]="dimension_view.view_dim_product_master dimension_table.dim_product_master"
  [view_dim_product_mkt]="dimension_view.view_dim_product_mkt dimension_table.dim_product_mkt"
  [view_dim_sale_representative_last]="dimension_view.view_dim_sale_representative_last dimension_table.dim_department_last"
  [fact_delivery]="fact_table.fact_delivery"
  [fact_order]="fact_table.fact_order"
  [fact_quotation]="fact_table.fact_quotation"
  [fact_transaction_delivery]="fact_table.fact_transaction_delivery"
  [view_fact_transcation]="fact_view.view_fact_transcation dimension_table.dim_aging dimension_view.view_dim_aging fact_table.fact_invoice function_dataset.clean_company_prefix mds_dataset.mds_data_crc_shop_name_rename onetime.mapping_invoice validated_mac5.deb"
  [mds_data_org_ols_center]="mds_dataset.mds_data_org_ols_center"
  [product_attribute]="onetime.Product_Attribute dimension_table.dim_company validated_mac5.stg validated_mastersku.product"
  [view_rls_sale_data]="process_dataset.view_rls_sale_data dimension_table.dim_company dimension_view.view_dim_company mds_dataset.mds_data_org_employee_mapping_center"
  [brand]="validated_mastersku.brand"
  [rls_ta_customer]="process_dataset.rls_ta_customer"
  [mds_data_ta_dashboard_display_control]="mds_dataset.mds_data_ta_dashboard_display_control"
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

log "Checking prerequisites"
command -v gcloud >/dev/null || die "gcloud not found"
command -v bq >/dev/null || die "bq not found"
command -v curl >/dev/null || die "curl not found (needed for the Dataform repository policy)"
[ -f "$workflow_yaml" ] || die "missing $workflow_yaml"
python_bin="$(pick_python)"
export_tables="$(read_export_tables "$python_bin")"
[ -n "$export_tables" ] || die "no tables in $config_json"
for t in "$BQ_DATASET.mart_export_config" "$BQ_DATASET.mart_sent_state"; do
  bq_table_exists "$t" || die "$PROJECT:$t not found - run tag pub_sub from Dataform release production first"
done
# The workflow reads mart_export_config by column position.
bq --project_id="$PROJECT" show --schema --format=json "$PROJECT:$BQ_DATASET.mart_export_config" |
  "$python_bin" -c 'import json, sys; sys.exit(0 if [f["name"] for f in json.load(sys.stdin)][6:8] == ["trigger_scheduler", "seeded_at"] else 1)' ||
  die "$BQ_DATASET.mart_export_config requires trigger_scheduler as its 7th and seeded_at as its 8th column - run tag pub_sub from Dataform release production first"
while IFS=$'\t' read -r table_name source_view _topic; do
  bq_table_exists "pub_sub.$source_view" || die "view pub_sub.$source_view not found - run tag pub_sub first"
  [ -n "${SOURCE_TABLES[$table_name]:-}" ] || die "SOURCE_TABLES has no entry for $table_name"
done <<< "$export_tables"
gcloud secrets describe "$SLACK_SECRET" --project="$PROJECT" >/dev/null 2>&1 ||
  die "secret $SLACK_SECRET not found - store the Slack webhook URL in it first"
export_location="$(bq --project_id="$PROJECT" show --format=prettyjson "$PROJECT:$EXPORT_DATASET" |
  "$python_bin" -c 'import json, sys; print(json.load(sys.stdin)["location"].lower())')"
[ "$export_location" = "$SNAPSHOT_LOCATION" ] ||
  die "dataset $EXPORT_DATASET is in $export_location but SNAPSHOT_LOCATION is $SNAPSHOT_LOCATION; EXPORT DATA needs them to match"
project_number="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
pubsub_agent="service-$project_number@gcp-sa-pubsub.iam.gserviceaccount.com"

log "Enabling APIs"
gcloud services enable --project="$PROJECT" \
  workflows.googleapis.com workflowexecutions.googleapis.com cloudscheduler.googleapis.com \
  pubsub.googleapis.com secretmanager.googleapis.com dataform.googleapis.com bigquery.googleapis.com \
  storage.googleapis.com

log "Service accounts (keyless - never create keys)"
ensure_sa "$TRIGGER_SA_NAME" "Cloud Scheduler -> Workflows datamart-publish"
ensure_sa "$PUBLISHER_SA_NAME" "Workflows datamart-publish runner"

log "Topics and dead-letter topics"
while IFS=$'\t' read -r _table_name _source_view topic; do
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

log "Least-privilege roles for $publisher_sa"
# Project level only for roles that exist only there: run BigQuery jobs / write workflow logs.
for role in roles/bigquery.jobUser roles/logging.logWriter; do
  gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$publisher_sa" \
    --role="$role" --condition=None >/dev/null
  echo "  $role on project"
done
# The workflow lists workflow invocations of the repository and queries their actions, nothing
# else of Dataform: a custom role with those two permissions, granted on the repository only.
ensure_custom_role "$DATAFORM_ROLE_ID" "Data Mart publish: read Dataform invocations" "$DATAFORM_ROLE_PERMISSIONS"
grant_dataform_repo "serviceAccount:$publisher_sa" "projects/$PROJECT/roles/$DATAFORM_ROLE_ID"
revoke_project "serviceAccount:$publisher_sa" roles/dataform.viewer
grant_bq "$BQ_DATASET.mart_export_config" roles/bigquery.dataEditor
grant_bq "$BQ_DATASET.mart_sent_state" roles/bigquery.dataEditor
# Read on the export view only; the view is authorized on its base tables' datasets.
declare -A view_datasets=()
while IFS=$'\t' read -r table_name source_view _topic; do
  grant_bq "pub_sub.$source_view" roles/bigquery.dataViewer
  for base in ${SOURCE_TABLES[$table_name]}; do
    view_datasets["${base%%.*} $source_view"]=1
  done
done <<< "$export_tables"
for dataset_view in "${!view_datasets[@]}"; do
  authorize_view "${dataset_view% *}" "${dataset_view#* }"
done
while IFS=$'\t' read -r table_name _source_view _topic; do
  for base in ${SOURCE_TABLES[$table_name]}; do
    # Routines (function_dataset) have no table IAM policy: only tables and views carry an old grant to remove.
    bq_table_exists "$base" || continue
    revoke_bq "$base" roles/bigquery.dataViewer
  done
done <<< "$export_tables"
gcloud secrets add-iam-policy-binding "$SLACK_SECRET" --project="$PROJECT" \
  --member="serviceAccount:$publisher_sa" --role=roles/secretmanager.secretAccessor >/dev/null
echo "  roles/secretmanager.secretAccessor on secret $SLACK_SECRET"

log "Workflow $WORKFLOW ($REGION)"
gcloud workflows deploy "$WORKFLOW" --project="$PROJECT" --location="$REGION" \
  --source="$workflow_yaml" --service-account="$publisher_sa" \
  --description="Publish changed rows of Pub/Sub export tables (infra/pubsub in data-buffet)"
# Workflows has no IAM on a single workflow and IAM Conditions do not support Workflows
# resources, so the narrowest grant is project level: a custom role that can only start an
# execution (no get/list/cancel). It is the trigger SA's only role.
ensure_custom_role "$TRIGGER_ROLE_ID" "Data Mart publish: start workflow executions" "$TRIGGER_ROLE_PERMISSIONS"
gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$trigger_sa" \
  --role="projects/$PROJECT/roles/$TRIGGER_ROLE_ID" --condition=None >/dev/null
echo "  $TRIGGER_ROLE_ID on project for $trigger_sa (its only role)"
revoke_project "serviceAccount:$trigger_sa" roles/workflows.invoker

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

log "Done. Verify the first run: document/how-to/setup-pubsub-export.md (A4)"
