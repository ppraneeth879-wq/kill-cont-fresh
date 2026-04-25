#!/usr/bin/env bash
# Deploy the KillCont API to Cloud Run.
#
# Prereqs (run once per machine):
#   gcloud auth login
#   gcloud config set project "${GCP_PROJECT_ID}"
#   gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
#       firestore.googleapis.com storage.googleapis.com \
#       artifactregistry.googleapis.com identitytoolkit.googleapis.com
#
# Usage (from repo root):
#   GCP_PROJECT_ID=killcont-demo \
#   FIREBASE_STORAGE_BUCKET=killcont-demo-media \
#   PUBLIC_WEB_ORIGIN=https://killcont-demo.web.app \
#   GEMINI_API_KEY=...optional... \
#   bash infra/google-cloud/deploy-api.sh
#
# All env vars below are required unless they have a default.

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?GCP_PROJECT_ID is required}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-killcont-api}"
BUCKET="${FIREBASE_STORAGE_BUCKET:?FIREBASE_STORAGE_BUCKET is required}"
WEB_ORIGIN="${PUBLIC_WEB_ORIGIN:?PUBLIC_WEB_ORIGIN is required}"
GEMINI_KEY="${GEMINI_API_KEY:-}"
PHASH_THRESHOLD="${PHASH_MATCH_THRESHOLD:-0.80}"
DEMO_ORG_ID="${DEMO_ORG_ID:-org-demo-1}"

ENV_VARS=(
  "RUNTIME_PROFILE=public"
  "AUTH_BACKEND=firebase"
  "METADATA_BACKEND=firestore"
  "MEDIA_BACKEND=gcs"
  "GCP_PROJECT_ID=${PROJECT_ID}"
  "FIREBASE_PROJECT_ID=${PROJECT_ID}"
  "FIREBASE_STORAGE_BUCKET=${BUCKET}"
  "PHASH_MATCH_THRESHOLD=${PHASH_THRESHOLD}"
  "DEMO_ORG_ID=${DEMO_ORG_ID}"
  "ALLOWED_ORIGINS=${WEB_ORIGIN}"
  "PUBLIC_WEB_ORIGIN=${WEB_ORIGIN}"
)

if [[ -n "${GEMINI_KEY}" ]]; then
  ENV_VARS+=("GEMINI_API_KEY=${GEMINI_KEY}")
fi

ENV_VAR_FLAG="$(IFS=,; echo "${ENV_VARS[*]}")"

echo "[deploy-api] building + deploying ${SERVICE_NAME} in ${REGION} (project ${PROJECT_ID})"

gcloud run deploy "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --source apps/api \
  --allow-unauthenticated \
  --port 8080 \
  --cpu 1 \
  --memory 512Mi \
  --max-instances 2 \
  --set-env-vars "${ENV_VAR_FLAG}"

echo "[deploy-api] applying Firestore composite indexes"
gcloud firestore indexes composite create-from-file \
  --file infra/google-cloud/firestore.indexes.json \
  --project "${PROJECT_ID}" || \
  echo "[deploy-api] (some indexes may already exist — non-fatal)"

echo "[deploy-api] granting public-read on the media bucket (previews)"
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --member=allUsers \
  --role=roles/storage.objectViewer \
  --project "${PROJECT_ID}" || true

URL="$(gcloud run services describe "${SERVICE_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --format='value(status.url)')"

echo "[deploy-api] live URL: ${URL}"
echo "[deploy-api] smoke (after sign-in to grab an ID token):"
echo "  SMOKE_FIREBASE_ID_TOKEN=... python scripts/smoke.py --base-url ${URL}/api/v1 --profile public"
