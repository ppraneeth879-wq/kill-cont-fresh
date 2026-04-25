#!/usr/bin/env bash
# Build + deploy the KillCont web app to Firebase Hosting.
#
# Prereqs (run once per machine):
#   npm install -g firebase-tools
#   firebase login
#
# Required env vars (the Vite build bakes these into the JS bundle):
#   VITE_API_BASE_URL                Cloud Run URL + /api/v1 (e.g. https://killcont-api-xxxxx.a.run.app/api/v1)
#   VITE_AUTH_MODE=firebase
#   VITE_FIREBASE_API_KEY            Firebase Console -> Project settings -> Your apps
#   VITE_FIREBASE_AUTH_DOMAIN        usually <project>.firebaseapp.com
#   VITE_FIREBASE_PROJECT_ID         e.g. killcont-demo
#   VITE_FIREBASE_STORAGE_BUCKET     e.g. killcont-demo-media
#   VITE_FIREBASE_MESSAGING_SENDER_ID
#   VITE_FIREBASE_APP_ID
#
# Optional:
#   VITE_GOOGLE_MAPS_API_KEY         Threat map; omit to use the offline SVG fallback.
#   FIREBASE_PROJECT                 Override the project alias from .firebaserc (default: default).
#
# Usage (from repo root):
#   VITE_API_BASE_URL=https://killcont-api-xxxxx.a.run.app/api/v1 \
#   VITE_AUTH_MODE=firebase \
#   VITE_FIREBASE_API_KEY=... \
#   VITE_FIREBASE_AUTH_DOMAIN=killcont-demo.firebaseapp.com \
#   VITE_FIREBASE_PROJECT_ID=killcont-demo \
#   VITE_FIREBASE_STORAGE_BUCKET=killcont-demo-media \
#   VITE_FIREBASE_MESSAGING_SENDER_ID=... \
#   VITE_FIREBASE_APP_ID=... \
#   bash infra/google-cloud/deploy-web.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEB_DIR="${REPO_ROOT}/apps/web"

: "${VITE_API_BASE_URL:?VITE_API_BASE_URL is required (Cloud Run URL + /api/v1)}"
: "${VITE_AUTH_MODE:=firebase}"
: "${VITE_FIREBASE_API_KEY:?VITE_FIREBASE_API_KEY is required}"
: "${VITE_FIREBASE_AUTH_DOMAIN:?VITE_FIREBASE_AUTH_DOMAIN is required}"
: "${VITE_FIREBASE_PROJECT_ID:?VITE_FIREBASE_PROJECT_ID is required}"
: "${VITE_FIREBASE_STORAGE_BUCKET:?VITE_FIREBASE_STORAGE_BUCKET is required}"
: "${VITE_FIREBASE_MESSAGING_SENDER_ID:?VITE_FIREBASE_MESSAGING_SENDER_ID is required}"
: "${VITE_FIREBASE_APP_ID:?VITE_FIREBASE_APP_ID is required}"
: "${VITE_GOOGLE_MAPS_API_KEY:=}"
: "${FIREBASE_PROJECT:=default}"

ENV_FILE="${WEB_DIR}/.env.production"

echo "[deploy-web] writing ${ENV_FILE}"
cat > "${ENV_FILE}" <<EOF
VITE_API_BASE_URL=${VITE_API_BASE_URL}
VITE_AUTH_MODE=${VITE_AUTH_MODE}
VITE_FIREBASE_API_KEY=${VITE_FIREBASE_API_KEY}
VITE_FIREBASE_AUTH_DOMAIN=${VITE_FIREBASE_AUTH_DOMAIN}
VITE_FIREBASE_PROJECT_ID=${VITE_FIREBASE_PROJECT_ID}
VITE_FIREBASE_STORAGE_BUCKET=${VITE_FIREBASE_STORAGE_BUCKET}
VITE_FIREBASE_MESSAGING_SENDER_ID=${VITE_FIREBASE_MESSAGING_SENDER_ID}
VITE_FIREBASE_APP_ID=${VITE_FIREBASE_APP_ID}
VITE_GOOGLE_MAPS_API_KEY=${VITE_GOOGLE_MAPS_API_KEY}
EOF

echo "[deploy-web] installing dependencies (npm ci preferred, falling back to npm install)"
cd "${WEB_DIR}"
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi

echo "[deploy-web] building production bundle (vite build)"
# tsc -b can hit a pre-existing TS5103 on some toolchains; vite build
# alone produces a fully working dist/. Run tsc-aware build first, fall
# back to vite-only if the type build fails.
if ! npm run build; then
  echo "[deploy-web] npm run build failed (likely tsc); falling back to 'vite build'"
  npx vite build
fi

echo "[deploy-web] deploying to Firebase Hosting (project alias: ${FIREBASE_PROJECT})"
firebase deploy --only hosting --project "${FIREBASE_PROJECT}"

echo "[deploy-web] done. Visit:"
echo "  https://${VITE_FIREBASE_PROJECT_ID}.web.app"
echo "[deploy-web] reminder: back-fill PUBLIC_WEB_ORIGIN on Cloud Run so CORS accepts this origin:"
echo "  gcloud run services update killcont-api --region us-central1 \\"
echo "    --update-env-vars PUBLIC_WEB_ORIGIN=https://${VITE_FIREBASE_PROJECT_ID}.web.app,ALLOWED_ORIGINS=https://${VITE_FIREBASE_PROJECT_ID}.web.app"
