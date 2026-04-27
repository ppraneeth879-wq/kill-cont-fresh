# KillCont — Firebase + Google Cloud Setup

Operator-facing walkthrough to provision everything KillCont needs for **real Google sign-in** (Bundle F) and the eventual **public deployment** (S12).

You'll go from "fresh Google account, nothing provisioned" to "I can click 'Continue with Google' on `localhost:5173` and it actually works" in ~10 minutes. The deploy phase reuses the same project — no second setup.

---

## Prerequisites

- A Google account (any free Gmail works).
- ~10 minutes for the auth setup, ~15 minutes more for the deploy.
- **No payment required** for the Spark (free) plan we use here. Cloud Run / Firestore / Cloud Storage in S12 will require a billing account on file (free tier covers demo traffic, but Google requires a card on the project before they'll let you deploy).

This guide assumes you're running on Windows with Git Bash or PowerShell. Adjust paths if you're on macOS/Linux.

---

## Part 1 — Real Google sign-in (this is Bundle F)

### Step 1.1 — Create the Firebase project

1. Open <https://console.firebase.google.com>.
2. Click **Add project**.
3. Project name: `killcont-demo` (or any name; the project *ID* will get auto-suffixed).
4. **Disable** Google Analytics for this project (you don't need it for the demo). If the dialog forces you to keep it, accept the default Analytics account — you can ignore it later.
5. Click **Create project**, wait ~30 s, click **Continue**.

You're now on the project Overview page. Note the **Project ID** at the top (something like `killcont-demo-a1b2c3`). You'll paste it later.

### Step 1.2 — Enable Authentication and the Google provider

1. Left sidebar → **Build** → **Authentication**.
2. Click **Get started**.
3. On the "Sign-in method" tab, click **Google** in the providers list.
4. Toggle **Enable** to ON.
5. Pick a **Project support email** (your Gmail is fine).
6. Click **Save**.

You should see Google listed under "Sign-in providers" with a green checkmark. Confirm `localhost` is in the **Authorized domains** list at the bottom of the same page (it should be by default; if not, click "Add domain" and add `localhost`).

### Step 1.3 — Register a Web App and copy the config

1. Project Overview (top-left home icon) → click the **`</>` Web** icon to register a web app.
2. App nickname: `KillCont Web`.
3. **Do not** check "Also set up Firebase Hosting" yet (we'll do that in Part 2).
4. Click **Register app**.
5. Firebase shows a code snippet with a `firebaseConfig` object. **Copy these 6 values** somewhere safe — you'll paste them into `apps/web/.env`:

   ```javascript
   const firebaseConfig = {
     apiKey: "AIza...",                              // → VITE_FIREBASE_API_KEY
     authDomain: "killcont-demo-a1b2c3.firebaseapp.com",  // → VITE_FIREBASE_AUTH_DOMAIN
     projectId: "killcont-demo-a1b2c3",              // → VITE_FIREBASE_PROJECT_ID
     storageBucket: "killcont-demo-a1b2c3.appspot.com",   // → VITE_FIREBASE_STORAGE_BUCKET
     messagingSenderId: "1234567890",                // → VITE_FIREBASE_MESSAGING_SENDER_ID
     appId: "1:1234567890:web:abc123def456",         // → VITE_FIREBASE_APP_ID
   };
   ```

6. Click **Continue to console**.

> **Heads up:** these `apiKey`-and-friends values are **safe to commit publicly** per Firebase's own docs. They identify the project, not the user. Real security comes from your Firestore/Storage rules + backend ID-token verification. Don't panic if they end up in git — they're not secrets.

### Step 1.4 — Generate a service account key (backend credentials)

The frontend uses the public web config. The **backend** needs admin credentials to verify ID tokens. We use a service account JSON file for this.

1. Project Settings (gear icon next to "Project Overview") → **Service accounts** tab.
2. You'll see "Firebase Admin SDK" with a code snippet for Python.
3. Click **Generate new private key** → confirm in the dialog → a JSON file downloads.
4. **Move that file to `apps/api/service-account.json`** in your repo.

> **Heads up:** this JSON file **IS** a real credential. Anyone with it can impersonate the Firebase Admin SDK on your project. The repo's `.gitignore` already includes `service-account.json` and `*.json` — verify it's gitignored before committing anything:
>
> ```bash
> cd D:\kill-cont-fresh
> git check-ignore apps/api/service-account.json
> # Should print: apps/api/service-account.json
> ```
>
> If it doesn't print anything (meaning the file is NOT ignored), STOP and add `service-account.json` to `apps/api/.gitignore` before continuing.

### Step 1.5 — Wire up `apps/api/.env`

Copy `apps/api/.env.example` to `apps/api/.env` if you haven't already, then edit:

```
AUTH_BACKEND=firebase
FIREBASE_PROJECT_ID=killcont-demo-a1b2c3       # from step 1.3
FIREBASE_CREDENTIALS_PATH=service-account.json
```

Leave `GEMINI_API_KEY` as whatever you already had (it's unrelated to auth).

### Step 1.6 — Wire up `apps/web/.env`

Copy `apps/web/.env.example` to `apps/web/.env` if you haven't already, then paste the 6 Firebase web values from step 1.3:

```
VITE_AUTH_MODE=firebase
VITE_FIREBASE_API_KEY=AIza...
VITE_FIREBASE_AUTH_DOMAIN=killcont-demo-a1b2c3.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=killcont-demo-a1b2c3
VITE_FIREBASE_STORAGE_BUCKET=killcont-demo-a1b2c3.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=1234567890
VITE_FIREBASE_APP_ID=1:1234567890:web:abc123def456
```

### Step 1.7 — Restart, sign in, verify

1. Stop your running uvicorn and vite (Ctrl+C in each terminal).
2. Restart the API:
   ```bash
   cd D:\kill-cont-fresh\apps\api
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
   Look for this line in the startup output:
   ```
   INFO     killcont.startup:AUTH_BACKEND=firebase using credentials at .../service-account.json
   ```
   If you instead see `does not exist - sign-in will fail`, the service account path is wrong — fix `FIREBASE_CREDENTIALS_PATH` and restart.
3. Restart the web in another terminal:
   ```bash
   cd D:\kill-cont-fresh\apps\web
   npm run dev
   ```
4. Open <http://localhost:5173> in your browser.
5. Click **Sign in** in the top nav (or land on `/sign-in` directly).
6. You should now see a single **Continue with Google** button (the email + name form is gone — that was demo mode).
7. Click it. Google's popup opens. Pick your account. Approve.
8. Browser redirects to `/app/overview`. Top-right shows your real Google name + email.

If you get **"This domain isn't on the Firebase Authorized Domains list"**: go back to Authentication → Settings → Authorized domains → make sure `localhost` is there. (The newer Firebase Console buries this under Authentication → Settings tab → "Authorized domains" subsection.)

If you get a popup-blocked error: allow popups for `localhost:5173` in your browser settings, then retry.

If the popup opens but the page never redirects: open browser DevTools → Network → look for the `/api/v1/session/login` request. If it returned 401, the backend rejected the token — most likely the service account JSON is for the wrong Firebase project. Verify `FIREBASE_PROJECT_ID` in `apps/api/.env` matches the project in your service account JSON's `project_id` field.

### Step 1.8 — Confirm a user row was created

```bash
cd D:\kill-cont-fresh\apps\api
sqlite3 var/app.db "SELECT id, email, display_name, role, org_id FROM users;"
```

You should see your real Google email with `role=operator` and `org_id=org-demo-1`. Existing demo users (if any) keep their `admin` role — Bundle F doesn't demote them.

**You're done with Part 1.** Real Google sign-in works against your local dev server. Anyone with a Google account can now click through and use KillCont. To go back to the offline demo flow (no Firebase needed), set `AUTH_BACKEND=demo` in `apps/api/.env` and `VITE_AUTH_MODE=demo` in `apps/web/.env`, restart both servers.

---

## Part 2 — Public deployment (S12)

This part publishes KillCont to the public internet. The frontend goes to **Firebase Hosting** (free), the backend goes to **Cloud Run** (free tier covers demo traffic). Same Firebase/GCP project from Part 1.

### Step 2.1 — Enable billing on the GCP project

Cloud Run requires a billing account even when usage stays inside the always-free tier (Google's policy). You won't be charged unless you exceed free quotas. Free trial credit ($300 / 90 days) covers any accidents.

1. Open <https://console.cloud.google.com/billing>.
2. Click **Add billing account** → enter card details → confirm.
3. Open <https://console.cloud.google.com/billing/projects> → find `killcont-demo` → **Change billing**.
4. Link it to the billing account you just created.
5. Set a budget alert: Billing → Budgets & alerts → Create budget → $1/month with a 100% alert. This emails you the moment usage approaches anything you'd actually pay for. Belt-and-suspenders against accidents.

### Step 2.2 — Install the CLI tools

You need both `gcloud` and `firebase-tools`.

**`gcloud` (Google Cloud CLI):**
- Windows: <https://cloud.google.com/sdk/docs/install#windows> → download installer → run it → accept defaults.
- After install, restart your terminal so `gcloud` is on PATH.
- Authenticate: `gcloud auth login` → opens a browser, pick your Google account, approve.
- Set the project: `gcloud config set project killcont-demo-a1b2c3` (use YOUR project ID).

**`firebase-tools`:**
- Already cross-platform via npm: `npm install -g firebase-tools`
- Authenticate: `firebase login` → opens a browser, pick the same Google account, approve.

Verify both:
```bash
gcloud --version       # should show version 4xx+
firebase --version     # should show 13.x+
```

### Step 2.3 — Enable the GCP APIs the deploy will use

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com storage.googleapis.com identitytoolkit.googleapis.com
```

This call enables Cloud Run, Cloud Build (used to containerize the API), Artifact Registry (where the container image lives), Firestore (for the public-profile metadata adapter), Cloud Storage (for the public-profile media adapter), and Identity Toolkit (the Firebase Auth backend). Takes ~30 seconds; idempotent so you can re-run.

### Step 2.4 — Create the Firestore database (one-time)

```bash
gcloud firestore databases create --location=us-central1
```

Pick a region close to you. `us-central1` is always-free; `nam5` (multi-region) also is. Use single-region for lower latency unless you specifically need multi-region.

### Step 2.5 — Create the Cloud Storage bucket for media

```bash
gcloud storage buckets create gs://killcont-demo-a1b2c3-media --location=us-central1 --uniform-bucket-level-access
```

Use the same region as Firestore so the API doesn't pay cross-region egress. The `deploy-api.sh` script in this folder grants `allUsers:objectViewer` on this bucket so previews are publicly readable — that's intentional for a demo (every URL is unguessable but technically open). Tighten later via Storage rules if you want.

### Step 2.6 — Set environment variables for the deploy script

The `infra/google-cloud/deploy-api.sh` script reads these from your shell. Set them once:

```bash
export GCP_PROJECT_ID=killcont-demo-a1b2c3
export FIREBASE_PROJECT_ID=killcont-demo-a1b2c3
export FIREBASE_STORAGE_BUCKET=killcont-demo-a1b2c3-media
export GEMINI_API_KEY=$(grep GEMINI_API_KEY apps/api/.env | cut -d= -f2)
export PUBLIC_WEB_ORIGIN=""   # we don't know the hosted URL yet — back-fill in 2.9
```

(Replace `killcont-demo-a1b2c3` with your real project ID.)

### Step 2.7 — Deploy the API to Cloud Run

```bash
cd D:\kill-cont-fresh
bash infra/google-cloud/deploy-api.sh
```

This wraps `gcloud run deploy killcont-api --source apps/api --region us-central1 --allow-unauthenticated`. Cloud Build packages the Dockerfile, pushes the image, and deploys. Takes ~3–5 minutes the first time.

Output prints the **service URL** at the end:
```
Service [killcont-api] revision [killcont-api-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://killcont-api-xxxxxxxxxx.a.run.app
```

**Save that URL.** You'll paste it into the FE config next.

Sanity-check the API:
```bash
curl https://killcont-api-xxxxxxxxxx.a.run.app/api/v1/health
# → {"status":"ok"}
```

### Step 2.8 — Build the FE for production + deploy to Firebase Hosting

Create `apps/web/.env.production` from the template:

```bash
cp apps/web/.env.production.example apps/web/.env.production
```

Edit `apps/web/.env.production` and fill in:
- `VITE_API_BASE_URL=https://killcont-api-xxxxxxxxxx.a.run.app/api/v1` (your Cloud Run URL + `/api/v1`)
- `VITE_AUTH_MODE=firebase`
- The 6 `VITE_FIREBASE_*` values from step 1.3 (same as `apps/web/.env`)
- `VITE_GOOGLE_MAPS_API_KEY=` whatever you have, or leave blank

Then deploy:

```bash
bash infra/google-cloud/deploy-web.sh
```

This runs `npm run build` (falls back to `npx vite build` if tsc trips on TS5103) then `firebase deploy --only hosting`. Takes ~30 seconds.

Output prints the **hosted URL**:
```
+  Deploy complete!
Hosting URL: https://killcont-demo-a1b2c3.web.app
```

### Step 2.9 — Back-fill CORS + Authorized Domains

Two final touches that make the deployed app actually work:

**(a) Back-fill the FE origin into the Cloud Run env:**

```bash
gcloud run services update killcont-api \
  --update-env-vars PUBLIC_WEB_ORIGIN=https://killcont-demo-a1b2c3.web.app \
  --region us-central1
```

This makes the API's CORS allowlist accept requests from your hosted FE. Without this, the browser will block every API call with a CORS error.

**(b) Add the hosted domain to Firebase Authorized Domains:**

1. Firebase Console → Authentication → **Settings** tab → **Authorized domains** subsection.
2. Click **Add domain**.
3. Add `killcont-demo-a1b2c3.web.app` (your hosted URL hostname, no `https://`).
4. Save.

Without this, the Google sign-in popup will reject your hosted domain with `auth/unauthorized-domain`.

### Step 2.10 — Smoke-test the live deployment

Open `https://killcont-demo-a1b2c3.web.app` in a fresh incognito window. You should see:
1. Marketing/landing page.
2. Sign-in works via "Continue with Google".
3. After sign-in, `/app/overview` loads with seeded data.
4. Live Watch + Monitor + Incidents + Evidence all behave the same as local.
5. Network tab shows API calls hitting `https://killcont-api-xxxxxxxxxx.a.run.app/api/v1/...` and returning 200.

If something's broken, the most common issues are:
- **CORS errors** → step 2.9(a) wasn't run, or the hostname is wrong (use the exact `*.web.app` from `firebase deploy` output, no trailing slash).
- **`auth/unauthorized-domain`** → step 2.9(b).
- **Cold-start delay (~5 s)** on the first request → optional fix below.

### Step 2.11 — Optional: minimum instances for cold-start mitigation

Cloud Run scales to zero when idle. The first request after idle takes ~3–5 s while the container spins up. For a demo where judges click in fresh, that's annoying. Pin one instance always-on:

```bash
gcloud run services update killcont-api --min-instances=1 --region us-central1
```

This uses ~$5–10/month outside the free tier, so flip it back off after the demo:

```bash
gcloud run services update killcont-api --min-instances=0 --region us-central1
```

---

## Captured project IDs (fill these in once you've done it)

Paste your real values here for future reference. Keep this file in the repo so any future agent (or you, six months from now) knows what was provisioned.

```
GCP_PROJECT_ID=killcont-demo-a1b2c3
FIREBASE_PROJECT_ID=killcont-demo-a1b2c3
FIREBASE_STORAGE_BUCKET=killcont-demo-a1b2c3-media
CLOUD_RUN_URL=https://killcont-api-xxxxxxxxxx.a.run.app
HOSTED_WEB_URL=https://killcont-demo-a1b2c3.web.app
FIRESTORE_LOCATION=us-central1
```

---

## Rollback / cleanup

To take everything down (no charges accumulate against shut-down resources):

```bash
gcloud run services delete killcont-api --region us-central1
firebase hosting:disable
gcloud projects delete killcont-demo-a1b2c3   # nuclear: removes everything in the project
```

The Spark plan has no minimum charges, so leaving it provisioned and unused costs you nothing.
