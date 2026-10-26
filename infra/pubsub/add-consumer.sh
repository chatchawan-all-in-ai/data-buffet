#!/usr/bin/env bash
# Connects a consumer team to Pub/Sub export topics by PULL in databuffet-nonprd.
# Guide: document/how-to/setup-pubsub-export.md (ส่วน B). Idempotent: rerun to re-apply the
# settings or to add topics for the same team.
#
# Per team: service account sa-pull-<team> (no key, no project role).
# Per topic: pull subscription sub.<team>.<topic> that only sa-pull-<team> may pull from, and
# dlq.<team>.<topic> on <topic>-dead-letter holding that subscription's dead letters (we read
# it; the team gets no grant on it). The Pub/Sub service agent gets subscriber on the
# subscription; its publisher grant on <topic>-dead-letter belongs to setup.sh.
# The JSON key is made and handed over by hand (see the guide); this script never creates one.
#
# Prerequisites: setup.sh already run (topics + dead-letter topics exist); gcloud logged in as a
# project owner.
#
# Usage: bash infra/pubsub/add-consumer.sh <team> <topic>...
#   e.g. bash infra/pubsub/add-consumer.sh ai-dev export-ta-dim_company
set -euo pipefail

PROJECT=databuffet-nonprd
SA_PREFIX=sa-pull-
SA_ID_MAX=30                      # service account id limit

log() { printf '\n== %s\n' "$*"; }
die() { printf 'add-consumer.sh: %s\n' "$*" >&2; exit 1; }

[ $# -ge 2 ] || die "usage: bash infra/pubsub/add-consumer.sh <team> <topic>..."
team="$1"
shift
topics=("$@")

# Lowercase letters, digits and '-', starting and ending with a letter or digit (the SA id rule).
[[ "$team" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]] ||
  die "team '$team' must be lowercase letters, digits and '-', starting and ending with a letter or digit"
sa_id="$SA_PREFIX$team"
[ "${#sa_id}" -le "$SA_ID_MAX" ] ||
  die "service account id $sa_id is ${#sa_id} characters; the limit is $SA_ID_MAX (team at most $((SA_ID_MAX - ${#SA_PREFIX})))"
team_sa="$sa_id@$PROJECT.iam.gserviceaccount.com"

log "Checking prerequisites"
command -v gcloud >/dev/null || die "gcloud not found"
for topic in "${topics[@]}"; do
  gcloud pubsub topics describe "$topic" --project="$PROJECT" >/dev/null 2>&1 ||
    die "topic $topic not found - use a topic of includes/controller/mart-export-config.json after setup.sh has run"
  gcloud pubsub topics describe "$topic-dead-letter" --project="$PROJECT" >/dev/null 2>&1 ||
    die "dead-letter topic $topic-dead-letter not found - run setup.sh first"
done
project_number="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
pubsub_agent="service-$project_number@gcp-sa-pubsub.iam.gserviceaccount.com"

log "Service account $team_sa (no key, no project role)"
if gcloud iam service-accounts describe "$team_sa" --project="$PROJECT" >/dev/null 2>&1; then
  echo "  exists"
else
  gcloud iam service-accounts create "$sa_id" --project="$PROJECT" \
    --display-name="Pub/Sub pull consumer $team" >/dev/null
  echo "  created"
fi

# A new service account can take a minute to be accepted in IAM policies, so the grant retries.
grant_subscriber() { # <subscription> <member>
  local attempt
  for attempt in 1 2 3 4 5 6; do
    if gcloud pubsub subscriptions add-iam-policy-binding "$1" --project="$PROJECT" \
      --member="$2" --role=roles/pubsub.subscriber >/dev/null 2>&1; then
      echo "  roles/pubsub.subscriber on $1 for $2"
      return
    fi
    sleep $((attempt * 10))
  done
  gcloud pubsub subscriptions add-iam-policy-binding "$1" --project="$PROJECT" \
    --member="$2" --role=roles/pubsub.subscriber >/dev/null
  echo "  roles/pubsub.subscriber on $1 for $2"
}

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

log "Done. Make the key and hand it over by hand: document/how-to/setup-pubsub-export.md (ส่วน B)"
