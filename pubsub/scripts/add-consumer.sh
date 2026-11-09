#!/usr/bin/env bash
# Connects a consumer team to Pub/Sub export topics by PULL in databuffet-nonprd.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน B). Idempotent: rerun to re-apply the
# settings or to add topics for the same team.
#
# Two ways to name the identity that pulls (the "team SA"); every grant below is the same for both:
# - default (team outside GCP): our service account sa-pull-<team> (no project role); its JSON key
#   is made and handed over by hand (see the guide), this script never creates one.
# - --team-sa <email> (team on GCP): the team's own runtime service account. We create no service
#   account and no key. Domain-restricted sharing only admits accounts of our organization, so a
#   service account of a project outside it is refused - use the default (key) way for those.
# Per topic: pull subscription sub.<team>.<topic> that only the team SA may pull from, and
# dlq.<team>.<topic> on <topic>-dead-letter holding that subscription's dead letters (we read
# it; the team gets no grant on it). The Pub/Sub service agent gets subscriber on the
# subscription; its publisher grant on <topic>-dead-letter belongs to setup.sh.
# First-load files (export-snapshot.sh): the team SA may read objects under <team>/ of the
# snapshot bucket by exact name, nothing else of the bucket.
#
# Prerequisites: setup.sh already run (topics + dead-letter topics exist); gcloud logged in as a
# project owner.
#
# Usage: bash pubsub/scripts/add-consumer.sh [--team-sa <email>] <team> <topic>...
#   e.g. bash pubsub/scripts/add-consumer.sh ai-dev export-ta-org_levels
#        bash pubsub/scripts/add-consumer.sh --team-sa consumer-run@ai-prod.iam.gserviceaccount.com ai-prod export-ta-org_levels
set -euo pipefail

PROJECT=databuffet-nonprd
SA_PREFIX=sa-pull-
SA_ID_MAX=30                      # service account id limit
SNAPSHOT_BUCKET=databuffet-nonprd-datamart-snapshot   # bucket + roles created by setup.sh
SNAPSHOT_GET_ROLE_ID=datamartSnapshotGet

log() { printf '\n== %s\n' "$*"; }
die() { printf 'add-consumer.sh: %s\n' "$*" >&2; exit 1; }

usage="usage: bash pubsub/scripts/add-consumer.sh [--team-sa <email>] <team> <topic>..."
own_sa=""
if [ "${1:-}" = --team-sa ]; then
  [ $# -ge 2 ] || die "$usage"
  own_sa="$2"
  [ -n "$own_sa" ] || die "--team-sa requires a non-empty service account email"
  shift 2
fi
[ $# -ge 2 ] || die "$usage"
team="$1"
shift
topics=("$@")

# Lowercase letters, digits and '-', starting and ending with a letter or digit (the SA id rule).
[[ "$team" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] ||
  die "team '$team' must be lowercase letters, digits and '-', starting and ending with a letter or digit"
sa_id="$SA_PREFIX$team"
[ "${#sa_id}" -le "$SA_ID_MAX" ] ||
  die "service account id $sa_id is ${#sa_id} characters; the limit is $SA_ID_MAX (team at most $((SA_ID_MAX - ${#SA_PREFIX})))"
if [ -n "$own_sa" ]; then
  # A user-managed service account, or a project's default Compute Engine / App Engine one.
  sa_name='[a-z][a-z0-9-]{4,28}[a-z0-9]'
  [[ "$own_sa" =~ ^$sa_name@$sa_name\.iam\.gserviceaccount\.com$ ||
    "$own_sa" =~ ^[0-9]+-compute@developer\.gserviceaccount\.com$ ||
    "$own_sa" =~ ^$sa_name@appspot\.gserviceaccount\.com$ ]] ||
    die "--team-sa '$own_sa' is not a service account email (<name>@<project>.iam.gserviceaccount.com, <number>-compute@developer.gserviceaccount.com or <project>@appspot.gserviceaccount.com)"
  team_sa="$own_sa"
else
  team_sa="$sa_id@$PROJECT.iam.gserviceaccount.com"
fi

log "Checking prerequisites"
command -v gcloud >/dev/null || die "gcloud not found"
for topic in "${topics[@]}"; do
  gcloud pubsub topics describe "$topic" --project="$PROJECT" >/dev/null 2>&1 ||
    die "topic $topic not found - use a topic of includes/controller/mart-export-config.json after setup.sh has run"
  gcloud pubsub topics describe "$topic-dead-letter" --project="$PROJECT" >/dev/null 2>&1 ||
    die "dead-letter topic $topic-dead-letter not found - run setup.sh first"
done
gcloud storage buckets describe "gs://$SNAPSHOT_BUCKET" >/dev/null 2>&1 ||
  die "bucket gs://$SNAPSHOT_BUCKET not found - run setup.sh first"
gcloud iam roles describe "$SNAPSHOT_GET_ROLE_ID" --project="$PROJECT" >/dev/null 2>&1 ||
  die "custom role $SNAPSHOT_GET_ROLE_ID not found - run setup.sh first"
project_number="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
pubsub_agent="service-$project_number@gcp-sa-pubsub.iam.gserviceaccount.com"

if [ -n "$own_sa" ]; then
  log "Team service account $team_sa (theirs: we create no service account and no key)"
else
  log "Service account $team_sa (no key, no project role)"
  if gcloud iam service-accounts describe "$team_sa" --project="$PROJECT" >/dev/null 2>&1; then
    echo "  exists"
  else
    gcloud iam service-accounts create "$sa_id" --project="$PROJECT" \
      --display-name="Pub/Sub pull consumer $team" >/dev/null
    echo "  created"
  fi
fi

# A new service account can take a minute to be accepted in IAM policies, so grants retry.
# A refusal by domain-restricted sharing never clears with time, so it stops at once.
retry_grant() { # <command>...
  local attempt err
  for attempt in 1 2 3 4 5 6 7; do
    err="$("$@" 2>&1 >/dev/null)" && return
    if grep -qiE 'permitted customer|allowedPolicyMemberDomains' <<<"$err"; then
      die "IAM refused $team_sa: domain-restricted sharing (constraints/iam.allowedPolicyMemberDomains) only admits accounts of our organization, and this service account is outside it. Rerun without --team-sa to use our service account and a JSON key instead."
    fi
    [ "$attempt" -lt 7 ] || break
    sleep $((attempt * 10))
  done
  printf '%s\n' "$err" >&2
  return 1
}

grant_subscriber() { # <subscription> <member>
  retry_grant gcloud pubsub subscriptions add-iam-policy-binding "$1" --project="$PROJECT" \
    --member="$2" --role=roles/pubsub.subscriber
  echo "  roles/pubsub.subscriber on $1 for $2"
}

# A conditional binding of a custom role on the snapshot bucket for the team SA.
grant_snapshot() { # <role id> <condition title> <CEL expression>
  condition_file="$(mktemp)"
  trap 'rm -f "$condition_file"' EXIT   # also when a refused grant stops the run
  printf 'title: "%s"\nexpression: "%s"\n' "$2" "$3" > "$condition_file"
  retry_grant gcloud storage buckets add-iam-policy-binding "gs://$SNAPSHOT_BUCKET" \
    --member="serviceAccount:$team_sa" --role="projects/$PROJECT/roles/$1" \
    --condition-from-file="$condition_file"
  rm -f "$condition_file"
  echo "  $1 on gs://$SNAPSHOT_BUCKET when $3"
}

# Grant before creating subscriptions so an IAM refusal cannot leave new subscriptions behind.
log "First-load snapshot files: gs://$SNAPSHOT_BUCKET/$team/ only"
grant_snapshot "$SNAPSHOT_GET_ROLE_ID" "snapshot-get-$team" \
  "resource.name.startsWith('projects/_/buckets/$SNAPSHOT_BUCKET/objects/$team/')"

for topic in "${topics[@]}"; do
  sub="sub.$team.$topic"
  dlq_topic="$topic-dead-letter"
  dlq_sub="dlq.$team.$topic"
  dlq_filter="attributes.CloudPubSubDeadLetterSourceSubscription = \"$sub\""

  # The dead-letter hold comes first, so no dead letter of $sub is ever forwarded with nowhere
  # to land. Its filter cannot be changed after creation, so an existing one must already match.
  log "Dead-letter hold $dlq_sub on $dlq_topic"
  dlq_flags=(--project="$PROJECT" --message-retention-duration=31d --expiration-period=never)
  if existing_filter="$(gcloud pubsub subscriptions describe "$dlq_sub" --project="$PROJECT" \
    --format='value(filter)' 2>/dev/null)"; then
    [ "$existing_filter" = "$dlq_filter" ] ||
      die "$dlq_sub exists with filter '$existing_filter', expected '$dlq_filter'"
    gcloud pubsub subscriptions update "$dlq_sub" "${dlq_flags[@]}" >/dev/null
    echo "  exists, settings re-applied"
  else
    gcloud pubsub subscriptions create "$dlq_sub" --topic="$dlq_topic" "${dlq_flags[@]}" \
      --message-filter="$dlq_filter" >/dev/null
    echo "  created (retention 31 days, never expires, only dead letters of $sub)"
  fi

  log "Pull subscription $sub on $topic"
  sub_flags=(
    --project="$PROJECT"
    --ack-deadline=60
    --message-retention-duration=7d --retain-acked-messages
    --expiration-period=never
    --min-retry-delay=10s --max-retry-delay=600s
    --dead-letter-topic="projects/$PROJECT/topics/$dlq_topic" --max-delivery-attempts=5
  )
  if gcloud pubsub subscriptions describe "$sub" --project="$PROJECT" >/dev/null 2>&1; then
    gcloud pubsub subscriptions update "$sub" "${sub_flags[@]}" >/dev/null
    echo "  exists, settings re-applied"
  else
    gcloud pubsub subscriptions create "$sub" --topic="$topic" "${sub_flags[@]}" >/dev/null
    echo "  created (ack 60s, keeps acked messages 7 days, never expires, retry 10s-600s, dead letter after 5 attempts)"
  fi

  # The team pulls from its own subscription only; the service agent forwards dead letters
  # (subscriber here; its publisher grant on the dead-letter topic is made by setup.sh).
  grant_subscriber "$sub" "serviceAccount:$team_sa"
  grant_subscriber "$sub" "serviceAccount:$pubsub_agent"
done

if [ -n "$own_sa" ]; then
  log "Done. No key: the team pulls as $team_sa. Export the first load: document/how-to/setup-pubsub-export.md (ส่วน B)"
else
  log "Done. Make the key and hand it over by hand, then export the first load: document/how-to/setup-pubsub-export.md (ส่วน B)"
fi
